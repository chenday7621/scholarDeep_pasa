"""Standard-library-only I/O, original URL parser, and fail-closed offline guard."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import sysconfig

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SOURCE = Path('/home/chenyi/pasa-artifacts/PAGE2_SEARCH_PROBE_001-20260911')
PLAN = SOURCE / 'request_plan.json'
BASE = Path('/mnt/nvme3/chenyi/pasa/results/local-only-50q-baseline-seed42-20260910')
PARSER = re.compile(r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d+)')
BUDGETS = [25, 50, 75, 100, 150, 200, 'all']


def read(path):
    return json.loads(Path(path).read_text())


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def key(task):
    return f"Q{task['query_index']:02d}/s{task['query_sequence']:02d}"


def hits(record):
    return [dict(h, arxiv_id=m.group(1), organic_index=i)
            for i, h in enumerate(record['structured_response']['organic'])
            if (m := PARSER.search(h.get('link', '')))]


def check_response(record):
    assert record['http_status'] == 200
    assert hashlib.sha256(record['raw_response_text'].encode()).hexdigest() == record['raw_response_sha256']
    assert json.loads(record['raw_response_text']) == record['structured_response']


class Guard:
    """Exact data-file allowlist; no network, subprocess, model imports, or outside writes."""
    def __init__(self, reads, writes, code):
        self.allowed_reads = {str(Path(p).resolve()) for p in reads}
        self.allowed_writes = {str(Path(p).resolve()) for p in writes}
        self.code = {str(Path(p).resolve()) for p in code}
        self.stdlib = Path(sysconfig.get_path('stdlib')).resolve()
        self.read_paths = set()
        self.denied = []
        sys.addaudithook(self.audit)

    def allow(self, paths):
        self.allowed_reads.update(str(Path(p).resolve()) for p in paths)

    def audit(self, event, args):
        if event.startswith('socket.') or event in {'subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.fork', 'ctypes.dlopen'}:
            self.denied.append(event)
            raise PermissionError('Offline guard: ' + event)
        if event == 'import' and args[0].split('.')[0] in {
                'torch', 'transformers', 'requests', 'urllib', 'http', 'arxiv',
                'huggingface_hub', 'openai', 'subprocess', 'ctypes', 'evaluate'}:
            self.denied.append('import:' + args[0])
            raise PermissionError('Forbidden import: ' + args[0])
        if event != 'open' or isinstance(args[0], int):
            return
        path = str(Path(os.fsdecode(args[0])).resolve())
        mode, flags = args[1], args[2]
        writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
        if writing:
            allowed = path in self.allowed_writes
        else:
            library = Path(path).is_relative_to(self.stdlib) and 'site-packages' not in Path(path).parts and 'dist-packages' not in Path(path).parts
            allowed = path in self.allowed_reads or path in self.code or library
        if not allowed:
            self.denied.append(('write:' if writing else 'read:') + path)
            raise PermissionError('File not allowlisted: ' + path)
        if not writing:
            self.read_paths.add(path)

    def evidence(self):
        return {'read_paths': sorted(self.read_paths), 'denied_attempts': self.denied,
                'network_and_subprocess_blocked': True, 'model_imports_blocked': True}
