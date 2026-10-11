from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest

from corpus_research.claims import (
    accepted_claim_set, append_claim, claim_subject, final_claim_gate,
    history_claim, make_claim, revise_claim, synthesis_item, verify_synthesis,
)
from corpus_research.counterevidence import (
    ACTIONS, INDEPENDENCE_STATES, SEARCH_DIRECTIONS, assess_counterevidence,
    make_counterevidence_plan, search_counterevidence, source_independence,
)
from corpus_research.verification import evidence_gate, make_evidence_record


# Invented source text and host oracles; these are not scholarly evidence.
PASSAGES = ['All fixture reports describe a blue lamp.', 'One fixture report describes a red lamp.']


def fixture(evidence_id, *, segment=1, repository='fixture/source', path='work.txt',
            corpus='fixture', klass='authoritative_structured', role='translation_main', witness='Fixture edition'):
    header = {'work_id': 'fixture-work', 'language': 'en', 'text_role': role, 'witness': witness}
    content = json.dumps(header) + '\n' + '\n'.join(PASSAGES) + '\n'
    location = {**json.loads(content.splitlines()[0]), 'segment_id': f'fixture-work:{segment}', 'sequence_no': segment}
    quotation = None if klass == 'metadata_relationship' else PASSAGES[segment-1]
    contract = {corpus: {'repository': repository, 'repo_path': 'fixture/source',
                         'source_sha': '1'*40, 'evidence_class': klass}}
    candidate = make_evidence_record({**location, 'corpus': corpus, 'repository': repository,
        'source_sha': '1'*40, 'source_path': path, 'evidence_class': klass}, contract,
        evidence_id=evidence_id, quotation=quotation)
    def source_reader(request):
        if any(request.get(key) != value for key, value in (
            ('repository', repository), ('source_sha', '1'*40), ('source_path', path))):
            return None
        index = next((i for i in range(1, 3) if request.get('segment_id') == f'fixture-work:{i}'), None)
        if index is None:
            return None
        text = content.splitlines()[index]
        start = content.index(text)
        return {'repository': repository, 'source_sha': '1'*40, 'source_path': path,
                'content': content, 'location': {**json.loads(content.splitlines()[0]),
                'segment_id': f'fixture-work:{index}', 'sequence_no': index},
                'excerpt_range': [start, start+len(text)], 'context_range': [0, len(content)]}
    source = source_reader({'repository': repository, 'source_sha': '1'*40, 'source_path': path,
                            'segment_id': location['segment_id']})
    return evidence_gate(candidate, contract, source, source_reader=source_reader,
                         use='relationship' if klass == 'metadata_relationship' else 'textual')


class CounterevidenceTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {'ev-1': fixture('ev-1'), 'ev-2': fixture('ev-2', segment=2)}
        self.assertTrue(all(record['status'] == 'VERIFIED' for record in self.evidence.values()))
        self.claim = make_claim({'claim_id': 'c-1', 'run_id': 'run-1',
            'text': 'All fixture reports describe a blue lamp.', 'claim_type': 'textual',
            'supporting_evidence_ids': ['ev-1'], 'limitations': ['Fixture scope only.'],
            'presentation': {'certainty': 'tentative', 'quotations': []}})
        self.scope = {'corpora': ['fixture'], 'source_revisions': [{
            'corpus': 'fixture', 'repository': 'fixture/source', 'source_sha': '1'*40}],
            'constraints': ['Only the two fixture passages.']}
        self.steps = [{'step_id': 's-1', 'direction': 'exception', 'operation': 'search',
                       'query': 'red lamp', 'corpus': 'fixture', 'target_id': None}]
        self.history = append_claim([], self.claim)
        self.dependencies, self.reviews = {}, {}
        self.configure_search()

    def configure_search(self, *, hits=True):
        self.plan = make_counterevidence_plan(self.claim, search_id='search-1', scope=self.scope,
            steps=self.steps, unchecked_scope=['Other works and traditions have not been checked.'])
        self.receipt = {'step_id': 's-1', 'status': 'executed', 'complete': True,
            'checked_scope': copy.deepcopy(self.scope), 'limitations': [], 'candidates': [
                {'candidate_id': 'hit-1', 'evidence_id': 'ev-2', 'pointer': {'segment_id': 'fixture-work:2'}}] if hits else []}
        # This independently configured execution oracle stands in for a host
        # that ran the approved bounded query. Proposal flags never select it.
        self.executions = {'search-1': {'search_id': 'search-1',
            'plan': {key: copy.deepcopy(value) for key, value in self.plan.items() if key != 'status'},
            'reviewer': 'fixture-search-policy', 'rationale': 'Approved exception search in this fixture only.',
            'steps': [self.receipt]}}

    def options(self, **overrides):
        return {'search_reader': self.executions.get, 'evidence_reader': self.evidence.get, **overrides}

    def search(self, **overrides):
        return search_counterevidence(self.plan, **self.options(**overrides))

    def dependency_reader(self, request):
        return self.dependencies.get(tuple(request['evidence_ids']))

    def independence(self, ids=None, **overrides):
        return source_independence(ids or ['ev-1', 'ev-2'], **{
            'evidence_reader': self.evidence.get, 'dependency_reader': self.dependency_reader, **overrides})

    def pair(self, left, right, relation, *, derived=None):
        self.dependencies[left, right] = {'evidence': [copy.deepcopy(self.evidence[key]['evidence']) for key in (left, right)],
            'relationship': relation, 'derived_evidence_id': derived, 'basis': 'Reviewed pinned fixture source provenance.',
            'reviewer': 'fixture-dependency-reviewer', 'rationale': 'Software fixture relation approved by host.'}

    def approve(self, *, action='narrow', level='UNSUPPORTED', review_id='review-1', scope='research'):
        searched = self.search()
        candidate = copy.deepcopy(self.claim)
        candidate['counter_evidence_ids'] = list(dict.fromkeys(candidate['counter_evidence_ids'] + [
            record['evidence_id'] for record in searched['verified_evidence']]))
        ids = list(dict.fromkeys(candidate['supporting_evidence_ids'] + candidate['counter_evidence_ids']))
        independence = self.independence(ids)
        self.reviews[review_id] = {'review_id': review_id, 'claim': claim_subject(candidate),
            'evidence': [copy.deepcopy(self.evidence[key]['evidence']) for key in ids], 'atomic': True,
            'support_level': level, 'scope': scope, 'evidence_uses': [{'evidence_id': key,
            'basis': 'textual_report', 'justification': 'Approved fixture use.'} for key in ids],
            'required_limitations': ['Fixture scope only.'], 'max_certainty': 'tentative',
            'reviewer': 'authenticated-fixture-reviewer', 'rationale': 'Reviewed fixture claim and counters.',
            'counterevidence_review': {'search': searched, 'independence': independence,
            'findings': [{'evidence_id': key, 'effect': 'limits' if action != 'keep' else 'irrelevant',
                'rationale': 'Limits the universal fixture wording.' if action != 'keep' else 'Not adverse in this scope.'}
                for key in candidate['counter_evidence_ids']], 'action': action,
            'rationale': 'Restrict the wording to the passage actually checked.',
            'prior_review_id': 'prior-review' if action == 'lower_support' else None,
            'revision': {'claim_id': 'c-2', 'text': 'The first fixture passage describes a blue lamp.'}
                if action in ('narrow', 'rewrite') else None}}
        if action == 'lower_support':
            prior = copy.deepcopy(self.reviews[review_id])
            original_ids = list(dict.fromkeys(self.claim['supporting_evidence_ids'] + self.claim['counter_evidence_ids']))
            prior.update(review_id='prior-review', claim=claim_subject(self.claim), support_level='DIRECT',
                         evidence=[copy.deepcopy(self.evidence[key]['evidence']) for key in original_ids],
                         evidence_uses=[use for use in prior['evidence_uses'] if use['evidence_id'] in original_ids])
            prior.pop('counterevidence_review')
            self.reviews['prior-review'] = prior
        return candidate

    def assess(self, **overrides):
        return assess_counterevidence(self.claim, self.plan, **{
            **self.options(), 'dependency_reader': self.dependency_reader,
            'assessment_reader': self.reviews.get, 'review_id': 'review-1', **overrides})

    def history_reader(self, request):
        return {**request, 'complete': True, 'history': copy.deepcopy(self.history)}

    def gate_options(self, **overrides):
        return {'evidence_reader': self.evidence.get, 'assessment_reader': self.reviews.get,
                'history_reader': self.history_reader, **overrides}

    def test_same_source_citations_count_once(self):
        result = self.independence()
        self.assertEqual(result['pairs'][0]['relationship'], 'same_source_family')
        self.assertEqual(result['independent_source_count'], 1)

    def test_repeated_evidence_id_count_once(self):
        self.assertEqual(self.independence(['ev-1', 'ev-1'])['independent_source_count'], 1)

    def test_derived_source_is_not_an_independent_witness(self):
        self.evidence['ev-2'] = fixture('ev-2', repository='fixture/derived', klass='computational_segmented')
        self.pair('ev-1', 'ev-2', 'derived_from', derived='ev-2')
        result = self.independence()
        self.assertEqual(result['pairs'][0]['derived_evidence_id'], 'ev-2')
        self.assertEqual(result['independent_source_count'], 1)
        self.assertEqual(result['evidence'][1]['evidence_class'], 'computational_segmented')

    def test_same_family_metadata_relation_is_preserved(self):
        self.evidence['ev-2'] = fixture('ev-2', repository='fixture/other')
        self.pair('ev-1', 'ev-2', 'same_source_family')
        self.assertEqual(self.independence()['independent_source_count'], 1)

    def test_unknown_different_repositories_stay_uncertain(self):
        self.evidence['ev-2'] = fixture('ev-2', repository='fixture/other')
        result = self.independence()
        self.assertEqual(result['pairs'][0]['relationship'], 'uncertain')
        self.assertIsNone(result['independent_source_count'])

    def test_identical_words_do_not_prove_derivation(self):
        self.evidence['ev-2'] = fixture('ev-2', repository='fixture/other')
        self.assertEqual(self.evidence['ev-1']['evidence']['context'], self.evidence['ev-2']['evidence']['context'])
        self.assertEqual(self.independence()['pairs'][0]['relationship'], 'uncertain')

    def test_approved_independent_sources_can_count_separately(self):
        self.evidence['ev-2'] = fixture('ev-2', repository='fixture/other')
        self.pair('ev-1', 'ev-2', 'independent')
        self.assertEqual(self.independence()['independent_source_count'], 2)

    def test_partial_dependence_has_no_exact_independent_count(self):
        self.evidence['ev-2'] = fixture('ev-2', repository='fixture/other')
        self.pair('ev-1', 'ev-2', 'partially_dependent')
        self.assertIsNone(self.independence()['independent_source_count'])

    def test_uncertain_approved_relation_is_not_promoted(self):
        self.evidence['ev-2'] = fixture('ev-2', repository='fixture/other')
        self.pair('ev-1', 'ev-2', 'uncertain')
        self.assertIsNone(self.independence()['independent_source_count'])
        self.assertEqual(len(INDEPENDENCE_STATES), 5)

    def test_independent_approval_cannot_override_same_source(self):
        self.pair('ev-1', 'ev-2', 'independent')
        self.assertEqual(self.independence()['status'], 'REJECTED')

    def test_dependency_approval_binds_full_snapshots(self):
        self.evidence['ev-2'] = fixture('ev-2', repository='fixture/other')
        self.pair('ev-1', 'ev-2', 'independent')
        self.evidence['ev-2']['evidence']['context']['after'] += ' Changed context.'
        self.assertIsNone(self.independence()['independent_source_count'])

    def test_dependency_reader_receives_ids_only(self):
        requests = []
        def reader(request):
            requests.append(request)
            return None
        self.independence(dependency_reader=reader)
        self.assertEqual(requests, [{'evidence_ids': ['ev-1', 'ev-2']}])

    def test_missing_evidence_cannot_count_sources(self):
        result = self.independence(evidence_reader=None)
        self.assertEqual(result['status'], 'UNVERIFIED')
        self.assertIsNone(result['independent_source_count'])

    def test_derivation_cycles_and_family_conflicts_rejected(self):
        self.evidence['ev-2'] = fixture('ev-2', repository='fixture/two')
        self.evidence['ev-3'] = fixture('ev-3', repository='fixture/three')
        self.pair('ev-1', 'ev-2', 'derived_from', derived='ev-1')
        self.pair('ev-1', 'ev-3', 'derived_from', derived='ev-3')
        self.pair('ev-2', 'ev-3', 'derived_from', derived='ev-2')
        self.assertEqual(self.independence(['ev-1', 'ev-2', 'ev-3'])['status'], 'REJECTED')
        self.pair('ev-1', 'ev-3', 'independent')
        self.assertEqual(self.independence(['ev-1', 'ev-2', 'ev-3'])['status'], 'REJECTED')

    def test_plan_only_does_not_attest_execution(self):
        forged = {**self.plan, 'completed': True, 'verified': True, 'no_counterevidence': True}
        result = search_counterevidence(forged, evidence_reader=self.evidence.get)
        self.assertEqual(result['status'], 'UNVERIFIED')
        self.assertFalse(result['execution_complete'])
        self.assertIsNone(result['summary'])

    def test_all_seven_search_directions_representable(self):
        self.assertEqual(len(SEARCH_DIRECTIONS), 7)
        for direction in SEARCH_DIRECTIONS:
            plan = make_counterevidence_plan(self.claim, search_id='search-x', scope=self.scope,
                steps=[{**self.steps[0], 'direction': direction}], unchecked_scope=[])
            self.assertEqual(plan['status'], 'PLANNED')

    def test_existing_relation_variant_context_operations_representable(self):
        for operation in ('context', 'evidence', 'parallels', 'variants', 'resolve', 'work'):
            plan = make_counterevidence_plan(self.claim, search_id='search-x', scope=self.scope,
                steps=[{**self.steps[0], 'operation': operation, 'query': None, 'target_id': 'fixture-work'}], unchecked_scope=[])
            self.assertEqual(plan['steps'][0]['operation'], operation)

    def test_invalid_scope_steps_and_plan_fail_closed(self):
        for field, value in (('search_id', ''), ('steps', []), ('unchecked_scope', None),
                             ('scope', {}), ('claim', None)):
            self.assertEqual(search_counterevidence({**self.plan, field: value})['status'], 'REJECTED')
        for field, value in (('operation', 'scan_all'), ('direction', 'anything'), ('corpus', 'unknown'),
                             ('query', None), ('target_id', 'wrong')):
            self.assertEqual(search_counterevidence({**self.plan, 'steps': [{**self.steps[0], field: value}]})['status'], 'REJECTED')

    def test_host_execution_reader_receives_only_search_id(self):
        requests = []
        def reader(key):
            requests.append(key)
            return self.executions.get(key)
        self.assertEqual(self.search(search_reader=reader)['status'], 'SEARCHED')
        self.assertEqual(requests, ['search-1'])

    def test_unopened_search_hit_remains_unverified(self):
        self.receipt['candidates'][0]['evidence_id'] = None
        result = self.search()
        self.assertTrue(result['execution_complete'])
        self.assertEqual(result['status'], 'UNVERIFIED')
        self.assertEqual(result['verified_evidence'], [])
        self.assertIsNone(result['summary'])

    def test_search_hit_with_forged_a_status_is_not_verified(self):
        self.evidence['ev-2'] = {'status': 'VERIFIED', 'evidence': {'state': 'VERIFIED'}}
        self.assertEqual(self.search()['status'], 'UNVERIFIED')

    def test_verified_source_is_not_automatically_semantic_counterevidence(self):
        result = self.search()
        self.assertEqual(result['status'], 'SEARCHED')
        self.assertEqual(len(result['verified_evidence']), 1)
        assessed = self.assess()
        self.assertEqual(assessed['status'], 'UNVERIFIED')
        self.assertIsNone(assessed['decision'])

    def test_failed_not_run_incomplete_and_truncated_steps_stay_pending(self):
        for update in ({'status': 'failed', 'candidates': [], 'complete': False},
                       {'status': 'not_run', 'candidates': [], 'complete': False},
                       {'complete': False}, {'limitations': ['truncated results']}):
            original = copy.deepcopy(self.receipt)
            self.receipt.update(update)
            result = self.search()
            self.assertEqual(result['status'], 'UNVERIFIED')
            self.assertFalse(result['execution_complete'])
            self.receipt.clear()
            self.receipt.update(original)

    def test_missing_extra_duplicate_step_receipts_fail_closed(self):
        for receipts in ([], [self.receipt, self.receipt], [{**self.receipt, 'step_id': 'other'}]):
            self.executions['search-1']['steps'] = receipts
            self.assertNotEqual(self.search()['status'], 'SEARCHED')

    def test_scope_pins_constraints_and_claim_changes_invalidate_execution(self):
        for field, value in (('claim', {**self.plan['claim'], 'text': 'Different claim.'}),
                             ('scope', {**self.scope, 'constraints': ['Much wider scope.']})):
            changed = {**self.plan, field: value}
            self.assertEqual(search_counterevidence(changed, **self.options())['status'], 'UNVERIFIED')
        self.receipt['checked_scope']['source_revisions'][0]['source_sha'] = '2'*40
        self.assertEqual(self.search()['status'], 'REJECTED')

    def test_no_hits_is_only_a_bounded_statement(self):
        self.configure_search(hits=False)
        result = self.search()
        self.assertEqual(result['status'], 'SEARCHED')
        self.assertIn('trong các truy vấn và phạm vi đã kiểm', result['summary'])
        self.assertIn('không kết luận', result['summary'])
        self.assertEqual(result['plan']['unchecked_scope'], self.plan['unchecked_scope'])
        self.receipt['complete'] = False
        self.assertIsNone(self.search()['summary'])

    def test_out_of_scope_evidence_is_rejected(self):
        self.evidence['ev-2'] = fixture('ev-2', corpus='outside')
        self.assertEqual(self.search()['status'], 'REJECTED')

    def test_metadata_is_not_quotation_or_primary_text(self):
        self.evidence['ev-2'] = fixture('ev-2', klass='metadata_relationship', role='relationship')
        self.approve(action='keep', level='DIRECT')
        result = self.assess()
        self.assertEqual(result['search']['verified_evidence'][0]['evidence_class'], 'metadata_relationship')
        self.assertIsNone(result['search']['verified_evidence'][0]['quotation'])
        self.assertEqual(result['status'], 'REJECTED')
        self.assertEqual(result['assessment']['checks']['type:ev-2']['status'], 'FAIL')

    def test_reviewed_counter_can_require_narrowing(self):
        self.approve()
        result = self.assess()
        self.assertEqual(result['status'], 'REVISION_REQUIRED')
        self.assertEqual(result['revision_proposal']['supersedes_claim_id'], 'c-1')
        self.assertEqual(result['revision_proposal']['counter_evidence_ids'], ['ev-2'])
        self.assertIsNone(result['revision_proposal']['verification_status'])
        self.assertEqual(result['revision_proposal']['status'], 'candidate')

    def test_reviewed_keep_lower_unsupported_contradicted_reject_and_rewrite(self):
        self.assertEqual(len(ACTIONS), 7)
        for action, level, status in (('keep', 'DIRECT', 'ASSESSED'), ('lower_support', 'WEAK', 'ASSESSED'),
            ('unsupported', 'UNSUPPORTED', 'ASSESSED'), ('contradicted', 'CONTRADICTED', 'ASSESSED'),
            ('reject', 'UNSUPPORTED', 'REJECTED'), ('rewrite', 'WEAK', 'REVISION_REQUIRED')):
            with self.subTest(action=action):
                self.approve(action=action, level=level)
                result = self.assess()
                self.assertEqual(result['status'], status)
                self.assertEqual(result['claim']['verification_status'], level)
                self.assertEqual(result['claim']['status'], 'candidate')

    def test_wrong_action_level_or_unjustified_change_is_rejected(self):
        for action, level in (('narrow', 'DIRECT'), ('lower_support', 'DIRECT'), ('unsupported', 'STRONG'),
                             ('contradicted', 'WEAK'), ('reject', 'DIRECT')):
            self.approve(action=action, level=level)
            self.assertEqual(self.assess()['status'], 'REJECTED')
        self.approve()
        self.reviews['review-1']['counterevidence_review']['findings'][0]['effect'] = 'irrelevant'
        self.assertEqual(self.assess()['status'], 'REJECTED')

    def test_wrong_revision_id_or_unchanged_wording_cannot_create_revision(self):
        for field, value in (('claim_id', 'c-1'), ('text', self.claim['text'])):
            self.approve()
            self.reviews['review-1']['counterevidence_review']['revision'][field] = value
            result = self.assess()
            self.assertEqual(result['status'], 'REJECTED')
            self.assertIsNone(result['revision_proposal'])

    def test_old_approval_and_forged_impact_json_have_no_authority(self):
        self.approve()
        forged = {**self.claim, 'counterevidence_review': self.reviews['review-1']['counterevidence_review'],
                  'completed': True, 'approved': True, 'independence_status': 'independent'}
        result = assess_counterevidence(forged, self.plan, **self.options())
        self.assertEqual(result['status'], 'UNVERIFIED')
        self.assertIsNone(result['decision'])

    def test_changed_search_receipt_invalidates_impact_approval(self):
        self.approve()
        self.receipt['candidates'][0]['pointer']['new_hint'] = 'Changed search observation.'
        self.assertEqual(self.assess()['status'], 'UNVERIFIED')

    def test_changed_source_invalidates_impact_approval(self):
        self.approve()
        self.evidence['ev-2']['evidence']['context']['after'] += ' New evidence context.'
        self.assertEqual(self.assess()['status'], 'UNVERIFIED')

    def test_missing_findings_or_rationale_cannot_authorize_impact(self):
        for field, value in (('findings', []), ('rationale', ''), ('action', 'approved'), ('revision', None)):
            self.approve()
            self.reviews['review-1']['counterevidence_review'][field] = value
            self.assertNotEqual(self.assess()['status'], 'REVISION_REQUIRED')

    def test_missing_failed_and_noncallable_capabilities_fail_closed(self):
        self.approve()
        def failed(_):
            raise OSError('fixture channel failed')
        for field in ('search_reader', 'evidence_reader', 'assessment_reader'):
            for reader in (None, failed, {}, lambda _: None, lambda _: []):
                with self.subTest(field=field, reader=type(reader).__name__):
                    self.assertNotIn(self.assess(**{field: reader})['status'], ('ASSESSED', 'REVISION_REQUIRED'))

    def test_research_still_pending_and_quick_uses_original_b_gate(self):
        candidate = self.approve(action='keep', level='DIRECT', scope='narrow_lookup')
        self.history = append_claim([], candidate)
        options = self.gate_options()
        self.assertEqual(final_claim_gate(candidate, mode='quick', review_id='review-1', **options)['status'], 'accepted')
        self.assertEqual(final_claim_gate(candidate, mode='research', review_id='review-1', **options)['status'], 'candidate')

    def test_narrowing_end_to_end_preserves_history_and_blocks_old_publication(self):
        self.approve()
        before = copy.deepcopy(self.history)
        result = self.assess()
        revision = result['revision_proposal']
        updated = revise_claim(self.history, 'c-1', revision, reason=revision['revision_reason'],
                               revision_evidence_ids=revision['revision_evidence_ids'])
        self.assertEqual(self.history, before)
        self.assertEqual(updated[0], before[0])
        self.assertEqual(history_claim(updated, 'c-1')['status'], 'superseded')
        self.history = updated
        self.assertEqual(final_claim_gate(updated[-1], review_id='review-1', **self.gate_options())['status'], 'candidate')
        # Host separately approves the new narrow subject through B; C did not.
        old_review = copy.deepcopy(self.reviews['review-1'])
        new_review = {**old_review, 'review_id': 'review-2', 'claim': claim_subject(updated[-1]),
                      'support_level': 'DIRECT', 'scope': 'narrow_lookup'}
        new_review.pop('counterevidence_review')
        self.reviews['review-2'] = new_review
        self.assertEqual(final_claim_gate(updated[-1], review_id='review-2', **self.gate_options())['status'], 'accepted')
        # Preserve a still-valid old B approval: only host history removes C1.
        self.reviews['old-review'] = {**old_review, 'review_id': 'old-review', 'claim': claim_subject(self.claim),
            'evidence': [self.evidence['ev-1']['evidence']], 'support_level': 'DIRECT', 'scope': 'narrow_lookup',
            'evidence_uses': [old_review['evidence_uses'][0]]}
        old = final_claim_gate(self.claim, review_id='old-review', **self.gate_options())
        self.assertEqual(old['status'], 'superseded')
        self.assertEqual(accepted_claim_set([self.claim], {'c-1': 'old-review'}, **self.gate_options())['accepted_claims'], [])
        self.assertEqual(verify_synthesis([synthesis_item(old['claim'])], [self.claim], {'c-1': 'old-review'},
            **self.gate_options())['status'], 'REJECTED')

    def test_preexisting_counters_survive_revision(self):
        self.evidence['old-counter'] = fixture('old-counter', segment=2)
        self.claim['counter_evidence_ids'] = ['old-counter']
        self.history = append_claim([], self.claim)
        self.configure_search()
        self.approve()
        proposal = self.assess()['revision_proposal']
        result = revise_claim(self.history, 'c-1', proposal, reason=proposal['revision_reason'],
                               revision_evidence_ids=proposal['revision_evidence_ids'])
        self.assertEqual(result[-1]['counter_evidence_ids'], ['old-counter', 'ev-2'])

    def test_true_independent_claims_are_not_superseded(self):
        candidate = self.approve(action='keep', level='DIRECT', scope='narrow_lookup')
        other = {**candidate, 'claim_id': 'independent-claim', 'text': 'Another narrow fixture claim.'}
        self.history = append_claim(append_claim([], candidate), other)
        self.reviews['review-other'] = {**copy.deepcopy(self.reviews['review-1']), 'review_id': 'review-other',
                                        'claim': claim_subject(other)}
        result = accepted_claim_set([candidate, other], {'c-1': 'review-1', 'independent-claim': 'review-other'},
                                    **self.gate_options())
        self.assertEqual([item['status'] for item in result['results']], ['accepted', 'accepted'])

    def test_json_roundtrip_and_outputs_do_not_mutate_host_inputs(self):
        self.approve()
        before = copy.deepcopy([self.claim, self.plan, self.evidence, self.executions, self.reviews, self.dependencies])
        result = self.assess()
        self.assertEqual(json.loads(json.dumps(result)), result)
        result['search']['plan']['unchecked_scope'].append('Output mutation')
        result['revision_proposal']['text'] = 'Output mutation'
        self.assertEqual([self.claim, self.plan, self.evidence, self.executions, self.reviews, self.dependencies], before)

    def test_no_sqlite_shell_or_retrieval_import_required(self):
        self.approve()
        code = '''
import builtins, json, sys
original = builtins.__import__
def isolated(name, *args, **kwargs):
    if name in {'sqlite3', 'subprocess'} or name.endswith(('retrieval', 'index', 'pointer_export')):
        raise ImportError('disabled')
    return original(name, *args, **kwargs)
builtins.__import__ = isolated
from corpus_research.counterevidence import assess_counterevidence, search_counterevidence, source_independence
assert search_counterevidence({})['status'] == 'REJECTED'
assert source_independence(['id'])['status'] == 'UNVERIFIED'
claim, plan, evidence, executions, reviews = json.load(sys.stdin)
result = assess_counterevidence(claim, plan, review_id='review-1',
    evidence_reader=evidence.get, search_reader=executions.get, assessment_reader=reviews.get)
assert result['status'] == 'REVISION_REQUIRED', result
'''
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True,
            input=json.dumps([self.claim, self.plan, self.evidence, self.executions, self.reviews]))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_or_false_prior_approval_cannot_lower_support(self):
        self.approve(action='lower_support', level='WEAK')
        self.reviews.pop('prior-review')
        self.assertEqual(self.assess()['status'], 'UNVERIFIED')
        self.approve(action='lower_support', level='STRONG')
        self.reviews['prior-review']['support_level'] = 'WEAK'
        self.assertEqual(self.assess()['status'], 'REJECTED')

    def test_malformed_dependency_channel_never_grants_independence(self):
        self.evidence['ev-2'] = fixture('ev-2', repository='fixture/other')
        self.pair('ev-1', 'ev-2', 'independent')
        original = copy.deepcopy(self.dependencies['ev-1', 'ev-2'])
        def failed(_):
            raise OSError('failed dependency channel')
        for reader in (None, {}, failed, lambda _: [], lambda _: {**original, 'extra': float('nan')}):
            self.assertIsNone(self.independence(dependency_reader=reader)['independent_source_count'])
        for field, value in (('relationship', []), ('basis', ''), ('derived_evidence_id', 'ev-1'),
                             ('reviewer', None), ('evidence', [])):
            self.dependencies['ev-1', 'ev-2'] = {**original, field: value}
            self.assertIsNone(self.independence()['independent_source_count'])

    def test_false_independence_labels_and_citation_scores_are_ignored(self):
        self.evidence['ev-2'] = fixture('ev-2', repository='fixture/other')
        self.evidence['ev-1']['independent'] = True
        self.evidence['ev-1']['score'] = 10**30
        self.evidence['ev-2']['independence_status'] = 'independent'
        self.assertIsNone(self.independence()['independent_source_count'])

    def test_unknown_relation_does_not_erase_observed_same_source(self):
        self.pair('ev-1', 'ev-2', 'uncertain')
        result = self.independence()
        self.assertEqual(result['pairs'][0]['relationship'], 'same_source_family')
        self.assertEqual(result['independent_source_count'], 1)

    def test_partial_scope_is_kept_but_not_reported_complete(self):
        self.scope['corpora'].append('other')
        self.scope['source_revisions'].append({'corpus': 'other', 'repository': 'fixture/other', 'source_sha': '2'*40})
        self.configure_search()
        checked = copy.deepcopy(self.scope)
        checked['corpora'].remove('other')
        checked['source_revisions'].pop()
        self.receipt.update(checked_scope=checked, complete=False)
        result = self.search()
        self.assertEqual(result['status'], 'UNVERIFIED')
        self.assertEqual(result['attempts'][0]['checked_scope'], checked)
        self.receipt['complete'] = True
        self.assertEqual(self.search()['status'], 'REJECTED')

    def test_missing_checked_scope_cannot_certify_countersearch(self):
        self.receipt.update(checked_scope=None, complete=False)
        self.assertEqual(self.search()['status'], 'UNVERIFIED')
        self.receipt['complete'] = True
        self.assertEqual(self.search()['status'], 'REJECTED')

    def test_conflicting_candidate_identity_rejected(self):
        self.receipt['candidates'].append({**self.receipt['candidates'][0], 'evidence_id': 'ev-1'})
        self.assertEqual(self.search()['status'], 'REJECTED')

    def test_nonjson_execution_or_review_cannot_authorize(self):
        for field in ('search_reader', 'assessment_reader'):
            self.approve()
            record = copy.deepcopy(self.executions['search-1'] if field == 'search_reader' else self.reviews['review-1'])
            result = self.assess(**{field: lambda _: {**record, 'extra': object()}})
            self.assertNotIn(result['status'], ('ASSESSED', 'REVISION_REQUIRED'))
            json.dumps(result)

    def test_old_review_without_c_extension_cannot_assess_counterimpact(self):
        self.approve()
        self.reviews['review-1'].pop('counterevidence_review')
        result = self.assess()
        self.assertEqual(result['assessment']['status'], 'ASSESSED')
        self.assertEqual(result['status'], 'UNVERIFIED')

    def test_mixed_evidence_reads_are_rejected(self):
        self.approve()
        reads = []
        def reader(eid):
            reads.append(eid)
            record = copy.deepcopy(self.evidence.get(eid))
            if eid == 'ev-2' and reads.count('ev-2') >= 3:
                record['evidence']['context']['after'] += ' Changed between readers.'
            return record
        result = self.assess(evidence_reader=reader)
        self.assertEqual(result['status'], 'REJECTED')
        self.assertEqual(result['checks']['evidence_snapshot_binding'], 'FAIL')

    def test_semantic_review_can_find_a_candidate_irrelevant(self):
        self.approve(action='keep', level='DIRECT')
        result = self.assess()
        self.assertEqual(result['decision']['findings'][0]['effect'], 'irrelevant')
        self.assertEqual(result['status'], 'ASSESSED')
        self.assertIsNone(result['revision_proposal'])

    def test_unknown_source_dependence_can_be_acknowledged_without_fake_count(self):
        self.evidence['ev-2'] = fixture('ev-2', path='other-work.txt')
        self.approve()
        result = self.assess()
        self.assertEqual(result['status'], 'REVISION_REQUIRED')
        self.assertEqual(result['independence']['pairs'][0]['relationship'], 'uncertain')
        self.assertIsNone(result['independence']['independent_source_count'])

    def test_unsupported_and_contradicted_assessments_are_rejected_by_b(self):
        for level, action in (('UNSUPPORTED', 'unsupported'), ('CONTRADICTED', 'contradicted')):
            candidate = self.approve(action=action, level=level)
            self.history = append_claim([], candidate)
            self.assertEqual(self.assess()['status'], 'ASSESSED')
            self.assertEqual(final_claim_gate(candidate, mode='research', review_id='review-1',
                                             **self.gate_options())['status'], 'rejected')


if __name__ == '__main__':
    unittest.main()
