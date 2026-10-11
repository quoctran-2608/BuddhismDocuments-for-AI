"""Phase B: claims, authenticated support assessments, gates and revisions.

No JSON object carries authority. The host wires evidence_reader(evidence_id)
to a store of genuine Phase A gate results (or re-runs that gate), and wires
assessment_reader(review_id) to an authenticated, already-approved assessment
channel. Neither capability may be selected by input JSON/model-generated code,
echo proposals, or treat arbitrary uploaded JSON as approval. Readers receive
IDs only. A failed/missing read leaves the claim pending, not UNSUPPORTED.

An approved assessment contains review_id, claim (claim_subject's exact result),
evidence (the complete current Evidence Records in support/counter ID order),
atomic (bool), support_level, scope (narrow_lookup/research), evidence_uses,
required_limitations, max_certainty, reviewer and rationale. Each evidence use
has evidence_id, basis and justification. Full snapshots bind text, provenance,
context, roles, witnesses and limitations; a matching hash is not approval.
Atomicity, scope, semantic support and appropriateness of the declared basis
are reviewer responsibilities, not punctuation heuristics or score mappings.

The final gate accepts only narrow textual/relationship lookups in quick mode.
Research and other types can be assessed, but cannot be accepted until C/D exist.
WEAK needs tentative presentation and explicit limitations. No free prose is
certified: verify_synthesis checks exact structured items after re-running all
gates, never trusting a serialized accepted set. Host applications must route
publication through these functions; JSON/status flags cannot enforce access
control against a host that bypasses them.

Revision helpers return copies of an append-only JSON history. The host owns
its persistence and must prevent external replacement of stored snapshots.
Original snapshots stay unchanged; history_claim projects superseded status.
Supply the complete host-held history to gates/export after revision; the host
must also revoke superseded approvals if it exposes claims without that history.
History/status data is never an alternative source of gate authority. No DB,
shell, remote integration, counterevidence search or Research Run is built here.
"""

from __future__ import annotations

import copy
import json

from .verification import (
    DIRECT_QUOTE_STATUSES, EVIDENCE_FIELDS, _path, _read_capability, _sha,
)


CLAIM_TYPES = frozenset({
    'textual', 'historical', 'relationship', 'comparative', 'interpretive',
    'empirical', 'metaphysical',
})
SUPPORT_LEVELS = frozenset({'DIRECT', 'STRONG', 'WEAK', 'UNSUPPORTED', 'CONTRADICTED'})
SUBJECT_FIELDS = (
    'claim_id', 'run_id', 'text', 'claim_type', 'supporting_evidence_ids',
    'counter_evidence_ids', 'limitations', 'supersedes_claim_id',
    'revision_reason', 'revision_evidence_ids', 'presentation',
)
SYNTHESIS_FIELDS = ('claim_id', 'text', 'verification_status', 'limitations', 'presentation')
EVIDENCE_BASES = {
    'textual': {'textual_report', 'primary_text'},
    'relationship': {'relationship'},
    'historical': {'historical_corroboration'},
    'comparative': {'comparison'},
    'interpretive': {'interpretation'},
    'empirical': {'empirical_observation'},
    'metaphysical': {'metaphysical_argument'},
}
DISCOVERY_CLASSES = frozenset({
    'computational_segmented', 'parallel_alignment', 'derived_critical_lemma',
    'auxiliary_reference',
})


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _strings(value):
    return isinstance(value, list) and all(_text(item) for item in value)


def _json(value):
    """Strict JSON; serialized equality also distinguishes bool from int."""
    def validate(item):
        if type(item) is dict:
            if not all(type(key) is str for key in item):
                raise ValueError('JSON object keys must be strings')
            for child in item.values():
                validate(child)
        elif type(item) is list:
            for child in item:
                validate(child)
        elif type(item) not in (str, int, float, bool, type(None)):
            raise ValueError('non-JSON value')
    validate(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _same(a, b):
    return _json(a) == _json(b)


def claim_subject(claim: dict) -> dict:
    """Content to bind in approval; never include self-declared gate labels."""
    result = {key: copy.deepcopy(claim.get(key)) for key in SUBJECT_FIELDS}
    for key in ('supporting_evidence_ids', 'counter_evidence_ids', 'limitations', 'revision_evidence_ids'):
        if key not in claim:
            result[key] = []
    if 'presentation' not in claim:
        result['presentation'] = {'certainty': None, 'quotations': []}
    return result


def _validate(subject):
    _json(subject)
    if not all(_text(subject.get(key)) for key in ('claim_id', 'text', 'claim_type')):
        raise ValueError('claim_id, text and claim_type are required')
    if subject['claim_type'] not in CLAIM_TYPES:
        raise ValueError('unknown claim_type')
    for key in ('run_id', 'supersedes_claim_id', 'revision_reason'):
        if subject[key] is not None and not _text(subject[key]):
            raise ValueError(f'invalid {key}')
    for key in ('supporting_evidence_ids', 'counter_evidence_ids', 'limitations', 'revision_evidence_ids'):
        value = subject[key]
        if not _strings(value) or len(set(value)) != len(value):
            raise ValueError(f'{key} must be a list of distinct nonempty strings')
    predecessor = subject['supersedes_claim_id']
    if predecessor is not None:
        if predecessor == subject['claim_id'] or not _text(subject['revision_reason']) or not subject['revision_evidence_ids']:
            raise ValueError('revision needs a distinct predecessor, reason and evidence')
        linked = subject['supporting_evidence_ids'] + subject['counter_evidence_ids']
        if not set(subject['revision_evidence_ids']).issubset(linked):
            raise ValueError('revision evidence must remain linked')
    elif subject['revision_reason'] is not None or subject['revision_evidence_ids']:
        raise ValueError('revision data requires a predecessor')
    presentation = subject['presentation']
    if not isinstance(presentation, dict) or set(presentation) != {'certainty', 'quotations'}:
        raise ValueError('presentation requires certainty and quotations only')
    if presentation['certainty'] not in (None, 'tentative', 'asserted') or not isinstance(presentation['quotations'], list):
        raise ValueError('invalid presentation')
    for quote in presentation['quotations']:
        if not isinstance(quote, dict) or set(quote) != {'evidence_id', 'text', 'kind', 'text_role', 'witness'}:
            raise ValueError('invalid quotation declaration')
        if not all(_text(quote[key]) for key in ('evidence_id', 'text', 'text_role')) or quote['kind'] not in ('direct', 'paraphrase'):
            raise ValueError('invalid quotation declaration')
        if quote['witness'] is not None and not _text(quote['witness']):
            raise ValueError('invalid quotation witness')


def make_claim(payload: dict) -> dict:
    """Create a candidate, with no inferred support, independence or atomicity."""
    if not isinstance(payload, dict):
        raise ValueError('claim must be an object')
    subject = claim_subject(payload)
    _validate(subject)
    return {**subject, 'status': 'candidate', 'verification_status': None,
            'independence_status': 'uncertain'}


def _evidence_record(result, evidence_id):
    """Validate the host's A result envelope, not a candidate's VERIFIED flag."""
    record = result.get('evidence')
    checks = result.get('checks')
    quote = result.get('quote')
    if (result.get('status') != 'VERIFIED' or result.get('source_opened') is not True
            or not isinstance(record, dict) or not isinstance(checks, dict)
            or not isinstance(quote, dict)):
        return None
    if (record.get('state') != 'VERIFIED' or record.get('evidence_id') != evidence_id
            or any(key not in record for key in EVIDENCE_FIELDS)):
        return None
    if (not all(_text(record[key]) for key in ('corpus', 'repository', 'evidence_class', 'text_role'))
            or not _sha(record['source_sha']) or not _path(record['source_path'])):
        return None
    if record['evidence_class'] not in DISCOVERY_CLASSES | {'canonical_root', 'authoritative_structured', 'metadata_relationship'}:
        return None
    for key in ('run_id', 'source_blob_sha', 'indexed_source_path', 'work_id', 'segment_id', 'language', 'witness', 'quotation', 'retrieval_query'):
        if record[key] is not None and not _text(record[key]):
            return None
    if record['source_blob_sha'] is not None and not _sha(record['source_blob_sha']):
        return None
    sequence = record['sequence_no']
    if sequence is not None and (type(sequence) is not int or sequence < 0):
        return None
    for key in ('independent_source', 'required_provenance'):
        if not isinstance(checks.get(key), dict) or checks[key].get('status') != 'PASS':
            return None
    for check in checks.values():
        if not isinstance(check, dict) or check.get('status') == 'FAIL':
            return None
        if check.get('required') is True and check.get('status') not in ('PASS', 'NOT_APPLICABLE'):
            return None
    if quote.get('status') != record.get('quote_verification_status'):
        return None
    if record.get('quotation') is not None:
        status = record['quote_verification_status']
        if status in DIRECT_QUOTE_STATUSES:
            if quote.get('direct_quote_allowed') is not True:
                return None
        elif status != 'PARAPHRASE' or quote.get('paraphrase_allowed') is not True:
            return None
    context = record.get('context')
    if not isinstance(context, dict) or set(context) != {'before', 'text', 'after'}:
        return None
    if not all(isinstance(value, str) for value in context.values()) or not _text(context['text']):
        return None
    snapshot = {key: copy.deepcopy(record[key]) for key in EVIDENCE_FIELDS}
    snapshot['state'] = 'VERIFIED'
    _json(snapshot)
    return snapshot


def assess_claim(claim: dict, *, review_id=None, evidence_reader=None, assessment_reader=None) -> dict:
    """Read approved semantic support; checks report PASS/FAIL/UNVERIFIED.

    Missing approval is UNVERIFIED, distinct from assessed UNSUPPORTED. Trusted
    readers can retrieve cached A results or run A again; cached stores must
    invalidate records when their content/provenance changes.
    """
    checks = {}

    def check(name, status, detail=''):
        checks[name] = {'status': status, 'detail': detail}

    evidence = []
    assessment = None
    try:
        candidate = make_claim(claim)
    except (ValueError, TypeError, AttributeError, RecursionError):
        return {'status': 'REJECTED', 'claim': None, 'evidence': [], 'assessment': None,
                'checks': {'claim_structure': {'status': 'FAIL', 'detail': 'invalid claim data'}}}
    check('claim_structure', 'PASS')
    ids = list(dict.fromkeys(candidate['supporting_evidence_ids'] + candidate['counter_evidence_ids']))
    check('supporting_evidence', 'PASS' if candidate['supporting_evidence_ids'] else 'FAIL')
    for evidence_id in ids:
        try:
            record = _evidence_record(_read_capability(evidence_reader, evidence_id), evidence_id)
        except (ValueError, TypeError, RecursionError):
            record = None
        check(f'evidence:{evidence_id}', 'PASS' if record else 'UNVERIFIED', 'requires a host-provided Phase A gate result')
        if record:
            evidence.append(record)
    reviewed = _read_capability(assessment_reader, review_id) if _text(review_id) else {}
    try:
        _json(reviewed)
        bound = (reviewed.get('review_id') == review_id
                 and _same(reviewed.get('claim'), claim_subject(candidate))
                 and len(evidence) == len(ids) and _same(reviewed.get('evidence'), evidence))
    except (ValueError, TypeError, RecursionError):
        bound = False
    check('approved_binding', 'PASS' if bound else 'UNVERIFIED', 'approval must bind the exact current claim and evidence snapshots')
    if bound:
        level = reviewed.get('support_level')
        uses = reviewed.get('evidence_uses')
        required = reviewed.get('required_limitations')
        valid = (isinstance(level, str) and level in SUPPORT_LEVELS
                 and type(reviewed.get('atomic')) is bool
                 and reviewed.get('scope') in ('narrow_lookup', 'research')
                 and reviewed.get('max_certainty') in ('tentative', 'asserted')
                 and _strings(required) and _text(reviewed.get('reviewer'))
                 and _text(reviewed.get('rationale')) and isinstance(uses, list))
        check('assessment_contract', 'PASS' if valid else 'UNVERIFIED')
        if valid:
            assessment = {key: copy.deepcopy(reviewed[key]) for key in (
                'review_id', 'atomic', 'support_level', 'scope', 'evidence_uses',
                'required_limitations', 'max_certainty', 'reviewer', 'rationale',
            )}
            candidate['verification_status'] = level
            check('atomic', 'PASS' if reviewed['atomic'] else 'FAIL', 'semantic atomicity is approved by the reviewer')
            uses_valid = all(isinstance(use, dict) and set(use) == {'evidence_id', 'basis', 'justification'}
                             and _text(use['evidence_id']) and _text(use['basis']) and _text(use['justification']) for use in uses)
            uses_valid = uses_valid and [use['evidence_id'] for use in uses] == ids
            check('evidence_uses', 'PASS' if uses_valid else 'FAIL')
            if uses_valid:
                for record, use in zip(evidence, uses):
                    basis = use['basis']
                    compatible = basis in EVIDENCE_BASES[candidate['claim_type']]
                    if record['evidence_class'] == 'metadata_relationship':
                        compatible = compatible and basis == 'relationship'
                    if basis == 'primary_text':
                        compatible = compatible and record['evidence_class'] in {'canonical_root', 'authoritative_structured'}
                        compatible = compatible and record['text_role'] == 'root_text' and _text(record['witness'])
                    check(f'type:{record["evidence_id"]}', 'PASS' if compatible else 'FAIL', 'source authority is separate from claim-specific support')
            required = set(required)
            for record in evidence:
                limitations = record.get('limitations')
                if limitations is not None and not _strings(limitations):
                    check('evidence_limitations', 'FAIL')
                else:
                    required.update(limitations or [])
                if record['evidence_class'] in DISCOVERY_CLASSES:
                    required.add(f'discovery_source:{record["evidence_id"]}:{record["evidence_class"]}')
            check('limitations', 'PASS' if required.issubset(candidate['limitations']) else 'FAIL', 'all evidence/reviewer limitations must be retained')
            certainty = candidate['presentation']['certainty']
            check('certainty', 'UNVERIFIED' if certainty is None else (
                'FAIL' if certainty == 'asserted' and reviewed['max_certainty'] != 'asserted' else 'PASS'))
            if level == 'WEAK':
                check('weak_presentation', 'PASS' if certainty == 'tentative' and candidate['limitations'] else 'FAIL')
    records = {record['evidence_id']: record for record in evidence}
    for index, quote in enumerate(candidate['presentation']['quotations']):
        record = records.get(quote['evidence_id'])
        if record is None:
            check(f'quotation:{index}', 'UNVERIFIED' if quote['evidence_id'] in ids else 'FAIL')
            continue
        appropriate = (quote['text'] == record['quotation'] and quote['text_role'] == record['text_role']
                       and quote['witness'] == record['witness'] and record['evidence_class'] != 'metadata_relationship')
        status = record['quote_verification_status']
        appropriate = appropriate and (status in DIRECT_QUOTE_STATUSES if quote['kind'] == 'direct' else status == 'PARAPHRASE')
        check(f'quotation:{index}', 'PASS' if appropriate else 'FAIL')
    failed = any(check['status'] == 'FAIL' for check in checks.values())
    pending = any(check['status'] == 'UNVERIFIED' for check in checks.values())
    return {'status': 'REJECTED' if failed else ('UNVERIFIED' if pending else 'ASSESSED'),
            'claim': candidate, 'evidence': evidence, 'assessment': assessment, 'checks': checks}


def final_claim_gate(claim: dict, *, mode='quick', review_id=None, evidence_reader=None, assessment_reader=None, history=None) -> dict:
    """The only publisher of accepted status; no C/D completion flags accepted."""
    result = assess_claim(claim, review_id=review_id, evidence_reader=evidence_reader, assessment_reader=assessment_reader)
    checks = result['checks']
    checks['mode'] = {'status': 'PASS' if mode in ('quick', 'research') else 'FAIL', 'detail': ''}
    candidate = result['claim']
    assessment = result['assessment']
    superseded = False
    if candidate:
        if history is not None:
            try:
                index, replaced = _history_index(history)
                matches = candidate['claim_id'] in index and _same(index[candidate['claim_id']], claim_subject(candidate))
                checks['history'] = {'status': 'PASS' if matches else 'FAIL', 'detail': 'claim must match its immutable history snapshot'}
                superseded = matches and candidate['claim_id'] in replaced
            except (ValueError, TypeError, RecursionError):
                checks['history'] = {'status': 'FAIL', 'detail': 'invalid revision history'}
        elif candidate['supersedes_claim_id'] is not None:
            checks['history'] = {'status': 'UNVERIFIED', 'detail': 'revision requires its complete history'}
        if mode == 'research' and not _text(candidate['run_id']):
            checks['run_id'] = {'status': 'FAIL', 'detail': 'research requires a run ID'}
        research = mode == 'research' or candidate['claim_type'] not in ('textual', 'relationship')
        research = research or (assessment is not None and assessment['scope'] != 'narrow_lookup')
        if research:
            checks['research_conditions'] = {'status': 'UNVERIFIED', 'detail': 'Phase C counterevidence/independence and Phase D Research Run are not implemented'}
        if assessment:
            level = assessment['support_level']
            checks['support_level'] = {'status': 'FAIL' if level in ('UNSUPPORTED', 'CONTRADICTED') else 'PASS', 'detail': level}
    failed = any(check['status'] == 'FAIL' for check in checks.values())
    pending = any(check['status'] == 'UNVERIFIED' for check in checks.values())
    status = 'rejected' if failed else ('superseded' if superseded else ('candidate' if pending else 'accepted'))
    if candidate:
        candidate['status'] = status
    return {**result, 'status': status, 'mode': mode if mode in ('quick', 'research') else None}


def accepted_claim_set(claims: list, review_ids: dict, **gate_options) -> dict:
    """Re-run gates and export only current accepted structured claims.

    Outputs are data, not reusable authority. Re-evaluate when publishing, with
    current readers. Duplicate IDs and malformed batches fail closed.
    """
    if not isinstance(claims, list) or not isinstance(review_ids, dict):
        raise ValueError('claims and review_ids must be structured data')
    ids = [item.get('claim_id') if isinstance(item, dict) else None for item in claims]
    if not all(_text(item) for item in ids) or len(set(ids)) != len(ids):
        raise ValueError('claim IDs must be valid and unique')
    # A complete history can contain old and current snapshots. Old claims must
    # not re-enter publication merely because their original approval still exists.
    history = gate_options.get('history')
    history = claims if history is None else history
    index, _ = _history_index(history)
    if not all(claim['claim_id'] in index and _same(index[claim['claim_id']], claim_subject(claim)) for claim in claims):
        raise ValueError('batch must match the complete supplied history')
    gate_options['history'] = history
    results = [final_claim_gate(claim, review_id=review_ids.get(claim['claim_id']), **gate_options) for claim in claims]
    return {'accepted_claims': [result['claim'] for result in results if result['status'] == 'accepted'],
            'results': results}


def synthesis_item(claim: dict) -> dict:
    """Render only checked fields; this helper itself grants no authority."""
    return {key: copy.deepcopy(claim.get(key)) for key in SYNTHESIS_FIELDS}


def verify_synthesis(items, claims, review_ids, **gate_options) -> dict:
    """Check an exact structured list, not the semantics of arbitrary prose."""
    try:
        approved = accepted_claim_set(claims, review_ids, **gate_options)['accepted_claims']
        available = {claim['claim_id']: synthesis_item(claim) for claim in approved}
        if not isinstance(items, list):
            raise ValueError('synthesis must be a structured list')
        used = set()
        for item in items:
            if not isinstance(item, dict) or set(item) != set(SYNTHESIS_FIELDS) or not _text(item.get('claim_id')):
                raise ValueError('unexpected synthesis fields or free prose')
            claim_id = item['claim_id']
            if claim_id in used or claim_id not in available or not _same(item, available[claim_id]):
                raise ValueError('unaccepted, duplicated or changed claim')
            used.add(claim_id)
    except (ValueError, TypeError, RecursionError):
        return {'status': 'REJECTED', 'items': [], 'detail': 'synthesis requires exact currently accepted structured claims'}
    return {'status': 'VERIFIED', 'items': copy.deepcopy(items), 'detail': 'structured claims only; free prose is not certified'}


def _history_index(history):
    if not isinstance(history, list):
        raise ValueError('history must be an append-only list')
    index = {}
    replaced = set()
    for snapshot in history:
        if not isinstance(snapshot, dict):
            raise ValueError('invalid history snapshot')
        subject = claim_subject(snapshot)
        _validate(subject)
        claim_id = subject['claim_id']
        if claim_id in index:
            raise ValueError('cannot overwrite a claim ID')
        predecessor = subject['supersedes_claim_id']
        if predecessor is not None:
            if predecessor not in index or predecessor in replaced:
                raise ValueError('predecessor must be an earlier active claim; cycles/branches are forbidden')
            old = index[predecessor]
            if old['run_id'] != subject['run_id'] or not set(old['counter_evidence_ids']).issubset(subject['counter_evidence_ids']):
                raise ValueError('revision must preserve run and counterevidence')
            replaced.add(predecessor)
        index[claim_id] = subject
    return index, replaced


def append_claim(history: list, claim: dict) -> list:
    """Append a new candidate; labels in input/history never confer acceptance."""
    index, _ = _history_index(history)
    candidate = make_claim(claim)
    if candidate['claim_id'] in index or candidate['supersedes_claim_id'] is not None:
        raise ValueError('new IDs only; use revise_claim to supersede a claim')
    return [*copy.deepcopy(history), candidate]


def revise_claim(history: list, old_claim_id: str, payload: dict, *, reason: str, revision_evidence_ids: list) -> list:
    """Append a candidate revision without editing any original snapshot."""
    index, replaced = _history_index(history)
    if not _text(old_claim_id) or old_claim_id not in index or old_claim_id in replaced:
        raise ValueError('revision requires an active predecessor')
    if not isinstance(payload, dict) or not _text(payload.get('claim_id')) or not _text(payload.get('text')):
        raise ValueError('revision requires a new ID and explicit text')
    old = index[old_claim_id]
    subject = {**copy.deepcopy(old), **copy.deepcopy(payload)}
    if subject['claim_id'] in index or subject['run_id'] != old['run_id']:
        raise ValueError('cannot reuse an ID or change run')
    counter = subject['counter_evidence_ids']
    if not _strings(counter):
        raise ValueError('invalid counterevidence IDs')
    subject['counter_evidence_ids'] = list(dict.fromkeys(old['counter_evidence_ids'] + counter))
    subject.update(supersedes_claim_id=old_claim_id, revision_reason=reason,
                   revision_evidence_ids=copy.deepcopy(revision_evidence_ids))
    candidate = make_claim(subject)
    result = [*copy.deepcopy(history), candidate]
    _history_index(result)
    return result


def history_claim(history: list, claim_id: str) -> dict:
    """Read a copy with projected superseded status, retaining original data."""
    index, replaced = _history_index(history)
    if not _text(claim_id) or claim_id not in index:
        raise ValueError('unknown claim ID')
    original = next(claim for claim in history if claim['claim_id'] == claim_id)
    result = copy.deepcopy(original)
    if claim_id in replaced:
        result['status'] = 'superseded'
    return result
