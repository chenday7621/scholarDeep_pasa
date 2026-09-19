# PaSa 单条 RealScholarQuery 审计

## 范围与口径

- 样本：`RealScholarQuery_0`
- Query：`Give me papers which show that using a smaller dataset in large language model pre-training can result in better models than using bigger datasets.`
- GT 来源：`data/RealScholarQuery/test.jsonl` 第一行。
- 推理结果：`results/smoke-real-20260908-flash/0.json`。
- 运行观测：`results/smoke-real-20260908-flash/smoke_report.json` 和 `run.log`。
- 本报告仅分析既有文件和源码，没有重跑 inference 或访问网络。
- 指标沿用官方 `metrics.py`：论文标题只保留字母并转小写后做精确集合匹配；Selector 阈值为 `score > 0.5`。
- “直接 Search”仅指深度 0 的搜索结果；“Crawler”按官方指标指 Selector 前的全部 Search 和 Citation Expand 候选。

## 指标

| 指标 | 数值 |
|---|---:|
| GT 总数 | 9 |
| 直接 Search 命中 | 1 |
| Citation Expand 新增 GT | 2 |
| 完整 Crawler 候选命中 | 3 |
| 最终返回论文 | 8 |
| 最终 GT 命中（TP） | 2 |
| FP / FN | 6 / 7 |
| Final Precision | 0.2500 |
| Final Recall | 0.2222 |
| Final F1 | 0.2353 |

直接 Search 找到 `How to Train Data-Efficient LLMs`。Citation Expand 又找到 `Deduplicating Training Data Makes Language Models Better` 和 `AlpaGasus: Training A Better Alpaca with Fewer Data`。Selector 保留前者和 AlpaGasus，但把 Deduplicating 以 `0.0614` 的分数删掉。

## 逐个 GT 漏失分析

| arXiv ID | GT | 到达阶段与证据 | 结论 |
|---|---|---|---|
| 2309.04564 | When Less is More: Investigating Data Pruning for Pretraining LLMs at Scale | 未进入节点或 `touch_ids`；标题出现在 3 个已搜到论文的引用表中，但对应 section 没有生成 child | **Citation Expand 未覆盖**。既有结果不能区分 section 未被 Crawler 选择和该 section 的引用解析全部失败；网络原因可能但无法确认 |
| 2402.09668 | How to Train Data-Efficient LLMs | 深度 0 Search，score `0.9793` | **最终命中** |
| 2107.06499 | Deduplicating Training Data Makes Language Models Better | 深度 1 Expand，score `0.0614` | **Selector 误删** |
| 2307.08701 | AlpaGasus: Training A Better Alpaca with Fewer Data | 深度 1 Expand，score `0.8671` | **最终命中** |
| 2305.02301 | Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes | 未进入节点；标题出现在 `Data-Centric AI in the Age of Large Language Models` 的引用表中，对应 section 没有 child | **Citation Expand 未覆盖**；section 选择与引用请求失败无法进一步区分 |
| 2402.04333 | LESS: Selecting Influential Data for Targeted Instruction Tuning | 标题位于 `Amuro & Char` 的已选 section；该 section 成功生成了 6 个其他 child，但此 GT 未进入 `touch_ids` | **标题解析失败/无法判断**。可以确认调用了 `search_paper_by_title`，但日志没有把标题与 reset/429 逐请求关联；可能是网络失败，也可能是 arXiv 搜索页精确标题匹配失败 |
| 2210.10951 | Automatic Document Selection for Efficient Encoder Pretraining | 未出现在节点、`touch_ids` 或任何已抓取引用表中 | **Search/Crawler 未召回** |
| 2305.12816 | Farewell to aimless large-scale pretraining: Influential subset selection for language model | 标题出现在深度 0 的 `A Survey of Large Language Models` 引用表中；该父节点标记为 `not expand` | **Citation Expand 未覆盖** |
| 2409.17312 | Babyllama-2: Ensemble-distilled models consistently outperform teachers with limited data | 未出现在节点、`touch_ids` 或任何已抓取引用表中 | **Search/Crawler 未召回** |

漏失归类汇总（7 个 FN）：

- Search/Crawler 搜索图中完全没有覆盖：2。
- 已存在引用线索但 Citation Expand 未覆盖：3。
- Selector 误删：1。
- 标题解析失败且无法从现有日志区分网络/匹配原因：1。
- 可逐条证明确由网络失败造成：0；有 1 个 GT 属于网络原因高度可疑但不可证实。

9 个 GT 的 ID、标题和正文记录都存在于本地 `id2paper.json` 与 `cs_paper_2nd.zip`。因此 GT 缺失不是数据文件不完整造成的；Citation Expand 仍须先通过 arXiv 搜索页把引用标题解析为 arXiv ID，之后才能命中本地库。

## 网络异常与调用链

### 观测统计

| 入口 | URL | 调用数 | 结果 |
|---|---|---:|---|
| Serper 搜索 | `https://google.serper.dev/search` | 5 | 5 次 HTTP 200 |
| arXiv 标题搜索 | `https://arxiv.org/search/?query=...&searchtype=title&abstracts=hide&size=200` | 1379 | 814 次 connection reset、12 次 remote disconnect、396 次 HTTP 429，共 1222 次网络失败（88.61%）；另有 40 次页面未返回可接受结果 |
| arXiv API | `https://export.arxiv.org/api/query?...` | 推断为 1 次 | 本地库外的 `2403.08763` 成功返回；无 `Failed to search arxiv id` 警告 |
| ar5iv HTML | `https://ar5iv.labs.arxiv.org/html/2403.08763` | 1 | 成功解析为 19 个 section；无 ar5iv HTTP/HTML/解析失败 |

connection reset 和 429 均由 `utils.search_arxiv_id_by_title()` 的 `requests.get()` 路径产生。异常消息没有记录请求 URL 或引用标题，所以无法从既有日志恢复 1222 个失败各自对应的完整 URL。对 GT `LESS`，按源码和引用标题可以重建预期 URL：

```text
https://arxiv.org/search/?query=Less%3A+Selecting+influential+data+for+targeted+instruction+tuning&searchtype=title&abstracts=hide&size=200
```

但无法证明该次请求属于 reset、429，还是返回 200 后精确标题匹配失败。

### Search 调用链

```text
PaperAgent.run
  -> PaperAgent.search
    -> Crawler.infer（生成 5 个 query）
    -> do_parallel(search_paper, 5)
      -> google_search_arxiv_id
        -> POST google.serper.dev/search
      -> search_paper_by_arxiv_id
        -> 本地 id2paper + ZIP（优先）
        -> arxiv.Client.results -> export.arxiv.org/api/query（本地没有时）
      -> Selector.infer_score
```

### Citation Expand 调用链

```text
PaperAgent.run
  -> PaperAgent.expand
    -> do_parallel(get_paper_content, 20)
      -> 本地 sections
      -> search_section_by_arxiv_id -> GET ar5iv HTML（sections 为空时）
    -> Crawler.batch_infer（选择 section）
    -> do_parallel(do_expand, 20)
      -> 每个活跃父论文 do_parallel(search_ref, threads_num * 3 = 60)
        -> search_paper_by_title
          -> search_arxiv_id_by_title
            -> GET arxiv.org/search/?query=<引用标题>...
          -> search_paper_by_arxiv_id
            -> 本地库优先，否则 arXiv API
        -> Selector.infer_score
```

### 并发、重复、retry、backoff、cache

- Search 阶段最多 5 个 query worker。
- Expand 阶段有 20 个 `do_expand` worker；每个活跃父论文又创建 60 个 `search_ref` worker，峰值理论上可同时出现约 1200 个内层标题查询线程。这与 arXiv 搜索页的 429 和连接重置高度一致。
- `search_arxiv_id_by_title` 和 `search_section_by_arxiv_id` 都只有单次 `requests.get`，没有 timeout、retry 或 backoff。
- arXiv Python Client 默认 `num_retries=3`，即首次请求失败后最多再试 3 次；这里只设置了固定 `delay_seconds=0.05`，没有指数 backoff。本次没有观察到 API 失败。
- Serper 代码最多尝试 3 次，没有 backoff；本次 5 个 query 都首次成功。
- 本地 `id2paper` 和 ZIP 是按 arXiv ID 的论文缓存，但没有“引用标题 -> arXiv ID”缓存。
- `touch_ids` 只在标题查询成功并解析出 ID 后去重。因此同一标题在并发请求失败期间可以被重复查询；即使多个请求成功，去重也发生在网络请求之后。

### 失败处理及实际影响

- arXiv 标题搜索发生 reset/disconnect 时捕获异常、返回 `None`；HTTP 非 200（包括 429）同样返回 `None`。`search_ref` 随即 `continue`，该引用不会进入 Crawler 候选，也不会交给 Selector。
- ar5iv 获取或解析失败时，父论文会标记 `expand = get full paper error`，整篇论文的引用扩展被跳过。本次没有发生。
- arXiv API 失败时 `search_paper_by_arxiv_id` 返回 `None`，对应搜索结果直接丢失。本次没有发生。
- 1222 次标题搜索网络失败确定造成大量引用候选请求被丢弃；但日志没有记录失败请求的标题，且同一标题可能重复请求，因此不能从“请求失败次数”换算为“丢失的唯一论文数”。
- 对 GT 的可确认影响为 0 个；`LESS` 是 1 个直接进入标题查询但原因不可回溯的 GT miss。网络失败也可能间接阻断通向其他 GT 的第二层引用路径，现有产物无法量化。

## 最终字段

```text
GT_TOTAL=9
CRAWLER_GT_FOUND=3
FINAL_GT_FOUND=2
FINAL_PRECISION=0.2500
FINAL_RECALL=0.2222
FINAL_F1=0.2353
NETWORK_FAILURES=1222
NETWORK_CAUSED_GT_MISS=0（可确认；另有 1 个直接可疑但无法归因）
MAIN_FAILURE_STAGE=Crawler/Citation Expand 候选召回（6/9 GT 未进入候选集；之后 Selector 再误删 1 个）
```
