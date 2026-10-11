"""Phase D JSON core. Reports/snapshots are audit data, never capabilities.

The host supplies context (pinned versions) and time outside proposal JSON.
ResearchStore supplies current complete history in a transaction. A/B/C readers
retain their existing trust contracts; stored observations are historical and
must not be wired back as fresh evidence/approval. No publication is granted
by this module, finalized status, hashes, an imported report or model agreement.
No chain-of-thought field is accepted. Host data must exclude secrets; bounded
schemas/key checks are not a general content redaction service.
"""
from __future__ import annotations

import copy
from datetime import datetime
import hashlib

from .claims import (_evidence_record, _history_index, _json, _same, _strings, _text,
                     assess_claim, claim_subject, final_claim_gate, history_claim)
from .counterevidence import _record, _scope, assess_counterevidence
from .verification import _path, _read_capability, _sha

RUN_FIELDS = (
    'run_id', 'run_status', 'question', 'created_at', 'finalized_at', 'mode', 'scope',
    'main_repository', 'main_repository_commit', 'remote_repository',
    'remote_repository_commit', 'remote_root', 'source_revisions', 'search_hypotheses',
    'queries', 'evidence_ids', 'candidate_claim_ids', 'accepted_claim_ids',
    'rejected_claim_ids', 'superseded_claim_ids', 'counterevidence_performed',
    'counterevidence_summary', 'limitations', 'answer_artifact', 'model_identifier',
    'verification_config', 'supersedes_run_id', 'revision_reason',
)
PROPOSAL_FIELDS = {'run_id', 'question', 'mode', 'scope', 'search_hypotheses', 'queries',
                   'limitations', 'answer_artifact', 'supersedes_run_id', 'revision_reason'}
HOST_FIELDS = ('main_repository', 'main_repository_commit', 'remote_repository',
               'remote_repository_commit', 'remote_root', 'source_revisions',
               'model_identifier', 'verification_config', 'environment')
FORBIDDEN_KEYS = {'chain_of_thought', 'internal_reasoning', 'reasoning_trace',
                  'api_key', 'password', 'access_token', 'secret', 'credentials'}


def safe_json(value):
    _json(value)
    def visit(item):
        if isinstance(item, dict):
            if any(key.lower() in FORBIDDEN_KEYS for key in item):
                raise ValueError('private reasoning/credentials must not enter a research record')
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
    visit(value)


def timestamp(value):
    if not _text(value):
        raise ValueError('host timestamp required')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('timestamp must include timezone')
    return parsed


def snapshot_hash(value):
    return hashlib.sha256(_json(value).encode('utf-8')).hexdigest()


def make_research_run(proposal, *, host_context, now):
    """Normalize a draft; host context is configuration, not uploaded authority."""
    safe_json(proposal)
    safe_json(host_context)
    if not isinstance(proposal, dict) or set(proposal) - set(RUN_FIELDS) - {'environment', 'approved', 'verified', 'version'}:
        raise ValueError('unknown run proposal fields')
    if not all(_text(proposal.get(key)) for key in ('run_id', 'question')) or proposal.get('mode') not in ('quick', 'research'):
        raise ValueError('run_id, question and quick/research mode required')
    timestamp(now)
    if not isinstance(host_context, dict) or set(host_context) - set(HOST_FIELDS):
        raise ValueError('invalid host context')
    context = {key: copy.deepcopy(host_context.get(key)) for key in HOST_FIELDS}
    if not _text(context['main_repository']) or not _sha(context['main_repository_commit']):
        raise ValueError('host must establish main repository and commit')
    if context['environment'] not in ('local', 'connector'):
        raise ValueError('host must establish execution environment')
    remote = [context[key] for key in ('remote_repository', 'remote_repository_commit', 'remote_root')]
    if context['environment'] == 'connector':
        if not _text(remote[0]) or not _sha(remote[1]) or not _path(remote[2]):
            raise ValueError('connector requires pinned locator repository/commit/root')
    elif any(value is not None for value in remote):
        raise ValueError('local locator fields must be null')
    if context['model_identifier'] is not None and not _text(context['model_identifier']):
        raise ValueError('invalid model identifier')
    if context['verification_config'] is not None and not isinstance(context['verification_config'], dict):
        raise ValueError('verification_config must be an object or null')
    scope = copy.deepcopy(proposal.get('scope'))
    _scope(scope)
    revisions = context['source_revisions']
    if not isinstance(revisions, list):
        raise ValueError('host must establish pinned source revisions')
    _scope({'corpora': [item.get('corpus') for item in revisions if isinstance(item, dict)],
            'source_revisions': revisions, 'constraints': []})
    if any(item not in revisions for item in scope['source_revisions']):
        raise ValueError('proposed scope differs from host source pins')
    predecessor, reason = proposal.get('supersedes_run_id'), proposal.get('revision_reason')
    if predecessor is not None:
        if not _text(predecessor) or predecessor == proposal['run_id'] or not _text(reason):
            raise ValueError('run revision needs a distinct predecessor and reason')
    elif reason is not None:
        raise ValueError('revision reason requires a predecessor')
    result = {key: None for key in RUN_FIELDS}
    result.update(context)
    for key in PROPOSAL_FIELDS:
        if key in proposal:
            result[key] = copy.deepcopy(proposal[key])
    for key in ('search_hypotheses', 'queries', 'limitations'):
        result[key] = copy.deepcopy(proposal.get(key, []))
        if not _strings(result[key]):
            raise ValueError('hypotheses, planned queries and limitations must be string lists')
    if result['answer_artifact'] is not None and not _text(result['answer_artifact']):
        raise ValueError('answer_artifact is a reference, not an unverified answer body')
    result.update(run_status='draft', created_at=now, finalized_at=None,
                  source_revisions=copy.deepcopy(scope['source_revisions']), version=1,
                  evidence_ids=[], candidate_claim_ids=[], accepted_claim_ids=[],
                  rejected_claim_ids=[], superseded_claim_ids=[], counterevidence_performed=False,
                  counterevidence_summary=[], claims=[], evidence=[], assessments={},
                  counterevidence=[], checks={}, retrieval={}, research={}, captured_at=None)
    result['counter_requests'] = []
    return result


def capture_research_run(run, history, *, review_ids, counter_requests,
                         evidence_reader=None, assessment_reader=None, search_reader=None,
                         dependency_reader=None):
    """Observe A/B/C with host-held history. Never persist or authorize publication."""
    safe_json(review_ids)
    safe_json(counter_requests)
    if not isinstance(review_ids, dict) or not all(_text(k) and _text(v) for k, v in review_ids.items()):
        raise ValueError('review IDs must be a claim-to-review mapping')
    if not isinstance(counter_requests, list):
        raise ValueError('counter requests must be a list')
    index, replaced = _history_index(history)
    if any(claim['run_id'] != run['run_id'] for claim in index.values()) or set(review_ids) - set(index):
        raise ValueError('claim/approval references cross run scope')
    result = copy.deepcopy(run)
    checks = {'history': 'PASS', 'claims': 'PASS' if index else 'UNVERIFIED'}
    ids = list(dict.fromkeys(eid for claim in index.values() for eid in
        claim['supporting_evidence_ids'] + claim['counter_evidence_ids']))
    records, envelopes = {}, {}
    for eid in ids:
        envelope = _read_capability(evidence_reader, eid)
        try:
            record = _evidence_record(envelope, eid)
        except (ValueError, TypeError, RecursionError):
            record = None
        checks['evidence:'+eid] = 'PASS' if record else 'UNVERIFIED'
        if record:
            identity = {key: record[key] for key in ('corpus', 'repository', 'source_sha')}
            if identity not in run['source_revisions'] or record['run_id'] not in (None, run['run_id']):
                checks['evidence:'+eid] = 'FAIL'
            else:
                records[eid], envelopes[eid] = record, envelope
    # Only cache fresh observations within this capture. Later calls read again.
    def current_evidence(eid):
        return envelopes.get(eid, {})
    assessments, gates = {}, {}
    history_reader = lambda request: {**request, 'complete': True, 'history': copy.deepcopy(history)}
    for cid, claim in index.items():
        reviewed = _read_capability(assessment_reader, review_ids.get(cid))
        reader = lambda key, review=reviewed, rid=review_ids.get(cid): review if key == rid else {}
        assessment = assess_claim(claim, review_id=review_ids.get(cid), evidence_reader=current_evidence,
                                  assessment_reader=reader)
        assessments[cid] = assessment
        # B assessment validity is separate from its support/publication verdict.
        # Valid UNSUPPORTED/CONTRADICTED assessments still belong in the audit.
        checks['assessment:'+cid] = ('PASS' if assessment['status'] == 'ASSESSED' else
                                    'FAIL' if assessment['status'] == 'REJECTED' else 'UNVERIFIED')
        gates[cid] = final_claim_gate(claim, mode=run['mode'], review_id=review_ids.get(cid),
            evidence_reader=current_evidence, assessment_reader=reader, history_reader=history_reader)
    counters, seen = [], set()
    for request in counter_requests:
        if (not isinstance(request, dict) or set(request) != {'claim_id', 'plan', 'review_id'}
                or not _text(request['claim_id']) or request['claim_id'] not in index
                or request['claim_id'] in seen or request['review_id'] is not None and not _text(request['review_id'])):
            raise ValueError('counter request must reference one registered claim in this run')
        cid = request['claim_id']
        seen.add(cid)
        counter = assess_counterevidence(index[cid], request['plan'], review_id=request['review_id'],
            evidence_reader=evidence_reader, assessment_reader=assessment_reader,
            search_reader=search_reader, dependency_reader=dependency_reader)
        counters.append({'claim_id': cid, 'result': counter})
        search = counter['search']
        checks['counter_scope:'+cid] = 'PASS' if search['plan'] and _same(search['plan']['scope'], run['scope']) else 'UNVERIFIED'
        # A requested revision cannot remain the active final conclusion.
        valid = counter['status'] == 'ASSESSED' or (cid in replaced and counter['status'] == 'REVISION_REQUIRED')
        valid = valid or (counter['status'] == 'REJECTED' and counter['decision'] is not None
                         and counter['decision']['action'] == 'reject' and 'FAIL' not in counter['checks'].values())
        checks['counter:'+cid] = 'PASS' if valid else 'UNVERIFIED'
        observations = search['verified_evidence'] + (counter['independence']['evidence'] if counter['independence'] else [])
        for record in observations:
            eid = record['evidence_id']
            if eid not in records:
                # Found evidence may not yet be linked to an immutable B claim.
                fresh = _record(eid, evidence_reader)
                identity = {key: record[key] for key in ('corpus', 'repository', 'source_sha')}
                if fresh and _same(fresh, record) and identity in run['source_revisions'] and record['run_id'] in (None, run['run_id']):
                    records[eid] = record
                else:
                    checks['counter_snapshot:'+eid] = 'UNVERIFIED'
            elif not _same(records[eid], record):
                checks['counter_snapshot:'+eid] = 'FAIL'
    active = set(index) - replaced
    complete = bool(active) and all(cid in seen and checks.get('counter:'+cid) == 'PASS'
        and checks.get('counter_scope:'+cid) == 'PASS' for cid in active)
    checks['research_counterevidence'] = 'PASS' if run['mode'] == 'quick' or complete else 'UNVERIFIED'
    result.update(claims=copy.deepcopy(history), evidence=list(records.values()), assessments=assessments,
        counterevidence=counters, checks=checks, evidence_ids=list(records),
        candidate_claim_ids=[cid for cid, gate in gates.items() if gate['status'] == 'candidate'],
        accepted_claim_ids=[cid for cid, gate in gates.items() if gate['status'] == 'accepted'],
        rejected_claim_ids=[cid for cid, gate in gates.items() if gate['status'] == 'rejected'],
        superseded_claim_ids=sorted(replaced), counterevidence_performed=complete,
        counterevidence_summary=[{'claim_id': item['claim_id'], 'search': item['result']['search']['status'],
            'summary': item['result']['search']['summary'], 'decision': item['result']['decision']} for item in counters])
    limits = list(run['limitations'])
    for claim in index.values():
        limits.extend(claim['limitations'])
    for item in counters:
        plan = item['result']['search']['plan']
        if plan:
            limits.extend(plan['unchecked_scope'])
        for attempt in item['result']['search']['attempts']:
            limits.extend(attempt['limitations'])
    result['limitations'] = list(dict.fromkeys(limits))
    result['retrieval'] = {'planned_queries': copy.deepcopy(run['queries']), 'scope': copy.deepcopy(run['scope']),
        'source_revisions': copy.deepcopy(run['source_revisions']), 'main_repository_commit': run['main_repository_commit'],
        'locator': {key: run[key] for key in ('remote_repository', 'remote_repository_commit', 'remote_root')},
        'actual_countersearches': [item['result']['search'] for item in counters]}
    result['research'] = {'evidence': copy.deepcopy(result['evidence']), 'claims': copy.deepcopy(history),
        'assessments': copy.deepcopy(assessments), 'gates': gates, 'counterevidence': copy.deepcopy(counters),
        'exact_answer_reproduction': False, 'publication_authorized': False}
    safe_json(result)
    return result


def trace_claim(run, claim_id):
    claim = history_claim(run['claims'], claim_id)
    evidence = {record['evidence_id']: record for record in run['evidence']}
    ids = claim['supporting_evidence_ids'] + claim['counter_evidence_ids']
    return copy.deepcopy({'run_id': run['run_id'], 'version': run['version'], 'claim': claim,
        'evidence': [evidence[eid] for eid in dict.fromkeys(ids) if eid in evidence],
        'missing_evidence_ids': [eid for eid in dict.fromkeys(ids) if eid not in evidence],
        'assessment': run['assessments'].get(claim_id),
        'successors': [item['claim_id'] for item in run['claims'] if item['supersedes_claim_id'] == claim_id],
        'counterevidence': [item for item in run['counterevidence'] if item['claim_id'] == claim_id],
        'historical_observation_only': True})


def review_markdown(package):
    run = package['snapshot']
    lines = ['# Hồ sơ thẩm định', '', f"Package: {package['package_id']}",
             f"Run: {run['run_id']} — snapshot {package['snapshot_version']}",
             f"SHA-256 snapshot: {package['snapshot_sha256']}", '', run['question'], '',
             'Hồ sơ này không cấp quyền công bố hoặc phê duyệt.', '', '## Luận điểm', '']
    for claim in run['claims']:
        lines.extend([f"### {claim['claim_id']} ({claim['claim_type']})", '', claim['text'], '',
            'Hỗ trợ: '+', '.join(claim['supporting_evidence_ids']),
            'Phản chứng: '+', '.join(claim['counter_evidence_ids']), ''])
    lines.extend(['## Câu hỏi thẩm định', '', *['- '+question for question in package['review_questions']], '',
                  '## Snapshot đầy đủ: nguồn, ngữ cảnh, phạm vi và các phép kiểm', '',
                  '```json', _json({'snapshot': run, 'run_history': package['run_history'],
                                   'predecessor_snapshot': package['predecessor_snapshot']}), '```', ''])
    return '\n'.join(lines)
