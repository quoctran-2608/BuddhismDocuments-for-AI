import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from corpus_research.connector_host import ConnectorHost
from corpus_research.verification import git_blob_sha


class ConnectorContractTests(unittest.TestCase):
    def setUp(self):
        self.content = '{"mn1:1.1":"A software blue lamp."}'
        self.path = 'root/pli/ms/sutta/mn/mn1_root-pli-ms.json'
        self.mapping = {'suttacentral-bilara':dict(repository='fixture/bilara',repo_path='suttacentral/bilara-data',
            source_sha='1'*40,evidence_class='canonical_root',blob_check_required=True)}
        self.config = dict(repository='fixture/locator',root_path='remote/pointer-production-v1',mode='pointer_production_v1')
        self.pointer = dict(corpus='suttacentral-bilara',repository='fixture/bilara',source_sha='1'*40,source_path=self.path,
            source_blob_sha=git_blob_sha(self.content.encode()),work_id='mn1',segment_id='mn1:1.1',sequence_no=0,
            language='pli',text_role='root_text',witness='root:root-pli-ms',evidence_class='canonical_root')
        self.calls = []
        def fetch(request):
            self.calls.append(copy.deepcopy(request))
            return {**request,'content':self.content,'source_blob_sha':git_blob_sha(self.content.encode())}
        self.fetch = fetch

    def host(self,**kwargs):
        return ConnectorHost(self.mapping,self.config,locator_commit='2'*40,**kwargs)

    def test_missing_transport_keeps_pointer_unverified(self):
        result = self.host().verify_pointer({**self.pointer,'approved':True,'state':'VERIFIED'},evidence_id='ev-1')
        self.assertEqual(result['status'],'UNVERIFIED')
        self.assertIsNone(result['evidence'])

    def test_source_transport_contract_and_json_roundtrip(self):
        result = self.host(source_fetch=self.fetch).verify_pointer(json.loads(json.dumps(self.pointer)),evidence_id='ev-1')
        self.assertEqual(result['status'],'VERIFIED')
        self.assertEqual(result,json.loads(json.dumps(result)))
        self.assertEqual(len(self.calls),2)
        self.assertTrue(all(set(call)=={'repository','source_sha','source_path'} for call in self.calls))

    def test_production_pointer_missing_language_is_resolved_from_source(self):
        pointer = {k:v for k,v in self.pointer.items() if k!='language'}
        result = self.host(source_fetch=self.fetch).verify_pointer(pointer,evidence_id='ev-1')
        self.assertEqual(result['status'],'VERIFIED')
        self.assertEqual(result['evidence']['language'],'pli')
        self.assertNotIn('language',pointer)
        wrong = self.host(source_fetch=self.fetch).verify_pointer({**pointer,'language':'zh'},evidence_id='ev-2')
        self.assertEqual(wrong['status'],'REJECTED')

    def test_wrong_revision_blob_and_location_cannot_verify(self):
        for field,value in [('source_sha','3'*40),('source_blob_sha','4'*40),('segment_id','mn1:99'),('text_role','translator_comment')]:
            with self.subTest(field=field):
                pointer = {**self.pointer,field:value}
                self.assertNotEqual(self.host(source_fetch=self.fetch).verify_pointer(pointer,evidence_id='ev-1')['status'],'VERIFIED')

    def test_fetch_does_not_get_to_supply_fake_locations(self):
        def fetch(request):
            return {**self.fetch(request),'location':dict(segment_id='mn1:99'),
                    'excerpt_range':[0,len(self.content)],'approved':True}
        result = self.host(source_fetch=fetch).verify_pointer(self.pointer,evidence_id='ev-1')
        self.assertEqual(result['status'],'VERIFIED')
        self.assertEqual(result['evidence']['segment_id'],'mn1:1.1')

    def test_fetch_with_unbound_identity_or_missing_blob_is_unverified(self):
        for changes in [dict(repository='other/repo'),dict(source_sha='3'*40),dict(source_blob_sha=None)]:
            result = self.host(source_fetch=lambda request:{**self.fetch(request),**changes}).verify_pointer(self.pointer,evidence_id='ev-1')
            self.assertNotEqual(result['status'],'VERIFIED')

    def test_locator_uses_config_pin_bucket_and_exact_key(self):
        requests = []
        def locator(request):
            requests.append(request)
            return {**request,'content':json.dumps(dict(key='anicca',pointers=[self.pointer]))+'\n'}
        result = self.host(locator_fetch=locator).lookup('terms/latin','  ANICCA  ')
        self.assertEqual(result['status'],'CANDIDATE')
        self.assertEqual(requests[0],dict(repository='fixture/locator',source_sha='2'*40,
            source_path='remote/pointer-production-v1/locator/terms/latin/45/part-000001.jsonl'))

    def test_identifier_spelling_is_preserved(self):
        requests = []
        def locator(request):
            requests.append(request)
            return {**request,'content':json.dumps(dict(key='Dhp',pointers=[self.pointer]))}
        host = self.host(locator_fetch=locator)
        self.assertEqual(host.lookup('ids','Dhp')['status'],'CANDIDATE')
        self.assertEqual(host.lookup('ids','dhp')['status'],'UNVERIFIED')
        self.assertNotEqual(requests[0]['source_path'],requests[1]['source_path'])

    def test_cjk_and_missing_locator_fail_closed(self):
        self.assertEqual(self.host().lookup('terms/latin','如是我聞')['status'],'UNVERIFIED')
        self.assertEqual(self.host().lookup('ids','mn1')['status'],'UNVERIFIED')
        with self.assertRaises(ValueError): self.host().lookup('terms/cjk','如是我聞')

    def test_locator_duplicate_or_wrong_revision_does_not_route(self):
        row = json.dumps(dict(key='mn1',pointers=[self.pointer]))
        for changes in [dict(content=row+'\n'+row),dict(content=row,source_sha='3'*40)]:
            host = self.host(locator_fetch=lambda request:{**request,**changes})
            self.assertEqual(host.lookup('ids','mn1')['status'],'UNVERIFIED')

    def test_portable_adapter_import_and_gate_need_no_sqlite_or_shell(self):
        script = """
import builtins,json
original=builtins.__import__
def restricted(name,*args,**kwargs):
    if name.split('.')[0] in ('sqlite3','subprocess'):
        raise AssertionError('portable contract imported local I/O')
    return original(name,*args,**kwargs)
builtins.__import__=restricted
from corpus_research.connector_host import ConnectorHost
from corpus_research.verification import git_blob_sha
content='{"mn1:1.1":"A software blue lamp."}'
contract={'suttacentral-bilara':dict(repository='fixture/bilara',repo_path='suttacentral/bilara-data',source_sha='1'*40,evidence_class='canonical_root',blob_check_required=True)}
config=dict(repository='fixture/locator',root_path='remote/pointer-production-v1',mode='pointer_production_v1')
host=ConnectorHost(contract,config,locator_commit='2'*40,source_fetch=lambda req:{**req,'content':content,'source_blob_sha':git_blob_sha(content.encode())})
pointer=dict(corpus='suttacentral-bilara',repository='fixture/bilara',source_sha='1'*40,source_path='root/pli/ms/sutta/mn/mn1_root-pli-ms.json',work_id='mn1',segment_id='mn1:1.1',sequence_no=0,language='pli',text_role='root_text',witness='root:root-pli-ms',evidence_class='canonical_root')
result=host.verify_pointer(pointer,evidence_id='e-1')
assert result['status']=='VERIFIED'
assert json.loads(json.dumps(result))==result
"""
        env = {**os.environ,'PYTHONPATH':str(Path(__file__).resolve().parents[1]/'tools')}
        result = subprocess.run([sys.executable,'-c',script],env=env,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__':
    unittest.main()
