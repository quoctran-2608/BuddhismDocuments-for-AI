import copy
from contextlib import closing
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from corpus_research.counterevidence import make_counterevidence_plan, search_counterevidence
from corpus_research.local_host import LocalHost
from corpus_research.local_research import LocalResearch
from corpus_research.research_store import ConflictError
from corpus_research.source_resolvers import resolve_source
from e_fixtures import BILARA_PATH, BLUE, RED, ROOT, build_fixture


class LocalIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory()
        cls.root = Path(cls.fixture.name)
        cls.db = build_fixture(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store_path = Path(self.temp.name)/'research.sqlite3'
        self.host = LocalHost(self.root,self.db)

    def row(self,corpus='suttacentral-bilara',role='root_text',segment='mn1:1.1'):
        with closing(sqlite3.connect(self.db)) as con:
            con.row_factory = sqlite3.Row
            return dict(con.execute('SELECT * FROM records WHERE corpus=? AND text_role=? AND segment_id=?',
                                    (corpus,role,segment)).fetchone())

    def start(self,**changes):
        research = LocalResearch(self.host,self.store_path)
        result = research.create(**{'run_id':'r-1','question':'What do the software fixtures report?',
            'queries':['blue lamp'],'corpora':['suttacentral-bilara'],'limit':1,**changes})
        return research,result['run']

    def plan(self,claim,*,operation='search',query='red lamp',target=None,corpora=None):
        corpora = corpora or ['suttacentral-bilara']
        return make_counterevidence_plan(claim,search_id='search-fixture',scope=self.host.scope(corpora),
            steps=[dict(step_id='s-'+str(i),direction='exception',operation=operation,
                        query=query,corpus=corpus,target_id=target) for i,corpus in enumerate(corpora)],
            unchecked_scope=['Software fixture only; no semantic approval.'])

    def test_bilara_source_is_verified_from_git(self):
        result = self.host.verify_record(self.row()['id'],quotation=BLUE)
        self.assertEqual(result['status'],'VERIFIED')
        self.assertEqual(result['evidence']['context']['text'],BLUE)
        self.assertRegex(result['evidence']['source_blob_sha'],r'^[0-9a-f]{40}$')
        self.assertEqual(result['evidence']['quotation'],BLUE)
        self.assertEqual(self.host.metrics['source_reads'],2)

    def test_search_hits_and_ranking_are_unchanged(self):
        from corpus_research.retrieval import search
        direct = search(self.db,'blue lamp',corpus='suttacentral-bilara',limit=2)
        quick = self.host.quick('blue lamp',corpus='suttacentral-bilara',limit=2)
        self.assertEqual(quick['retrieval'],direct)
        self.assertTrue(quick['verified_evidence'])
        self.assertFalse(self.store_path.exists())
        self.assertEqual(quick['claim_assessment'],'NOT_REQUESTED')

    def test_quick_does_not_call_c_or_d_or_semantic_reader(self):
        def forbidden(*args,**kwargs):
            raise AssertionError('Quick called Research machinery')
        self.host.assessment_reader = forbidden
        with patch('corpus_research.research_store.ResearchStore',side_effect=forbidden), patch.object(self.host,'search_reader',side_effect=forbidden):
            result = self.host.quick('blue lamp',limit=1)
        self.assertTrue(result['verified_evidence'])

    def test_pinned_blob_is_read_instead_of_mutable_source_file(self):
        path = self.root/'suttacentral/bilara-data'/BILARA_PATH
        original = path.read_bytes()
        try:
            path.write_text('{"mn1:1.1":"Forged mutable text."}',encoding='utf-8')
            result = self.host.verify_record(self.row()['id'],quotation=BLUE)
            self.assertEqual(result['status'],'VERIFIED')
            self.assertNotIn('Forged',json.dumps(result))
        finally:
            path.write_bytes(original)

    def test_wrong_sha_does_not_verify(self):
        pointer = self.host.pointer(self.row())
        pointer['source_sha'] = '0'*40
        self.assertEqual(self.host.verify_pointer(pointer,quotation=BLUE)['status'],'REJECTED')

    def test_wrong_location_does_not_verify(self):
        pointer = self.host.pointer(self.row())
        pointer['segment_id'] = 'mn1:1.2'
        result = self.host.verify_pointer(pointer,quotation=BLUE)
        self.assertNotEqual(result['status'],'VERIFIED')
        self.assertIsNone(result['evidence'])

    def test_wrong_work_sequence_role_witness_language_are_blocked(self):
        for key,value in [('work_id','other'),('sequence_no',999),('text_role','translation_main'),('witness','fake'),('language','zh')]:
            with self.subTest(key=key):
                pointer = self.host.pointer(self.row())
                pointer[key] = value
                self.assertNotEqual(self.host.verify_pointer(pointer,quotation=BLUE)['status'],'VERIFIED')

    def test_pointer_cannot_select_capabilities_or_fake_verification(self):
        pointer = self.host.pointer(self.row())
        pointer.update(verified=True,approved=True,state='VERIFIED',source_reader='fake')
        with patch.object(self.host,'source_reader',return_value={}):
            result = self.host.verify_pointer(pointer,quotation=BLUE)
        self.assertEqual(result['status'],'UNVERIFIED')

    def test_cbeta_line_is_resolved_with_original_bytes(self):
        result = self.host.verify_record(self.row('cbeta-tei',segment='T01n0001:0001a01')['id'])
        self.assertEqual(result['status'],'VERIFIED')
        self.assertEqual(result['evidence']['quotation'],'如是我聞，藍燈。')
        self.assertNotIn('注釋',result['evidence']['context']['text'])

    def test_cbeta_note_cannot_be_quoted_as_root_line(self):
        result = self.host.verify_record(self.row('cbeta-tei',segment='T01n0001:0001a01')['id'],quotation='注釋假原文。')
        self.assertEqual(result['status'],'REJECTED')

    def test_84000_main_and_note_roles_are_distinct(self):
        for role,segment in [('translation_main','p1'),('translation_note','note1')]:
            with self.subTest(role=role):
                result = self.host.verify_record(self.row('84000-tei',role,segment)['id'])
                self.assertEqual(result['status'],'VERIFIED')
                self.assertEqual(result['evidence']['text_role'],role)

    def test_84000_note_does_not_verify_in_main_excerpt(self):
        result = self.host.verify_record(self.row('84000-tei','translation_main','p1')['id'],quotation='The translator adds a fictional green lamp.')
        self.assertEqual(result['status'],'REJECTED')

    def test_xml_entities_and_unsupported_format_fail_closed(self):
        for corpus,content,path in [('cbeta-tei','<!DOCTYPE TEI [<!ENTITY x "fake">]><TEI/>','T/T01/T01n0001.xml'),
                                    ('unsupported','{"text":"fake"}','source.json')]:
            with self.assertRaises(ValueError):
                resolve_source(content,corpus,path,{'work_id':'x','segment_id':'x'})

    def test_json_escapes_do_not_receive_fake_source_ranges(self):
        content = '{"mn1:1.1":"escaped \\u006c\\u0061\\u006d\\u0070"}'
        with self.assertRaises(ValueError):
            resolve_source(content,'suttacentral-bilara',BILARA_PATH,{'work_id':'mn1','segment_id':'mn1:1.1','sequence_no':0})

    def test_bilara_chunk_is_resolved_independently(self):
        content = json.dumps({'mn1:1.1':BLUE,'mn1:1.2':RED})
        resolved = resolve_source(content,'suttacentral-bilara',BILARA_PATH,
            {'work_id':'mn1','segment_id':'mn1:1.1..mn1:1.2','sequence_no':0})
        a,b = resolved['excerpt_range']
        self.assertIn(content[a:b],(BLUE,RED))
        self.assertEqual(resolved['location']['segment_id'],'mn1:1.1..mn1:1.2')

    def test_source_path_traversal_is_blocked(self):
        pointer = self.host.pointer(self.row())
        pointer['source_path'] = '../secret.json'
        self.assertEqual(self.host.verify_pointer(pointer,quotation=BLUE)['status'],'REJECTED')

    def test_stale_index_pins_are_rejected_without_downloads(self):
        db = Path(self.temp.name)/'stale.sqlite3'
        shutil.copyfile(self.db,db)
        with closing(sqlite3.connect(db)) as con:
            with con:
                con.execute("UPDATE source_state SET source_sha=?",('0'*40,))
        with self.assertRaises(ValueError): LocalHost(self.root,db)

    def test_research_saves_real_evidence_and_actual_receipts_but_no_approval(self):
        research,run = self.start(counter_queries=['red lamp'])
        self.assertEqual(run['run_status'],'draft')
        self.assertTrue(run['evidence'])
        self.assertEqual(run['accepted_claim_ids'],[])
        self.assertEqual(run['checks']['assessment:'+run['claims'][0]['claim_id']],'UNVERIFIED')
        search = run['counterevidence'][0]['result']['search']
        self.assertTrue(search['execution_complete'])
        self.assertTrue(search['verified_evidence'])
        self.assertEqual(search['verified_evidence'][0]['quotation'],RED)
        self.assertFalse(run['counterevidence_performed'])
        self.assertTrue((self.store_path.parent/run['answer_artifact']).exists())
        self.assertFalse(research.publication_check('r-1',expected_version=run['version'])['publication_authorized'])

    def test_reopened_run_reverifies_locators_instead_of_replaying_a_flags(self):
        _,run = self.start()
        research = LocalResearch(LocalHost(self.root,self.db),self.store_path)
        captured = research.capture('r-1',expected_version=run['version'])
        self.assertEqual(captured['evidence'],run['evidence'])
        self.assertTrue(research.host.metrics['source_reads'])

    def test_missing_semantic_approval_blocks_finalization(self):
        research,run = self.start()
        with self.assertRaises(ValueError): research.finalize('r-1',expected_version=run['version'])
        self.assertEqual(research.store.get_run('r-1')['version'],run['version'])

    def test_c_search_receipt_is_linked_to_hit_not_arbitrary_evidence(self):
        _,run = self.start()
        plan = self.plan(run['claims'][0])
        self.host.register_plan(plan)
        result = search_counterevidence(plan,search_reader=self.host.search_reader,evidence_reader=self.host.evidence_reader)
        self.assertEqual(result['status'],'SEARCHED')
        self.assertEqual(result['verified_evidence'][0]['quotation'],RED)
        receipt = self.host.search_reader(plan['search_id'])
        blue = run['evidence'][0]['evidence_id']
        receipt['steps'][0]['candidates'][0]['evidence_id'] = blue
        wrong = search_counterevidence(plan,search_reader=lambda _:receipt,evidence_reader=self.host.evidence_reader)
        self.assertEqual(wrong['status'],'REJECTED')

    def test_c_multicorpus_receipts_use_per_step_scope(self):
        _,run = self.start()
        plan = self.plan(run['claims'][0],corpora=['suttacentral-bilara','84000-tei'])
        self.host.register_plan(plan)
        result = search_counterevidence(plan,search_reader=self.host.search_reader,evidence_reader=self.host.evidence_reader)
        self.assertTrue(result['execution_complete'])
        self.assertEqual([item['checked_scope']['corpora'] for item in result['attempts']],
                         [['suttacentral-bilara'],['84000-tei']])

    def test_c_result_limit_is_not_complete_search(self):
        _,run = self.start()
        self.host.max_candidates = 1
        plan = self.plan(run['claims'][0],query='lamp')
        self.host.register_plan(plan)
        result = search_counterevidence(plan,search_reader=self.host.search_reader,evidence_reader=self.host.evidence_reader)
        self.assertFalse(result['execution_complete'])
        self.assertTrue(result['attempts'][0]['limitations'])

    def test_c_empty_query_results_do_not_establish_global_absence(self):
        _,run = self.start()
        plan = self.plan(run['claims'][0],query='ZXQ-no-such-fixture')
        self.host.register_plan(plan)
        result = search_counterevidence(plan,search_reader=self.host.search_reader,evidence_reader=self.host.evidence_reader)
        self.assertEqual(result['status'],'SEARCHED')
        self.assertIn('không kết luận',result['summary'])

    def test_c_unenforceable_scope_cannot_be_registered(self):
        _,run = self.start()
        plan = self.plan(run['claims'][0])
        plan['scope']['constraints'].append('Invented full historical scope')
        with self.assertRaises(ValueError): self.host.register_plan(plan)

    def test_c_context_target_outside_corpus_is_not_completed(self):
        _,run = self.start()
        plan = self.plan(run['claims'][0],operation='context',query=None,
            target=str(self.row('cbeta-tei',segment='T01n0001:0001a01')['id']))
        self.host.register_plan(plan)
        receipt = self.host.search_reader(plan['search_id'])['steps'][0]
        self.assertEqual(receipt['status'],'failed')
        self.assertFalse(receipt['complete'])

    def test_c_context_truncated_by_host_bound_is_incomplete(self):
        _,run = self.start()
        self.host.max_candidates = 1
        plan = self.plan(run['claims'][0],operation='context',query=None,
                         target=str(self.row()['id']))
        self.host.register_plan(plan)
        receipt = self.host.search_reader(plan['search_id'])['steps'][0]
        self.assertEqual(receipt['status'],'executed')
        self.assertFalse(receipt['complete'])
        self.assertIn('incomplete',' '.join(receipt['limitations']))

    def test_outputs_cannot_be_written_into_sources_or_corpus_index(self):
        for path in [self.db,self.root/'suttacentral/bilara-data/research.sqlite3']:
            with self.assertRaises(ValueError): LocalResearch(self.host,path)

    def test_stale_version_is_blocked_after_reopen(self):
        research,run = self.start()
        research.capture('r-1',expected_version=run['version'])
        with self.assertRaises(ConflictError): research.capture('r-1',expected_version=run['version'])

    def test_cli_quick_and_quote_use_separate_entry_point(self):
        env = {**__import__('os').environ,'PYTHONPATH':str(ROOT/'tools'),'PYTHONIOENCODING':'utf-8'}
        command = [sys.executable,'-m','corpus_research.v2_cli','--root',str(self.root),'--db',str(self.db),'--store',str(self.store_path)]
        result = subprocess.run(command+['quick','blue lamp','--limit','1'],env=env,capture_output=True,text=True,encoding='utf-8',check=True)
        self.assertTrue(json.loads(result.stdout)['verified_evidence'])
        self.assertFalse(self.store_path.exists())
        result = subprocess.run(command+['quote','--record-id',str(self.row()['id']),'--text','The wrong fixture lamp.'],env=env,capture_output=True,text=True,encoding='utf-8',check=True)
        self.assertEqual(json.loads(result.stdout)['status'],'REJECTED')

    def test_cli_outputs_utf8_even_when_inherited_pipe_encoding_is_ascii(self):
        env = {**__import__('os').environ,'PYTHONPATH':str(ROOT/'tools'),'PYTHONIOENCODING':'ascii'}
        command = [sys.executable,'-m','corpus_research.v2_cli','--root',str(self.root),'--db',str(self.db),
                   'quick','如是我聞','--corpus','cbeta-tei','--limit','1']
        result = subprocess.run(command,env=env,capture_output=True,text=True,encoding='utf-8',check=True)
        self.assertEqual(json.loads(result.stdout)['verified_evidence'][0]['quotation'],'如是我聞，藍燈。')

    def test_review_roundtrip_without_host_approval_is_proposed(self):
        research,run = self.start()
        package = research.store.export_review('r-1',expected_version=run['version'],review_questions=['Review fixture claim scope.'])['json']
        cid, eid = run['claims'][0]['claim_id'],run['evidence_ids'][0]
        report = dict(report_id='report-1',package_id=package['package_id'],snapshot_sha256=package['snapshot_sha256'],
            reviewer='declared-fixture-reviewer',reviewer_role='AI',reviewed_at=run['created_at'],session=None,
            relationship_to_proposer='uncertain',unverified=['Not an actual independent review.'],trusted=True,approved=True,
            comments=[dict(claim_id=cid,comment='Fixture comment only.',evidence_ids=[eid],limitations=['Software fixture.'],recommendation='keep')])
        self.assertEqual(research.store.import_review(report)['status'],'PROPOSED')
        self.assertEqual(research.store.record_review_decision('report-1',review_id='self-approved')['status'],'UNVERIFIED')
        self.assertEqual(research.store.get_review('report-1')['decisions'],[])

    def report(self,research,run,**changes):
        package = research.store.export_review('r-1',expected_version=run['version'],review_questions=['Check the exact fixture.'])['json']
        result = dict(report_id='report-1',package_id=package['package_id'],snapshot_sha256=package['snapshot_sha256'],
            reviewer='software-oracle',reviewer_role='AI',reviewed_at=run['created_at'],session=None,
            relationship_to_proposer='uncertain',unverified=['Protocol fixture, not independent scholarly review.'],
            comments=[dict(claim_id=run['claims'][0]['claim_id'],comment='Check the fixture.',
                evidence_ids=[run['evidence_ids'][0]],limitations=['Fixture only.'],recommendation='keep')])
        return {**result,**changes}

    def test_review_wrong_snapshot_is_rejected_with_real_a_adapter(self):
        research,run = self.start()
        with self.assertRaises(ValueError):
            research.store.import_review(self.report(research,run,snapshot_sha256='0'*64))

    def test_review_unknown_evidence_is_rejected(self):
        research,run = self.start()
        report = self.report(research,run)
        report['comments'][0]['evidence_ids'] = ['not-opened']
        with self.assertRaises(ValueError): research.store.import_review(report)

    def test_review_export_becomes_stale_after_claim_revision(self):
        research,run = self.start()
        report = self.report(research,run)
        old = run['claims'][0]
        revised = research.store.revise_claim('r-1',old['claim_id'],
            {**old,'claim_id':'c-2','text':'A narrower description of the fixture.'},reason='Narrow scope.',
            revision_evidence_ids=old['supporting_evidence_ids'],expected_version=run['version'])
        from corpus_research.claims import history_claim
        self.assertEqual(history_claim(revised['claims'],old['claim_id'])['status'],'superseded')
        self.assertEqual(revised['claims'][0],old)  # Append-only original remains unchanged.
        self.assertEqual(revised['claims'][-1]['claim_id'],'c-2')
        with self.assertRaises(ConflictError): research.store.import_review(report)

    def test_revised_run_reopens_source_locators_without_replaying_old_checks(self):
        research,run = self.start()
        old = run['claims'][0]
        revised = research.store.revise_claim('r-1',old['claim_id'],
            {**old,'claim_id':'c-2','text':'Narrower fixture statement.'},reason='Narrow scope.',
            revision_evidence_ids=old['supporting_evidence_ids'],expected_version=run['version'])
        self.assertEqual(revised['evidence'],[])
        reopened = LocalResearch(LocalHost(self.root,self.db),self.store_path)
        captured = reopened.capture('r-1',expected_version=revised['version'])
        self.assertTrue(set(old['supporting_evidence_ids']).issubset(captured['evidence_ids']))
        self.assertTrue(reopened.host.metrics['source_reads'])
        self.assertEqual(captured['checks']['assessment:c-2'],'UNVERIFIED')
        self.assertEqual(captured['accepted_claim_ids'],[])

    def test_c1_assessment_cannot_be_reused_for_c2(self):
        from corpus_research.claims import claim_subject,final_claim_gate
        reviews = {}
        self.host.assessment_reader = reviews.get  # Explicit SOFTWARE oracle.
        research,run = self.start()
        old = run['claims'][0]
        reviews['oracle-c1'] = dict(review_id='oracle-c1',claim=claim_subject(old),
            evidence=[e for e in run['evidence'] if e['evidence_id'] in old['supporting_evidence_ids']],
            atomic=True,support_level='DIRECT',scope='narrow_lookup',
            evidence_uses=[dict(evidence_id=old['supporting_evidence_ids'][0],basis='textual_report',justification='Software oracle.')],
            required_limitations=old['limitations'],max_certainty='tentative',reviewer='software-oracle',rationale='Fixture only.')
        options = dict(review_id='oracle-c1',evidence_reader=self.host.evidence_reader,
            assessment_reader=reviews.get,history_reader=research.store.history_reader)
        self.assertEqual(final_claim_gate(old,**options)['status'],'accepted')
        revised = research.store.revise_claim('r-1',old['claim_id'],
            {**old,'claim_id':'c-2','text':'Narrower fixture statement.'},reason='Narrow scope.',
            revision_evidence_ids=old['supporting_evidence_ids'],expected_version=run['version'])
        self.assertNotEqual(final_claim_gate(revised['claims'][-1],**options)['status'],'accepted')
        self.assertNotEqual(final_claim_gate(old,**options)['status'],'accepted')

    def test_reopened_run_cannot_replay_flags_when_source_reader_is_missing(self):
        _,run = self.start()
        host = LocalHost(self.root,self.db)
        research = LocalResearch(host,self.store_path)
        with patch.object(host,'source_reader',return_value={}):
            captured = research.capture('r-1',expected_version=run['version'])
        self.assertEqual(captured['evidence'],[])
        self.assertNotIn('PASS',[value for key,value in captured['checks'].items() if key.startswith('evidence:')])

    def test_changed_host_context_requires_new_run(self):
        research,run = self.start()
        original = self.host.context_reader
        def changed(run_id):
            return {**original(run_id),'main_repository_commit':'0'*40}
        research.store.context_reader = changed
        with self.assertRaises(ConflictError): research.capture('r-1',expected_version=run['version'])

    def test_two_hosts_cannot_overwrite_each_others_version(self):
        first,run = self.start()
        second = LocalResearch(LocalHost(self.root,self.db),self.store_path)
        second.capture('r-1',expected_version=run['version'])
        with self.assertRaises(ConflictError): first.capture('r-1',expected_version=run['version'])


if __name__=='__main__':
    unittest.main()
