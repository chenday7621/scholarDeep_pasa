# PAGE2_ROUTING_PREREG_VALIDATION_003

**已按用户协议停在静态兼容性 gate；未抽样、未生成、未 Search。**

原因：`STOPPED_MAPPING_AMBIGUITY`。这不是 Router 成功或失败的效果结果。

| 来源 | specific题数 | 全gold兼容题数 | 不兼容题数 | 要求抽样 |
|---|---:|---:|---:|---:|
| author-written | 211 | 164 | 47 | 25 |
| inline-citation | 231 | 165 | 66 | 25 |

## 数据来源与口径

- [官方 LitSearch 数据集](https://huggingface.co/datasets/princeton-nlp/LitSearch)，固定 revision `9573fb284a1026c998df47024b888a163f0f0e25`。6 份 query API response 的 X-Revision 均与该版本一致。
- [官方论文 Table 1/2](https://aclanthology.org/2024.emnlp-main.840.pdf)确认 specificity=1，specific 共 211 author-written / 231 inline-citation；合计 442 题、432 个 unique gold corpusid。
- 数据查看器 filter 接口对批量和单 ID 请求均返回 HTTP 500，改用固定 revision 的 Parquet HTTP Range，只读取 corpusid/title 列及 footer；不读取 corpus 的 abstract/full_paper 列。
- 读取列及 footer 共 3,642,569 bytes，提取 432 个所需 corpusid/title；未下载完整 2.85GB corpus。独立 vendor 中 PyArrow 安装包约 50.1 MB，不属于 corpus 下载，未改 PaSa 环境依赖。

## 静态兼容性

- AST 复用原 utils.keep_letters 和 _build_local_title_index，未导入模型或执行项目在线工具。要求每题全部 gold 均可唯一映射，并核对 ZIP 中原始标题归一化一致和 native parser 的 ID 格式。
- 不依据 Search/Page2 outcome 过滤，不使用质量、主题、词面分数，不丢弃某题的未映射 gold 后缩小分母。
- gold 映射统计：`{'local_title_miss': 113, 'compatible': 315, 'empty_normalized_title': 3, 'ambiguous_local_title': 1}`。

## 必须停止的映射异常

1. `{"type": "ambiguous_local_title", "corpusid": 258960101, "title": "DNA-GPT: DIVERGENT N-GRAM ANALYSIS FOR TRAINING-FREE DETECTION OF GPT-GENERATED TEXT", "arxiv_ids": ["2303.02909", "2305.17359"]}`

用户要求“若数据映射存在歧义，先停止并报告，不自行修改实验定义”。即使某组兼容数量已够，也未自行忽略、修复或选择一个候选 ID；正式抽样保持 0。

## 预注册与执行状态

- PREREGISTRATION.md 已冻结用户指定方向、每题 top1、tie-break、1000 次 Random、评测和失败处理，但明确标记 **NOT_ACTIVATED_GATE_STOP**。不存在完成抽样后的有效 50 题 preregistration。
- PREREGISTRATION.md SHA256：`d084f7a5fe253e7f00e06b7d3222f51f96c503df886303c579c542787264d2f8`。
- dataset_manifest.json 保存全部 442 题兼容性、432 个 gold 映射和源哈希；snapshot_manifest/states/decisions 均显式未执行，results 指标为 null，不伪造 0 收益。
- Crawler generation=0；Serper Search=0；Page1=0；Page2=0；正式 paper_agent.py 等源码哈希未变。没有比较 policy、调方向或挑预算。

## 验证

- query 数据版本、specific 来源计数、全部本地索引函数和源码哈希已核对；金标题来自固定版本列数据。
- 停止时没有生成 50 题样本，沒有新实验响应；所有效果指标未定义。
- 兼容性结果可用 `python3 -B page2_routing_prereg_validation_003/compatibility.py` 在冻结前复算；冻结后不覆盖原 manifest，后续修订须独立版本。
