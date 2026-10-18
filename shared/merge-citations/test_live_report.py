"""Check source paths and review status in the portable live handoff."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import live_report as report
import merge_ledger as merge


class LiveReportTests(unittest.TestCase):
    def setUp(self):
        self.raw = (Path(report.__file__).resolve().parent / 'examples/zto.md').read_bytes()
        self.saved = {'format': report.ledger_tool.FORMAT, 'entries': [
            {'id': 'zto', 'anchor': report.ledger_tool.anchor.capture_bytes(
                self.raw, 'zto.md', 3, 6)}]}

    def test_unchanged_and_relocated_keep_source(self):
        original = copy.deepcopy(self.saved)
        for raw, status, reviews in ((self.raw, 'unchanged', 0),
                                     (b'# Reading copy\n\n' + self.raw, 'relocated', 1)):
            checked = report.ledger_tool.check_bytes(self.saved, {'zto.md': raw})
            out = report.summarize(self.saved, checked)
            self.assertEqual(out['entries'][0]['source'], 'zto.md')
            self.assertEqual(out['entries'][0]['status'], status)
            self.assertEqual(out['review_count'], reviews)
            self.assertFalse(out['source_verified'])
        self.assertEqual(self.saved, original)

    def test_mismatched_checked_ids_fail_closed(self):
        checked = report.ledger_tool.check_bytes(self.saved, {'zto.md': self.raw})
        checked['entries'][0]['id'] = 'other'
        with self.assertRaisesRegex(ValueError, 'do not match'):
            report.summarize(self.saved, checked)

    def test_same_ledger_bridges_proposed_merge_and_live_queue(self):
        before = self.raw.decode('utf-8')
        ours = '# Reading copy\n\n' + before
        theirs = before + '\nReview before use.\n'
        sources = [{'files': {'zto.md': text}, 'directories': set()}
                   for text in (before, ours, theirs)]
        proposal = merge.inspect(sources, self.saved)
        self.assertEqual(proposal['status'], 'ready-for-review')
        candidate = ('# Reading copy\n\n' + theirs).encode('utf-8')
        live = report.summarize(self.saved, report.ledger_tool.check_bytes(
            self.saved, {'zto.md': candidate}))
        self.assertEqual(live['entries'][0]['source'], 'zto.md')
        self.assertEqual(live['entries'][0]['status'], 'relocated')
        self.assertEqual(live['review_count'], 1)

    def test_live_cli_and_exit_status(self):
        Path('test/scratch').mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir='test/scratch') as folder:
            root = Path(folder)
            docs = root / 'docs'
            docs.mkdir()
            source = docs / 'zto.md'
            source.write_bytes(self.raw)
            ledger = root / 'ledger.json'
            ledger.write_text(json.dumps(self.saved))
            command = [sys.executable, '-B', str(Path(report.__file__)),
                       'check', str(docs), str(ledger)]
            passed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertTrue(json.loads(passed.stdout)['source_verified'])
            source.write_bytes(b'# Reading copy\n\n' + self.raw)
            review = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(review.returncode, 1, review.stderr)
            self.assertEqual(json.loads(review.stdout)['entries'][0]['source'], 'zto.md')

    def test_portable_bundle_demo(self):
        Path('test/scratch').mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir='test/scratch') as folder:
            copied = Path(folder) / 'merge-citations'
            shutil.copytree(Path(report.__file__).resolve().parent, copied)
            run = subprocess.run([sys.executable, '-B', str(copied / 'live_report.py'),
                                  'demo'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)['relocated']['entries'][0]['source'],
                             'zto.md')


if __name__ == '__main__':
    unittest.main()
