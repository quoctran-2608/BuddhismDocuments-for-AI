"""Source-specific, portable resolvers for pinned UTF-8 bytes (no I/O).

Ranges address the ORIGINAL source, never flattened/re-serialized XML/JSON.
Only a contiguous unescaped text span can be quoted by the existing A gate.
Markup-spanning quotations and unsupported formats fail closed. No semantic
support, relationship equivalence or reviewer approval is inferred here.
"""
from __future__ import annotations

from array import array
from bisect import bisect_left, bisect_right
from functools import lru_cache
import copy
import json
from pathlib import PurePosixPath
import re
from xml.parsers import expat

from .model import work_from_segment

SUPPORTED = ('suttacentral-bilara', 'cbeta-tei', '84000-tei')
SPAN_LIMITATION = 'Only the resolved contiguous source text is verified; markup/escaped text is not flattened.'


def contract_for(contract, corpus, path):
    selected = copy.deepcopy(contract)
    if corpus == 'suttacentral-bilara' and corpus in selected:
        kind = path.split('/')[0] if isinstance(path,str) else None
        if kind in ('translation','comment'):
            selected[corpus]['evidence_class'] = 'authoritative_structured'
    return selected


def _selected(units, selector):
    matches = [i for i, unit in enumerate(units) if unit['segment_id'] == selector['segment_id']
               and (selector.get('sequence_no') is None or unit['sequence_no'] == selector['sequence_no'])]
    if len(matches) != 1:
        raise ValueError('source location is missing or ambiguous')
    i = matches[0]
    unit = units[i]
    if selector.get('work_id') != unit['work_id']:
        raise ValueError('source work does not match locator')
    spans = unit['spans']
    if not spans:
        raise ValueError('no contiguous unescaped text at this source location')
    excerpt = max(spans, key=lambda span: span[1]-span[0])
    context = [min(unit['start'],units[max(0, i-1)]['start']),
               max(unit['end'],units[min(len(units)-1, i+1)]['end'])]
    return {'location': {key: unit[key] for key in ('work_id', 'segment_id', 'sequence_no',
            'language', 'text_role', 'witness')}, 'excerpt_range': list(excerpt),
            'context_range': context, 'evidence_class': unit['evidence_class'],
            'limitations': [SPAN_LIMITATION]}


def _bilara(content, path, selector):
    parts = PurePosixPath(path).parts
    if len(parts) < 3 or parts[0] not in ('root', 'translation', 'comment') or not path.endswith('.json'):
        raise ValueError('unsupported Bilara role/path')
    kind, language = parts[:2]
    witness = PurePosixPath(path).stem.rsplit('_', 1)[-1]
    if not witness.startswith(kind+'-'+language+'-'):
        raise ValueError('Bilara filename does not establish witness/language')
    # Parse offsets as well as values, reject duplicate keys and trailing data.
    decoder = json.JSONDecoder()
    if not isinstance(json.loads(content),dict):
        raise ValueError('Bilara must be a segment dictionary')
    pos = len(content)-len(content.lstrip())
    if content[pos:pos+1] != '{':
        raise ValueError('Bilara must be a segment dictionary')
    pos += 1
    entries, seen = [], set()
    while True:
        pos += len(content[pos:])-len(content[pos:].lstrip())
        if content[pos:pos+1] == '}':
            pos += 1
            break
        key, pos = decoder.raw_decode(content, pos)
        if not isinstance(key, str) or key in seen:
            raise ValueError('invalid or duplicate Bilara segment')
        seen.add(key)
        pos += len(content[pos:])-len(content[pos:].lstrip())
        if content[pos:pos+1] != ':':
            raise ValueError('invalid Bilara object')
        pos += 1
        pos += len(content[pos:])-len(content[pos:].lstrip())
        start = pos
        value, pos = decoder.raw_decode(content, pos)
        # JSON escape sequences and HTML need another range contract, not a
        # fake byte span. They remain unavailable for direct quotation.
        plain = isinstance(value, str) and content[start+1:pos-1] == value and not any(x in value for x in '<>&')
        entries.append((key, value, start, pos, [(start+1, pos-1)] if plain and value.strip() else []))
        pos += len(content[pos:])-len(content[pos:].lstrip())
        if content[pos:pos+1] == ',':
            pos += 1
        elif content[pos:pos+1] != '}':
            raise ValueError('invalid Bilara separator')
    if content[pos:].strip():
        raise ValueError('trailing Bilara data')
    role = {'root':'root_text', 'translation':'translation_main', 'comment':'translator_comment'}[kind]
    cls = 'canonical_root' if kind == 'root' else 'authoritative_structured'
    units = []
    if '..' in (selector.get('segment_id') or ''):
        nonempty = [entry for entry in entries if isinstance(entry[1], str) and entry[1].strip()]
        groups = [nonempty[i:i+50] for i in range(0, len(nonempty), 50)]
        for sequence, group in enumerate(groups):
            units.append(dict(work_id=work_from_segment(group[0][0]),
                segment_id=group[0][0]+'..'+group[-1][0], sequence_no=sequence,
                start=group[0][2], end=group[-1][3], spans=[span for entry in group for span in entry[4]]))
    else:
        for sequence, (segment, value, start, end, spans) in enumerate(entries):
            if isinstance(value, str) and value.strip():
                units.append(dict(work_id=work_from_segment(segment), segment_id=segment,
                    sequence_no=sequence, start=start, end=end, spans=spans))
    for unit in units:
        unit.update(language=language, text_role=role, witness=kind+':'+witness, evidence_class=cls)
    return _selected(units, selector)


@lru_cache(maxsize=4)
def _xml(content):
    """Offsets/ancestry from an XML parser, excluding entities and external I/O."""
    data = content.encode('utf-8')
    offsets = array('I', [0])
    for char in content:
        offsets.append(offsets[-1]+len(char.encode('utf-8')))
    at = lambda byte: bisect_left(offsets, byte)
    parser = expat.ParserCreate(namespace_separator='}')
    nodes, stack, runs = [], [], []
    def start(tag, attrs):
        index = len(nodes)
        nodes.append({'tag':tag.rsplit('}',1)[-1], 'attrs':attrs,
                      'start':at(parser.CurrentByteIndex), 'end':None, 'parents':tuple(stack)})
        stack.append(index)
    def end(tag):
        node = nodes[stack.pop()]
        index = at(parser.CurrentByteIndex)
        node['end'] = content.find('>',index)+1 if content[index:index+2] == '</' else index
    def chars(text):
        start = at(parser.CurrentByteIndex)
        # Expanded entities/CRLF do not have a direct original-byte span.
        if text.strip() and content[start:start+len(text)] == text:
            runs.append((start,start+len(text),tuple(stack)))
    def forbidden(*args):
        raise ValueError('DTD/entities are unsupported by the source resolver')
    parser.StartElementHandler, parser.EndElementHandler = start, end
    parser.CharacterDataHandler = chars
    parser.StartDoctypeDeclHandler = forbidden
    parser.EntityDeclHandler = forbidden
    parser.ExternalEntityRefHandler = forbidden
    parser.Parse(data,True)
    return nodes, runs


def _attr(node, name):
    return node['attrs'].get('http://www.w3.org/XML/1998/namespace}'+name)


@lru_cache(maxsize=4)
def _tei_units(content, path, corpus):
    nodes, runs = _xml(content)
    if not nodes or nodes[0]['tag'] != 'TEI':
        raise ValueError('not a TEI source')
    bodies = [i for i,n in enumerate(nodes) if n['tag'] == 'body']
    if len(bodies) != 1:
        raise ValueError('missing or ambiguous TEI body')
    body = bodies[0]
    units = []
    if corpus == 'cbeta-tei':
        work = _attr(nodes[0], 'id')
        if not work or work != PurePosixPath(path).stem:
            raise ValueError('CBETA source work/path conflict')
        lbs = [i for i,n in enumerate(nodes) if n['tag']=='lb' and body in n['parents']]
        starts = [nodes[i]['start'] for i in lbs]
        groups = [[] for _ in range(len(lbs)+1)]
        for start,end,parents in runs:
            if body in parents and not any(nodes[i]['tag'] in ('note','rdg') for i in parents):
                groups[bisect_right(starts,start)].append((start,end))
        for i, spans in enumerate(groups):
            if not spans:
                continue
            segment = work+':'+(nodes[lbs[i-1]]['attrs'].get('n','') if i else work+':head')
            if segment.endswith(':'):
                raise ValueError('CBETA line has no anchor')
            units.append(dict(work_id=work,segment_id=segment,sequence_no=len(units),
                start=nodes[lbs[i-1]]['start'] if i else nodes[body]['start'],
                end=starts[i] if i < len(lbs) else nodes[body]['end'],spans=spans,
                language='lzh',text_role='root_text',witness=PurePosixPath(path).parts[0],
                evidence_class='authoritative_structured'))
    else:
        idnos = [n for n in nodes if n['tag']=='idno' and any(nodes[p]['tag']=='publicationStmt' for p in n['parents'])]
        bibls = [n for n in nodes if n['tag']=='bibl' and any(nodes[p]['tag']=='sourceDesc' for p in n['parents'])]
        if len(idnos) != 1 or not _attr(idnos[0],'id') or len(bibls) != 1:
            raise ValueError('84000 work/witness metadata missing or ambiguous')
        work, witness = _attr(idnos[0],'id'), bibls[0]['attrs'].get('key')
        text_by_parent, notes_by_parent, nested_units = {}, {}, set()
        for a,b,parents in runs:
            if not any(nodes[p]['tag']=='note' for p in parents):
                for p in parents:
                    text_by_parent.setdefault(p,[]).append((a,b))
        for j,n in enumerate(nodes):
            if n['tag']=='note':
                for p in n['parents']:
                    notes_by_parent.setdefault(p,[]).append((j,n))
            if n['tag'] in ('p','l') and n['parents']:
                nested_units.add(n['parents'][-1])
        note_runs = {}
        for a,b,parents in runs:
            for p in parents:
                if nodes[p]['tag']=='note':
                    note_runs.setdefault(p,[]).append((a,b))
        current, sequence = work, 0
        for i,node in enumerate(nodes):
            if body not in node['parents']:
                continue
            if node['tag']=='milestone' and _attr(node,'id'):
                current = _attr(node,'id')
            if node['tag'] not in ('head','p','l') or i in nested_units:
                continue
            spans = text_by_parent.get(i,[])
            if not spans:
                continue
            segment = _attr(node,'id') or current
            common = dict(work_id=work,sequence_no=sequence,language='en',witness=witness,
                          evidence_class='authoritative_structured')
            units.append(dict(common,segment_id=segment,start=node['start'],end=node['end'],spans=spans,
                text_role='translation_heading' if node['tag']=='head' else 'translation_main'))
            notes = notes_by_parent.get(i,[])
            for number,(j,note) in enumerate(notes,1):
                units.append(dict(common,segment_id=_attr(note,'id') or f'{segment}:synthetic-note:{sequence}:{number}',
                    start=note['start'],end=note['end'],spans=note_runs.get(j,[]),
                    text_role='translation_note'))
            sequence += 1
    return units


def _tei(content,path,selector,corpus):
    result = _selected(_tei_units(content,path,corpus), selector)
    # Nested notes overlap their containing paragraph; include the complete
    # selected body unit even when a neighboring note ends earlier.
    result['context_range'][0] = min(result['context_range'][0],result['excerpt_range'][0])
    result['context_range'][1] = max(result['context_range'][1],result['excerpt_range'][1])
    return result


def resolve_source(content, corpus, path, selector):
    if not isinstance(content,str) or not content or len(content.encode('utf-8')) > 20_000_000:
        raise ValueError('source unavailable or beyond resolver size limit')
    if corpus == 'suttacentral-bilara':
        return _bilara(content,path,selector)
    if corpus in ('cbeta-tei','84000-tei'):
        return _tei(content,path,selector,corpus)
    raise ValueError('no trusted source-specific resolver for this corpus')
