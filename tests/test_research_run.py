from __future__ import annotations

import copy
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from corpus_research.claims import (accepted_claim_set, claim_subject, final_claim_gate,
    make_claim, synthesis_item, verify_synthesis)
from corpus_research.counterevidence import (assess_counterevidence, make_counterevidence_plan,
    search_counterevidence, source_independence)
from corpus_research.research_run import RUN_FIELDS, make_research_run
from corpus_research.research_store import ConflictError, ResearchStore
from test_counterevidence import fixture


class ResearchRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'research.sqlite'
        self.time = '2026-10-11T09:00:00+07:00'
        self.scope = {'corpora': ['fixture'], 'source_revisions': [
            {'corpus': 'fixture', 'repository': 'fixture/source', 'source_sha': '1'*40}],
            'constraints': ['Only the two software fixture passages.']}
        self.context = {'main_repository': 'fixture/main', 'main_repository_commit': '3'*40,
            'environment': 'local', 'remote_repository': None, 'remote_repository_commit': None,
            'remote_root': None, 'source_revisions': copy.deepcopy(self.scope['source_revisions']),
            'model_identifier': None, 'verification_config': None}
        self.proposal = {'run_id': 'r-1', 'question': 'What do the fixture reports say?',
            'mode': 'quick', 'scope': copy.deepcopy(self.scope), 'queries': ['blue lamp'],
            'search_hypotheses': ['Try the fixture phrase.'], 'limitations': ['Software fixture only.']}
        self.evidence = {'ev-1': fixture('ev-1'), 'ev-2': fixture('ev-2', segment=2)}
        self.reviews, self.executions = {}, {}
        self.requests = []
        self.store = self.open_store()

    def open_store(self, **overrides):
        def context_reader(run_id):
            self.requests.append(run_id)
            return copy.deepcopy(self.context)
        return ResearchStore(self.path, **{
            'context_reader': context_reader, 'evidence_reader': self.evidence.get,
            'assessment_reader': self.reviews.get, 'search_reader': self.executions.get,
            'clock': lambda: self.time, **overrides})

    def create(self, **changes):
        return self.store.create_run({**self.proposal, **changes})

    def claim(self, claim_id='c-1', run_id='r-1', **changes):
        return make_claim({'claim_id': claim_id, 'run_id': run_id, 'text': 'The first fixture passage describes a blue lamp.',
            'claim_type': 'textual', 'supporting_evidence_ids': ['ev-1'],
            'limitations': ['Software fixture only.'], 'presentation': {'certainty': 'tentative', 'quotations': []}, **changes})

    def approve(self, claim, review_id=None, *, level='DIRECT', scope='narrow_lookup'):
        rid = review_id or 'b-'+claim['claim_id']
        ids = list(dict.fromkeys(claim['supporting_evidence_ids']+claim['counter_evidence_ids']))
        self.reviews[rid] = {'review_id': rid, 'claim': claim_subject(claim),
            'evidence': [copy.deepcopy(self.evidence[eid]['evidence']) for eid in ids],
            'atomic': True, 'support_level': level, 'scope': scope,
            'evidence_uses': [{'evidence_id': eid, 'basis': 'textual_report', 'justification': 'Fixture textual report.'} for eid in ids],
            'required_limitations': ['Software fixture only.'], 'max_certainty': 'tentative',
            'reviewer': 'fixture-host-approved-reviewer', 'rationale': 'Approved software fixture assessment.'}
        return rid

    def registered(self, *, run_id='r-1', claim_id='c-1', mode='quick', **changes):
        run = self.create(run_id=run_id, mode=mode, **changes)
        claim = self.claim(claim_id, run_id)
        run = self.store.append_claim(run_id, claim, expected_version=run['version'])
        rid = self.approve(claim)
        return run, claim, {claim_id: rid}

    def finalized(self, **changes):
        run, claim, reviews = self.registered(**changes)
        return self.store.finalize(run['run_id'], expected_version=run['version'], review_ids=reviews), claim, reviews

    def counter(self, claim, *, action='keep'):
        sid, rid = 'search-'+claim['claim_id'], 'c-'+claim['claim_id']
        plan = make_counterevidence_plan(claim, search_id=sid, scope=self.scope,
            steps=[{'step_id': 's-1', 'direction': 'exception', 'operation': 'search', 'query': 'red lamp',
                    'corpus': 'fixture', 'target_id': None}], unchecked_scope=['Other works/traditions unchecked.'])
        record = self.evidence['ev-2']['evidence']
        pointer = {key: record[key] for key in ('corpus', 'repository', 'source_sha', 'source_path', 'work_id', 'segment_id')}
        receipt = {'step_id': 's-1', 'status': 'executed', 'complete': True, 'checked_scope': copy.deepcopy(self.scope),
            'candidates': [{'candidate_id': 'hit-'+sid, 'evidence_id': 'ev-2', 'pointer': pointer}], 'limitations': []}
        self.executions[sid] = {'search_id': sid, 'plan': {key: value for key, value in plan.items() if key != 'status'},
            'reviewer': 'fixture-search-host', 'rationale': 'Approved bounded fixture query.', 'steps': [receipt]}
        searched = search_counterevidence(plan, evidence_reader=self.evidence.get, search_reader=self.executions.get)
        enriched = make_claim({**claim, 'counter_evidence_ids': list(dict.fromkeys(claim['counter_evidence_ids']+['ev-2']))})
        self.approve(enriched, rid, level='UNSUPPORTED' if action == 'narrow' else 'DIRECT')
        independence = source_independence(enriched['supporting_evidence_ids']+enriched['counter_evidence_ids'], evidence_reader=self.evidence.get)
        self.reviews[rid]['counterevidence_review'] = {'search': searched, 'independence': independence,
            'findings': [{'evidence_id': eid, 'effect': 'limits' if action == 'narrow' else 'irrelevant',
                          'rationale': 'Reviewed fixture relation to claim.'} for eid in enriched['counter_evidence_ids']],
            'action': action, 'rationale': 'Restrict universal wording to the first fixture passage.', 'prior_review_id': None,
            'revision': {'claim_id': claim['claim_id']+'-new', 'text': 'The first fixture passage reports a blue lamp.'}
                if action == 'narrow' else None}
        return {'claim_id': claim['claim_id'], 'plan': plan, 'review_id': rid}

    def package(self, *, final=False):
        run, claim, reviews = self.finalized() if final else self.registered()
        if not final:
            run = self.store.capture('r-1', expected_version=run['version'], review_ids=reviews)
        exported = self.store.export_review('r-1', expected_version=run['version'], review_questions=['Is this claim supported within the checked scope?'])
        return run, claim, reviews, exported

    def report(self, package, **changes):
        return {'report_id': 'report-1', 'package_id': package['package_id'], 'snapshot_sha256': package['snapshot_sha256'],
            'reviewer': 'declared-second-AI', 'reviewer_role': 'AI', 'reviewed_at': self.time,
            'session': None, 'relationship_to_proposer': 'uncertain', 'unverified': ['Other traditions unchecked.'],
            'comments': [{'claim_id': 'c-1', 'comment': 'Keep the bounded fixture wording.', 'evidence_ids': ['ev-1'],
                          'limitations': ['Software fixture only.'], 'recommendation': 'keep'}], **changes}

    def test_create_draft_has_every_design_field(self):
        run = self.create()
        self.assertTrue(set(RUN_FIELDS).issubset(run))
        self.assertEqual(run['run_status'], 'draft')
        self.assertIsNone(run['finalized_at'])
        self.assertEqual(run['main_repository_commit'], '3'*40)

    def test_missing_required_proposal_identity_is_rejected(self):
        for key in ('run_id', 'question', 'mode', 'scope'):
            proposal = copy.deepcopy(self.proposal)
            proposal.pop(key)
            with self.subTest(key=key), self.assertRaises((ValueError, TypeError)):
                self.store.create_run(proposal)

    def test_missing_host_main_commit_or_source_pins_is_rejected(self):
        for key in ('main_repository_commit', 'source_revisions'):
            original = copy.deepcopy(self.context)
            self.context.pop(key)
            with self.assertRaises(ValueError):
                self.create()
            self.context = original

    def test_local_needs_no_remote_locator(self):
        self.assertIsNone(self.create()['remote_root'])

    def test_connector_requires_all_locator_fields(self):
        self.context.update(environment='connector', remote_repository='fixture/locator', remote_repository_commit='4'*40, remote_root='production/v1')
        for key in ('remote_repository', 'remote_repository_commit', 'remote_root'):
            original = self.context[key]
            self.context[key] = None
            with self.assertRaises(ValueError):
                self.create()
            self.context[key] = original
        self.assertEqual(self.create()['remote_repository_commit'], '4'*40)

    def test_source_pins_and_scope_cannot_override_host(self):
        for field, value in (('source_sha', '2'*40), ('repository', 'fixture/other'), ('corpus', 'outside')):
            proposal = copy.deepcopy(self.proposal)
            proposal['scope']['source_revisions'][0][field] = value
            with self.assertRaises(ValueError):
                self.store.create_run(proposal)

    def test_claimed_status_time_and_versions_have_no_authority(self):
        run = self.create(run_status='finalized', finalized_at='2099-01-01', created_at='2099-01-01',
            main_repository_commit='f'*40, counterevidence_performed=True, approved=True, accepted_claim_ids=['fake'])
        self.assertEqual(run['created_at'], self.time)
        self.assertEqual(run['run_status'], 'draft')
        self.assertEqual(run['main_repository_commit'], '3'*40)
        self.assertEqual(run['accepted_claim_ids'], [])
        self.assertFalse(run['counterevidence_performed'])

    def test_context_reader_gets_only_run_id(self):
        self.create()
        self.assertEqual(self.requests, ['r-1'])

    def test_missing_failed_context_capability_fails_closed(self):
        def failed(_):
            raise OSError('host unavailable')
        for reader in (None, {}, failed, lambda _: {'trusted': True}):
            with self.assertRaises(ValueError):
                self.open_store(context_reader=reader).create_run(self.proposal)

    def test_host_clock_must_be_timezone_aware(self):
        with self.assertRaises(ValueError):
            self.open_store(clock=lambda: '2026-10-11T09:00:00').create_run(self.proposal)

    def test_unknown_private_fields_are_rejected(self):
        for field in ('chain_of_thought', 'internal_reasoning', 'credentials', 'store_path'):
            with self.assertRaises(ValueError):
                self.create(**{field: 'do not store this'})

    def test_json_roundtrip_and_output_mutation_do_not_edit_store(self):
        run = self.create()
        self.assertEqual(json.loads(json.dumps(run)), run)
        run['question'] = 'Output changed'
        self.assertEqual(self.store.get_run('r-1')['question'], self.proposal['question'])

    def test_pure_core_import_does_not_need_sqlite_or_shell(self):
        code = '''
import builtins, json, sys
original = builtins.__import__
def isolated(name, *args, **kwargs):
    if name in {'sqlite3', 'subprocess'}: raise ImportError('disabled')
    return original(name, *args, **kwargs)
builtins.__import__ = isolated
from corpus_research.research_run import make_research_run
proposal, context, now = json.load(sys.stdin)
assert make_research_run(proposal, host_context=context, now=now)['run_status'] == 'draft'
'''
        result = subprocess.run([sys.executable, '-c', code], input=json.dumps([self.proposal, self.context, self.time]),
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_trace_claim_retains_a_provenance_and_assessment(self):
        run, claim, reviews = self.registered()
        self.store.capture('r-1', expected_version=run['version'], review_ids=reviews)
        trace = self.store.trace_claim('r-1', 'c-1')
        self.assertEqual(trace['evidence'][0], self.evidence['ev-1']['evidence'])
        self.assertEqual(trace['assessment']['claim']['verification_status'], 'DIRECT')
        self.assertEqual(trace['missing_evidence_ids'], [])

    def test_missing_evidence_is_recorded_unverified_not_finalized(self):
        run = self.create()
        run = self.store.append_claim('r-1', self.claim(supporting_evidence_ids=['missing']), expected_version=run['version'])
        captured = self.store.capture('r-1', expected_version=run['version'], review_ids={})
        self.assertEqual(captured['checks']['evidence:missing'], 'UNVERIFIED')
        self.assertEqual(self.store.trace_claim('r-1', 'c-1')['missing_evidence_ids'], ['missing'])
        with self.assertRaises(ValueError):
            self.store.finalize('r-1', expected_version=captured['version'], review_ids={})

    def test_evidence_wrong_pin_or_run_cannot_finalize(self):
        for field, value in (('source_sha', '2'*40), ('run_id', 'another-run')):
            run, claim, reviews = self.registered(run_id='run-'+field, claim_id='claim-'+field)
            original = copy.deepcopy(self.evidence['ev-1'])
            self.evidence['ev-1']['evidence'][field] = value
            with self.assertRaises(ValueError):
                self.store.finalize(run['run_id'], expected_version=run['version'], review_ids=reviews)
            self.evidence['ev-1'] = original

    def test_stored_evidence_is_not_a_fresh_approval_channel(self):
        run, claim, reviews = self.finalized()
        self.assertEqual(run['accepted_claim_ids'], ['c-1'])
        result = final_claim_gate(claim, review_id=reviews['c-1'], history_reader=self.store.history_reader)
        self.assertEqual(result['status'], 'candidate')

    def test_retrieval_and_research_reproducibility_are_separate(self):
        run, _, reviews = self.registered()
        captured = self.store.capture('r-1', expected_version=run['version'], review_ids=reviews)
        self.assertEqual(captured['retrieval']['planned_queries'], ['blue lamp'])
        self.assertEqual(captured['retrieval']['actual_countersearches'], [])
        self.assertEqual(len(captured['research']['evidence']), 1)
        self.assertFalse(captured['research']['exact_answer_reproduction'])

    def test_partial_countersearch_retains_actual_and_unchecked_scope(self):
        run, claim, reviews = self.registered(mode='research')
        request = self.counter(claim)
        self.executions[request['plan']['search_id']]['steps'][0]['complete'] = False
        captured = self.store.capture('r-1', expected_version=run['version'], review_ids=reviews, counter_requests=[request])
        search = captured['counterevidence'][0]['result']['search']
        self.assertEqual(search['attempts'][0]['checked_scope'], self.scope)
        self.assertEqual(search['plan']['unchecked_scope'], ['Other works/traditions unchecked.'])
        self.assertFalse(captured['counterevidence_performed'])
        with self.assertRaises(ValueError):
            self.store.finalize('r-1', expected_version=captured['version'], review_ids=reviews, counter_requests=[request])

    def test_failed_countersearch_is_never_performed(self):
        run, claim, reviews = self.registered(mode='research')
        request = self.counter(claim)
        self.executions[request['plan']['search_id']]['steps'][0].update(status='failed', candidates=[], complete=False)
        captured = self.store.capture('r-1', expected_version=run['version'], review_ids=reviews, counter_requests=[request])
        self.assertFalse(captured['counterevidence_performed'])
        self.assertEqual(captured['counterevidence'][0]['result']['search']['attempts'][0]['status'], 'failed')

    def test_counter_request_cannot_cross_run_or_register_unknown_claim(self):
        run, claim, reviews = self.registered()
        request = self.counter(claim)
        request['claim_id'] = 'missing'
        with self.assertRaises(ValueError):
            self.store.capture('r-1', expected_version=run['version'], review_ids=reviews, counter_requests=[request])

    def test_rejected_claim_is_preserved_with_approved_reason(self):
        run, claim, reviews = self.registered()
        self.reviews[reviews['c-1']]['support_level'] = 'CONTRADICTED'
        finalized = self.store.finalize('r-1', expected_version=run['version'], review_ids=reviews)
        self.assertEqual(finalized['rejected_claim_ids'], ['c-1'])
        self.assertEqual(self.store.trace_claim('r-1', 'c-1')['assessment']['assessment']['support_level'], 'CONTRADICTED')

    def test_finalized_run_cannot_be_updated_appended_revised_or_recaptured(self):
        run, claim, reviews = self.finalized()
        operations = [lambda: self.store.update_draft('r-1', {'question': 'new'}, expected_version=run['version']),
            lambda: self.store.append_claim('r-1', self.claim('c-2'), expected_version=run['version']),
            lambda: self.store.revise_claim('r-1', 'c-1', {'claim_id': 'c-2', 'text': 'new'}, reason='new data', revision_evidence_ids=['ev-1'], expected_version=run['version']),
            lambda: self.store.capture('r-1', expected_version=run['version'], review_ids=reviews)]
        for operation in operations:
            with self.assertRaises(ConflictError): operation()
        self.assertEqual(self.store.run_history('r-1')[-1], run)

    def test_snapshot_table_rejects_update_and_delete(self):
        self.finalized()
        for operation in ("UPDATE snapshots SET body='{}'", 'DELETE FROM snapshots'):
            con = sqlite3.connect(self.path)
            try:
                with self.assertRaises(sqlite3.IntegrityError): con.execute(operation)
            finally: con.close()

    def test_research_run_successor_preserves_old_snapshot(self):
        old, _, _ = self.finalized()
        new, _, _ = self.finalized(run_id='r-2', claim_id='c-2', supersedes_run_id='r-1', revision_reason='New fixture information.')
        self.assertEqual(new['supersedes_run_id'], 'r-1')
        self.assertEqual(self.store.run_history('r-1')[-1], old)
        self.assertEqual(self.store.get_run('r-1')['run_status'], 'superseded')
        self.assertEqual(self.store.get_run('r-1')['superseded_by_run_id'], 'r-2')

    def test_revision_requires_reason_and_existing_finalized_predecessor(self):
        self.create()
        for predecessor, reason in (('r-1', None), ('missing', 'new'), ('r-1', 'new')):
            with self.assertRaises(ValueError):
                self.create(run_id='r-2', supersedes_run_id=predecessor, revision_reason=reason)

    def test_duplicate_ids_and_cycles_are_rejected(self):
        self.create()
        with self.assertRaises(ConflictError): self.create()
        with self.assertRaises(ValueError): self.create(run_id='r-2', supersedes_run_id='r-2', revision_reason='cycle')

    def test_two_run_successors_cannot_both_finalize(self):
        self.finalized()
        first, _, rev1 = self.registered(run_id='r-2', claim_id='c-2', supersedes_run_id='r-1', revision_reason='first')
        second, _, rev2 = self.registered(run_id='r-3', claim_id='c-3', supersedes_run_id='r-1', revision_reason='second')
        self.store.finalize('r-2', expected_version=first['version'], review_ids=rev1)
        with self.assertRaises(ConflictError): self.store.finalize('r-3', expected_version=second['version'], review_ids=rev2)
        self.assertEqual(self.store.get_run('r-3')['run_status'], 'draft')

    def test_stale_draft_update_cannot_overwrite_newer_version(self):
        run = self.create()
        self.store.update_draft('r-1', {'question': 'first edit'}, expected_version=run['version'])
        with self.assertRaises(ConflictError): self.store.update_draft('r-1', {'question': 'stale edit'}, expected_version=run['version'])
        self.assertEqual(self.store.get_run('r-1')['question'], 'first edit')

    def test_two_processes_with_same_version_have_one_winner(self):
        self.create()
        code = '''
import os, pathlib, sys, time
from corpus_research.research_store import ResearchStore, ConflictError
path, barrier = sys.argv[1:]
store = ResearchStore(path)
pathlib.Path(barrier, str(os.getpid())).touch()
deadline = time.monotonic()+10
while len(list(pathlib.Path(barrier).iterdir())) < 2:
    if time.monotonic() > deadline: raise RuntimeError('barrier timeout')
    time.sleep(.01)
try:
    store.update_draft('r-1', {'question': str(os.getpid())}, expected_version=1)
    print('saved')
except ConflictError:
    print('conflict')
'''
        barrier = Path(self.temp.name)/'barrier'
        barrier.mkdir()
        children = [subprocess.Popen([sys.executable, '-c', code, str(self.path), str(barrier)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        outputs = [child.communicate(timeout=20) for child in children]
        self.assertEqual([child.returncode for child in children], [0, 0], outputs)
        self.assertEqual(sorted(stdout.strip() for stdout, _ in outputs), ['conflict', 'saved'])
        self.assertEqual(self.store.get_run('r-1')['version'], 2)
        self.assertEqual(len(self.store.run_history('r-1')), 2)

    def test_store_reopens_with_history_and_packages(self):
        run, _, _, exported = self.package(final=True)
        reopened = self.open_store()
        self.assertEqual(reopened.run_history('r-1')[-1], run)
        self.assertEqual(reopened.verify_review_package(exported['json'])['status'], 'MATCHED')

    def test_unrelated_sqlite_database_is_not_modified(self):
        other = Path(self.temp.name)/'corpus.sqlite'
        con = sqlite3.connect(other)
        con.execute('CREATE TABLE records(id INTEGER)')
        con.commit(); con.close()
        before = other.read_bytes()
        with self.assertRaises(ValueError): ResearchStore(other)
        self.assertEqual(other.read_bytes(), before)

    def test_history_reader_is_complete_current_and_scoped(self):
        run, claim, reviews = self.registered()
        revised = self.store.revise_claim('r-1', 'c-1', {'claim_id': 'c-2', 'text': 'Narrow fixture claim.'},
            reason='Fixture revision.', revision_evidence_ids=['ev-1'], expected_version=run['version'])
        response = self.store.history_reader({'claim_id': 'c-1', 'run_id': 'r-1'})
        self.assertTrue(response['complete'])
        self.assertEqual([item['claim_id'] for item in response['history']], ['c-1', 'c-2'])
        self.assertEqual(response['history'], revised['claims'])
        self.assertEqual(self.store.history_reader({'claim_id': 'c-1', 'run_id': 'r-2'}), {})

    def test_caller_truncated_history_cannot_republish_old_claim_on_any_b_path(self):
        run, old, reviews = self.registered()
        self.store.revise_claim('r-1', 'c-1', {'claim_id': 'c-2', 'text': 'New bounded wording.'},
            reason='Fixture correction.', revision_evidence_ids=['ev-1'], expected_version=run['version'])
        options = dict(evidence_reader=self.evidence.get, assessment_reader=self.reviews.get,
            history_reader=self.store.history_reader, history=[old])
        gated = final_claim_gate(old, review_id=reviews['c-1'], **options)
        self.assertEqual(gated['status'], 'superseded')
        self.assertEqual(accepted_claim_set([old], reviews, **options)['accepted_claims'], [])
        self.assertEqual(verify_synthesis([synthesis_item(gated['claim'])], [old], reviews, **options)['status'], 'REJECTED')

    def test_b_revision_still_cannot_cross_run(self):
        run, _, _ = self.registered()
        with self.assertRaises(ValueError):
            self.store.revise_claim('r-1', 'c-1', {'claim_id': 'c-2', 'text': 'new', 'run_id': 'r-2'},
                reason='new run', revision_evidence_ids=['ev-1'], expected_version=run['version'])

    def test_run_replacement_uses_new_claim_ids_and_old_run_cannot_publish(self):
        old, claim, reviews = self.finalized()
        new = self.create(run_id='r-2', supersedes_run_id='r-1', revision_reason='new study')
        with self.assertRaises(ConflictError):
            self.store.append_claim('r-2', self.claim(run_id='r-2'), expected_version=new['version'])
        new = self.store.append_claim('r-2', self.claim('c-2', 'r-2'), expected_version=new['version'])
        rid = self.approve(new['claims'][-1])
        self.store.finalize('r-2', expected_version=new['version'], review_ids={'c-2': rid})
        result = final_claim_gate(claim, review_id=reviews['c-1'], evidence_reader=self.evidence.get,
            assessment_reader=self.reviews.get, history_reader=self.store.history_reader)
        self.assertNotEqual(result['status'], 'accepted')
        with self.assertRaises(ConflictError): self.store.check_publication('r-1', expected_version=old['version'], items=[], review_ids=reviews)

    def test_history_change_after_check_invalidates_publication_version(self):
        run, claim, reviews = self.registered()
        gated = final_claim_gate(claim, review_id=reviews['c-1'], evidence_reader=self.evidence.get,
            assessment_reader=self.reviews.get, history_reader=self.store.history_reader)
        self.assertEqual(gated['status'], 'accepted')
        check = self.store.check_publication('r-1', expected_version=run['version'], items=[synthesis_item(gated['claim'])], review_ids=reviews)
        self.assertFalse(check['publication_authorized'])
        self.store.revise_claim('r-1', 'c-1', {'claim_id': 'c-2', 'text': 'New wording.'},
            reason='Fixture correction.', revision_evidence_ids=['ev-1'], expected_version=run['version'])
        with self.assertRaises(ConflictError):
            self.store.check_publication('r-1', expected_version=run['version'], items=[synthesis_item(gated['claim'])], review_ids=reviews)

    def test_changed_host_pin_blocks_finalization(self):
        run, _, reviews = self.registered()
        self.context['main_repository_commit'] = '5'*40
        with self.assertRaises(ConflictError): self.store.finalize('r-1', expected_version=run['version'], review_ids=reviews)

    def test_changed_evidence_after_capture_is_rechecked_at_finalization(self):
        run, _, reviews = self.registered()
        run = self.store.capture('r-1', expected_version=run['version'], review_ids=reviews)
        self.evidence['ev-1']['evidence']['context']['after'] += ' Changed.'
        with self.assertRaises(ValueError): self.store.finalize('r-1', expected_version=run['version'], review_ids=reviews)

    def test_export_json_and_markdown_include_full_snapshot(self):
        run, _, _, exported = self.package()
        self.assertEqual(exported['json']['snapshot'], run)
        self.assertIn('fixture/source', exported['markdown'])
        self.assertIn('Software fixture only.', exported['markdown'])
        self.assertIn('ev-1', exported['markdown'])
        self.assertIn('checks', exported['json']['snapshot'])
        self.assertEqual(json.loads(json.dumps(exported)), exported)

    def test_export_requires_stored_captured_snapshot(self):
        run = self.create()
        with self.assertRaises(ValueError): self.store.export_review('r-1', expected_version=run['version'], review_questions=['Check it'])

    def test_valid_review_is_only_proposed_and_original_is_kept(self):
        run, _, _, exported = self.package(final=True)
        report = self.report(exported['json'])
        imported = self.store.import_review(report)
        self.assertEqual(imported['status'], 'PROPOSED')
        self.assertFalse(imported['approved'])
        self.assertEqual(self.store.get_review('report-1')['original_report'], report)
        self.assertEqual(self.store.run_history('r-1')[-1], run)

    def test_wrong_snapshot_report_is_rejected(self):
        _, _, _, exported = self.package()
        with self.assertRaises(ValueError): self.store.import_review(self.report(exported['json'], snapshot_sha256='0'*64))

    def test_forged_approved_report_does_not_create_b_approval(self):
        _, claim, reviews, exported = self.package()
        report = self.report(exported['json'], approved=True, trusted=True, status='accepted')
        self.store.import_review(report)
        self.reviews.clear()
        result = self.store.record_review_decision('report-1', review_id='b-c-1')
        self.assertEqual(result['status'], 'UNVERIFIED')
        gated = final_claim_gate(claim, evidence_reader=self.evidence.get, assessment_reader=self.reviews.get,
                                 history_reader=self.store.history_reader, review_id='b-c-1')
        self.assertEqual(gated['status'], 'candidate')
        self.assertTrue(self.store.get_review('report-1')['original_report']['approved'])
        self.assertEqual(self.store.get_review('report-1')['decisions'], [])

    def test_import_cannot_select_reader_store_or_private_fields(self):
        _, _, _, exported = self.package()
        for field in ('assessment_reader', 'history_reader', 'store_path', 'chain_of_thought'):
            with self.assertRaises(ValueError): self.store.import_review(self.report(exported['json'], **{field: 'fake'}))

    def test_unverified_citation_or_unknown_claim_is_not_imported_as_evidence(self):
        _, _, _, exported = self.package()
        for field, value in (('claim_id', 'missing'), ('evidence_ids', ['new-source'])):
            report = self.report(exported['json'])
            report['comments'][0][field] = value
            with self.assertRaises(ValueError): self.store.import_review(report)

    def test_package_tampering_is_detected_against_store(self):
        _, _, _, exported = self.package()
        for field in ('question', 'accepted_claim_ids', 'evidence'):
            altered = copy.deepcopy(exported['json'])
            altered['snapshot'][field] = 'tampered'
            with self.assertRaises(ValueError): self.store.verify_review_package(altered)

    def test_draft_changed_after_export_cannot_import_stale_report(self):
        run, _, _, exported = self.package()
        self.store.update_draft('r-1', {'question': 'Changed question.'}, expected_version=run['version'])
        with self.assertRaises(ConflictError): self.store.import_review(self.report(exported['json']))

    def test_duplicate_report_is_rejected_and_original_immutable(self):
        _, _, _, exported = self.package()
        report = self.report(exported['json'])
        self.store.import_review(report)
        with self.assertRaises(ConflictError): self.store.import_review(report)
        self.assertEqual(self.store.get_review('report-1')['original_report'], report)

    def test_host_decision_uses_existing_b_channel_and_separate_object(self):
        _, _, reviews, exported = self.package(final=True)
        self.store.import_review(self.report(exported['json']))
        rid = reviews['c-1']
        self.reviews[rid]['review_report_decision'] = {'report_id': 'report-1', 'package_id': exported['json']['package_id'],
            'claim_id': 'c-1', 'disposition': 'approve', 'rationale': 'Host approved this review against the stored subject.'}
        result = self.store.record_review_decision('report-1', review_id=rid)
        self.assertEqual(result['status'], 'RECORDED')
        self.assertFalse(result['publication_authorized'])
        read = self.store.get_review('report-1')
        self.assertEqual(len(read['decisions']), 1)
        self.assertEqual(read['original_report']['reviewer'], 'declared-second-AI')

    def test_plain_b_approval_does_not_approve_arbitrary_review_report(self):
        _, _, reviews, exported = self.package()
        self.store.import_review(self.report(exported['json']))
        self.assertEqual(self.store.record_review_decision('report-1', review_id=reviews['c-1'])['status'], 'UNVERIFIED')

    def test_new_claim_needs_new_b_approval(self):
        run, _, reviews = self.registered()
        run = self.store.revise_claim('r-1', 'c-1', {'claim_id': 'c-2', 'text': 'Corrected narrow wording.'},
            reason='Fixture revision.', revision_evidence_ids=['ev-1'], expected_version=run['version'])
        with self.assertRaises(ValueError):
            self.store.finalize('r-1', expected_version=run['version'], review_ids={**reviews, 'c-2': reviews['c-1']})

    def test_quick_b_gate_still_accepts_legitimate_stored_claim(self):
        _, claim, reviews = self.registered()
        self.assertEqual(final_claim_gate(claim, review_id=reviews['c-1'], evidence_reader=self.evidence.get,
            assessment_reader=self.reviews.get, history_reader=self.store.history_reader)['status'], 'accepted')

    def test_research_without_c_cannot_finalize(self):
        run, _, reviews = self.registered(mode='research')
        with self.assertRaises(ValueError): self.store.finalize('r-1', expected_version=run['version'], review_ids=reviews)

    def test_finalized_research_audit_is_not_accepted_research(self):
        run, claim, reviews = self.registered(mode='research')
        request = self.counter(claim)
        run = self.store.finalize('r-1', expected_version=run['version'], review_ids=reviews, counter_requests=[request])
        self.assertEqual(run['run_status'], 'finalized')
        self.assertTrue(run['counterevidence_performed'])
        self.assertEqual(run['accepted_claim_ids'], [])
        self.assertEqual(run['candidate_claim_ids'], ['c-1'])
        self.assertFalse(run['research']['publication_authorized'])
        self.assertEqual(final_claim_gate(claim, mode='research', review_id=reviews['c-1'], evidence_reader=self.evidence.get,
            assessment_reader=self.reviews.get, history_reader=self.store.history_reader)['status'], 'candidate')

    def test_missing_assessment_or_search_capability_cannot_finalize(self):
        run, claim, reviews = self.registered(mode='research')
        request = self.counter(claim)
        for field in ('evidence_reader', 'assessment_reader', 'search_reader'):
            with self.assertRaises(ValueError):
                self.open_store(**{field: None}).finalize('r-1', expected_version=run['version'], review_ids=reviews, counter_requests=[request])

    def test_end_to_end_c_revision_d_snapshot_run_replacement_and_export(self):
        run = self.create()
        claim = self.claim(text='All fixture reports describe a blue lamp.')
        run = self.store.append_claim('r-1', claim, expected_version=run['version'])
        old_rid = self.approve(claim)
        request = self.counter(claim, action='narrow')
        run = self.store.capture('r-1', expected_version=run['version'], review_ids={'c-1': old_rid}, counter_requests=[request])
        counter = run['counterevidence'][0]['result']
        self.assertEqual(counter['status'], 'REVISION_REQUIRED')
        proposed = counter['revision_proposal']
        run = self.store.revise_claim('r-1', 'c-1', proposed, reason=proposed['revision_reason'],
            revision_evidence_ids=proposed['revision_evidence_ids'], expected_version=run['version'])
        rid = self.approve(run['claims'][-1])
        final = self.store.finalize('r-1', expected_version=run['version'], review_ids={'c-1': old_rid, 'c-1-new': rid}, counter_requests=[request])
        trace = self.store.trace_claim('r-1', 'c-1-new')
        self.assertEqual(trace['claim']['counter_evidence_ids'], ['ev-2'])
        self.assertEqual(final['superseded_claim_ids'], ['c-1'])
        self.assertEqual(final['accepted_claim_ids'], ['c-1-new'])
        newer, _, _ = self.finalized(run_id='r-2', claim_id='c-3', supersedes_run_id='r-1', revision_reason='Later fixture findings.')
        exported = self.store.export_review('r-2', expected_version=newer['version'], review_questions=['Check the new fixture conclusion.'])
        self.assertEqual(exported['json']['snapshot']['supersedes_run_id'], 'r-1')
        self.assertEqual(exported['json']['predecessor_snapshot'], final)
        self.assertEqual(self.store.run_history('r-1')[-1], final)

    def test_export_preserves_c_observations_from_earlier_draft_versions(self):
        run, claim, reviews = self.registered()
        request = self.counter(claim)
        captured = self.store.capture('r-1', expected_version=run['version'], review_ids=reviews, counter_requests=[request])
        final = self.store.finalize('r-1', expected_version=captured['version'], review_ids=reviews)
        exported = self.store.export_review('r-1', expected_version=final['version'], review_questions=['Check prior countersearches too.'])
        versions = exported['json']['run_history']
        self.assertEqual(versions[captured['version']-1]['counterevidence'], captured['counterevidence'])
        self.assertIn('Other works/traditions unchecked.', exported['markdown'])
        self.assertFalse(exported['json']['publication_authorized'])

    def test_partial_c_scope_cannot_become_full_run_coverage(self):
        run, claim, reviews = self.registered(mode='research')
        request = self.counter(claim)
        # A separately approved C search covers only fixture, while the run
        # planned another corpus. This remains explicit partial audit data.
        self.context['source_revisions'].append({'corpus': 'other', 'repository': 'fixture/other', 'source_sha': '2'*40})
        other_scope = copy.deepcopy(self.scope)
        other_scope['corpora'].append('other')
        other_scope['source_revisions'].append(copy.deepcopy(self.context['source_revisions'][-1]))
        # Core test uses a host-derived run for this broader scope, not editing
        # a stored snapshot or letting C receipts claim the second corpus.
        from corpus_research.research_run import capture_research_run
        broader = make_research_run({**self.proposal, 'mode': 'research', 'scope': other_scope}, host_context=self.context, now=self.time)
        captured = capture_research_run(broader, run['claims'], review_ids=reviews, counter_requests=[request],
            evidence_reader=self.evidence.get, assessment_reader=self.reviews.get, search_reader=self.executions.get)
        self.assertEqual(captured['checks']['counter_scope:c-1'], 'UNVERIFIED')
        self.assertFalse(captured['counterevidence_performed'])

    def test_active_c_revision_required_cannot_finalize_as_complete(self):
        run, claim, reviews = self.registered(mode='research')
        request = self.counter(claim, action='narrow')
        with self.assertRaises(ValueError):
            self.store.finalize('r-1', expected_version=run['version'], review_ids=reviews, counter_requests=[request])
        self.assertEqual(self.store.get_run('r-1')['run_status'], 'draft')

    def test_review_decision_rechecks_evidence_against_exported_snapshot(self):
        _, claim, reviews, exported = self.package(final=True)
        self.store.import_review(self.report(exported['json']))
        self.evidence['ev-1']['evidence']['context']['after'] += ' changed'
        rid = self.approve(claim, 'new-host-review')
        self.reviews[rid]['review_report_decision'] = {'report_id': 'report-1', 'package_id': exported['json']['package_id'],
            'claim_id': 'c-1', 'disposition': 'approve', 'rationale': 'New subject review.'}
        self.assertEqual(self.store.record_review_decision('report-1', review_id=rid)['status'], 'UNVERIFIED')
        self.assertEqual(self.store.get_review('report-1')['decisions'], [])

    def test_stale_report_decision_after_run_version_change_is_blocked(self):
        run, _, reviews, exported = self.package()
        self.store.import_review(self.report(exported['json']))
        self.store.update_draft('r-1', {'question': 'changed'}, expected_version=run['version'])
        with self.assertRaises(ConflictError): self.store.record_review_decision('report-1', review_id=reviews['c-1'])

    def test_finalization_time_cannot_precede_host_creation(self):
        run, _, reviews = self.registered()
        self.time = '2026-10-10T09:00:00+07:00'
        with self.assertRaises(ValueError): self.store.finalize('r-1', expected_version=run['version'], review_ids=reviews)
        self.assertEqual(self.store.get_run('r-1')['version'], run['version'])

    def test_malformed_history_requests_cannot_select_arbitrary_history(self):
        self.registered()
        for request in ({'claim_id': ['c-1'], 'run_id': 'r-1'}, {'claim_id': 'c-1', 'run_id': None},
                        {'claim_id': 'c-1', 'run_id': 'r-1', 'history': []}):
            self.assertEqual(self.store.history_reader(request), {})

    def test_c_evidence_change_between_capture_observations_blocks_finalize(self):
        run, claim, reviews = self.registered(mode='research')
        request = self.counter(claim)
        reads = []
        def changing(eid):
            reads.append(eid)
            envelope = copy.deepcopy(self.evidence.get(eid))
            if eid == 'ev-1' and reads.count(eid) > 1:
                envelope['evidence']['context']['after'] += ' changed between observations'
            return envelope
        with self.assertRaises(ValueError):
            self.open_store(evidence_reader=changing).finalize('r-1', expected_version=run['version'], review_ids=reviews, counter_requests=[request])

    def test_host_verification_config_must_exclude_credentials(self):
        self.context['verification_config'] = {'credentials': 'must not enter the package'}
        with self.assertRaises(ValueError): self.create()

    def test_quick_finalization_cannot_omit_previously_recorded_adverse_c(self):
        run, claim, reviews = self.registered()
        request = self.counter(claim, action='narrow')
        run = self.store.capture('r-1', expected_version=run['version'], review_ids=reviews, counter_requests=[request])
        with self.assertRaises(ValueError):
            self.store.finalize('r-1', expected_version=run['version'], review_ids=reviews, counter_requests=[])
        self.assertEqual(self.store.get_run('r-1')['counter_requests'], [request])

    def test_draft_update_preserves_c_requests_and_rechecks_them(self):
        run, claim, reviews = self.registered()
        request = self.counter(claim)
        run = self.store.capture('r-1', expected_version=run['version'], review_ids=reviews, counter_requests=[request])
        run = self.store.update_draft('r-1', {'question': 'Reworded fixture question.'}, expected_version=run['version'])
        self.executions[request['plan']['search_id']]['steps'][0]['complete'] = False
        with self.assertRaises(ValueError):
            self.store.finalize('r-1', expected_version=run['version'], review_ids=reviews)
        self.assertEqual(run['counter_requests'], [request])

    def test_review_cannot_cite_registered_but_unverified_evidence_as_basis(self):
        run, _, reviews = self.registered()
        self.evidence.pop('ev-1')
        run = self.store.capture('r-1', expected_version=run['version'], review_ids=reviews)
        package = self.store.export_review('r-1', expected_version=run['version'], review_questions=['Check missing evidence.'])['json']
        self.assertEqual(package['snapshot']['checks']['evidence:ev-1'], 'UNVERIFIED')
        with self.assertRaises(ValueError): self.store.import_review(self.report(package))


if __name__ == '__main__':
    unittest.main()
