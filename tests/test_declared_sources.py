"""P0/1 software regressions. Fixture text is not scholarly ground truth."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from corpus_research.declared_sources import create_declared_run, search_expanded_sources, verify_declared_source
from corpus_research.local_host import LocalHost
from corpus_research.local_research import LocalResearch
from corpus_research.counterevidence import make_counterevidence_plan
from e_fixtures import BILARA_PATH, BLUE, ROOT, build_fixture


class DeclaredSourcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory()
        cls.root = Path(cls.fixture.name)
        cls.db = build_fixture(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.host = LocalHost(self.root, self.db)
        self.research = LocalResearch(self.host, Path(self.temp.name)/'research.sqlite3')
        self.ref = dict(corpus='suttacentral-bilara', work_id='mn1', source_path=BILARA_PATH,
                        source_sha=self.host.contract['suttacentral-bilara']['source_sha'],
                        witness='root:root-pli-ms', segment_id='mn1:1.1', quotation=BLUE)

    def verify(self, **changes):
        return verify_declared_source(self.host, {**self.ref, **changes}, claim_id='AC01')

    def create(self, refs=None, **changes):
        return create_declared_run(self.research, **dict(
            run_id='r-declared', question='Fixture question',
            claims=[dict(claim_id='AC01', text='Original claim; not a generated quotation.', claim_type='textual')],
            source_references={'AC01':refs or [self.ref]}, corpora=['suttacentral-bilara'], **changes))

    def test_exact_reference_preserves_provenance_without_search(self):
        with patch.object(self.host, 'retrieve', side_effect=AssertionError('lexical fallback')):
            result = self.verify()
        self.assertEqual(result['status'], 'VERIFIED')
        self.assertEqual(result['claim_id'], 'AC01')
        self.assertEqual(result['source_origin'], 'DECLARED')
        record = result['gate']['evidence']
        for field in ('corpus', 'work_id', 'source_path', 'source_sha', 'witness', 'segment_id'):
            self.assertEqual(record[field], self.ref[field])
        for field in ('repository', 'source_blob_sha', 'evidence_class', 'text_role', 'context'):
            self.assertTrue(record[field])
        self.assertFalse(result['publication_authorized'])

    def test_wrong_work(self):
        self.assertEqual(self.verify(work_id='mn2')['reason'], 'DECLARED_SOURCE_NOT_INDEXED')

    def test_wrong_path(self):
        self.assertEqual(self.verify(source_path='root/absent.json')['reason'], 'DECLARED_SOURCE_NOT_INDEXED')

    def test_wrong_sha(self):
        self.assertEqual(self.verify(source_sha='0'*40)['reason'], 'PIN_MISMATCH')

    def test_omitted_pin_uses_trusted_manifest_and_is_explicit_in_evidence(self):
        ref = {k:v for k,v in self.ref.items() if k != 'source_sha'}
        result = verify_declared_source(self.host, ref, claim_id='c')
        self.assertEqual(result['status'], 'VERIFIED')
        self.assertNotIn('source_sha', result['declared_reference'])
        self.assertEqual(result['gate']['evidence']['source_sha'], self.ref['source_sha'])

    def test_wrong_repository(self):
        self.assertEqual(self.verify(repository='other/repo')['reason'], 'REPOSITORY_MISMATCH')

    def test_wrong_witness(self):
        self.assertEqual(self.verify(witness='root:another')['reason'], 'WITNESS_MISMATCH')

    def test_wrong_segment(self):
        self.assertEqual(self.verify(segment_id='mn2:1.1')['status'], 'UNVERIFIED')

    def test_wrong_quotation(self):
        self.assertNotEqual(self.verify(quotation='Absent quotation')['status'], 'VERIFIED')

    def test_multiple_witnesses_require_disambiguation(self):
        result = verify_declared_source(self.host, dict(corpus='suttacentral-bilara', work_id='mn1'), claim_id='c')
        self.assertEqual(result['reason'], 'AMBIGUOUS_DECLARED_SOURCE')
        self.assertGreater(len(result['candidates']), 1)

    def test_witness_without_path_is_resolved_from_source(self):
        ref = {k:v for k,v in self.ref.items() if k != 'source_path'}
        result = verify_declared_source(self.host, ref, claim_id='c')
        self.assertEqual(result['status'], 'VERIFIED')
        self.assertEqual(result['gate']['evidence']['source_path'], BILARA_PATH)

    def test_missing_git_source_never_uses_index_wording(self):
        with patch('corpus_research.local_host.read_local_source', return_value={'error':'missing pinned object'}):
            result = self.verify()
        self.assertEqual(result['reason'], 'SOURCE_OR_SEGMENT_UNAVAILABLE')
        self.assertNotIn('gate', result)

    def test_bound_is_explicit(self):
        self.host.max_candidates = 1
        result = verify_declared_source(self.host, dict(corpus='suttacentral-bilara', work_id='mn1'), claim_id='c')
        self.assertEqual(result['reason'], 'CANDIDATE_BOUND_EXCEEDED')

    def test_invalid_or_unsupported_identity_rejected(self):
        for changes in ({'edition':'invented'}, {'source_path':'../escape'}, {'work_id':''}, {'witness':None}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.verify(**changes)

    def test_original_claim_kept_and_semantic_publication_closed(self):
        result = self.create()
        run = result['run']
        claim = run['claims'][0]
        self.assertEqual(claim['claim_id'], 'AC01')
        self.assertEqual(claim['text'], 'Original claim; not a generated quotation.')
        self.assertTrue(claim['supporting_evidence_ids'])
        self.assertFalse(run['accepted_claim_ids'])
        self.assertFalse(result['publication_authorized'])
        publication = self.research.publication_check(run['run_id'], expected_version=run['version'])
        self.assertFalse(publication['publication_authorized'])
        artifact = json.loads(Path(result['retrieval_artifact']).read_text())
        self.assertEqual(artifact['declared_bindings'], result['declared_bindings'])
        self.assertEqual(artifact['expanded_sources'], [])

    def test_one_failed_reference_does_not_allow_partial_substitution(self):
        result = self.create(refs=[self.ref, {**self.ref, 'work_id':'missing'}])
        self.assertEqual(result['run']['claims'][0]['supporting_evidence_ids'], [])
        self.assertTrue(any('UNRESOLVED' in s for s in result['run']['claims'][0]['limitations']))

    def test_reopened_declared_run_rechecks_real_source(self):
        result = self.create()
        run = result['run']
        reopened = LocalResearch(LocalHost(self.root,self.db),self.research.path)
        fresh = reopened.capture(run['run_id'],expected_version=run['version'])
        self.assertTrue(fresh['evidence'])
        with patch.object(reopened.host,'source_reader',return_value={}):
            missing = reopened.capture(run['run_id'],expected_version=fresh['version'])
        self.assertFalse(missing['evidence'])
        self.assertFalse(missing['accepted_claim_ids'])

    def test_claim_reference_association_must_be_exact(self):
        with self.assertRaises(ValueError):
            create_declared_run(self.research, run_id='r', question='q',
                claims=[dict(claim_id='c', text='t', claim_type='textual')],
                source_references={'wrong':[self.ref]}, corpora=['suttacentral-bilara'])

    def test_expanded_counter_search_does_not_replace_declared_binding(self):
        result = self.create(refs=[{**self.ref, 'work_id':'missing'}])
        run = result['run']; claim = run['claims'][0]
        plan = make_counterevidence_plan(claim, search_id='additional-search', scope=self.host.scope(['suttacentral-bilara']),
            steps=[dict(step_id='extra', direction='exception', operation='search', query='red lamp',
                        corpus='suttacentral-bilara', target_id=None)], unchecked_scope=['semantic review pending'])
        updated = self.research.capture(run['run_id'], expected_version=run['version'],
            counter_requests=[dict(claim_id='AC01', plan=plan, review_id=None)])
        self.assertTrue(updated['counterevidence'])
        self.assertEqual(updated['claims'][0]['supporting_evidence_ids'], [])
        self.assertFalse(updated['accepted_claim_ids'])

    def test_expanded_discovery_is_labeled_and_cannot_mutate_run(self):
        result = self.create(refs=[{**self.ref, 'work_id':'missing'}])
        before = self.research.store.get_run(result['run']['run_id'])
        expanded = search_expanded_sources(self.host, 'red lamp', claim_id='AC01', corpus='suttacentral-bilara', limit=1)
        self.assertEqual(expanded['source_origin'], 'EXPANDED')
        self.assertFalse(expanded['replaces_declared_source'])
        self.assertTrue(expanded['discovery']['verified_evidence'])
        self.assertEqual(before, self.research.store.get_run(before['run_id']))

    def test_verify_source_cli(self):
        input_path = Path(self.temp.name)/'source.json'
        input_path.write_text(json.dumps(self.ref))
        # Use the module entry point, preserving existing CLI exception/exit conventions.
        result = subprocess.run([sys.executable, '-m', 'corpus_research.v2_cli', '--root', str(self.root),
            '--db', str(self.db), 'verify-source', '--claim-id', 'AC01', '--input', str(input_path)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'VERIFIED')

    def test_claim_create_and_expanded_search_cli(self):
        input_path = Path(self.temp.name)/'claims.json'
        input_path.write_text(json.dumps(dict(
            claims=[dict(claim_id='AC01',text='Original fixture claim.',claim_type='textual')],
            source_references={'AC01':[self.ref]})))
        base = [sys.executable,'-m','corpus_research.v2_cli','--root',str(self.root),
                '--db',str(self.db),'--store',str(self.research.path)]
        created = subprocess.run(base+['claim-run-create','--run-id','cli-run','--question','q',
            '--corpus','suttacentral-bilara','--input',str(input_path)],capture_output=True,text=True)
        self.assertEqual(created.returncode,0,created.stderr)
        run = json.loads(created.stdout)['run']
        self.assertEqual(run['claims'][0]['text'],'Original fixture claim.')
        expanded = subprocess.run(base+['source-search','red lamp','--claim-id','AC01',
            '--corpus','suttacentral-bilara','--limit','1'],capture_output=True,text=True)
        self.assertEqual(expanded.returncode,0,expanded.stderr)
        self.assertEqual(json.loads(expanded.stdout)['source_origin'],'EXPANDED')


if __name__ == '__main__':
    unittest.main()
