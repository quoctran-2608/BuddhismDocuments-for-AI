"""Deterministic SOFTWARE transport fixture, NOT model inference or truth labels.

No Buddhist interpretation is performed. Scenarios exercise pipeline branches.
"""
import json
import sys
import time

request=json.load(sys.stdin)
scenario=sys.argv[1] if len(sys.argv)>1 else 'keep'
if scenario=='timeout':
    time.sleep(5)
if scenario=='malformed':
    print('{');raise SystemExit
if scenario=='duplicate':
    print('{"claim_id":"a","claim_id":"b"}');raise SystemExit
if scenario=='overflow':
    print('X'*10000);raise SystemExit
if scenario=='exit':
    raise SystemExit(3)
evidence=request['data']['evidence'];ids=[e['evidence_id'] for e in evidence]
result=dict(claim_id=request['data']['claim']['claim_id'],assessment_status='PROPOSED',support_level='DIRECT',
    supporting_evidence_ids=ids[:1],considered_evidence_ids=ids,
    reasoning=[dict(evidence_id=e['evidence_id'],quote=e['quotation'],explanation='Software fixture rationale, not semantic ground truth.') for e in evidence],
    scope_limits=['Only under the supplied temporal/causal conditions.'],missing_evidence=[],unresolved_questions=[])
if request['stage']=='challenge':
    result.update(action='KEEP',counter_evidence_ids=[],issues=[])
    if scenario=='lower':
        result.update(action='LOWER',support_level='WEAK',scope_limits=['Retain the explicit exception and time condition.'])
    if scenario=='limit':
        result.update(action='LIMIT',support_level='STRONG')
    if scenario=='unresolved':
        result.update(action='UNRESOLVED',assessment_status='UNRESOLVED',support_level=None,
            unresolved_questions=['Unresolved causal scope in this scripted fixture.'])
    if scenario=='contradiction':
        result.update(action='CONTRADICTION',support_level='CONTRADICTED',counter_evidence_ids=ids[-1:])
    if scenario=='issue':
        result['issues']=[dict(issue='Ignored important counterexample',impact='UNRESOLVED',evidence_ids=ids[-1:],explanation='Scripted adverse condition requires resolution.')]
    if scenario=='omit':
        result['reasoning']=result['reasoning'][:1]
    if scenario=='upgrade':
        result.update(action='LOWER',support_level='DIRECT')
if scenario=='id':
    result['supporting_evidence_ids']=['invented']
if scenario=='quote':
    result['reasoning'][0]['quote']='This sentence does not occur in the verified fixture.'
if scenario=='approved':
    result['approved']=True
if scenario=='accepted':
    result['accepted']=True
if scenario=='publication':
    result['publication_authorized']=True
if scenario=='private':
    result['password']='DO_NOT_PERSIST'
if scenario=='role':
    result['provenance']=[{'text_role':'root_text','witness':'invented-primary-witness'}]
if scenario=='no-rationale':
    result['reasoning']=[]
print(json.dumps(result,ensure_ascii=False))
