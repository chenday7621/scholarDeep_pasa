"""Inspect only local model metadata and package metadata, never load weights."""
import importlib.metadata as metadata
import os
from pathlib import Path
import sys

from audit_common import HERE, SHARED_CODE, Guard, read, save, sha


def main():
    roots = [Path(p) for p in [
        '/home/chenyi/.cache/huggingface/hub', '/home/chenyi/.cache/torch',
        '/mnt/nvme3/chenyi/hf-cache/hub', '/mnt/nvme3/chenyi/cache/huggingface',
        '/mnt/nvme3/chenyi/pasa/checkpoints']]
    variables = ['HF_HOME', 'HUGGINGFACE_HUB_CACHE', 'TRANSFORMERS_CACHE', 'SENTENCE_TRANSFORMERS_HOME', 'TORCH_HOME']
    overrides = {k: os.environ.get(k) for k in variables}
    roots += [Path(v) for v in overrides.values() if v]
    config_paths, inventories = [], []
    for root in roots:
        configs = sorted(set(root.rglob('config.json')) | set(root.rglob('modules.json')) | set(root.rglob('sentence_bert_config.json'))) if root.exists() else []
        inventories.append({'root': str(root), 'exists': root.exists(), 'metadata_paths': list(map(str, configs))})
        config_paths += configs
    # Package metadata inspection does not import any of these packages.
    versions = {}
    for name in ['torch', 'transformers', 'sentence-transformers', 'scipy', 'numpy', 'scikit-learn']:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None
    guard = Guard(config_paths, [HERE / 'environment_audit.json'], [__file__, *SHARED_CODE])
    configs = []
    for path in config_paths:
        data = read(path)
        configs.append({'path': str(path), 'sha256': sha(path),
                        'architectures': data.get('architectures') if isinstance(data, dict) else None,
                        'model_type': data.get('model_type') if isinstance(data, dict) else None})
    assert len(configs) == 2 and all(c['architectures'] == ['Qwen2ForCausalLM'] for c in configs), 'Environment changed: re-inspect before proceeding.'
    save(HERE / 'environment_audit.json', {
        'python': sys.version, 'executable': sys.executable, 'cache_overrides': overrides,
        'checked_roots': inventories, 'model_metadata': configs, 'package_versions': versions,
        'semantic_embedding_status': 'unavailable_in_checked_project_and_user_caches',
        'reason': 'Only PaSa Crawler/Selector causal-LM checkpoints found; no sentence embedding checkpoint. No model is loaded or repurposed.',
        'model_loads': 0, 'model_calls': 0, 'network_requests': 0,
        'scope_limit': 'Checked project/user model locations, not other users or every system filesystem.',
        'access': guard.evidence(),
    })
    print('Local inspection: no embedding checkpoint; zero model loads/calls.')


if __name__ == '__main__':
    main()
