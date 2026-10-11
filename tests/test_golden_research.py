"""Eleven portable SOFTWARE rule cases; approval/dependence are test oracles.

Independent scholarly review and real-corpus answer quality are NOT measured
by these tests. Descriptors in fixtures/v2/golden-cases.json state the rubric.
"""
import copy
import json
from pathlib import Path
import unittest

from corpus_research.claims import (assess_claim,claim_subject,final_claim_gate,make_claim,
                                   synthesis_item,verify_synthesis)
from corpus_research.counterevidence import source_independence
from test_counterevidence import fixture


class GoldenResearchTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {'ev-1':fixture('ev-1'),'ev-2':fixture('ev-2',segment=2)}
        self.claim = make_claim(dict(claim_id='c-1',run_id='run-1',text='The first fixture reports a blue lamp.',
            claim_type='textual',supporting_evidence_ids=['ev-1'],limitations=['Only the two software passages.'],
            presentation={'certainty':'tentative','quotations':[]}))
        self.review = dict(review_id='fixture-review',claim=claim_subject(self.claim),
            evidence=[copy.deepcopy(self.evidence['ev-1']['evidence'])],atomic=True,support_level='DIRECT',
            scope='narrow_lookup',evidence_uses=[dict(evidence_id='ev-1',basis='textual_report',justification='Software rule oracle.')],
            required_limitations=self.claim['limitations'],max_certainty='tentative',reviewer='fixture-oracle',rationale='Test only, no real review.')
        self.history = [copy.deepcopy(self.claim)]
        self.options = dict(review_id='fixture-review',evidence_reader=self.evidence.get,
            assessment_reader=lambda _:copy.deepcopy(self.review),
            history_reader=lambda request:{**request,'complete':True,'history':copy.deepcopy(self.history)})

    def case(self,number):
        cases = json.loads((Path(__file__).parent/'fixtures/v2/golden-cases.json').read_text(encoding='utf-8'))
        case = next(item for item in cases if item['id']==number)
        for field in ('question','scope','allowed_sources','evidence_to_check','forbidden_evidence_use','known_counterevidence',
                      'valid_claim','invalid_claim','expected','required_limitations','pass_criterion'):
            self.assertIn(field,case)
        self.assertEqual(case['layer'],'software_fixture')

    def test_golden_01_one_word_quote_change(self):
        self.case(1)
        from corpus_research.verification import verify_quote
        source = self.evidence['ev-1']['evidence']['quotation']
        self.assertEqual(verify_quote(source,source)['status'],'VERIFIED_EXACT')
        self.assertEqual(verify_quote(source.replace('blue','green'),source)['status'],'QUOTE_MISMATCH')

    def test_golden_02_wrong_source_sha(self):
        self.case(2)
        bad = copy.deepcopy(self.evidence['ev-1'])
        bad['evidence']['source_sha'] = 'not-a-sha'
        self.evidence['ev-1'] = bad
        self.assertNotEqual(final_claim_gate(self.claim,**self.options)['status'],'accepted')

    def test_golden_03_wrong_source_segment(self):
        self.case(3)
        self.evidence['ev-1'] = fixture('ev-1',segment=2)
        self.assertNotEqual(final_claim_gate(self.claim,**self.options)['status'],'accepted')

    def test_golden_04_translation_note_is_not_root(self):
        self.case(4)
        self.evidence['ev-1'] = fixture('ev-1',role='translation_note')
        self.review['evidence'] = [copy.deepcopy(self.evidence['ev-1']['evidence'])]
        self.review['evidence_uses'][0]['basis'] = 'primary_text'
        result = assess_claim(self.claim,**{k:v for k,v in self.options.items() if k!='history_reader'})
        self.assertEqual(result['status'],'REJECTED')

    def test_golden_05_parallel_metadata_is_not_wording(self):
        self.case(5)
        self.evidence['ev-1'] = fixture('ev-1',klass='metadata_relationship')
        self.review['evidence'] = [copy.deepcopy(self.evidence['ev-1']['evidence'])]
        self.assertEqual(final_claim_gate(self.claim,**self.options)['status'],'rejected')
        valid = make_claim({**self.claim,'claim_type':'relationship'})
        self.review.update(claim=claim_subject(valid),evidence_uses=[dict(evidence_id='ev-1',basis='relationship',justification='Fixture relation, not wording.')])
        self.history = [valid]
        self.assertEqual(final_claim_gate(valid,**self.options)['status'],'accepted')

    def test_golden_06_dependent_sources_are_not_independent(self):
        self.case(6)
        current = [self.evidence['ev-1']['evidence'],self.evidence['ev-2']['evidence']]
        result = source_independence(['ev-1','ev-2'],evidence_reader=self.evidence.get)
        self.assertEqual(result['independent_source_count'],1)
        fake = dict(evidence=current,relationship='independent',derived_evidence_id=None,
                    basis='Different passages',reviewer='fixture',rationale='Deliberately false dependence oracle.')
        rejected = source_independence(['ev-1','ev-2'],evidence_reader=self.evidence.get,dependency_reader=lambda _:fake)
        self.assertEqual(rejected['status'],'REJECTED')

    def test_golden_07_universal_claim_exceeds_support(self):
        self.case(7)
        self.claim = make_claim({**self.claim,'text':'Every fixture passage always reports a blue lamp.'})
        self.history = [self.claim]
        self.review.update(claim=claim_subject(self.claim),support_level='UNSUPPORTED')
        self.assertEqual(final_claim_gate(self.claim,**self.options)['status'],'rejected')

    def test_golden_08_wrong_basis_for_historical_empirical_metaphysical(self):
        self.case(8)
        for kind in ('historical','empirical','metaphysical'):
            with self.subTest(kind=kind):
                claim = make_claim({**self.claim,'claim_type':kind})
                self.review['claim'] = claim_subject(claim)
                self.history = [claim]
                self.assertEqual(final_claim_gate(claim,**self.options)['status'],'rejected')

    def test_golden_09_research_without_countersearch(self):
        self.case(9)
        result = final_claim_gate(self.claim,mode='research',**self.options)
        self.assertNotEqual(result['status'],'accepted')
        self.assertEqual(result['checks']['research_conditions']['status'],'UNVERIFIED')

    def test_golden_10_invented_pali_chinese_equivalence(self):
        self.case(10)
        comparative = make_claim({**self.claim,'claim_type':'comparative','text':'The Pali and Chinese fixture terms are doctrinally identical.'})
        self.review['claim'] = claim_subject(comparative)
        self.history = [comparative]
        self.assertEqual(final_claim_gate(comparative,mode='research',**self.options)['status'],'rejected')

    def test_golden_11_synthesis_adds_new_claim(self):
        self.case(11)
        result = final_claim_gate(self.claim,**self.options)
        self.assertEqual(result['status'],'accepted')
        valid = synthesis_item(result['claim'])
        options = {k:v for k,v in self.options.items() if k!='review_id'}
        self.assertEqual(verify_synthesis([valid],[self.claim],{'c-1':'fixture-review'},**options)['status'],'VERIFIED')
        injected = {**valid,'claim_id':'unreviewed','text':'An unreviewed universal conclusion.'}
        self.assertEqual(verify_synthesis([valid,injected],[self.claim],{'c-1':'fixture-review'},**options)['status'],'REJECTED')


if __name__=='__main__':
    unittest.main()
