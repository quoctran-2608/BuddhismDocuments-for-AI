"""Opt-in Pilot 01 source-identity regressions against an EXISTING pinned index.

Set BCR_P01_DB and BCR_SOURCE_ROOT; never build/download/modify the pilot index.
These tests assert identity and source bytes, not semantic support of claims.
"""
import os
import json
from pathlib import Path
import tempfile
import unittest

from corpus_research.declared_sources import create_declared_run, verify_declared_source
from corpus_research.local_host import LocalHost
from corpus_research.local_research import LocalResearch
from corpus_research.retrieval import search

ROOT = Path(__file__).resolve().parents[1]
PIN = '0914c609e49215bb1473199929ee8a2996b423c4'


class PilotDeclaredSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.environ.get('BCR_P01_DB') or not os.environ.get('BCR_SOURCE_ROOT'):
            raise unittest.SkipTest('Set BCR_P01_DB and BCR_SOURCE_ROOT to existing pinned data; no download.')

    def setUp(self):
        self.host = LocalHost(ROOT, Path(os.environ['BCR_P01_DB']), source_root=Path(os.environ['BCR_SOURCE_ROOT']))
        self.assertEqual(self.host.contract['suttacentral-bilara']['source_sha'], PIN)

    def ref(self, work='sn36.21', segment='sn36.21:2.1'):
        division = work.rsplit('.', 1)[0]
        return dict(corpus='suttacentral-bilara', work_id=work,
                    source_path=f'root/pli/ms/sutta/sn/{division}/{work}_root-pli-ms.json',
                    source_sha=PIN, witness='root:root-pli-ms', segment_id=segment)

    def test_ac01_sn3621_individual_segment_inside_core_chunk(self):
        result = verify_declared_source(self.host, self.ref(), claim_id='AC01-C01')
        self.assertEqual(result['status'], 'VERIFIED', result)
        evidence = result['gate']['evidence']
        for key, value in self.ref().items():
            self.assertEqual(evidence[key], value)

    def test_ac01_default_lexical_remains_off_target_but_declared_is_exact(self):
        lexical = search(self.host.db, 'pubbekatahetu', corpus='suttacentral-bilara', limit=1)
        quick = self.host.quick('pubbekatahetu', corpus='suttacentral-bilara', limit=1)
        self.assertEqual(quick['retrieval'], lexical)
        self.assertNotEqual(lexical['results'][0]['work_id'], 'sn36.21')
        self.assertEqual(verify_declared_source(self.host, self.ref(), claim_id='AC01-C01')['status'], 'VERIFIED')

    def test_ac04_sn35145_and_sn35146_remain_distinct(self):
        records=[]
        for work in ('sn35.145','sn35.146'):
            result=verify_declared_source(self.host,self.ref(work,work+':0.2'),claim_id='AC04-C01')
            self.assertEqual(result['status'],'VERIFIED',result)
            records.append(result['gate']['evidence'])
        self.assertNotEqual(records[0]['work_id'],records[1]['work_id'])
        self.assertNotEqual(records[0]['source_path'],records[1]['source_path'])
        self.assertNotEqual(records[0]['source_blob_sha'],records[1]['source_blob_sha'])
        self.assertNotEqual(records[0]['quotation'],records[1]['quotation'])

    def test_ac04_cross_work_path_does_not_auto_renumber(self):
        ref=self.ref('sn35.145','sn35.145:0.2')
        ref['source_path']=self.ref('sn35.146')['source_path']
        self.assertEqual(verify_declared_source(self.host,ref,claim_id='AC04-C01')['reason'],'DECLARED_SOURCE_NOT_INDEXED')

    def test_actual_wrong_work_path_pin_witness_segment(self):
        for key,value in [('work_id','sn36.missing'),('source_path','root/absent.json'),
                          ('source_sha','0'*40),('witness','root:unknown'),('segment_id','sn36.21:999.999')]:
            with self.subTest(field=key):
                ref={**self.ref(),key:value}
                result=verify_declared_source(self.host,ref,claim_id='AC01-C01')
                self.assertNotEqual(result['status'],'VERIFIED',result)

    def test_actual_missing_source_repository(self):
        with tempfile.TemporaryDirectory() as empty:
            self.host.source_root=Path(empty)
            result=verify_declared_source(self.host,self.ref(),claim_id='AC01-C01')
            self.assertEqual(result['reason'],'SOURCE_OR_SEGMENT_UNAVAILABLE')

    def test_actual_multiple_witnesses_are_ambiguous(self):
        ref=dict(corpus='suttacentral-bilara',work_id='sn36.21')
        self.assertEqual(verify_declared_source(self.host,ref,claim_id='AC01-C01')['reason'],'AMBIGUOUS_DECLARED_SOURCE')

    def test_actual_claim_binding_and_publication_remain_pending(self):
        with tempfile.TemporaryDirectory() as output:
            research=LocalResearch(self.host,Path(output)/'research.sqlite3')
            # Software claim shell; never rewrite or approve the frozen pilot claim.
            result=create_declared_run(research,run_id='p01-ac01-regression',question='Source identity regression',
                claims=[dict(claim_id='AC01-C01',text='Declared SN 36.21 source identity only.',claim_type='textual')],
                source_references={'AC01-C01':[self.ref()]},corpora=['suttacentral-bilara'])
            self.assertEqual(result['declared_bindings'][0]['status'],'VERIFIED')
            self.assertFalse(result['run']['accepted_claim_ids'])
            pub=research.publication_check(result['run']['run_id'],expected_version=result['run']['version'])
            self.assertFalse(pub['publication_authorized'])

    def test_original_pilot_claim_text_is_preserved_in_new_pending_draft(self):
        path=os.environ.get('BCR_P01_CLAIMS')
        if not path:
            self.skipTest('Set BCR_P01_CLAIMS to the existing frozen atomic-claims-register.json.')
        raw=Path(path).read_bytes()
        original=next(c for c in json.loads(raw)['claims'] if c['claim_id']=='AC01-C01')
        with tempfile.TemporaryDirectory() as output:
            research=LocalResearch(self.host,Path(output)/'research.sqlite3')
            result=create_declared_run(research,run_id='original-ac01-text',question='Source binding only; semantic review pending.',
                claims=[dict(claim_id=original['claim_id'],text=original['statement_to_adjudicate'],claim_type='textual')],
                source_references={original['claim_id']:[self.ref()]},corpora=['suttacentral-bilara'])
            self.assertEqual(result['run']['claims'][0]['text'],original['statement_to_adjudicate'])
            self.assertFalse(result['run']['accepted_claim_ids'])
            self.assertEqual(result['declared_bindings'][0]['status'],'VERIFIED')
        self.assertEqual(Path(path).read_bytes(),raw)
