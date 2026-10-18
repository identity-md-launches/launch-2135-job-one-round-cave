#!/usr/bin/env python3
"""Make a deterministic audit receipt from a verified storage witness."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'proof_receipt_storage_fields', HERE.parent / 'storage-fields/storage_fields.py'
)
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)
w = storage.w


def _canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode('ascii')


def _receipt_payload(result):
    """Keep only fields derived after cryptographic proof and layout validation."""
    return {
        'format': 'proof-receipt/1',
        'verified': True,
        'stateRoot': result['stateRoot'],
        'address': result['address'],
        'codeHash': result['codeHash'],
        'layoutSha256': result['layoutSha256'],
        'slots': [
            {
                'slot': row['slot'],
                'word': row['word'],
                'storageExists': row['storageExists'],
                'unusedBits': row['unusedBits'],
                'fields': [
                    {'name': field['name'], 'rawBits': field['rawBits'],
                     'valueDecimal': field['valueDecimal']}
                    for field in row['fields']
                ],
            }
            for row in result['slots']
        ],
    }


def make_receipt(bundle, state_root, address, layout):
    """Verify first, then summarize only authenticated state and decoded fields."""
    result = storage.verify(bundle, state_root, address, layout)
    payload = _receipt_payload(result)
    payload['receiptSha256'] = hashlib.sha256(_canonical(payload)).hexdigest()
    return payload


def _load_inputs(witness_path, layout_path):
    bundle = w.load_bundle(witness_path)
    layout = storage.load_layout(layout_path)
    return bundle, layout


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('demo', help='make a receipt from the historical real ZTO/IMD fixture')
    verify = sub.add_parser('verify')
    verify.add_argument('witness')
    verify.add_argument('layout')
    verify.add_argument('--state-root', required=True)
    verify.add_argument('--address', required=True)
    args = parser.parse_args(argv)
    try:
        demo = args.command == 'demo'
        bundle, layout = _load_inputs(
            HERE.parent / 'state-witness/examples/zto-pool-mainnet.json' if demo else args.witness,
            HERE.parent / 'storage-fields/pool-layout.json' if demo else args.layout,
        )
        receipt = make_receipt(
            bundle, w.DEMO_ROOT if demo else args.state_root,
            w.POOL_MANAGER if demo else args.address, layout,
        )
        if demo:
            receipt['demo'] = (
                'Real ZTO/IMD historical fixture at block 26212390; '
                'illustrative RPC-observed root, not an independently authenticated checkpoint.'
            )
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    except w.Invalid as error:
        print(json.dumps({'verified': False, 'error': str(error)}), file=sys.stderr)
        return 1
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        print(json.dumps({'verified': False, 'error': 'Unreadable or malformed input.'}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
