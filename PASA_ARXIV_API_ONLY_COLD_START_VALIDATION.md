# PaSa arXiv API-only 冷启动验证

## 范围与条件

- 只请求 `https://export.arxiv.org/api/query`，参数为 `search_query=ti:"<title>"`。
- 标题来自 Q0 `failed_titles`：1 个独立探针标题，24 个不同的正式测试标题。
- 上一轮最后请求到本轮探针前冷却约 9029 秒（约 2.5 小时）。
- 全程使用同一个 `requests.Session`，连接池大小为 1，严格串行，无并发、burst 和 retry。
- 探针和正式请求均经过同一个 3 秒启动间隔 limiter。
- 探针结果：HTTP 200，解析=PASS，延迟 1.294s。探针通过后才开始正式测试。
- `API_ID_FOUND` 只统计通过当前 PaSa `_normalized_title()` 严格标题相等规则取得的 ID；可解析的空 feed 仍计为 API 成功。

## 汇总

```text
TEST_TITLES=24
REQUESTS_STARTED=24
MIN_REQUEST_START_SPACING=3.001034s
MAX_REQUESTS_IN_ANY_1S_WINDOW=1
HTTP_200=23
HTTP_429=1
TIMEOUTS=0
FIRST_429_AT=24
API_ID_FOUND=12
API_SUCCESS_RATE=95.83%
API_429_RATE=4.17%
API_ONLY_STABLE=YES
```

`REQUESTS_STARTED=24` 只统计正式测试，另有 1 次测试前探针。把探针也纳入启动间隔核验后，最小间隔为 3.001034s。

## 逐请求结果

| Sequence | Title | UTC request timestamp | HTTP | Latency | Atom 正常解析 | 严格匹配 arXiv ID |
|---:|---|---|---:|---:|:---:|---|
| 1 | Instructeval: Towards holistic evaluation of instruction-tuned large language models | `2026-09-09T11:41:37.022931+00:00` | 200 | 0.589s | Y | 2306.04757 |
| 2 | Xtreme: A massively multilingual multi-task benchmark for evaluating cross-lingual generalisation | `2026-09-09T11:41:40.025360+00:00` | 200 | 0.460s | Y | — |
| 3 | Camels in a changing climate: Enhancing lm adaptation with tulu 2 | `2026-09-09T11:41:43.027921+00:00` | 200 | 0.477s | Y | 2311.10702 |
| 4 | Continual learning under language shift | `2026-09-09T11:41:46.030464+00:00` | 200 | 0.508s | Y | 2311.01200 |
| 5 | Search augmented instruction learning | `2026-09-09T11:41:49.032976+00:00` | 200 | 5.620s | Y | — |
| 6 | Dataset Deduplication with Datamodels | `2026-09-09T11:41:54.653070+00:00` | 200 | 0.460s | Y | — |
| 7 | Jamming transition as a paradigm to understand the loss landscape of deep neural networks | `2026-09-09T11:41:57.655638+00:00` | 200 | 0.615s | Y | — |
| 8 | Reconciling modern machine learning and the bias-variance trade-off | `2026-09-09T11:42:00.658042+00:00` | 200 | 0.461s | Y | — |
| 9 | T-mars: Improving visual representations by circumventing text feature learning | `2026-09-09T11:42:03.660601+00:00` | 200 | 0.471s | Y | 2307.03132 |
| 10 | Model dementia: Generated data makes models forget | `2026-09-09T11:42:06.663157+00:00` | 200 | 0.453s | Y | — |
| 11 | On the opportunities and risks of foundation models | `2026-09-09T11:42:09.665720+00:00` | 200 | 0.627s | Y | 2108.07258 |
| 12 | Self-instruct: Aligning language models with self-generated instructions | `2026-09-09T11:42:12.668115+00:00` | 200 | 0.485s | Y | 2212.10560 |
| 13 | Autonomous data selection with language models for mathematical texts | `2026-09-09T11:42:15.670648+00:00` | 200 | 0.483s | Y | — |
| 14 | Mamba: Linear-time sequence modeling with selective state spaces | `2026-09-09T11:42:18.673182+00:00` | 200 | 0.581s | Y | 2312.00752 |
| 15 | Gemini: A family of highly capable multimodal models | `2026-09-09T11:42:21.675622+00:00` | 200 | 1.402s | Y | 2312.11805 |
| 16 | D2 pruning: Message passing for balancing diversity and difficulty in data pruning | `2026-09-09T11:42:24.677238+00:00` | 200 | 0.575s | Y | 2310.07931 |
| 17 | React: Synergizing reasoning and acting in language models | `2026-09-09T11:42:27.679682+00:00` | 200 | 0.478s | Y | 2210.03629 |
| 18 | The refinedweb dataset for falcon llm: Outperforming curated corpora with web data only | `2026-09-09T11:42:30.682230+00:00` | 200 | 0.654s | Y | — |
| 19 | Atlas: Few-shot learning with retrieval augmented language models | `2026-09-09T11:42:33.684594+00:00` | 200 | 0.476s | Y | 2208.03299 |
| 20 | Retrieval augmented language model pre-training | `2026-09-09T11:42:36.687138+00:00` | 200 | 0.641s | Y | — |
| 21 | Scaling language models: Methods, analysis and insights from training gopher, 2021. | `2026-09-09T11:42:39.689516+00:00` | 200 | 0.481s | Y | — |
| 22 | Sheared llama: Accelerating language model pre-training via structured pruning | `2026-09-09T11:42:42.692055+00:00` | 200 | 1.983s | Y | 2310.06694 |
| 23 | Qwen-vl: A frontier large vision-language model with versatile abilities | `2026-09-09T11:42:45.693088+00:00` | 200 | 0.476s | Y | — |
| 24 | Self-rag: Learning to retrieve, generate, and critique through self-reflection | `2026-09-09T11:42:48.695632+00:00` | 429 | 0.366s | N | — |

## 判断

1. **本轮没有复现“前若干次成功、随后持续 429”。** 前 23 个正式请求连续返回可解析的 HTTP 200，第 24 个请求返回一次 429；没有连续 429，因此也未触发“连续 3 个 429 提前停止”。
2. **API-only 在这次充分冷却的小样本中基本稳定。** 正式请求成功率为 95.83%，429 率为 4.17%，无 timeout 或其他 HTTP 异常。不过最后一次 429 表明 API 仍会限流，不能把单轮结果理解为始终不会出现 429。
3. **值得把 API 作为正式 fallback 的候选。** 结合上一轮 API 对 HTML 的明显优势以及本轮 23/24 的可解析响应，下一步可以用 API 替代 HTML 路径做最小实现验证。正式实现仍应保留 local resolver 优先、全局低频、有限 retry/cooldown、缓存和严格标题核验。
4. **不建议继续追求通过调节 arXiv 限速把 429 降到绝对为零。** 当前证据足以说明 API 更适合作为受保护的 fallback；服务端限流具有波动性，应由有限失败处理吸收，而不是继续扩大请求实验。

## 原始产物

- `/mnt/nvme3/chenyi/tmp/pasa-arxiv-api-only/run-20260909/probe.json`
- `/mnt/nvme3/chenyi/tmp/pasa-arxiv-api-only/run-20260909/requests.jsonl`
- `/mnt/nvme3/chenyi/tmp/pasa-arxiv-api-only/run-20260909/results.json`
- `/mnt/nvme3/chenyi/tmp/pasa-arxiv-api-only/run-20260909/summary.json`

本实验未访问 HTML、未加载模型、未运行 RealScholarQuery，也未修改 PaSa 正式 fallback 源码。
