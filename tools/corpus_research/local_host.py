"""Offline host adapters after retrieval 1.0; no built-in semantic approval.

The application selects roots, index, pins and executable readers. Proposals,
reports and saved A snapshots never select a reader or grant approval. Stored
evidence is used only as a locator/quotation to run A again on pinned Git bytes.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import time
from xml.parsers.expat import ExpatError

from . import retrieval
from .index import connect_readonly, state_parser_version
from .source_resolvers import contract_for, resolve_source, SPAN_LIMITATION
from .verification import (_path, _sha, evidence_gate, github_source_path,
                           make_evidence_record, read_local_source)


def source_contract(root):
    """Host configuration, not a field in research/approval JSON."""
    root = Path(root)
    pins = {item['rel_dest']:item['commit_sha'] for item in json.loads((root/'manifest.json').read_text(encoding='utf-8'))}
    sources = json.loads((root/'config/corpus-sources.json').read_text(encoding='utf-8'))['sources']
    result = {}
    for source in sources:
        path, sha = source['repo'], pins.get(source['repo'])
        if not _path(path) or not _sha(sha) or source['corpus'] in result:
            raise ValueError('invalid/ambiguous host source configuration')
        result[source['corpus']] = dict(repo_path=path,repository=source['github_repository'],
            source_sha=sha,evidence_class=source['evidence_class'],blob_check_required=True)
    return result


def source_request(candidate):
    return {key:candidate.get(key) for key in ('corpus','repository','source_sha','source_path',
                                              'work_id','segment_id','sequence_no')}


class LocalHost:
    def __init__(self, root, db, *, source_root=None, assessment_reader=None,
                 review_reader=None, dependency_reader=None, max_candidates=20):
        self.root, self.db = Path(root).resolve(), Path(db).resolve()
        self.source_root = Path(source_root or root).resolve()
        self.contract = source_contract(self.root)
        if type(max_candidates) is not int or not 1 <= max_candidates <= 100:
            raise ValueError('host candidate bound must be 1..100')
        self.max_candidates = max_candidates
        self.assessment_reader, self.review_reader = assessment_reader, review_reader
        self.dependency_reader = dependency_reader
        self.recipes, self.plans, self.receipts = {}, {}, {}
        self.reset_metrics()
        self.index_state = self._index_state()

    def reset_metrics(self):
        self.metrics = dict(retrieval_seconds=0.0,source_seconds=0.0,verification_seconds=0.0,
                            source_reads=0,retrieval_calls=0)

    def _index_state(self):
        wal = Path(str(self.db)+'-wal')
        if wal.exists() and wal.stat().st_size:
            raise ValueError('checkpoint the corpus index before using the immutable retrieval reader')
        con = connect_readonly(self.db)
        try:
            rows = [dict(row) for row in con.execute('SELECT * FROM source_state ORDER BY corpus')]
            if not rows:
                raise ValueError('index has no pinned source state')
            for row in rows:
                mapping = self.contract.get(row['corpus'])
                if not mapping or row['source_sha'] != mapping['source_sha'] or row['repo_path'] != mapping['repo_path']:
                    raise ValueError('index source revisions differ from host pins')
            return rows
        finally:
            con.close()

    def context_reader(self, run_id):
        commit = subprocess.check_output(['git','-C',str(self.root),'rev-parse','HEAD'],text=True).strip()
        return dict(main_repository='quoctran-2608/BuddhismDocuments-for-AI',main_repository_commit=commit,
            remote_repository=None,remote_repository_commit=None,remote_root=None,environment='local',
            source_revisions=[dict(corpus=c,repository=m['repository'],source_sha=m['source_sha']) for c,m in self.contract.items()],
            model_identifier=None,verification_config={'adapter':'local-v1','semantic_approval_configured':callable(self.assessment_reader)})

    def scope(self, corpora):
        state = {row['corpus']:row for row in self._index_state()}
        if not corpora or len(set(corpora)) != len(corpora) or any(c not in state for c in corpora):
            raise ValueError('scope must name distinct indexed corpora')
        profiles = {row['parser_version'].rsplit(':',1)[-1] for row in state.values() if row['corpus'] in corpora}
        if len(profiles) != 1:
            raise ValueError('mixed index profiles require a separate explicit host scope policy')
        profile = profiles.pop()
        if any(state[c]['parser_version'] != state_parser_version(c,profile) for c in corpora):
            raise ValueError('index parser/profile is stale')
        return {'corpora':list(corpora),'source_revisions':[dict(corpus=c,repository=self.contract[c]['repository'],
                source_sha=self.contract[c]['source_sha']) for c in corpora],
                'constraints':['indexed_profile:'+profile]}

    def source_reader(self, request, *, quotation=None, retrieval_query=None):
        started = time.perf_counter()
        try:
            if set(request) != set(source_request({})):
                return {}
            self.metrics['source_reads'] += 1
            opened = read_local_source(self.source_root,request,self.contract)
            if not opened.get('content'):
                return opened
            resolved = resolve_source(opened['content'],request['corpus'],request['source_path'],request,
                                      quotation=quotation,retrieval_query=retrieval_query)
            return {**opened,**resolved}
        except (ValueError,KeyError,TypeError,ExpatError):
            return {'error':'source format/location or matching contiguous span is unavailable or unsupported'}
        finally:
            self.metrics['source_seconds'] += time.perf_counter()-started

    def pointer(self, row):
        corpus = row.get('corpus')
        mapping = self.contract.get(corpus,{})
        return {key:copy.deepcopy(row.get(key)) for key in ('corpus','source_sha','work_id','segment_id',
                'sequence_no','language','text_role','witness','evidence_class','relation_ids','match_reasons')} | {
                'repository':mapping.get('repository'),
                'source_path':github_source_path(row['source_path'],mapping['repo_path']),
                'indexed_source_path':row['source_path'],'source_blob_sha':None}

    def verify_pointer(self, pointer, *, quotation=None, run_id=None, retrieval_query=None):
        contract = contract_for(self.contract,pointer.get('corpus'),pointer.get('source_path'))
        opened = self.source_reader(source_request(pointer),quotation=quotation,retrieval_query=retrieval_query)
        pointer = copy.deepcopy(pointer)
        if pointer.get('source_blob_sha') is None:
            pointer['source_blob_sha'] = opened.get('source_blob_sha')
        if quotation is None and opened.get('excerpt_range'):
            start,end = opened['excerpt_range']
            quotation = opened['content'][start:end]
        identity = {key:pointer.get(key) for key in ('corpus','repository','source_sha','source_path',
                    'work_id','segment_id','sequence_no')}
        eid = 'e-'+hashlib.sha256(json.dumps([identity,run_id,quotation,retrieval_query,
            pointer.get('match_reasons'),pointer.get('relation_ids')],sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:24]
        candidate = make_evidence_record(pointer,contract,evidence_id=eid,quotation=quotation,run_id=run_id)
        candidate['retrieval_query'] = retrieval_query
        candidate['limitations'] = [SPAN_LIMITATION]
        return self._gate(candidate,opened,contract,register=True)

    def _gate(self, candidate, opened, contract, *, register=False):
        before_source = self.metrics['source_seconds']
        started = time.perf_counter()
        # Bind the selection hint in host code, outside A's request/proposal.
        # The second read still derives all ranges from original pinned bytes.
        reader = lambda request: self.source_reader(request,quotation=candidate['quotation'])
        result = evidence_gate(candidate,contract,opened,source_reader=reader,review_reader=self.review_reader,
                               mode='research' if candidate['run_id'] else 'quick')
        self.metrics['verification_seconds'] += max(0.0,time.perf_counter()-started-(self.metrics['source_seconds']-before_source))
        if opened.get('error'):
            result['limitations'] = [opened['error']]
        if register and result['status']=='VERIFIED':
            old = self.recipes.get(candidate['evidence_id'])
            if old is not None and old != candidate:
                raise ValueError('evidence ID cannot be rebound')
            self.recipes[candidate['evidence_id']] = copy.deepcopy(candidate)
        return result

    def verify_record(self, record_id, *, quotation=None, run_id=None, retrieval_query=None):
        bundle = self.retrieve('evidence',record_id)
        if not bundle.get('found'):
            return {'status':'UNVERIFIED','evidence':None,'limitations':['Indexed record unavailable.']}
        return self.verify_pointer(self.pointer(bundle['record']),quotation=quotation,run_id=run_id,retrieval_query=retrieval_query)

    def evidence_reader(self, evidence_id):
        candidate = self.recipes.get(evidence_id)
        if candidate is None:
            return {}
        candidate = copy.deepcopy(candidate)
        opened = self.source_reader(source_request(candidate),quotation=candidate['quotation'])
        return self._gate(candidate,opened,contract_for(self.contract,candidate['corpus'],candidate['source_path']))

    def restore_locators(self, run):
        # Rebuild proposals, NOT gate envelopes, from the audit snapshot.
        for record in run['evidence']:
            contract = contract_for(self.contract,record['corpus'],record['source_path'])
            candidate = make_evidence_record(record,contract,evidence_id=record['evidence_id'],
                quotation=record['quotation'],run_id=record['run_id'])
            self.recipes[record['evidence_id']] = candidate
        for item in run['counter_requests']:
            self.register_plan(item['plan'])

    def retrieve(self, operation, *args, **kwargs):
        if operation not in ('search','context','evidence','work','parallels','variants','resolve','compare','provenance'):
            raise ValueError('unsupported retrieval operation')
        started = time.perf_counter()
        try:
            self.metrics['retrieval_calls'] += 1
            return getattr(retrieval,operation)(self.db,*args,**kwargs)
        finally:
            self.metrics['retrieval_seconds'] += time.perf_counter()-started

    def quick(self, query, *, corpus=None, language=None, limit=3):
        if type(limit) is not int or not 1 <= limit <= self.max_candidates:
            raise ValueError('Quick limit exceeds the host bound')
        self.reset_metrics()
        started = time.perf_counter()
        hits = self.retrieve('search',query,limit=limit,corpus=corpus,language=language)
        checked = [self.verify_pointer(self.pointer(row),retrieval_query=query) for row in hits['results']]
        return {'mode':'quick','retrieval':hits,'verification':checked,
                'verified_evidence':[item['evidence'] for item in checked if item['status']=='VERIFIED'],
                'publication_authorized':False,'claim_assessment':'NOT_REQUESTED',
                'limitations':list(dict.fromkeys(hits['limitations']+[SPAN_LIMITATION])),
                'metrics':{**self.metrics,'total_seconds':time.perf_counter()-started}}

    def register_plan(self, plan):
        from .counterevidence import _plan
        proposed = _plan(plan)
        if proposed['scope'] != self.scope(proposed['scope']['corpora']):
            raise ValueError('plan must use the exact executable indexed scope')
        previous = self.plans.get(proposed['search_id'])
        if previous is not None and previous != proposed:
            raise ValueError('search ID cannot be rebound to a different plan')
        self.plans[proposed['search_id']] = proposed

    def search_reader(self, search_id):
        plan = self.plans.get(search_id)
        if plan is None or plan['scope'] != self.scope(plan['scope']['corpora']):
            return {}
        steps, raw = [], []
        for step in plan['steps']:
            receipt = dict(step_id=step['step_id'],status='not_run',complete=False,checked_scope=None,candidates=[],limitations=[])
            try:
                corpus, op = step['corpus'], step['operation']
                if op == 'search':
                    result = self.retrieve(op,step['query'],corpus=corpus,limit=self.max_candidates+1)
                    rows = result['results']
                elif op in ('evidence','context'):
                    target = int(step['target_id'])
                    target_bundle = self.retrieve('evidence',target)
                    if not target_bundle.get('found') or target_bundle['record']['corpus'] != corpus:
                        raise ValueError('target record is outside step corpus')
                    result = self.retrieve(op,target)
                    rows = [result['record']] if op == 'evidence' else result['context']
                else:
                    result = self.retrieve(op,step['target_id'])
                    rows = result.get('records',result.get('relations',result.get('variants',[])))
                    # Metadata/variant rows lack a textual A resolver here;
                    # retain the real raw result, never upgrade it to A.
                    if op in ('parallels','variants'):
                        receipt['limitations'].append('Metadata/variant source verification is not integrated.')
                raw.append({'step':copy.deepcopy(step),'result':copy.deepcopy(result)})
                if (len(rows)>self.max_candidates or op == 'resolve' and len(rows)>=100
                        or op in ('parallels','variants') and len(rows)>=500 or op=='work' and len(rows)>=100):
                    receipt['limitations'].append('Result bound reached; search coverage is incomplete.')
                if result.get('limitations'):
                    receipt['limitations'].extend(result['limitations'])
                receipt.update(status='executed',checked_scope={'corpora':[corpus],
                    'source_revisions':[r for r in plan['scope']['source_revisions'] if r['corpus']==corpus],
                    'constraints':copy.deepcopy(plan['scope']['constraints'])})
                for number,row in enumerate(rows[:self.max_candidates]):
                    if row['corpus'] != corpus:
                        continue
                    if op in ('parallels','variants'):
                        continue
                    # Work rows omit roles/language: resolve the ACTUAL hit by
                    # its record ID through evidence(), never from a chosen A ID.
                    bundle = self.retrieve('evidence',row['id'])
                    pointer = self.pointer(bundle['record'])
                    checked = self.verify_pointer(pointer,run_id=plan['claim']['run_id'],retrieval_query=step['query'])
                    if checked['status']=='VERIFIED':
                        # Enrich this actual hit only with its just-verified
                        # Git blob identity; keep C's exact pointer binding.
                        pointer['source_blob_sha'] = checked['evidence']['source_blob_sha']
                    receipt['candidates'].append({'candidate_id':f'{search_id}:{step["step_id"]}:{number}',
                        'evidence_id':checked['evidence']['evidence_id'] if checked['status']=='VERIFIED' else None,
                        'pointer':pointer})
                receipt['complete'] = not receipt['limitations']
            except (ValueError,KeyError,OSError,TypeError) as exc:
                receipt.update(status='failed',complete=False,checked_scope=None,candidates=[],limitations=[str(exc)])
            steps.append(receipt)
        response = {'search_id':search_id,'plan':{key:value for key,value in plan.items() if key!='status'},
                    'reviewer':'local-deterministic-executor','rationale':'Host allowlist executed bounded retrieval; semantic adequacy is not approved.',
                    'steps':steps}
        self.receipts[search_id] = {'response':copy.deepcopy(response),'operations':raw}
        return response
