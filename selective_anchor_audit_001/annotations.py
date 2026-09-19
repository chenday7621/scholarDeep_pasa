"""Analyst-authored, source-grounded element annotations; no outcome/GT access.

Indices are 1-based native-query positions judged to retain the COMPLETE element.
They are review judgments, not an automated semantic scorer or a trigger.
"""

METHOD = 'entity_method_model'
NAME = 'benchmark_dataset_acronym'
TECH = 'domain_technical_phrase'
LIMIT = 'numeric_comparison_negation_condition'


def e(span, category, high_information, retained, note=''):
    return {'source_span': span, 'category': category, 'high_information': high_information,
            'reviewed_retained_native_indices': retained, 'review_note': note}


# No GT titles, IDs, gains, labels, thresholds, candidate triggers, or search results.
ANNOTATIONS = {
 'Q0': [
  e('large language model', METHOD, False, [2,4], 'Unqualified language model is not credited as explicitly large.'),
  e('pre-training', METHOD, True, [1,2,3,4,5]),
  e('smaller dataset', TECH, True, [1,2,4], 'limited dataset alone does not retain the comparative smaller.'),
  e('using a smaller dataset in large language model pre-training can result in better models than using bigger datasets', LIMIT, True, [], 'Benefits/effectiveness do not preserve the explicit smaller-versus-bigger superiority claim.')],
 'Q1': [
  e('large language models', METHOD, False, [2]),
  e('in-context learning', METHOD, True, [1,2,3,4,5]),
  e('pre-training', METHOD, True, [2,3,4,5], 'pre-trained in q1 denotes a model state; it does not specify studying the pre-training process.'),
  e('gain in-context learning capability in the process of pre-training', LIMIT, True, [5], 'q5 development of in-context learning during pre-training retains acquisition; association alone is insufficient.')],
 'Q2': [
  e('autoregressive transformer', METHOD, True, [1,2,3,4,5]),
  e('generate videos', TECH, True, [1,3,4,5], 'video generation/creation retained; video editing/composition in q2 is a different task.')],
 'Q3': [
  e('multimodal foundation models', METHOD, True, [1,2,3], 'q4 drops multimodal explicitly; q5 Large Multimodal Models drops foundation status.'),
  e('both visual and audio inputs', LIMIT, True, [3,4]),
  e('pre-trained on large-scale datasets', LIMIT, True, [1]),
  e('including visual, audio, and audio-visual data', LIMIT, True, [], 'q2 has audio-visual pretraining but not all three specified data types.'),
  e('exclude survey papers', LIMIT, True, [], 'Not generating the word survey does not explicitly retain exclusion.')],
 'Q4': [
  e('reinforcement learning', METHOD, True, [1,2,3,4,5]),
  e('Large Language Model', METHOD, False, [1,2,3,4,5]),
  e('agent tasks', TECH, True, [3,4,5], 'Explicit LLM agents preserve the task object; generic LLM training does not.')],
 'Q5': [
  e('RLHF', NAME, True, [1,2,3,4,5]),
  e('hallucination problem', TECH, True, [3,4,5]),
  e('image', TECH, False, [1,4]),
  e('video', TECH, False, [2,3]),
  e('description', TECH, True, [1,2,4]),
  e('apply RLHF to address the hallucination problem in image and video description', LIMIT, True, [], 'No single query retains RLHF + hallucination + description for BOTH modalities; the component elements are distributed.')],
 'Q6': [
  e('large language models', METHOD, False, [1,2,3,5]),
  e('HotPotQA', NAME, True, [1,2,3,4,5]),
  e('evaluate their performance through experiments', LIMIT, True, [4], 'q2 evaluation methods does not explicitly require empirical experiments; q4 explicitly experiments.')],
 'Q7': [
  e('long video description', TECH, True, [1,3,5], 'Summarization/understanding do not fully preserve description.'),
  e('duration of at least several minutes', LIMIT, True, [])],
 'Q8': [
  e('reward shaping', METHOD, True, [1,2,3]),
  e('large language model', METHOD, False, [1,3,4,5]),
  e('agent', TECH, True, [2]),
  e('train', TECH, False, [1,2,3,5])],
 'Q9': [
  e('LLM', NAME, False, [1,2,4,5], 'q5 uses the explicit full form Large Language Models; q3 Language Model omits large.'),
  e('rank search results', TECH, True, [1,2,3,4], 'q5 ranking mechanisms omits search results.')],
 'Q10': [
  e('scaling law', TECH, True, [1,2,3,5], 'q4 scaling behavior is not explicitly a scaling law.'),
  e('multi-module models', METHOD, True, [1], 'Keep source multi-module; do not silently correct it to multimodal.'),
  e('video-text', TECH, True, [2,4]),
  e('image-text', TECH, True, [3])],
 'Q11': [
  e('visual-LLM', METHOD, True, [1,2,4,5], 'q3 multimodal is broader than the explicitly visual modality.'),
  e('MoE', NAME, True, [1,2,3,4,5])],
 'Q12': [
  e('transformer architecture', METHOD, True, [1,2,3,4,5]),
  e('3d', LIMIT, True, [1,2,3,4,5]),
  e('video generation', TECH, True, [1,2,3,4,5], 'production/creation/synthesis accepted as task paraphrases here.')],
 'Q13': [
  e('self-correction', METHOD, True, [1,2,3,4,5]),
  e('LLMs', NAME, False, [3,4,5]),
  e('does not enhance their performance', LIMIT, True, [3,4], 'q3 explicitly not enhancing; q4 ineffectiveness is credited as equivalent. q1 limitations and q2/q5 impact are weaker or neutral.')],
 'Q14': [
  e('LLMs', NAME, False, [1,2,3,5]),
  e('LLM-based agents', METHOD, True, [3,5]),
  e('automatically write', LIMIT, True, [1,4], 'Automatic survey writing/synthesis; q5 multi-document summary is not explicitly automatic.'),
  e('surveys or summaries', TECH, True, [1,2,3,4,5]),
  e('multiple scholarly documents', LIMIT, True, [], 'q5 multi-document omits scholarly; q2/q3 scholarly documents do not explicitly preserve multi-document aggregation.')],
 'Q15': [
  e('reinforcement learning', METHOD, True, [1,2,3,4,5]),
  e('supervised fine-tuned LLMs', METHOD, True, [1,4], 'q2 describes supervised fine-tuning but not an explicitly large model; q3/q5 drop supervised.'),
  e('negatively impact the performance', LIMIT, True, [1,4], 'Negative impacts/downsides retained; effects/implications alone do not preserve direction.')],
 'Q16': [
  e('trigger-free', LIMIT, True, [1,2,3,4], 'without triggers accepted; q5 only excludes human-annotated triggers, not all triggers.'),
  e('document-level', LIMIT, True, [1,3,4]),
  e('event extraction', TECH, True, [1,2,3,4,5]),
  e('do not use human-annotated triggers', LIMIT, True, [1,2,3,4,5], 'Trigger-free/without any triggers entails excluding human-annotated triggers; a stronger restriction is credited and noted.')],
 'Q17': [
  e('in-context learning', METHOD, True, [1,2,3,4,5]),
  e('LLMs', NAME, False, [3,5]),
  e('supervised fine-tuned small language models', METHOD, True, [4]),
  e('information extraction', TECH, True, [1,2,3]),
  e('NER', NAME, True, [4]),
  e('RE', NAME, True, []),
  e('EE', NAME, True, []),
  e('cannot surpass', LIMIT, True, [4], 'q4 small supervised models outperform in-context learning preserves the claimed direction; comparison/limitations alone does not.')],
 'Q18': [
  e('LLMs', NAME, False, [1,2,3,4]),
  e('detect LLM-generated text', TECH, True, [2,3], 'q4 evaluation in zero-shot scenarios is not explicitly detection; q1 detection omits generated text.'),
  e('zero-shot', LIMIT, True, [1,2,4]),
  e('supervised fine-tuned small classification models', METHOD, True, [3]),
  e('perform better than supervised fine-tuned small classification models', LIMIT, True, [], 'q1 comparison and q3 vs do not preserve the explicit better-than relation.')],
 'Q19': [
  e('LLMs', NAME, False, [1,2,3,4,5]),
  e('generation quality', TECH, True, [1,2,4]),
  e('vocabulary watermarking', METHOD, True, [1,2,4,5], 'q3 changes the subject to detecting/mitigating watermarking attacks.'),
  e('protect the generation quality', LIMIT, True, [1,2], 'q5 mitigate effects on generation does not explicitly retain quality; q4 impact is neutral.'),
  e('under vocabulary watermarking settings', LIMIT, True, [1,2,4,5])],
 'Q20': [
  e('knowledgeable LLMs', METHOD, True, [], 'LLMs without knowledgeable does not preserve the qualifier.'),
  e('sufficient inductive capacity', LIMIT, True, [], 'q1 inductive capacity drops sufficient.'),
  e('relationships between multiple papers', TECH, True, [], 'q3/q5 analyze multiple papers but do not state inter-paper relationships.'),
  e('systematically write a survey', TECH, True, [4], 'systematic review writing accepted as task equivalent.')],
 'Q21': [
  e('large language models', METHOD, False, [3,5]),
  e('same prompt with different responses', LIMIT, True, [3,4], 'q1 different response prompts can suggest different prompts; q2 drops the same-prompt restriction.'),
  e('SFT', NAME, True, [1,2,3,4,5]),
  e('improve the performance', LIMIT, True, [1,5], 'Enhancing/improving retained; impact/affect without direction is insufficient.')],
 'Q22': [
  e('common sense problems', TECH, True, [1,2,3,4,5]),
  e('machine translation', TECH, True, [1,2,3,4,5])],
 'Q23': [
  e('reinforcement learning', METHOD, True, [1,2,3,4,5]),
  e('diffusion models', METHOD, True, [1,2,4,5]),
  e('video generation', TECH, True, [1,2,3,4,5], 'Video diffusion models in optimization context credited to generation in q2.'),
  e('optimize', LIMIT, True, [1,2,3,5])],
 'Q24': [
  e('machine translation', TECH, True, [1,2,3,4,5]),
  e('agents', METHOD, True, [1,2,5])],
 'Q25': [
  e('Video', TECH, False, [1,2,3,4,5]),
  e('aesthetics score', TECH, True, [3], 'q2 scoring drops aesthetics; q4 aesthetics drops score; q5 quality is broader.'),
  e('multimodal large models', METHOD, True, [1,2], 'q3/q4 omit large; q5 omits multimodal.')],
 'Q26': [
  e('Scaling Laws', TECH, True, [1,2,3,5]),
  e('Fine-Grained', LIMIT, True, [1,2,4]),
  e('Mixture of Experts', METHOD, True, [1,2,3,4,5])],
 'Q27': [
  e('rejection sampling', METHOD, True, [1,2,3,4,5]),
  e('finetuning', METHOD, True, [1,2,4,5], 'fine-tuning spelling variant accepted.')],
 'Q28': [
  e('code evaluation datasets', TECH, True, [1,2,3,4]),
  e('mid-level hardness', LIMIT, True, [2,3]),
  e('HumanEval', NAME, True, []),
  e('MBPP', NAME, True, []),
  e('code_contests', NAME, True, []),
  e('harder than HumanEval and MBPP', LIMIT, True, []),
  e('easier than code_contests', LIMIT, True, [])],
 'Q29': [
  e('llms', NAME, False, [2,4]),
  e('math prove', TECH, True, [3], 'Source wording preserved; mathematical proof is the reviewed equivalent.'),
  e('IMO', NAME, True, [2,4,5]),
  e('IMO level math problems', LIMIT, True, [2,4,5]),
  e('teaching', TECH, False, [1,3])],
 'Q30': [
  e('test time training', METHOD, True, [1,2,3,4,5]),
  e('LLM', NAME, False, [2,4,5])],
 'Q31': [
  e('DPO', NAME, True, [1,2,3,4,5]),
  e('large-scale', LIMIT, True, [2,3,4,5]),
  e('vision-language models', METHOD, True, [1,2,3,4,5])],
 'Q32': [
  e('neural network', METHOD, True, [1,2,3,4,5]),
  e('quantum Monte Carlo', METHOD, True, [1,2,3,4,5]),
  e('cutting edge', LIMIT, False, [3,5], 'Recent advancements/state-of-the-art preserve the soft recency/novelty preference; no date invented.')],
 'Q33': [
  e('textual adversarial examples', TECH, True, [1,2,3], 'q4/q5 adversarial examples drop textual.'),
  e('machine translation', TECH, True, [1,2,3,4,5]),
  e('popular', LIMIT, False, [], 'state-of-the-art is not the same as popularity.')],
 'Q34': [
  e('3d scene understanding', TECH, True, [1,4,5], 'q2/q3 3D modifies the models but scene understanding is not explicitly stated as 3D.'),
  e('3D AIGC foundation models', METHOD, True, [2,3], 'q1 omits AIGC; q4/q5 omit foundation.'),
  e('AIGC', NAME, True, [2,3,4,5])],
 'Q35': [
  e('LLM', NAME, False, [1,3,4,5]),
  e('quantized pretraining', METHOD, True, [1,3,4,5], 'quantization in pretraining accepted; q2 quantitative is not quantized.')],
 'Q36': [
  e('identity preservation', TECH, True, [1,2,3,4,5]),
  e('video generation', TECH, True, [1,2,3,4], 'q5 video editing is a different task.')],
 'Q37': [
  e('LLM agents', METHOD, True, [3,4], 'q1/q5 omit large; q2 LLM-based drops agents.'),
  e('schedule planning', TECH, True, [1,2,3,4,5])],
 'Q38': [
  e('image encoding distributions', TECH, True, [1,2,4,5], 'q4 encoding techniques and their distribution preserves the phrase relation; q3 probabilistic compression is narrower/different.')],
 'Q39': [
  e('synthetic data', TECH, True, [1,4,5]),
  e('large language models', METHOD, False, [1,5]),
  e('automatically generate', LIMIT, True, [3]),
  e('large-scale', LIMIT, True, []),
  e('high-quality', LIMIT, True, [3]),
  e('diverse', LIMIT, True, [3,5]),
  e('difficult', LIMIT, True, []),
  e('valuable', LIMIT, True, [2]),
  e('long thought data', TECH, True, [2])],
 'Q40': [
  e('Quantization-Aware Training', METHOD, True, [1,2,3,4,5]),
  e('QAT', NAME, True, [1,2,3,4,5], 'The full form is explicitly defined in the original question; semantic retention counts it, strict acronym surface coverage is separately zero.'),
  e('low-bit weights', LIMIT, True, [3]),
  e('better representations', LIMIT, True, [], 'Representations/impact without better drops the comparative benefit.')],
 'Q41': [
  e('synthesis data', TECH, True, [1,2,3,4,5], 'synthetic data accepted as the wording variant.'),
  e('sft', NAME, True, [1,3], 'soft target data in q2/q4 is not credited as SFT.'),
  e('scaling up', LIMIT, True, [1,2,3,4,5])],
 'Q42': [
  e('select frames', TECH, True, [1,2,4,5], 'frame selection/sampling accepted; q3 temporal sampling is broader and does not explicitly specify frames.'),
  e('video understanding', TECH, True, [1,2,4], 'q3 representation learning and q5 summary generation are not the same task.')],
 'Q43': [
  e('AI for Science', TECH, True, [4], 'AI in scientific research is credited; protein-specific applications alone do not preserve the broad domain phrase.'),
  e('protein design', TECH, True, [1,3,5]),
  e('DPO', NAME, True, [2]),
  e('antibody design', TECH, True, [2]),
  e('DPO of antibody design', LIMIT, True, [2])],
 'Q44': [
  e('Crypto-based Private Learning', METHOD, True, [1,2,3,5], 'Cryptographic/encryption private-learning paraphrases credited. q4 homomorphic encryption is an unsupported specific narrowing, not credited as the whole broad phrase.'),
  e('privacy-preserving machine learning', TECH, True, [2,3,5], 'private machine learning in q2 accepted. q1/q4 private learning plus machine learning is less explicit about their relation.')],
 'Q45': [
  e('controllability', TECH, True, [1,2,3,4,5], 'control aspects/controlling accepted as direct task paraphrases.'),
  e('video generation', TECH, True, [1,2,3,4,5], 'video production in this control context credited; borderline convention is explicit.')],
 'Q46': [
  e('robot decision making', TECH, True, [1,3,4,5]),
  e('task planning', TECH, True, [2]),
  e('datasets', TECH, False, [3,4]),
  e('benchmarks', TECH, False, [3,5])],
 'Q47': [
  e('LLM agents', METHOD, True, [1,2,3,4,5]),
  e('evaluated', TECH, False, [1,3,4,5]),
  e('benchmarked', TECH, False, [2,4]),
  e('financial tasks', TECH, True, [1,2,3,4,5]),
  e('I am referring to agents', LIMIT, True, [1,2,3,4,5], 'Explicit agent emphasis retained; overlapping element counted transparently.')],
 'Q48': [
  e('large language models', METHOD, False, [1,3,5], 'q2 language models omit large; q4 GPT-3 adds a specific model instead of preserving the general LLM class.'),
  e('mining factors', TECH, True, []),
  e('stock exchange analysis', TECH, True, [1,3,5], 'stock market analysis in q1 accepted; prediction/trend analysis in q2/q4 is narrower/different.')],
 'Q49': [
  e('large vision-language models', METHOD, True, [2,4], 'q3 multimodal is broader; q5 omits large.'),
  e('agents', METHOD, True, [2,5]),
  e('automatically play', LIMIT, True, [1,3,4]),
  e('PC games', TECH, True, [1,3,4])],
}
