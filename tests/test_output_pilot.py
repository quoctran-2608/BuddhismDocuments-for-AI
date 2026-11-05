"""Real observed regressions: fresh source facts, not semantic ground truth."""
import json
import os
from pathlib import Path
import unittest

from corpus_research.declared_sources import verify_declared_source
from corpus_research.local_host import LocalHost
from corpus_research.output_verification import OutputContext,verify_output,source_identity,observe_tool_result
from corpus_research.output_workflow import LocalOutputFacts,checked_markdown

ROOT=Path(__file__).resolve().parents[1]


class OutputPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all(os.environ.get(k) for k in ('BCR_P01_DB','BCR_SOURCE_ROOT','BCR_AGENT_EVALUATION')):
            raise unittest.SkipTest('Existing pinned DB/source and locked agent evaluation required; no download.')
        cls.eval=Path(os.environ['BCR_AGENT_EVALUATION'])
        cls.ledger=json.loads((cls.eval/'core-evidence-ledger.json').read_text())
        assert len(cls.ledger)==336

    def setUp(self):
        self.host=LocalHost(ROOT,Path(os.environ['BCR_P01_DB']),source_root=Path(os.environ['BCR_SOURCE_ROOT']))

    def evidence(self,work,segment,english=False):
        old=next(e for e in self.ledger if e['work_id']==work and e['segment_id']==segment and e['witness'].startswith('translation:' if english else 'root:'))
        reference={k:old[k] for k in ('corpus','repository','work_id','source_path','source_sha','witness','segment_id')}
        result=verify_declared_source(self.host,reference,claim_id='regression')
        self.assertEqual(result['status'],'VERIFIED',result)
        e=result['gate']['evidence'];self.assertEqual(e['quotation'],old['quotation'])
        return e

    def context(self,evidence,notes=None):
        claim=dict(claim_id='regression',text='Output regression only; not a new scholarly finding.',claim_type='textual',supporting_evidence_ids=[e['evidence_id'] for e in evidence])
        return OutputContext(evidence_reader=self.host.evidence_reader,claims=[claim],notes={'regression':notes} if notes else None,fact_reader=LocalOutputFacts(self.host))

    def single(self,e,kind,text,**extra):
        return dict(item_id='i',claim_id='regression',kind=kind,text=text,evidence_id=e['evidence_id'],source=source_identity(e),**extra)

    def check(self,ctx,item):return verify_output(dict(schema_version='bcr-output-1',items=[item]),ctx)

    def conclusion(self,evidence,**extra):
        return dict(item_id='conclusion',claim_id='regression',kind='CONCLUSION',text='Scoped AI interpretation, not an approved conclusion.',evidence_ids=[e['evidence_id'] for e in evidence],condition_ids=[],scope_limit_ids=['host:0'],attributions=[],scope='BOUNDED',label='AI_INTERPRETATION',**extra)

    def test_ac04_actual_locked_pali_typo_is_detected(self):
        e=self.evidence('sn35.145','sn35.145:0.3');ctx=self.context([e])
        self.assertEqual(e['quotation'].strip(),'Bāhirānattahetusutta')
        good=self.single(e,'TITLE','Bāhirānattahetusutta')
        self.assertEqual(self.check(ctx,good)['status'],'CHECKED')
        bad={**good,'text':'Bāhirāniccahetuanattasutta'}
        result=self.check(ctx,bad)
        self.assertEqual(result['status'],'REJECTED')
        self.assertTrue(any(c['check']=='TITLE_MATCH' and c['status']=='FAIL' for c in result['checks']))

    def test_ac04_translation_title_and_alternative_namespace(self):
        translation=self.evidence('sn35.145','sn35.145:0.3',True)
        self.assertEqual(self.check(self.context([translation]),self.single(translation,'TITLE',translation['quotation'].strip()))['status'],'CHECKED')
        e=self.evidence('sn35.146','sn35.146:0.3');ctx=self.context([e])
        alias=self.single(e,'IDENTIFIER','SN 35.145',namespace='SC_ALT_ACRONYM')
        result=self.check(ctx,alias);self.assertEqual(result['status'],'CHECKED')
        self.assertEqual(result['checked_items'][0]['source']['work_id'],'sn35.146')
        self.assertTrue(result['checked_items'][0]['fact_provenance'])
        alias.update(namespace='SC_BILARA_UID',text='sn35.145')
        self.assertEqual(self.check(ctx,alias)['status'],'REJECTED')

    def test_ac01_scope_and_recorded_rejected_view_survive(self):
        e=self.evidence('sn36.21','sn36.21:1.5')
        # This stance is a recorded interpretation, not discovered by code.
        notes=dict(conditions=[],scope_limits=[dict(id='feelings-only',text='Only the cited feeling discussion; no universal causal conclusion.')],attributions=[dict(id='reported',evidence_id=e['evidence_id'],quote=e['quotation'],speaker='reported view in the question',stance='REPORTED_REJECTED')])
        ctx=self.context([e],notes)
        item=self.conclusion([e]);item.update(scope_limit_ids=['feelings-only','host:0'],attributions=[dict(id='reported',speaker='reported view in the question',stance='REPORTED_REJECTED')])
        result=self.check(ctx,item);self.assertEqual(result['status'],'CHECKED')
        self.assertFalse(result['semantic_truth_verified'])
        item['scope']='UNIVERSAL';self.assertEqual(self.check(ctx,item)['status'],'REJECTED')
        q=self.single(e,'QUOTE',e['quotation'],use='SCRIPTURAL_TEACHING')
        self.assertEqual(self.check(ctx,q)['status'],'REJECTED')

    def test_ac05_ac11_postmortem_rebirth_links_cannot_be_dropped(self):
        for cid,segments in [('AC05',('mn135:5.2','mn135:5.3')),('AC11',('mn135:7.2','mn135:7.3'))]:
            with self.subTest(case=cid):
                es=[self.evidence('mn135',s,True) for s in segments]
                notes=dict(conditions=[dict(id=i,evidence_id=e['evidence_id'],quote=e['quotation'],description='Recorded temporal/conditional annotation, not inferred by code.') for i,e in zip(('postmortem','rebirth'),es)],scope_limits=[],attributions=[])
                ctx=self.context(es,notes);item=self.conclusion(es);item['condition_ids']=['postmortem','rebirth']
                result=self.check(ctx,item);self.assertEqual(result['status'],'CHECKED')
                self.assertIn(es[0]['quotation'].strip(),checked_markdown(dict(schema_version='bcr-output-1',items=[item]),ctx))
                item['condition_ids']=['postmortem'];self.assertEqual(self.check(ctx,item)['status'],'REJECTED')

    def test_actual_exit_zero_negative_controls_are_not_verified(self):
        controls=json.loads((self.eval/'negative-controls-summary.json').read_text())
        commands=[json.loads(s) for s in (self.eval/'commands.jsonl').read_text().splitlines()]
        self.assertEqual(len(commands),38)
        for name in ('bad-pin','bad-witness','wrong-work-same-path','nonexistent-segment','wrong-quote'):
            with self.subTest(control=name):
                command=next(c for c in commands if c['name']=='negative-'+name)
                self.assertEqual(command['exit_code'],0)
                observation=observe_tool_result(command['exit_code'],controls[name])
                self.assertFalse(observation['source_gate_observed_verified'])
