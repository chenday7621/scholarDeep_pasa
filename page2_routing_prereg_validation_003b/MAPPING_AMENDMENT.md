# MAPPING_AMENDMENT — identity resolution only

冻结时间 UTC：2026-09-17T05:46:32.264899+00:00

## 唯一映射修订规则

- 同一 normalized gold title 对应多个本地 arXiv ID 时，只允许依据静态官方论文身份 metadata 核验。
- 禁止依据 Page1/Page2 Search outcome、GT gain 或后续实验结果选择 ID。
- 只有一个候选的官方 arXiv title/metadata 与 gold paper 身份一致时保留该 ID，其余视为本地 index 错误；仍无法唯一确定则立即停止。
- 只处理一对多 identity conflict；不扩大 fuzzy matching，不补普通 title miss，不改原 keep_letters，不修改正式本地 index。

## 静态核验结论与证据

审计原冻结的 442 个 specific questions、432 个不同 gold corpusid，仅发现 DNA-GPT 这一处 normalized title → multiple arXiv IDs。

- corpusid=258960101；保留 `2305.17359`，官方标题为 DNA-GPT: Divergent N-Gram Analysis for Training-Free Detection of GPT-Generated Text。
- `2303.02909` 官方标题为 Dynamic Prompting: A Unified Framework for Prompt Tuning，拒绝本地索引中的错误 DNA-GPT 关联。
- 官方来源：https://arxiv.org/abs/2305.17359 、https://arxiv.org/abs/2303.02909 。
- 原始 HTML、HTTP 来源/时间、citation metadata 和逐文件 SHA-256 存于原 003 的 identity_evidence/。
- identity_resolution.json SHA-256：`42e38a4ad780aec2a96c1631e958a8118d2a9d239eda104add97453ab7aa7276`。
- 原 003 全部已存停止记录与原 PREREGISTRATION.md 保持不变；本修订不改变其历史停止结论。

## 003B 继承与激活

003B 的 PREREGISTRATION.md 是原 003 文件的逐字节副本，SHA-256 `d084f7a5fe253e7f00e06b7d3222f51f96c503df886303c579c542787264d2f8`。其中原 003 名称、冻结日期、旧 dataset hash、旧兼容计数及“未激活/停止”段落是历史记录；本用户授权的 003B 通过本 amendment 唯一解决 identity gate 后独立激活，并以 registration_manifest.json 和新的 dataset_manifest.json 记录状态。

除此 identity-resolution amendment 和必要的新版本执行记录外，所有实验条件保持不变：seed=20260917、先 author-written 25 再 inline-citation 25、原 Crawler 每题 seed=42、原 prompt/parser/generation 配置、before:2026-09-17、每 query 配对 Page1/Page2 Top10、每题 max_jaccard top1、并列原生成序号最小、Random 1000 trials、原统计口径及停止规则。

本文件及继承协议在抽样、任何 Crawler/Search 之前冻结；不按新数据结果调参、改变方向或重抽样。
