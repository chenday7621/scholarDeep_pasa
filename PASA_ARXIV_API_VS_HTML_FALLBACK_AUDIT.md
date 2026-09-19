# PaSa arXiv API 与 HTML fallback 小实验

## 范围与方法

- 样本：Q0 `smoke_report.json` 的 `failed_titles` 中 24 个不同、外观上像论文标题的真实 `LOCAL_TITLE_MISS`。
- A：`https://arxiv.org/search/`，参数与当前 PaSa HTML fallback 相同。
- B：`https://export.arxiv.org/api/query`，使用 `search_query=ti:"<title>"`、`max_results=10`。
- 两批均严格串行；包括 retry 在内，相邻请求启动至少间隔 3 秒。API 实测最小间隔 3.000563s，HTML 实测最小间隔 3.001512s。
- 只对 429、timeout、临时连接异常和 5xx 最多额外重试一次。API 批次结束后无请求冷却 5 分钟，再开始 HTML 批次。
- “成功”表示最终 HTTP 200 且响应可正常解析；“ID found / 预期标题命中”表示候选标题通过当前 PaSa 的 `_normalized_title()` 严格相等比较后得到 ID。正常的空结果响应计为端点成功，但不计为 ID found。
- 延迟按实际 HTTP attempt 统计，包含失败响应；快速返回的 429/500 会压低平均值。

## 汇总

```text
TEST_TITLES=24
HTML_SUCCESS=1
HTML_429=33
HTML_TIMEOUTS=0
API_SUCCESS=14
API_429=20
API_TIMEOUTS=0
API_ID_FOUND=9
HTML_ID_FOUND=1
ID_AGREEMENT=1/1
API_AVG_LATENCY=0.553s
HTML_AVG_LATENCY=0.626s
```

补充统计：API 共 34 次 HTTP attempt（10 次 retry），429 影响 10/24 个标题；HTML 共 47 次 attempt（23 次 retry），429 影响 17/24 个标题，另有 `HTTP 500=13`。仅看 HTTP 200 响应，API 平均延迟 0.764s，HTML 平均延迟 3.788s。

## 逐标题结果

| # | Citation title | HTML 状态与延迟 | HTML 成功 | HTML ID | HTML 预期标题 | API 状态与延迟 | API 成功 | API ID | API 预期标题 | ID 一致 |
|---:|---|---|:---:|---|:---:|---|:---:|---|:---:|:---:|
| 1 | On the opportunities and risks of foundation models | 200 (3.788s) | Y | 2108.07258 | Y | 200 (2.448s) | Y | 2108.07258 | Y | Y |
| 2 | Self-instruct: Aligning language models with self-generated instructions | 500 (1.024s) → 500 (0.772s) | N | — | N | 200 (0.653s) | Y | 2212.10560 | Y | N/A |
| 3 | Autonomous data selection with language models for mathematical texts | 500 (1.497s) → 500 (0.771s) | N | — | N | 200 (0.485s) | Y | — | N | N/A |
| 4 | Mamba: Linear-time sequence modeling with selective state spaces | 500 (0.721s) → 500 (0.780s) | N | — | N | 200 (0.521s) | Y | 2312.00752 | Y | N/A |
| 5 | Gemini: A family of highly capable multimodal models | 500 (1.169s) → 500 (1.154s) | N | — | N | 200 (1.817s) | Y | 2312.11805 | Y | N/A |
| 6 | D2 pruning: Message passing for balancing diversity and difficulty in data pruning | 500 (0.807s) → 500 (0.763s) | N | — | N | 200 (0.525s) | Y | 2310.07931 | Y | N/A |
| 7 | React: Synergizing reasoning and acting in language models | 500 (0.864s) → 500 (0.735s) | N | — | N | 200 (0.686s) | Y | 2210.03629 | Y | N/A |
| 8 | The refinedweb dataset for falcon llm: Outperforming curated corpora with web data only | 500 (1.102s) → 429 (0.392s) | N | — | N | 200 (0.455s) | Y | — | N | N/A |
| 9 | Atlas: Few-shot learning with retrieval augmented language models | 429 (0.409s) → 429 (0.377s) | N | — | N | 200 (0.514s) | Y | 2208.03299 | Y | N/A |
| 10 | Retrieval augmented language model pre-training | 429 (0.396s) → 429 (0.400s) | N | — | N | 200 (0.519s) | Y | — | N | N/A |
| 11 | Scaling language models: Methods, analysis and insights from training gopher, 2021. | 429 (0.387s) → 429 (0.372s) | N | — | N | 200 (0.544s) | Y | — | N | N/A |
| 12 | Sheared llama: Accelerating language model pre-training via structured pruning | 429 (0.403s) → 429 (0.447s) | N | — | N | 200 (0.505s) | Y | 2310.06694 | Y | N/A |
| 13 | Qwen-vl: A frontier large vision-language model with versatile abilities | 429 (0.451s) → 429 (0.402s) | N | — | N | 200 (0.513s) | Y | — | N | N/A |
| 14 | Self-rag: Learning to retrieve, generate, and critique through self-reflection | 429 (0.573s) → 429 (0.359s) | N | — | N | 200 (0.514s) | Y | 2310.11511 | Y | N/A |
| 15 | Instructeval: Towards holistic evaluation of instruction-tuned large language models | 429 (0.655s) → 429 (0.507s) | N | — | N | 429 (0.360s) → 429 (0.394s) | N | — | N | N/A |
| 16 | Xtreme: A massively multilingual multi-task benchmark for evaluating cross-lingual generalisation | 429 (0.392s) → 429 (0.393s) | N | — | N | 429 (0.401s) → 429 (0.428s) | N | — | N | N/A |
| 17 | Camels in a changing climate: Enhancing lm adaptation with tulu 2 | 429 (0.379s) → 429 (0.373s) | N | — | N | 429 (0.423s) → 429 (0.504s) | N | — | N | N/A |
| 18 | Continual learning under language shift | 429 (0.363s) → 429 (0.373s) | N | — | N | 429 (0.409s) → 429 (0.365s) | N | — | N | N/A |
| 19 | Search augmented instruction learning | 429 (0.471s) → 429 (0.376s) | N | — | N | 429 (0.383s) → 429 (0.413s) | N | — | N | N/A |
| 20 | Dataset Deduplication with Datamodels | 429 (0.393s) → 429 (0.373s) | N | — | N | 429 (0.392s) → 429 (0.519s) | N | — | N | N/A |
| 21 | Jamming transition as a paradigm to understand the loss landscape of deep neural networks | 429 (0.367s) → 429 (0.368s) | N | — | N | 429 (0.388s) → 429 (0.381s) | N | — | N | N/A |
| 22 | Reconciling modern machine learning and the bias-variance trade-off | 429 (0.387s) → 429 (0.367s) | N | — | N | 429 (0.357s) → 429 (0.386s) | N | — | N | N/A |
| 23 | T-mars: Improving visual representations by circumventing text feature learning | 429 (0.396s) → 429 (0.388s) | N | — | N | 429 (0.379s) → 429 (0.411s) | N | — | N | N/A |
| 24 | Model dementia: Generated data makes models forget | 429 (0.373s) → 429 (0.389s) | N | — | N | 429 (0.402s) → 429 (0.398s) | N | — | N | N/A |

API 的 14 个有效响应中，9 个严格命中预期标题并得到 ID；5 个没有严格命中。第 10 个标题 `Retrieval augmented language model pre-training` 返回候选 `REALM: Retrieval-Augmented Language Model Pre-Training`（`2002.08909`），但因引用标题缺少前缀，依照当前 PaSa 语义不计为命中。其余四个有效 API 响应为空结果。

## 判断

1. **API 在本轮比 HTML 稳定，但仍不足以称为稳定 fallback。** API 有效响应率为 14/24（58.3%），HTML 为 1/24（4.2%）；API 没有 500 或 timeout，而 HTML 有 13 次 500。两者随后都进入持续 429，API 的 3 秒间隔并未避免限流。
2. **两边的 title → ID 一致性证据不足。** 两端都实际解析到 ID 的交集只有 1 个，该 ID 一致（`2108.07258`，即 1/1）。由于 HTML 大面积 500/429，无法据此证明两种方法在整批标题上“基本一致”。API 已取得的 9 个精确 ID 与返回标题自身一致，但缺少同批 HTML 对照。
3. **值得做下一步受控验证，但不宜现在直接替换正式 fallback。** API 显著改善了可用响应和 ID 产出，方向值得继续；在改源码前，应先查明 arXiv 对该出口/IP/User-Agent 的限流窗口，并在充分冷却后用更低速率或官方建议的节流方式做交叉验证。若正式采用，还需保留本地 resolver、有限 retry、全局 cooldown，以及严格标题核验，避免 API 候选前缀差异改变现有匹配语义。

## 原始产物

- `api_attempts.jsonl` / `html_attempts.jsonl`：每次请求的 UTC 时间、状态、异常、延迟与解析结果。
- `api_results.json` / `html_results.json`：每个标题的最终结果和完整 attempt 列表。
- `api_summary.json` / `html_summary.json`：批次统计。
- 目录：`/mnt/nvme3/chenyi/tmp/pasa-arxiv-api-vs-html/run-20260909`

本实验未加载模型、未运行 RealScholarQuery，也未修改 PaSa 正式 fallback 源码。
