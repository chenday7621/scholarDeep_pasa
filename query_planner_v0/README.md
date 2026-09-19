# Constraint-aware Query Planner V0

独立离线原型，不导入或修改 PaSa 的 Search、Selector、Expand、Ranking 或评测入口。只读取用户问题和保存的 baseline query 文本。LLM 使用现有本地 Crawler checkpoint，不训练、不改权重；本目录 prompts 仅服务新 planner。

## 执行

```bash
cd /home/chenyi/pasa
CUDA_VISIBLE_DEVICES=1 PYTHONHASHSEED=42 /mnt/nvme3/chenyi/conda-envs/pasa/bin/python query_planner_v0/generate.py --batch-size 8
CUDA_VISIBLE_DEVICES=1 PYTHONHASHSEED=42 /mnt/nvme3/chenyi/conda-envs/pasa/bin/python query_planner_v0/repair.py --batch-size 8
python3 query_planner_v0/audit.py
python3 -m unittest query_planner_v0.test_validation
```

本次运行已经完成，无需为查看报告再次加载模型。仅重新生成审计使用后两条命令。生成脚本会跳过已成功的阶段，但可能重新尝试失败阶段；如需新的独立实验，请给 `generate.py` 指定新的 `--artifacts` 和 `--output`，给 `repair.py` 指定对应 `--results` 与独立 `--artifacts`，再给 `audit.py` 指定同一 `--results`、主流程 `--artifacts .../run` 和新 `--report`。不要覆盖本次原始尝试记录。

## 文件职责

- `generate.py`：本地模型加载、三个阶段、JSON格式校验、原文约束过滤、保存baseline与新输出。禁止网络连接，Hugging Face只加载本地文件。
- `prompts.json`：提取、facet规划和批量query生成的完整指令。
- `repair.py`：对失败阶段进行有上限的补救；批量query失败后，每个已规划facet独立生成一条，由程序绑定标签。补救指令也随manifest保存。
- `audit.py`：仅基于文本统计约束保留、pair Jaccard、facet分布并渲染逐题人工审计。保留部分成功输出，不伪造失败槽位。
- `reference_constraints.json`：运行前从50个用户问题标注的140个评估片段，仅审计读取，模型输入不包含它。
- `manual_review.json`：对双方原始query的逐题人工复核，供报告引用，不参与生成。
- `test_validation.py`：验证source grounding、错误facet绑定、网络阻断及JSON尾随控制标签处理。

## 结果解释

最终输出在项目根目录：`CONSTRAINT_QUERY_PLANNER_V0_RESULTS.json`、`CONSTRAINT_QUERY_PLANNER_AUDIT.md`。

原始prompt/响应在 `/home/chenyi/pasa-artifacts/CONSTRAINT_QUERY_PLANNER_V0/{run,repair}`；合成格式诊断独立保存。每个失败、重试和source-grounding剔除值均有记录。结果中的 `generation_status` 表示结构完整程度；`PARTIAL` 保留成功生成的部分槽位。`covered_constraints` 是模型自报值，另有独立的 `automatic_audit` 核验。

本轮结构完整45/50，另5题部分成功；结构完整并不代表query语义合格。控制词、错误缩写、需求外扩展等真实坏输出保留用于审计，禁止直接视作已获准搜索的query。V0目前不具备“所有输出都满足硬约束”的保证，不应仅因JSON完整就接入Search。

生成阶段增加了模型调用和token预算，批量与逐facet补救路径的开销不同。后续若研究纯机制效果，应预先固定规划模型和调用预算并做独立消融。本阶段没有搜索结果或召回指标，也没有训练或Git提交。
