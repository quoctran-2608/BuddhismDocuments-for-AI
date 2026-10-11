"""Actual pinned corpora, not generated fixtures or scholarly quality oracles.

Run with all 13 existing checkouts; BCR_SOURCE_ROOT can select another local
checkout. Never fetch missing data. Exact bytes/roles are deterministic tests;
no independent expected interpretation or semantic approval is fabricated.
"""
from contextlib import closing
import copy
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest

from corpus_research import retrieval
from corpus_research.index import build_index
from corpus_research.local_host import LocalHost,source_request
from corpus_research.local_research import LocalResearch
from corpus_research.claims import final_claim_gate,make_claim
from corpus_research.counterevidence import make_counterevidence_plan,search_counterevidence

ROOT = Path(__file__).resolve().parents[1]
SOURCES = Path(os.environ.get('BCR_SOURCE_ROOT',ROOT))


class ActualCorpusIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
        for pin in cls.pins:
            repo = SOURCES/pin['rel_dest']
            try:
                head = subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],stderr=subprocess.DEVNULL,text=True).strip()
                blob = subprocess.check_output(['git','-C',str(repo),'rev-parse','--show-toplevel'],stderr=subprocess.DEVNULL,text=True).strip()
            except subprocess.CalledProcessError:
                raise unittest.SkipTest('Actual corpus checkouts unavailable; no download attempted.')
            if Path(blob).resolve()!=repo.resolve() or head!=pin['commit_sha']:
                raise unittest.SkipTest('All 13 exact source checkouts are required; no download attempted.')
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.temp.name)/'acceptance.sqlite3'
        build_index(SOURCES,cls.db,profile='acceptance')

    @classmethod
    def tearDownClass(cls):
        try:
            for pin in cls.pins:
                repo = SOURCES/pin['rel_dest']
                assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==pin['commit_sha']
                subprocess.run(['git','-C',str(repo),'diff','--quiet'],check=True)
        finally:
            cls.temp.cleanup()

    def setUp(self):
        self.host = LocalHost(ROOT,self.db,source_root=SOURCES)
        self.output = tempfile.TemporaryDirectory()
        self.addCleanup(self.output.cleanup)

    def row(self,corpus,role=None):
        with closing(sqlite3.connect(self.db)) as con:
            con.row_factory = sqlite3.Row
            sql = 'SELECT * FROM records WHERE corpus=?'
            args = [corpus]
            if role:
                sql += ' AND text_role=?'
                args.append(role)
            for row in con.execute(sql+' ORDER BY id LIMIT 40',args):
                item = dict(row)
                verified = self.host.verify_pointer(self.host.pointer(item))
                if verified['status']=='VERIFIED': return item,verified['evidence']
        self.fail('No verifiable actual source span for '+corpus+' '+str(role))

    def start(self):
        research = LocalResearch(self.host,Path(self.output.name)/'research.sqlite3')
        run = research.create(run_id='actual-run',question='Nguồn ghim ghi câu nào tại các đoạn tìm được?',
            queries=['sutaṃ'],corpora=['suttacentral-bilara'],counter_queries=['anicca'],limit=1)['run']
        self.assertTrue(run['evidence'])
        return research,run

    def test_actual_13_pins_and_index_state(self):
        self.assertEqual(len(self.host.contract),13)
        self.assertEqual(len(self.host.index_state),13)
        self.assertTrue(all(row['parser_version'].endswith(':acceptance') for row in self.host.index_state))

    def test_actual_bilara_root_matches_original_json_value(self):
        row,evidence = self.row('suttacentral-bilara','root_text')
        opened = self.host.source_reader(source_request(self.host.pointer(row)))
        content = json.loads(opened['content'])
        self.assertIn(evidence['quotation'],content.values())
        self.assertEqual(evidence['text_role'],'root_text')
        self.assertEqual(evidence['source_sha'],self.host.contract[row['corpus']]['source_sha'])

    def test_actual_bilara_translation_retains_language_witness(self):
        _,evidence = self.row('suttacentral-bilara','translation_main')
        self.assertEqual(evidence['language'],'en')
        self.assertTrue(evidence['witness'].startswith('translation:'))
        self.assertEqual(evidence['evidence_class'],'authoritative_structured')

    def test_actual_cbeta_exact_quote_and_one_word_change(self):
        row,evidence = self.row('cbeta-tei','root_text')
        self.assertEqual(self.host.verify_record(row['id'],quotation=evidence['quotation'])['status'],'VERIFIED')
        self.assertEqual(self.host.verify_record(row['id'],quotation=evidence['quotation']+'偽') ['status'],'REJECTED')

    def test_actual_wrong_sha_is_blocked(self):
        row,evidence = self.row('suttacentral-bilara','root_text')
        pointer = self.host.pointer(row)
        pointer['source_sha'] = '0'*40
        self.assertEqual(self.host.verify_pointer(pointer,quotation=evidence['quotation'])['status'],'REJECTED')

    def test_actual_wrong_segment_is_blocked(self):
        row,evidence = self.row('cbeta-tei','root_text')
        pointer = self.host.pointer(row)
        pointer['segment_id'] = 'invented-source-location'
        self.assertNotEqual(self.host.verify_pointer(pointer,quotation=evidence['quotation'])['status'],'VERIFIED')

    def test_actual_84000_main_and_note_verified_separately(self):
        for role in ('translation_main','translation_note'):
            with self.subTest(role=role):
                _,evidence = self.row('84000-tei',role)
                self.assertEqual(evidence['text_role'],role)
                self.assertTrue(evidence['quotation'])

    def test_actual_84000_note_cannot_be_promoted_to_root(self):
        row,evidence = self.row('84000-tei','translation_note')
        pointer = self.host.pointer(row)
        pointer['text_role'] = 'root_text'
        self.assertEqual(self.host.verify_pointer(pointer,quotation=evidence['quotation'])['status'],'REJECTED')

    def test_actual_quick_preserves_original_rank_and_content(self):
        for corpus,query in [('suttacentral-bilara','sutaṃ'),('cbeta-tei','如是我聞'),('84000-tei','Thus')]:
            with self.subTest(corpus=corpus):
                result = self.host.quick(query,corpus=corpus,limit=2)
                self.assertEqual(result['retrieval'],retrieval.search(self.db,query,corpus=corpus,limit=2))
                self.assertTrue(result['verified_evidence'])
                self.assertFalse(result['publication_authorized'])

    def test_actual_multicorpus_c_receipts_with_a_binding(self):
        _,run = self.start()
        corpora = ['suttacentral-bilara','84000-tei']
        plan = make_counterevidence_plan(run['claims'][0],search_id='actual-c',scope=self.host.scope(corpora),
            steps=[dict(step_id=str(i),corpus=c,operation='search',direction='other_witness',
                        query='sutaṃ' if i==0 else 'Thus',target_id=None) for i,c in enumerate(corpora)],
            unchecked_scope=['Acceptance sample and lexical queries; semantic adequacy not reviewed.'])
        self.host.register_plan(plan)
        result = search_counterevidence(plan,search_reader=self.host.search_reader,evidence_reader=self.host.evidence_reader)
        self.assertTrue(result['verified_evidence'])
        self.assertEqual([r['checked_scope']['corpora'] for r in result['attempts']],[[c] for c in corpora])
        self.assertFalse(result['execution_complete'])  # Many actual hits exceed the host bound.

    def test_actual_research_draft_reopened_and_exported(self):
        research,run = self.start()
        self.assertEqual(run['accepted_claim_ids'],[])
        self.assertFalse(run['counterevidence_performed'])
        reopened = LocalResearch(LocalHost(ROOT,self.db,source_root=SOURCES),research.path)
        captured = reopened.capture(run['run_id'],expected_version=run['version'])
        self.assertEqual(captured['evidence'],run['evidence'])
        exported = reopened.store.export_review(run['run_id'],expected_version=captured['version'],review_questions=['Check source role and scope.'])
        self.assertEqual(json.loads(json.dumps(exported['json']))['snapshot']['evidence'],run['evidence'])
        self.assertFalse(reopened.publication_check(run['run_id'],expected_version=captured['version'])['publication_authorized'])

    def test_actual_unsupported_source_is_not_faked(self):
        with closing(sqlite3.connect(self.db)) as con:
            con.row_factory = sqlite3.Row
            row = dict(con.execute("SELECT * FROM records WHERE corpus='buddhist-neural-parser' LIMIT 1").fetchone()) if con.execute("SELECT COUNT(*) FROM records WHERE corpus='buddhist-neural-parser'").fetchone()[0] else dict(con.execute("SELECT * FROM records WHERE corpus NOT IN ('suttacentral-bilara','cbeta-tei','84000-tei') LIMIT 1").fetchone())
        result = self.host.verify_pointer(self.host.pointer(row))
        self.assertNotEqual(result['status'],'VERIFIED')
        self.assertIsNone(result['evidence'])

    def test_actual_parallel_metadata_stays_separate_from_text(self):
        relation = self.host.retrieve('parallels','mn1')
        bridge = self.host.retrieve('resolve','ea9.7')
        self.assertIsInstance(relation,dict)
        self.assertIsInstance(bridge,dict)
        self.assertNotIn('verified_evidence',relation)
        self.assertNotIn('verified_evidence',bridge)

    def test_actual_claim_without_semantic_assessment_remains_pending(self):
        research,run = self.start()
        result = final_claim_gate(run['claims'][0],mode='research',evidence_reader=self.host.evidence_reader,
                                  history_reader=research.store.history_reader)
        self.assertNotEqual(result['status'],'accepted')
        with self.assertRaises(ValueError): research.finalize(run['run_id'],expected_version=run['version'])


if __name__=='__main__': unittest.main()
