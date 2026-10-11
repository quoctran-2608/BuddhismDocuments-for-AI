"""Separate v2 entry point. CLI 1.0 remains unchanged; no approval-file shortcut."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys

from .local_host import LocalHost
from .local_research import LocalResearch
from .research_run import safe_json


def parser():
    p = argparse.ArgumentParser(prog='buddhist-research',description='Offline source verification and pending-review Research dossiers.')
    root = Path(__file__).resolve().parents[2]
    p.add_argument('--root',type=Path,default=root)
    p.add_argument('--source-root',type=Path)
    p.add_argument('--db',type=Path,default=root/'derived/corpus.sqlite3')
    p.add_argument('--store',type=Path,default=root/'derived/research.sqlite3')
    sub = p.add_subparsers(dest='command',required=True)
    quick = sub.add_parser('quick',help='Retrieve a few hits and verify their pinned source spans; no research store.')
    quick.add_argument('query')
    quick.add_argument('--corpus')
    quick.add_argument('--language')
    quick.add_argument('--limit',type=int,default=3)
    quote = sub.add_parser('quote',help='Verify a direct quote at an indexed record location.')
    quote.add_argument('--record-id',type=int,required=True)
    quote.add_argument('--text',required=True)
    create = sub.add_parser('run-create',help='Create a Research draft, real A evidence, candidate claims and lexical C receipts.')
    create.add_argument('--run-id',required=True)
    create.add_argument('--question',required=True)
    create.add_argument('--query',action='append',required=True)
    create.add_argument('--corpus',action='append',required=True)
    create.add_argument('--counter-query',action='append')
    create.add_argument('--limit',type=int,default=3)
    for command in ('run-show','run-capture','run-finalize','publication-check','review-export','claim-add','claim-revise'):
        item = sub.add_parser(command)
        item.add_argument('--run-id',required=True)
        if command!='run-show':
            item.add_argument('--version',type=int,required=True)
        if command in ('claim-add','claim-revise'):
            item.add_argument('--input',type=Path,required=True)
        if command=='claim-revise':
            item.add_argument('--claim-id',required=True)
            item.add_argument('--reason',required=True)
            item.add_argument('--revision-evidence-id',action='append',required=True)
        if command=='review-export':
            item.add_argument('--question',action='append',required=True)
            item.add_argument('--output',type=Path,required=True)
    report = sub.add_parser('review-import',help='Import a PROPOSED report; no approval authority.')
    report.add_argument('--input',type=Path,required=True)
    decision = sub.add_parser('review-decision',help='Missing host semantic approval stays UNVERIFIED.')
    decision.add_argument('--report-id',required=True)
    decision.add_argument('--review-id',required=True)
    return p


def load(path):
    value = json.loads(path.read_text(encoding='utf-8'))
    safe_json(value)
    return value


def main(argv=None):
    # JSON output is UTF-8 on Windows pipes as well as native terminals.
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    args = parser().parse_args(argv)
    try:
        host = LocalHost(args.root,args.db,source_root=args.source_root)
        if args.command=='quick':
            result = host.quick(args.query,corpus=args.corpus,language=args.language,limit=args.limit)
        elif args.command=='quote':
            result = host.verify_record(args.record_id,quotation=args.text)
        else:
            research = LocalResearch(host,args.store)
            store = research.store
            if args.command=='run-create':
                result = research.create(run_id=args.run_id,question=args.question,queries=args.query,
                    corpora=args.corpus,limit=args.limit,counter_queries=args.counter_query)
            elif args.command=='run-show':
                result = store.get_run(args.run_id)
            elif args.command=='run-capture':
                result = research.capture(args.run_id,expected_version=args.version)
            elif args.command=='run-finalize':
                result = research.finalize(args.run_id,expected_version=args.version)
            elif args.command=='publication-check':
                result = research.publication_check(args.run_id,expected_version=args.version)
            elif args.command=='claim-add':
                result = store.append_claim(args.run_id,load(args.input),expected_version=args.version)
            elif args.command=='claim-revise':
                result = store.revise_claim(args.run_id,args.claim_id,load(args.input),reason=args.reason,
                    revision_evidence_ids=args.revision_evidence_id,expected_version=args.version)
            elif args.command=='review-export':
                exported = store.export_review(args.run_id,expected_version=args.version,review_questions=args.question)
                paths = [args.output.with_suffix('.json'),args.output.with_suffix('.md')]
                for path in paths:
                    research.check_output_path(path)
                    if path.exists():
                        raise ValueError('review export must use fresh output paths')
                paths[0].parent.mkdir(parents=True,exist_ok=True)
                with paths[0].open('x',encoding='utf-8') as handle:
                    json.dump(exported['json'],handle,ensure_ascii=False,indent=2)
                with paths[1].open('x',encoding='utf-8') as handle:
                    handle.write(exported['markdown'])
                result = {'package_id':exported['json']['package_id'],'json':str(paths[0]),'markdown':str(paths[1]),'publication_authorized':False}
            elif args.command=='review-import':
                result = store.import_review(load(args.input))
            elif args.command=='review-decision':
                result = store.record_review_decision(args.report_id,review_id=args.review_id)
        safe_json(result)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (ValueError,OSError,sqlite3.Error) as exc:
        print(json.dumps({'status':'UNVERIFIED','publication_authorized':False,'error':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
