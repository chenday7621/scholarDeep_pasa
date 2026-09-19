# Query Planner V0 人工审计工作表

## 总体说明

- 数据集：RealScholarQuery-50，完整收录 RealScholarQuery_0 至 RealScholarQuery_49。
- 对比对象：PaSa baseline queries 与 Constraint-aware Query Planner V0 queries。
- 当前阶段：仅人工审计 query 质量，不涉及搜索结果，不涉及 Recall/F1。
- 人工审计目标：判断 V0 相比 baseline 是否更忠实保留用户约束、query 是否更加互补、是否减少遗漏，以及是否引入错误信息。
- 所有评价选项、说明与错误统计均预留空白，由人工填写；本文件不导入已有实验报告中的质量判断。

整理规则：英文问题与 query 直接取自已有产物，保留原文；中文紧跟对应英文，忠实翻译，不纠正原文术语、缩写展开或控制词。V0 按已保存的 planned_sequence 对齐到五个原始槽位，缺失槽位标为 [FAILED GENERATION]，后续 query 不前移。Baseline 原记录不足五条时标为 [NOT GENERATED IN BASELINE]（原始记录未生成），不将其解释为 V0 生成失败。原文换行在表格中用 <code>&lt;br&gt;</code> 显示。

来源：[V0 RESULTS](CONSTRAINT_QUERY_PLANNER_V0_RESULTS.json)、[RealScholarQuery-50 原始数据](data/RealScholarQuery/test.jsonl)，并逐条核对 RESULTS 所指向的 baseline smoke 与 V0 阶段记录。仅整理已存在的文本，没有重新运行模型或生成 query。

# RealScholarQuery_0

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_0 |
| Original Question | Give me papers which show that using a smaller dataset in large language model pre-training can result in better models than using bigger datasets. |
| Question Chinese Translation | 请提供一些论文，证明在大语言模型预训练中，使用较小的数据集能够比使用更大的数据集得到更好的模型。 |
| Baseline Query 1 | Papers on the effectiveness of smaller datasets in language model pre-training |
| Baseline Query 1 CN | 关于较小数据集在语言模型预训练中有效性的论文 |
| Baseline Query 2 | Advantages of using smaller datasets in large language model pre-training |
| Baseline Query 2 CN | 在大语言模型预训练中使用较小数据集的优势 |
| Baseline Query 3 | Benefits of limited dataset in pre-training of language models |
| Baseline Query 3 CN | 在语言模型预训练中使用有限数据集的益处 |
| Baseline Query 4 | Survey papers on large language model pre-training using smaller dataset |
| Baseline Query 4 CN | 关于使用较小数据集进行大语言模型预训练的综述论文 |
| Baseline Query 5 | Effects of dataset size on language model pre-training effectiveness |
| Baseline Query 5 CN | 数据集规模对语言模型预训练效果的影响 |
| V0 Query 1 | Effect of smaller datasets on pre-training of large language models |
| V0 Query 1 CN | 较小数据集对大语言模型预训练的影响 |
| V0 Query 2 | Comparison of dataset sizes in language model pre-training |
| V0 Query 2 CN | 语言模型预训练中不同数据集规模的比较 |
| V0 Query 3 | Papers on smaller dataset approaches in language model pre-training |
| V0 Query 3 CN | 关于语言模型预训练中采用较小数据集的方法的论文 |
| V0 Query 4 | Benefits of using smaller datasets in large language model pre-training |
| V0 Query 4 CN | 在大语言模型预训练中使用较小数据集的益处 |
| V0 Query 5 | Negative effects of small datasets in language model pre-training |
| V0 Query 5 CN | 小数据集对语言模型预训练的负面影响 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_1

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_1 |
| Original Question | Give me papers that share some insights about how large language models gain in-context learning capability in the process of pre-training.<br> |
| Question Chinese Translation | 请提供一些论文，阐释大语言模型如何在预训练过程中获得上下文学习能力。 |
| Baseline Query 1 | Survey papers on in-context learning in pre-trained language models |
| Baseline Query 1 CN | 关于预训练语言模型中上下文学习的综述论文 |
| Baseline Query 2 | In-context learning in pre-training of large language models |
| Baseline Query 2 CN | 大语言模型预训练中的上下文学习 |
| Baseline Query 3 | Pre-training methods for in-context learning in language models |
| Baseline Query 3 CN | 用于语言模型上下文学习的预训练方法 |
| Baseline Query 4 | Insights into the process of pre-training for in-context learning in language models |
| Baseline Query 4 CN | 关于语言模型中支持上下文学习的预训练过程的见解 |
| Baseline Query 5 | Role of pre-training in the development of in-context learning in language models |
| Baseline Query 5 CN | 预训练在语言模型上下文学习能力形成中的作用 |
| V0 Query 1 | Pre-training methods for in-context learning in language models |
| V0 Query 1 CN | 用于语言模型上下文学习的预训练方法 |
| V0 Query 2 | Exploration of in-context learning in pre-trained language models |
| V0 Query 2 CN | 对预训练语言模型中上下文学习的探索 |
| V0 Query 3 | Techniques used in pre-training of large language models for in-context learning |
| V0 Query 3 CN | 大语言模型预训练中用于上下文学习的技术 |
| V0 Query 4 | Impact of pre-training on in-context learning in language models |
| V0 Query 4 CN | 预训练对语言模型上下文学习的影响 |
| V0 Query 5 | Understanding the limitations of in-context learning in pre-trained language models |
| V0 Query 5 CN | 理解预训练语言模型中上下文学习的局限 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_2

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_2 |
| Original Question | List all papers that use autoregressive transformer to generate videos. |
| Question Chinese Translation | 列出所有使用自回归 Transformer 生成视频的论文。 |
| Baseline Query 1 | Autoregressive transformer models in video generation research papers |
| Baseline Query 1 CN | 视频生成研究论文中的自回归 Transformer 模型 |
| Baseline Query 2 | Research on using autoregressive transformers for video editing and composition |
| Baseline Query 2 CN | 关于使用自回归 Transformer 进行视频编辑和合成的研究 |
| Baseline Query 3 | Papers on video generation using autoregressive transformer |
| Baseline Query 3 CN | 关于使用自回归 Transformer 生成视频的论文 |
| Baseline Query 4 | Studies on autoregressive transformer in video creation |
| Baseline Query 4 CN | 关于自回归 Transformer 用于视频创作的研究 |
| Baseline Query 5 | Use of autoregressive transformer in video generation papers |
| Baseline Query 5 CN | 视频生成论文中自回归 Transformer 的使用 |
| V0 Query 1 | Research on video generation using autoregressive transformer |
| V0 Query 1 CN | 关于使用自回归 Transformer 生成视频的研究 |
| V0 Query 2 | Papers on autoregressive transformer in video generation |
| V0 Query 2 CN | 关于自回归 Transformer 用于视频生成的论文 |
| V0 Query 3 | Autoregressive Transformer techniques in video generation studies |
| V0 Query 3 CN | 视频生成研究中的自回归 Transformer 技术 |
| V0 Query 4 | Autoregressive Transformer in video generation research papers |
| V0 Query 4 CN | 视频生成研究论文中的自回归 Transformer |
| V0 Query 5 | Limitations of autoregressive transformer in video generation |
| V0 Query 5 CN | 自回归 Transformer 在视频生成中的局限 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_3

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_3 |
| Original Question | I am looking for research papers on the construction of multimodal foundation models that support both visual and audio inputs. These models should be pre-trained on large-scale datasets, including visual, audio, and audio-visual data. Please exclude survey papers. |
| Question Chinese Translation | 我正在寻找关于构建同时支持视觉和音频输入的多模态基础模型的研究论文。这些模型应在大规模数据集上进行预训练，数据包括视觉、音频和视听数据。请排除综述论文。 |
| Baseline Query 1 | Pre-training of multimodal foundation models on large-scale datasets |
| Baseline Query 1 CN | 在大规模数据集上进行多模态基础模型预训练 |
| Baseline Query 2 | Research on audio-visual pretraining in multimodal foundation models |
| Baseline Query 2 CN | 关于多模态基础模型中视听预训练的研究 |
| Baseline Query 3 | Multimodal foundation models for visual and audio inputs |
| Baseline Query 3 CN | 用于视觉和音频输入的多模态基础模型 |
| Baseline Query 4 | Foundation models supporting visual and audio inputs |
| Baseline Query 4 CN | 支持视觉和音频输入的基础模型 |
| Baseline Query 5 | Research on Large Multimodal Models (LMMs) for integrating visual and textual data |
| Baseline Query 5 CN | 关于用于融合视觉和文本数据的大型多模态模型（LMMs）的研究 |
| V0 Query 1 | Contrastive loss application in multimodal foundation models for joint training of vision and audio modalities |
| V0 Query 1 CN | 对比损失在多模态基础模型中用于视觉与音频模态联合训练的应用 |
| V0 Query 2 | Research on the development of multimodal foundation models supporting visual and audio inputs. |
| V0 Query 2 CN | 关于开发支持视觉和音频输入的多模态基础模型的研究。 |
| V0 Query 3 | Studies on large-scale datasets for multimodal foundation models with visual and audio inputs |
| V0 Query 3 CN | 关于面向视觉和音频输入多模态基础模型的大规模数据集的研究 |
| V0 Query 4 | Pre-training methods for multimodal foundation models supporting visual and audio inputs |
| V0 Query 4 CN | 支持视觉和音频输入的多模态基础模型的预训练方法 |
| V0 Query 5 | Research on the development of multimodal foundation models supporting visual and audio inputs |
| V0 Query 5 CN | 关于开发支持视觉和音频输入的多模态基础模型的研究 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_4

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_4 |
| Original Question | Provide me with all papers that discuss reinforcement learning training for Large Language Model agent tasks. |
| Question Chinese Translation | 请提供所有讨论面向大语言模型智能体任务的强化学习训练的论文。 |
| Baseline Query 1 | Survey papers on reinforcement learning training for large language models |
| Baseline Query 1 CN | 关于大语言模型强化学习训练的综述论文 |
| Baseline Query 2 | Research on task-agnostic rewards in reinforcement learning training for large language models |
| Baseline Query 2 CN | 关于大语言模型强化学习训练中任务无关奖励的研究 |
| Baseline Query 3 | Reinforcement learning approaches for optimizing Large Language Model agents |
| Baseline Query 3 CN | 用于优化大语言模型智能体的强化学习方法 |
| Baseline Query 4 | Case studies of Large Language Model agents trained using reinforcement learning |
| Baseline Query 4 CN | 关于使用强化学习训练大语言模型智能体的案例研究 |
| Baseline Query 5 | Experiences in training Large Language Model agents using reinforcement learning |
| Baseline Query 5 CN | 使用强化学习训练大语言模型智能体的经验 |
| V0 Query 1 | Papers on reinforcement learning training for large language model agents |
| V0 Query 1 CN | 关于大语言模型智能体强化学习训练的论文 |
| V0 Query 2 | Reinforcement learning training for Large Language Model agent tasks |
| V0 Query 2 CN | 面向大语言模型智能体任务的强化学习训练 |
| V0 Query 3 | Benchmark datasets used in reinforcement learning training for large language models |
| V0 Query 3 CN | 大语言模型强化学习训练中使用的基准数据集 |
| V0 Query 4 | Exploration mechanisms in reinforcement learning training for Large Language Models |
| V0 Query 4 CN | 大语言模型强化学习训练中的探索机制 |
| V0 Query 5 | Studies on RLHF in training Large Language Model agents |
| V0 Query 5 CN | 关于使用 RLHF 训练大语言模型智能体的研究 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_5

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_5 |
| Original Question | Papers that apply RLHF to address the hallucination problem in image and video description. |
| Question Chinese Translation | 将 RLHF 用于解决图像和视频描述中幻觉问题的论文。 |
| Baseline Query 1 | Survey papers on RLHF for image description |
| Baseline Query 1 CN | 关于 RLHF 用于图像描述的综述论文 |
| Baseline Query 2 | Application of RLHF in video description |
| Baseline Query 2 CN | RLHF 在视频描述中的应用 |
| Baseline Query 3 | Use of RLHF in addressing hallucination in video content |
| Baseline Query 3 CN | 使用 RLHF 解决视频内容中的幻觉 |
| Baseline Query 4 | Impact of RLHF on hallucination issue in image description |
| Baseline Query 4 CN | RLHF 对图像描述中幻觉问题的影响 |
| Baseline Query 5 | Role of RLHF in reducing hallucination in multimodal generation |
| Baseline Query 5 CN | RLHF 在减少多模态生成幻觉方面的作用 |
| V0 Query 1 | Application of Reinforcement Learning Hindsight Experience in video description tasks |
| V0 Query 1 CN | 强化学习事后经验（Reinforcement Learning Hindsight Experience）在视频描述任务中的应用 |
| V0 Query 2 | Use of Large Language Models in RLHF for multi-modal content description |
| V0 Query 2 CN | 在用于多模态内容描述的 RLHF 中使用大语言模型 |
| V0 Query 3 | Impact of RLHF on reducing hallucination in image and video descriptions |
| V0 Query 3 CN | RLHF 对减少图像和视频描述中幻觉的影响 |
| V0 Query 4 | Comparative analysis of RLHF and other methods in addressing hallucination in image and video description |
| V0 Query 4 CN | RLHF 与其他方法在解决图像和视频描述幻觉问题方面的比较分析 |
| V0 Query 5 | Latest research applying RLHF to image and video description tasks |
| V0 Query 5 CN | 将 RLHF 应用于图像和视频描述任务的最新研究 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_6

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_6 |
| Original Question | Papers that propose methods based on large language models and evaluate their performance through experiments on the HotPotQA dataset. |
| Question Chinese Translation | 提出基于大语言模型的方法，并通过在 HotPotQA 数据集上进行实验来评估其性能的论文。 |
| Baseline Query 1 | Large language model based methods for HotPotQA dataset |
| Baseline Query 1 CN | 面向 HotPotQA 数据集的基于大语言模型的方法 |
| Baseline Query 2 | Research on evaluation methods for Large Language Models on HotPotQA dataset |
| Baseline Query 2 CN | 关于在 HotPotQA 数据集上评估大语言模型的方法的研究 |
| Baseline Query 3 | Survey papers on methods using large language models for HotPotQA |
| Baseline Query 3 CN | 关于在 HotPotQA 中使用大语言模型的方法的综述论文 |
| Baseline Query 4 | Experiments on the HotPotQA dataset for language models |
| Baseline Query 4 CN | 语言模型在 HotPotQA 数据集上的实验 |
| Baseline Query 5 | Proposed methods for HotPotQA using large language models |
| Baseline Query 5 CN | 针对 HotPotQA 提出的使用大语言模型的方法 |
| V0 Query 1 | Proposed methods for HotPotQA using large language models |
| V0 Query 1 CN | 针对 HotPotQA 提出的使用大语言模型的方法 |
| V0 Query 2 | Experimental evaluations of large language model methods on HotPotQA |
| V0 Query 2 CN | 在 HotPotQA 上对大语言模型方法进行实验评估 |
| V0 Query 3 | Application of large language models in HotPotQA domain |
| V0 Query 3 CN | 大语言模型在 HotPotQA 领域中的应用 |
| V0 Query 4 | Research papers not proposing methods for HotPotQA using large language models |
| V0 Query 4 CN | 未提出使用大语言模型解决 HotPotQA 的方法的研究论文 |
| V0 Query 5 | StopSearch |
| V0 Query 5 CN | 停止搜索（StopSearch） |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_7

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_7 |
| Original Question | Show me research on the long video description. Here, long videos are defined as those with a duration of at least several minutes. |
| Question Chinese Translation | 请提供关于长视频描述的研究。这里的长视频指时长至少为数分钟的视频。 |
| Baseline Query 1 | Survey papers on long video description techniques |
| Baseline Query 1 CN | 关于长视频描述技术的综述论文 |
| Baseline Query 2 | Research on automatic video summarization for long videos |
| Baseline Query 2 CN | 关于长视频自动摘要的研究 |
| Baseline Query 3 | Long video description research papers |
| Baseline Query 3 CN | 长视频描述研究论文 |
| Baseline Query 4 | Studies on multi-modal language models for long video understanding |
| Baseline Query 4 CN | 关于用于长视频理解的多模态语言模型的研究 |
| Baseline Query 5 | Research on long-duration video description |
| Baseline Query 5 CN | 关于长时长视频描述的研究 |
| V0 Query 1 | Survey papers on long video description techniques |
| V0 Query 1 CN | 关于长视频描述技术的综述论文 |
| V0 Query 2 | Research on large language models for long video description |
| V0 Query 2 CN | 关于用于长视频描述的大语言模型的研究 |
| V0 Query 3 | Studies on automatic video summarization for long videos |
| V0 Query 3 CN | 关于长视频自动摘要的研究 |
| V0 Query 4 | Advancements in long video description methods |
| V0 Query 4 CN | 长视频描述方法的进展 |
| V0 Query 5 | Existing datasets for long video description research |
| V0 Query 5 CN | 用于长视频描述研究的现有数据集 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_8

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_8 |
| Original Question | Do you know some papers about using reward shaping methods to train large language model agent. |
| Question Chinese Translation | 你知道一些关于使用奖励塑形方法训练大语言模型智能体的论文吗？ |
| Baseline Query 1 | Reward shaping techniques in large language model training |
| Baseline Query 1 CN | 大语言模型训练中的奖励塑形技术 |
| Baseline Query 2 | Application of reward shaping in language model agent training |
| Baseline Query 2 CN | 奖励塑形在语言模型智能体训练中的应用 |
| Baseline Query 3 | Effectiveness of reward shaping methods in training large language models |
| Baseline Query 3 CN | 奖励塑形方法在大语言模型训练中的有效性 |
| Baseline Query 4 | Research on using small extrinsic rewards for aligning large language models with user intent |
| Baseline Query 4 CN | 关于使用少量外在奖励使大语言模型与用户意图对齐的研究 |
| Baseline Query 5 | Exploring the use of self-rewarding mechanisms in training large language models |
| Baseline Query 5 CN | 探索大语言模型训练中自奖励机制的使用 |
| V0 Query 1 | Review papers on reward shaping techniques for language models |
| V0 Query 1 CN | 关于语言模型奖励塑形技术的综述论文 |
| V0 Query 2 | Research on applying reward shaping in language model training |
| V0 Query 2 CN | 关于在语言模型训练中应用奖励塑形的研究 |
| V0 Query 3 | Research on the use of intrinsic rewards for training large language models without extrinsic rewards |
| V0 Query 3 CN | 关于不使用外在奖励、而使用内在奖励训练大语言模型的研究 |
| V0 Query 4 | Research on the use of reward shaping in language model agents |
| V0 Query 4 CN | 关于在语言模型智能体中使用奖励塑形的研究 |
| V0 Query 5 | Exploration of reward shaping methods for training large language model agents |
| V0 Query 5 CN | 探索用于训练大语言模型智能体的奖励塑形方法 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_9

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_9 |
| Original Question | Give me papers about how to rank search results by the use of LLM. |
| Question Chinese Translation | 请提供关于如何使用 LLM 对搜索结果进行排序的论文。 |
| Baseline Query 1 | Use of LLM in ranking search results |
| Baseline Query 1 CN | 使用 LLM 对搜索结果进行排序 |
| Baseline Query 2 | Influence of LLM on search result rankings |
| Baseline Query 2 CN | LLM 对搜索结果排名的影响 |
| Baseline Query 3 | Survey papers on ranking search results with Language Model |
| Baseline Query 3 CN | 关于使用语言模型对搜索结果排序的综述论文 |
| Baseline Query 4 | Application of LLM in search result ranking |
| Baseline Query 4 CN | LLM 在搜索结果排序中的应用 |
| Baseline Query 5 | Ranking mechanisms in Large Language Models |
| Baseline Query 5 CN | 大语言模型中的排序机制 |
| V0 Query 1 | Research on ranking search results using Language Model |
| V0 Query 1 CN | 关于使用语言模型对搜索结果排序的研究 |
| V0 Query 2 | [FAILED GENERATION] |
| V0 Query 2 CN | [FAILED GENERATION]（生成失败，留空） |
| V0 Query 3 | Papers on ranking search results using LLMs |
| V0 Query 3 CN | 关于使用 LLM 对搜索结果排序的论文 |
| V0 Query 4 | Evaluation metrics for search result ranking using LLMs |
| V0 Query 4 CN | 使用 LLM 对搜索结果排序的评价指标 |
| V0 Query 5 | Influence of LLMs on search result rankings |
| V0 Query 5 CN | LLM 对搜索结果排名的影响 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_10

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_10 |
| Original Question | Is there any work that analyzes the scaling law of the multi-module models, such as video-text, image-text models? |
| Question Chinese Translation | 是否有研究分析多模块模型的缩放定律，例如视频—文本、图像—文本模型？ |
| Baseline Query 1 | Survey papers on scaling law of multi-module models |
| Baseline Query 1 CN | 关于多模块模型缩放定律的综述论文 |
| Baseline Query 2 | Analysis of scaling law in video-text models |
| Baseline Query 2 CN | 视频—文本模型中的缩放定律分析 |
| Baseline Query 3 | Research on scaling law in image-text models |
| Baseline Query 3 CN | 关于图像—文本模型缩放定律的研究 |
| Baseline Query 4 | Scaling behavior of multi-modal transformer models in video-text tasks |
| Baseline Query 4 CN | 视频—文本任务中多模态 Transformer 模型的缩放行为 |
| Baseline Query 5 | Empirical studies on the scaling laws of text-to-video generation models |
| Baseline Query 5 CN | 关于文本生成视频模型缩放定律的实证研究 |
| V0 Query 1 | Investigations on the scaling laws in large multimodal models like VLMs |
| V0 Query 1 CN | 关于 VLM 等大型多模态模型缩放定律的研究 |
| V0 Query 2 | Exploration of the learning dynamics and scaling laws in multimodal transformer models |
| V0 Query 2 CN | 探索多模态 Transformer 模型的学习动态和缩放定律 |
| V0 Query 3 | Research on the scaling behavior of video-text and image-text models |
| V0 Query 3 CN | 关于视频—文本与图像—文本模型缩放行为的研究 |
| V0 Query 4 | Overview of scaling laws in multi-modal AI models |
| V0 Query 4 CN | 多模态 AI 模型缩放定律概述 |
| V0 Query 5 | Studies contradicting the universal applicability of scaling laws in multimodal models |
| V0 Query 5 CN | 与缩放定律在多模态模型中具有普适性这一观点相矛盾的研究 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_11

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_11 |
| Original Question | Give me all visual-LLM models that are MoE architecture |
| Question Chinese Translation | 请提供所有采用 MoE 架构的 visual-LLM 模型。 |
| Baseline Query 1 | MoE architecture models in visual-LLM |
| Baseline Query 1 CN | visual-LLM 中采用 MoE 架构的模型 |
| Baseline Query 2 | Survey papers on visual-LLM models with MoE architecture |
| Baseline Query 2 CN | 关于采用 MoE 架构的 visual-LLM 模型的综述论文 |
| Baseline Query 3 | Multi-Modal Large Language Models with MoE architecture |
| Baseline Query 3 CN | 采用 MoE 架构的多模态大语言模型 |
| Baseline Query 4 | Research on MoE architecture in visual-LLMs |
| Baseline Query 4 CN | 关于 visual-LLM 中 MoE 架构的研究 |
| Baseline Query 5 | Objectives of visual-LLM models using MoE architecture |
| Baseline Query 5 CN | 采用 MoE 架构的 visual-LLM 模型的目标 |
| V0 Query 1 | All visual-LLM models using MoE architecture |
| V0 Query 1 CN | 所有使用 MoE 架构的 visual-LLM 模型 |
| V0 Query 2 | [FAILED GENERATION] |
| V0 Query 2 CN | [FAILED GENERATION]（生成失败，留空） |
| V0 Query 3 | Give me all visual-LLM models that are MoE architecture |
| V0 Query 3 CN | 请提供所有采用 MoE 架构的 visual-LLM 模型 |
| V0 Query 4 | Datasets used for benchmarking MoE visual-LLM models |
| V0 Query 4 CN | 用于对 MoE visual-LLM 模型进行基准评测的数据集 |
| V0 Query 5 | [FAILED GENERATION] |
| V0 Query 5 CN | [FAILED GENERATION]（生成失败，留空） |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_12

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_12 |
| Original Question | What papers discuss the use of transformer architecture in 3d video generation |
| Question Chinese Translation | 哪些论文讨论了在 3D 视频生成中使用 Transformer 架构？ |
| Baseline Query 1 | Use of transformer model in 3D video production |
| Baseline Query 1 CN | Transformer 模型在 3D 视频制作中的使用 |
| Baseline Query 2 | Research on 3D video generation using transformer architecture |
| Baseline Query 2 CN | 关于使用 Transformer 架构生成 3D 视频的研究 |
| Baseline Query 3 | Papers on transformer-based methods in 3D video generation |
| Baseline Query 3 CN | 关于 3D 视频生成中基于 Transformer 的方法的论文 |
| Baseline Query 4 | Transformer architecture application in 3D video creation |
| Baseline Query 4 CN | Transformer 架构在 3D 视频创作中的应用 |
| Baseline Query 5 | Exploration of transformer architecture for 3D video synthesis |
| Baseline Query 5 CN | 探索用于 3D 视频合成的 Transformer 架构 |
| V0 Query 1 | Research on the application of transformer models in 3D video synthesis |
| V0 Query 1 CN | 关于 Transformer 模型应用于 3D 视频合成的研究 |
| V0 Query 2 | Use of Transformer architecture in 3D video generation research papers |
| V0 Query 2 CN | 在 3D 视频生成研究论文中使用 Transformer 架构 |
| V0 Query 3 | Research on the use of transformer architecture in 3D video generation |
| V0 Query 3 CN | 关于在 3D 视频生成中使用 Transformer 架构的研究 |
| V0 Query 4 | What research articles are there on the use of transformer models in 3D video synthesis? |
| V0 Query 4 CN | 有哪些关于在 3D 视频合成中使用 Transformer 模型的研究文章？ |
| V0 Query 5 | Limitations of using transformer architecture in 3D video generation |
| V0 Query 5 CN | 在 3D 视频生成中使用 Transformer 架构的局限 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_13

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_13 |
| Original Question | Provide papers demonstrating that the self-correction of LLMs does not enhance their performance. |
| Question Chinese Translation | 请提供证明 LLM 自我纠正不能提高其性能的论文。 |
| Baseline Query 1 | Studies on the limitations of self-correction in language models |
| Baseline Query 1 CN | 关于语言模型自我纠正局限性的研究 |
| Baseline Query 2 | Impact of self-correction on language model performance |
| Baseline Query 2 CN | 自我纠正对语言模型性能的影响 |
| Baseline Query 3 | Survey papers on self-correction not enhancing LLM performance |
| Baseline Query 3 CN | 关于自我纠正未能提升 LLM 性能的综述论文 |
| Baseline Query 4 | Academic papers on the ineffectiveness of self-correction in LLMs |
| Baseline Query 4 CN | 关于 LLM 自我纠正无效性的学术论文 |
| Baseline Query 5 | Research on self-correction mechanisms in LLMs and their impact on performance |
| Baseline Query 5 CN | 关于 LLM 自我纠正机制及其对性能影响的研究 |
| V0 Query 1 | Studies showing no performance boost from self-correction in LLMs |
| V0 Query 1 CN | 表明 LLM 自我纠正没有带来性能提升的研究 |
| V0 Query 2 | Research articles on the non-enhancing effect of self-correction in Language Models |
| V0 Query 2 CN | 关于自我纠正对语言模型没有提升效果的研究文章 |
| V0 Query 3 | Studies on the ineffectiveness of self-correction in language models |
| V0 Query 3 CN | 关于语言模型自我纠正无效性的研究 |
| V0 Query 4 | Research articles on the unsuccessful application of self-correction in language learning machines for performance enhancement |
| V0 Query 4 CN | 关于在语言学习机器中应用自我纠正未能提升性能的研究文章 |
| V0 Query 5 | Articles discussing the challenges in measuring the impact of self-correction in LLMs |
| V0 Query 5 CN | 讨论衡量自我纠正对 LLM 影响所面临挑战的文章 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_14

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_14 |
| Original Question | Find papers that use LLMs or LLM-based agents to automatically write surveys or summaries for multiple scholarly documents. |
| Question Chinese Translation | 寻找使用 LLM 或基于 LLM 的智能体，对多篇学术文献自动撰写综述或摘要的论文。 |
| Baseline Query 1 | Use of LLMs in automatic survey writing |
| Baseline Query 1 CN | LLM 在自动撰写综述中的使用 |
| Baseline Query 2 | Survey papers on the use of LLMs in scholarly document summarization |
| Baseline Query 2 CN | 关于 LLM 在学术文献摘要中应用的综述论文 |
| Baseline Query 3 | Papers on LLM-based agents for writing summaries of scholarly articles |
| Baseline Query 3 CN | 关于用于撰写学术文章摘要的 LLM 智能体的论文 |
| Baseline Query 4 | Research on using language models for automatic synthesis of literature reviews |
| Baseline Query 4 CN | 关于使用语言模型自动合成文献综述的研究 |
| Baseline Query 5 | Articles on the application of LLM-based agents in multi-document summary |
| Baseline Query 5 CN | 关于基于 LLM 的智能体在多文档摘要中应用的文章 |
| V0 Query 1 | Use of LLMs in automatic survey writing for multiple scholarly documents |
| V0 Query 1 CN | 使用 LLM 为多篇学术文献自动撰写综述 |
| V0 Query 2 | Scholarly document summarization using LLM-based agents |
| V0 Query 2 CN | 使用基于 LLM 的智能体进行学术文献摘要 |
| V0 Query 3 | Application of language models in automatic synthesis of survey papers |
| V0 Query 3 CN | 语言模型在自动合成综述论文中的应用 |
| V0 Query 4 | Research on LLMs for automatic writing of survey papers |
| V0 Query 4 CN | 关于使用 LLM 自动撰写综述论文的研究 |
| V0 Query 5 | Limitations of LLMs in generating summaries for multiple scholarly documents |
| V0 Query 5 CN | LLM 为多篇学术文献生成摘要的局限 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_15

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_15 |
| Original Question | Provide papers claiming that reinforcement learning can negatively impact the performance of supervised fine-tuned LLMs. |
| Question Chinese Translation | 请提供声称强化学习会对经过监督微调的 LLM 的性能产生负面影响的论文。 |
| Baseline Query 1 | Survey papers on negative impacts of reinforcement learning on supervised fine-tuned LLMs |
| Baseline Query 1 CN | 关于强化学习对经过监督微调的 LLM 产生负面影响的综述论文 |
| Baseline Query 2 | Implications of Reinforcement Learning on Supervised Fine-Tuning in Language Models |
| Baseline Query 2 CN | 强化学习对语言模型监督微调的影响 |
| Baseline Query 3 | Effects of reinforcement learning on fine-tuned language models |
| Baseline Query 3 CN | 强化学习对微调语言模型的影响 |
| Baseline Query 4 | Downsides of reinforcement learning in supervised fine-tuned LLMs |
| Baseline Query 4 CN | 强化学习在经过监督微调的 LLM 中的弊端 |
| Baseline Query 5 | Impact of reinforcement learning on performance of fine-tuned LLMs |
| Baseline Query 5 CN | 强化学习对微调 LLM 性能的影响 |
| V0 Query 1 | Negative consequences of reinforcement learning on supervised fine-tuned LLMs |
| V0 Query 1 CN | 强化学习对经过监督微调的 LLM 产生的负面后果 |
| V0 Query 2 | Impact of reinforcement learning on supervised fine-tuned language models |
| V0 Query 2 CN | 强化学习对经过监督微调的语言模型的影响 |
| V0 Query 3 | Performance implications of applying reinforcement learning to supervised fine-tuned LLMs |
| V0 Query 3 CN | 对经过监督微调的 LLM 应用强化学习所产生的性能影响 |
| V0 Query 4 | Challenges in using reinforcement learning for supervised fine-tuning in large language models |
| V0 Query 4 CN | 在大语言模型监督微调中使用强化学习所面临的挑战 |
| V0 Query 5 | Exploration of the relationship between reinforcement learning and supervised fine-tuning in language models |
| V0 Query 5 CN | 探索语言模型中强化学习与监督微调的关系 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_16

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_16 |
| Original Question | Find papers on trigger-free document-level event extraction methods that do not use human-annotated triggers. |
| Question Chinese Translation | 寻找无需触发词的文档级事件抽取方法的论文，这些方法不使用人工标注的触发词。 |
| Baseline Query 1 | Document-level event extraction without triggers research papers |
| Baseline Query 1 CN | 关于无触发词文档级事件抽取的研究论文 |
| Baseline Query 2 | Papers on event extraction methods without triggers |
| Baseline Query 2 CN | 关于无触发词事件抽取方法的论文 |
| Baseline Query 3 | Survey papers on trigger-free document-level event extraction |
| Baseline Query 3 CN | 关于无需触发词的文档级事件抽取的综述论文 |
| Baseline Query 4 | Research articles on document-level event extraction without triggers |
| Baseline Query 4 CN | 关于无触发词文档级事件抽取的研究文章 |
| Baseline Query 5 | Studies on event extraction techniques without human-annotated triggers |
| Baseline Query 5 CN | 关于不使用人工标注触发词的事件抽取技术的研究 |
| V0 Query 1 | Overview of trigger-free document-level event extraction techniques |
| V0 Query 1 CN | 无需触发词的文档级事件抽取技术概述 |
| V0 Query 2 | Research articles on event extraction without triggers |
| V0 Query 2 CN | 关于无触发词事件抽取的研究文章 |
| V0 Query 3 | Academic studies on non-triggered document-level event extraction techniques |
| V0 Query 3 CN | 关于无触发式文档级事件抽取技术的学术研究 |
| V0 Query 4 | Studies on document-level event extraction without triggers |
| V0 Query 4 CN | 关于无触发词文档级事件抽取的研究 |
| V0 Query 5 | Application of large language models in trigger-free, document-level event extraction |
| V0 Query 5 CN | 大语言模型在无需触发词的文档级事件抽取中的应用 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_17

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_17 |
| Original Question | Provide papers explaining why the in-context learning performance of LLMs cannot surpass that of supervised fine-tuned small language models in information extraction tasks, such as NER, RE, and EE. |
| Question Chinese Translation | 请提供论文，解释为何在 NER、RE 和 EE 等信息抽取任务中，LLM 的上下文学习性能无法超过经过监督微调的小型语言模型。 |
| Baseline Query 1 | Performance comparison of in-context learning and supervised fine-tuning in language models for information extraction |
| Baseline Query 1 CN | 在信息抽取中比较语言模型的上下文学习与监督微调性能 |
| Baseline Query 2 | Limitations of in-context learning in language models for information extraction |
| Baseline Query 2 CN | 语言模型上下文学习在信息抽取中的局限 |
| Baseline Query 3 | In-context learning vs supervised fine-tuning in LLMs for information extraction |
| Baseline Query 3 CN | 信息抽取中 LLM 的上下文学习与监督微调的比较 |
| Baseline Query 4 | Why supervised fine-tuned small language models outperform in-context learning in NER |
| Baseline Query 4 CN | 为何经过监督微调的小型语言模型在 NER 中优于上下文学习 |
| Baseline Query 5 | Impact of parameter size on the performance of in-context learning versus supervised fine-tuning in large language models |
| Baseline Query 5 CN | 参数规模对大语言模型中上下文学习与监督微调性能的影响 |
| V0 Query 1 | Performance limitations of in-context learning in language models for information extraction tasks |
| V0 Query 1 CN | 语言模型上下文学习在信息抽取任务中的性能局限 |
| V0 Query 2 | Why can't in-context learning surpass supervised fine-tuning in LLMs for NER, RE, and EE? |
| V0 Query 2 CN | 为何在 NER、RE 和 EE 中，LLM 的上下文学习无法超过监督微调？ |
| V0 Query 3 | Investigation on the impact of demonstration retrieval in enhancing in-context learning performance in LLMs for information extraction tasks |
| V0 Query 3 CN | 研究示例检索对提升 LLM 在信息抽取任务中上下文学习性能的影响 |
| V0 Query 4 | Studies on the impact of parameter space geometry on the performance of in-context learning vs supervised fine-tuning in LLMs |
| V0 Query 4 CN | 关于参数空间几何结构对 LLM 中上下文学习与监督微调性能影响的研究 |
| V0 Query 5 | Benchmark studies comparing in-context learning and supervised fine-tuned small language models for information extraction |
| V0 Query 5 CN | 比较上下文学习与经过监督微调的小型语言模型在信息抽取中表现的基准研究 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_18

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_18 |
| Original Question | Can LLMs detect LLM-generated text in a zero-shot manner? Do they perform better than supervised fine-tuned small classification models? Provide related papers. |
| Question Chinese Translation | LLM 能否以零样本方式检测由 LLM 生成的文本？它们的表现是否优于经过监督微调的小型分类模型？请提供相关论文。 |
| Baseline Query 1 | Performance comparison of LLMs and supervised fine-tuned models in zero-shot detection |
| Baseline Query 1 CN | LLM 与经过监督微调的模型在零样本检测中的性能比较 |
| Baseline Query 2 | Zero-shot detection of LLM-generated content |
| Baseline Query 2 CN | 对 LLM 生成内容进行零样本检测 |
| Baseline Query 3 | Supervised fine-tuned small classification models vs LLMs for detecting LLM-generated text |
| Baseline Query 3 CN | 经过监督微调的小型分类模型与 LLM 在检测 LLM 生成文本方面的比较 |
| Baseline Query 4 | Evaluation of LLM-generated text in zero-shot scenarios |
| Baseline Query 4 CN | 在零样本场景下评估 LLM 生成的文本 |
| Baseline Query 5 | [NOT GENERATED IN BASELINE] |
| Baseline Query 5 CN | [NOT GENERATED IN BASELINE]（原始记录未生成） |
| V0 Query 1 | Can LLMs detect LLM-generated text in a zero-shot manner? Do they perform better than supervised fine-tuned small classification models? |
| V0 Query 1 CN | LLM 能否以零样本方式检测由 LLM 生成的文本？它们的表现是否优于经过监督微调的小型分类模型？ |
| V0 Query 2 | Can LLMs detect LLM-generated text in a zero-shot manner? Do they perform better than supervised fine-tuned small classification models? Provide related papers. |
| V0 Query 2 CN | LLM 能否以零样本方式检测由 LLM 生成的文本？它们的表现是否优于经过监督微调的小型分类模型？请提供相关论文。 |
| V0 Query 3 | Can LLMs detect LLM-generated text in a zero-shot manner? Do they perform better than supervised fine-tuned small classification models? Provide related papers. |
| V0 Query 3 CN | LLM 能否以零样本方式检测由 LLM 生成的文本？它们的表现是否优于经过监督微调的小型分类模型？请提供相关论文。 |
| V0 Query 4 | Can LLMs detect LLM-generated text in a zero-shot manner? Do they perform better than supervised fine-tuned small classification models? Provide related papers. |
| V0 Query 4 CN | LLM 能否以零样本方式检测由 LLM 生成的文本？它们的表现是否优于经过监督微调的小型分类模型？请提供相关论文。 |
| V0 Query 5 | Studies on LLM-generated text detection in a zero-shot scenario |
| V0 Query 5 CN | 关于零样本场景下检测 LLM 生成文本的研究 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_19

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_19 |
| Original Question | Provide papers on methods that protect the generation quality of LLMs under vocabulary watermarking settings. |
| Question Chinese Translation | 请提供关于在词汇水印设置下保护 LLM 生成质量的方法的论文。 |
| Baseline Query 1 | Survey papers on protecting generation quality of LLMs under vocabulary watermarking |
| Baseline Query 1 CN | 关于在词汇水印设置下保护 LLM 生成质量的综述论文 |
| Baseline Query 2 | Research on methods to maintain generation quality in LLMs during vocabulary watermarking |
| Baseline Query 2 CN | 关于在词汇水印过程中保持 LLM 生成质量的方法的研究 |
| Baseline Query 3 | Studies on the use of word embeddings in LLMs for detecting and mitigating vocabulary-based watermarking attacks |
| Baseline Query 3 CN | 关于使用词嵌入来检测和缓解针对 LLM 的词汇水印攻击的研究 |
| Baseline Query 4 | Impact of vocabulary watermarking on LLMs generation quality |
| Baseline Query 4 CN | 词汇水印对 LLM 生成质量的影响 |
| Baseline Query 5 | Techniques to mitigate vocabulary watermarking effects on LLM generation |
| Baseline Query 5 CN | 减轻词汇水印对 LLM 生成影响的技术 |
| V0 Query 1 | Methods for maintaining generation quality in LLMs under vocabulary watermarking |
| V0 Query 1 CN | 在词汇水印设置下保持 LLM 生成质量的方法 |
| V0 Query 2 | Methods to maintain generation quality in LLMs under vocabulary watermarking |
| V0 Query 2 CN | 在词汇水印设置下维持 LLM 生成质量的方法 |
| V0 Query 3 | Methods to protect generation quality of LLMs under vocabulary watermarking |
| V0 Query 3 CN | 在词汇水印设置下保护 LLM 生成质量的方法 |
| V0 Query 4 | Research on the use of next-token probability masking to maintain generation quality in LLMs under vocabulary watermarking |
| V0 Query 4 CN | 关于在词汇水印设置下使用下一个 token 概率掩码来保持 LLM 生成质量的研究 |
| V0 Query 5 | Studies on preserving generation quality in LLMs under vocabulary masking using benchmark datasets |
| V0 Query 5 CN | 使用基准数据集研究在词汇掩码设置下保持 LLM 生成质量 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_20

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_20 |
| Original Question | Find papers supporting the claim that knowledgeable LLMs have sufficient inductive capacity to analyze the relationships between multiple papers and systematically write a survey on them. |
| Question Chinese Translation | 寻找支持以下观点的论文：知识丰富的 LLM 具有足够的归纳能力，能够分析多篇论文之间的关系，并据此系统地撰写综述。 |
| Baseline Query 1 | Survey papers on inductive capacity of language models |
| Baseline Query 1 CN | 关于语言模型归纳能力的综述论文 |
| Baseline Query 2 | Research on the impact of large language models on academic literature review |
| Baseline Query 2 CN | 关于大语言模型对学术文献综述影响的研究 |
| Baseline Query 3 | Scholarly articles on the analysis of multiple papers by LLMs |
| Baseline Query 3 CN | 关于 LLM 分析多篇论文的学术文章 |
| Baseline Query 4 | Papers on systematic review writing by AI models |
| Baseline Query 4 CN | 关于 AI 模型撰写系统性综述的论文 |
| Baseline Query 5 | LLMs and their ability to analyze multiple research papers |
| Baseline Query 5 CN | LLM 及其分析多篇研究论文的能力 |
| V0 Query 1 | Research on inductive capacity of language models |
| V0 Query 1 CN | 关于语言模型归纳能力的研究 |
| V0 Query 2 | Survey writing capabilities of advanced LLMs |
| V0 Query 2 CN | 先进 LLM 的综述撰写能力 |
| V0 Query 3 | Inter-paper relationship analysis in LLMs |
| V0 Query 3 CN | LLM 中的论文间关系分析 |
| V0 Query 4 | Multi-document analysis capabilities of LLMs |
| V0 Query 4 CN | LLM 的多文档分析能力 |
| V0 Query 5 | Existing datasets for evaluating inductive capacity of LLMs |
| V0 Query 5 CN | 用于评估 LLM 归纳能力的现有数据集 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_21

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_21 |
| Original Question | Search for papers related to large language models that demonstrate how the same prompt with different responses can improve the performance of the SFT model. |
| Question Chinese Translation | 寻找与大语言模型相关的论文，展示同一提示词搭配不同回答如何提升 SFT 模型的性能。 |
| Baseline Query 1 | Papers on enhancing SFT model performance with different response prompts |
| Baseline Query 1 CN | 关于通过不同回答提示词增强 SFT 模型性能的论文 |
| Baseline Query 2 | Research on the impact of diverse responses on the performance of SFT models |
| Baseline Query 2 CN | 关于多样化回答对 SFT 模型性能影响的研究 |
| Baseline Query 3 | Survey papers on the use of varied responses to a single prompt in large language models for SFT |
| Baseline Query 3 CN | 关于大语言模型中为 SFT 使用同一提示词的多种回答的综述论文 |
| Baseline Query 4 | Studies on how different responses to the same prompt affect SFT model |
| Baseline Query 4 CN | 关于同一提示词的不同回答如何影响 SFT 模型的研究 |
| Baseline Query 5 | Prompt engineering methods for improving SFT model performance in large language models |
| Baseline Query 5 CN | 用于提升大语言模型中 SFT 模型性能的提示工程方法 |
| V0 Query 1 | Exploration on enhancing SFT model performance with different response prompts |
| V0 Query 1 CN | 探索通过不同回答提示词增强 SFT 模型性能 |
| V0 Query 2 | Investigations into prompt engineering methods for enhancing SFT model performance |
| V0 Query 2 CN | 研究用于增强 SFT 模型性能的提示工程方法 |
| V0 Query 3 | Research on the impact of diverse responses to the same prompt in SFT model optimization |
| V0 Query 3 CN | 关于同一提示词的多样化回答对 SFT 模型优化影响的研究 |
| V0 Query 4 | Studies on improving SFT model performance with varied prompt responses |
| V0 Query 4 CN | 关于通过多样化提示词回答提升 SFT 模型性能的研究 |
| V0 Query 5 | Examination of the effectiveness of diverse prompt responses on SFT model benchmark datasets |
| V0 Query 5 CN | 检验多样化提示词回答在 SFT 模型基准数据集上的有效性 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_22

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_22 |
| Original Question | Papers on solving common sense problems in machine translation. |
| Question Chinese Translation | 关于解决机器翻译中常识问题的论文。 |
| Baseline Query 1 | Machine translation challenges in commonsense reasoning |
| Baseline Query 1 CN | 常识推理中的机器翻译挑战 |
| Baseline Query 2 | Algorithms used in solving common sense problems in machine translation |
| Baseline Query 2 CN | 用于解决机器翻译中常识问题的算法 |
| Baseline Query 3 | Improving common sense in machine translation |
| Baseline Query 3 CN | 改善机器翻译中的常识 |
| Baseline Query 4 | Research articles on machine translation and common sense issues |
| Baseline Query 4 CN | 关于机器翻译和常识问题的研究文章 |
| Baseline Query 5 | Survey papers on common sense problems in machine translation |
| Baseline Query 5 CN | 关于机器翻译中常识问题的综述论文 |
| V0 Query 1 | Papers on applying commonsense reasoning to machine translation |
| V0 Query 1 CN | 关于将常识推理应用于机器翻译的论文 |
| V0 Query 2 | Studies on overcoming common sense barriers in machine translation |
| V0 Query 2 CN | 关于克服机器翻译中常识障碍的研究 |
| V0 Query 3 | Research on solving common sense issues in machine translation |
| V0 Query 3 CN | 关于解决机器翻译中常识问题的研究 |
| V0 Query 4 | Evaluating common sense solutions in machine translation tasks |
| V0 Query 4 CN | 评估机器翻译任务中的常识问题解决方案 |
| V0 Query 5 | Papers on solving common sense problems in machine translation |
| V0 Query 5 CN | 关于解决机器翻译中常识问题的论文 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_23

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_23 |
| Original Question | Show me papers utilizing reinforcement learning to optimize diffusion models for video generation. |
| Question Chinese Translation | 请提供使用强化学习来优化视频生成扩散模型的论文。 |
| Baseline Query 1 | Papers on diffusion models for video generation optimized with reinforcement learning |
| Baseline Query 1 CN | 关于使用强化学习优化视频生成扩散模型的论文 |
| Baseline Query 2 | Research on reinforcement learning techniques in video diffusion models optimization |
| Baseline Query 2 CN | 关于视频扩散模型优化中强化学习技术的研究 |
| Baseline Query 3 | Survey papers on reinforcement learning optimization in video generation |
| Baseline Query 3 CN | 关于视频生成中强化学习优化的综述论文 |
| Baseline Query 4 | Studies on video synthesis using reinforcement learning in diffusion models |
| Baseline Query 4 CN | 关于在扩散模型中使用强化学习进行视频合成的研究 |
| Baseline Query 5 | Use of reinforcement learning in optimizing diffusion models for video production |
| Baseline Query 5 CN | 使用强化学习优化用于视频制作的扩散模型 |
| V0 Query 1 | Papers on reinforcement learning optimization for diffusion models |
| V0 Query 1 CN | 关于扩散模型强化学习优化的论文 |
| V0 Query 2 | Papers on reinforcement learning optimization for video generation |
| V0 Query 2 CN | 关于视频生成强化学习优化的论文 |
| V0 Query 3 | Benchmark datasets used in reinforcement learning optimization for video generation |
| V0 Query 3 CN | 视频生成强化学习优化中使用的基准数据集 |
| V0 Query 4 | Papers on reinforcement learning optimization for diffusion models in video generation |
| V0 Query 4 CN | 关于视频生成中扩散模型强化学习优化的论文 |
| V0 Query 5 | Papers on reinforcement learning optimization for diffusion models in video generation |
| V0 Query 5 CN | 关于视频生成中扩散模型强化学习优化的论文 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_24

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_24 |
| Original Question | Show me all research papers on machine translation agents. |
| Question Chinese Translation | 请提供所有关于机器翻译智能体的研究论文。 |
| Baseline Query 1 | Machine translation agents research papers |
| Baseline Query 1 CN | 机器翻译智能体研究论文 |
| Baseline Query 2 | Papers on machine translation using agents |
| Baseline Query 2 CN | 关于使用智能体进行机器翻译的论文 |
| Baseline Query 3 | Survey papers on machine translation |
| Baseline Query 3 CN | 关于机器翻译的综述论文 |
| Baseline Query 4 | Research on machine learning in machine translation |
| Baseline Query 4 CN | 关于机器翻译中机器学习的研究 |
| Baseline Query 5 | Latest advancements in machine translation agents |
| Baseline Query 5 CN | 机器翻译智能体的最新进展 |
| V0 Query 1 | Latest advancements in machine translation agents |
| V0 Query 1 CN | 机器翻译智能体的最新进展 |
| V0 Query 2 | Influence of reinforcement learning in machine translation agents |
| V0 Query 2 CN | 强化学习对机器翻译智能体的影响 |
| V0 Query 3 | Evolution of machine translation technology |
| V0 Query 3 CN | 机器翻译技术的演进 |
| V0 Query 4 | Application of machine translation in wearable technology |
| V0 Query 4 CN | 机器翻译在可穿戴技术中的应用 |
| V0 Query 5 | Challenges in machine translation agent development |
| V0 Query 5 CN | 开发机器翻译智能体所面临的挑战 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_25

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_25 |
| Original Question | Video aesthetics score, using multimodal large models. |
| Question Chinese Translation | 使用多模态大模型进行视频美学评分。 |
| Baseline Query 1 | Multimodal large models for video analysis |
| Baseline Query 1 CN | 用于视频分析的多模态大模型 |
| Baseline Query 2 | Use of multimodal large models in video scoring |
| Baseline Query 2 CN | 多模态大模型在视频评分中的使用 |
| Baseline Query 3 | Survey papers on video aesthetics score using multimodal models |
| Baseline Query 3 CN | 关于使用多模态模型进行视频美学评分的综述论文 |
| Baseline Query 4 | Multimodal machine learning for video aesthetics |
| Baseline Query 4 CN | 用于视频美学的多模态机器学习 |
| Baseline Query 5 | Large language models in video quality assessment |
| Baseline Query 5 CN | 视频质量评估中的大语言模型 |
| V0 Query 1 | Overview of video aesthetics scoring using multimodal large models |
| V0 Query 1 CN | 使用多模态大模型进行视频美学评分的概述 |
| V0 Query 2 | Application tasks of video aesthetics scoring with multimodal large models |
| V0 Query 2 CN | 使用多模态大模型进行视频美学评分的应用任务 |
| V0 Query 3 | Technical mechanisms used in multimodal large models for video aesthetics scoring |
| V0 Query 3 CN | 多模态大模型进行视频美学评分所使用的技术机制 |
| V0 Query 4 | Benchmark datasets used in multimodal large models for video aesthetics scoring |
| V0 Query 4 CN | 多模态大模型进行视频美学评分所使用的基准数据集 |
| V0 Query 5 | Exploration of video aesthetics through the lens of multimodal large models |
| V0 Query 5 CN | 从多模态大模型的视角探索视频美学 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_26

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_26 |
| Original Question | Scaling Laws for Fine-Grained Mixture of Experts. |
| Question Chinese Translation | 细粒度混合专家的缩放定律。 |
| Baseline Query 1 | Survey papers on Scaling Laws for Fine-Grained Mixture of Experts |
| Baseline Query 1 CN | 关于细粒度混合专家缩放定律的综述论文 |
| Baseline Query 2 | Scaling laws in fine-grained mixture of experts model |
| Baseline Query 2 CN | 细粒度混合专家模型中的缩放定律 |
| Baseline Query 3 | Influence of mixture of experts on scaling laws |
| Baseline Query 3 CN | 混合专家对缩放定律的影响 |
| Baseline Query 4 | Examination of the impact of parameter increase on performance scaling in Fine-Grained Mixture of Experts |
| Baseline Query 4 CN | 考察参数增加对细粒度混合专家性能缩放的影响 |
| Baseline Query 5 | Optimization of mixture of experts model using scaling laws |
| Baseline Query 5 CN | 使用缩放定律优化混合专家模型 |
| V0 Query 1 | Application of scaling laws to mixture of experts model |
| V0 Query 1 CN | 缩放定律在混合专家模型中的应用 |
| V0 Query 2 | Understanding the impact of fine-grained mixture on expert performance |
| V0 Query 2 CN | 理解细粒度混合对专家性能的影响 |
| V0 Query 3 | Exploration of fine-grained mixture of experts in machine learning |
| V0 Query 3 CN | 探索机器学习中的细粒度混合专家 |
| V0 Query 4 | Scaling laws for fine-grained mixture of experts datasets |
| V0 Query 4 CN | 面向细粒度混合专家数据集的缩放定律 |
| V0 Query 5 | Investigation of scaling laws in various application tasks of mixture of experts model |
| V0 Query 5 CN | 研究混合专家模型在各种应用任务中的缩放定律 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_27

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_27 |
| Original Question | Show me research on rejection sampling finetuning. |
| Question Chinese Translation | 请提供关于拒绝采样微调的研究。 |
| Baseline Query 1 | Survey papers on rejection sampling fine-tuning |
| Baseline Query 1 CN | 关于拒绝采样微调的综述论文 |
| Baseline Query 2 | Research articles on fine-tuning techniques in rejection sampling |
| Baseline Query 2 CN | 关于拒绝采样中微调技术的研究文章 |
| Baseline Query 3 | Academic studies on rejection sampling optimization |
| Baseline Query 3 CN | 关于拒绝采样优化的学术研究 |
| Baseline Query 4 | Rejection sampling fine-tuning in machine learning |
| Baseline Query 4 CN | 机器学习中的拒绝采样微调 |
| Baseline Query 5 | Studies on improving rejection sampling efficiency in fine-tuning |
| Baseline Query 5 CN | 关于提升微调中拒绝采样效率的研究 |
| V0 Query 1 | Research on detailed explanation of rejection sampling fine-tuning technique |
| V0 Query 1 CN | 关于详细解释拒绝采样微调技术的研究 |
| V0 Query 2 | Research on improving worst-group accuracy in rejection sampling fine-tuning |
| V0 Query 2 CN | 关于提升拒绝采样微调中最差群体准确率的研究 |
| V0 Query 3 | Research on different methods for rejection sampling fine-tuning |
| V0 Query 3 CN | 关于拒绝采样微调不同方法的研究 |
| V0 Query 4 | Case studies on rejection sampling fine-tuning in various tasks |
| V0 Query 4 CN | 关于拒绝采样微调在各种任务中应用的案例研究 |
| V0 Query 5 | Benchmark datasets for rejection sampling fine-tuning |
| V0 Query 5 CN | 用于拒绝采样微调的基准数据集 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_28

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_28 |
| Original Question | Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests. |
| Question Chinese Translation | 请提供中等难度的代码评测数据集。其难度应高于 HumanEval 和 MBPP，但低于 code_contests。 |
| Baseline Query 1 | Survey papers on code evaluation datasets |
| Baseline Query 1 CN | 关于代码评测数据集的综述论文 |
| Baseline Query 2 | Middle difficulty level code evaluation datasets |
| Baseline Query 2 CN | 中等难度的代码评测数据集 |
| Baseline Query 3 | Code evaluation datasets with mid-level hardness |
| Baseline Query 3 CN | 具有中等难度的代码评测数据集 |
| Baseline Query 4 | Comparison studies on difficulty levels of different code evaluation datasets |
| Baseline Query 4 CN | 关于不同代码评测数据集难度水平的比较研究 |
| Baseline Query 5 | [NOT GENERATED IN BASELINE] |
| Baseline Query 5 CN | [NOT GENERATED IN BASELINE]（原始记录未生成） |
| V0 Query 1 | Survey papers on mid-level hardness code evaluation datasets |
| V0 Query 1 CN | 关于中等难度代码评测数据集的综述论文 |
| V0 Query 2 | Comparison between HumanEval, MBPP, code_contests and other datasets |
| V0 Query 2 CN | HumanEval、MBPP、code_contests 与其他数据集之间的比较 |
| V0 Query 3 | Investigation on mid-level hardness in code evaluation datasets |
| V0 Query 3 CN | 关于代码评测数据集中等难度的研究 |
| V0 Query 4 | Development of a new mid-level hardness code evaluation dataset |
| V0 Query 4 CN | 开发一个新的中等难度代码评测数据集 |
| V0 Query 5 | StopSearch |
| V0 Query 5 CN | 停止搜索（StopSearch） |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_29

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_29 |
| Original Question | Research on teaching llms to do math prove and solve IMO level math problems. |
| Question Chinese Translation | 关于教 LLM 进行数学证明并解决 IMO 级别数学问题的研究。 |
| Baseline Query 1 | Survey papers on teaching language models mathematics |
| Baseline Query 1 CN | 关于教语言模型学习数学的综述论文 |
| Baseline Query 2 | Research on solving IMO level math problems using LLMs |
| Baseline Query 2 CN | 关于使用 LLM 解决 IMO 级别数学问题的研究 |
| Baseline Query 3 | Methods to teach language models mathematical proof |
| Baseline Query 3 CN | 教语言模型进行数学证明的方法 |
| Baseline Query 4 | Advanced techniques to solve IMO level math problems with LLMs |
| Baseline Query 4 CN | 使用 LLM 解决 IMO 级别数学问题的先进技术 |
| Baseline Query 5 | Machine learning approaches for solving IMO problems |
| Baseline Query 5 CN | 解决 IMO 问题的机器学习方法 |
| V0 Query 1 | Machine learning approaches for solving IMO level math problems |
| V0 Query 1 CN | 解决 IMO 级别数学问题的机器学习方法 |
| V0 Query 2 | Research on teaching language models mathematical problem-solving skills at IMO level |
| V0 Query 2 CN | 关于教语言模型掌握 IMO 级别数学解题技能的研究 |
| V0 Query 3 | Research on teaching language models mathematical proof |
| V0 Query 3 CN | 关于教语言模型进行数学证明的研究 |
| V0 Query 4 | Research on teaching large language models advanced mathematics problem-solving techniques |
| V0 Query 4 CN | 关于教大语言模型掌握高等数学解题技术的研究 |
| V0 Query 5 | Limitations of current AI in solving IMO level math problems |
| V0 Query 5 CN | 当前 AI 在解决 IMO 级别数学问题方面的局限 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_30

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_30 |
| Original Question | I would like to find some research papers about test time training topic, in LLM research area. |
| Question Chinese Translation | 我想寻找一些 LLM 研究领域中关于测试时训练这一主题的研究论文。 |
| Baseline Query 1 | Survey papers on test time training in language models |
| Baseline Query 1 CN | 关于语言模型测试时训练的综述论文 |
| Baseline Query 2 | Test-time training techniques in large language models |
| Baseline Query 2 CN | 大语言模型中的测试时训练技术 |
| Baseline Query 3 | Advancements in test time training for language models |
| Baseline Query 3 CN | 语言模型测试时训练的进展 |
| Baseline Query 4 | LLM research on test time training |
| Baseline Query 4 CN | 关于测试时训练的 LLM 研究 |
| Baseline Query 5 | Online learning techniques for test-time training in large language models |
| Baseline Query 5 CN | 大语言模型测试时训练中的在线学习技术 |
| V0 Query 1 | Overview of test-time training techniques in LLMs |
| V0 Query 1 CN | LLM 测试时训练技术概述 |
| V0 Query 2 | Adversarial approaches for test-time training in large language models |
| V0 Query 2 CN | 大语言模型测试时训练的对抗式方法 |
| V0 Query 3 | Investigations on reducing inference costs in test-time training for large language models |
| V0 Query 3 CN | 关于降低大语言模型测试时训练推理成本的研究 |
| V0 Query 4 | Exploration of test-time training in language model research |
| V0 Query 4 CN | 探索语言模型研究中的测试时训练 |
| V0 Query 5 | Comprehensive study on test time training in LLMs |
| V0 Query 5 CN | 关于 LLM 测试时训练的综合研究 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_31

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_31 |
| Original Question | DPO training for large-scale vision-language models. |
| Question Chinese Translation | 面向大规模视觉—语言模型的 DPO 训练。 |
| Baseline Query 1 | Survey papers on DPO training for vision-language models |
| Baseline Query 1 CN | 关于视觉—语言模型 DPO 训练的综述论文 |
| Baseline Query 2 | Effects of DPO training on large-scale vision-language models |
| Baseline Query 2 CN | DPO 训练对大规模视觉—语言模型的影响 |
| Baseline Query 3 | Comparative studies on DPO and other methods for training large-scale vision-language models |
| Baseline Query 3 CN | 关于 DPO 与其他大规模视觉—语言模型训练方法的比较研究 |
| Baseline Query 4 | Application of DPO in large-scale vision-language model training |
| Baseline Query 4 CN | DPO 在大规模视觉—语言模型训练中的应用 |
| Baseline Query 5 | Challenges in DPO training for large-scale vision-language models |
| Baseline Query 5 CN | 大规模视觉—语言模型 DPO 训练中的挑战 |
| V0 Query 1 | Overview of DPO training in vision-language models |
| V0 Query 1 CN | 视觉—语言模型 DPO 训练概述 |
| V0 Query 2 | Influence of DPO training on large-scale vision-language models performance |
| V0 Query 2 CN | DPO 训练对大规模视觉—语言模型性能的影响 |
| V0 Query 3 | Comparative analysis of DPO training with other techniques in vision-language models |
| V0 Query 3 CN | 对视觉—语言模型中 DPO 训练与其他技术进行比较分析 |
| V0 Query 4 | Applications of DPO training in vision-language models |
| V0 Query 4 CN | DPO 训练在视觉—语言模型中的应用 |
| V0 Query 5 | Exploring the efficacy and stability of DPO training in large-scale vision-language models |
| V0 Query 5 CN | 探索 DPO 训练在大规模视觉—语言模型中的有效性和稳定性 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_32

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_32 |
| Original Question | Show me cutting edge research works on neural network based quantum Monte Carlo. |
| Question Chinese Translation | 请提供关于基于神经网络的量子蒙特卡洛的前沿研究。 |
| Baseline Query 1 | Application of neural networks in quantum Monte Carlo studies |
| Baseline Query 1 CN | 神经网络在量子蒙特卡洛研究中的应用 |
| Baseline Query 2 | Neural network based quantum Monte Carlo papers |
| Baseline Query 2 CN | 关于基于神经网络的量子蒙特卡洛的论文 |
| Baseline Query 3 | Recent advancements in quantum Monte Carlo using neural networks |
| Baseline Query 3 CN | 使用神经网络进行量子蒙特卡洛的最新进展 |
| Baseline Query 4 | Survey papers on neural network based quantum Monte Carlo |
| Baseline Query 4 CN | 关于基于神经网络的量子蒙特卡洛的综述论文 |
| Baseline Query 5 | State-of-the-art research in neural network quantum Monte Carlo |
| Baseline Query 5 CN | 神经网络量子蒙特卡洛领域的前沿研究 |
| V0 Query 1 | Latest advancements in Neural Network methods for Quantum Monte Carlo |
| V0 Query 1 CN | 用于量子蒙特卡洛的神经网络方法的最新进展 |
| V0 Query 2 | Exploration of neural network applications in quantum Monte Carlo studies |
| V0 Query 2 CN | 探索神经网络在量子蒙特卡洛研究中的应用 |
| V0 Query 3 | Use cases of Neural Networks in Quantum Monte Carlo simulations |
| V0 Query 3 CN | 神经网络在量子蒙特卡洛模拟中的应用案例 |
| V0 Query 4 | Incorporation of Neural Networks in Quantum Monte Carlo: recent studies |
| V0 Query 4 CN | 将神经网络引入量子蒙特卡洛：近期研究 |
| V0 Query 5 | Recent research on neural network-based quantum Monte Carlo datasets |
| V0 Query 5 CN | 关于基于神经网络的量子蒙特卡洛数据集的近期研究 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_33

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_33 |
| Original Question | Show me some popular papers on generating textual adversarial examples for machine translation. |
| Question Chinese Translation | 请提供一些关于为机器翻译生成文本对抗样本的热门论文。 |
| Baseline Query 1 | Survey papers on textual adversarial examples in machine translation |
| Baseline Query 1 CN | 关于机器翻译中文本对抗样本的综述论文 |
| Baseline Query 2 | Textual adversarial examples in machine translation research papers |
| Baseline Query 2 CN | 机器翻译中的文本对抗样本研究论文 |
| Baseline Query 3 | Adversarial example creation in machine translation using textual methods |
| Baseline Query 3 CN | 在机器翻译中使用文本方法创建对抗样本 |
| Baseline Query 4 | State-of-the-art techniques for generating adversarial examples in machine translation |
| Baseline Query 4 CN | 在机器翻译中生成对抗样本的前沿技术 |
| Baseline Query 5 | Methods for generating adversarial examples in machine translation |
| Baseline Query 5 CN | 在机器翻译中生成对抗样本的方法 |
| V0 Query 1 | Research articles on adversarial attacks on machine translation systems |
| V0 Query 1 CN | 关于对机器翻译系统进行对抗攻击的研究文章 |
| V0 Query 2 | Exploring the impact of Adversarial Machine Translation on NMT systems |
| V0 Query 2 CN | 探索对抗式机器翻译对 NMT 系统的影响 |
| V0 Query 3 | Textual adversarial examples for machine translation techniques |
| V0 Query 3 CN | 面向机器翻译技术的文本对抗样本 |
| V0 Query 4 | Exploration of adversarial attacks on machine translation systems |
| V0 Query 4 CN | 探索对机器翻译系统的对抗攻击 |
| V0 Query 5 | Limitations of current techniques in generating textual adversarial examples for machine translation |
| V0 Query 5 CN | 当前技术在为机器翻译生成文本对抗样本方面的局限 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_34

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_34 |
| Original Question | Show me research on 3d scene understanding leveraging progress on 3D AIGC foundation models. |
| Question Chinese Translation | 请提供利用 3D AIGC 基础模型进展进行 3D 场景理解的研究。 |
| Baseline Query 1 | Foundation models and their role in 3D scene understanding |
| Baseline Query 1 CN | 基础模型及其在 3D 场景理解中的作用 |
| Baseline Query 2 | Application of 3D AIGC foundation models in scene understanding |
| Baseline Query 2 CN | 3D AIGC 基础模型在场景理解中的应用 |
| Baseline Query 3 | Advancements in 3D AIGC foundational models for scene understanding |
| Baseline Query 3 CN | 用于场景理解的 3D AIGC 基础模型的进展 |
| Baseline Query 4 | Research on 3D scene understanding using AIGC |
| Baseline Query 4 CN | 关于使用 AIGC 进行 3D 场景理解的研究 |
| Baseline Query 5 | Survey papers on 3D scene understanding with 3D AIGC models |
| Baseline Query 5 CN | 关于使用 3D AIGC 模型进行 3D 场景理解的综述论文 |
| V0 Query 1 | Research on 3D AIGC foundation models for scene understanding |
| V0 Query 1 CN | 关于用于场景理解的 3D AIGC 基础模型的研究 |
| V0 Query 2 | Application of 3D AIGC foundation models in scene understanding |
| V0 Query 2 CN | 3D AIGC 基础模型在场景理解中的应用 |
| V0 Query 3 | Exploration of 3D scene understanding using 3D AIGC foundation models |
| V0 Query 3 CN | 探索使用 3D AIGC 基础模型进行 3D 场景理解 |
| V0 Query 4 | Techniques employed in 3D scene understanding with 3D AIGC models |
| V0 Query 4 CN | 使用 3D AIGC 模型进行 3D 场景理解所采用的技术 |
| V0 Query 5 | Evaluation of 3D AIGC foundation models on 3D scene understanding tasks |
| V0 Query 5 CN | 在 3D 场景理解任务上评估 3D AIGC 基础模型 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_35

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_35 |
| Original Question | Give me papers about LLM quantized pretraining. |
| Question Chinese Translation | 请提供关于 LLM 量化预训练的论文。 |
| Baseline Query 1 | Survey papers on LLM quantized pretraining |
| Baseline Query 1 CN | 关于 LLM 量化预训练的综述论文 |
| Baseline Query 2 | Quantitative pretraining of language models |
| Baseline Query 2 CN | 语言模型的定量预训练 |
| Baseline Query 3 | Methods for quantized pretraining in LLM |
| Baseline Query 3 CN | LLM 量化预训练的方法 |
| Baseline Query 4 | Research on quantization techniques in LLM pretraining |
| Baseline Query 4 CN | 关于 LLM 预训练中量化技术的研究 |
| Baseline Query 5 | Effects of quantization on language model pretraining |
| Baseline Query 5 CN | 量化对语言模型预训练的影响 |
| V0 Query 1 | Introduction to quantization techniques in LLM pretraining |
| V0 Query 1 CN | LLM 预训练中的量化技术介绍 |
| V0 Query 2 | Latest research on LLM quantized pretraining |
| V0 Query 2 CN | 关于 LLM 量化预训练的最新研究 |
| V0 Query 3 | Quantitative pretraining tasks for language models |
| V0 Query 3 CN | 语言模型的定量预训练任务 |
| V0 Query 4 | Comparison of quantization methods in LLM pretraining |
| V0 Query 4 CN | LLM 预训练中量化方法的比较 |
| V0 Query 5 | Benchmark datasets in LLM quantized pretraining studies |
| V0 Query 5 CN | LLM 量化预训练研究中的基准数据集 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_36

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_36 |
| Original Question | Show me research on identity preservation video generation. |
| Question Chinese Translation | 请提供关于身份保持视频生成的研究。 |
| Baseline Query 1 | Survey papers on identity preservation in video generation |
| Baseline Query 1 CN | 关于视频生成中身份保持的综述论文 |
| Baseline Query 2 | Deep learning techniques for identity preservation in video generation |
| Baseline Query 2 CN | 视频生成中用于身份保持的深度学习技术 |
| Baseline Query 3 | Research articles on identity preservation video creation |
| Baseline Query 3 CN | 关于身份保持视频创作的研究文章 |
| Baseline Query 4 | Latest techniques in identity preservation video generation |
| Baseline Query 4 CN | 身份保持视频生成的最新技术 |
| Baseline Query 5 | AI approaches for identity preservation in video editing |
| Baseline Query 5 CN | 视频编辑中用于身份保持的 AI 方法 |
| V0 Query 1 | Research on the latest methods for preserving identities in video generation |
| V0 Query 1 CN | 关于视频生成中保持身份的最新方法的研究 |
| V0 Query 2 | Research on identity preservation in video generation |
| V0 Query 2 CN | 关于视频生成中身份保持的研究 |
| V0 Query 3 | Exploration of identity preservation video generation research |
| V0 Query 3 CN | 探索身份保持视频生成研究 |
| V0 Query 4 | Research on techniques used in identity preservation video generation |
| V0 Query 4 CN | 关于身份保持视频生成所用技术的研究 |
| V0 Query 5 | Limitations and challenges in identity preservation video generation |
| V0 Query 5 CN | 身份保持视频生成的局限与挑战 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_37

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_37 |
| Original Question | Give me some papers showing that LLM agents can do schedule planning. |
| Question Chinese Translation | 请提供一些表明 LLM 智能体能够进行日程规划的论文。 |
| Baseline Query 1 | Survey papers on schedule planning with Language Model agents |
| Baseline Query 1 CN | 关于使用语言模型智能体进行日程规划的综述论文 |
| Baseline Query 2 | Research articles on LLM-based schedule planning |
| Baseline Query 2 CN | 关于基于 LLM 的日程规划的研究文章 |
| Baseline Query 3 | LLM agents in schedule planning research papers |
| Baseline Query 3 CN | 日程规划研究论文中的 LLM 智能体 |
| Baseline Query 4 | Use of LLM agents in schedule planning studies |
| Baseline Query 4 CN | 日程规划研究中 LLM 智能体的使用 |
| Baseline Query 5 | Language Model agents and their application in schedule planning |
| Baseline Query 5 CN | 语言模型智能体及其在日程规划中的应用 |
| V0 Query 1 | Methods used in LLM for schedule planning |
| V0 Query 1 CN | LLM 中用于日程规划的方法 |
| V0 Query 2 | Use of LLM in schedule planning tasks |
| V0 Query 2 CN | LLM 在日程规划任务中的使用 |
| V0 Query 3 | Techniques employed by LLM agents for schedule planning |
| V0 Query 3 CN | LLM 智能体用于日程规划的技术 |
| V0 Query 4 | Different domains where LLMs have done schedule planning |
| V0 Query 4 CN | LLM 已开展日程规划的不同领域 |
| V0 Query 5 | Research on LLM agents in schedule planning |
| V0 Query 5 CN | 关于 LLM 智能体进行日程规划的研究 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_38

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_38 |
| Original Question | Show me research on image encoding distributions. |
| Question Chinese Translation | 请提供关于图像编码分布的研究。 |
| Baseline Query 1 | Investigations on the use of diffusion models for image encoding distributions |
| Baseline Query 1 CN | 关于使用扩散模型处理图像编码分布的研究 |
| Baseline Query 2 | Survey papers on image encoding distributions |
| Baseline Query 2 CN | 关于图像编码分布的综述论文 |
| Baseline Query 3 | Research on binary image compression using probabilistic encoding and decoding |
| Baseline Query 3 CN | 关于使用概率编码与解码进行二进制图像压缩的研究 |
| Baseline Query 4 | Studies on image encoding techniques and their distribution |
| Baseline Query 4 CN | 关于图像编码技术及其分布的研究 |
| Baseline Query 5 | Analysis of image encoding distributions in machine learning |
| Baseline Query 5 CN | 机器学习中的图像编码分布分析 |
| V0 Query 1 | Overview of image encoding distributions research |
| V0 Query 1 CN | 图像编码分布研究概述 |
| V0 Query 2 | Research on binomial image compression and encoding distributions |
| V0 Query 2 CN | 关于二项式图像压缩与编码分布的研究 |
| V0 Query 3 | Use cases of image encoding distributions in AI |
| V0 Query 3 CN | 图像编码分布在 AI 中的应用案例 |
| V0 Query 4 | Methods for image encoding distributions |
| V0 Query 4 CN | 图像编码分布的方法 |
| V0 Query 5 | Benchmark datasets for image encoding distributions |
| V0 Query 5 CN | 用于图像编码分布的基准数据集 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_39

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_39 |
| Original Question | Help me search for the work related to the synthetic data of large language models. I want to know how to automatically generate large-scale, high-quality, diverse, difficult, and valuable long thought data for learning. |
| Question Chinese Translation | 请帮我寻找与大语言模型合成数据相关的工作。我想了解如何自动生成用于学习的大规模、高质量、多样、困难且有价值的长思维数据。 |
| Baseline Query 1 | Survey papers on synthetic data for large language models |
| Baseline Query 1 CN | 关于大语言模型合成数据的综述论文 |
| Baseline Query 2 | Methods for generating valuable long thought data for AI learning |
| Baseline Query 2 CN | 生成用于 AI 学习的有价值长思维数据的方法 |
| Baseline Query 3 | Research on automatic generation of high-quality diverse data for language models |
| Baseline Query 3 CN | 关于为语言模型自动生成高质量、多样化数据的研究 |
| Baseline Query 4 | Techniques for generating synthetic data for language model training |
| Baseline Query 4 CN | 为语言模型训练生成合成数据的技术 |
| Baseline Query 5 | Efficient methods for sampling diverse test cases from large language models using synthetic data |
| Baseline Query 5 CN | 使用合成数据从大语言模型中高效采样多样化测试用例的方法 |
| V0 Query 1 | [FAILED GENERATION] |
| V0 Query 1 CN | [FAILED GENERATION]（生成失败，留空） |
| V0 Query 2 | Challenges in generating high-quality long thought data for language model training |
| V0 Query 2 CN | 为语言模型训练生成高质量长思维数据所面临的挑战 |
| V0 Query 3 | Auto-generation techniques for diverse long thought data in language models |
| V0 Query 3 CN | 语言模型中多样化长思维数据的自动生成技术 |
| V0 Query 4 | [FAILED GENERATION] |
| V0 Query 4 CN | [FAILED GENERATION]（生成失败，留空） |
| V0 Query 5 | Exploration on large scale pretraining of language models with synthetic data |
| V0 Query 5 CN | 探索使用合成数据进行语言模型大规模预训练 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_40

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_40 |
| Original Question | Could you list research that demonstrates the advantages of Quantization-Aware Training (QAT), which can enable the model to learn better representations for low-bit weights?. |
| Question Chinese Translation | 能否列出一些研究，展示量化感知训练（QAT）的优势，即它能够使模型为低比特权重学到更好的表示？ |
| Baseline Query 1 | Survey papers on Quantization-Aware Training benefits |
| Baseline Query 1 CN | 关于量化感知训练益处的综述论文 |
| Baseline Query 2 | Advantages of Quantization-Aware Training in AI |
| Baseline Query 2 CN | 量化感知训练在 AI 中的优势 |
| Baseline Query 3 | Research papers on the impact of Quantization-Aware Training on low-bit weight representations |
| Baseline Query 3 CN | 关于量化感知训练对低比特权重表示影响的研究论文 |
| Baseline Query 4 | Effects of Quantization-Aware Training on model representations |
| Baseline Query 4 CN | 量化感知训练对模型表示的影响 |
| Baseline Query 5 | Comparative studies on Quantization-Aware Training and Post-Training Quantization in AI |
| Baseline Query 5 CN | 关于 AI 中量化感知训练与训练后量化的比较研究 |
| V0 Query 1 | Research on the impact of Quantization-Aware Training on model representations |
| V0 Query 1 CN | 关于量化感知训练对模型表示影响的研究 |
| V0 Query 2 | Studies on QAT and low-bit weight representations |
| V0 Query 2 CN | 关于 QAT 与低比特权重表示的研究 |
| V0 Query 3 | Quantization-Aware Training benefits for low-bit weights research papers |
| V0 Query 3 CN | 关于量化感知训练对低比特权重益处的研究论文 |
| V0 Query 4 | Comparative studies between Quantization-Aware Training and Post-Training Quantization |
| V0 Query 4 CN | 量化感知训练与训练后量化的比较研究 |
| V0 Query 5 | Research on the effectiveness of Quantization-Aware Training in low-bit weight learning |
| V0 Query 5 CN | 关于量化感知训练在低比特权重学习中有效性的研究 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_41

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_41 |
| Original Question | Using synthesis data for scaling up sft data. |
| Question Chinese Translation | 使用合成数据扩大 SFT 数据规模。 |
| Baseline Query 1 | Use of synthetic data in increasing volume of SFT data |
| Baseline Query 1 CN | 使用合成数据增加 SFT 数据量 |
| Baseline Query 2 | Survey paper on usage of synthetic data for scaling up soft target data |
| Baseline Query 2 CN | 关于使用合成数据扩大软目标数据规模的综述论文 |
| Baseline Query 3 | Scaling up SFT data with synthesis data |
| Baseline Query 3 CN | 使用合成数据扩大 SFT 数据规模 |
| Baseline Query 4 | Applications of generative AI in creating synthetic data for soft target data scaling |
| Baseline Query 4 CN | 生成式 AI 在为软目标数据扩展创建合成数据方面的应用 |
| Baseline Query 5 | Exponential growth of training data in NLP through synthetic data |
| Baseline Query 5 CN | 通过合成数据实现 NLP 训练数据的指数增长 |
| V0 Query 1 | Use of synthetic data in language model pre-training |
| V0 Query 1 CN | 合成数据在语言模型预训练中的使用 |
| V0 Query 2 | Techniques for generating synthetic data for SFT |
| V0 Query 2 CN | 为 SFT 生成合成数据的技术 |
| V0 Query 3 | Scaling up SFT data with synthesis data |
| V0 Query 3 CN | 使用合成数据扩大 SFT 数据规模 |
| V0 Query 4 | Effects of synthesis data on SFT data scaling |
| V0 Query 4 CN | 合成数据对 SFT 数据规模扩展的影响 |
| V0 Query 5 | Existing benchmarks for synthetic data in SFT |
| V0 Query 5 CN | 用于 SFT 合成数据的现有基准 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_42

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_42 |
| Original Question | Show me research on how to select frames when doing video understanding. |
| Question Chinese Translation | 请提供关于在视频理解中如何选择帧的研究。 |
| Baseline Query 1 | Survey papers on frame selection in video understanding |
| Baseline Query 1 CN | 关于视频理解中帧选择的综述论文 |
| Baseline Query 2 | Optical flow-based methods for key frame selection in video understanding |
| Baseline Query 2 CN | 视频理解中基于光流的关键帧选择方法 |
| Baseline Query 3 | Research on temporal sampling strategies for video representation learning |
| Baseline Query 3 CN | 关于视频表示学习中时间采样策略的研究 |
| Baseline Query 4 | Studies on efficient frame sampling in video comprehension |
| Baseline Query 4 CN | 关于视频理解中高效帧采样的研究 |
| Baseline Query 5 | Papers on automated video summary generation using frame selection |
| Baseline Query 5 CN | 关于使用帧选择自动生成视频摘要的论文 |
| V0 Query 1 | Research on techniques for selecting key frames in video comprehension |
| V0 Query 1 CN | 关于视频理解中关键帧选择技术的研究 |
| V0 Query 2 | Research on object detection techniques for video frame selection |
| V0 Query 2 CN | 关于用于视频帧选择的目标检测技术的研究 |
| V0 Query 3 | Research on critical frame selection for video comprehension |
| V0 Query 3 CN | 关于视频理解中关键帧选择的研究 |
| V0 Query 4 | Survey papers on frame selection techniques in video analysis |
| V0 Query 4 CN | 关于视频分析中帧选择技术的综述论文 |
| V0 Query 5 | Understanding the importance of frame selection in video analytics |
| V0 Query 5 CN | 理解帧选择在视频分析中的重要性 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_43

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_43 |
| Original Question | AI for Science papers, especially protein design and DPO of antibody design. |
| Question Chinese Translation | 关于 AI for Science 的论文，尤其是蛋白质设计和抗体设计中的 DPO。 |
| Baseline Query 1 | AI tools for protein design |
| Baseline Query 1 CN | 用于蛋白质设计的 AI 工具 |
| Baseline Query 2 | Research on DPO in antibody design |
| Baseline Query 2 CN | 关于抗体设计中 DPO 的研究 |
| Baseline Query 3 | Survey papers on protein design using AI |
| Baseline Query 3 CN | 关于使用 AI 进行蛋白质设计的综述论文 |
| Baseline Query 4 | Application of AI in scientific research papers |
| Baseline Query 4 CN | AI 在科学研究论文中的应用 |
| Baseline Query 5 | AI advancements in protein design |
| Baseline Query 5 CN | AI 在蛋白质设计中的进展 |
| V0 Query 1 | Overview of AI techniques used in protein design |
| V0 Query 1 CN | 蛋白质设计中所用 AI 技术的概述 |
| V0 Query 2 | Studies on Decoupled Protein Optimization (DPO) in antibody design |
| V0 Query 2 CN | 关于抗体设计中解耦蛋白质优化（Decoupled Protein Optimization，DPO）的研究 |
| V0 Query 3 | Algorithms used in AI for protein design |
| V0 Query 3 CN | AI 用于蛋白质设计所使用的算法 |
| V0 Query 4 | [FAILED GENERATION] |
| V0 Query 4 CN | [FAILED GENERATION]（生成失败，留空） |
| V0 Query 5 | Benchmark datasets for AI in protein design |
| V0 Query 5 CN | 用于 AI 蛋白质设计的基准数据集 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_44

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_44 |
| Original Question | What are the researches that have explored the application of Crypto-based Private Learning in privacy-preserving machine learning?. |
| Question Chinese Translation | 哪些研究探索了基于密码学的隐私学习（Crypto-based Private Learning）在隐私保护机器学习中的应用？ |
| Baseline Query 1 | Survey papers on Crypto-based Private Learning in machine learning |
| Baseline Query 1 CN | 关于机器学习中基于密码学的隐私学习的综述论文 |
| Baseline Query 2 | Application of cryptographic techniques in private machine learning |
| Baseline Query 2 CN | 密码学技术在隐私机器学习中的应用 |
| Baseline Query 3 | Research on encryption methods in privacy-preserving machine learning |
| Baseline Query 3 CN | 关于隐私保护机器学习中加密方法的研究 |
| Baseline Query 4 | Use of homomorphic encryption in private learning for machine learning |
| Baseline Query 4 CN | 在机器学习的隐私学习中使用同态加密 |
| Baseline Query 5 | Research articles on privacy-preserving machine learning using cryptography |
| Baseline Query 5 CN | 关于使用密码学进行隐私保护机器学习的研究文章 |
| V0 Query 1 | Overview of cryptographic methods used for privacy in machine learning |
| V0 Query 1 CN | 机器学习中用于隐私保护的密码学方法概述 |
| V0 Query 2 | Studies on the use of differential privacy and homomorphic encryption in private learning for machine learning |
| V0 Query 2 CN | 关于在机器学习的隐私学习中使用差分隐私和同态加密的研究 |
| V0 Query 3 | Research papers on application of cryptography in privacy preserving ML |
| V0 Query 3 CN | 关于密码学在隐私保护机器学习中应用的研究论文 |
| V0 Query 4 | Comparison between cryptographic-based private learning and differential privacy in machine learning |
| V0 Query 4 CN | 机器学习中基于密码学的隐私学习与差分隐私的比较 |
| V0 Query 5 | Exploration of various cryptographic techniques in privacy-preserving machine learning |
| V0 Query 5 CN | 探索隐私保护机器学习中的各种密码学技术 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_45

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_45 |
| Original Question | All papers about controllability of video generation. |
| Question Chinese Translation | 所有关于视频生成可控性的论文。 |
| Baseline Query 1 | Survey papers on controllability of video generation |
| Baseline Query 1 CN | 关于视频生成可控性的综述论文 |
| Baseline Query 2 | Research papers on video generation controllability |
| Baseline Query 2 CN | 关于视频生成可控性的研究论文 |
| Baseline Query 3 | Latest research on controllability of video generation |
| Baseline Query 3 CN | 关于视频生成可控性的最新研究 |
| Baseline Query 4 | Studies on the control aspects of video production |
| Baseline Query 4 CN | 关于视频制作中控制方面的研究 |
| Baseline Query 5 | Papers on techniques for controlling video generation |
| Baseline Query 5 CN | 关于控制视频生成的技术的论文 |
| V0 Query 1 | Research on controllability of video generation |
| V0 Query 1 CN | 关于视频生成可控性的研究 |
| V0 Query 2 | Exploration of Large Language Models' role in controllable video generation |
| V0 Query 2 CN | 探索大语言模型在可控视频生成中的作用 |
| V0 Query 3 | Survey papers on controllability in video generation |
| V0 Query 3 CN | 关于视频生成可控性的综述论文 |
| V0 Query 4 | Papers on controllability aspects in video generation |
| V0 Query 4 CN | 关于视频生成中可控性方面的论文 |
| V0 Query 5 | Research on non-controllable factors in video editing |
| V0 Query 5 CN | 关于视频编辑中不可控因素的研究 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_46

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_46 |
| Original Question | Show me research on robot decision making and task planning, especially relevant datasets and benchmarks. |
| Question Chinese Translation | 请提供关于机器人决策和任务规划的研究，尤其是相关数据集和基准。 |
| Baseline Query 1 | Survey papers on robot decision making |
| Baseline Query 1 CN | 关于机器人决策的综述论文 |
| Baseline Query 2 | Research on task planning in robotics |
| Baseline Query 2 CN | 关于机器人任务规划的研究 |
| Baseline Query 3 | Benchmark datasets for robot decision making |
| Baseline Query 3 CN | 用于机器人决策的基准数据集 |
| Baseline Query 4 | Relevant datasets for robot decision making |
| Baseline Query 4 CN | 与机器人决策相关的数据集 |
| Baseline Query 5 | Benchmarks used in robot decision making research |
| Baseline Query 5 CN | 机器人决策研究中使用的基准 |
| V0 Query 1 | Studies on algorithms for robot decision making and task planning |
| V0 Query 1 CN | 关于机器人决策和任务规划算法的研究 |
| V0 Query 2 | Studies on task planning in robotics |
| V0 Query 2 CN | 关于机器人任务规划的研究 |
| V0 Query 3 | [FAILED GENERATION] |
| V0 Query 3 CN | [FAILED GENERATION]（生成失败，留空） |
| V0 Query 4 | Research on robot decision making and task planning datasets |
| V0 Query 4 CN | 关于机器人决策和任务规划数据集的研究 |
| V0 Query 5 | Studies on standardized benchmarks for evaluating robot decision making |
| V0 Query 5 CN | 关于用于评估机器人决策的标准化基准的研究 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_47

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_47 |
| Original Question | How can LLM agents be evaluated and benchmarked for financial tasks? Note that I am referring to agents. |
| Question Chinese Translation | 如何对金融任务中的 LLM 智能体进行评估和基准测试？请注意，我指的是智能体。 |
| Baseline Query 1 | Survey papers on evaluation of LLM agents in finance |
| Baseline Query 1 CN | 关于金融领域 LLM 智能体评估的综述论文 |
| Baseline Query 2 | Benchmarking methods for LLM agents in financial tasks |
| Baseline Query 2 CN | 金融任务中 LLM 智能体的基准测试方法 |
| Baseline Query 3 | Evaluation metrics for LLM agents in financial tasks |
| Baseline Query 3 CN | 金融任务中 LLM 智能体的评价指标 |
| Baseline Query 4 | Regulatory and industry-standard benchmarks for evaluating LLM agents in finance |
| Baseline Query 4 CN | 用于评估金融领域 LLM 智能体的监管和行业标准基准 |
| Baseline Query 5 | Comparative studies on LLM agent evaluation in financial domain |
| Baseline Query 5 CN | 关于金融领域 LLM 智能体评估的比较研究 |
| V0 Query 1 | Evaluation methodologies for LLM agents in finance |
| V0 Query 1 CN | 金融领域 LLM 智能体的评估方法 |
| V0 Query 2 | Benchmarking frameworks for LLM agents in financial tasks |
| V0 Query 2 CN | 金融任务中 LLM 智能体的基准测试框架 |
| V0 Query 3 | Performance evaluation of LLM agents on financial datasets |
| V0 Query 3 CN | 在金融数据集上评估 LLM 智能体的性能 |
| V0 Query 4 | Comparative analysis of LLM agents for financial applications |
| V0 Query 4 CN | 面向金融应用的 LLM 智能体比较分析 |
| V0 Query 5 | Application of LLM agents in financial domain |
| V0 Query 5 CN | LLM 智能体在金融领域中的应用 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_48

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_48 |
| Original Question | Papers that explore using large language models for mining factors in stock exchange analysis. |
| Question Chinese Translation | 探索使用大语言模型在证券交易分析中挖掘因子的论文。 |
| Baseline Query 1 | Application of large language models in stock market analysis |
| Baseline Query 1 CN | 大语言模型在股票市场分析中的应用 |
| Baseline Query 2 | Role of AI and language models in stock prediction |
| Baseline Query 2 CN | AI 和语言模型在股票预测中的作用 |
| Baseline Query 3 | Impact of large language models on stock exchange analysis |
| Baseline Query 3 CN | 大语言模型对证券交易分析的影响 |
| Baseline Query 4 | Use of GPT-3 in stock market trend analysis |
| Baseline Query 4 CN | GPT-3 在股票市场趋势分析中的使用 |
| Baseline Query 5 | Survey papers on large language models in stock exchange analysis |
| Baseline Query 5 CN | 关于大语言模型在证券交易分析中应用的综述论文 |
| V0 Query 1 | Exploration of large language models in stock exchange analysis |
| V0 Query 1 CN | 探索大语言模型在证券交易分析中的应用 |
| V0 Query 2 | Exploration of AI-driven factor mining in stock exchange |
| V0 Query 2 CN | 探索证券交易中由 AI 驱动的因子挖掘 |
| V0 Query 3 | Research on the use of artificial intelligence, particularly large language models, for predicting stock prices and identifying influential factors in stock exchange analysis. |
| V0 Query 3 CN | 关于使用人工智能，尤其是大语言模型，在证券交易分析中预测股价并识别影响因素的研究。 |
| V0 Query 4 | Quantitative analysis of factors influencing stock prices using language models |
| V0 Query 4 CN | 使用语言模型对影响股价的因素进行定量分析 |
| V0 Query 5 | Limitations of using AI for stock exchange analysis |
| V0 Query 5 CN | 使用 AI 进行证券交易分析的局限 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---

# RealScholarQuery_49

| 字段 | 内容 |
|---|---|
| ID | RealScholarQuery_49 |
| Original Question | Can you help me find research papers that explore the use of large vision-language models as agents to automatically play PC games? |
| Question Chinese Translation | 能否帮我找到探索使用大型视觉—语言模型作为智能体自动玩 PC 游戏的研究论文？ |
| Baseline Query 1 | Use of AI in automated PC game playing |
| Baseline Query 1 CN | AI 在自动玩 PC 游戏中的使用 |
| Baseline Query 2 | Exploration of large vision-language models as gaming agents |
| Baseline Query 2 CN | 探索大型视觉—语言模型作为游戏智能体 |
| Baseline Query 3 | Research on Large Multimodal Models (LMMs) and their application in automatic PC game play |
| Baseline Query 3 CN | 关于大型多模态模型（LMMs）及其在自动玩 PC 游戏中应用的研究 |
| Baseline Query 4 | Studies on PC game automation using large vision-language models |
| Baseline Query 4 CN | 关于使用大型视觉—语言模型实现 PC 游戏自动化的研究 |
| Baseline Query 5 | Survey papers on vision-language models as game agents |
| Baseline Query 5 CN | 关于视觉—语言模型作为游戏智能体的综述论文 |
| V0 Query 1 | Research on the use of Multimodal Large Language Models in automated PC game play |
| V0 Query 1 CN | 关于使用多模态大语言模型自动玩 PC 游戏的研究 |
| V0 Query 2 | Studies on large vision-language models as agents in PC gaming |
| V0 Query 2 CN | 关于大型视觉—语言模型作为 PC 游戏智能体的研究 |
| V0 Query 3 | Use of AI in the gaming sector: recent studies |
| V0 Query 3 CN | AI 在游戏领域中的使用：近期研究 |
| V0 Query 4 | Investigation on the effectiveness of large vision-language models in PC game automation |
| V0 Query 4 CN | 研究大型视觉—语言模型在 PC 游戏自动化中的有效性 |
| V0 Query 5 | Papers on automatic game play using large vision-language models |
| V0 Query 5 CN | 关于使用大型视觉—语言模型自动玩游戏的论文 |


## Manual Review

### 1. Core Constraint Preservation

以下项目分别检查 Baseline 和 V0：

- 是否保留核心方法？
- 是否保留模型？
- 是否保留任务？
- 是否保留数据集/benchmark？
- 是否保留特殊限制？

Baseline：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

Baseline 备注：

________________________________________________________________

V0：

- [ ] 完整
- [ ] 部分遗漏
- [ ] 严重遗漏

V0 备注：

________________________________________________________________

### 2. Hallucinated Constraint

V0 是否引入原问题不存在的信息，例如新模型、新算法、新数据集、新评价指标或新任务限定？

- [ ] 无
- [ ] 有

类型：

________________________________________________________________

说明：

________________________________________________________________

### 3. Query Diversity

判断五条 query 是否提供不同检索角度：

- [ ] 高
- [ ] 中
- [ ] 低

说明（可记录与 baseline 的对比）：

________________________________________________________________

### 4. Search Usability

判断 query 是否适合作为搜索 query：

- [ ] 好
- [ ] 一般
- [ ] 差

问题：

- [ ] 直接复制用户问题
- [ ] 过长
- [ ] 不是搜索关键词形式
- [ ] 包含控制词(stopSearch等)
- [ ] 其他

问题说明：

________________________________________________________________

### 5. Overall Comparison

相比 baseline：

- [ ] V0明显更好
- [ ] V0略好
- [ ] 基本相同
- [ ] baseline更好
- [ ] 无法判断

原因：

________________________________________________________________

________________________________________________________________

---


# Manual Audit Summary

## Overall Result

Total samples: 50

V0 better:

V0 slightly better:

Same:

Baseline better:

Unclear:

## Error Statistics

### 1. Hallucinated constraints

数量：

案例：

________________________________________________________________

### 2. Query duplication

数量：

案例：

________________________________________________________________

### 3. Missing constraints

数量：

案例：

________________________________________________________________

### 4. Search-unfriendly query

数量：

案例：

________________________________________________________________

### 5. Wrong terminology expansion

数量：

案例：

________________________________________________________________
