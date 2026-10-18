#!/usr/bin/env python3
"""Summarize a saved citation ledger against a stable local corpus."""
import argparse
import json
from pathlib import Path
import sys

import check_citations as bridge

ledger_tool = bridge.module('live_report_ledger', 'tools/citation-ledger/ledger.py')


def summarize(saved, checked):
    """Join checked results to validated anchor paths by citation ID."""
    ledger_tool.validate(saved)
    anchors = {entry['id']: entry['anchor']['path'] for entry in saved['entries']}
    entries = checked['entries']
    if len(entries) != len(anchors) or {entry['id'] for entry in entries} != set(anchors):
        raise ValueError('checked citation IDs do not match the saved ledger')
    rows = []
    for entry in entries:
        rows.append({'id': entry['id'], 'source': anchors[entry['id']],
                     'status': entry['result']['status'],
                     'needs_review': entry['needs_review']})
    return {'format': 'citation-review/v1',
            'source_verified': checked['source_verified'],
            'all_unchanged': checked['all_unchanged'],
            'entry_count': len(rows),
            'review_count': sum(row['needs_review'] for row in rows),
            'entries': rows}


def check(root, ledger_path):
    saved = ledger_tool.load(ledger_path)
    return summarize(saved, ledger_tool.check_live(Path(root), saved))


def demo():
    raw = (Path(__file__).resolve().parent / 'examples/zto.md').read_bytes()
    anchor = ledger_tool.anchor.capture_bytes(raw, 'zto.md', 3, 6)
    saved = {'format': ledger_tool.FORMAT,
             'entries': [{'id': 'zto', 'anchor': anchor}]}
    return {'unchanged': summarize(saved, ledger_tool.check_bytes(saved, {'zto.md': raw})),
            'relocated': summarize(saved, ledger_tool.check_bytes(
                saved, {'zto.md': b'# Reading copy\n\n' + raw}))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('demo')
    p = sub.add_parser('check')
    p.add_argument('root')
    p.add_argument('ledger')
    args = parser.parse_args(argv)
    try:
        report = demo() if args.command == 'demo' else check(args.root, args.ledger)
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 0 if args.command == 'demo' or report['all_unchanged'] else 1
    except (ledger_tool.engine.SearchError, OSError, ValueError, RecursionError) as error:
        print(json.dumps({'status': 'invalid', 'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
