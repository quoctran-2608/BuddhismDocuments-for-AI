"""Small host-owned, persistent Phase D adapter, separate from corpus SQLite.

Path, readers and clock are wired by the host outside proposal/import JSON.
BEGIN IMMEDIATE serializes writers across processes; expected_version is a CAS
precondition. Snapshot rows are append-only, including draft revisions. DB
ownership/permissions remain the host's responsibility: this is not protection
against a privileged actor replacing the file or configuring fake capabilities.
No user authentication service or corpus/Connector adapter is implemented.
check_publication rechecks B under the store lock, but NEVER authorizes an
external side effect: E must coordinate that effect and all external providers.
"""
from __future__ import annotations

import copy
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import uuid

from .claims import (_json, _same, _strings, _text, append_claim, assess_claim,
                     revise_claim, verify_synthesis)
from .research_run import (HOST_FIELDS, PROPOSAL_FIELDS, capture_research_run,
    make_research_run, review_markdown, safe_json, snapshot_hash, timestamp, trace_claim)
from .verification import _read_capability

APPLICATION_ID = 0x42435244


class ConflictError(ValueError):
    """Stale version, reused ID or conflicting successor; caller must read anew."""


class ResearchStore:
    def __init__(self, path, *, context_reader=None, evidence_reader=None,
                 assessment_reader=None, search_reader=None, dependency_reader=None, clock=None):
        if str(path) == ':memory:':
            raise ValueError('use a dedicated persistent research store file')
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.context_reader = context_reader
        self.readers = dict(evidence_reader=evidence_reader, assessment_reader=assessment_reader,
                            search_reader=search_reader, dependency_reader=dependency_reader)
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat())
        with self._transaction() as con:
            tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            marker = con.execute('PRAGMA application_id').fetchone()[0]
            if tables and marker != APPLICATION_ID or marker not in (0, APPLICATION_ID):
                raise ValueError('not a dedicated BCR research store; corpus index is forbidden')
            con.execute(f'PRAGMA application_id={APPLICATION_ID}')
            for statement in (
                'CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY, current_version INTEGER NOT NULL)',
                'CREATE TABLE IF NOT EXISTS snapshots(run_id TEXT NOT NULL, version INTEGER NOT NULL, body TEXT NOT NULL, digest TEXT NOT NULL, PRIMARY KEY(run_id,version))',
                'CREATE TABLE IF NOT EXISTS claim_ids(claim_id TEXT PRIMARY KEY, run_id TEXT NOT NULL)',
                'CREATE TABLE IF NOT EXISTS successions(old_id TEXT PRIMARY KEY, new_id TEXT UNIQUE NOT NULL)',
                'CREATE TABLE IF NOT EXISTS packages(package_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, version INTEGER NOT NULL, body TEXT NOT NULL)',
                'CREATE TABLE IF NOT EXISTS reports(report_id TEXT PRIMARY KEY, package_id TEXT NOT NULL, body TEXT NOT NULL, imported_at TEXT NOT NULL)',
                'CREATE TABLE IF NOT EXISTS decisions(review_id TEXT PRIMARY KEY, report_id TEXT NOT NULL, body TEXT NOT NULL)',
            ):
                con.execute(statement)
            for table in ('snapshots', 'claim_ids', 'successions', 'packages', 'reports', 'decisions'):
                for operation in ('UPDATE', 'DELETE'):
                    con.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_{operation.lower()} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT,'immutable research record'); END")

    @contextmanager
    def _transaction(self):
        con = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        try:
            con.execute('BEGIN IMMEDIATE')
            yield con
            con.commit()
        except BaseException:
            con.rollback()
            raise
        finally:
            con.close()

    def _now(self):
        value = self.clock()
        timestamp(value)
        return value

    def _get(self, con, run_id, version=None):
        if not _text(run_id) or version is not None and (type(version) is not int or version < 1):
            raise ValueError('valid run ID and version required')
        row = con.execute('SELECT current_version FROM runs WHERE run_id=?', (run_id,)).fetchone()
        if row is None:
            raise ValueError('unknown run')
        selected = row[0] if version is None else version
        snapshot = con.execute('SELECT body,digest FROM snapshots WHERE run_id=? AND version=?', (run_id, selected)).fetchone()
        if snapshot is None:
            raise ValueError('unknown run version')
        run = json.loads(snapshot[0])
        if snapshot_hash(run) != snapshot[1] or run['run_id'] != run_id or run['version'] != selected:
            raise ValueError('corrupt research snapshot')
        return run

    def _active(self, con, run):
        if con.execute('SELECT 1 FROM successions WHERE old_id=?', (run['run_id'],)).fetchone():
            raise ConflictError('run has been superseded')

    def _draft(self, con, run_id, expected_version):
        run = self._get(con, run_id)
        self._expected(run, expected_version)
        self._active(con, run)
        if run['run_status'] != 'draft':
            raise ConflictError('finalized snapshots cannot be edited')
        return run

    @staticmethod
    def _expected(run, expected_version):
        if type(expected_version) is not int or run['version'] != expected_version:
            raise ConflictError('stale snapshot version')

    def _save(self, con, run, *, new=False):
        safe_json(run)
        previous = run['version']
        if new:
            con.execute('INSERT INTO runs VALUES(?,?)', (run['run_id'], previous))
        else:
            run['version'] += 1
            cursor = con.execute('UPDATE runs SET current_version=? WHERE run_id=? AND current_version=?',
                (run['version'], run['run_id'], previous))
            if cursor.rowcount != 1:
                raise ConflictError('concurrent snapshot update')
        con.execute('INSERT INTO snapshots VALUES(?,?,?,?)',
            (run['run_id'], run['version'], _json(run), snapshot_hash(run)))
        return copy.deepcopy(run)

    def create_run(self, proposal):
        run_id = proposal.get('run_id') if isinstance(proposal, dict) else None
        if not _text(run_id):
            raise ValueError('run ID required before consulting host context')
        context = _read_capability(self.context_reader, run_id)
        run = make_research_run(proposal, host_context=context, now=self._now())
        try:
            with self._transaction() as con:
                if run['supersedes_run_id'] is not None:
                    old = self._get(con, run['supersedes_run_id'])
                    self._active(con, old)
                    if old['run_status'] != 'finalized':
                        raise ConflictError('replace a finalized active run, not a draft')
                return self._save(con, run, new=True)
        except sqlite3.IntegrityError as exc:
            raise ConflictError('run ID already exists') from exc

    def get_run(self, run_id, *, version=None):
        with self._transaction() as con:
            run = self._get(con, run_id, version)
            successor = con.execute('SELECT new_id FROM successions WHERE old_id=?', (run_id,)).fetchone()
            if successor:
                run['run_status'] = 'superseded'  # projection only, never rewrite old bytes
            run['superseded_by_run_id'] = successor[0] if successor else None
            return run

    def run_history(self, run_id):
        with self._transaction() as con:
            self._get(con, run_id)
            return [self._get(con, run_id, row[0]) for row in con.execute(
                'SELECT version FROM snapshots WHERE run_id=? ORDER BY version', (run_id,)).fetchall()]

    def update_draft(self, run_id, changes, *, expected_version):
        safe_json(changes)
        allowed = {'question', 'search_hypotheses', 'queries', 'limitations', 'answer_artifact'}
        if not isinstance(changes, dict) or not changes or set(changes) - allowed:
            raise ValueError('only draft descriptive fields can be updated')
        with self._transaction() as con:
            old = self._draft(con, run_id, expected_version)
            proposal = {key: old[key] for key in PROPOSAL_FIELDS}
            proposal.update(changes)
            context = {key: old[key] for key in HOST_FIELDS}
            run = make_research_run(proposal, host_context=context, now=old['created_at'])
            run.update(version=old['version'], claims=old['claims'], counter_requests=old['counter_requests'])
            return self._save(con, run)

    def append_claim(self, run_id, claim, *, expected_version):
        with self._transaction() as con:
            run = self._draft(con, run_id, expected_version)
            history = append_claim(run['claims'], claim)
            return self._claim_update(con, run, history)

    def revise_claim(self, run_id, old_claim_id, proposal, *, reason, revision_evidence_ids, expected_version):
        with self._transaction() as con:
            run = self._draft(con, run_id, expected_version)
            history = revise_claim(run['claims'], old_claim_id, proposal,
                reason=reason, revision_evidence_ids=revision_evidence_ids)
            return self._claim_update(con, run, history)

    def _claim_update(self, con, run, history):
        claim = history[-1]
        if claim['run_id'] != run['run_id']:
            raise ValueError('B claim revision remains within its original run')
        try:
            con.execute('INSERT INTO claim_ids VALUES(?,?)', (claim['claim_id'], run['run_id']))
        except sqlite3.IntegrityError as exc:
            raise ConflictError('claim ID cannot be reused across runs') from exc
        # Invalidate derived observations; complete append-only history survives.
        proposal = {key: run[key] for key in PROPOSAL_FIELDS}
        context = {key: run[key] for key in HOST_FIELDS}
        updated = make_research_run(proposal, host_context=context, now=run['created_at'])
        updated.update(version=run['version'], claims=history, counter_requests=run['counter_requests'])
        return self._save(con, updated)

    def _capture(self, run, review_ids, counter_requests):
        # Pin information is re-observed through the configured host, not JSON.
        context = _read_capability(self.context_reader, run['run_id'])
        proposal = {key: run[key] for key in PROPOSAL_FIELDS}
        current = make_research_run(proposal, host_context=context, now=run['created_at'])
        if not _same({key: current[key] for key in HOST_FIELDS}, {key: run[key] for key in HOST_FIELDS}):
            raise ConflictError('host provenance/config changed; start a new run')
        safe_json(counter_requests)
        if not isinstance(counter_requests, list):
            raise ValueError('counter requests must be a list')
        retained = {item['claim_id']: copy.deepcopy(item) for item in run['counter_requests']}
        seen = set()
        for request in counter_requests:
            if not isinstance(request, dict) or not _text(request.get('claim_id')) or request['claim_id'] in seen:
                raise ValueError('invalid/duplicate counter request')
            seen.add(request['claim_id'])
            retained[request['claim_id']] = copy.deepcopy(request)
        observed_run = {**run, 'counter_requests': list(retained.values())}
        captured = capture_research_run(observed_run, run['claims'], review_ids=review_ids,
            counter_requests=observed_run['counter_requests'], **self.readers)
        captured['captured_at'] = self._now()
        return captured

    def capture(self, run_id, *, expected_version, review_ids, counter_requests=None):
        with self._transaction() as con:
            run = self._draft(con, run_id, expected_version)
            return self._save(con, self._capture(run, review_ids, [] if counter_requests is None else counter_requests))

    def finalize(self, run_id, *, expected_version, review_ids, counter_requests=None):
        with self._transaction() as con:
            run = self._draft(con, run_id, expected_version)
            run = self._capture(run, review_ids, [] if counter_requests is None else counter_requests)
            if any(value != 'PASS' for value in run['checks'].values()):
                raise ValueError('incomplete/conflicting research record cannot be finalized')
            now = self._now()
            if timestamp(now) < timestamp(run['created_at']):
                raise ValueError('finalization precedes creation')
            if run['supersedes_run_id'] is not None:
                old = self._get(con, run['supersedes_run_id'])
                self._active(con, old)
                if old['run_status'] != 'finalized':
                    raise ConflictError('predecessor is not finalized')
                con.execute('INSERT INTO successions VALUES(?,?)', (old['run_id'], run_id))
            run.update(run_status='finalized', finalized_at=now)
            return self._save(con, run)

    def _history_response(self, con, request):
        if (not isinstance(request, dict) or set(request) != {'claim_id', 'run_id'}
                or not all(_text(request[key]) for key in ('claim_id', 'run_id'))):
            return {}
        row = con.execute('SELECT run_id FROM claim_ids WHERE claim_id=?', (request['claim_id'],)).fetchone()
        if row is None or row[0] != request['run_id']:
            return {}
        run = self._get(con, row[0])
        retired = con.execute('SELECT 1 FROM successions WHERE old_id=?', (row[0],)).fetchone()
        return {**request, 'complete': not bool(retired), 'history': copy.deepcopy(run['claims'])}

    def history_reader(self, request):
        with self._transaction() as con:
            return self._history_response(con, request)

    def trace_claim(self, run_id, claim_id):
        return trace_claim(self.get_run(run_id), claim_id)

    def check_publication(self, run_id, *, expected_version, items, review_ids):
        """Fresh B check with a version guard. External publication stays closed."""
        with self._transaction() as con:
            run = self._get(con, run_id)
            self._expected(run, expected_version)
            self._active(con, run)
            verified = verify_synthesis(items, run['claims'], review_ids, mode=run['mode'],
                evidence_reader=self.readers['evidence_reader'], assessment_reader=self.readers['assessment_reader'],
                history_reader=lambda request: self._history_response(con, request))
            return {'status': 'UNVERIFIED', 'publication_authorized': False, 'run_id': run_id,
                    'snapshot_version': run['version'], 'gate_result': verified,
                    'reason': 'E must coordinate external publication and provider freshness; a saved check is not a publication permit'}

    def export_review(self, run_id, *, expected_version, review_questions):
        if not _strings(review_questions) or not review_questions:
            raise ValueError('explicit review questions required')
        with self._transaction() as con:
            run = self._get(con, run_id)
            self._expected(run, expected_version)
            self._active(con, run)
            if run['captured_at'] is None:
                raise ValueError('capture A/B/C observations before exporting')
            package = {'package_id': str(uuid.uuid4()), 'run_id': run_id,
                'snapshot_version': run['version'], 'snapshot_sha256': snapshot_hash(run),
                'snapshot': run, 'review_questions': copy.deepcopy(review_questions),
                'exported_at': self._now(), 'publication_authorized': False}
            package['run_history'] = [self._get(con, run_id, row[0]) for row in con.execute(
                'SELECT version FROM snapshots WHERE run_id=? ORDER BY version', (run_id,)).fetchall()]
            package['predecessor_snapshot'] = self._get(con, run['supersedes_run_id']) if run['supersedes_run_id'] else None
            safe_json(package)
            con.execute('INSERT INTO packages VALUES(?,?,?,?)',
                (package['package_id'], run_id, run['version'], _json(package)))
            return {'json': copy.deepcopy(package), 'markdown': review_markdown(package)}

    def _package(self, con, package_id):
        row = con.execute('SELECT body FROM packages WHERE package_id=?', (package_id,)).fetchone()
        if row is None:
            raise ValueError('unknown package')
        package = json.loads(row[0])
        run = self._get(con, package['run_id'])
        self._expected(run, package['snapshot_version'])
        self._active(con, run)
        if not _same(run, package['snapshot']) or snapshot_hash(run) != package['snapshot_sha256']:
            raise ConflictError('package does not match authoritative snapshot')
        return package

    def verify_review_package(self, package):
        safe_json(package)
        with self._transaction() as con:
            actual = self._package(con, package.get('package_id'))
            if not _same(actual, package):
                raise ValueError('exported package was altered')
            return {'status': 'MATCHED', 'publication_authorized': False}

    def import_review(self, report):
        safe_json(report)
        required = {'report_id', 'package_id', 'snapshot_sha256', 'reviewer', 'reviewer_role',
                    'reviewed_at', 'session', 'relationship_to_proposer', 'comments', 'unverified'}
        if not isinstance(report, dict) or set(report) - required - {'approved', 'trusted', 'status'} or not required.issubset(report):
            raise ValueError('invalid review report structure')
        if not all(_text(report[key]) for key in ('report_id', 'package_id', 'snapshot_sha256', 'reviewer', 'reviewer_role', 'relationship_to_proposer')):
            raise ValueError('review report identity required')
        timestamp(report['reviewed_at'])
        if report['session'] is not None and not _text(report['session']) or not _strings(report['unverified']):
            raise ValueError('invalid review session/limits')
        if not isinstance(report['comments'], list) or not report['comments']:
            raise ValueError('claim-specific comments required')
        with self._transaction() as con:
            package = self._package(con, report['package_id'])
            if report['snapshot_sha256'] != package['snapshot_sha256']:
                raise ValueError('review is for a different snapshot')
            index = {claim['claim_id']: claim for claim in package['snapshot']['claims']}
            seen = set()
            for comment in report['comments']:
                if (not isinstance(comment, dict) or set(comment) != {'claim_id', 'comment', 'evidence_ids', 'limitations', 'recommendation'}
                        or not _text(comment['claim_id']) or comment['claim_id'] not in index or comment['claim_id'] in seen
                        or not _text(comment['comment']) or not _strings(comment['evidence_ids'])
                        or not _strings(comment['limitations']) or comment['recommendation'] not in ('keep', 'rewrite', 'narrow', 'reject')):
                    raise ValueError('invalid review comment')
                seen.add(comment['claim_id'])
                claim = index[comment['claim_id']]
                if (not set(comment['evidence_ids']).issubset(claim['supporting_evidence_ids'] + claim['counter_evidence_ids'])
                        or not set(comment['evidence_ids']).issubset(package['snapshot']['evidence_ids'])):
                    raise ValueError('unverified/orphan citations cannot become evidence')
            try:
                con.execute('INSERT INTO reports VALUES(?,?,?,?)',
                    (report['report_id'], report['package_id'], _json(report), self._now()))
            except sqlite3.IntegrityError as exc:
                raise ConflictError('report ID already exists') from exc
            return {'report_id': report['report_id'], 'status': 'PROPOSED', 'approved': False}

    def get_review(self, report_id):
        with self._transaction() as con:
            row = con.execute('SELECT body,imported_at FROM reports WHERE report_id=?', (report_id,)).fetchone()
            if row is None:
                raise ValueError('unknown report')
            decisions = [json.loads(item[0]) for item in con.execute('SELECT body FROM decisions WHERE report_id=?', (report_id,))]
            return {'original_report': json.loads(row[0]), 'imported_at': row[1], 'status': 'PROPOSED', 'decisions': decisions}

    def record_review_decision(self, report_id, *, review_id):
        """Persist a host decision via the SAME B channel; report flags grant nothing."""
        with self._transaction() as con:
            row = con.execute('SELECT body FROM reports WHERE report_id=?', (report_id,)).fetchone()
            if row is None:
                raise ValueError('unknown report')
            report = json.loads(row[0])
            package = self._package(con, report['package_id'])
            approved = _read_capability(self.readers['assessment_reader'], review_id)
            safe_json(approved)
            decision = approved.get('review_report_decision')
            if not isinstance(decision, dict) or set(decision) != {'report_id', 'package_id', 'claim_id', 'disposition', 'rationale'}:
                return {'status': 'UNVERIFIED', 'decision': None}
            if (decision['report_id'] != report_id or decision['package_id'] != package['package_id']
                    or decision['claim_id'] not in [item['claim_id'] for item in report['comments']]
                    or decision['disposition'] not in ('approve', 'reject') or not _text(decision['rationale'])):
                return {'status': 'UNVERIFIED', 'decision': None}
            claim = next(item for item in package['snapshot']['claims'] if item['claim_id'] == decision['claim_id'])
            assessment = assess_claim(claim, review_id=review_id, evidence_reader=self.readers['evidence_reader'],
                assessment_reader=lambda key: approved if key == review_id else {})
            if assessment['status'] != 'ASSESSED':
                return {'status': 'UNVERIFIED', 'decision': None}
            captured = package['snapshot']['assessments'].get(claim['claim_id'])
            if captured is None or not _same(captured['evidence'], assessment['evidence']):
                return {'status': 'UNVERIFIED', 'decision': None}
            record = {'review_id': review_id, 'report_id': report_id, 'decision': decision,
                      'assessment': assessment, 'recorded_at': self._now()}
            try:
                con.execute('INSERT INTO decisions VALUES(?,?,?)', (review_id, report_id, _json(record)))
            except sqlite3.IntegrityError as exc:
                raise ConflictError('review decision ID already recorded') from exc
            return {'status': 'RECORDED', 'decision': copy.deepcopy(record), 'publication_authorized': False}
