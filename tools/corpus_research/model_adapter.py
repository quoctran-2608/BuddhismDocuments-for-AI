"""Host-configured JSON subprocess transport. No provider, tools or approval API.

The command is trusted executable configuration, never supplied by a source or
model response. The host owns data-use authorization and command isolation.
"""
from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import tempfile
import time

from .research_run import safe_json


def json_bytes(value):
    safe_json(value)
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True)+'\n').encode('utf-8')


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    value = json.loads(raw, object_pairs_hook=pairs)
    safe_json(value)
    return value


class ModelError(ValueError):
    pass


def model_from_config(config):
    allowed={'command','model_id','model_version','mode','data_policy','timeout','max_context_bytes','max_output_bytes'}
    if not isinstance(config,dict) or set(config)-allowed or not {'command','model_id','model_version'}<=set(config):
        raise ValueError('invalid trusted host model config')
    return CommandModel(**config)


class CommandModel:
    """Two stateless calls, bounded UTF-8 context/output, wall timeout, no shell.

    A configured command receives one request on stdin and emits one JSON object.
    FIXTURE is always labeled MODEL_INFERENCE_NOT_EXECUTED. MODEL indicates only
    a host-declared live adapter, not proof of provider identity or correctness.
    """
    def __init__(self, command, *, model_id, model_version, mode='MODEL',
                 data_policy='LOCAL_ONLY', timeout=30, max_context_bytes=65536,
                 max_output_bytes=32768):
        if not isinstance(command,list) or not command or not all(isinstance(s,str) and s for s in command):
            raise ValueError('host command must be a nonempty argv list')
        if not all(isinstance(s,str) and s.strip() for s in (model_id,model_version)):
            raise ValueError('host model identity/version required')
        if mode not in ('MODEL','FIXTURE') or data_policy not in ('LOCAL_ONLY','AUTHORIZED_REMOTE'):
            raise ValueError('invalid host inference/data policy')
        if type(timeout) not in (int,float) or not 0 < timeout <= 60:
            raise ValueError('timeout must be 0..60 seconds')
        for bound in (max_context_bytes,max_output_bytes):
            if type(bound) is not int or not 1024 <= bound <= 1048576:
                raise ValueError('context/output bounds must be 1024..1048576 bytes')
        self.command = list(command)
        self.timeout, self.max_context_bytes, self.max_output_bytes = timeout,max_context_bytes,max_output_bytes
        self.metadata = dict(model_id=model_id,model_version=model_version,mode=mode,data_policy=data_policy,
            command_sha256=hashlib.sha256(json_bytes(command)).hexdigest(),timeout_seconds=timeout,
            max_context_bytes=max_context_bytes,max_output_bytes=max_output_bytes,max_calls=2)
        self.calls = []

    def generate(self, request):
        if len(self.calls) >= 2:
            raise ModelError('MODEL_CALL_BUDGET_EXCEEDED')
        raw = json_bytes(request)
        if len(raw) > self.max_context_bytes:
            raise ModelError('MODEL_CONTEXT_BOUND_EXCEEDED: no silent truncation')
        record = dict(stage=request['stage'],input_sha256=hashlib.sha256(raw).hexdigest(),
                      input_bytes=len(raw),status='STARTED')
        self.calls.append(record)
        started = time.perf_counter()
        try:
            # Files avoid unbounded in-memory communicate() buffers. Poll sizes
            # during execution, terminate on timeout/output overflow.
            with tempfile.TemporaryFile() as stdin, tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
                stdin.write(raw); stdin.seek(0)
                proc = subprocess.Popen(self.command,stdin=stdin,stdout=stdout,stderr=stderr,
                    shell=False,start_new_session=os.name=='posix')
                try:
                    while True:
                        if max(os.fstat(stdout.fileno()).st_size,os.fstat(stderr.fileno()).st_size) > self.max_output_bytes:
                            raise ModelError('MODEL_OUTPUT_BOUND_EXCEEDED')
                        remaining = self.timeout-(time.perf_counter()-started)
                        if remaining <= 0:
                            raise ModelError('MODEL_TIMEOUT')
                        try:
                            proc.wait(timeout=min(0.02,remaining)); break
                        except subprocess.TimeoutExpired:
                            pass
                finally:
                    if proc.poll() is None:
                        if os.name=='posix':
                            os.killpg(proc.pid,signal.SIGKILL)
                        else:
                            proc.kill()
                        proc.wait()
                stdout.seek(0); stderr.seek(0)
                output, errors = stdout.read(self.max_output_bytes+1),stderr.read(self.max_output_bytes+1)
                record.update(exit_code=proc.returncode,output_sha256=hashlib.sha256(output).hexdigest(),
                              stderr_sha256=hashlib.sha256(errors).hexdigest(),output_bytes=len(output))
                if max(len(output),len(errors)) > self.max_output_bytes:
                    raise ModelError('MODEL_OUTPUT_BOUND_EXCEEDED')
                if proc.returncode:
                    raise ModelError('MODEL_PROCESS_FAILED')
                result = strict_json(output.decode('utf-8'))
                record['status'] = 'RETURNED_JSON'
                return result
        except (ValueError,OSError,UnicodeError,RecursionError) as exc:
            record['status'] = 'FAILED'
            raise ModelError(str(exc)) from exc
        finally:
            record['elapsed_seconds'] = time.perf_counter()-started
