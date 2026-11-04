"""Optional real-source Pilot plumbing; FIXTURE is never semantic ground truth."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from corpus_research.claims import make_claim
from corpus_research.declared_sources import create_declared_run
from corpus_research.local_host import LocalHost
from corpus_research.local_research import LocalResearch
from corpus_research.model_adapter import CommandModel
from corpus_research.semantic_workflow import assess_research_claim

ROOT=Path(__file__).resolve().parents[1]
PIN='0914c609e49215bb1473199929ee8a2996b423c4'


class SemanticPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all(os.environ.get(k) for k in ('BCR_P01_DB','BCR_SOURCE_ROOT','BCR_P01_CLAIMS')):
            raise unittest.SkipTest('Existing Pilot DB, pinned sources and frozen claim register required; no download.')
        cls.path=Path(os.environ['BCR_P01_CLAIMS']);cls.original=cls.path.read_bytes()
        cls.claims={c['claim_id']:c for c in json.loads(cls.original)['claims']}

    @classmethod
    def tearDownClass(cls):
        assert cls.path.read_bytes()==cls.original

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.host=LocalHost(ROOT,Path(os.environ['BCR_P01_DB']),source_root=Path(os.environ['BCR_SOURCE_ROOT']))
        self.research=LocalResearch(self.host,Path(self.temp.name)/'research.sqlite3')

    def ref(self,work,segment,translation=False):
        division=work.rsplit('.',1)[0] if work.startswith('sn') else 'mn'
        prefix='translation/en/sujato' if translation else 'root/pli/ms'
        suffix='translation-en-sujato' if translation else 'root-pli-ms'
        return dict(corpus='suttacentral-bilara',work_id=work,source_path=f'{prefix}/sutta/'+('sn/' if work.startswith('sn') else '')+f'{division}/{work}_{suffix}.json',
            source_sha=PIN,witness=('translation:translation-en-sujato' if translation else 'root:root-pli-ms'),segment_id=segment)

    def trial(self,cid,refs,scenario=None):
        original=self.claims[cid]
        run=create_declared_run(self.research,run_id='pilot-'+cid,question='P0/2 pipeline regression; no semantic ground truth.',
            claims=[dict(claim_id=cid,text=original['statement_to_adjudicate'],claim_type='textual',limitations=['Native unit sample only; full citation-range coverage has not been established.'])],
            source_references={cid:refs},corpora=['suttacentral-bilara'])['run']
        model=CommandModel([sys.executable,str(ROOT/'tests/fixtures/semantic_model.py'),scenario],model_id='fixture-not-inference',model_version='1',mode='FIXTURE') if scenario else None
        result=assess_research_claim(self.research,run_id=run['run_id'],claim_id=cid,expected_version=run['version'],model=model)
        self.assertEqual(result['claim']['text'],original['statement_to_adjudicate'])
        self.assertEqual(result['inference_status'],'MODEL_INFERENCE_NOT_EXECUTED')
        self.assertFalse(self.research.store.get_run(run['run_id'])['accepted_claim_ids'])
        self.assertFalse(result['publication_authorized'])
        return result

    def test_ac01_real_source_no_configured_model_is_unresolved(self):
        result=self.trial('AC01-C01',[self.ref('sn36.21','sn36.21:2.1')])
        self.assertTrue(result['evidence'])
        self.assertEqual(result['evidence'][0]['work_id'],'sn36.21')
        self.assertEqual(result['synthesis']['assessment_status'],'UNRESOLVED')
        self.assertFalse(result['model_calls'])

    def test_ac01_scripted_challenge_demonstrates_lowering_not_detection(self):
        result=self.trial('AC01-C02',[self.ref('sn36.21','sn36.21:1.5')],'lower')
        self.assertEqual(result['support']['support_level'],'DIRECT')
        self.assertEqual(result['synthesis']['support_level'],'WEAK')

    def test_ac04_numbering_survives_both_model_stages(self):
        result=self.trial('AC04-C01',[self.ref(w,w+':0.2') for w in ('sn35.145','sn35.146')],'keep')
        for stage in ('support','challenge'):
            self.assertEqual({p['work_id'] for p in result[stage]['provenance']},{'sn35.145','sn35.146'})

    def test_ac05_conditional_claim_and_translation_scope_retained(self):
        result=self.trial('AC05-C01',[self.ref('mn135','mn135:5.1'),self.ref('mn135','mn135:5.1',True)],'limit')
        self.assertEqual(len(result['evidence']),2)
        self.assertIsNone(result['synthesis']['independent_source_count'])

    def test_ac08_competing_translation_remains_separate(self):
        result=self.trial('AC08-C01',[self.ref('sn36.21','sn36.21:3.6'),self.ref('sn36.21','sn36.21:3.6',True)],'issue')
        self.assertEqual(result['synthesis']['assessment_status'],'UNRESOLVED')
        self.assertEqual(len({e['witness'] for e in result['evidence']}),2)

    def test_ac11_temporal_claim_preserved_without_semantic_claim_of_success(self):
        result=self.trial('AC11-C01',[self.ref('mn135','mn135:5.1')],'lower')
        self.assertIn('Retain the explicit exception and time condition.',result['synthesis']['scope_limits'])

    def test_original_five_source_version_blockers_stay_unresolved(self):
        for cid in ('AC03-C02','AC07-C01','AC07-C02','AC07-C03','AC07-C04'):
            with self.subTest(claim_id=cid):
                claim=self.claims[cid]
                scope=self.host.scope(['suttacentral-bilara'])
                run=self.research.store.create_run(dict(run_id='blocked-'+cid,question='Preserve missing original source/version.',mode='research',scope=scope))
                run=self.research.store.append_claim(run['run_id'],make_claim(dict(claim_id=cid,run_id=run['run_id'],text=claim['statement_to_adjudicate'],claim_type='textual',limitations=['DECLARED_SOURCE_UNRESOLVED: original source/version unavailable; no substitute chosen.'])),expected_version=run['version'])
                result=assess_research_claim(self.research,run_id=run['run_id'],claim_id=cid,expected_version=run['version'])
                self.assertEqual(result['synthesis']['assessment_status'],'UNRESOLVED')
                self.assertFalse(result['model_calls'])
                self.assertFalse(result['evidence'])
