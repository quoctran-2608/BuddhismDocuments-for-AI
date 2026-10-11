"""Phase C: scoped search receipts, source dependence and reviewed impacts.

Pure JSON core, with no retrieval engine, DB, shell or publication authority.
The host wires all readers outside proposal JSON/model-generated code:
* evidence_reader(id): genuine current Phase A gate results, as in Phase B.
* dependency_reader({'evidence_ids': [left, right]}): approved provenance or
  source-dependence analysis, bound to both full current evidence snapshots.
  Returns evidence, relationship, derived_evidence_id (otherwise null), basis,
  reviewer, rationale. Repository names, wording and reviewer-model identity
  are not grounds for independence. A callable or JSON labels prove nothing.
* search_reader(search_id): host-approved plan and actual execution receipts.
  Returns search_id, plan (without status), reviewer, rationale, steps. Each
  receipt has step_id, status (executed/failed/not_run), complete (bool),
  checked_scope (or null), candidates [{candidate_id, evidence_id, pointer}],
  limitations. It must invoke existing retrieval/source tools or read genuine
  receipts for the exact pinned scope; never echo proposed completion flags.
  Complete means that bounded operation finished without truncation/missing
  data, not that every possible counterargument was searched. Host policy
  approves appropriate directions and records important unchecked scope.
* assessment_reader(review_id): existing B approval channel. Its ordinary B
  assessment binds the claim enriched with found evidence IDs as *potential*
  counters. Optional counterevidence_review additionally binds exact search
  and independence results, findings (evidence_id/effect/rationale), action,
  rationale, prior_review_id (required for lowering, otherwise null), and
  revision (null or {claim_id, text}). This is an approved
  semantic judgment, not a second approval channel. Findings distinguish
  supports/irrelevant/limits/contradicts; opened text alone cannot decide.

Search results never certify semantic counterevidence or global absence. C
never grants accepted or persists revisions: pass its candidate revision to
revise_claim, persist via the host, obtain new B approval and re-run B gates
with history_reader. Research remains blocked pending D/E. Host adapters,
authenticated stores, freshness and coordination are integration obligations;
no real corpus research or independent reviewer service is built here.
"""

from __future__ import annotations

import copy
from itertools import combinations

from .claims import (
    _evidence_record, _json, _same, _strings, _text, assess_claim,
    claim_subject, make_claim,
)
from .verification import _read_capability, _sha


INDEPENDENCE_STATES = frozenset({
    'independent', 'partially_dependent', 'same_source_family', 'derived_from', 'uncertain',
})
SEARCH_DIRECTIONS = frozenset({
    'exception', 'other_witness', 'variant', 'parallel_mismatch',
    'peer_conflict', 'source_dependency', 'scope_limit',
})
OPERATIONS = frozenset({'search', 'context', 'evidence', 'parallels', 'variants', 'resolve', 'work'})
PLAN_FIELDS = ('search_id', 'claim', 'scope', 'steps', 'unchecked_scope')
ACTIONS = frozenset({'keep', 'lower_support', 'narrow', 'rewrite', 'unsupported', 'contradicted', 'reject'})


def _status(checks, success='ASSESSED'):
    if 'FAIL' in checks.values():
        return 'REJECTED'
    return 'UNVERIFIED' if 'UNVERIFIED' in checks.values() else success


def _record(evidence_id, reader):
    try:
        return _evidence_record(_read_capability(reader, evidence_id), evidence_id)
    except (ValueError, TypeError, RecursionError):
        return None


def source_independence(evidence_ids, *, evidence_reader=None, dependency_reader=None):
    """Conservative pair relations; unknown pairs never contribute a count."""
    if not _strings(evidence_ids) or not evidence_ids:
        raise ValueError('nonempty evidence IDs required')
    ids = list(dict.fromkeys(evidence_ids))
    records = {key: _record(key, evidence_reader) for key in ids}
    checks = {f'evidence:{key}': 'PASS' if value else 'UNVERIFIED' for key, value in records.items()}
    pairs = []
    parent = {key: key for key in ids}

    def group(key):
        while parent[key] != key:
            key = parent[key]
        return key

    for pair_index, (left, right) in enumerate(combinations(ids, 2)):
        a, b = records[left], records[right]
        relation, derived, basis, state = 'uncertain', None, None, 'UNVERIFIED'
        same_source = a is not None and b is not None and all(
            a[key] == b[key] for key in ('repository', 'source_sha', 'source_path', 'work_id', 'witness'))
        if same_source:
            relation, basis, state = 'same_source_family', 'same pinned source/work/witness', 'PASS'
        approved = _read_capability(dependency_reader, {'evidence_ids': [left, right]})
        try:
            _json(approved)
            valid = (a is not None and b is not None and _same(approved.get('evidence'), [a, b])
                     and isinstance(approved.get('relationship'), str)
                     and approved['relationship'] in INDEPENDENCE_STATES
                     and all(_text(approved.get(key)) for key in ('basis', 'reviewer', 'rationale'))
                     and 'derived_evidence_id' in approved)
            if valid:
                relation = approved['relationship']
                derived = approved['derived_evidence_id']
                valid = derived in (left, right) if relation == 'derived_from' else derived is None
            if valid:
                basis = {key: approved[key] for key in ('basis', 'reviewer', 'rationale')}
                state = 'UNVERIFIED' if relation == 'uncertain' else 'PASS'
                if same_source and relation == 'uncertain':
                    relation, basis, state = 'same_source_family', 'same pinned source/work/witness', 'PASS'
                if same_source and relation in ('independent', 'derived_from'):
                    relation, derived, state = 'uncertain', None, 'FAIL'
            elif approved:
                # A stale/malformed assessment cannot override observed identity.
                relation, derived, basis, state = ('same_source_family', None,
                    'same pinned source/work/witness', 'PASS') if same_source else ('uncertain', None, None, 'UNVERIFIED')
        except (ValueError, TypeError, RecursionError):
            pass
        checks[f'pair:{pair_index}'] = state
        pairs.append({'evidence_ids': [left, right], 'relationship': relation,
                      'derived_evidence_id': derived, 'basis': copy.deepcopy(basis)})
        if state == 'PASS' and relation in ('same_source_family', 'derived_from'):
            parent[group(right)] = group(left)
    groups = [[key for key in ids if group(key) == leader] for leader in dict.fromkeys(group(key) for key in ids)]
    # Transitive family/derivation chains cannot coexist with independent edges.
    if any(pair['relationship'] == 'independent' and group(pair['evidence_ids'][0]) == group(pair['evidence_ids'][1]) for pair in pairs):
        checks['consistent_families'] = 'FAIL'
    edges = {key: set() for key in ids}
    for pair in pairs:
        if pair['relationship'] == 'derived_from':
            child = pair['derived_evidence_id']
            edges[child].add(next(key for key in pair['evidence_ids'] if key != child))
    remaining = set(ids)
    while remaining:
        leaves = {key for key in remaining if not (edges[key] & remaining)}
        if not leaves:
            checks['acyclic_derivation'] = 'FAIL'
            break
        remaining -= leaves
    count = None
    if all(records.values()) and 'FAIL' not in checks.values():
        cross_pairs = [pair for pair in pairs if group(pair['evidence_ids'][0]) != group(pair['evidence_ids'][1])]
        if all(pair['relationship'] == 'independent' for pair in cross_pairs):
            count = len(groups)
    return {'status': _status(checks), 'evidence': [record for record in records.values() if record],
            'pairs': pairs, 'source_groups': groups, 'independent_source_count': count,
            'checks': checks}


def _scope(value):
    _json(value)
    if not isinstance(value, dict) or set(value) != {'corpora', 'source_revisions', 'constraints'}:
        raise ValueError('scope requires corpora, source_revisions, constraints')
    corpora, revisions = value['corpora'], value['source_revisions']
    if not _strings(corpora) or not corpora or len(set(corpora)) != len(corpora) or not _strings(value['constraints']):
        raise ValueError('invalid scope')
    if not isinstance(revisions, list) or len(revisions) != len(corpora):
        raise ValueError('scope must pin every corpus')
    for item in revisions:
        if not isinstance(item, dict) or set(item) != {'corpus', 'repository', 'source_sha'}:
            raise ValueError('invalid source revision')
        if not _text(item['corpus']) or not _text(item['repository']) or not _sha(item['source_sha']):
            raise ValueError('invalid source revision')
    if {item['corpus'] for item in revisions} != set(corpora):
        raise ValueError('ambiguous source revisions')


def make_counterevidence_plan(claim, *, search_id, scope, steps, unchecked_scope):
    """Prepare a proposal; planning/keywords never attest execution."""
    subject = claim_subject(make_claim(claim))
    _scope(scope)
    if not _text(search_id) or not _strings(unchecked_scope) or not isinstance(steps, list) or not steps:
        raise ValueError('search ID, steps and explicit unchecked scope required')
    seen = set()
    _json(steps)
    for step in steps:
        if not isinstance(step, dict) or set(step) != {'step_id', 'direction', 'operation', 'query', 'corpus', 'target_id'}:
            raise ValueError('invalid search step')
        if (not _text(step['step_id']) or step['step_id'] in seen or step['direction'] not in SEARCH_DIRECTIONS
                or step['operation'] not in OPERATIONS or step['corpus'] not in scope['corpora']):
            raise ValueError('invalid or duplicate step')
        if step['operation'] == 'search':
            valid = _text(step['query']) and step['target_id'] is None
        else:
            valid = step['query'] is None and _text(step['target_id'])
        if not valid:
            raise ValueError('search requires query; other operations require target ID')
        seen.add(step['step_id'])
    return copy.deepcopy({'search_id': search_id, 'claim': subject, 'scope': scope,
                          'steps': steps, 'unchecked_scope': unchecked_scope, 'status': 'PLANNED'})


def _plan(value):
    if not isinstance(value, dict):
        raise ValueError('plan must be an object')
    return make_counterevidence_plan(value.get('claim'), **{key: value.get(key) for key in PLAN_FIELDS if key != 'claim'})


def search_counterevidence(plan, *, search_reader=None, evidence_reader=None):
    """Read actual bounded executions; opened evidence still needs semantics."""
    checks, attempts, candidates, evidence = {}, [], {}, {}
    try:
        proposed = _plan(plan)
    except (ValueError, TypeError, AttributeError, RecursionError):
        return {'status': 'REJECTED', 'plan': None, 'attempts': [], 'candidates': [],
                'verified_evidence': [], 'execution_complete': False, 'summary': None,
                'checks': {'plan': 'FAIL'}}
    subject = {key: proposed[key] for key in PLAN_FIELDS}
    response = _read_capability(search_reader, proposed['search_id'])
    try:
        _json(response)
        bound = (response.get('search_id') == proposed['search_id'] and _same(response.get('plan'), subject)
                 and all(_text(response.get(key)) for key in ('reviewer', 'rationale')))
    except (ValueError, TypeError, RecursionError):
        bound = False
    checks['execution_binding'] = 'PASS' if bound else 'UNVERIFIED'
    receipts = response.get('steps') if bound else None
    if not isinstance(receipts, list):
        receipts = []
    receipt_ids = [item.get('step_id') if isinstance(item, dict) else None for item in receipts]
    expected_ids = [step['step_id'] for step in proposed['steps']]
    if receipts and (not _strings(receipt_ids) or len(set(receipt_ids)) != len(receipt_ids) or not set(receipt_ids).issubset(expected_ids)):
        checks['receipt_ids'] = 'FAIL'
        receipts = []
    for step in proposed['steps']:
        receipt = next((item for item in receipts if item['step_id'] == step['step_id']), None)
        name = 'step:' + step['step_id']
        try:
            if (not isinstance(receipt, dict) or set(receipt) != {'step_id', 'status', 'complete', 'checked_scope', 'candidates', 'limitations'}
                    or receipt['status'] not in ('executed', 'failed', 'not_run') or type(receipt['complete']) is not bool
                    or not _strings(receipt['limitations']) or not isinstance(receipt['candidates'], list)):
                raise ValueError('unavailable execution receipt')
            hits = receipt['candidates']
            for hit in hits:
                if (not isinstance(hit, dict) or set(hit) != {'candidate_id', 'evidence_id', 'pointer'}
                        or not _text(hit['candidate_id']) or not isinstance(hit['pointer'], dict)
                        or hit['evidence_id'] is not None and not _text(hit['evidence_id'])):
                    raise ValueError('invalid candidate')
            if receipt['checked_scope'] is not None:
                _scope(receipt['checked_scope'])
            complete = receipt['status'] == 'executed' and receipt['complete'] and not receipt['limitations']
            checks[name] = 'PASS' if complete else 'UNVERIFIED'
            checked = receipt['checked_scope']
            if complete and not _same(checked, proposed['scope']):
                checks[name] = 'FAIL'
            elif checked is not None:
                if (not set(checked['corpora']).issubset(proposed['scope']['corpora'])
                        or any(item not in proposed['scope']['source_revisions'] for item in checked['source_revisions'])
                        or checked['constraints'] != proposed['scope']['constraints']):
                    checks[name] = 'FAIL'
            attempts.append(copy.deepcopy(receipt))
            # Failed/not-run attempts cannot provide observed hits.
            if receipt['status'] != 'executed' and (hits or receipt['complete']):
                checks[name] = 'FAIL'
            for hit in hits if receipt['status'] == 'executed' else []:
                key = hit['candidate_id']
                if key in candidates and not _same(candidates[key], hit):
                    checks['candidate:' + key] = 'FAIL'
                candidates[key] = copy.deepcopy(hit)
                eid = hit['evidence_id']
                record = _record(eid, evidence_reader) if eid else None
                checks['candidate:' + key] = checks.get('candidate:' + key, 'PASS' if record else 'UNVERIFIED')
                if record:
                    identity = {key: record[key] for key in ('corpus', 'repository', 'source_sha')}
                    if checked is None and checks['candidate:' + key] != 'FAIL':
                        checks['candidate:' + key] = 'UNVERIFIED'
                    elif checked is not None and identity not in checked['source_revisions']:
                        checks['candidate:' + key] = 'FAIL'
                    if eid in evidence and not _same(evidence[eid], record):
                        checks['candidate:' + key] = 'FAIL'
                    evidence[eid] = record
        except (ValueError, TypeError, RecursionError):
            checks[name] = 'UNVERIFIED'
    executed = checks['execution_binding'] == 'PASS' and all(checks.get('step:' + key) == 'PASS' for key in expected_ids)
    result_status = _status(checks, 'SEARCHED')
    summary = None
    if result_status == 'SEARCHED' and not candidates:
        summary = 'Không tìm thấy ứng viên phản chứng trong các truy vấn và phạm vi đã kiểm; không kết luận phản chứng không tồn tại.'
    return {'status': result_status, 'plan': subject, 'attempts': attempts,
            'candidates': list(candidates.values()), 'verified_evidence': list(evidence.values()),
            'execution_complete': executed, 'summary': summary, 'checks': checks}


def assess_counterevidence(claim, plan, *, review_id=None, evidence_reader=None,
                           search_reader=None, dependency_reader=None, assessment_reader=None):
    """Reuse approved B semantics; return assessments/proposals, never accepted."""
    searched = search_counterevidence(plan, search_reader=search_reader, evidence_reader=evidence_reader)
    checks = {'search': 'PASS' if searched['status'] == 'SEARCHED' else (
        'FAIL' if searched['status'] == 'REJECTED' else 'UNVERIFIED')}
    try:
        candidate = make_claim(claim)
        matches = searched['plan'] is not None and _same(claim_subject(candidate), searched['plan']['claim'])
        if not matches:
            raise ValueError('search belongs to a different claim snapshot')
    except (ValueError, TypeError, AttributeError, RecursionError):
        return {'status': 'REJECTED', 'claim': None, 'search': searched, 'independence': None,
                'assessment': None, 'decision': None, 'revision_proposal': None, 'checks': {**checks, 'claim_binding': 'FAIL'}}
    found_ids = [record['evidence_id'] for record in searched['verified_evidence']]
    candidate['counter_evidence_ids'] = list(dict.fromkeys(candidate['counter_evidence_ids'] + found_ids))
    ids = list(dict.fromkeys(candidate['supporting_evidence_ids'] + candidate['counter_evidence_ids']))
    independence = source_independence(ids, evidence_reader=evidence_reader, dependency_reader=dependency_reader) if ids else None
    checks['independence_inputs'] = 'UNVERIFIED' if independence is None else (
        'FAIL' if independence['status'] == 'REJECTED' else
        ('PASS' if len(independence['evidence']) == len(ids) else 'UNVERIFIED'))
    # Cache only the external host channel's observation, never proposal JSON.
    reviewed = _read_capability(assessment_reader, review_id) if _text(review_id) else {}
    assessed = assess_claim(candidate, review_id=review_id, evidence_reader=evidence_reader,
                            assessment_reader=lambda key: reviewed if key == review_id else {})
    checks['assessment'] = 'PASS' if assessed['status'] == 'ASSESSED' else (
        'FAIL' if assessed['status'] == 'REJECTED' else 'UNVERIFIED')
    current = {record['evidence_id']: record for record in assessed['evidence']}
    observations = searched['verified_evidence'] + (independence['evidence'] if independence else [])
    checks['evidence_snapshot_binding'] = 'PASS'
    for record in observations:
        eid = record['evidence_id']
        if eid not in current:
            checks['evidence_snapshot_binding'] = 'UNVERIFIED'
        elif not _same(record, current[eid]):
            checks['evidence_snapshot_binding'] = 'FAIL'
            break
    decision, revision = None, None
    extra = reviewed.get('counterevidence_review')
    bound = False
    try:
        _json(extra)
        bound = (isinstance(extra, dict) and set(extra) == {'search', 'independence', 'findings', 'action', 'rationale', 'prior_review_id', 'revision'}
                 and _same(extra['search'], searched) and _same(extra['independence'], independence))
        checks['counterevidence_binding'] = 'PASS' if bound else 'UNVERIFIED'
        if bound and checks['assessment'] == 'PASS':
            action, findings = extra['action'], extra['findings']
            valid = isinstance(action, str) and action in ACTIONS and _text(extra['rationale']) and isinstance(findings, list)
            valid = valid and all(isinstance(item, dict) and set(item) == {'evidence_id', 'effect', 'rationale'}
                                  and _text(item['evidence_id']) and item['effect'] in ('supports', 'irrelevant', 'limits', 'contradicts')
                                  and _text(item['rationale']) for item in findings)
            valid = valid and [item['evidence_id'] for item in findings] == candidate['counter_evidence_ids']
            level = assessed['claim']['verification_status']
            if valid:
                allowed = {'keep': {'DIRECT', 'STRONG', 'WEAK'}, 'lower_support': {'STRONG', 'WEAK'},
                           'unsupported': {'UNSUPPORTED'}, 'contradicted': {'CONTRADICTED'},
                           'reject': {'UNSUPPORTED', 'CONTRADICTED'},
                           'narrow': {'WEAK', 'UNSUPPORTED', 'CONTRADICTED'},
                           'rewrite': {'WEAK', 'UNSUPPORTED', 'CONTRADICTED'}}
                valid = level in allowed[action]
                if action == 'lower_support':
                    prior = assess_claim(claim, review_id=extra['prior_review_id'],
                                         evidence_reader=evidence_reader, assessment_reader=assessment_reader)
                    checks['prior_assessment'] = 'PASS' if prior['status'] == 'ASSESSED' else (
                        'FAIL' if prior['status'] == 'REJECTED' else 'UNVERIFIED')
                    if checks['prior_assessment'] == 'PASS':
                        order = {'DIRECT': 3, 'STRONG': 2, 'WEAK': 1}
                        valid = valid and order.get(prior['claim']['verification_status'], 0) > order[level]
                else:
                    valid = valid and extra['prior_review_id'] is None
                changing = action != 'keep'
                grounds = [item['evidence_id'] for item in findings if item['effect'] in ('limits', 'contradicts')]
                valid = valid and (bool(grounds) or not changing)
                if action in ('narrow', 'rewrite'):
                    payload = extra['revision']
                    valid = valid and isinstance(payload, dict) and set(payload) == {'claim_id', 'text'}
                    if valid:
                        revision = make_claim({**candidate, **payload, 'supersedes_claim_id': candidate['claim_id'],
                                               'revision_reason': extra['rationale'], 'revision_evidence_ids': grounds})
                        valid = revision['text'] != candidate['text']
                else:
                    valid = valid and extra['revision'] is None
            checks['decision_contract'] = 'PASS' if valid else 'FAIL'
            if valid:
                decision = {key: copy.deepcopy(extra[key]) for key in ('action', 'rationale', 'findings')}
    except (ValueError, TypeError, RecursionError):
        checks['decision_contract' if bound else 'counterevidence_binding'] = 'FAIL' if bound else 'UNVERIFIED'
    status = _status(checks)
    if status == 'ASSESSED' and decision['action'] in ('narrow', 'rewrite', 'reject'):
        status = 'REJECTED' if decision['action'] == 'reject' else 'REVISION_REQUIRED'
    if status not in ('ASSESSED', 'REVISION_REQUIRED'):
        revision = None
    return {'status': status, 'claim': assessed['claim'], 'search': searched, 'independence': independence,
            'assessment': assessed, 'decision': decision, 'revision_proposal': revision, 'checks': checks}
