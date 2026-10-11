from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest

from corpus_research.claims import (
    CLAIM_TYPES, SUPPORT_LEVELS, accepted_claim_set, append_claim, assess_claim,
    claim_subject, final_claim_gate, history_claim, make_claim, revise_claim,
    synthesis_item, verify_synthesis,
)
from corpus_research.verification import evidence_gate, make_evidence_record


# Invented software fixtures. The host's approval store below is a test oracle,
# not an assessment of real scripture, scholarly truth or source independence.
PASSAGE = 'The fixture work describes a blue lamp.'


def phase_a_fixture(evidence_id='ev-1', *, evidence_class='authoritative_structured',
                    role='translation_main', witness='Fixture edition', quotation=PASSAGE,
                    quote_kind='direct', limitations=None):
    location = {'work_id': 'fixture-work', 'segment_id': 'fixture-work:1',
                'sequence_no': 1, 'language': 'en', 'text_role': role, 'witness': witness}
    content = json.dumps(location, sort_keys=True) + '\n' + PASSAGE + '\n'
    source = {'repository': 'fixture/source', 'source_sha': '1' * 40,
              'source_path': 'work.txt', 'content': content,
              'location': json.loads(content.splitlines()[0]),
              'excerpt_range': [content.index(PASSAGE), content.index(PASSAGE) + len(PASSAGE)],
              'context_range': [0, len(content)]}
    contract = {'fixture': {'repository': 'fixture/source', 'repo_path': 'fixture/source',
                            'source_sha': '1' * 40, 'evidence_class': evidence_class}}
    pointer = {'corpus': 'fixture', 'repository': 'fixture/source', 'source_sha': '1' * 40,
               'source_path': 'work.txt', 'evidence_class': evidence_class,
               'limitations': limitations, **location}
    candidate = make_evidence_record(pointer, contract, evidence_id=evidence_id, quotation=quotation)
    quote_review = {'review_id': 'quote-review', 'quotation': quotation, 'source_text': PASSAGE,
                    'supported': True, 'reviewer': 'fixture-reviewer', 'rationale': 'Fixture paraphrase approval.'}
    approvals = {'quote-review': copy.deepcopy(quote_review)}
    # A re-read is independent of the proposed snapshot; test-host configuration
    # knows the exact fixture identity. No source data is supplied in the request.
    def source_reader(request):
        if all(request.get(key) == source[key] for key in ('repository', 'source_sha', 'source_path')):
            return copy.deepcopy(source)
        return None
    return evidence_gate(candidate, contract, copy.deepcopy(source),
                         use='relationship' if evidence_class == 'metadata_relationship' else 'textual',
                         quote_kind=quote_kind, paraphrase_review=quote_review,
                         source_reader=source_reader, review_reader=approvals.get)


class ClaimTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {'ev-1': phase_a_fixture()}
        self.assertEqual(self.evidence['ev-1']['status'], 'VERIFIED')
        self.reviews = {}
        self.claim = make_claim({'claim_id': 'c-1', 'text': 'Fixture work reports a blue lamp.',
                                 'claim_type': 'textual', 'supporting_evidence_ids': ['ev-1'],
                                 'presentation': {'certainty': 'asserted', 'quotations': []}})

    def approve(self, claim=None, *, review_id='review-1', level='DIRECT', atomic=True,
                scope='narrow_lookup', bases=None, required_limitations=None, max_certainty='asserted'):
        claim = self.claim if claim is None else claim
        ids = list(dict.fromkeys(claim['supporting_evidence_ids'] + claim['counter_evidence_ids']))
        review = {'review_id': review_id, 'claim': claim_subject(claim),
                  'evidence': [copy.deepcopy(self.evidence[item]['evidence']) for item in ids],
                  'atomic': atomic, 'support_level': level, 'scope': scope,
                  'evidence_uses': [{'evidence_id': item, 'basis': (bases or {}).get(item, 'textual_report'),
                                     'justification': 'Host-approved fixture assessment of this exact passage.'} for item in ids],
                  'required_limitations': required_limitations or [], 'max_certainty': max_certainty,
                  'reviewer': 'authenticated-fixture-reviewer', 'rationale': 'Approved software fixture only.'}
        self.reviews[review_id] = copy.deepcopy(review)
        return review_id

    def options(self, **kwargs):
        return {'review_id': 'review-1', 'evidence_reader': self.evidence.get,
                'assessment_reader': self.reviews.get, **kwargs}

    def gate(self, claim=None, **kwargs):
        return final_claim_gate(self.claim if claim is None else claim, **self.options(**kwargs))

    def batch_options(self, **kwargs):
        return {'evidence_reader': self.evidence.get, 'assessment_reader': self.reviews.get, **kwargs}

    def test_new_claim_is_candidate_even_with_self_declared_acceptance(self):
        claim = make_claim({**self.claim, 'status': 'accepted', 'verification_status': 'DIRECT',
                            'atomic': True, 'independence_status': 'independent'})
        self.assertEqual(claim['status'], 'candidate')
        self.assertIsNone(claim['verification_status'])
        self.assertEqual(claim['independence_status'], 'uncertain')
        self.assertNotIn('atomic', claim)

    def test_missing_required_claim_fields_are_rejected(self):
        for key in ('claim_id', 'text', 'claim_type'):
            for value in (None, '', ' ', [], True):
                with self.subTest(key=key, value=value):
                    claim = {**self.claim, key: value}
                    with self.assertRaises(ValueError):
                        make_claim(claim)
                    self.assertEqual(self.gate(claim)['status'], 'rejected')

    def test_all_seven_types_are_representable_invalid_type_is_rejected(self):
        self.assertEqual(len(CLAIM_TYPES), 7)
        for kind in CLAIM_TYPES:
            self.assertEqual(make_claim({**self.claim, 'claim_type': kind})['claim_type'], kind)
        self.assertEqual(self.gate({**self.claim, 'claim_type': 'unknown'})['status'], 'rejected')

    def test_unknown_fields_are_not_guessed(self):
        claim = make_claim({'claim_id': 'empty', 'text': 'Fixture proposal.', 'claim_type': 'textual'})
        for field in ('run_id', 'verification_status', 'supersedes_claim_id', 'revision_reason'):
            self.assertIsNone(claim[field])
        for field in ('supporting_evidence_ids', 'counter_evidence_ids', 'limitations', 'revision_evidence_ids'):
            self.assertEqual(claim[field], [])
        self.assertEqual(claim['independence_status'], 'uncertain')
        self.assertIsNone(claim['presentation']['certainty'])

    def test_proposed_split_needs_independent_semantic_approval(self):
        claims = [make_claim({**self.claim, 'claim_id': f'part-{index}', 'text': text}) for index, text in enumerate(
            ('Fixture work contains X.', 'X is interpreted as Y.', 'Y appeared in year Z.', 'This proves W.'))]
        for claim in claims:
            self.assertEqual(self.gate({**claim, 'atomic': True})['status'], 'candidate')
        compound = {**self.claim, 'text': 'A says X, therefore Y originated in Z and proves W.'}
        self.approve(compound, atomic=False)
        self.assertEqual(self.gate(compound)['checks']['atomic']['status'], 'FAIL')
        self.assertEqual(self.gate(compound)['status'], 'rejected')

    def test_punctuation_does_not_decide_atomicity(self):
        claim = {**self.claim, 'text': 'The phrase is “lamp, oil and wick”.'}
        self.approve(claim, atomic=True)
        self.assertEqual(self.gate(claim)['status'], 'accepted')

    def test_no_supporting_evidence_cannot_be_accepted(self):
        claim = {**self.claim, 'supporting_evidence_ids': []}
        self.approve(claim)
        self.assertEqual(self.gate(claim)['status'], 'rejected')

    def test_candidate_verified_json_cannot_supply_evidence_authority(self):
        self.approve()
        forged = {**self.claim, 'evidence': self.evidence, 'state': 'VERIFIED', 'accepted': True}
        result = self.gate(forged, evidence_reader=None)
        self.assertEqual(result['status'], 'candidate')
        self.assertEqual(result['checks']['evidence:ev-1']['status'], 'UNVERIFIED')

    def test_a_result_must_come_through_reader_and_match_requested_id(self):
        self.approve()
        self.assertEqual(self.gate()['status'], 'accepted')
        self.evidence['ev-1']['evidence']['evidence_id'] = 'other'
        self.assertEqual(self.gate()['status'], 'candidate')

    def test_invalid_a_result_envelopes_fail_closed(self):
        self.approve()
        original = copy.deepcopy(self.evidence['ev-1'])
        for update in ({'status': 'UNVERIFIED'}, {'source_opened': False}, {'checks': {}},
                       {'evidence': {'evidence_id': 'ev-1', 'state': 'VERIFIED'}},
                       {'checks': {'independent_source': {'status': 'UNVERIFIED'}}}):
            with self.subTest(update=update):
                self.evidence['ev-1'] = {**original, **update}
                self.assertEqual(self.gate()['status'], 'candidate')

    def test_retrieval_score_cannot_create_support(self):
        claim = {**self.claim, 'retrieval_score': 10**30, 'rank': 1, 'verification_status': 'DIRECT'}
        self.assertEqual(self.gate(claim)['status'], 'candidate')
        self.approve()
        self.assertEqual(self.gate(claim)['status'], 'accepted')
        self.assertEqual(self.gate(claim)['claim']['verification_status'], 'DIRECT')

    def test_citation_count_cannot_create_strong_support(self):
        for number in range(2, 8):
            self.evidence[f'ev-{number}'] = phase_a_fixture(f'ev-{number}')
        claim = {**self.claim, 'supporting_evidence_ids': list(self.evidence), 'verification_status': 'STRONG'}
        self.assertEqual(self.gate(claim)['status'], 'candidate')

    def test_direct_and_strong_need_all_gate_conditions(self):
        for level in ('DIRECT', 'STRONG'):
            with self.subTest(level=level):
                self.approve(level=level)
                result = self.gate()
                self.assertEqual(result['status'], 'accepted')
                self.assertEqual(result['claim']['verification_status'], level)
                self.assertEqual(result['claim']['independence_status'], 'uncertain')

    def test_all_five_levels_are_distinct_from_lifecycle(self):
        self.assertEqual(len(SUPPORT_LEVELS), 5)
        for level in SUPPORT_LEVELS:
            claim = copy.deepcopy(self.claim)
            if level == 'WEAK':
                claim['limitations'] = ['Only this fixture passage was checked.']
                claim['presentation']['certainty'] = 'tentative'
            self.approve(claim, level=level)
            result = self.gate(claim)
            self.assertEqual(result['claim']['verification_status'], level)
            self.assertEqual(result['status'], 'rejected' if level in ('UNSUPPORTED', 'CONTRADICTED') else 'accepted')

    def test_missing_assessment_is_not_assessed_unsupported(self):
        pending = self.gate()
        self.assertEqual(pending['status'], 'candidate')
        self.assertIsNone(pending['claim']['verification_status'])
        self.approve(level='UNSUPPORTED')
        assessed = self.gate()
        self.assertEqual(assessed['status'], 'rejected')
        self.assertEqual(assessed['claim']['verification_status'], 'UNSUPPORTED')

    def test_self_proposed_assessment_does_not_approve_itself(self):
        proposed = {**self.claim, 'support_level': 'DIRECT', 'assessment': {'atomic': True, 'approved': True},
                    'assessment_reader': 'approved', 'verification_status': 'DIRECT', 'status': 'accepted'}
        result = self.gate(proposed)
        self.assertEqual(result['status'], 'candidate')
        self.assertIsNone(result['claim']['verification_status'])

    def test_capabilities_receive_only_ids(self):
        self.approve()
        evidence_requests, review_requests = [], []
        def evidence_reader(value):
            evidence_requests.append(value)
            return self.evidence.get(value)
        def assessment_reader(value):
            review_requests.append(value)
            return self.reviews.get(value)
        self.assertEqual(self.gate(evidence_reader=evidence_reader, assessment_reader=assessment_reader)['status'], 'accepted')
        self.assertEqual(evidence_requests, ['ev-1'])
        self.assertEqual(review_requests, ['review-1'])

    def test_missing_failed_noncallable_capabilities_fail_closed(self):
        self.approve()
        def failed(_):
            raise OSError('fixture channel unavailable')
        for field in ('evidence_reader', 'assessment_reader'):
            for reader in (None, failed, lambda _: None, {'approved': True}, lambda _: []):
                with self.subTest(field=field, reader=type(reader).__name__):
                    self.assertEqual(self.gate(**{field: reader})['status'], 'candidate')

    def test_changed_claim_content_or_type_invalidates_approval(self):
        self.approve()
        for field, value in (('text', 'All works prove a real historical event.'), ('claim_type', 'historical'),
                             ('claim_id', 'other'), ('run_id', 'different-run'), ('limitations', ['Changed scope.'])):
            with self.subTest(field=field):
                result = self.gate({**self.claim, field: value})
                self.assertEqual(result['status'], 'candidate')
                self.assertEqual(result['checks']['approved_binding']['status'], 'UNVERIFIED')

    def test_changed_source_content_provenance_and_roles_invalidate_approval(self):
        self.approve()
        original = copy.deepcopy(self.evidence['ev-1'])
        for field, value in (('source_sha', '2' * 40), ('source_blob_sha', '3' * 40),
                             ('repository', 'other/source'), ('source_path', 'other.txt'),
                             ('quotation', 'Changed quotation.'), ('witness', 'Other witness'),
                             ('text_role', 'root_text'), ('evidence_class', 'canonical_root'),
                             ('context', {'before': '', 'text': 'Changed context.', 'after': ''})):
            with self.subTest(field=field):
                self.evidence['ev-1'] = copy.deepcopy(original)
                self.evidence['ev-1']['evidence'][field] = value
                result = self.gate()
                self.assertNotEqual(result['status'], 'accepted')
                self.assertEqual(result['checks']['approved_binding']['status'], 'UNVERIFIED')

    def test_changing_evidence_id_or_counterevidence_invalidates_approval(self):
        self.approve()
        self.evidence['ev-2'] = phase_a_fixture('ev-2')
        for update in ({'supporting_evidence_ids': ['ev-2']}, {'counter_evidence_ids': ['ev-2']}):
            self.assertEqual(self.gate({**self.claim, **update})['status'], 'candidate')

    def test_malformed_assessment_cannot_grant_support(self):
        self.approve()
        original = copy.deepcopy(self.reviews['review-1'])
        for field, value in (('atomic', 1), ('support_level', '99%'), ('support_level', []),
                             ('reviewer', ''), ('rationale', ''), ('scope', 'all'),
                             ('max_certainty', 'absolute'), ('required_limitations', None)):
            with self.subTest(field=field):
                self.reviews['review-1'] = {**original, field: value}
                result = self.gate()
                self.assertEqual(result['status'], 'candidate')
                self.assertIsNone(result['claim']['verification_status'])

    def test_unknown_review_id_or_wrong_binding_cannot_pass(self):
        self.approve()
        self.assertEqual(self.gate(review_id='missing')['status'], 'candidate')
        self.reviews['review-1']['review_id'] = 'wrong'
        self.assertEqual(self.gate()['status'], 'candidate')

    def test_relationship_metadata_can_support_only_a_reviewed_relationship(self):
        self.evidence['ev-1'] = phase_a_fixture(evidence_class='metadata_relationship', role='relationship', quotation=None)
        claim = {**self.claim, 'claim_type': 'relationship', 'text': 'The fixture metadata links A and B.'}
        self.approve(claim, bases={'ev-1': 'relationship'})
        self.assertEqual(self.gate(claim)['status'], 'accepted')
        self.assertEqual(self.gate({**claim, 'claim_type': 'textual'})['status'], 'candidate')
        textual = {**claim, 'claim_type': 'textual'}
        self.approve(textual, bases={'ev-1': 'textual_report'})
        self.assertEqual(self.gate(textual)['status'], 'rejected')

    def test_text_does_not_prove_historical_empirical_or_metaphysical_truth(self):
        for kind in ('historical', 'empirical', 'metaphysical'):
            with self.subTest(kind=kind):
                claim = {**self.claim, 'claim_type': kind, 'text': 'The reported event is true in reality.'}
                self.approve(claim, bases={'ev-1': 'textual_report'})
                self.assertEqual(self.gate(claim)['status'], 'rejected')
                self.assertEqual(self.gate(claim)['checks']['type:ev-1']['status'], 'FAIL')

    def test_nonquick_types_can_be_assessed_but_not_finalized_without_c_d(self):
        bases = {'historical': 'historical_corroboration', 'empirical': 'empirical_observation',
                 'metaphysical': 'metaphysical_argument', 'comparative': 'comparison', 'interpretive': 'interpretation'}
        for kind, basis in bases.items():
            with self.subTest(kind=kind):
                claim = {**self.claim, 'claim_type': kind}
                self.approve(claim, bases={'ev-1': basis}, scope='research')
                assessed = assess_claim(claim, **self.options())
                self.assertEqual(assessed['status'], 'ASSESSED')
                self.assertEqual(self.gate(claim)['status'], 'candidate')

    def test_note_translation_and_discovery_cannot_claim_primary_root_authority(self):
        for role, klass in (('translation_note', 'authoritative_structured'),
                            ('translation_main', 'canonical_root'), ('root_text', 'computational_segmented'),
                            ('root_text', 'parallel_alignment')):
            with self.subTest(role=role, klass=klass):
                self.evidence['ev-1'] = phase_a_fixture(role=role, evidence_class=klass)
                claim = {**self.claim, 'limitations': [f'discovery_source:ev-1:{klass}'] if klass in ('computational_segmented', 'parallel_alignment') else []}
                self.approve(claim, bases={'ev-1': 'primary_text'})
                self.assertEqual(self.gate(claim)['status'], 'rejected')

    def test_reviewed_primary_text_requires_root_role_and_witness(self):
        self.evidence['ev-1'] = phase_a_fixture(role='root_text', evidence_class='canonical_root')
        self.approve(bases={'ev-1': 'primary_text'})
        self.assertEqual(self.gate()['status'], 'accepted')
        self.evidence['ev-1'] = phase_a_fixture(role='root_text', evidence_class='canonical_root', witness=None)
        self.approve(bases={'ev-1': 'primary_text'})
        self.assertEqual(self.gate()['status'], 'rejected')

    def test_discovery_lookup_keeps_explicit_limits_and_original_class(self):
        self.evidence['ev-1'] = phase_a_fixture(evidence_class='computational_segmented', role='computational_text')
        self.approve()
        self.assertEqual(self.gate()['status'], 'rejected')
        claim = {**self.claim, 'limitations': ['discovery_source:ev-1:computational_segmented']}
        self.approve(claim)
        result = self.gate(claim)
        self.assertEqual(result['status'], 'accepted')
        self.assertEqual(result['evidence'][0]['evidence_class'], 'computational_segmented')
        self.assertEqual(result['evidence'][0]['text_role'], 'computational_text')
        self.assertEqual(result['evidence'][0]['witness'], 'Fixture edition')

    def test_evidence_uses_must_cover_exact_current_evidence(self):
        self.approve()
        original = copy.deepcopy(self.reviews['review-1'])
        for uses in ([], [{'evidence_id': 'wrong', 'basis': 'textual_report', 'justification': 'Test'}],
                     [{'evidence_id': 'ev-1', 'basis': 'textual_report', 'justification': ''}]):
            self.reviews['review-1'] = {**original, 'evidence_uses': uses}
            self.assertEqual(self.gate()['status'], 'rejected')

    def test_unsupported_stays_rejected_with_tentative_wording(self):
        claim = {**self.claim, 'text': 'Perhaps the fixture proves everything.',
                 'presentation': {'certainty': 'tentative', 'quotations': []}}
        self.approve(claim, level='UNSUPPORTED')
        self.assertEqual(self.gate(claim)['status'], 'rejected')

    def test_contradicted_cannot_enter_accepted_set(self):
        self.approve(level='CONTRADICTED')
        result = accepted_claim_set([self.claim], {'c-1': 'review-1'}, **self.batch_options())
        self.assertEqual(result['accepted_claims'], [])
        self.assertEqual(result['results'][0]['claim']['verification_status'], 'CONTRADICTED')

    def test_weak_requires_tentative_presentation_and_limitations(self):
        for certainty, limitations, expected in (('asserted', ['Limited fixture.'], 'rejected'),
                                                  ('tentative', [], 'rejected'),
                                                  ('tentative', ['Limited fixture.'], 'accepted')):
            claim = {**self.claim, 'limitations': limitations, 'presentation': {'certainty': certainty, 'quotations': []}}
            self.approve(claim, level='WEAK', max_certainty='tentative')
            self.assertEqual(self.gate(claim)['status'], expected)

    def test_reviewer_and_evidence_limits_cannot_be_omitted(self):
        self.evidence['ev-1'] = phase_a_fixture(limitations=['Fixture edition only.'])
        for limitations, expected in (([], 'rejected'), (['Fixture edition only.'], 'rejected'),
                                       (['Fixture edition only.', 'Narrow approved scope.'], 'accepted')):
            claim = {**self.claim, 'limitations': limitations}
            self.approve(claim, required_limitations=['Narrow approved scope.'])
            self.assertEqual(self.gate(claim)['status'], expected)

    def test_direct_cannot_exceed_approved_certainty(self):
        self.approve(max_certainty='tentative')
        self.assertEqual(self.gate()['status'], 'rejected')

    def test_unknown_presentation_remains_pending(self):
        claim = {**self.claim, 'presentation': {'certainty': None, 'quotations': []}}
        self.approve(claim)
        self.assertEqual(self.gate(claim)['status'], 'candidate')

    def test_direct_quotes_must_match_verified_wording_role_and_witness(self):
        quote = {'evidence_id': 'ev-1', 'text': PASSAGE, 'kind': 'direct',
                 'text_role': 'translation_main', 'witness': 'Fixture edition'}
        claim = {**self.claim, 'presentation': {'certainty': 'asserted', 'quotations': [quote]}}
        self.approve(claim)
        self.assertEqual(self.gate(claim)['status'], 'accepted')
        for field, value in (('text', 'Changed words.'), ('text_role', 'root_text'),
                             ('witness', 'Other edition'), ('evidence_id', 'unknown')):
            broken = {**claim, 'presentation': {'certainty': 'asserted', 'quotations': [{**quote, field: value}]}}
            self.approve(broken)
            self.assertEqual(self.gate(broken)['status'], 'rejected')

    def test_paraphrase_cannot_be_presented_as_direct_quote(self):
        text = 'A blue lamp appears in the fixture.'
        self.evidence['ev-1'] = phase_a_fixture(quotation=text, quote_kind='paraphrase')
        self.assertEqual(self.evidence['ev-1']['status'], 'VERIFIED')
        quote = {'evidence_id': 'ev-1', 'text': text, 'kind': 'direct',
                 'text_role': 'translation_main', 'witness': 'Fixture edition'}
        claim = {**self.claim, 'presentation': {'certainty': 'asserted', 'quotations': [quote]}}
        self.approve(claim)
        self.assertEqual(self.gate(claim)['status'], 'rejected')
        claim['presentation']['quotations'][0]['kind'] = 'paraphrase'
        self.approve(claim)
        self.assertEqual(self.gate(claim)['status'], 'accepted')

    def test_quote_mismatch_or_unverified_a_result_cannot_be_used(self):
        self.approve()
        for status in ('QUOTE_MISMATCH', 'UNVERIFIED'):
            self.evidence['ev-1']['evidence']['quote_verification_status'] = status
            self.evidence['ev-1']['quote']['status'] = status
            self.assertEqual(self.gate()['status'], 'candidate')

    def test_research_cannot_be_completed_by_json_flags(self):
        claim = {**self.claim, 'run_id': 'run-1', 'counterevidence_completed': True,
                 'independence_status': 'independent', 'research_run': {'status': 'finalized'}}
        self.approve(claim)
        result = self.gate(claim, mode='research')
        self.assertEqual(result['status'], 'candidate')
        self.assertEqual(result['checks']['research_conditions']['status'], 'UNVERIFIED')
        self.assertEqual(result['claim']['independence_status'], 'uncertain')

    def test_research_requires_run_id_and_invalid_mode_rejected(self):
        self.approve()
        self.assertEqual(self.gate(mode='research')['status'], 'rejected')
        self.assertEqual(self.gate(mode='unrecognized')['status'], 'rejected')

    def test_broad_scope_cannot_be_finalized_through_quick_mode(self):
        self.approve(scope='research')
        self.assertEqual(self.gate(mode='quick')['status'], 'candidate')

    def test_accepted_set_filters_pending_and_rejected_claims(self):
        self.approve()
        second = {**self.claim, 'claim_id': 'c-2', 'text': 'Fixture unsupported proposal.'}
        third = {**self.claim, 'claim_id': 'c-3', 'text': 'Fixture pending proposal.'}
        self.approve(second, review_id='review-2', level='UNSUPPORTED')
        result = accepted_claim_set([self.claim, second, third], {'c-1': 'review-1', 'c-2': 'review-2'}, **self.batch_options())
        self.assertEqual([item['claim_id'] for item in result['accepted_claims']], ['c-1'])
        self.assertEqual([item['status'] for item in result['results']], ['accepted', 'rejected', 'candidate'])

    def test_duplicate_claim_ids_are_not_ambiguous(self):
        with self.assertRaises(ValueError):
            accepted_claim_set([self.claim, {**self.claim, 'text': 'Changed'}], {}, **self.batch_options())

    def test_structured_synthesis_allows_only_currently_accepted_items(self):
        self.approve()
        accepted = self.gate()['claim']
        items = [synthesis_item(accepted)]
        result = verify_synthesis(items, [self.claim], {'c-1': 'review-1'}, **self.batch_options())
        self.assertEqual(result['status'], 'VERIFIED')
        self.assertEqual(result['items'], items)
        self.assertIn('free prose is not certified', result['detail'])

    def test_synthesis_rejects_new_changed_or_strengthened_claims(self):
        self.approve()
        original = synthesis_item(self.gate()['claim'])
        for field, value in (('claim_id', 'new'), ('text', 'New academic conclusion.'),
                             ('verification_status', 'STRONG'), ('limitations', ['Rewritten scope.']),
                             ('presentation', {'certainty': 'tentative', 'quotations': []})):
            item = {**original, field: value}
            self.assertEqual(verify_synthesis([item], [self.claim], {'c-1': 'review-1'}, **self.batch_options())['status'], 'REJECTED')

    def test_synthesis_rejects_free_prose_or_extra_conclusions(self):
        self.approve()
        item = synthesis_item(self.gate()['claim'])
        for items in ('A new conclusion referencing c-1.', {'claim_ids': ['c-1'], 'text': 'Unchecked prose'},
                      [{**item, 'extra_conclusion': 'Everything is established.'}], [item, item]):
            self.assertEqual(verify_synthesis(items, [self.claim], {'c-1': 'review-1'}, **self.batch_options())['status'], 'REJECTED')

    def test_serialized_accepted_results_are_not_synthesis_authority(self):
        self.approve()
        accepted = json.loads(json.dumps(self.gate()['claim']))
        result = verify_synthesis([synthesis_item(accepted)], [accepted], {'c-1': 'review-1'})
        self.assertEqual(result['status'], 'REJECTED')

    def test_synthesis_rechecks_source_after_acceptance(self):
        self.approve()
        item = synthesis_item(self.gate()['claim'])
        self.evidence['ev-1']['evidence']['context']['after'] += ' New context.'
        self.assertEqual(verify_synthesis([item], [self.claim], {'c-1': 'review-1'}, **self.batch_options())['status'], 'REJECTED')

    def test_revision_has_new_id_reason_evidence_and_original_snapshot(self):
        history = append_claim([], self.claim)
        before = copy.deepcopy(history)
        result = revise_claim(history, 'c-1', {'claim_id': 'c-2', 'text': 'Only this fixture passage reports X.'},
                              reason='Narrow the reviewed scope.', revision_evidence_ids=['ev-1'])
        self.assertEqual(history, before)
        self.assertEqual(result[0], before[0])
        self.assertEqual(result[1]['status'], 'candidate')
        self.assertIsNone(result[1]['verification_status'])
        self.assertEqual(result[1]['supersedes_claim_id'], 'c-1')
        self.assertEqual(result[1]['revision_reason'], 'Narrow the reviewed scope.')
        self.assertEqual(result[1]['revision_evidence_ids'], ['ev-1'])
        self.assertEqual(history_claim(result, 'c-1')['status'], 'superseded')
        self.assertEqual(history_claim(result, 'c-1')['text'], self.claim['text'])
        self.assertEqual(history_claim(result, 'c-2')['status'], 'candidate')

    def test_revision_preserves_counterevidence_from_predecessor(self):
        old = {**self.claim, 'counter_evidence_ids': ['counter-old']}
        history = append_claim([], old)
        result = revise_claim(history, 'c-1', {'claim_id': 'c-2', 'text': 'Narrower fixture.', 'counter_evidence_ids': ['counter-new']},
                              reason='Counterexamples constrain scope.', revision_evidence_ids=['counter-old'])
        self.assertEqual(result[1]['counter_evidence_ids'], ['counter-old', 'counter-new'])
        self.assertEqual(result[0]['counter_evidence_ids'], ['counter-old'])

    def test_revision_rejects_reused_id_missing_reason_or_lost_evidence(self):
        history = append_claim([], self.claim)
        for payload, reason, ids in (({'claim_id': 'c-1', 'text': 'Changed'}, 'Reason', ['ev-1']),
                                     ({'claim_id': 'c-2', 'text': 'Changed'}, '', ['ev-1']),
                                     ({'claim_id': 'c-2', 'text': 'Changed'}, 'Reason', []),
                                     ({'claim_id': 'c-2', 'text': 'Changed'}, 'Reason', ['missing'])):
            with self.assertRaises(ValueError):
                revise_claim(history, 'c-1', payload, reason=reason, revision_evidence_ids=ids)
        with self.assertRaises(ValueError):
            append_claim(history, {**self.claim, 'text': 'Silently overwrite'})

    def test_revision_requires_known_active_predecessor_and_same_run(self):
        history = append_claim([], self.claim)
        revised = revise_claim(history, 'c-1', {'claim_id': 'c-2', 'text': 'Narrow'}, reason='Narrow', revision_evidence_ids=['ev-1'])
        for old_id in ('missing', 'c-1'):
            with self.assertRaises(ValueError):
                revise_claim(revised, old_id, {'claim_id': 'c-3', 'text': 'Changed'}, reason='Reason', revision_evidence_ids=['ev-1'])
        with self.assertRaises(ValueError):
            revise_claim(history, 'c-1', {'claim_id': 'c-2', 'text': 'Changed', 'run_id': 'different'}, reason='Reason', revision_evidence_ids=['ev-1'])

    def test_history_rejects_cycles_and_duplicate_snapshots(self):
        first = {**self.claim, 'supersedes_claim_id': 'c-2', 'revision_reason': 'Reason', 'revision_evidence_ids': ['ev-1']}
        second = {**self.claim, 'claim_id': 'c-2', 'supersedes_claim_id': 'c-1', 'revision_reason': 'Reason', 'revision_evidence_ids': ['ev-1']}
        for history in ([first, second], [self.claim, self.claim], [{**first, 'supersedes_claim_id': 'c-1'}]):
            with self.assertRaises(ValueError):
                history_claim(history, 'c-1')

    def test_revision_cannot_reuse_old_semantic_approval(self):
        self.approve()
        history = revise_claim(append_claim([], self.claim), 'c-1', {'claim_id': 'c-2', 'text': 'Narrower scope.'},
                               reason='Scope change.', revision_evidence_ids=['ev-1'])
        self.assertEqual(self.gate(history[-1])['status'], 'candidate')
        self.assertEqual(self.gate(history[-1])['checks']['approved_binding']['status'], 'UNVERIFIED')

    def test_superseded_claim_is_excluded_even_with_old_valid_approval(self):
        self.approve()
        history = revise_claim(append_claim([], self.claim), 'c-1', {'claim_id': 'c-2', 'text': 'Narrower scope.'},
                               reason='Scope change.', revision_evidence_ids=['ev-1'])
        self.approve(history[-1], review_id='review-2')
        result = accepted_claim_set(history, {'c-1': 'review-1', 'c-2': 'review-2'}, **self.batch_options())
        self.assertEqual([item['claim_id'] for item in result['accepted_claims']], ['c-2'])
        self.assertEqual(result['results'][0]['status'], 'superseded')
        old_item = synthesis_item(self.gate()['claim'])
        self.assertEqual(verify_synthesis([old_item], history, {'c-1': 'review-1', 'c-2': 'review-2'}, **self.batch_options())['status'], 'REJECTED')

    def test_revision_requires_history_before_acceptance_and_cannot_edit_snapshot(self):
        history = revise_claim(append_claim([], self.claim), 'c-1', {'claim_id': 'c-2', 'text': 'Narrower scope.'},
                               reason='Scope change.', revision_evidence_ids=['ev-1'])
        self.approve(history[-1])
        self.assertEqual(self.gate(history[-1])['status'], 'candidate')
        self.assertEqual(self.gate(history[-1], history=history)['status'], 'accepted')
        changed = {**history[-1], 'text': 'Silently edited snapshot.'}
        self.approve(changed)
        self.assertEqual(self.gate(changed, history=history)['status'], 'rejected')

    def test_malformed_host_evidence_is_unverified_without_crashing(self):
        self.approve()
        original = copy.deepcopy(self.evidence['ev-1'])
        for field, value in (('evidence_class', []), ('source_sha', 'main'), ('source_path', '../outside'),
                             ('witness', {}), ('sequence_no', True), ('context', {'text': object()}), ('match_reasons', ('tuple',))):
            with self.subTest(field=field):
                self.evidence['ev-1'] = copy.deepcopy(original)
                self.evidence['ev-1']['evidence'][field] = value
                self.assertEqual(self.gate()['status'], 'candidate')

    def test_batch_cannot_disable_known_supersession_by_overriding_history(self):
        self.approve()
        history = revise_claim(append_claim([], self.claim), 'c-1', {'claim_id': 'c-2', 'text': 'Narrower scope.'},
                               reason='Scope change.', revision_evidence_ids=['ev-1'])
        self.approve(history[-1], review_id='review-2')
        review_ids = {'c-1': 'review-1', 'c-2': 'review-2'}
        result = accepted_claim_set(history, review_ids, history=None, **self.batch_options())
        self.assertEqual([item['claim_id'] for item in result['accepted_claims']], ['c-2'])
        with self.assertRaises(ValueError):
            accepted_claim_set(history, review_ids, history=[self.claim], **self.batch_options())

    def test_reviewed_revision_subset_can_use_complete_host_history(self):
        history = revise_claim(append_claim([], self.claim), 'c-1', {'claim_id': 'c-2', 'text': 'Narrower scope.'},
                               reason='Scope change.', revision_evidence_ids=['ev-1'])
        self.approve(history[-1], review_id='review-2')
        result = accepted_claim_set([history[-1]], {'c-2': 'review-2'}, history=history, **self.batch_options())
        self.assertEqual([item['claim_id'] for item in result['accepted_claims']], ['c-2'])

    def test_missing_approval_fields_and_non_json_approval_fail_closed(self):
        self.approve()
        original = copy.deepcopy(self.reviews['review-1'])
        for key in original:
            self.reviews['review-1'] = copy.deepcopy(original)
            self.reviews['review-1'].pop(key)
            self.assertNotEqual(self.gate()['status'], 'accepted', key)
        self.reviews['review-1'] = {**original, 'extra': float('nan')}
        self.assertEqual(self.gate()['status'], 'candidate')

    def test_invalid_mode_does_not_return_non_json_objects(self):
        self.approve()
        result = self.gate(mode=object())
        self.assertEqual(result['status'], 'rejected')
        self.assertIsNone(json.loads(json.dumps(result))['mode'])

    def test_history_and_gate_outputs_do_not_mutate_inputs(self):
        self.approve()
        inputs = copy.deepcopy([self.claim, self.evidence, self.reviews])
        result = self.gate()
        result['claim']['text'] = 'Mutation of returned copy'
        result['evidence'][0]['context']['text'] = 'Mutation of returned evidence'
        self.assertEqual([self.claim, self.evidence, self.reviews], inputs)
        history = append_claim([], self.claim)
        view = history_claim(history, 'c-1')
        view['text'] = 'Mutation of projection'
        self.assertEqual(history[0]['text'], self.claim['text'])

    def test_json_roundtrip_preserves_contract_and_meaning(self):
        self.approve()
        original = self.gate()
        claim = json.loads(json.dumps(self.claim))
        result = self.gate(claim)
        self.assertEqual(json.loads(json.dumps(result)), original)
        history = revise_claim(append_claim([], claim), 'c-1', {'claim_id': 'c-2', 'text': 'Narrow'}, reason='Narrow', revision_evidence_ids=['ev-1'])
        self.assertEqual(json.loads(json.dumps(history)), history)

    def test_non_json_and_malformed_data_fail_closed(self):
        for claim in (None, [], {**self.claim, 'text': float('nan')},
                      {**self.claim, 'supporting_evidence_ids': 'ev-1'},
                      {**self.claim, 'supporting_evidence_ids': ['ev-1', 'ev-1']},
                      {**self.claim, 'limitations': [object()]},
                      {**self.claim, 'presentation': {'certainty': 'asserted', 'quotations': [], 'unreviewed': 'extra'}}):
            with self.subTest(claim=type(claim).__name__):
                self.assertEqual(final_claim_gate(claim)['status'], 'rejected')

    def test_core_import_and_gate_need_no_sqlite_or_shell(self):
        self.approve()
        code = '''
import builtins, json, sys
original = builtins.__import__
def isolated(name, *args, **kwargs):
    if name in {'sqlite3', 'subprocess'} or name.startswith('corpus_research.pointer_export'):
        raise ImportError('disabled host capability')
    return original(name, *args, **kwargs)
builtins.__import__ = isolated
from corpus_research.claims import final_claim_gate
claim, evidence, reviews = json.load(sys.stdin)
result = final_claim_gate(claim, review_id='review-1', evidence_reader=evidence.get, assessment_reader=reviews.get)
assert result['status'] == 'accepted', result
assert final_claim_gate(claim)['status'] == 'candidate'
'''
        result = subprocess.run([sys.executable, '-c', code], input=json.dumps([self.claim, self.evidence, self.reviews]),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
