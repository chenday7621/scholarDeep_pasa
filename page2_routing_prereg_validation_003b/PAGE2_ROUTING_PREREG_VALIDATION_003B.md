# PAGE2_ROUTING_PREREG_VALIDATION_003B

## 结论

Jaccard Router 在每题 1 次额外 Page2 logical call 下新增 **0 个 normalized GT**；incremental micro recall=0.0000，incremental macro recall=0.0000。
1000 次固定 seed Random 中，Random ΔGT >= Router 的经验概率为 **1.0000**；加一 Monte Carlo p=1.0000。

该结果按冻结协议完整报告；未根据这 50 题修改方向、threshold、feature、weight、seed、样本或 budget。

## 数据与冻结

- Princeton LitSearch specific questions：25 author-written + 25 inline-citation。
- 抽样 seed：20260917；Crawler 每题 generation seed：42。
- normalized GT 总数：50。
- native query 总数：222。
- 实际冻结 Page1/Page2 response：222/222。
- snapshot ID：`6c0a3ea5d79b1667966a2dada5c89700218bf48f363b9b7c9b32eb75688d6d95`。
- 实际采集为所有 native queries 的 Page1/Page2；各 policy 均 replay 同一 snapshot。

## Policy 结果

| Policy | GT found | Macro recall | Micro recall | ΔGT | Page2 calls | ΔGT/call | Always gain retention |
|---|---:|---:|---:|---:|---:|---:|---:|
| Native Page1 | 12/50 | 0.2400 | 0.2400 | 0 | 0 | NA | NA |
| Jaccard Router | 12/50 | 0.2400 | 0.2400 | 0 | 50 | 0.0000 | NA |
| Always Page2 | 12/50 | 0.2400 | 0.2400 | 0 | 222 | 0.0000 | NA |
| Oracle top1 | 12/50 | 0.2400 | 0.2400 | 0 | 50 | 0.0000 | NA |

Random top1（1000 trials）：

- ΔGT mean=0.0000，std=0.0000，range=0–0。
- GT found mean=12.0000；macro recall mean=0.2400；micro recall mean=0.2400。
- Random >= Router：1000/1000。

## 判别能力

- max_jaccard global ROC-AUC：NA。
- within-question pair-weighted AUC：NA。
- 可比较题数：0；positive-negative pairs：0。
- query labels：positive=0，negative=222。

标签固定为：单条 query 的 Page2 相对该题全部 native Page1 union 是否新增至少一个 GT；排序方向固定为 max_jaccard 越高越优。

## 分组结果

### author-written

| Policy | GT found | Macro recall | Micro recall | ΔGT | Calls | ΔGT/call | Retention |
|---|---:|---:|---:|---:|---:|---:|---:|
| Native Page1 | 9/25 | 0.3600 | 0.3600 | 0 | 0 | NA | NA |
| Jaccard Router | 9/25 | 0.3600 | 0.3600 | 0 | 25 | 0.0000 | NA |
| Always Page2 | 9/25 | 0.3600 | 0.3600 | 0 | 105 | 0.0000 | NA |
| Oracle top1 | 9/25 | 0.3600 | 0.3600 | 0 | 25 | 0.0000 | NA |

Random ΔGT mean=0.0000，std=0.0000；macro recall mean=0.3600。

### inline-citation

| Policy | GT found | Macro recall | Micro recall | ΔGT | Calls | ΔGT/call | Retention |
|---|---:|---:|---:|---:|---:|---:|---:|
| Native Page1 | 3/25 | 0.1200 | 0.1200 | 0 | 0 | NA | NA |
| Jaccard Router | 3/25 | 0.1200 | 0.1200 | 0 | 25 | 0.0000 | NA |
| Always Page2 | 3/25 | 0.1200 | 0.1200 | 0 | 117 | 0.0000 | NA |
| Oracle top1 | 3/25 | 0.1200 | 0.1200 | 0 | 25 | 0.0000 | NA |

Random ΔGT mean=0.0000，std=0.0000；macro recall mean=0.1200。

## 身份映射修订

唯一 exact-normalized-title 一对多冲突依据官方静态 arXiv metadata 解决：corpusid 258960101 保留 `2305.17359`（DNA-GPT），拒绝误关联的 `2303.02909`（Dynamic Prompting）。未使用 Search/Page2 outcome，未扩展 fuzzy matching，未补普通 title miss。

原 PAGE2_ROUTING_PREREG_VALIDATION_003 的停止记录、0 抽样和 0 Search 结论保持不变；003B 由独立 amendment 激活。

## 口径与限制

- GT 按冻结的 normalized title groups 与静态唯一 arXiv ID 映射计数，同题跨 query/page 去重。
- Primary 的 50 次 Page2 是 policy replay logical budget；真实采集成本等于 Always Page2。
- Oracle top1 使用 GT，仅为离线上界，不属于可部署 policy。
- Serper Page1/Page2 是尽量连续获取的同次实验快照，但搜索服务本身不是可重复的静态索引。
- CPU 环境预检在首个 forward、生成任何 token 前失败；未产生 query 或 Search，正式采集使用冻结 CUDA/FlashAttention 路径。

## 产物完整性

- PREREGISTRATION.md：`d084f7a5fe253e7f00e06b7d3222f51f96c503df886303c579c542787264d2f8`
- MAPPING_AMENDMENT.md：`65e0c52874e1822c869b9d9e8170b9aff22777ede644639129e906665d5b53f9`
- dataset_manifest.json：`56082bf76d06f8c25547b3ad2322a766507ddbdac6654fefc4e874cd1c6b328f`
- snapshot_manifest.json：`f101297bca8b4142a3949f222d710d02c619d82eba89008e545f01b32d48cc63`
- states.json：`726ddda0a5dce6e9ec758ec11641664260f5a563b0ccfdcc3a6b5bee733b6066`
- decisions.json：`ddd293b0cb184222e76170bac192b3f7acce5fc01cf84ea8d078e806d8f9c7e3`
- results.json：`9406a8982abcbb6190905ca296000f09da4ebaf038878fbf1b939341943fb460`

最终独立验证结论见 `validation.json`。
