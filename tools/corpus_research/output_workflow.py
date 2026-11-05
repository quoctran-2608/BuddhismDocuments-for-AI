"""Local pinned fact readers and opt-in output export; old report paths unchanged."""
from copy import deepcopy
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

from .local_host import source_request
from .model_adapter import json_bytes,strict_json
from .output_verification import OutputContext,source_identity,verify_output
from .verification import read_local_source
from .research_store import ConflictError


class LocalOutputFacts:
    def __init__(self,host):
        self.host=host

    def __call__(self,request):
        kind,e=request['kind'],request['evidence']
        source=source_identity(e)
        if kind=='IDENTIFIER' and e['corpus']=='suttacentral-bilara':
            namespaces={'SC_BILARA_UID':[e['work_id']]}
            provenance=[]
            corpus='suttacentral-relations';mapping=self.host.contract.get(corpus)
            if mapping:
                req=dict(corpus=corpus,repository=mapping['repository'],source_sha=mapping['source_sha'],
                    source_path='structure/text_extra_info.json',work_id=e['work_id'],segment_id=None,sequence_no=None)
                opened=read_local_source(self.host.source_root,req,self.host.contract)
                if opened.get('content'):
                    rows=strict_json(opened['content'])
                    matches=[r for r in rows if isinstance(r,dict) and r.get('uid')==e['work_id']] if isinstance(rows,list) else []
                    if len(matches)==1:
                        row=matches[0]
                        for ns,key in [('SC_ACRONYM','acronym'),('SC_ALT_ACRONYM','alt_acronym'),('SC_VOLPAGE','volpage')]:
                            if isinstance(row.get(key),str):namespaces[ns]=[row[key]]
                        provenance=[dict(corpus=corpus,repository=mapping['repository'],source_sha=mapping['source_sha'],
                            source_path=req['source_path'],source_blob_sha=opened['source_blob_sha'],uid=e['work_id'],
                            evidence_class='metadata_relationship',text_role='metadata')]
            return dict(kind=kind,source=source,namespaces=namespaces,provenance=provenance)
        if kind!='TITLE':
            return {}
        opened=self.host.source_reader(source_request(e))
        if not opened.get('content') or opened.get('source_blob_sha')!=e['source_blob_sha']:
            return {}
        values=[];selector=None
        if e['corpus']=='suttacentral-bilara' and isinstance(e['work_id'],str) and re.fullmatch(r'sn\d+\.\d+',e['work_id']) and e['text_role'] in ('root_text','translation_main'):
            # Explicit initial coverage: SN heading :0.3. No guessing another
            # unit from title-like wording, index labels or filename similarity.
            key=e['work_id']+':0.3';data=strict_json(opened['content'])
            if isinstance(data,dict) and isinstance(data.get(key),str) and data[key].strip():
                values=[data[key].strip()];selector=key
        elif e['corpus'] in ('cbeta-tei','84000-tei'):
            root=ET.fromstring(opened['content'])
            nodes=root.findall('.//{http://www.tei-c.org/ns/1.0}teiHeader/{http://www.tei-c.org/ns/1.0}fileDesc/{http://www.tei-c.org/ns/1.0}titleStmt/{http://www.tei-c.org/ns/1.0}title')
            values=[' '.join(''.join(n.itertext()).split()) for n in nodes]
            values=[v for v in values if v];selector='teiHeader/fileDesc/titleStmt/title'
        if not values:return {}
        return dict(kind=kind,source=source,values=values,
            provenance=dict(source=source,selector=selector,text_role='title_metadata'))


def check_research_output(research, *, run_id, expected_version, document, notes=None):
    run=research.prepare(run_id)
    if type(expected_version) is not int or run['version']!=expected_version:
        raise ConflictError('stale output snapshot version')
    claims=deepcopy(run['claims'])
    for c in claims:
        if run['run_status']=='superseded' or c['claim_id'] in run['superseded_claim_ids']+run['rejected_claim_ids']:
            c['limitations'].append('DECLARED_SOURCE_UNRESOLVED: claim/run blocked at output')
    context=OutputContext(claims=claims,notes=notes,evidence_reader=research.host.evidence_reader,
                          fact_reader=LocalOutputFacts(research.host))
    result=verify_output(document,context)
    current=research.store.get_run(run_id)
    if current['version']!=run['version'] or current['run_status']!=run['run_status']:
        result.update(status='UNVERIFIED',checked_items=[])
        result['checks'].append(dict(item_id=None,check='RUN_CHANGED',status='UNVERIFIED',detail=''))
    result.update(run_id=run_id,run_version=run['version'],main_repository_commit=research.host.context_reader(run_id)['main_repository_commit'])
    return result


def _checked_markdown(result):
    if result['status']!='CHECKED':
        raise ValueError('report export blocked: structured output did not pass')
    def block(value):
        return '\n'.join('    '+line for line in json.dumps(value,ensure_ascii=False,indent=2).splitlines())
    return '# BCR — structured fields checked; semantic interpretation remains unapproved\n\n'+ '\n\n'.join(block(i) for i in result['checked_items'])+'\n\n'+block(result['limitations'])+'\n\nHUMAN_ADJUDICATION_PENDING · DISTRIBUTION_CLEARED = 0 · PUBLICATION_NOT_PERMITTED\n'


def checked_markdown(document,context):
    """Public renderer always checks again; saved CHECKED JSON is not a ticket."""
    return _checked_markdown(verify_output(document,context))


def write_output_check(research, *,run_id,expected_version,document,output,notes=None):
    """Check current host sources/run at export, never accept a saved receipt."""
    result=check_research_output(research,run_id=run_id,expected_version=expected_version,document=document,notes=notes)
    paths=[Path(output).with_suffix('.json')]
    if result['status']=='CHECKED':paths.append(Path(output).with_suffix('.md'))
    # Also reserve the Markdown name on failure: never leave an older successful
    # report beside a new rejection receipt at the same prefix.
    for path in [Path(output).with_suffix('.json'),Path(output).with_suffix('.md')]:
        research.check_output_path(path)
        if path.exists():raise ValueError('fresh output paths required')
    data=[json_bytes(result)]+([_checked_markdown(result).encode('utf-8')] if len(paths)==2 else [])
    paths[0].parent.mkdir(parents=True,exist_ok=True)
    for path,raw in zip(paths,data):
        with path.open('xb') as handle:handle.write(raw)
    result['artifacts']=dict(receipt=str(paths[0]),report=str(paths[1]) if len(paths)==2 else None,publication_authorized=False)
    return result
