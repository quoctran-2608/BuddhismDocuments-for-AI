"""Narrow E regressions: real temporary Git/index, invented text only."""
from contextlib import closing
import copy
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from corpus_research.connector_host import ConnectorHost
from corpus_research.index import build_index
from corpus_research.local_host import LocalHost
from corpus_research.source_resolvers import resolve_source
from corpus_research.verification import git_blob_sha
from e_fixtures import BILARA_PATH, ROOT, build_fixture, commit


class SourceSpanSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        build_fixture(cls.root)
        long_text = 'A much longer fictional passage which contains no requested keyword.'
        cls.short = {'suttacentral-bilara':'Needle.', '84000-tei':'Needle.', 'cbeta-tei':'短針。'}
        bilara = cls.root/'suttacentral/bilara-data'/BILARA_PATH
        bilara.write_text(json.dumps({'mn1:1.1':long_text,'mn1:1.2':'Needle.'}),encoding='utf-8')
        # Resolve repository paths from configuration, rather than assuming a layout.
        sources = json.loads((cls.root/'config/corpus-sources.json').read_text())['sources']
        repos = {s['corpus']:cls.root/s['repo'] for s in sources}
        cbeta = repos['cbeta-tei']/'T/T01/T01n0001.xml'
        cbeta.write_text('<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="T01n0001"><text><body><p><lb n="0001a01"/>這是一段很長的虛構文字，沒有要搜尋的詞。<hi>短針。</hi><note>僅注。</note><lb n="0001a02"/>另一行。</p></body></text></TEI>',encoding='utf-8')
        tei = repos['84000-tei']/'translations/kangyur/translations/001-001_toh1-1_chapter_on_going_forth.xml'
        tei.write_text('<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader><fileDesc><publicationStmt><idno xml:id="UT22084-001-001"/></publicationStmt><sourceDesc><bibl key="toh-fixture"/></sourceDesc></fileDesc></teiHeader><text><body><p xml:id="p1">'+long_text+'<hi>Needle.</hi><note xml:id="n1">NoteOnly.</note></p><p xml:id="p2">Another unit.</p></body></text></TEI>',encoding='utf-8')
        pins = [{'rel_dest':s['repo'],'commit_sha':commit(repos[s['corpus']])} for s in sources]
        (cls.root/'manifest.json').write_text(json.dumps(pins),encoding='utf-8')
        cls.db = cls.root/'derived/spans.sqlite3'
        cls.chunk_db = cls.root/'derived/chunks.sqlite3'
        build_index(cls.root,cls.db,profile='acceptance',only_sources=list(repos),progress=False)
        build_index(cls.root,cls.chunk_db,profile='core',only_sources=['suttacentral-bilara'],progress=False)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def host_row(self, corpus):
        db = self.chunk_db if corpus=='suttacentral-bilara' else self.db
        host = LocalHost(self.root,db)
        segment = {'suttacentral-bilara':'mn1:1.1..mn1:1.2','cbeta-tei':'T01n0001:0001a01','84000-tei':'p1'}[corpus]
        with closing(sqlite3.connect(db)) as con:
            con.row_factory = sqlite3.Row
            row = dict(con.execute('SELECT * FROM records WHERE corpus=? AND segment_id=? ORDER BY id LIMIT 1',(corpus,segment)).fetchone())
        return host,row

    def test_quick_selects_short_matching_span_in_each_format(self):
        for corpus,quote in self.short.items():
            with self.subTest(corpus=corpus):
                host,row = self.host_row(corpus)
                result = host.quick(quote.rstrip('.。'),corpus=corpus,limit=1)
                self.assertEqual(result['retrieval']['results'][0]['id'],row['id'])
                self.assertEqual(result['verification'][0]['status'],'VERIFIED')
                self.assertEqual(result['verified_evidence'][0]['quotation'],quote)
                self.assertEqual(host.metrics['source_reads'],2)

    def test_quote_cli_accepts_exact_short_span_in_each_format(self):
        import os
        env = {**os.environ,'PYTHONPATH':str(ROOT/'tools'),'PYTHONIOENCODING':'utf-8'}
        for corpus,quote in self.short.items():
            with self.subTest(corpus=corpus):
                host,row = self.host_row(corpus)
                output = subprocess.run([sys.executable,'-m','corpus_research.v2_cli','--root',str(self.root),
                    '--db',str(host.db),'quote','--record-id',str(row['id']),'--text',quote],
                    env=env,capture_output=True,text=True,encoding='utf-8',check=True)
                checked = json.loads(output.stdout)
                self.assertEqual(checked['status'],'VERIFIED')
                self.assertEqual(checked['quote']['status'],'VERIFIED_EXACT')

    def test_evidence_reread_keeps_short_span_binding(self):
        for corpus,quote in self.short.items():
            with self.subTest(corpus=corpus):
                host,row = self.host_row(corpus)
                result = host.verify_record(row['id'],quotation=quote)
                self.assertEqual(result['status'],'VERIFIED')
                reread = host.evidence_reader(result['evidence']['evidence_id'])
                self.assertEqual(reread['status'],'VERIFIED')
                self.assertEqual(reread['evidence'],result['evidence'])

    def test_connector_resolves_short_span_from_bound_source_twice(self):
        for corpus,quote in self.short.items():
            with self.subTest(corpus=corpus):
                local,row = self.host_row(corpus)
                pointer = local.pointer(row)
                calls = []
                def fetch(request):
                    calls.append(copy.deepcopy(request))
                    content = subprocess.check_output(['git','-C',str(self.root/local.contract[corpus]['repo_path']),
                        'show',request['source_sha']+':'+request['source_path']]).decode('utf-8')
                    return {**request,'content':content,'source_blob_sha':git_blob_sha(content.encode('utf-8')),
                            'excerpt_range':[0,len(content)],'location':{'segment_id':'forged'}}
                host = ConnectorHost(local.contract,dict(repository='fixture/locator',root_path='locator',
                    mode='pointer_production_v1'),locator_commit='2'*40,source_fetch=fetch)
                result = host.verify_pointer(pointer,evidence_id='short-span',quotation=quote)
                self.assertEqual(result['status'],'VERIFIED')
                self.assertEqual(result['evidence']['quotation'],quote)
                self.assertEqual(len(calls),2)

    def test_wrong_unit_cannot_verify_a_short_quote_from_another_unit(self):
        for corpus,quote in self.short.items():
            with self.subTest(corpus=corpus):
                host,row = self.host_row(corpus)
                pointer = host.pointer(row)
                pointer['segment_id'] = {'suttacentral-bilara':'mn1:1.1','cbeta-tei':'T01n0001:0001a02','84000-tei':'p2'}[corpus]
                pointer['sequence_no'] = 0 if corpus=='suttacentral-bilara' else 1
                checked = host.verify_pointer(pointer,quotation=quote)
                self.assertNotEqual(checked['status'],'VERIFIED')
                self.assertIsNone(checked['evidence'])

    def test_missing_location_does_not_allow_searching_the_entire_source(self):
        for corpus,quote in self.short.items():
            host,row = self.host_row(corpus)
            for key in ('work_id','segment_id','sequence_no'):
                with self.subTest(corpus=corpus,key=key):
                    pointer = host.pointer(row)
                    pointer.pop(key)
                    checked = host.verify_pointer(pointer,quotation=quote)
                    self.assertNotEqual(checked['status'],'VERIFIED')
                    self.assertIsNone(checked['evidence'])

    def test_short_quote_does_not_override_wrong_pin_or_blob(self):
        for key in ('source_sha','source_blob_sha'):
            host,row = self.host_row('84000-tei')
            pointer = {**host.pointer(row),key:'0'*40}
            checked = host.verify_pointer(pointer,quotation='Needle.')
            self.assertNotEqual(checked['status'],'VERIFIED')
            self.assertIsNone(checked['evidence'])

    def test_supplied_offsets_are_ignored_for_short_span(self):
        for corpus,quote in self.short.items():
            with self.subTest(corpus=corpus):
                host,row = self.host_row(corpus)
                pointer = {**host.pointer(row),'excerpt_range':[0,999999],
                           'context_range':[0,999999],'spans':[[0,999999]]}
                checked = host.verify_pointer(pointer,quotation=quote)
                self.assertEqual(checked['status'],'VERIFIED')
                self.assertEqual(checked['evidence']['context']['text'],quote)

    def test_quote_cannot_join_markup_or_bilara_entries(self):
        for corpus in self.short:
            with self.subTest(corpus=corpus):
                host,row = self.host_row(corpus)
                prefix = '這是一段很長的虛構文字，沒有要搜尋的詞。' if corpus=='cbeta-tei' else 'A much longer fictional passage which contains no requested keyword.'
                checked = host.verify_record(row['id'],quotation=prefix+self.short[corpus])
                self.assertEqual(checked['status'],'REJECTED')
                self.assertEqual(checked['quote']['status'],'QUOTE_MISMATCH')

    def test_query_from_note_or_different_unit_keeps_hit_unverified(self):
        for corpus,query in [('84000-tei','NoteOnly'),('84000-tei','Another unit'),('cbeta-tei','僅注')]:
            with self.subTest(corpus=corpus,query=query):
                host,row = self.host_row(corpus)
                checked = host.verify_pointer(host.pointer(row),retrieval_query=query)
                self.assertNotEqual(checked['status'],'VERIFIED')
                self.assertIsNone(checked['evidence'])

    def test_query_across_spans_keeps_1_0_hit_but_has_no_verified_quote(self):
        host,row = self.host_row('84000-tei')
        result = host.quick('keyword. Needle',corpus='84000-tei',limit=1)
        self.assertEqual(result['retrieval']['results'][0]['id'],row['id'])
        self.assertEqual(result['verified_evidence'],[])
        self.assertEqual(result['verification'][0]['status'],'UNVERIFIED')

    def test_normalized_query_selects_source_text_without_changing_quote(self):
        host,_ = self.host_row('84000-tei')
        result = host.quick('NEEDLE',corpus='84000-tei',limit=1)
        self.assertEqual(result['verified_evidence'][0]['quotation'],'Needle.')
        self.assertEqual(result['verified_evidence'][0]['quote_verification_status'],'VERIFIED_EXACT')

    def test_quote_word_boundary_remains_enforced_in_short_span(self):
        host,row = self.host_row('84000-tei')
        checked = host.verify_record(row['id'],quotation='Need')
        self.assertEqual(checked['status'],'REJECTED')
        self.assertEqual(checked['quote']['status'],'QUOTE_MISMATCH')

    def test_folded_query_selects_short_span_but_does_not_normalize_quote(self):
        content = json.dumps({'mn1:1.1':'Much longer unrelated fictional text.','mn1:1.2':'Evaṁ.'},ensure_ascii=False)
        selector = dict(work_id='mn1',segment_id='mn1:1.1..mn1:1.2',sequence_no=0)
        selected = resolve_source(content,'suttacentral-bilara',BILARA_PATH,selector,retrieval_query='evam')
        a,b = selected['excerpt_range']
        self.assertEqual(content[a:b],'Evaṁ.')
        # A's direct quote rules do not permit retrieval's diacritic folding.
        mismatch = resolve_source(content,'suttacentral-bilara',BILARA_PATH,selector,quotation='Evam.')
        a,b = mismatch['excerpt_range']
        self.assertNotEqual(content[a:b],'Evam.')

    def test_default_without_selection_hint_preserves_longest_span(self):
        host,row = self.host_row('84000-tei')
        checked = host.verify_record(row['id'])
        self.assertEqual(checked['status'],'VERIFIED')
        self.assertEqual(checked['evidence']['quotation'],'A much longer fictional passage which contains no requested keyword.')

    def test_independent_read_must_resolve_the_same_short_span(self):
        host,row = self.host_row('84000-tei')
        original = host.source_reader
        calls = []
        def inconsistent(request,**selection):
            calls.append(request)
            # Same pinned bytes/location but a different independently selected
            # range must fail A, even though the first quote matches exactly.
            return original(request,**selection) if len(calls)==1 else original(request)
        with patch.object(host,'source_reader',side_effect=inconsistent):
            checked = host.verify_record(row['id'],quotation='Needle.')
        self.assertEqual(checked['status'],'REJECTED')
        self.assertEqual(checked['checks']['independent_excerpt_range']['status'],'FAIL')
        self.assertIsNone(checked['evidence'])


if __name__=='__main__':
    unittest.main()
