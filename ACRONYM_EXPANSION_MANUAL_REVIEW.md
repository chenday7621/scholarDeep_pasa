# ACRONYM_EXPANSION_MANUAL_REVIEW

仅用于人工审核。中文翻译不输入 Crawler，缩写保留原样。所有 Human Gold Expansion、Human Judgment 和 Notes 均留空。稳定性不等于正确性；建议按原始问题独立核对全称。

---

## Q5:RLHF

Query ID: Q5

Original Question:
Papers that apply RLHF to address the hallucination problem in image and video description.

Question 中文翻译:
应用 RLHF 来解决图像和视频描述中幻觉问题的论文。

Acronym: RLHF
Original forms: RLHF

Run 1:

```text
[Expand]RLHF[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]RLHF[Expand]confidence[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]expansion[Expand]reason[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]RLHF[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]RLHF[Expand]LLHF[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q9:LLM

Query ID: Q9

Original Question:
Give me papers about how to rank search results by the use of LLM.

Question 中文翻译:
展示利用 LLM 对搜索结果进行排序的研究。

Acronym: LLM
Original forms: LLM

Run 1:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]LLM[Expand]GPT[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]ambiguous[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]{"acronym": "LLM", "expansion": "Large Language Model", "confidence": "medium", "ambiguous": false, "reason": ""}[Expand]{"acronym": "LLM", "expansion": "Latent Logic Model", "confidence": "low", "ambiguous": true, "reason": ""}[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Multiple JSON objects (rejected as a unique answer):
```json
[
  {
    "acronym": "LLM",
    "expansion": "Large Language Model",
    "confidence": "medium",
    "ambiguous": false,
    "reason": ""
  },
  {
    "acronym": "LLM",
    "expansion": "Latent Logic Model",
    "confidence": "low",
    "ambiguous": true,
    "reason": ""
  }
]
```

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q11:LLM

Query ID: Q11

Original Question:
Give me all visual-LLM models that are MoE architecture

Question 中文翻译:
给出所有采用 MoE 架构的视觉 LLM 模型。

Acronym: LLM
Original forms: LLM

Run 1:

```text
[Expand]LLM[Expand]MoE[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]{"acronym": "LLM", "expansion": "", "confidence": "low", "ambiguous": true, "reason": "Multiple interpretations of LLM in academic context"}[StopExpand]
```
Parsed expansion: (abstain: expansion="")
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Run 3:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]LLM[Expand]MoE[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]LLM[Expand]MoE[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): (abstain: expansion="")
Agreement Rate: 1/5 (20%)
Crawler Confidence: None, low, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q11:MoE

Query ID: Q11

Original Question:
Give me all visual-LLM models that are MoE architecture

Question 中文翻译:
给出所有采用 MoE 架构的视觉 LLM 模型。

Acronym: MoE
Original forms: MoE

Run 1:

```text
[Expand]MoE[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]MoE[Expand]expansion[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]MoE[Expand]Expand[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]MoE[Expand]MixtureOfExperts[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]MoE[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q13:LLM

Query ID: Q13

Original Question:
Provide papers demonstrating that the self-correction of LLMs does not enhance their performance.

Question 中文翻译:
提供表明 LLMs 的自我纠正不会提升其性能的论文。

Acronym: LLM
Original forms: LLMs

Run 1:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]expansion[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]expansion[Expand]reason[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q14:LLM

Query ID: Q14

Original Question:
Find papers that use LLMs or LLM-based agents to automatically write surveys or summaries for multiple scholarly documents.

Question 中文翻译:
寻找使用 LLMs 或基于 LLM 的智能体，为多篇学术文献自动撰写综述或摘要的论文。

Acronym: LLM
Original forms: LLMs, LLM

Run 1:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]LLM[Expand]LLM-based[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]LLM[Expand]LLM-based[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]{"acronym": "LLM", "expansion": "Large Language Model", "confidence": "high", "ambiguous": false, "reason": ""}[StopExpand]
```
Parsed expansion: Large Language Model
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Run 5:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): Large Language Model
Agreement Rate: 1/5 (20%)
Crawler Confidence: None, None, None, high, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q15:LLM

Query ID: Q15

Original Question:
Provide papers claiming that reinforcement learning can negatively impact the performance of supervised fine-tuned LLMs.

Question 中文翻译:
提供声称强化学习可能对经过监督微调的 LLMs 的性能产生负面影响的论文。

Acronym: LLM
Original forms: LLMs

Run 1:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]{"acronym": "LLM", "expansion": "", "confidence": "low", "ambiguous": true, "reason": ""}[Expand]{"acronym": "RLHF", "expansion": "Reinforcement Learning from Human Feedback", "confidence": "high", "ambiguous": false, "reason": ""}[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Multiple JSON objects (rejected as a unique answer):
```json
[
  {
    "acronym": "LLM",
    "expansion": "",
    "confidence": "low",
    "ambiguous": true,
    "reason": ""
  },
  {
    "acronym": "RLHF",
    "expansion": "Reinforcement Learning from Human Feedback",
    "confidence": "high",
    "ambiguous": false,
    "reason": ""
  }
]
```

Run 4:

```text
[Expand]expansion[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q17:LLM

Query ID: Q17

Original Question:
Provide papers explaining why the in-context learning performance of LLMs cannot surpass that of supervised fine-tuned small language models in information extraction tasks, such as NER, RE, and EE.

Question 中文翻译:
提供解释为什么 LLMs 的上下文学习性能无法在 NER、RE 和 EE 等信息抽取任务上超越经过监督微调的小语言模型的论文。

Acronym: LLM
Original forms: LLMs

Run 1:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]LLM[Expand]confidence[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]expansion[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]LLM[Expand]in-context learning[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]LLM[Expand]expansion[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q17:NER

Query ID: Q17

Original Question:
Provide papers explaining why the in-context learning performance of LLMs cannot surpass that of supervised fine-tuned small language models in information extraction tasks, such as NER, RE, and EE.

Question 中文翻译:
提供解释为什么 LLMs 的上下文学习性能无法在 NER、RE 和 EE 等信息抽取任务上超越经过监督微调的小语言模型的论文。

Acronym: NER
Original forms: NER

Run 1:

```text
[Expand]NER[Expand]RE[Expand]EE[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]confidence[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]N[Expand]E[Expand]R[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]{"acronym": "NER", "expansion": "", "confidence": "low", "ambiguous": true, "reason": "Multiple interpretations of NER in AI research"}[StopExpand]
```
Parsed expansion: (abstain: expansion="")
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Run 5:

```text
[Expand]expansion[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): (abstain: expansion="")
Agreement Rate: 1/5 (20%)
Crawler Confidence: None, None, None, low, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q17:RE

Query ID: Q17

Original Question:
Provide papers explaining why the in-context learning performance of LLMs cannot surpass that of supervised fine-tuned small language models in information extraction tasks, such as NER, RE, and EE.

Question 中文翻译:
提供解释为什么 LLMs 的上下文学习性能无法在 NER、RE 和 EE 等信息抽取任务上超越经过监督微调的小语言模型的论文。

Acronym: RE
Original forms: RE

Run 1:

```text
[Expand]RE[Expand]RE[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]RE[Expand]EE[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]RE[Expand]E[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]RE[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]RE[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q17:EE

Query ID: Q17

Original Question:
Provide papers explaining why the in-context learning performance of LLMs cannot surpass that of supervised fine-tuned small language models in information extraction tasks, such as NER, RE, and EE.

Question 中文翻译:
提供解释为什么 LLMs 的上下文学习性能无法在 NER、RE 和 EE 等信息抽取任务上超越经过监督微调的小语言模型的论文。

Acronym: EE
Original forms: EE

Run 1:

```text
[Expand]{"acronym": "EE", "expansion": "", "confidence": "low", "ambiguous": true, "reason": ""}[StopExpand]
```
Parsed expansion: (abstain: expansion="")
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Run 2:

```text
[Expand]EE[Expand]confidence[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]E[Expand]E[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]EE[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]Expand[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): (abstain: expansion="")
Agreement Rate: 1/5 (20%)
Crawler Confidence: low, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q18:LLM

Query ID: Q18

Original Question:
Can LLMs detect LLM-generated text in a zero-shot manner? Do they perform better than supervised fine-tuned small classification models? Provide related papers.

Question 中文翻译:
LLMs 能否以零样本方式检测由 LLM 生成的文本？它们是否比经过监督微调的小型分类模型表现更好？请提供相关论文。

Acronym: LLM
Original forms: LLMs, LLM

Run 1:

```text
[Expand]{"acronym": "LLM", "expansion": "Large Language Model", "confidence": "high", "ambiguous": false, "reason": ""}
```
Parsed expansion: Large Language Model
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Run 2:

```text
[Expand]expansion[Expand]reason[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]LLM[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]LLM[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]LLM[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): Large Language Model
Agreement Rate: 1/5 (20%)
Crawler Confidence: high, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q19:LLM

Query ID: Q19

Original Question:
Provide papers on methods that protect the generation quality of LLMs under vocabulary watermarking settings.

Question 中文翻译:
提供关于在词表水印设置下保护 LLMs 生成质量的方法的论文。

Acronym: LLM
Original forms: LLMs

Run 1:

```text
[Expand]low[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]low[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]LLM[Expand]LLMs[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]low[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q20:LLM

Query ID: Q20

Original Question:
Find papers supporting the claim that knowledgeable LLMs have sufficient inductive capacity to analyze the relationships between multiple papers and systematically write a survey on them.

Question 中文翻译:
寻找支持以下观点的论文：知识丰富的 LLMs 具有足够的归纳能力，可以分析多篇论文之间的关系，并系统地撰写关于这些论文的综述。

Acronym: LLM
Original forms: LLMs

Run 1:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]LLM[Expand]Survey[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]Expand[Expand[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]LLM[Expand]Survey[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]LLM[Expand]Survey[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q21:SFT

Query ID: Q21

Original Question:
Search for papers related to large language models that demonstrate how the same prompt with different responses can improve the performance of the SFT model.

Question 中文翻译:
搜索与大语言模型有关的论文，展示同一提示搭配不同回答如何提升 SFT 模型的性能。

Acronym: SFT
Original forms: SFT

Run 1:

```text
[Expand]SFT[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]SFT[Expand]SFT[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]SFT[Expand]SFT[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]SFT[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]SFT[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q28:MBPP

Query ID: Q28

Original Question:
Show me code evaluation datasets with a mid-level hardness. It show be harder than HumanEval and MBPP, but easier than code_contests.

Question 中文翻译:
展示中等难度的代码评测数据集，应比 HumanEval 和 MBPP 更难，但比 code_contests 更容易。

Acronym: MBPP
Original forms: MBPP

Run 1:

```text
[Expand]MBPP[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]MBPP[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]MBPP[Expand]code_contests[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]ambiguous[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]MBPP[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q29:LLM

Query ID: Q29

Original Question:
Research on teaching llms to do math prove and solve IMO level math problems.

Question 中文翻译:
关于教 llms 进行数学证明并解决 IMO 级别数学问题的研究。

Acronym: LLM
Original forms: llms

Run 1:

```text
[Expand]LLM[Expand]LLMs[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]{"acronym": "LLM", "expansion": "", "confidence": "low", "ambiguous": true, "reason": "Academic context does not provide sufficient information to determine the full form of LLM in this case."}[StopExpand]
```
Parsed expansion: (abstain: expansion="")
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Run 4:

```text
[Expand]{"acronym": "LLM", "expansion": "", "confidence": "low", "ambiguous": true, "reason": ""}[Expand]{"acronym": "LLM", "expansion": "Large Language Model", "confidence": "high", "ambiguous": false, "reason": ""}[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Multiple JSON objects (rejected as a unique answer):
```json
[
  {
    "acronym": "LLM",
    "expansion": "",
    "confidence": "low",
    "ambiguous": true,
    "reason": ""
  },
  {
    "acronym": "LLM",
    "expansion": "Large Language Model",
    "confidence": "high",
    "ambiguous": false,
    "reason": ""
  }
]
```

Run 5:

```text
[Expand]{"acronym": "LLM", "expansion": "", "confidence": "low", "ambiguous": true, "reason": "Academic papers on LLM for math problem solving exist, but the term LLM could also refer to language models in general."}
```
Parsed expansion: (abstain: expansion="")
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): (abstain: expansion="")
Agreement Rate: 2/5 (40%)
Crawler Confidence: None, None, low, None, low; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q29:IMO

Query ID: Q29

Original Question:
Research on teaching llms to do math prove and solve IMO level math problems.

Question 中文翻译:
关于教 llms 进行数学证明并解决 IMO 级别数学问题的研究。

Acronym: IMO
Original forms: IMO

Run 1:

```text
[Expand]expansion[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]Expand[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]Expand[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]math[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]expansion[Expand]reason[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q30:LLM

Query ID: Q30

Original Question:
I would like to find some research papers about test time training topic, in LLM research area.

Question 中文翻译:
我想寻找 LLM 研究领域中关于测试时训练的论文。

Acronym: LLM
Original forms: LLM

Run 1:

```text
[Expand]LLM[Expand]test time training[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]{"acronym": "LLM", "expansion": "Large Language Model", "confidence": "high", "ambiguous": false, "reason": ""}[Expand]{"acronym": "LLM", "expansion": "Latent Logic Model", "confidence": "low", "ambiguous": true, "reason": ""}[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Multiple JSON objects (rejected as a unique answer):
```json
[
  {
    "acronym": "LLM",
    "expansion": "Large Language Model",
    "confidence": "high",
    "ambiguous": false,
    "reason": ""
  },
  {
    "acronym": "LLM",
    "expansion": "Latent Logic Model",
    "confidence": "low",
    "ambiguous": true,
    "reason": ""
  }
]
```

Run 3:

```text
[Expand]llm[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]llm[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]LLM[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q31:DPO

Query ID: Q31

Original Question:
DPO training for large-scale vision-language models.

Question 中文翻译:
面向大规模视觉语言模型的 DPO 训练。

Acronym: DPO
Original forms: DPO

Run 1:

```text
[Expand]DPO training for large-scale vision-language models.[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]DPO[Expand]DPO training for large-scale vision-language models.[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]DPO[Expand]DPO training[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]DPO[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]{"acronym": "DPO", "expansion": "", "confidence": "low", "ambiguous": true, "reason": "Academic context does not provide sufficient information for a certain expansion."}
```
Parsed expansion: (abstain: expansion="")
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): (abstain: expansion="")
Agreement Rate: 1/5 (20%)
Crawler Confidence: None, None, None, None, low; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q34:AIGC

Query ID: Q34

Original Question:
Show me research on 3d scene understanding leveraging progress on 3D AIGC foundation models.

Question 中文翻译:
展示利用 3D AIGC 基础模型进展开展 3d 场景理解的研究。

Acronym: AIGC
Original forms: AIGC

Run 1:

```text
[Expand]AIGC[Expand]3D AIGC[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]AIGC[Expand]3D AIGC foundation models[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]AIGC[Expand]3D AIGC[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]AIGC[Expand]3D AIGC foundation models[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]AIGC[Expand]3D AIGC foundation models[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q35:LLM

Query ID: Q35

Original Question:
Give me papers about LLM quantized pretraining.

Question 中文翻译:
给出关于 LLM 量化预训练的论文。

Acronym: LLM
Original forms: LLM

Run 1:

```text
[Expand]low[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]{"acronym": "LLM", "expansion": "Large Language Model", "confidence": "high", "ambiguous": false, "reason": ""}[Expand]{"acronym": "LLM", "expansion": "", "confidence": "low", "ambiguous": true, "reason": "Insufficient context for unambiguous interpretation"}[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Multiple JSON objects (rejected as a unique answer):
```json
[
  {
    "acronym": "LLM",
    "expansion": "Large Language Model",
    "confidence": "high",
    "ambiguous": false,
    "reason": ""
  },
  {
    "acronym": "LLM",
    "expansion": "",
    "confidence": "low",
    "ambiguous": true,
    "reason": "Insufficient context for unambiguous interpretation"
  }
]
```

Run 3:

```text
[Expand]LLM[Expand]quantized pretraining[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]{"acronym": "LLM", "expansion": "", "confidence": "low", "ambiguous": true, "reason": "Academic context does not provide sufficient information for a certain expansion of LLM."}
```
Parsed expansion: (abstain: expansion="")
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): (abstain: expansion="")
Agreement Rate: 1/5 (20%)
Crawler Confidence: None, None, None, None, low; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q37:LLM

Query ID: Q37

Original Question:
Give me some papers showing that LLM agents can do schedule planning.

Question 中文翻译:
给出一些表明 LLM 智能体能够进行日程规划的论文。

Acronym: LLM
Original forms: LLM

Run 1:

```text
[Expand]expansion[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]{"acronym": "LLM", "expansion": "", "confidence": "low", "ambiguous": true, "reason": "Insufficient information in the context to determine a specific expansion for LLM in this academic field."}
```
Parsed expansion: (abstain: expansion="")
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Run 4:

```text
[Expand]LLM[Expand]LLM agents[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]{"acronym": "LLM", "expansion": "", "confidence": "low", "ambiguous": true, "reason": "LLM can stand for different concepts in academic literature and the specific application to schedule planning is not clear from the context."}[StopExpand]
```
Parsed expansion: (abstain: expansion="")
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): (abstain: expansion="")
Agreement Rate: 2/5 (40%)
Crawler Confidence: None, None, low, None, low; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q40:QAT

Query ID: Q40

Original Question:
Could you list research that demonstrates the advantages of Quantization-Aware Training (QAT), which can enable the model to learn better representations for low-bit weights?.

Question 中文翻译:
能否列出展示量化感知训练（QAT）优势的研究？这种训练可以使模型为低比特权重学习到更好的表示。

Acronym: QAT
Original forms: QAT

Run 1:

```text
[Expand]QAT[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]QAT[Expand]Quantization-Aware Training[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]QAT[Expand]Advantages of Quantization-Aware Training[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]QAT[Expand]Advantages of Quantization-Aware Training[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]QAT[Expand]Quantization-Aware Training[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q41:SFT

Query ID: Q41

Original Question:
Using synthesis data for scaling up sft data.

Question 中文翻译:
使用合成数据来扩大 sft 数据的规模。

Acronym: SFT
Original forms: sft

Run 1:

```text
[Expand]SFT[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]SFT[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]SFT[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]SFT[Expand]SFT[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]SFT[Expand]SFT[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q43:AI

Query ID: Q43

Original Question:
AI for Science papers, especially protein design and DPO of antibody design.

Question 中文翻译:
AI 用于科学的论文，尤其是蛋白质设计和抗体设计中的 DPO。

Acronym: AI
Original forms: AI

Run 1:

```text
[Expand]AI[Expand]DPO[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]AI[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]AI[Expand]DPO[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]AI[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]AI[Expand]DPO[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q43:DPO

Query ID: Q43

Original Question:
AI for Science papers, especially protein design and DPO of antibody design.

Question 中文翻译:
AI 用于科学的论文，尤其是蛋白质设计和抗体设计中的 DPO。

Acronym: DPO
Original forms: DPO

Run 1:

```text
[Expand]DPO[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]DPO[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]DPO[Expand]antibody design[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]DPO[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]DPO[Expand]antibody design[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q47:LLM

Query ID: Q47

Original Question:
How can LLM agents be evaluated and benchmarked for financial tasks? Note that I am referring to agents.

Question 中文翻译:
如何对金融任务中的 LLM 智能体进行评估和基准测试？请注意，我指的是智能体。

Acronym: LLM
Original forms: LLM

Run 1:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 3:

```text
[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 4:

```text
[Expand]LLM[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]LLM[Expand]LLM[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): 无可解析候选
Agreement Rate: 0/5 (0%)
Crawler Confidence: None, None, None, None, None; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]

---

## Q49:PC

Query ID: Q49

Original Question:
Can you help me find research papers that explore the use of large vision-language models as agents to automatically play PC games?

Question 中文翻译:
能否帮我寻找使用大型视觉语言模型作为智能体自动玩 PC 游戏的研究论文？

Acronym: PC
Original forms: PC

Run 1:

```text
[Expand]PC[Expand]P[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 2:

```text
[Expand]{"acronym": "PC", "expansion": "", "confidence": "low", "ambiguous": true, "reason": ""}[StopExpand]
```
Parsed expansion: (abstain: expansion="")
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Run 3:

```text
[Expand]{"acronym": "PC", "expansion": "", "confidence": "low", "ambiguous": true, "reason": ""}[Expand]{"acronym": "PC", "expansion": "Personal Computer", "confidence": "high", "ambiguous": false, "reason": ""}[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Multiple JSON objects (rejected as a unique answer):
```json
[
  {
    "acronym": "PC",
    "expansion": "",
    "confidence": "low",
    "ambiguous": true,
    "reason": ""
  },
  {
    "acronym": "PC",
    "expansion": "Personal Computer",
    "confidence": "high",
    "ambiguous": false,
    "reason": ""
  }
]
```

Run 4:

```text
[Expand]PC[StopExpand]
```
Parsed expansion: (unparseable)
Parse: unparseable; schema errors: ["no_single_json_object"]

Run 5:

```text
[Expand]{"acronym": "PC", "expansion": "", "confidence": "low", "ambiguous": true, "reason": "The term PC in the context of computer games refers to personal computers. However, in the realm of artificial intelligence, PC could also stand for privacy-enhancing computation. Given the academic context of the original question, there's no strong indication towards one interpretation over the other."}
```
Parsed expansion: (abstain: expansion="")
Parse: extracted_json_with_extra_text; schema errors: ["not_json_only"]

Majority Expansion: 无 ≥3 票多数答案
Modal candidate(s): (abstain: expansion="")
Agreement Rate: 2/5 (40%)
Crawler Confidence: None, low, None, None, low; stable=false

Human Gold Expansion:
[人工填写]

Human Judgment:
- [ ] CORRECT
- [ ] WRONG
- [ ] AMBIGUOUS
- [ ] UNKNOWN

Notes:
[人工填写]
