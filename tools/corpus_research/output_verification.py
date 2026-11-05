"""P0/3 structured output checks, not a semantic or publication approval gate.

Only host-held readers establish current source facts. Recorded conditions and
speaker/stance notes remain interpretations: code checks preservation, not truth.
"""
from copy import deepcopy
import hashlib
import unicodedata

from .claims import _evidence_record, make_claim
from .model_adapter import json_bytes
from .verification import _read_capability, verify_quote

SCHEMA='bcr-output-1'
SOURCE_FIELDS=('corpus','repository','source_path','source_sha','source_blob_sha','work_id',
               'segment_id','witness','text_role','evidence_class')
BASE={'item_id','claim_id','kind','text'}
SINGLE={'evidence_id','source'}
EXTRA={'TITLE':SINGLE,'QUOTE':SINGLE|{'use'},'IDENTIFIER':SINGLE|{'namespace'},
       'CONCLUSION':{'evidence_ids','condition_ids','scope_limit_ids','attributions','scope','label'}}
STANCES={'ENDORSED','REPORTED','REPORTED_REJECTED','UNRESOLVED'}


def text(value):
    return isinstance(value,str) and 0<len(value.strip())<=16000


def ids(value):
    return isinstance(value,list) and len(value)<=128 and all(text(x) for x in value) and len(set(value))==len(value)


def source_identity(evidence):
    return {k:deepcopy(evidence[k]) for k in SOURCE_FIELDS}


def observe_tool_result(exit_code, payload):
    """Interpret a tool receipt, NEVER authenticate serialized JSON as a reader."""
    outer=payload.get('status') if isinstance(payload,dict) else None
    gate=payload.get('gate',payload) if isinstance(payload,dict) else {}
    eid=gate.get('evidence',{}).get('evidence_id') if isinstance(gate,dict) and isinstance(gate.get('evidence'),dict) else None
    valid=False
    try:
        valid=type(exit_code) is int and exit_code==0 and outer=='VERIFIED' and _evidence_record(gate,eid) is not None
    except (ValueError,TypeError,KeyError,AttributeError):
        pass
    return dict(process_succeeded=type(exit_code) is int and exit_code==0,
                observed_status=outer,source_gate_observed_verified=valid,
                authenticates_source=False,publication_authorized=False)


class OutputContext:
    """Host boundary, outside output JSON. Notes are recorded AI interpretations.

    A caller can register new notes, but cannot claim their semantic correctness
    from a matching hash. No snapshot/notes file is an A/B reader capability.
    """
    def __init__(self, *, evidence_reader, claims, notes=None, fact_reader=None):
        self.evidence_reader,self.fact_reader=evidence_reader,fact_reader
        normalized=[make_claim(c) for c in claims]
        self.claims={c['claim_id']:c for c in normalized}
        if not normalized or len(self.claims)!=len(normalized):
            raise ValueError('distinct claims required')
        notes=deepcopy({} if notes is None else notes)
        if not isinstance(notes,dict) or set(notes)-set(self.claims):
            raise ValueError('notes must bind existing claims')
        self.notes={}
        for cid,claim in self.claims.items():
            note=notes.get(cid,dict(conditions=[],scope_limits=[],attributions=[]))
            if not isinstance(note,dict) or set(note)!={'conditions','scope_limits','attributions'}:
                raise ValueError('notes require conditions/scope_limits/attributions')
            allowed=set(claim['supporting_evidence_ids']+claim['counter_evidence_ids'])
            all_ids=[]
            for kind in ('conditions','scope_limits','attributions'):
                if not isinstance(note[kind],list) or len(note[kind])>64:
                    raise ValueError('bounded note lists required')
                fields={'id','text'} if kind=='scope_limits' else ({'id','evidence_id','quote','description'} if kind=='conditions' else {'id','evidence_id','quote','speaker','stance'})
                for entry in note[kind]:
                    if not isinstance(entry,dict) or set(entry)!=fields or not all(text(v) for v in entry.values()):
                        raise ValueError('invalid recorded note')
                    if kind!='scope_limits' and entry['evidence_id'] not in allowed:
                        raise ValueError('note evidence outside claim')
                    if kind=='attributions' and entry['stance'] not in STANCES:
                        raise ValueError('unknown recorded stance')
                    all_ids.append(entry['id'])
            if len(set(all_ids))!=len(all_ids) or any(i.startswith('host:') for i in all_ids):
                raise ValueError('note IDs must be unique, without reserved host prefix')
            limits=claim['limitations']+['Semantic meaning and search completeness are not established by this output check.']
            note['scope_limits'] += [dict(id='host:'+str(i),text=s) for i,s in enumerate(dict.fromkeys(limits))]
            self.notes[cid]=note


def verify_output(document, context):
    """Check objective fields and recorded links, never all free prose meaning."""
    if not isinstance(context,OutputContext):
        raise ValueError('host OutputContext required; serialized labels are not capabilities')
    checks=[];records={};checked=[]
    def check(item,name,status,detail=''):
        checks.append(dict(item_id=item,check=name,status=status,detail=detail))
    def fresh(eid):
        try:
            return _evidence_record(_read_capability(context.evidence_reader,eid),eid)
        except (ValueError,TypeError,KeyError,AttributeError):
            return None
    def anchor(entry):
        e=records.get(entry['evidence_id'])
        return bool(e and verify_quote(entry['quote'],e['context']['text'])['direct_quote_allowed'])
    try:
        json_bytes(document)
        if not isinstance(document,dict) or set(document)!={'schema_version','items'} or document['schema_version']!=SCHEMA:
            raise ValueError('output schema_version/items required')
        items=document['items']
        if not isinstance(items,list) or not 1<=len(items)<=256:
            raise ValueError('1..256 output items required')
        seen=set()
        for item in items:
            if not isinstance(item,dict) or not all(text(item.get(k)) for k in BASE) or item['kind'] not in EXTRA or set(item)!=BASE|EXTRA[item['kind']]:
                raise ValueError('unknown/missing output fields or kind')
            if item['item_id'] in seen or item['claim_id'] not in context.claims:
                raise ValueError('duplicate item or unknown claim')
            seen.add(item['item_id'])
        selected={i['claim_id'] for i in items}
        for cid in sorted(selected):
            c=context.claims[cid]
            for eid in c['supporting_evidence_ids']+c['counter_evidence_ids']:
                if eid not in records:
                    records[eid]=fresh(eid)
                    check(None,'CURRENT_A:'+eid,'PASS' if records[eid] else 'UNVERIFIED')
                if records[eid] is not None:
                    check(None,'RUN_BINDING:'+eid,'PASS' if records[eid]['run_id'] in (None,c['run_id']) else 'FAIL')
            for entry in context.notes[cid]['conditions']+context.notes[cid]['attributions']:
                check(None,'NOTE_ANCHOR:'+entry['id'],'UNVERIFIED' if records.get(entry['evidence_id']) is None else ('PASS' if anchor(entry) else 'FAIL'))
        for item in items:
            start=len(checks);iid=item['item_id'];cid=item['claim_id'];kind=item['kind']
            c=context.claims[cid];notes=context.notes[cid];allowed=set(c['supporting_evidence_ids']+c['counter_evidence_ids'])
            rendered=deepcopy(item)
            if kind!='CONCLUSION':
                eid=item['evidence_id']
                if not text(eid) or eid not in allowed:
                    check(iid,'EVIDENCE_BINDING','FAIL');continue
                e=records[eid]
                if e is None:
                    check(iid,'CURRENT_SOURCE','UNVERIFIED');continue
                check(iid,'SOURCE_IDENTITY','PASS' if item['source']==source_identity(e) else 'FAIL')
                if kind=='QUOTE':
                    use=item['use']
                    if use not in ('TEXTUAL_QUOTE','SCRIPTURAL_TEACHING','METADATA_REPORT'):
                        check(iid,'QUOTE_USE','FAIL')
                    check(iid,'QUOTATION','PASS' if verify_quote(item['text'],e['context']['text'])['direct_quote_allowed'] else 'FAIL')
                    if use=='SCRIPTURAL_TEACHING':
                        primary=e['text_role'] in ('root_text','translation_main') and e['evidence_class'] in ('canonical_root','authoritative_structured')
                        check(iid,'TEXT_ROLE','PASS' if primary else 'FAIL')
                        attrs=[a for a in notes['attributions'] if a['evidence_id']==eid]
                        check(iid,'RECORDED_STANCE','UNVERIFIED' if not attrs else ('PASS' if all(a['stance']=='ENDORSED' for a in attrs) else 'FAIL'),
                              'Consistency with recorded AI annotation only; speaker/stance meaning is not proven.')
                else:
                    facts=_read_capability(context.fact_reader,dict(kind=kind,evidence=e))
                    valid=facts.get('source')==source_identity(e) and facts.get('kind')==kind
                    if not valid:
                        check(iid,kind+'_FACT_READER','UNVERIFIED')
                    elif kind=='TITLE':
                        actual=[unicodedata.normalize('NFC',v).strip() for v in facts.get('values',[]) if isinstance(v,str)]
                        check(iid,'TITLE_MATCH','PASS' if unicodedata.normalize('NFC',item['text']).strip() in actual else 'FAIL')
                        rendered['fact_provenance']=facts.get('provenance')
                    else:
                        values=facts.get('namespaces',{}).get(item['namespace'],[])
                        check(iid,'IDENTIFIER_NAMESPACE','PASS' if item['text'] in values else 'FAIL')
                        rendered['fact_provenance']=facts.get('provenance')
            else:
                eids=item['evidence_ids']
                if not ids(eids) or not eids or not set(eids)<=allowed:
                    check(iid,'CONCLUSION_EVIDENCE','FAIL');continue
                check(iid,'CONCLUSION_SOURCE','PASS' if all(records[eid] for eid in eids) else 'UNVERIFIED')
                conditions={n['id']:n for n in notes['conditions']};limits={n['id']:n for n in notes['scope_limits']}
                check(iid,'CONDITION_LINKS','PASS' if ids(item['condition_ids']) and set(item['condition_ids'])==set(conditions) and all(n['evidence_id'] in eids for n in conditions.values()) else 'FAIL')
                check(iid,'SCOPE_LINKS','PASS' if ids(item['scope_limit_ids']) and set(item['scope_limit_ids'])==set(limits) else 'FAIL')
                check(iid,'INTERPRETATION_LABEL','PASS' if item['label'] in ('AI_INTERPRETATION','UNRESOLVED') and item['scope'] in ('BOUNDED','UNRESOLVED') else 'FAIL')
                attrs=item['attributions'];expected=[{k:a[k] for k in ('id','speaker','stance')} for a in notes['attributions']]
                check(iid,'ATTRIBUTION_LINKS','PASS' if attrs==expected and all(a['evidence_id'] in eids for a in notes['attributions']) else 'FAIL',
                      'Recorded interpretation consistency, not semantic validation.')
                if any('DECLARED_SOURCE_UNRESOLVED' in s for s in c['limitations']):
                    check(iid,'BLOCKED_CLAIM','PASS' if item['label']=='UNRESOLVED' and item['scope']=='UNRESOLVED' else 'FAIL')
                rendered.update(conditions=deepcopy(list(conditions.values())),scope_limits=deepcopy(list(limits.values())),
                                provenance=[source_identity(records[eid]) for eid in eids if records[eid]],semantic_truth_verified=False)
            if all(x['status']=='PASS' for x in checks[start:]):
                checked.append(rendered)
        # A readable snapshot is still not a capability on later re-use.
        for eid,e in records.items():
            if e is not None and fresh(eid)!=e:
                check(None,'SOURCE_CHANGED:'+eid,'UNVERIFIED')
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError) as exc:
        check(None,'STRUCTURE','FAIL',str(exc))
    status='REJECTED' if any(x['status']=='FAIL' for x in checks) else ('UNVERIFIED' if any(x['status']=='UNVERIFIED' for x in checks) else 'CHECKED')
    return dict(schema_version=SCHEMA,status=status,checks=checks,checked_items=checked if status=='CHECKED' else [],
        recorded_context_sha256=hashlib.sha256(json_bytes(dict(claims=context.claims,notes=context.notes))).hexdigest(),
        semantic_truth_verified=False,academic_approval=False,publication_authorized=False,
        limitations=['Checks cover structured fields only, not arbitrary prose or missing/unrecognized semantic conditions.',
                    'Recorded speaker/stance/condition meanings remain AI interpretations; CHECKED is not A VERIFIED or B accepted.'])
