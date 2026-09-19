# PaSa Q3 CUDA OOM 只读审计

## 审计范围

本次仅阅读现有源码、Q0–Q3 `smoke_report.json`、Q3 `run.log` 和 pilot 调度记录。未加载模型、未重跑 query、未访问网络，也未修改 PaSa 算法源码。

## 结论

Q3 OOM 的主要原因可以确认是：Expand 阶段最多 20 个 `do_expand` worker 会在没有锁和显式同步的情况下，共享同一个 Selector 实例并分别调用 `infer_score(select_prompts)`。每次调用又会把该 worker 收集的全部 prompts 作为一个 batch 传给 `generate()`。Q3 有三个不同 worker 在同一段日志中进入 Selector 的 Qwen2 forward 并发生 OOM；前两个异常栈彼此交错，证明至少两个 Selector forward 同时处于执行中。

Q0–Q2 的进程在每题结束后均退出，两张物理 GPU 都回落到 0 MiB，Q3 启动前也是 0 MiB，因此没有证据支持跨 query 显存残留。

```text
Q3_OOM_PRIMARY_CAUSE=Expand阶段多个do_expand worker无锁并发调用同一Selector；每个调用使用未设上限的动态prompt batch，导致并发激活、logits和临时MLP张量使单卡瞬时超出40GB
CONCURRENT_SELECTOR_FORWARD=YES
INFERENCE_MODE_PRESENT=NO (literal torch.inference_mode is absent; transformers.generate has torch.no_grad)
COMPUTATION_GRAPH_RETAINED=NO
MEMORY_FRAGMENTATION_ROLE=SECONDARY
WORKER_EXCEPTION_PROPAGATION_BUG=YES
MINIMAL_FIX_RECOMMENDATION=先让worker异常可靠传播到主线程；再仅对共享Selector的infer_score调用增加全局互斥以串行化GPU forward，保留标题解析并发和每个batch内容。若串行后单个batch仍OOM，再单独评估有序micro-batch。
```

## 1. Expand 到 Selector 的调用链

完整调用链如下：

```text
single_query_runner.py
  agent.expand(depth)
    PaperAgent.expand()
      do_parallel(get_paper_content, ..., threads_num=20)
      crawler.batch_infer(crawl_prompts, batch_size=8)
      do_parallel(do_expand, ..., threads_num=20)
        do_expand()                         # 外层 Expand worker
          do_parallel(search_ref, ..., threads_num*3=60)
            search_ref()                    # 本地 title resolver，不调用 Selector
          self.selector.infer_score(select_prompts)
            Agent.infer_score()
              tokenizer(..., padding=True, truncation=True)
              self.model.generate(max_new_tokens=1, output_scores=True)
                GenerationMixin._sample()
                  Qwen2ForCausalLM.forward()
                    Qwen2Model.forward()
                      Qwen2DecoderLayer.forward()
                        Qwen2MLP.forward()
```

线程数量和共享关系：

- `PaperAgent.do_parallel()` 使用原生 `threading.Thread`，循环启动指定数量的线程，然后逐个 `join()`。
- Search 阶段创建最多 5 个 `search_paper` worker；每个 worker也可能调用同一 Selector，Search 阶段理论上最多 5 个并发 Selector forward。
- Expand 的内容获取阶段创建 20 个 `get_paper_content` worker，但这些线程不调用 Selector。
- Expand 的筛选阶段创建 20 个 `do_expand` worker，因此最多可能同时存在 20 个 Selector `infer_score()` 调用。
- 每个 `do_expand` worker内部最多再创建 60 个 `search_ref` worker。若 20 个外层 worker同时处于标题解析阶段，理论上最多约 1200 个标题解析线程；这些内层线程只构建 `select_prompts`，不直接进入 GPU forward。
- 所有外层 worker通过 `self.selector` 访问构造 `PaperAgent` 时传入的同一个 Selector 实例。`infer_score()` 调用周围没有共享锁。
- 两个 Expand depth 顺序执行；每层的 20 个外层 worker完成 `join()` 后才进入下一层，因此两层的 worker不会彼此重叠。

相关源码位置：`paper_agent.py:70-78`、`paper_agent.py:166-184`、`paper_agent.py:207-216`。

## 2. Selector inference 与 batch 形成

`models.Agent.infer_score()` 本身没有 `torch.no_grad()` 或 `torch.inference_mode()` 装饰器，也没有显式上下文管理器。不过实际调用的作者版 Transformers `GenerationMixin.generate()` 在 `generation/utils.py:1869` 有 `@torch.no_grad()`，因此模型 forward 不构建 autograd 计算图。

严格区分如下：

- `torch.inference_mode()`：没有。
- `torch.no_grad()`：有，由 `generate()` 提供。
- 计算图保留：没有证据；`generate()` 返回的 logits 不带 autograd graph。
- GPU tensor 生命周期仍然存在：每个并发调用的输入、padding 后 batch、激活、KV/cache、临时 MLP tensor 和一份输出 scores 会保留到该次调用完成。`no_grad` 只能去除 autograd graph，不能消除这些推理内存。

Selector batch 没有固定上限：

- Search：每个查询把成功读取的搜索论文组成一个 `select_prompts` batch；每个查询最多取 10 个搜索结果，去重/本地缺失后可少于 10。
- Expand：每个 `do_expand` worker每次弹出一篇父论文，从 Crawler 选择的 section 中收集引用，经本地 title resolver 和全局 arXiv-ID 去重后，将剩余的全部引用一次性传给 `infer_score()`。这里没有 batch-size cap。
- `Agent.batch_infer(batch_size=8)` 只用于 Crawler 的 section 生成，不适用于 Selector 的 `infer_score()`。
- Tokenizer 使用 `padding=True`，因此一个 Selector batch 会补齐到该 batch 中最长 prompt；显存不仅取决于 prompt 数量，也取决于最长 token 长度。现有日志没有记录每个 batch 的 token 长度。

没有发现 `torch.cuda.synchronize()`、CUDA event、Semaphore 或包围 `infer_score()` 的 inference lock。Python 列表和队列锁只保护共享数据结构，不保护 GPU forward。

## 3. Q3 OOM 栈与显存

三次异常都来自不同的 `do_expand` worker，并沿同一路径发生：

```text
paper_agent.py:184 self.selector.infer_score(select_prompts)
models.py:35 self.model.generate(...)
generation/utils.py:2217 generate -> _sample
generation/utils.py:3208 outputs = self(...)
modeling_qwen2.py:1170 Qwen2ForCausalLM.forward
modeling_qwen2.py:901 Qwen2Model.forward
modeling_qwen2.py:639 decoder layer MLP
modeling_qwen2.py:224 Qwen2MLP.forward / Linear F.linear
```

异常现场：

| Worker/逻辑 GPU | 物理 GPU | 失败申请 | Allocated | Reserved but unallocated | Free | 位置 |
|---|---:|---:|---:|---:|---:|---|
| Thread-91 或 Thread-156 / GPU 1 | 2 | 1.01 GiB | 32.62 GiB | 6.10 GiB | 110.56 MiB | Qwen2 MLP/linear |
| Thread-91 或 Thread-156 / GPU 1 | 2 | 1.35 GiB | 32.26 GiB | 6.46 GiB | 110.56 MiB | Qwen2 MLP/`F.linear` |
| Thread-44 / GPU 0 | 1 | 3.38 GiB | 26.08 GiB | 11.11 GiB | 1.63 GiB | Qwen2 MLP |

运行设置 `CUDA_VISIBLE_DEVICES=1,2`，所以异常中的逻辑 GPU 0/1 分别对应物理 GPU 1/2。

Q3 整体监控峰值为：

| 指标 | 物理 GPU 1（逻辑 0） | 物理 GPU 2（逻辑 1） |
|---|---:|---:|
| `nvidia-smi` process peak | 39014 MiB | 40372 MiB |
| Torch peak allocated | 32800.8 MiB | 35284.0 MiB |
| Torch peak reserved | 38342.0 MiB | 39700.0 MiB |

并发证据较强：

- 日志先后打印 `Thread-91 (do_expand)` 和 `Thread-156 (do_expand)`，两者的 Python 栈逐行交错，而不是一个异常完整结束后再出现另一个。
- 两个线程同时位于 `infer_score → generate → _sample → Qwen2 forward → MLP`。
- 随后第三个 `Thread-44 (do_expand)` 也在同一 Expand 阶段、同一路径发生 OOM。
- 可以确认至少两个 Selector forward 同时 in-flight；瞬时究竟是 2、3 还是更多，现有日志没有每次 forward 的开始/结束时间戳，无法精确计数。源码上限为 20。

碎片的作用属于次要放大因素。三个异常都显示 6.10–11.11 GiB 的 reserved-but-unallocated memory，数值大于失败申请，说明缓存块布局/碎片使这些空间不能满足连续分配，直接促进了 OOM。但这些碎片和高 reserved 水位是在多个不同形状 batch 的并发分配生命周期中形成的；根本压力仍是共享 Selector 的无锁并发 forward 与动态大 batch。仅凭现有日志不能证明在完全串行时同样会 OOM。

## 4. Q0–Q3 对比

现有 instrumentation 在进入 `infer_score()` 前记录调用数和 prompt 数。对成功输出树逐父节点统计 children，可重建成功的 Expand batch；Q3 的三个失败调用没有写入 children。

| Query | Selector calls | Selector prompts | Search prompts / calls | Expand attempts | Expand attempted prompts | 成功 Expand batch 最大值 | Expand nodes | Local lookups | GPU peak MiB（物理 1 / 2） | 并发 forward |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Q0 | 54 | 540 | 29 / 5 | 49 | 511 | 64 | 511 | 1452 | 31582 / 36322 | 上限 20；实际数未知 |
| Q1 | 52 | 593 | 27 / 5 | 47 | 566 | 101 | 566 | 1721 | 39650 / 40268 | 上限 20；实际数未知 |
| Q2 | 51 | 441 | 26 / 5 | 46 | 415 | 36 | 415 | 1432 | 25698 / 29146 | 上限 20；实际数未知 |
| Q3 | 61 | 937 | 36 / 5 | 56 | 901 | 38（仅成功 batch） | 668（不完整） | 2448 | 39014 / 40372 | 至少 2，可能更多，上限 20 |

Q3 的 901 个 Expand prompts 中只有 668 个出现在成功结果树。三个失败调用在 wrapper 中已经先计入 prompts，但在 `infer_score()` 抛错后没有机会创建子节点，因此可推断三个失败 batch 合计有 233 个 prompts，平均约 77.7 个；现有记录不能恢复各自的精确 batch size。Q3 每次 Expand 调用平均 16.09 prompts，Q1 为 12.04，Q0 为 10.43，Q2 为 9.02。

Q1 虽然有一个成功 batch 达到 101 prompts，但 batch prompt 数量不是唯一决定因素：padding 后的最长序列长度、同一时刻其他 worker 的 batch 数量与大小，以及 allocator 当时的碎片都会改变峰值。Q1 的物理 GPU 2 峰值已达到 40268 MiB，距离 Q3 的 40372 MiB 很近，说明 Q1 本身就是临界通过。Q3 总 prompts 更多、调用更多，并且日志明确记录多个较大的失败 batch并发处于 forward 中，最终需要额外 1.01–3.38 GiB 时无法满足。

## 5. Worker 异常传播

`PaperAgent.do_parallel()` 使用裸 `threading.Thread`：

```python
thread = threading.Thread(target=func, args=args)
thread.start()
...
thread.join()
```

Python 子线程异常不会由 `Thread.join()` 自动重新抛到主线程；它只调用 `threading.excepthook` 并结束对应线程。因此三个 `do_expand` worker失败后，其余线程继续执行，`do_parallel()` 最终正常返回。

本次临时 runner 注册了自定义 `threading.excepthook`，所以三个 OOM 被保存进 `metrics.thread_exceptions`；但 runner 在 `agent.expand()` 返回后无条件把 `report.status` 改成 `PASS`，没有检查该列表。调度器随后只检查子进程 exit code 和 `runner_status`。两者都显示成功，因此它开始了 Q4。日志人工核查发现隐藏 OOM 后，Q4 在进入 Search 前被中断，Serper 调用数为 0。

这是明确的异常传播缺陷，并导致 Q3 生成了不完整但表面上标记为成功的结果。

## 最小修复建议（本次未实施）

1. 正确性优先：让 `do_parallel()` 收集子线程异常，并在全部线程 join 后由主线程重新抛出；测试 runner 也应在 `thread_exceptions` 非空时强制 FAIL。这会防止部分结果被误报为 PASS，也会阻止下一题启动。
2. 显存优先：为同一个 Selector 实例的 `infer_score()` 增加一个全局互斥锁，只串行化 Selector GPU forward。标题解析、Crawler 和原有每个 prompt batch 内容可以保持不变。
3. 若串行化后单个动态 batch仍会 OOM，再评估保持顺序的 Selector micro-batch。由于拆 batch 可能带来细小数值差异，应在后续单独验证，不能从本次只读审计直接实施。

基于现有源码和日志，第一、二项足以分别处理“错误未上报”和“并发显存峰值”两个已证实的问题。
