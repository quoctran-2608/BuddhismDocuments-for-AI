"""Small SOFTWARE fixtures, including real temporary Git blobs and SQLite.

These are not canonical texts, independent scholarly answers or real approvals.
"""
import json
from pathlib import Path
import shutil
import subprocess

from corpus_research.index import build_index

ROOT = Path(__file__).resolve().parents[1]
BLUE = 'The first fixture passage describes a blue lamp.'
RED = 'The second fixture passage describes a red lamp.'
BILARA_PATH = 'root/pli/ms/sutta/mn/mn1_root-pli-ms.json'


def git(root,*args):
    result = subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,check=True)
    return result.stdout.strip()


def commit(root):
    git(root,'init','-q')
    git(root,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','add','.')
    git(root,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Software fixture')
    return git(root,'rev-parse','HEAD')


def build_fixture(root):
    root = Path(root)
    selected = ('suttacentral-bilara','cbeta-tei','84000-tei')
    sources = [item for item in json.loads((ROOT/'config/corpus-sources.json').read_text())['sources'] if item['corpus'] in selected]
    manifest = []
    for source in sources:
        repo = root/source['repo']
        repo.mkdir(parents=True)
        if source['corpus']=='suttacentral-bilara':
            files = {
                BILARA_PATH:{'mn1:1.1':BLUE,'mn1:1.2':RED},
                'translation/en/sujato/sutta/mn/mn1_translation-en-sujato.json':{'mn1:1.1':BLUE,'mn1:1.2':RED},
                'comment/en/sujato/sutta/mn/mn1_comment-en-sujato.json':{'mn1:1.1':'A software translator comment, not root text.'},
                'variant/pli/ms/sutta/mn/mn1_variant-pli-ms.json':{'mn1:1.1':RED}}
            for path,data in files.items():
                target = repo/path
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        elif source['corpus']=='cbeta-tei':
            target = repo/'T/T01/T01n0001.xml'
            target.parent.mkdir(parents=True)
            target.write_text('<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="T01n0001"><text><body><p><lb n="0001a01"/>如是我聞，藍燈。<note>注釋假原文。</note><lb n="0001a02"/>紅燈。</p></body></text></TEI>',encoding='utf-8')
        else:
            for name,work in [('001-001_toh1-1_chapter_on_going_forth','UT22084-001-001'),('072-037_toh337_wheel_of_dharma','UT22084-072-037')]:
                target = repo/f'translations/kangyur/translations/{name}.xml'
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(f'<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader><fileDesc><publicationStmt><idno xml:id="{work}"/></publicationStmt><sourceDesc><bibl key="toh-fixture"/></sourceDesc></fileDesc></teiHeader><text><body><p xml:id="p1">{BLUE}<note xml:id="note1">The translator adds a fictional green lamp.</note></p><p xml:id="p2">{RED}</p></body></text></TEI>',encoding='utf-8')
        manifest.append({'rel_dest':source['repo'],'commit_sha':commit(repo)})
    (root/'config').mkdir()
    (root/'config/corpus-sources.json').write_text(json.dumps({'sources':sources}),encoding='utf-8')
    (root/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
    (root/'schema').mkdir()
    shutil.copyfile(ROOT/'schema/corpus-index.sql',root/'schema/corpus-index.sql')
    git(root,'init','-q')
    git(root,'add','config','manifest.json','schema')
    git(root,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Fixture host configuration')
    db = root/'derived/corpus.sqlite3'
    build_index(root,db,profile='acceptance',only_sources=list(selected),progress=False)
    return db
