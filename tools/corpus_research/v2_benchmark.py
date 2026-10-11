"""Offline E1/E2/E3 measurements against an explicit historical 1.0 checkout.

Same immutable index, warm OS cache, one warm-up and repeated observations.
No cold-cache claim, network, source downloads, AI service or acceptance threshold.
Raw results are small JSON artifacts; databases remain outside version control.
"""
from __future__ import annotations
import argparse
import hashlib
import gzip
import io
import json
import os
from pathlib import Path
import platform
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
import unittest


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def git(root,*args):
    return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()


def resources():
    try:
        import resource
        own,children = resource.getrusage(resource.RUSAGE_SELF),resource.getrusage(resource.RUSAGE_CHILDREN)
        result = dict(cpu_self_seconds=own.ru_utime+own.ru_stime,cpu_children_seconds=children.ru_utime+children.ru_stime,
            max_rss_self_kib=own.ru_maxrss,max_rss_children_kib=children.ru_maxrss,
            input_blocks=own.ru_inblock+children.ru_inblock,output_blocks=own.ru_oublock+children.ru_oublock)
        if Path('/proc/self/io').exists():
            values = dict(line.split(': ') for line in Path('/proc/self/io').read_text().splitlines())
            result.update(io_read_bytes_self=int(values['read_bytes']),io_write_bytes_self=int(values['write_bytes']),
                          io_rchar_self=int(values['rchar']),io_wchar_self=int(values['wchar']))
        return result
    except ImportError:
        return {'resource_measurement':'CHƯA ĐO: resource module unavailable'}


def measure(call):
    before = resources()
    started = time.perf_counter()
    result = call()
    elapsed = time.perf_counter()-started
    after = resources()
    measured = {key:value if key.startswith('max_rss') or not isinstance(value,(float,int)) else value-before[key]
                for key,value in after.items()}
    return result,{'wall_seconds':elapsed,**measured}


def worker(config):
    from corpus_research import retrieval
    db,root = Path(config['db']),Path(config['root'])
    mode = config['mode']
    host = None
    if mode in ('quick','research'):
        from corpus_research.local_host import LocalHost
        host = LocalHost(root,db,source_root=config['source_root'])
    output = []
    for task in config['tasks']:
        def execute():
            if mode=='retrieval': return getattr(retrieval,task['operation'])(db,*task['args'],**task.get('kwargs',{}))
            if mode=='quick': return host.quick(*task['args'],**task.get('kwargs',{}))
            if mode=='golden':
                sys.path.insert(0,str(root/'tests'))
                suite = unittest.defaultTestLoader.discover(str(root/'tests'),pattern='test_golden_research.py')
                result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
                return dict(ran=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
                    independent_scholarly_review=False)
            from corpus_research.local_research import LocalResearch
            host.reset_metrics()
            with tempfile.TemporaryDirectory() as directory:
                research = LocalResearch(host,Path(directory)/'research.sqlite3')
                response = research.create(run_id='benchmark-run',**task['kwargs'])
                run = response['run']
                return dict(metrics=response['metrics'],evidence_count=len(run['evidence']),claim_count=len(run['claims']),
                    accepted_claim_count=len(run['accepted_claim_ids']),run_status=run['run_status'],
                    executed_counter_steps=sum(len(c['result'].get('search',{}).get('attempts',[])) for c in run['counterevidence']),
                    verified_counter_candidates=sum(len(c['result'].get('search',{}).get('verified_evidence',[])) for c in run['counterevidence']),
                    counterevidence_performed=run['counterevidence_performed'],publication_authorized=False,
                    limitations=run['limitations'],independent_expected_answer=False)
        execute()  # Warm-up, excluded from samples; OS cache is never flushed.
        samples,first = [],None
        for _ in range(config['repeats']):
            result,resource = measure(execute)
            if first is None: first=result
            comparable = result['retrieval'] if mode=='quick' else result
            samples.append({**resource,'result_sha256':digest(comparable),
                            **({'phases':result['metrics']} if mode in ('quick','research') else {})})
        output.append({'task':task,'result':first,'samples':samples})
    return output


def stats(samples):
    values = [s['wall_seconds'] for s in samples]
    return dict(n=len(values),median_seconds=statistics.median(values),min_seconds=min(values),max_seconds=max(values),
                median_cpu_seconds=statistics.median(s['cpu_self_seconds']+s['cpu_children_seconds'] for s in samples)
                    if all('cpu_self_seconds' in s and 'cpu_children_seconds' in s for s in samples) else None)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--worker',action='store_true')
    p.add_argument('--root',type=Path)
    p.add_argument('--legacy-root',type=Path)
    p.add_argument('--source-root',type=Path)
    p.add_argument('--db',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--repeats',type=int,default=7)
    args = p.parse_args(argv)
    if args.worker:
        print(json.dumps(worker(json.load(sys.stdin)),ensure_ascii=False)); return 0
    if not all((args.root,args.legacy_root,args.source_root,args.db,args.output)) or args.repeats<3:
        p.error('root, legacy-root, source-root, db, output and at least 3 repeats required')
    if platform.system()!='Linux': p.error('Resource units are implemented for Linux/WSL; do not invent measurements on other OSes.')
    legacy_commit = git(args.legacy_root,'rev-parse','HEAD')
    if subprocess.run(['git','-C',str(args.legacy_root),'cat-file','-e',legacy_commit+':tools/corpus_research/verification.py'],capture_output=True).returncode==0:
        p.error('legacy checkout must precede Phase A')
    if git(args.root,'rev-parse',legacy_commit+'^{commit}')!=legacy_commit: p.error('historical commit must exist in primary repository history')
    from corpus_research import retrieval
    row = retrieval.search(args.db,'sutaṃ',corpus='suttacentral-bilara',limit=1)['results'][0]
    tasks = [dict(name='pali',operation='search',args=['sutaṃ'],kwargs={'corpus':'suttacentral-bilara','limit':5}),
        dict(name='latin',operation='search',args=['impermanent'],kwargs={'limit':5}),
        dict(name='cjk',operation='search',args=['如是我聞'],kwargs={'corpus':'cbeta-tei','limit':5}),
        dict(name='identifier',operation='search',args=['mn1'],kwargs={'limit':5}),
        *[dict(name=op,operation=op,args=[row['id']]) for op in ('context','evidence','provenance')],
        *[dict(name=op,operation=op,args=[identifier]) for op,identifier in [('work','mn1'),('parallels','mn1'),('variants','T01n0001'),('resolve','ea9.7')]],
        dict(name='compare',operation='compare',args=[['mn1','T01n0001']])]
    quick_tasks = [dict(name=c,operation='search',args=[q],kwargs={'corpus':c,'limit':1}) for c,q in
                   [('suttacentral-bilara','sutaṃ'),('cbeta-tei','如是我聞'),('84000-tei','Thus')]]
    def run(root,mode,tasks):
        config = dict(root=str(root),source_root=str(args.source_root),db=str(args.db),mode=mode,tasks=tasks,repeats=args.repeats)
        env = dict(os.environ,PYTHONPATH=str(root/'tools'),PYTHONDONTWRITEBYTECODE='1')
        result = subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker'],input=json.dumps(config),
            capture_output=True,text=True,encoding='utf-8',env=env,check=True)
        return json.loads(result.stdout)
    raw = dict(legacy=run(args.legacy_root,'retrieval',tasks),current=run(args.root,'retrieval',tasks),
        quick_baseline=run(args.legacy_root,'retrieval',quick_tasks),quick=run(args.root,'quick',quick_tasks),
        research=run(args.root,'research',[dict(name='actual-pending-dossier',kwargs=dict(question='Nguồn ghim ghi gì tại các đoạn tìm được?',
            queries=['sutaṃ'],corpora=['suttacentral-bilara'],counter_queries=['anicca'],limit=1))]),
        golden=run(args.root,'golden',[dict(name='eleven-software-oracles')]))
    comparison = []
    for old,new in zip(raw['legacy'],raw['current']):
        equal = old['result']==new['result'] and all(s['result_sha256']==digest(old['result']) for s in old['samples']+new['samples'])
        comparison.append(dict(task=old['task']['name'],identical=equal,legacy=stats(old['samples']),current=stats(new['samples'])))
        if not equal: raise ValueError('1.0 output regression: '+old['task']['name'])
    quick_summary = []
    for old,new in zip(raw['quick_baseline'],raw['quick']):
        if old['result']!=new['result']['retrieval']: raise ValueError('Quick retrieval changed')
        old_stats,new_stats = stats(old['samples']),stats(new['samples'])
        quick_summary.append(dict(task=old['task']['name'],legacy=old_stats,quick=new_stats,
            overhead_seconds=new_stats['median_seconds']-old_stats['median_seconds'],
            ratio=new_stats['median_seconds']/old_stats['median_seconds'],
            verified_evidence_count=len(new['result']['verified_evidence']),
            median_phases={k:statistics.median(s['phases'][k] for s in new['samples']) for k in new['samples'][0]['phases']}))
    protected = ['manifest.json','config/corpus-sources.json','tools/corpus_research/retrieval.py','tools/corpus_research/index.py','tools/corpus_research/cli.py','tools/corpus_research/model.py']
    hashes = {path:dict(legacy=git(args.legacy_root,'rev-parse',legacy_commit+':'+path),current=git(args.root,'hash-object',str(args.root/path))) for path in protected}
    code = {str(p.relative_to(args.root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((args.root/'tools/corpus_research').glob('*.py'))}
    with sqlite3.connect('file:'+str(args.db)+'?mode=ro',uri=True) as con:
        con.row_factory=sqlite3.Row
        state=[dict(r) for r in con.execute('SELECT * FROM source_state ORDER BY corpus')]
        counts={t:con.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ('records','relations','variants','lemmas')}
    report = dict(schema='bcr-e-measurement-v1',legacy_commit=legacy_commit,candidate_commit=git(args.root,'rev-parse','HEAD'),
        candidate_worktree_status=git(args.root,'status','--porcelain'),code_sha256=code,protected_git_blob_hashes=hashes,
        environment=dict(python=sys.version,sqlite=sqlite3.sqlite_version,platform=platform.platform(),cpu=platform.processor(),
            index_sha256=hashlib.sha256(args.db.read_bytes()).hexdigest(),index_counts=counts,source_state=state,
            cache='warm OS cache, 1 warm-up per task; XML LRU warm; no cache flush; acceptance profile only',
            timing='worker execution only; process startup/host construction and index build excluded; source subprocess CPU included',
            memory='process high-water ru_maxrss KiB, not per-operation allocation; child high-water reported separately',
            io='getrusage blocks self+children; /proc/self/io bytes exclude child IO; cached IO zeros are observed values'),
        raw=raw,summary=dict(E1=comparison,E2=quick_summary,E3_research=stats(raw['research'][0]['samples']),
            E3_golden=stats(raw['golden'][0]['samples']),real_error_rate='CHƯA ĐO: no independent scholarly expected answers',
            independent_review='CHƯA THẨM ĐỊNH ĐỘC LẬP THỰC TẾ',ai_tokens='CHƯA ĐO: no AI service invoked',
            ai_cost='CHƯA ĐO: no AI service invoked',acceptance_threshold='CHỜ CHỐT NGƯỠNG'))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    opener = gzip.open if args.output.suffix=='.gz' else open
    with opener(args.output,'xt',encoding='utf-8') as handle: json.dump(report,handle,ensure_ascii=False,indent=2)
    print(json.dumps(report['summary'],ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__': raise SystemExit(main())
