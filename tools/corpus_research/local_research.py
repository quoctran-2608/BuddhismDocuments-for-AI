"""Use the existing D store for a real local, pending-review research workflow."""
from __future__ import annotations

import json
from pathlib import Path
import uuid

from .claims import make_claim, synthesis_item
from .counterevidence import make_counterevidence_plan
from .research_run import safe_json
from .research_store import ResearchStore

PENDING_REVIEW = 'Semantic claim/counterevidence assessment has not been authenticated; no Research publication is authorized.'
SAMPLE_SCOPE = 'Only the declared indexed profile and executed queries were checked; unindexed passages and other traditions remain unchecked.'


class LocalResearch:
    def __init__(self, host, path):
        self.host, self.path = host, Path(path).resolve()
        self.check_output_path(self.path)
        self.store = ResearchStore(self.path,context_reader=host.context_reader,
            evidence_reader=host.evidence_reader,assessment_reader=host.assessment_reader,
            search_reader=host.search_reader,dependency_reader=host.dependency_reader)

    def check_output_path(self, path):
        selected = Path(path).resolve()
        if selected == self.host.db:
            raise ValueError('corpus index cannot be used as an output/research store')
        for mapping in self.host.contract.values():
            for root in (self.host.root,self.host.source_root):
                if selected.is_relative_to((root/mapping['repo_path']).resolve()):
                    raise ValueError('outputs must remain outside immutable source repositories')

    def prepare(self, run_id):
        run = self.store.get_run(run_id)
        self.host.restore_locators(run)
        return run

    def create(self, *, run_id, question, queries, corpora, limit=3, counter_queries=None):
        if type(limit) is not int or not 1 <= limit <= self.host.max_candidates:
            raise ValueError('research candidate bound exceeds host policy')
        if not queries or not all(isinstance(q,str) and q.strip() for q in queries):
            raise ValueError('nonempty retrieval queries required')
        if counter_queries is not None and (not counter_queries or not all(isinstance(q,str) and q.strip() for q in counter_queries)):
            raise ValueError('counter queries must be nonempty strings')
        scope = self.host.scope(corpora)
        run = self.store.create_run(dict(run_id=run_id,question=question,mode='research',scope=scope,
            queries=queries,search_hypotheses=queries,limitations=[SAMPLE_SCOPE,PENDING_REVIEW]))
        observations, checked, seen = [], [], set()
        for query in queries:
            for corpus in corpora:
                result = self.host.retrieve('search',query,corpus=corpus,limit=limit)
                observations.append({'query':query,'corpus':corpus,'result':result})
                for hit in result['results']:
                    verified = self.host.verify_pointer(self.host.pointer(hit),run_id=run_id,retrieval_query=query)
                    checked.append(verified)
                    record = verified.get('evidence')
                    if verified['status']!='VERIFIED' or record['evidence_id'] in seen:
                        continue
                    seen.add(record['evidence_id'])
                    # This is a proposed, narrowly worded quotation observation,
                    # not an approved scholarly conclusion or AI assessment.
                    claim = make_claim(dict(claim_id='c-'+uuid.uuid4().hex,run_id=run_id,
                        text=f"Đoạn {record['work_id']}/{record['segment_id']} có câu trích: {record['quotation']}",
                        claim_type='textual',supporting_evidence_ids=[record['evidence_id']],
                        limitations=list(dict.fromkeys(record['limitations']+[SAMPLE_SCOPE,PENDING_REVIEW])),
                        presentation={'certainty':'tentative','quotations':[{'evidence_id':record['evidence_id'],
                            'text':record['quotation'],'kind':'direct','text_role':record['text_role'],'witness':record['witness']}]}))
                    run = self.store.append_claim(run_id,claim,expected_version=run['version'])
        requests = []
        for claim in run['claims']:
            steps = [dict(step_id=f's-{i}-{j}',direction='other_witness',operation='search',query=query,
                          corpus=corpus,target_id=None)
                     for i,corpus in enumerate(corpora) for j,query in enumerate(counter_queries or queries)]
            plan = make_counterevidence_plan(claim,search_id='s-'+uuid.uuid4().hex,scope=scope,steps=steps,
                unchecked_scope=[SAMPLE_SCOPE,'Lexical directions were executed; semantic adequacy/findings await an authenticated reviewer.'])
            self.host.register_plan(plan)
            requests.append(dict(claim_id=claim['claim_id'],plan=plan,review_id=None))
        # Keep genuine retrieval output as immutable audit DATA beside D. Never
        # read an artifact back as a source/assessment/search capability.
        artifact_dir = self.path.parent/'artifacts'
        artifact = artifact_dir/(uuid.uuid4().hex+'.json')
        self.check_output_path(artifact)
        artifact_dir.mkdir(parents=True,exist_ok=True)
        data = {'retrieval':observations,'initial_verification':checked,'publication_authorized':False}
        safe_json(data)
        with artifact.open('x',encoding='utf-8') as handle:
            json.dump(data,handle,ensure_ascii=False,indent=2)
        run = self.store.update_draft(run_id,{'answer_artifact':'artifacts/'+artifact.name},expected_version=run['version'])
        run = self.store.capture(run_id,expected_version=run['version'],review_ids={},counter_requests=requests)
        return {'run':run,'publication_authorized':False,'limitations':run['limitations'],
                'retrieval_artifact':str(artifact),'metrics':dict(self.host.metrics)}

    def capture(self, run_id, *, expected_version, review_ids=None, counter_requests=None):
        self.prepare(run_id)
        for request in counter_requests or []:
            self.host.register_plan(request['plan'])
        return self.store.capture(run_id,expected_version=expected_version,review_ids=review_ids or {},counter_requests=counter_requests)

    def finalize(self, run_id, *, expected_version, review_ids=None):
        self.prepare(run_id)
        return self.store.finalize(run_id,expected_version=expected_version,review_ids=review_ids or {})

    def publication_check(self, run_id, *, expected_version, review_ids=None):
        run = self.prepare(run_id)
        items = [synthesis_item(claim) for claim in run['claims'] if claim['claim_id'] not in run['superseded_claim_ids']]
        return self.store.check_publication(run_id,items=items,expected_version=expected_version,review_ids=review_ids or {})
