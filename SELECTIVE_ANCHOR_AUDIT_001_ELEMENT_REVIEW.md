# Selective Anchor 逐元素复核

此表为 assistant/analyst 文本复核，不是外部人工标注金标准。列出的元素频次来自 reviewed_retained_native_indices；严格词面频次另列。元素定义、重叠计数及边界说明见主报告。

## Q0

Original question:

Give me papers which show that using a smaller dataset in large language model pre-training can result in better models than using bigger datasets.

Native queries:

1. Papers on the effectiveness of smaller datasets in language model pre-training
2. Advantages of using smaller datasets in large language model pre-training
3. Benefits of limited dataset in pre-training of language models
4. Survey papers on large language model pre-training using smaller dataset
5. Effects of dataset size on language model pre-training effectiveness

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q0_E1: large language model | entity_method_model | 否 | 2/5; [2, 4] | [2, 4] | Unqualified language model is not credited as explicitly large. |
| Q0_E2: pre-training | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q0_E3: smaller dataset | domain_technical_phrase | 是 | 3/5; [1, 2, 4] | [4] | limited dataset alone does not retain the comparative smaller. |
| Q0_E4: using a smaller dataset in large language model pre-training can result in better models than using bigger datasets | numeric_comparison_negation_condition | 是 | 0/5; [] | [] | Benefits/effectiveness do not preserve the explicit smaller-versus-bigger superiority claim. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2963 | 0.4286 |
| 2 | 0.3600 | 0.5000 |
| 3 | 0.2308 | 0.3333 |
| 4 | 0.3600 | 0.5000 |
| 5 | 0.1786 | 0.3125 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q1

Original question:

Give me papers that share some insights about how large language models gain in-context learning capability in the process of pre-training.


Native queries:

1. Survey papers on in-context learning in pre-trained language models
2. In-context learning in pre-training of large language models
3. Pre-training methods for in-context learning in language models
4. Insights into the process of pre-training for in-context learning in language models
5. Role of pre-training in the development of in-context learning in language models

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q1_E1: large language models | entity_method_model | 否 | 1/5; [2] | [2] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q1_E2: in-context learning | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q1_E3: pre-training | entity_method_model | 是 | 4/5; [2, 3, 4, 5] | [2, 3, 4, 5] | pre-trained in q1 denotes a model state; it does not specify studying the pre-training process. |
| Q1_E4: gain in-context learning capability in the process of pre-training | numeric_comparison_negation_condition | 是 | 1/5; [5] | [] | q5 development of in-context learning during pre-training retains acquisition; association alone is insufficient. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2800 | 0.3571 |
| 2 | 0.4091 | 0.5833 |
| 3 | 0.2917 | 0.4615 |
| 4 | 0.4583 | 0.6154 |
| 5 | 0.3750 | 0.4286 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q2

Original question:

List all papers that use autoregressive transformer to generate videos.

Native queries:

1. Autoregressive transformer models in video generation research papers
2. Research on using autoregressive transformers for video editing and composition
3. Papers on video generation using autoregressive transformer
4. Studies on autoregressive transformer in video creation
5. Use of autoregressive transformer in video generation papers

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q2_E1: autoregressive transformer | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q2_E2: generate videos | domain_technical_phrase | 是 | 4/5; [1, 3, 4, 5] | [] | video generation/creation retained; video editing/composition in q2 is a different task. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2000 | 0.2857 |
| 2 | 0.0526 | 0.1250 |
| 3 | 0.2143 | 0.3333 |
| 4 | 0.1333 | 0.2857 |
| 5 | 0.2857 | 0.3333 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q3

Original question:

I am looking for research papers on the construction of multimodal foundation models that support both visual and audio inputs. These models should be pre-trained on large-scale datasets, including visual, audio, and audio-visual data. Please exclude survey papers.

Native queries:

1. Pre-training of multimodal foundation models on large-scale datasets
2. Research on audio-visual pretraining in multimodal foundation models
3. Multimodal foundation models for visual and audio inputs
4. Foundation models supporting visual and audio inputs
5. Research on Large Multimodal Models (LMMs) for integrating visual and textual data

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q3_E1: multimodal foundation models | entity_method_model | 是 | 3/5; [1, 2, 3] | [1, 2, 3] | q4 drops multimodal explicitly; q5 Large Multimodal Models drops foundation status. |
| Q3_E2: both visual and audio inputs | numeric_comparison_negation_condition | 是 | 2/5; [3, 4] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q3_E3: pre-trained on large-scale datasets | numeric_comparison_negation_condition | 是 | 1/5; [1] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q3_E4: including visual, audio, and audio-visual data | numeric_comparison_negation_condition | 是 | 0/5; [] | [] | q2 has audio-visual pretraining but not all three specified data types. |
| Q3_E5: exclude survey papers | numeric_comparison_negation_condition | 是 | 0/5; [] | [] | Not generating the word survey does not explicitly retain exclusion. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2647 | 0.3500 |
| 2 | 0.2000 | 0.2500 |
| 3 | 0.2424 | 0.3158 |
| 4 | 0.1765 | 0.2500 |
| 5 | 0.2500 | 0.2273 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q4

Original question:

Provide me with all papers that discuss reinforcement learning training for Large Language Model agent tasks.

Native queries:

1. Survey papers on reinforcement learning training for large language models
2. Research on task-agnostic rewards in reinforcement learning training for large language models
3. Reinforcement learning approaches for optimizing Large Language Model agents
4. Case studies of Large Language Model agents trained using reinforcement learning
5. Experiences in training Large Language Model agents using reinforcement learning

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q4_E1: reinforcement learning | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q4_E2: Large Language Model | entity_method_model | 否 | 5/5; [1, 2, 3, 4, 5] | [3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q4_E3: agent tasks | domain_technical_phrase | 是 | 3/5; [3, 4, 5] | [] | Explicit LLM agents preserve the task object; generic LLM training does not. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.3684 | 0.4545 |
| 2 | 0.2609 | 0.3846 |
| 3 | 0.3158 | 0.4167 |
| 4 | 0.2273 | 0.3846 |
| 5 | 0.3000 | 0.5455 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q5

Original question:

Papers that apply RLHF to address the hallucination problem in image and video description.

Native queries:

1. Survey papers on RLHF for image description
2. Application of RLHF in video description
3. Use of RLHF in addressing hallucination in video content
4. Impact of RLHF on hallucination issue in image description
5. Role of RLHF in reducing hallucination in multimodal generation

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q5_E1: RLHF | benchmark_dataset_acronym | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q5_E2: hallucination problem | domain_technical_phrase | 是 | 3/5; [3, 4, 5] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q5_E3: image | domain_technical_phrase | 否 | 2/5; [1, 4] | [1, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q5_E4: video | domain_technical_phrase | 否 | 2/5; [2, 3] | [2, 3] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q5_E5: description | domain_technical_phrase | 是 | 3/5; [1, 2, 4] | [1, 2, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q5_E6: apply RLHF to address the hallucination problem in image and video description | numeric_comparison_negation_condition | 是 | 0/5; [] | [] | No single query retains RLHF + hallucination + description for BOTH modalities; the component elements are distributed. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2353 | 0.3333 |
| 2 | 0.2500 | 0.3333 |
| 3 | 0.2222 | 0.3000 |
| 4 | 0.2778 | 0.4000 |
| 5 | 0.1579 | 0.1667 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q6

Original question:

Papers that propose methods based on large language models and evaluate their performance through experiments on the HotPotQA dataset.

Native queries:

1. Large language model based methods for HotPotQA dataset
2. Research on evaluation methods for Large Language Models on HotPotQA dataset
3. Survey papers on methods using large language models for HotPotQA
4. Experiments on the HotPotQA dataset for language models
5. Proposed methods for HotPotQA using large language models

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q6_E1: large language models | entity_method_model | 否 | 4/5; [1, 2, 3, 5] | [2, 3, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q6_E2: HotPotQA | benchmark_dataset_acronym | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q6_E3: evaluate their performance through experiments | numeric_comparison_negation_condition | 是 | 1/5; [4] | [] | q2 evaluation methods does not explicitly require empirical experiments; q4 explicitly experiments. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.3000 | 0.4615 |
| 2 | 0.3333 | 0.4615 |
| 3 | 0.3333 | 0.3846 |
| 4 | 0.3684 | 0.4167 |
| 5 | 0.2381 | 0.3846 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q7

Original question:

Show me research on the long video description. Here, long videos are defined as those with a duration of at least several minutes.

Native queries:

1. Survey papers on long video description techniques
2. Research on automatic video summarization for long videos
3. Long video description research papers
4. Studies on multi-modal language models for long video understanding
5. Research on long-duration video description

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q7_E1: long video description | domain_technical_phrase | 是 | 3/5; [1, 3, 5] | [1, 3] | Summarization/understanding do not fully preserve description. |
| Q7_E2: duration of at least several minutes | numeric_comparison_negation_condition | 是 | 0/5; [] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.1600 | 0.2500 |
| 2 | 0.2000 | 0.2500 |
| 3 | 0.1739 | 0.3000 |
| 4 | 0.1034 | 0.1250 |
| 5 | 0.2727 | 0.4000 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q8

Original question:

Do you know some papers about using reward shaping methods to train large language model agent.

Native queries:

1. Reward shaping techniques in large language model training
2. Application of reward shaping in language model agent training
3. Effectiveness of reward shaping methods in training large language models
4. Research on using small extrinsic rewards for aligning large language models with user intent
5. Exploring the use of self-rewarding mechanisms in training large language models

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q8_E1: reward shaping | entity_method_model | 是 | 3/5; [1, 2, 3] | [1, 2, 3] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q8_E2: large language model | entity_method_model | 否 | 4/5; [1, 3, 4, 5] | [1] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q8_E3: agent | domain_technical_phrase | 是 | 1/5; [2] | [2] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q8_E4: train | domain_technical_phrase | 否 | 4/5; [1, 2, 3, 5] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2632 | 0.5000 |
| 2 | 0.2500 | 0.5000 |
| 3 | 0.2381 | 0.4545 |
| 4 | 0.1111 | 0.1333 |
| 5 | 0.0769 | 0.1429 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q9

Original question:

Give me papers about how to rank search results by the use of LLM.

Native queries:

1. Use of LLM in ranking search results
2. Influence of LLM on search result rankings
3. Survey papers on ranking search results with Language Model
4. Application of LLM in search result ranking
5. Ranking mechanisms in Large Language Models

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q9_E1: LLM | benchmark_dataset_acronym | 否 | 4/5; [1, 2, 4, 5] | [1, 2, 4] | q5 uses the explicit full form Large Language Models; q3 Language Model omits large. |
| Q9_E2: rank search results | domain_technical_phrase | 是 | 4/5; [1, 2, 3, 4] | [] | q5 ranking mechanisms omits search results. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.3125 | 0.5000 |
| 2 | 0.1667 | 0.1667 |
| 3 | 0.1500 | 0.1429 |
| 4 | 0.1667 | 0.1667 |
| 5 | 0.0000 | 0.0000 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q10

Original question:

Is there any work that analyzes the scaling law of the multi-module models, such as video-text, image-text models?

Native queries:

1. Survey papers on scaling law of multi-module models
2. Analysis of scaling law in video-text models
3. Research on scaling law in image-text models
4. Scaling behavior of multi-modal transformer models in video-text tasks
5. Empirical studies on the scaling laws of text-to-video generation models

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q10_E1: scaling law | domain_technical_phrase | 是 | 4/5; [1, 2, 3, 5] | [1, 2, 3] | q4 scaling behavior is not explicitly a scaling law. |
| Q10_E2: multi-module models | entity_method_model | 是 | 1/5; [1] | [1] | Keep source multi-module; do not silently correct it to multimodal. |
| Q10_E3: video-text | domain_technical_phrase | 是 | 2/5; [2, 4] | [2, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q10_E4: image-text | domain_technical_phrase | 是 | 1/5; [3] | [3] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2857 | 0.5000 |
| 2 | 0.3000 | 0.5000 |
| 3 | 0.2381 | 0.5556 |
| 4 | 0.2609 | 0.3846 |
| 5 | 0.2500 | 0.3077 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q11

Original question:

Give me all visual-LLM models that are MoE architecture

Native queries:

1. MoE architecture models in visual-LLM
2. Survey papers on visual-LLM models with MoE architecture
3. Multi-Modal Large Language Models with MoE architecture
4. Research on MoE architecture in visual-LLMs
5. Objectives of visual-LLM models using MoE architecture

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q11_E1: visual-LLM | entity_method_model | 是 | 4/5; [1, 2, 4, 5] | [1, 2, 5] | q3 multimodal is broader than the explicitly visual modality. |
| Q11_E2: MoE | benchmark_dataset_acronym | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.4545 | 1.0000 |
| 2 | 0.3571 | 0.8333 |
| 3 | 0.2000 | 0.3333 |
| 4 | 0.2143 | 0.5000 |
| 5 | 0.3846 | 0.8333 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q12

Original question:

What papers discuss the use of transformer architecture in 3d video generation

Native queries:

1. Use of transformer model in 3D video production
2. Research on 3D video generation using transformer architecture
3. Papers on transformer-based methods in 3D video generation
4. Transformer architecture application in 3D video creation
5. Exploration of transformer architecture for 3D video synthesis

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q12_E1: transformer architecture | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [2, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q12_E2: 3d | numeric_comparison_negation_condition | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q12_E3: video generation | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [2, 3] | production/creation/synthesis accepted as task paraphrases here. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.4286 | 0.3750 |
| 2 | 0.3333 | 0.8333 |
| 3 | 0.4000 | 0.5000 |
| 4 | 0.3571 | 0.5000 |
| 5 | 0.3333 | 0.5000 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q13

Original question:

Provide papers demonstrating that the self-correction of LLMs does not enhance their performance.

Native queries:

1. Studies on the limitations of self-correction in language models
2. Impact of self-correction on language model performance
3. Survey papers on self-correction not enhancing LLM performance
4. Academic papers on the ineffectiveness of self-correction in LLMs
5. Research on self-correction mechanisms in LLMs and their impact on performance

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q13_E1: self-correction | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q13_E2: LLMs | benchmark_dataset_acronym | 否 | 3/5; [3, 4, 5] | [4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q13_E3: does not enhance their performance | numeric_comparison_negation_condition | 是 | 2/5; [3, 4] | [] | q3 explicitly not enhancing; q4 ineffectiveness is credited as equivalent. q1 limitations and q2/q5 impact are weaker or neutral. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2000 | 0.1818 |
| 2 | 0.2222 | 0.3000 |
| 3 | 0.2778 | 0.4000 |
| 4 | 0.3333 | 0.3333 |
| 5 | 0.2500 | 0.4444 |

既有收益标签：positive；anchor 新增 GT=1。

## Q14

Original question:

Find papers that use LLMs or LLM-based agents to automatically write surveys or summaries for multiple scholarly documents.

Native queries:

1. Use of LLMs in automatic survey writing
2. Survey papers on the use of LLMs in scholarly document summarization
3. Papers on LLM-based agents for writing summaries of scholarly articles
4. Research on using language models for automatic synthesis of literature reviews
5. Articles on the application of LLM-based agents in multi-document summary

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q14_E1: LLMs | benchmark_dataset_acronym | 否 | 4/5; [1, 2, 3, 5] | [1, 2] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q14_E2: LLM-based agents | entity_method_model | 是 | 2/5; [3, 5] | [3, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q14_E3: automatically write | numeric_comparison_negation_condition | 是 | 2/5; [1, 4] | [] | Automatic survey writing/synthesis; q5 multi-document summary is not explicitly automatic. |
| Q14_E4: surveys or summaries | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q14_E5: multiple scholarly documents | numeric_comparison_negation_condition | 是 | 0/5; [] | [] | q5 multi-document omits scholarly; q2/q3 scholarly documents do not explicitly preserve multi-document aggregation. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.0870 | 0.0714 |
| 2 | 0.1600 | 0.1429 |
| 3 | 0.3182 | 0.3846 |
| 4 | 0.0357 | 0.0000 |
| 5 | 0.1111 | 0.1875 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q15

Original question:

Provide papers claiming that reinforcement learning can negatively impact the performance of supervised fine-tuned LLMs.

Native queries:

1. Survey papers on negative impacts of reinforcement learning on supervised fine-tuned LLMs
2. Implications of Reinforcement Learning on Supervised Fine-Tuning in Language Models
3. Effects of reinforcement learning on fine-tuned language models
4. Downsides of reinforcement learning in supervised fine-tuned LLMs
5. Impact of reinforcement learning on performance of fine-tuned LLMs

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q15_E1: reinforcement learning | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q15_E2: supervised fine-tuned LLMs | entity_method_model | 是 | 2/5; [1, 4] | [1, 4] | q2 describes supervised fine-tuning but not an explicitly large model; q3/q5 drop supervised. |
| Q15_E3: negatively impact the performance | numeric_comparison_negation_condition | 是 | 2/5; [1, 4] | [] | Negative impacts/downsides retained; effects/implications alone do not preserve direction. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.4000 | 0.4615 |
| 2 | 0.2273 | 0.2857 |
| 3 | 0.2500 | 0.3077 |
| 4 | 0.3889 | 0.5455 |
| 5 | 0.4706 | 0.7000 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q16

Original question:

Find papers on trigger-free document-level event extraction methods that do not use human-annotated triggers.

Native queries:

1. Document-level event extraction without triggers research papers
2. Papers on event extraction methods without triggers
3. Survey papers on trigger-free document-level event extraction
4. Research articles on document-level event extraction without triggers
5. Studies on event extraction techniques without human-annotated triggers

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q16_E1: trigger-free | numeric_comparison_negation_condition | 是 | 4/5; [1, 2, 3, 4] | [3] | without triggers accepted; q5 only excludes human-annotated triggers, not all triggers. |
| Q16_E2: document-level | numeric_comparison_negation_condition | 是 | 3/5; [1, 3, 4] | [1, 3, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q16_E3: event extraction | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q16_E4: do not use human-annotated triggers | numeric_comparison_negation_condition | 是 | 5/5; [1, 2, 3, 4, 5] | [] | Trigger-free/without any triggers entails excluding human-annotated triggers; a stronger restriction is credited and noted. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.3158 | 0.4167 |
| 2 | 0.3333 | 0.3333 |
| 3 | 0.4444 | 0.5000 |
| 4 | 0.3000 | 0.3846 |
| 5 | 0.3000 | 0.3571 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q17

Original question:

Provide papers explaining why the in-context learning performance of LLMs cannot surpass that of supervised fine-tuned small language models in information extraction tasks, such as NER, RE, and EE.

Native queries:

1. Performance comparison of in-context learning and supervised fine-tuning in language models for information extraction
2. Limitations of in-context learning in language models for information extraction
3. In-context learning vs supervised fine-tuning in LLMs for information extraction
4. Why supervised fine-tuned small language models outperform in-context learning in NER
5. Impact of parameter size on the performance of in-context learning versus supervised fine-tuning in large language models

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q17_E1: in-context learning | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q17_E2: LLMs | benchmark_dataset_acronym | 否 | 2/5; [3, 5] | [3] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q17_E3: supervised fine-tuned small language models | entity_method_model | 是 | 1/5; [4] | [4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q17_E4: information extraction | domain_technical_phrase | 是 | 3/5; [1, 2, 3] | [1, 2, 3] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q17_E5: NER | benchmark_dataset_acronym | 是 | 1/5; [4] | [4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q17_E6: RE | benchmark_dataset_acronym | 是 | 0/5; [] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q17_E7: EE | benchmark_dataset_acronym | 是 | 0/5; [] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q17_E8: cannot surpass | numeric_comparison_negation_condition | 是 | 1/5; [4] | [] | q4 small supervised models outperform in-context learning preserves the claimed direction; comparison/limitations alone does not. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.3750 | 0.4286 |
| 2 | 0.2581 | 0.3000 |
| 3 | 0.2500 | 0.3333 |
| 4 | 0.3667 | 0.4500 |
| 5 | 0.2778 | 0.2800 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q18

Original question:

Can LLMs detect LLM-generated text in a zero-shot manner? Do they perform better than supervised fine-tuned small classification models? Provide related papers.

Native queries:

1. Performance comparison of LLMs and supervised fine-tuned models in zero-shot detection
2. Zero-shot detection of LLM-generated content
3. Supervised fine-tuned small classification models vs LLMs for detecting LLM-generated text
4. Evaluation of LLM-generated text in zero-shot scenarios

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q18_E1: LLMs | benchmark_dataset_acronym | 否 | 4/4; [1, 2, 3, 4] | [1, 3] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q18_E2: detect LLM-generated text | domain_technical_phrase | 是 | 2/4; [2, 3] | [] | q4 evaluation in zero-shot scenarios is not explicitly detection; q1 detection omits generated text. |
| Q18_E3: zero-shot | numeric_comparison_negation_condition | 是 | 3/4; [1, 2, 4] | [1, 2, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q18_E4: supervised fine-tuned small classification models | entity_method_model | 是 | 1/4; [3] | [3] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q18_E5: perform better than supervised fine-tuned small classification models | numeric_comparison_negation_condition | 是 | 0/4; [] | [] | q1 comparison and q3 vs do not preserve the explicit better-than relation. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2667 | 0.3500 |
| 2 | 0.1429 | 0.2105 |
| 3 | 0.3571 | 0.5263 |
| 4 | 0.2143 | 0.2632 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q19

Original question:

Provide papers on methods that protect the generation quality of LLMs under vocabulary watermarking settings.

Native queries:

1. Survey papers on protecting generation quality of LLMs under vocabulary watermarking
2. Research on methods to maintain generation quality in LLMs during vocabulary watermarking
3. Studies on the use of word embeddings in LLMs for detecting and mitigating vocabulary-based watermarking attacks
4. Impact of vocabulary watermarking on LLMs generation quality
5. Techniques to mitigate vocabulary watermarking effects on LLM generation

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q19_E1: LLMs | benchmark_dataset_acronym | 否 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q19_E2: generation quality | domain_technical_phrase | 是 | 3/5; [1, 2, 4] | [1, 2, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q19_E3: vocabulary watermarking | entity_method_model | 是 | 4/5; [1, 2, 4, 5] | [1, 2, 4, 5] | q3 changes the subject to detecting/mitigating watermarking attacks. |
| Q19_E4: protect the generation quality | numeric_comparison_negation_condition | 是 | 2/5; [1, 2] | [] | q5 mitigate effects on generation does not explicitly retain quality; q4 impact is neutral. |
| Q19_E5: under vocabulary watermarking settings | numeric_comparison_negation_condition | 是 | 4/5; [1, 2, 4, 5] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.5294 | 0.5455 |
| 2 | 0.3500 | 0.5455 |
| 3 | 0.2308 | 0.1875 |
| 4 | 0.4375 | 0.5000 |
| 5 | 0.2000 | 0.2308 |

既有收益标签：positive；anchor 新增 GT=1。

## Q20

Original question:

Find papers supporting the claim that knowledgeable LLMs have sufficient inductive capacity to analyze the relationships between multiple papers and systematically write a survey on them.

Native queries:

1. Survey papers on inductive capacity of language models
2. Research on the impact of large language models on academic literature review
3. Scholarly articles on the analysis of multiple papers by LLMs
4. Papers on systematic review writing by AI models
5. LLMs and their ability to analyze multiple research papers

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q20_E1: knowledgeable LLMs | entity_method_model | 是 | 0/5; [] | [] | LLMs without knowledgeable does not preserve the qualifier. |
| Q20_E2: sufficient inductive capacity | numeric_comparison_negation_condition | 是 | 0/5; [] | [] | q1 inductive capacity drops sufficient. |
| Q20_E3: relationships between multiple papers | domain_technical_phrase | 是 | 0/5; [] | [] | q3/q5 analyze multiple papers but do not state inter-paper relationships. |
| Q20_E4: systematically write a survey | domain_technical_phrase | 是 | 1/5; [4] | [] | systematic review writing accepted as task equivalent. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.1852 | 0.1875 |
| 2 | 0.0606 | 0.0000 |
| 3 | 0.1724 | 0.1176 |
| 4 | 0.0667 | 0.0000 |
| 5 | 0.2222 | 0.2000 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q21

Original question:

Search for papers related to large language models that demonstrate how the same prompt with different responses can improve the performance of the SFT model.

Native queries:

1. Papers on enhancing SFT model performance with different response prompts
2. Research on the impact of diverse responses on the performance of SFT models
3. Survey papers on the use of varied responses to a single prompt in large language models for SFT
4. Studies on how different responses to the same prompt affect SFT model
5. Prompt engineering methods for improving SFT model performance in large language models

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q21_E1: large language models | entity_method_model | 否 | 2/5; [3, 5] | [3, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q21_E2: same prompt with different responses | numeric_comparison_negation_condition | 是 | 2/5; [3, 4] | [] | q1 different response prompts can suggest different prompts; q2 drops the same-prompt restriction. |
| Q21_E3: SFT | benchmark_dataset_acronym | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q21_E4: improve the performance | numeric_comparison_negation_condition | 是 | 2/5; [1, 5] | [] | Enhancing/improving retained; impact/affect without direction is insufficient. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2222 | 0.2667 |
| 2 | 0.2222 | 0.2857 |
| 3 | 0.3667 | 0.4000 |
| 4 | 0.3462 | 0.4286 |
| 5 | 0.2963 | 0.4667 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q22

Original question:

Papers on solving common sense problems in machine translation.

Native queries:

1. Machine translation challenges in commonsense reasoning
2. Algorithms used in solving common sense problems in machine translation
3. Improving common sense in machine translation
4. Research articles on machine translation and common sense issues
5. Survey papers on common sense problems in machine translation

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q22_E1: common sense problems | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [2, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q22_E2: machine translation | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2500 | 0.2222 |
| 2 | 0.6364 | 0.8571 |
| 3 | 0.5000 | 0.5714 |
| 4 | 0.3846 | 0.5000 |
| 5 | 0.8000 | 0.7143 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q23

Original question:

Show me papers utilizing reinforcement learning to optimize diffusion models for video generation.

Native queries:

1. Papers on diffusion models for video generation optimized with reinforcement learning
2. Research on reinforcement learning techniques in video diffusion models optimization
3. Survey papers on reinforcement learning optimization in video generation
4. Studies on video synthesis using reinforcement learning in diffusion models
5. Use of reinforcement learning in optimizing diffusion models for video production

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q23_E1: reinforcement learning | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q23_E2: diffusion models | entity_method_model | 是 | 4/5; [1, 2, 4, 5] | [1, 2, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q23_E3: video generation | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 3] | Video diffusion models in optimization context credited to generation in q2. |
| Q23_E4: optimize | numeric_comparison_negation_condition | 是 | 4/5; [1, 2, 3, 5] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.5000 | 0.6667 |
| 2 | 0.2778 | 0.5000 |
| 3 | 0.2941 | 0.4000 |
| 4 | 0.2778 | 0.5000 |
| 5 | 0.3333 | 0.5000 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q24

Original question:

Show me all research papers on machine translation agents.

Native queries:

1. Machine translation agents research papers
2. Papers on machine translation using agents
3. Survey papers on machine translation
4. Research on machine learning in machine translation
5. Latest advancements in machine translation agents

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q24_E1: machine translation | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q24_E2: agents | entity_method_model | 是 | 3/5; [1, 2, 5] | [1, 2, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.5556 | 1.0000 |
| 2 | 0.5000 | 1.0000 |
| 3 | 0.4000 | 0.5000 |
| 4 | 0.3636 | 0.5000 |
| 5 | 0.2500 | 0.6000 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q25

Original question:

Video aesthetics score, using multimodal large models.

Native queries:

1. Multimodal large models for video analysis
2. Use of multimodal large models in video scoring
3. Survey papers on video aesthetics score using multimodal models
4. Multimodal machine learning for video aesthetics
5. Large language models in video quality assessment

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q25_E1: Video | domain_technical_phrase | 否 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q25_E2: aesthetics score | domain_technical_phrase | 是 | 1/5; [3] | [3] | q2 scoring drops aesthetics; q4 aesthetics drops score; q5 quality is broader. |
| Q25_E3: multimodal large models | entity_method_model | 是 | 2/5; [1, 2] | [1, 2] | q3/q4 omit large; q5 omits multimodal. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.4444 | 0.5714 |
| 2 | 0.3636 | 0.5714 |
| 3 | 0.6000 | 0.7143 |
| 4 | 0.3000 | 0.3750 |
| 5 | 0.2727 | 0.3333 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q26

Original question:

Scaling Laws for Fine-Grained Mixture of Experts.

Native queries:

1. Survey papers on Scaling Laws for Fine-Grained Mixture of Experts
2. Scaling laws in fine-grained mixture of experts model
3. Influence of mixture of experts on scaling laws
4. Examination of the impact of parameter increase on performance scaling in Fine-Grained Mixture of Experts
5. Optimization of mixture of experts model using scaling laws

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q26_E1: Scaling Laws | domain_technical_phrase | 是 | 4/5; [1, 2, 3, 5] | [1, 2, 3, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q26_E2: Fine-Grained | numeric_comparison_negation_condition | 是 | 3/5; [1, 2, 4] | [1, 2, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q26_E3: Mixture of Experts | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.7273 | 0.8571 |
| 2 | 0.7000 | 0.8571 |
| 3 | 0.5000 | 0.5714 |
| 4 | 0.3750 | 0.4545 |
| 5 | 0.4545 | 0.5000 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q27

Original question:

Show me research on rejection sampling finetuning.

Native queries:

1. Survey papers on rejection sampling fine-tuning
2. Research articles on fine-tuning techniques in rejection sampling
3. Academic studies on rejection sampling optimization
4. Rejection sampling fine-tuning in machine learning
5. Studies on improving rejection sampling efficiency in fine-tuning

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q27_E1: rejection sampling | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q27_E2: finetuning | entity_method_model | 是 | 4/5; [1, 2, 4, 5] | [] | fine-tuning spelling variant accepted. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2727 | 0.3333 |
| 2 | 0.3333 | 0.2857 |
| 3 | 0.3000 | 0.3333 |
| 4 | 0.1667 | 0.2857 |
| 5 | 0.2308 | 0.2500 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q28

Original question:

Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests.

Native queries:

1. Survey papers on code evaluation datasets
2. Middle difficulty level code evaluation datasets
3. Code evaluation datasets with mid-level hardness
4. Comparison studies on difficulty levels of different code evaluation datasets

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q28_E1: code evaluation datasets | domain_technical_phrase | 是 | 4/4; [1, 2, 3, 4] | [1, 2, 3, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q28_E2: mid-level hardness | numeric_comparison_negation_condition | 是 | 2/4; [2, 3] | [3] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q28_E3: HumanEval | benchmark_dataset_acronym | 是 | 0/4; [] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q28_E4: MBPP | benchmark_dataset_acronym | 是 | 0/4; [] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q28_E5: code_contests | benchmark_dataset_acronym | 是 | 0/4; [] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q28_E6: harder than HumanEval and MBPP | numeric_comparison_negation_condition | 是 | 0/4; [] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q28_E7: easier than code_contests | numeric_comparison_negation_condition | 是 | 0/4; [] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.1304 | 0.2308 |
| 2 | 0.1818 | 0.2857 |
| 3 | 0.3500 | 0.5000 |
| 4 | 0.1111 | 0.1765 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q29

Original question:

Research on teaching llms to do math prove and solve IMO level math problems.

Native queries:

1. Survey papers on teaching language models mathematics
2. Research on solving IMO level math problems using LLMs
3. Methods to teach language models mathematical proof
4. Advanced techniques to solve IMO level math problems with LLMs
5. Machine learning approaches for solving IMO problems

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q29_E1: llms | benchmark_dataset_acronym | 否 | 2/5; [2, 4] | [2, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q29_E2: math prove | domain_technical_phrase | 是 | 1/5; [3] | [] | Source wording preserved; mathematical proof is the reviewed equivalent. |
| Q29_E3: IMO | benchmark_dataset_acronym | 是 | 3/5; [2, 4, 5] | [2, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q29_E4: IMO level math problems | numeric_comparison_negation_condition | 是 | 3/5; [2, 4, 5] | [2, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q29_E5: teaching | domain_technical_phrase | 否 | 2/5; [1, 3] | [1] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.1111 | 0.0833 |
| 2 | 0.4667 | 0.5556 |
| 3 | 0.0526 | 0.0000 |
| 4 | 0.4375 | 0.6000 |
| 5 | 0.1111 | 0.1667 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q30

Original question:

I would like to find some research papers about test time training topic, in LLM research area.

Native queries:

1. Survey papers on test time training in language models
2. Test-time training techniques in large language models
3. Advancements in test time training for language models
4. LLM research on test time training
5. Online learning techniques for test-time training in large language models

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q30_E1: test time training | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q30_E2: LLM | benchmark_dataset_acronym | 否 | 3/5; [2, 4, 5] | [4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2500 | 0.3000 |
| 2 | 0.2000 | 0.2727 |
| 3 | 0.2000 | 0.3000 |
| 4 | 0.2941 | 0.5714 |
| 5 | 0.1739 | 0.2308 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q31

Original question:

DPO training for large-scale vision-language models.

Native queries:

1. Survey papers on DPO training for vision-language models
2. Effects of DPO training on large-scale vision-language models
3. Comparative studies on DPO and other methods for training large-scale vision-language models
4. Application of DPO in large-scale vision-language model training
5. Challenges in DPO training for large-scale vision-language models

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q31_E1: DPO | benchmark_dataset_acronym | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q31_E2: large-scale | numeric_comparison_negation_condition | 是 | 4/5; [2, 3, 4, 5] | [2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q31_E3: vision-language models | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.5455 | 0.6250 |
| 2 | 0.6364 | 0.8750 |
| 3 | 0.5714 | 0.6364 |
| 4 | 0.5000 | 0.6667 |
| 5 | 0.8000 | 0.8750 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q32

Original question:

Show me cutting edge research works on neural network based quantum Monte Carlo.

Native queries:

1. Application of neural networks in quantum Monte Carlo studies
2. Neural network based quantum Monte Carlo papers
3. Recent advancements in quantum Monte Carlo using neural networks
4. Survey papers on neural network based quantum Monte Carlo
5. State-of-the-art research in neural network quantum Monte Carlo

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q32_E1: neural network | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [2, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q32_E2: quantum Monte Carlo | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q32_E3: cutting edge | numeric_comparison_negation_condition | 否 | 2/5; [3, 5] | [] | Recent advancements/state-of-the-art preserve the soft recency/novelty preference; no date invented. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2222 | 0.3636 |
| 2 | 0.4286 | 0.7500 |
| 3 | 0.2222 | 0.3636 |
| 4 | 0.4667 | 0.6667 |
| 5 | 0.3333 | 0.5000 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q33

Original question:

Show me some popular papers on generating textual adversarial examples for machine translation.

Native queries:

1. Survey papers on textual adversarial examples in machine translation
2. Textual adversarial examples in machine translation research papers
3. Adversarial example creation in machine translation using textual methods
4. State-of-the-art techniques for generating adversarial examples in machine translation
5. Methods for generating adversarial examples in machine translation

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q33_E1: textual adversarial examples | domain_technical_phrase | 是 | 3/5; [1, 2, 3] | [1, 2] | q4/q5 adversarial examples drop textual. |
| Q33_E2: machine translation | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q33_E3: popular | numeric_comparison_negation_condition | 否 | 0/5; [] | [] | state-of-the-art is not the same as popularity. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.4667 | 0.6250 |
| 2 | 0.4000 | 0.7143 |
| 3 | 0.2222 | 0.4000 |
| 4 | 0.3158 | 0.5000 |
| 5 | 0.4000 | 0.6250 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q34

Original question:

Show me research on 3d scene understanding leveraging progress on 3D AIGC foundation models.

Native queries:

1. Foundation models and their role in 3D scene understanding
2. Application of 3D AIGC foundation models in scene understanding
3. Advancements in 3D AIGC foundational models for scene understanding
4. Research on 3D scene understanding using AIGC
5. Survey papers on 3D scene understanding with 3D AIGC models

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q34_E1: 3d scene understanding | domain_technical_phrase | 是 | 3/5; [1, 4, 5] | [1, 4, 5] | q2/q3 3D modifies the models but scene understanding is not explicitly stated as 3D. |
| Q34_E2: 3D AIGC foundation models | entity_method_model | 是 | 2/5; [2, 3] | [2] | q1 omits AIGC; q4/q5 omit foundation. |
| Q34_E3: AIGC | benchmark_dataset_acronym | 是 | 4/5; [2, 3, 4, 5] | [2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.3125 | 0.5556 |
| 2 | 0.4000 | 0.6667 |
| 3 | 0.3125 | 0.5000 |
| 4 | 0.4615 | 0.5000 |
| 5 | 0.4000 | 0.5556 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q35

Original question:

Give me papers about LLM quantized pretraining.

Native queries:

1. Survey papers on LLM quantized pretraining
2. Quantitative pretraining of language models
3. Methods for quantized pretraining in LLM
4. Research on quantization techniques in LLM pretraining
5. Effects of quantization on language model pretraining

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q35_E1: LLM | benchmark_dataset_acronym | 否 | 4/5; [1, 3, 4, 5] | [1, 3, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q35_E2: quantized pretraining | entity_method_model | 是 | 4/5; [1, 3, 4, 5] | [1, 3] | quantization in pretraining accepted; q2 quantitative is not quantized. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.4444 | 0.7500 |
| 2 | 0.0909 | 0.1667 |
| 3 | 0.3000 | 0.7500 |
| 4 | 0.1667 | 0.4000 |
| 5 | 0.0769 | 0.1429 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q36

Original question:

Show me research on identity preservation video generation.

Native queries:

1. Survey papers on identity preservation in video generation
2. Deep learning techniques for identity preservation in video generation
3. Research articles on identity preservation video creation
4. Latest techniques in identity preservation video generation
5. AI approaches for identity preservation in video editing

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q36_E1: identity preservation | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q36_E2: video generation | domain_technical_phrase | 是 | 4/5; [1, 2, 3, 4] | [1, 2, 4] | q5 video editing is a different task. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.4545 | 0.8000 |
| 2 | 0.3077 | 0.5714 |
| 3 | 0.5000 | 0.5000 |
| 4 | 0.3636 | 0.6667 |
| 5 | 0.2308 | 0.4286 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q37

Original question:

Give me some papers showing that LLM agents can do schedule planning.

Native queries:

1. Survey papers on schedule planning with Language Model agents
2. Research articles on LLM-based schedule planning
3. LLM agents in schedule planning research papers
4. Use of LLM agents in schedule planning studies
5. Language Model agents and their application in schedule planning

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q37_E1: LLM agents | entity_method_model | 是 | 2/5; [3, 4] | [3, 4] | q1/q5 omit large; q2 LLM-based drops agents. |
| Q37_E2: schedule planning | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2353 | 0.3750 |
| 2 | 0.1875 | 0.4286 |
| 3 | 0.3571 | 0.8000 |
| 4 | 0.2500 | 0.6667 |
| 5 | 0.1667 | 0.3750 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q38

Original question:

Show me research on image encoding distributions.

Native queries:

1. Investigations on the use of diffusion models for image encoding distributions
2. Survey papers on image encoding distributions
3. Research on binary image compression using probabilistic encoding and decoding
4. Studies on image encoding techniques and their distribution
5. Analysis of image encoding distributions in machine learning

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q38_E1: image encoding distributions | domain_technical_phrase | 是 | 4/5; [1, 2, 4, 5] | [1, 2, 5] | q4 encoding techniques and their distribution preserves the phrase relation; q3 probabilistic compression is narrower/different. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2857 | 0.5000 |
| 2 | 0.4444 | 0.7500 |
| 3 | 0.3077 | 0.2857 |
| 4 | 0.2500 | 0.3333 |
| 5 | 0.2500 | 0.5000 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q39

Original question:

Help me search for the work related to the synthetic data of large language models. I want to know how to automatically generate large-scale, high-quality, diverse, difficult, and valuable long thought data for learning.

Native queries:

1. Survey papers on synthetic data for large language models
2. Methods for generating valuable long thought data for AI learning
3. Research on automatic generation of high-quality diverse data for language models
4. Techniques for generating synthetic data for language model training
5. Efficient methods for sampling diverse test cases from large language models using synthetic data

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q39_E1: synthetic data | domain_technical_phrase | 是 | 3/5; [1, 4, 5] | [1, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q39_E2: large language models | entity_method_model | 否 | 2/5; [1, 5] | [1, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q39_E3: automatically generate | numeric_comparison_negation_condition | 是 | 1/5; [3] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q39_E4: large-scale | numeric_comparison_negation_condition | 是 | 0/5; [] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q39_E5: high-quality | numeric_comparison_negation_condition | 是 | 1/5; [3] | [3] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q39_E6: diverse | numeric_comparison_negation_condition | 是 | 2/5; [3, 5] | [3, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q39_E7: difficult | numeric_comparison_negation_condition | 是 | 0/5; [] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q39_E8: valuable | numeric_comparison_negation_condition | 是 | 1/5; [2] | [2] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q39_E9: long thought data | domain_technical_phrase | 是 | 1/5; [2] | [2] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.1818 | 0.2778 |
| 2 | 0.1818 | 0.2500 |
| 3 | 0.2353 | 0.3158 |
| 4 | 0.1176 | 0.1429 |
| 5 | 0.1892 | 0.2727 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q40

Original question:

Could you list research that demonstrates the advantages of Quantization-Aware Training (QAT), which can enable the model to learn better representations for low-bit weights?.

Native queries:

1. Survey papers on Quantization-Aware Training benefits
2. Advantages of Quantization-Aware Training in AI
3. Research papers on the impact of Quantization-Aware Training on low-bit weight representations
4. Effects of Quantization-Aware Training on model representations
5. Comparative studies on Quantization-Aware Training and Post-Training Quantization in AI

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q40_E1: Quantization-Aware Training | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q40_E2: QAT | benchmark_dataset_acronym | 是 | 5/5; [1, 2, 3, 4, 5] | [] | The full form is explicitly defined in the original question; semantic retention counts it, strict acronym surface coverage is separately zero. |
| Q40_E3: low-bit weights | numeric_comparison_negation_condition | 是 | 1/5; [3] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q40_E4: better representations | numeric_comparison_negation_condition | 是 | 0/5; [] | [] | Representations/impact without better drops the comparative benefit. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.1034 | 0.1875 |
| 2 | 0.1852 | 0.2667 |
| 3 | 0.3103 | 0.3750 |
| 4 | 0.2222 | 0.3333 |
| 5 | 0.0938 | 0.1667 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q41

Original question:

Using synthesis data for scaling up sft data.

Native queries:

1. Use of synthetic data in increasing volume of SFT data
2. Survey paper on usage of synthetic data for scaling up soft target data
3. Scaling up SFT data with synthesis data
4. Applications of generative AI in creating synthetic data for soft target data scaling
5. Exponential growth of training data in NLP through synthetic data

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q41_E1: synthesis data | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [3] | synthetic data accepted as the wording variant. |
| Q41_E2: sft | benchmark_dataset_acronym | 是 | 2/5; [1, 3] | [1, 3] | soft target data in q2/q4 is not credited as SFT. |
| Q41_E3: scaling up | numeric_comparison_negation_condition | 是 | 5/5; [1, 2, 3, 4, 5] | [2, 3] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.1538 | 0.2500 |
| 2 | 0.2667 | 0.3000 |
| 3 | 0.6250 | 1.0000 |
| 4 | 0.1875 | 0.1667 |
| 5 | 0.0667 | 0.0909 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q42

Original question:

Show me research on how to select frames when doing video understanding.

Native queries:

1. Survey papers on frame selection in video understanding
2. Optical flow-based methods for key frame selection in video understanding
3. Research on temporal sampling strategies for video representation learning
4. Studies on efficient frame sampling in video comprehension
5. Papers on automated video summary generation using frame selection

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q42_E1: select frames | domain_technical_phrase | 是 | 4/5; [1, 2, 4, 5] | [] | frame selection/sampling accepted; q3 temporal sampling is broader and does not explicitly specify frames. |
| Q42_E2: video understanding | domain_technical_phrase | 是 | 3/5; [1, 2, 4] | [1, 2] | q3 representation learning and q5 summary generation are not the same task. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.1765 | 0.2500 |
| 2 | 0.0952 | 0.1667 |
| 3 | 0.1667 | 0.1000 |
| 4 | 0.1111 | 0.1000 |
| 5 | 0.1053 | 0.1000 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q43

Original question:

AI for Science papers, especially protein design and DPO of antibody design.

Native queries:

1. AI tools for protein design
2. Research on DPO in antibody design
3. Survey papers on protein design using AI
4. Application of AI in scientific research papers
5. AI advancements in protein design

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q43_E1: AI for Science | domain_technical_phrase | 是 | 1/5; [4] | [] | AI in scientific research is credited; protein-specific applications alone do not preserve the broad domain phrase. |
| Q43_E2: protein design | domain_technical_phrase | 是 | 3/5; [1, 3, 5] | [1, 3, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q43_E3: DPO | benchmark_dataset_acronym | 是 | 1/5; [2] | [2] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q43_E4: antibody design | domain_technical_phrase | 是 | 1/5; [2] | [2] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q43_E5: DPO of antibody design | numeric_comparison_negation_condition | 是 | 1/5; [2] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.3333 | 0.3750 |
| 2 | 0.2143 | 0.4286 |
| 3 | 0.2857 | 0.3750 |
| 4 | 0.2000 | 0.1111 |
| 5 | 0.2308 | 0.3750 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q44

Original question:

What are the researches that have explored the application of Crypto-based Private Learning in privacy-preserving machine learning?.

Native queries:

1. Survey papers on Crypto-based Private Learning in machine learning
2. Application of cryptographic techniques in private machine learning
3. Research on encryption methods in privacy-preserving machine learning
4. Use of homomorphic encryption in private learning for machine learning
5. Research articles on privacy-preserving machine learning using cryptography

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q44_E1: Crypto-based Private Learning | entity_method_model | 是 | 4/5; [1, 2, 3, 5] | [1] | Cryptographic/encryption private-learning paraphrases credited. q4 homomorphic encryption is an unsupported specific narrowing, not credited as the whole broad phrase. |
| Q44_E2: privacy-preserving machine learning | domain_technical_phrase | 是 | 3/5; [2, 3, 5] | [3, 5] | private machine learning in q2 accepted. q1/q4 private learning plus machine learning is less explicit about their relation. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.3000 | 0.5000 |
| 2 | 0.3158 | 0.3636 |
| 3 | 0.2381 | 0.3636 |
| 4 | 0.2381 | 0.2727 |
| 5 | 0.1818 | 0.3636 |

既有收益标签：positive；anchor 新增 GT=1。

## Q45

Original question:

All papers about controllability of video generation.

Native queries:

1. Survey papers on controllability of video generation
2. Research papers on video generation controllability
3. Latest research on controllability of video generation
4. Studies on the control aspects of video production
5. Papers on techniques for controlling video generation

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q45_E1: controllability | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3] | control aspects/controlling accepted as direct task paraphrases. |
| Q45_E2: video generation | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 5] | video production in this control context credited; borderline convention is explicit. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.5556 | 0.7500 |
| 2 | 0.4444 | 1.0000 |
| 3 | 0.4000 | 0.7500 |
| 4 | 0.1538 | 0.1429 |
| 5 | 0.2727 | 0.4000 |

既有收益标签：positive；anchor 新增 GT=1。

## Q46

Original question:

Show me research on robot decision making and task planning, especially relevant datasets and benchmarks.

Native queries:

1. Survey papers on robot decision making
2. Research on task planning in robotics
3. Benchmark datasets for robot decision making
4. Relevant datasets for robot decision making
5. Benchmarks used in robot decision making research

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q46_E1: robot decision making | domain_technical_phrase | 是 | 4/5; [1, 3, 4, 5] | [1, 3, 4, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q46_E2: task planning | domain_technical_phrase | 是 | 1/5; [2] | [2] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q46_E3: datasets | domain_technical_phrase | 否 | 2/5; [3, 4] | [3, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q46_E4: benchmarks | domain_technical_phrase | 否 | 2/5; [3, 5] | [5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.2500 | 0.3000 |
| 2 | 0.2500 | 0.2000 |
| 3 | 0.2500 | 0.4000 |
| 4 | 0.3333 | 0.5556 |
| 5 | 0.3125 | 0.4444 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q47

Original question:

How can LLM agents be evaluated and benchmarked for financial tasks? Note that I am referring to agents.

Native queries:

1. Survey papers on evaluation of LLM agents in finance
2. Benchmarking methods for LLM agents in financial tasks
3. Evaluation metrics for LLM agents in financial tasks
4. Regulatory and industry-standard benchmarks for evaluating LLM agents in finance
5. Comparative studies on LLM agent evaluation in financial domain

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q47_E1: LLM agents | entity_method_model | 是 | 5/5; [1, 2, 3, 4, 5] | [1, 2, 3, 4] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q47_E2: evaluated | domain_technical_phrase | 否 | 4/5; [1, 3, 4, 5] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q47_E3: benchmarked | domain_technical_phrase | 否 | 2/5; [2, 4] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q47_E4: financial tasks | domain_technical_phrase | 是 | 5/5; [1, 2, 3, 4, 5] | [2, 3] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q47_E5: I am referring to agents | numeric_comparison_negation_condition | 是 | 5/5; [1, 2, 3, 4, 5] | [] | Explicit agent emphasis retained; overlapping element counted transparently. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.0833 | 0.1667 |
| 2 | 0.2500 | 0.3636 |
| 3 | 0.2500 | 0.3636 |
| 4 | 0.1667 | 0.1333 |
| 5 | 0.0833 | 0.1429 |

既有收益标签：no_added_gain；anchor 新增 GT=0。

## Q48

Original question:

Papers that explore using large language models for mining factors in stock exchange analysis.

Native queries:

1. Application of large language models in stock market analysis
2. Role of AI and language models in stock prediction
3. Impact of large language models on stock exchange analysis
4. Use of GPT-3 in stock market trend analysis
5. Survey papers on large language models in stock exchange analysis

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q48_E1: large language models | entity_method_model | 否 | 3/5; [1, 3, 5] | [1, 3, 5] | q2 language models omit large; q4 GPT-3 adds a specific model instead of preserving the general LLM class. |
| Q48_E2: mining factors | domain_technical_phrase | 是 | 0/5; [] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q48_E3: stock exchange analysis | domain_technical_phrase | 是 | 3/5; [1, 3, 5] | [3, 5] | stock market analysis in q1 accepted; prediction/trend analysis in q2/q4 is narrower/different. |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.3529 | 0.4545 |
| 2 | 0.2105 | 0.2500 |
| 3 | 0.3529 | 0.6000 |
| 4 | 0.1500 | 0.1538 |
| 5 | 0.5000 | 0.6000 |

既有收益标签：positive；anchor 新增 GT=1。

## Q49

Original question:

Can you help me find research papers that explore the use of large vision-language models as agents to automatically play PC games?

Native queries:

1. Use of AI in automated PC game playing
2. Exploration of large vision-language models as gaming agents
3. Research on Large Multimodal Models (LMMs) and their application in automatic PC game play
4. Studies on PC game automation using large vision-language models
5. Survey papers on vision-language models as game agents

| 元素 ID / 原文片段 | 类别 | 高信息 H | 语义复核频次/位置 | 严格词面位置 | 说明 |
|---|---|---|---|---|---|
| Q49_E1: large vision-language models | entity_method_model | 是 | 2/5; [2, 4] | [2, 4] | q3 multimodal is broader; q5 omits large. |
| Q49_E2: agents | entity_method_model | 是 | 2/5; [2, 5] | [2, 5] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q49_E3: automatically play | numeric_comparison_negation_condition | 是 | 3/5; [1, 3, 4] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |
| Q49_E4: PC games | domain_technical_phrase | 是 | 3/5; [1, 3, 4] | [] | 直接词面、词形或任务同义表达；完整 query 证据见 JSON。 |

| Native # | Original-native Jaccard | 去通用词 Jaccard |
|---|---:|---:|
| 1 | 0.1071 | 0.0714 |
| 2 | 0.2800 | 0.4167 |
| 3 | 0.1562 | 0.2667 |
| 4 | 0.1786 | 0.3846 |
| 5 | 0.2308 | 0.3333 |

既有收益标签：no_added_gain；anchor 新增 GT=0。
