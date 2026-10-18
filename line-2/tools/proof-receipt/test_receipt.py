import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('tested_proof_receipt', HERE / 'receipt.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.bundle = t.w.load_bundle(HERE.parent / 'state-witness/examples/zto-pool-mainnet.json')
        self.layout = t.storage.load_layout(HERE.parent / 'storage-fields/pool-layout.json')

    def make(self):
        return t.make_receipt(self.bundle, t.w.DEMO_ROOT, t.w.POOL_MANAGER, self.layout)

    def test_real_fixture_and_digest(self):
        receipt = self.make()
        self.assertTrue(receipt['verified'])
        self.assertEqual(receipt['format'], 'proof-receipt/1')
        self.assertEqual(receipt['slots'][0]['fields'][-1]['valueDecimal'], '12500')
        digest = receipt.pop('receiptSha256')
        self.assertEqual(digest, hashlib.sha256(t._canonical(receipt)).hexdigest())

    def test_digest_is_deterministic(self):
        self.assertEqual(self.make(), self.make())

    def test_wrong_root_fails_before_receipt(self):
        with self.assertRaises(t.w.Invalid):
            t.make_receipt(self.bundle, '0x' + '11' * 32, t.w.POOL_MANAGER, self.layout)

    def test_unverified_metadata_is_ignored(self):
        bundle = copy.deepcopy(self.bundle)
        bundle['block'] = {'stateRoot': 'forged', 'number': 'latest'}
        receipt = t.make_receipt(bundle, t.w.DEMO_ROOT, t.w.POOL_MANAGER, self.layout)
        self.assertNotIn('latest', json.dumps(receipt))
        self.assertEqual(receipt['stateRoot'], t.w.DEMO_ROOT)

    def test_input_objects_unchanged(self):
        before = (copy.deepcopy(self.bundle), copy.deepcopy(self.layout))
        self.make()
        self.assertEqual((self.bundle, self.layout), before)


if __name__ == '__main__':
    unittest.main()
