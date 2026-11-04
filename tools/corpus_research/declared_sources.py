"""Opt-in declared-source binding. No lexical fallback or semantic authority."""
from copy import deepcopy
from .index import connect_readonly
from .local_host import source_request
from .verification import _path
from .claims import make_claim
from .research_run import safe_json

FIELDS = {'corpus','repository','work_id','source_path','source_sha','witness','segment_id','quotation'}

def search_expanded_sources(host, query, *, claim_id, corpus, limit=3):
    """Explicit additional discovery, never an implicit declared-source repair.

    Reuses Quick's ranking and fresh source checks. This cannot link evidence
    to a claim, mutate a run or grant semantic/publication authority.
    """
    if not isinstance(claim_id,str) or not claim_id.strip():
        raise ValueError('claim_id required')
    host.scope([corpus])
    return dict(claim_id=claim_id, source_origin='EXPANDED',
                replaces_declared_source=False, publication_authorized=False,
                discovery=host.quick(query,corpus=corpus,limit=limit))


def verify_declared_source(host, reference, *, claim_id, run_id=None):
    """Resolve indexed identities, then independently reopen pinned Git through A.

    Paths are repository-relative. Unknown fields (including edition) are errors;
    missing identity is never guessed. claim_id is association, not authority.
    """
    if not isinstance(reference,dict) or set(reference)-FIELDS:
        raise ValueError('unknown declared-source fields; edition is not a supported identity')
    if not isinstance(claim_id,str) or not claim_id.strip():raise ValueError('claim_id required')
    if any(not isinstance(v,str) or not v.strip() for v in reference.values()):raise ValueError('reference values must be nonempty strings')
    if not all(reference.get(k) for k in ('corpus','work_id')):raise ValueError('corpus and work_id required')
    ref=deepcopy(reference)
    safe_json(ref)
    def result(status,reason,**extra):return dict(status=status,reason=reason,claim_id=claim_id,declared_reference=ref,source_origin='DECLARED',publication_authorized=False,**extra)
    mapping=host.contract.get(ref['corpus'])
    if not mapping:return result('REJECTED','UNKNOWN_CORPUS')
    if ref.get('source_sha',mapping['source_sha'])!=mapping['source_sha']:return result('REJECTED','PIN_MISMATCH')
    if ref.get('repository',mapping['repository'])!=mapping['repository']:return result('REJECTED','REPOSITORY_MISMATCH')
    if 'source_path' in ref and not _path(ref['source_path']):raise ValueError('unsafe source_path')
    host.scope([ref['corpus']])
    con=connect_readonly(host.db)
    try:
        params=[ref['corpus'],ref['work_id']];where='corpus=? AND work_id=?'
        if 'source_path' in ref:where+=' AND source_path=?';params.append(mapping['repo_path']+'/'+ref['source_path'])
        # Bound distinct files, not arbitrary top lexical hits or silent SQL LIMIT.
        paths=[r[0] for r in con.execute('SELECT DISTINCT source_path FROM records WHERE '+where+' ORDER BY source_path LIMIT ?',params+[host.max_candidates+1])]
        if not paths:return result('UNVERIFIED','DECLARED_SOURCE_NOT_INDEXED')
        if len(paths)>host.max_candidates:return result('UNVERIFIED','CANDIDATE_BOUND_EXCEEDED')
        choices=[];failures=[];multi_unit=[];witness_mismatches=[]
        for path in paths:
            rows=[dict(r) for r in con.execute('SELECT * FROM records WHERE corpus=? AND work_id=? AND source_path=? ORDER BY sequence_no,id LIMIT ?',params[:2]+[path,host.max_candidates+1])]
            if any(r['source_sha']!=mapping['source_sha'] for r in rows):return result('REJECTED','INDEX_PIN_MISMATCH')
            # A precise source segment can lie inside an indexed chunk. Resolve
            # it from source, not by guessing a chunk/offset in caller JSON.
            first=rows[0];pointer=host.pointer(first)
            if 'segment_id' in ref:pointer.update(segment_id=ref['segment_id'],sequence_no=None)
            opened=host.source_reader(source_request(pointer),quotation=ref.get('quotation'))
            location=opened.get('location')
            if not location:failures.append(dict(source_path=pointer['source_path'],error=opened.get('error','location unavailable')));continue
            if 'witness' in ref and location['witness']!=ref['witness']:
                witness_mismatches.append(dict(source_path=pointer['source_path'],witness=location['witness']))
                continue
            if 'segment_id' not in ref and len(rows)>1:multi_unit.append(path)
            pointer.update(location)
            choices.append(pointer)
        if not choices:return result('UNVERIFIED','SOURCE_OR_SEGMENT_UNAVAILABLE' if failures else 'WITNESS_MISMATCH',failures=failures,witness_mismatches=witness_mismatches)
        if len(choices)!=1 or failures:return result('UNVERIFIED','AMBIGUOUS_DECLARED_SOURCE',candidates=choices,failures=failures)
        if multi_unit:return result('UNVERIFIED','SEGMENT_REQUIRED_FOR_MULTI_UNIT_SOURCE')
        gate=host.verify_pointer(choices[0],quotation=ref.get('quotation'),run_id=run_id)
        return result(gate['status'],'SOURCE_VERIFIED' if gate['status']=='VERIFIED' else 'EVIDENCE_GATE_NOT_VERIFIED',gate=gate)
    finally:con.close()

def create_declared_run(research, *, run_id, question, claims, source_references, corpora):
    """Append original claim text/IDs to a NEW draft, linked only to declared A evidence.

    Supplemental/counter discovery stays on the existing C APIs and must be
    linked explicitly; it never substitutes for failed declared references.
    """
    if not isinstance(claims,list) or not claims:raise ValueError('nonempty claims required')
    if not all(isinstance(c,dict) for c in claims):raise ValueError('claims must be objects')
    if not isinstance(source_references,dict):raise ValueError('source_references mapping required')
    prepared=[make_claim({**c,'run_id':run_id}) for c in claims]
    ids=[c['claim_id'] for c in prepared]
    if len(set(ids))!=len(ids) or set(ids)!=set(source_references):raise ValueError('references must bind each unique claim_id exactly')
    for c in prepared:
        if c['supporting_evidence_ids'] or c['counter_evidence_ids'] or c['supersedes_claim_id']:raise ValueError('new declared claims cannot supply evidence IDs or revisions')
        refs=source_references[c['claim_id']]
        if not isinstance(refs,list) or not refs:raise ValueError('each claim needs declared references')
        for ref in refs:
            if not isinstance(ref,dict) or ref.get('corpus') not in corpora:raise ValueError('reference outside declared corpus scope')
    scope=research.host.scope(corpora)
    bindings=[verify_declared_source(research.host,ref,claim_id=c['claim_id'],run_id=run_id) for c in prepared for ref in source_references[c['claim_id']]]
    run=research.store.create_run(dict(run_id=run_id,question=question,mode='research',scope=scope,queries=[],search_hypotheses=[],limitations=['Declared-source lookup only; semantic approval and counterevidence remain pending.']))
    for c in prepared:
        items=[b for b in bindings if b['claim_id']==c['claim_id']]
        complete=all(b['status']=='VERIFIED' for b in items)
        c['supporting_evidence_ids']=list(dict.fromkeys(b['gate']['evidence']['evidence_id'] for b in items if b['status']=='VERIFIED')) if complete else []
        if not complete:c['limitations'].append('DECLARED_SOURCE_UNRESOLVED: no substitute evidence was linked')
        for b in items:
            if b['status']=='VERIFIED':c['limitations']+=b['gate']['evidence']['limitations']
        c['limitations']=list(dict.fromkeys(c['limitations']))
        run=research.store.append_claim(run_id,c,expected_version=run['version'])
    import uuid
    artifact=research.path.parent/'artifacts'/(uuid.uuid4().hex+'-declared.json')
    research.check_output_path(artifact);artifact.parent.mkdir(parents=True,exist_ok=True)
    import json
    with artifact.open('x',encoding='utf-8') as f:json.dump(dict(declared_bindings=bindings,expanded_sources=[],publication_authorized=False),f,ensure_ascii=False,indent=2)
    # Store-relative path is audit DATA, never a reader or approval capability.
    run=research.store.update_draft(run_id,{'answer_artifact':'artifacts/'+artifact.name},expected_version=run['version'])
    run=research.store.capture(run_id,expected_version=run['version'],review_ids={},counter_requests=[])
    return dict(run=run,declared_bindings=bindings,expanded_sources=[],retrieval_artifact=str(artifact),metrics=dict(research.host.metrics),publication_authorized=False)
