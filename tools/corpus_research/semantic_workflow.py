"""Read-only Research/P0/1 integration and separate proposal artifacts for P0/2."""
from copy import deepcopy
from pathlib import Path
import json
import uuid

from .counterevidence import make_counterevidence_plan
from .research_store import ConflictError
from .semantic_assessment import assess_evidence, strings
from .model_adapter import json_bytes


def assess_research_claim(research, *, run_id, claim_id, expected_version, model=None, counter_queries=None):
    run=research.prepare(run_id)
    if run['version']!=expected_version:
        raise ConflictError('stale snapshot version')
    if run['main_repository_commit']!=research.host.context_reader(run_id)['main_repository_commit']:
        raise ConflictError('host commit changed; create a new draft with fresh sources')
    matches=[c for c in run['claims'] if c['claim_id']==claim_id]
    if len(matches)!=1:
        raise ValueError('claim not found in this run')
    blocked=(run['run_status']=='superseded' or claim_id in run['superseded_claim_ids']+run['rejected_claim_ids'])
    claim=matches[0]
    queries=counter_queries or []
    if not strings(queries) or len(queries)>2:
        raise ValueError('at most two explicit counter queries per claim')
    receipts=[];counter_ids=[]
    limits=list(run['limitations'])+list(run['scope']['constraints'])
    # Re-execute existing plans and optional explicitly requested lexical searches.
    # This is C's current bounded executor, not a new semantic search planner.
    requests=[r['plan'] for r in run['counter_requests'] if r['claim_id']==claim_id]
    if queries and not blocked:
        plan=make_counterevidence_plan(claim,search_id='p02-'+uuid.uuid4().hex,scope=run['scope'],
            steps=[dict(step_id=f'{i}-{j}',direction='exception',operation='search',query=q,corpus=c,target_id=None)
                   for i,c in enumerate(run['scope']['corpora']) for j,q in enumerate(queries)],
            unchecked_scope=['Bounded lexical candidates only; no global absence or semantic search completeness.'])
        requests.append(plan)
    if not blocked:
        for plan in requests:
            research.host.register_plan(plan)
            receipt=research.host.search_reader(plan['search_id'])
            receipts.append(receipt)
            for step in receipt['steps']:
                limits+=step['limitations']
                for candidate in step['candidates']:
                    if candidate['evidence_id']:
                        counter_ids.append(candidate['evidence_id'])
            limits+=plan['unchecked_scope']
    if not receipts:
        limits.append('COUNTER_SEARCH_NOT_EXECUTED: challenge covers supplied evidence only.')
    result=assess_evidence(claim,evidence_reader=research.host.evidence_reader,model=model,
        scope_limits=list(dict.fromkeys(limits)),counter_evidence_ids=list(dict.fromkeys(counter_ids)),blocked=blocked)
    result.update(run_id=run_id,run_version=run['version'],main_repository_commit=run['main_repository_commit'],
                  search_receipts=receipts,evidence_origins={eid:'EXPANDED_COUNTER_CANDIDATE' for eid in counter_ids})
    for eid in claim['supporting_evidence_ids']:
        result['evidence_origins'][eid]='CLAIM_LINKED_SOURCE'
    for eid in claim['counter_evidence_ids']:
        result['evidence_origins'][eid]='CLAIM_LINKED_COUNTER'
    current=research.store.get_run(run_id)
    if current['version']!=run['version'] or current['run_status']=='superseded':
        result['errors'].append('RUN_CHANGED_DURING_ASSESSMENT')
        result['synthesis'].update(assessment_status='UNRESOLVED',support_level=None,supporting_evidence_ids=[])
    return result


def report_markdown(result):
    """Concise cited rationale only, never private chain-of-thought or approval."""
    def block(value):
        text=value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)
        return '\n'.join('    '+line for line in text.splitlines())+'\n'
    syn=result['synthesis']
    labels={None:'Chưa thể kết luận', 'DIRECT':'Đề xuất hỗ trợ trực tiếp trong phạm vi đã nêu',
            'STRONG':'Đề xuất hỗ trợ trong phạm vi đã nêu', 'WEAK':'Đề xuất hỗ trợ một phần/có điều kiện',
            'UNSUPPORTED':'Đề xuất không đủ căn cứ', 'CONTRADICTED':'Đề xuất có chứng cứ phản bác'}
    sections=[('# BCR — AI semantic proposal (không phải phê duyệt học thuật)',result['inference_status']),
        ('## Mệnh đề được kiểm tra',dict(claim_id=result['claim']['claim_id'],text=result['claim']['text'],claim_type=result['claim']['claim_type'])),
        ('## Nguồn đã kiểm — thông tin kiểm bằng chương trình',dict(current_checks=result['source_verification'],provenance=syn['provenance'])),
        ('## AI đánh giá — proposal',result['support']),('## AI phản biện — proposal riêng',result['challenge']),
        ('## Kết luận giới hạn — luôn đọc cùng phạm vi bên dưới',dict(label=labels[syn['support_level']],assessment_status=syn['assessment_status'],support_level=syn['support_level'],supporting_evidence_ids=syn['supporting_evidence_ids'],counter_evidence_ids=syn['counter_evidence_ids'])),
        ('## Phạm vi và điều kiện bắt buộc',syn['scope_limits']),
        ('## Việc cần kiểm tra thêm',dict(missing=syn['missing_evidence'],questions=syn['unresolved_questions'],issues=syn['issues'],errors=result['errors'])),
        ('## Trạng thái',dict(semantic_approval=False,publication_authorized=False,source_independence=syn['source_independence'],independent_source_count=None))]
    return '\n'.join(heading+'\n\n'+block(value) for heading,value in sections)+'\nHUMAN_ADJUDICATION_PENDING · DISTRIBUTION_CLEARED = 0 · PUBLICATION_NOT_PERMITTED\n'


def write_assessment(research, result, output):
    paths=[Path(output).with_suffix('.json'),Path(output).with_suffix('.md')]
    for path in paths:
        research.check_output_path(path)
        if path.exists():
            raise ValueError('assessment requires fresh output paths')
    paths[0].parent.mkdir(parents=True,exist_ok=True)
    for path,data in zip(paths,(json_bytes(result),report_markdown(result).encode('utf-8'))):
        with path.open('xb') as handle:
            handle.write(data)
    return dict(json=str(paths[0]),markdown=str(paths[1]),publication_authorized=False)
