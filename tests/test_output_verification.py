"""Objective field/link regressions using pinned synthetic software sources."""
from copy import deepcopy
from pathlib import Path
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from corpus_research.declared_sources import verify_declared_source,create_declared_run
from corpus_research.index import build_index
from corpus_research.local_host import LocalHost
from corpus_research.local_research import LocalResearch
from corpus_research.output_verification import OutputContext,verify_output,source_identity,observe_tool_result
from corpus_research.output_workflow import LocalOutputFacts,check_research_output,write_output_check,checked_markdown
from e_fixtures import ROOT,build_fixture,commit


class OutputVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name);cls.db=build_fixture(cls.root)
        repo=cls.root/'suttacentral/bilara-data'
        for work,title in [('sn35.145','Fixture Title Alpha'),('sn35.146','Fixture Title Beta')]:
            p=repo/f'root/pli/ms/sutta/sn/sn35/{work}_root-pli-ms.json';p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps({work+':0.3':title,work+':1.1':'Only under condition T, the fixture reports a blue lamp.'}),encoding='utf-8')
        sha=commit(repo)
        pins=json.loads((cls.root/'manifest.json').read_text())
        for p in pins:
            if p['rel_dest']=='suttacentral/bilara-data':p['commit_sha']=sha
        cbeta=cls.root/'cbeta/xml-p5';xml=cbeta/'T/T01/T01n0001.xml'
        xml.write_text(xml.read_text().replace('<text>','<teiHeader><fileDesc><titleStmt><title>測試標題</title></titleStmt></fileDesc></teiHeader><text>'))
        sha=commit(cbeta)
        for p in pins:
            if p['rel_dest']=='cbeta/xml-p5':p['commit_sha']=sha
        (cls.root/'manifest.json').write_text(json.dumps(pins))
        build_index(cls.root,cls.db,profile='core',only_sources=['suttacentral-bilara'],progress=False)
        build_index(cls.root,cls.db,profile='acceptance',only_sources=['cbeta-tei'],progress=False)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def setUp(self):
        self.host=LocalHost(self.root,self.db)
        self.output=tempfile.TemporaryDirectory();self.addCleanup(self.output.cleanup)
        self.ref=dict(corpus='suttacentral-bilara',work_id='sn35.145',source_path='root/pli/ms/sutta/sn/sn35/sn35.145_root-pli-ms.json',witness='root:root-pli-ms',segment_id='sn35.145:0.3')
        self.title=verify_declared_source(self.host,self.ref,claim_id='c')['gate']['evidence']
        self.body=verify_declared_source(self.host,{**self.ref,'segment_id':'sn35.145:1.1'},claim_id='c')['gate']['evidence']
        self.claim=dict(claim_id='c',text='Fixture claim',claim_type='textual',supporting_evidence_ids=[self.title['evidence_id'],self.body['evidence_id']])
        self.notes={'c':dict(conditions=[dict(id='T',evidence_id=self.body['evidence_id'],quote='Only under condition T',description='Recorded condition, not inferred by code.')],scope_limits=[dict(id='narrow',text='Only this fixture source and scope.')],attributions=[dict(id='voice',evidence_id=self.body['evidence_id'],quote='the fixture reports',speaker='reported speaker',stance='REPORTED_REJECTED')])}
        self.context=OutputContext(evidence_reader=self.host.evidence_reader,claims=[self.claim],notes=self.notes,fact_reader=LocalOutputFacts(self.host))

    def single(self,kind='TITLE',**kw):
        return dict(item_id='i',claim_id='c',kind=kind,text='Fixture Title Alpha',evidence_id=self.title['evidence_id'],source=source_identity(self.title),**kw)

    def conclusion(self):
        return dict(item_id='c1',claim_id='c',kind='CONCLUSION',text='A scoped interpretation.',evidence_ids=self.claim['supporting_evidence_ids'],condition_ids=['T'],scope_limit_ids=['narrow','host:0'],attributions=[dict(id='voice',speaker='reported speaker',stance='REPORTED_REJECTED')],scope='BOUNDED',label='AI_INTERPRETATION')

    def check(self,*items,context=None):
        return verify_output(dict(schema_version='bcr-output-1',items=list(items)),context or self.context)

    def test_title_exact_native_field_passes_and_typo_fails(self):
        self.assertEqual(self.check(self.single())['status'],'CHECKED')
        item=self.single();item['text']='Fixture Title Alpah'
        result=self.check(item);self.assertEqual(result['status'],'REJECTED')
        self.assertTrue(any(c['check']=='TITLE_MATCH' and c['status']=='FAIL' for c in result['checks']))

    def test_title_substring_is_not_full_title(self):
        item=self.single();item['text']='Title Alpha'
        self.assertEqual(self.check(item)['status'],'REJECTED')

    def test_quotation_reuses_gate_quote_rules(self):
        item=self.single('QUOTE',use='TEXTUAL_QUOTE')
        self.assertEqual(self.check(item)['status'],'CHECKED')
        item['text']='Fixture Title Beta';self.assertEqual(self.check(item)['status'],'REJECTED')

    def test_identity_path_pin_work_witness_and_role_mutations(self):
        for field,value in [('work_id','sn35.146'),('source_path','other.json'),('source_sha','0'*40),('witness','translation:other'),('text_role','metadata')]:
            with self.subTest(field=field):
                item=self.single();item['source'][field]=value
                self.assertEqual(self.check(item)['status'],'REJECTED')

    def test_uid_namespace_exact_and_no_implicit_renumbering(self):
        item=self.single('IDENTIFIER',namespace='SC_BILARA_UID');item['text']='sn35.145'
        self.assertEqual(self.check(item)['status'],'CHECKED')
        item['text']='sn35.146';self.assertEqual(self.check(item)['status'],'REJECTED')
        item['namespace']='UNDECLARED_SYSTEM';self.assertEqual(self.check(item)['status'],'REJECTED')

    def test_conditions_scope_and_attribution_rendered_from_context(self):
        result=self.check(self.conclusion());self.assertEqual(result['status'],'CHECKED')
        rendered=result['checked_items'][0]
        self.assertEqual(rendered['conditions'][0]['quote'],'Only under condition T')
        self.assertEqual(len(rendered['scope_limits']),2)
        self.assertIn('Only under condition T',checked_markdown(dict(schema_version='bcr-output-1',items=[self.conclusion()]),self.context))
        self.assertFalse(result['semantic_truth_verified']);self.assertFalse(result['publication_authorized'])

    def test_omitting_conditions_or_scope_fails(self):
        for key in ('condition_ids','scope_limit_ids'):
            with self.subTest(key=key):
                c=self.conclusion();c[key]=[];self.assertEqual(self.check(c)['status'],'REJECTED')

    def test_recorded_speaker_or_stance_cannot_be_upgraded(self):
        for key,value in [('speaker','the Buddha'),('stance','ENDORSED')]:
            c=self.conclusion();c['attributions'][0][key]=value
            self.assertEqual(self.check(c)['status'],'REJECTED')

    def test_reported_rejected_view_cannot_be_teaching_quote(self):
        q=self.single('QUOTE',use='SCRIPTURAL_TEACHING');q.update(evidence_id=self.body['evidence_id'],source=source_identity(self.body),text=self.body['quotation'])
        self.assertEqual(self.check(q)['status'],'REJECTED')

    def test_primary_quote_with_unrecorded_stance_stays_unverified(self):
        q=self.single('QUOTE',use='SCRIPTURAL_TEACHING')
        self.assertEqual(self.check(q)['status'],'UNVERIFIED')

    def test_fabricated_condition_anchor_fails(self):
        notes=deepcopy(self.notes);notes['c']['conditions'][0]['quote']='Fabricated time condition'
        ctx=OutputContext(evidence_reader=self.host.evidence_reader,claims=[self.claim],notes=notes)
        self.assertEqual(self.check(self.conclusion(),context=ctx)['status'],'REJECTED')

    def test_unknown_source_is_not_verified_by_json_flags(self):
        ctx=OutputContext(evidence_reader={'status':'VERIFIED'},claims=[self.claim])
        self.assertEqual(self.check(self.single(),context=ctx)['status'],'UNVERIFIED')

    def test_evidence_from_another_run_cannot_be_rebound(self):
        e=verify_declared_source(self.host,self.ref,claim_id='c',run_id='other-run')['gate']['evidence']
        claim={**self.claim,'run_id':'this-run','supporting_evidence_ids':[e['evidence_id']]}
        ctx=OutputContext(evidence_reader=self.host.evidence_reader,claims=[claim],fact_reader=LocalOutputFacts(self.host))
        item=self.single();item.update(evidence_id=e['evidence_id'],source=source_identity(e))
        self.assertEqual(self.check(item,context=ctx)['status'],'REJECTED')

    def test_source_changed_after_initial_read_blocks_export(self):
        original=self.host.evidence_reader;calls={}
        def reader(eid):
            calls[eid]=calls.get(eid,0)+1
            return original(eid) if calls[eid]==1 else {}
        ctx=OutputContext(evidence_reader=reader,claims=[self.claim],fact_reader=LocalOutputFacts(self.host))
        self.assertEqual(self.check(self.single(),context=ctx)['status'],'UNVERIFIED')

    def test_saved_checked_receipt_cannot_authorize_later_render(self):
        document=dict(schema_version='bcr-output-1',items=[self.single()])
        receipt=verify_output(document,self.context)
        self.assertEqual(receipt['status'],'CHECKED')
        with self.assertRaises(ValueError):checked_markdown(receipt,self.context)
        with patch.object(self.context,'evidence_reader',return_value={}):
            with self.assertRaises(ValueError):checked_markdown(document,self.context)

    def test_free_prose_truth_is_explicitly_not_proven(self):
        c=self.conclusion();c['text']='This prose might still contradict its recorded scope.'
        result=self.check(c)
        self.assertEqual(result['status'],'CHECKED')
        self.assertFalse(result['semantic_truth_verified'])

    def test_universal_scope_and_approval_labels_rejected(self):
        for field,value in [('scope','UNIVERSAL'),('label','accepted'),('publication_authorized',True)]:
            c=self.conclusion();c[field]=value;self.assertEqual(self.check(c)['status'],'REJECTED')

    def test_process_success_does_not_override_gate_json(self):
        gate=self.host.evidence_reader(self.title['evidence_id'])
        for status in ('REJECTED','UNVERIFIED'):
            r=observe_tool_result(0,dict(status=status,gate=gate))
            self.assertTrue(r['process_succeeded']);self.assertFalse(r['source_gate_observed_verified'])
        r=observe_tool_result(0,gate);self.assertTrue(r['source_gate_observed_verified']);self.assertFalse(r['authenticates_source'])
        self.assertFalse(observe_tool_result(2,gate)['source_gate_observed_verified'])

    def test_note_role_cannot_be_presented_as_scripture(self):
        con=sqlite3.connect(self.db)
        try:rid=con.execute("SELECT id FROM records WHERE text_role='translation_note' LIMIT 1").fetchone()[0]
        finally:con.close()
        e=self.host.verify_record(rid)['evidence'];claim={**self.claim,'supporting_evidence_ids':[e['evidence_id']]}
        ctx=OutputContext(evidence_reader=self.host.evidence_reader,claims=[claim])
        q=self.single('QUOTE',use='SCRIPTURAL_TEACHING');q.update(evidence_id=e['evidence_id'],source=source_identity(e),text=e['quotation'])
        self.assertEqual(self.check(q,context=ctx)['status'],'REJECTED')

    def test_chinese_header_title_from_actual_pinned_xml(self):
        con=sqlite3.connect(self.db)
        try:rid=con.execute("SELECT id FROM records WHERE corpus='cbeta-tei' LIMIT 1").fetchone()[0]
        finally:con.close()
        e=self.host.verify_record(rid)['evidence'];claim={**self.claim,'supporting_evidence_ids':[e['evidence_id']]}
        ctx=OutputContext(evidence_reader=self.host.evidence_reader,claims=[claim],fact_reader=LocalOutputFacts(self.host))
        item=self.single();item.update(evidence_id=e['evidence_id'],source=source_identity(e),text='測試標題')
        self.assertEqual(self.check(item,context=ctx)['status'],'CHECKED')

    def test_research_cli_and_failed_export_no_store_mutation(self):
        research=LocalResearch(self.host,Path(self.output.name)/'research.sqlite3')
        run=create_declared_run(research,run_id='r',question='Fixture output',claims=[dict(claim_id='c',text='Fixture claim',claim_type='textual')],source_references={'c':[self.ref]},corpora=['suttacentral-bilara'])['run']
        before=research.store.get_run('r');e=run['evidence'][0]
        item=self.single();item.update(evidence_id=e['evidence_id'],source=source_identity(e),text='Incorrect title')
        document=dict(schema_version='bcr-output-1',items=[item]);path=Path(self.output.name)/'input.json';path.write_text(json.dumps(document))
        cmd=[sys.executable,'-m','corpus_research.v2_cli','--root',str(self.root),'--db',str(self.db),'--store',str(research.path),'output-check','--run-id','r','--version',str(run['version']),'--input',str(path),'--output',str(Path(self.output.name)/'checked')]
        p=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(p.returncode,0,p.stderr)
        result=json.loads(p.stdout);self.assertEqual(result['status'],'REJECTED');self.assertIsNone(result['artifacts']['report'])
        self.assertEqual(before,research.store.get_run('r'))
        self.assertFalse(Path(self.output.name,'checked.md').exists())

    def test_bad_schema_and_reserved_context_notes_rejected(self):
        for document in ({},dict(schema_version='bcr-output-1',items=[]),dict(schema_version='bcr-output-1',items=[self.single()],approved=True)):
            self.assertEqual(verify_output(document,self.context)['status'],'REJECTED')
        notes=deepcopy(self.notes);notes['c']['conditions'][0]['id']='host:0'
        with self.assertRaises(ValueError):OutputContext(evidence_reader=self.host.evidence_reader,claims=[self.claim],notes=notes)
        for value in ([],False,''):
            with self.assertRaises(ValueError):OutputContext(evidence_reader=self.host.evidence_reader,claims=[self.claim],notes=value)
