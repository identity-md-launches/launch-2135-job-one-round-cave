"""Behavior and filesystem checks for review of independently supplied candidates."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('deletion_test_impl',
                                            Path(__file__).with_name('deletion_audit.py'))
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class DeletionTests(unittest.TestCase):
    def test_demo(self):
        report = audit.demo()
        self.assertEqual(report['respected_deletion']['status'], 'checked')
        self.assertEqual(report['accidental_restoration']['status'], 'review')

    def test_duplicate_reduction_not_total_removal(self):
        row = audit.audit_candidate('x', 'a\na\na\n', 'a\na\n', 'a\na\na\n', 'a\na\na\n')
        self.assertEqual(row['retained_lines'][0]['review_above_occurrences'], 2)
        self.assertEqual(row['retained_lines'][0]['candidate_occurrences'], 3)
        self.assertEqual(row['retained_lines'][0]['removed_by'], ['ours'])
        self.assertEqual(audit.audit_candidate('x', 'a\na\na\n', 'a\na\n',
                                             'a\na\na\n', 'a\na\n')['status'], 'checked')

    def test_either_side_and_strongest_reduction(self):
        row = audit.audit_candidate('x', 'a\na\n', 'a\n', '', 'a\n')
        self.assertEqual(row['retained_lines'][0]['removed_by'], ['ours', 'theirs'])
        self.assertEqual(row['retained_lines'][0]['review_above_occurrences'], 0)

    def test_replacement_flags_old_text(self):
        self.assertEqual(audit.audit_candidate('x', 'old\n', 'new\n', 'old\n',
                                             'old\nnew\n')['status'], 'review')

    def test_reordering_is_not_count_deletion(self):
        self.assertEqual(audit.audit_candidate('x', 'a\nb\n', 'b\na\n', 'a\nb\n',
                                             'a\nb\n')['status'], 'checked')

    def test_exact_newlines_and_unicode(self):
        for old, new in [('é\r\n', 'é\n'), ('é\n', 'é')]:
            self.assertEqual(audit.audit_candidate('x', old, new, old, old)['status'], 'review')
            self.assertEqual(audit.audit_candidate('x', old, new, old, new)['status'], 'checked')

    def test_missing_and_empty_differ(self):
        row = audit.audit_candidate('x', '', None, '', '')
        self.assertTrue(row['retained_deleted_file'])
        self.assertEqual(row['status'], 'review')
        self.assertEqual(audit.audit_candidate('x', '', None, '', None)['status'], 'checked')

    def test_no_base_no_deletion(self):
        self.assertEqual(audit.audit_candidate('x', None, 'a\n', None, 'a\n')['status'], 'checked')

    def test_candidate_missing_does_not_claim_additions_preserved(self):
        row = audit.audit_candidate('x', 'a\n', 'b\n', 'a\n', None)
        self.assertEqual(row['status'], 'checked')
        self.assertFalse(row['candidate_present'])
        self.assertIsNone(row['candidate_sha256'])

    def test_file_directory_collision_blocks_descendants(self):
        sources = [{'files': {'x': 'old\n'}, 'directories': set()},
                   {'files': {'x/child': 'new\n'}, 'directories': {'x'}},
                   {'files': {}, 'directories': set()},
                   {'files': {'x/child': 'new\n'}, 'directories': {'x'}}]
        report = audit.inspect(sources)
        self.assertEqual(report['counts']['blocked'], 2)
        self.assertTrue(report['needs_review'])

    def test_cli_real_files_immutable_and_manifests_bind_candidate(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as folder:
            paths = [Path(folder) / name for name in audit.SIDES]
            # Real inherited documentation, with independent removal and addition.
            text = Path('line-1/tools/threeway/README.md').read_text()
            removed = text.splitlines(keepends=True)[0]
            ours = text[len(removed):]
            theirs = text + '\nReview receipt retained.\n'
            candidate = ours + '\nReview receipt retained.\n'
            for path, content in zip(paths, (text, ours, theirs, candidate)):
                path.mkdir()
                (path / 'README.md').write_text(content)
            before = [(path / 'README.md').read_bytes() for path in paths]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(audit.main([str(path) for path in paths]), 0)
            report = json.loads(output.getvalue())
            self.assertFalse(report['needs_review'])
            self.assertEqual(before, [(path / 'README.md').read_bytes() for path in paths])
            (paths[3] / 'README.md').write_text(theirs)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(audit.main([str(path) for path in paths]), 1)
            changed = audit.from_directories(paths)
            self.assertNotEqual(report['inputs']['candidate'], changed['inputs']['candidate'])
            self.assertEqual(changed['files'][0]['retained_lines'][0]['removed_by'], ['ours'])

    def test_reject_symlink_no_partial_output(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as folder:
            root = Path(folder)
            (root / 'link').symlink_to('missing')
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(audit.main([str(root)] * 4), 2)
            self.assertEqual(stdout.getvalue(), '')
            self.assertIn('symlink', stderr.getvalue())

    def test_wrong_tree_count(self):
        with self.assertRaises(ValueError):
            audit.inspect([])
        with self.assertRaises(ValueError):
            audit.from_directories([])


if __name__ == '__main__':
    unittest.main()
