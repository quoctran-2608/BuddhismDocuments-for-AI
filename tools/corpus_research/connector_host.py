"""Portable contract adapter for existing production locator + pinned source.

No network, SQLite, shell, replacement search engine or semantic approval.
The application wires authenticated tool readers and pins OUTSIDE proposal JSON.
Test readers prove contract behavior only, not a real Work/plugin session.
"""
import copy
import hashlib
import json
from xml.parsers.expat import ExpatError

from .model import normalize
from .source_resolvers import contract_for, resolve_source, SPAN_LIMITATION
from .verification import (_path, _sha, _read_capability, evidence_gate,
                           git_blob_sha, make_evidence_record)


class ConnectorHost:
    def __init__(self, source_contract, remote_config, *, locator_commit,
                 source_fetch=None, locator_fetch=None, review_reader=None):
        self.contract = copy.deepcopy(source_contract)
        self.remote = copy.deepcopy(remote_config)
        if (self.remote.get('mode')!='pointer_production_v1' or not _path(self.remote.get('root_path'))
                or not isinstance(self.remote.get('repository'),str) or not _sha(locator_commit)):
            raise ValueError('host must pin the configured production locator')
        self.locator_commit = locator_commit
        self.source_fetch,self.locator_fetch,self.review_reader = source_fetch,locator_fetch,review_reader

    def source_reader(self, request):
        mapping = self.contract.get(request.get('corpus'),{})
        if (request.get('repository')!=mapping.get('repository') or request.get('source_sha')!=mapping.get('source_sha')
                or not _sha(request.get('source_sha')) or not _path(request.get('source_path'))):
            return {}
        identity = {key:request[key] for key in ('repository','source_sha','source_path')}
        fetched = _read_capability(self.source_fetch,identity)
        content,blob = fetched.get('content'),fetched.get('source_blob_sha')
        if (any(fetched.get(key)!=value for key,value in identity.items()) or not isinstance(content,str)
                or not _sha(blob) or git_blob_sha(content.encode('utf-8'))!=blob):
            return {}
        try:
            resolved = resolve_source(content,request['corpus'],request['source_path'],request)
        except (ValueError,KeyError,TypeError,ExpatError):
            return {}
        return {**identity,'content':content,'source_blob_sha':blob,'blob_check_required':True,**resolved}

    def verify_pointer(self, pointer, *, evidence_id, quotation=None, run_id=None):
        request = {key:pointer.get(key) for key in ('corpus','repository','source_sha','source_path',
                                                   'work_id','segment_id','sequence_no')}
        opened = self.source_reader(request)
        if quotation is None and opened.get('excerpt_range'):
            a,b = opened['excerpt_range']
            quotation = opened['content'][a:b]
        # Production v1 pointers omit language. Complete that field from the
        # independently resolved source, never from a self-declared flag.
        # Preserve a supplied value so disagreement remains a gate failure.
        pointer = copy.deepcopy(pointer)
        if pointer.get('language') is None:
            pointer['language'] = opened.get('location',{}).get('language')
        if pointer.get('source_blob_sha') is None:
            pointer['source_blob_sha'] = opened.get('source_blob_sha')
        candidate = make_evidence_record(pointer,contract_for(self.contract,pointer.get('corpus'),pointer.get('source_path')),
            evidence_id=evidence_id,quotation=quotation,run_id=run_id)
        candidate['limitations'] = [SPAN_LIMITATION]
        return evidence_gate(candidate,contract_for(self.contract,pointer.get('corpus'),pointer.get('source_path')),
            opened,source_reader=self.source_reader,review_reader=self.review_reader,
            mode='research' if run_id else 'quick')

    def lookup(self, namespace, key):
        if namespace not in ('terms/latin','ids') or not isinstance(key,str) or not key.strip():
            raise ValueError('production supports terms/latin and exact ids only')
        key = normalize(key) if namespace=='terms/latin' else key
        if namespace=='terms/latin' and any('\u3400'<=char<='\u9fff' for char in key):
            return {'status':'UNVERIFIED','pointers':[],'limitations':['Production has no arbitrary CJK term namespace.']}
        bucket = hashlib.sha256(key.encode('utf-8')).hexdigest()[:2]
        path = self.remote['root_path']+'/locator/'+namespace+'/'+bucket+'/part-000001.jsonl'
        identity = dict(repository=self.remote['repository'],source_sha=self.locator_commit,source_path=path)
        fetched = _read_capability(self.locator_fetch,identity)
        if any(fetched.get(k)!=v for k,v in identity.items()) or not isinstance(fetched.get('content'),str):
            return {'status':'UNVERIFIED','pointers':[],'limitations':['Pinned production locator unavailable.']}
        try:
            rows = [json.loads(line) for line in fetched['content'].splitlines() if line.strip()]
            matches = [row for row in rows if row.get('key')==key]
            if len(matches)!=1 or not isinstance(matches[0].get('pointers'),list):
                raise ValueError('exact production key unavailable or ambiguous')
        except (ValueError,TypeError,AttributeError):
            return {'status':'UNVERIFIED','pointers':[],'limitations':['Exact production key unavailable or malformed shard.']}
        return {'status':'CANDIDATE','key':key,'locator':identity,'pointers':copy.deepcopy(matches[0]['pointers']),
                'limitations':['Pointers require independent pinned source verification.']}
