#!/usr/bin/env python3
"""Read-only deletion review of a supplied merge candidate, standard library only."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

SPEC = importlib.util.spec_from_file_location(
    'deletion_audit_tree', Path(__file__).resolve().parents[1] / 'tree-review' / 'tree_review.py')
tree = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tree)
SIDES = ('base', 'ours', 'theirs', 'candidate')
LIMITS = [
    'Exact per-file line counts only; a flag requests review, not automatic removal.',
    'Moves, renames, replacements and intentional reintroductions need human interpretation.',
    'No check of additions, remaining conflicts, syntax, meaning, or approval.',
    'File/directory collisions and descendants are blocked conservatively.',
    'Stable bounded UTF-8 trees required; no atomic snapshot or path race protection.',
    'No merge engine is run; only Tree Review snapshots and manifests are reused.']


def counts(text):
    return Counter((text or '').splitlines(keepends=True))


def audit_candidate(path, base, ours, theirs, candidate):
    """Find base-line count reductions from either side not reflected in candidate."""
    original, left, right, result = map(counts, (base, ours, theirs, candidate))
    retained = []
    for line, before in original.items():
        ceiling = min(before, left[line], right[line])
        if ceiling < before and result[line] > ceiling:
            retained.append({
                'line_sha256': hashlib.sha256(line.encode('utf-8')).hexdigest(),
                'base_occurrences': before,
                'branch_occurrences': {'ours': left[line], 'theirs': right[line]},
                'review_above_occurrences': ceiling,
                'candidate_occurrences': result[line],
                'removed_by': [side for side, inventory in (('ours', left), ('theirs', right))
                               if inventory[line] < before]})
    # Empty-file deletion needs a presence check: it has no line counts to inspect.
    deletion_requested = base is not None and (ours is None or theirs is None)
    retained_file = deletion_requested and candidate is not None
    return {'path': path, 'status': 'review' if retained or retained_file else 'checked',
            'candidate_present': candidate is not None,
            'candidate_sha256': None if candidate is None else
                hashlib.sha256(candidate.encode('utf-8')).hexdigest(),
            'retained_deleted_file': retained_file,
            'retained_lines': retained}


def inspect(sources):
    if len(sources) != 4:
        raise ValueError('exactly four trees required: base, ours, theirs, candidate')
    files = set().union(*(set(source['files']) for source in sources))
    directories = set().union(*(source['directories'] for source in sources))
    collisions = sorted(files & directories)
    rows = []
    for path in sorted(files):
        blocked = [p for p in collisions if path == p or path.startswith(p + '/')]
        if blocked:
            rows.append({'path': path, 'status': 'blocked', 'blocked_by': blocked})
        else:
            rows.append(audit_candidate(path, *(source['files'].get(path) for source in sources)))
    totals = {status: sum(row['status'] == status for row in rows)
              for status in ('checked', 'review', 'blocked')}
    return {'schema': 'deletion-audit/v1',
            'needs_review': bool(totals['review'] or totals['blocked']),
            'inputs': {side: tree.manifest(source) for side, source in zip(SIDES, sources)},
            'counts': totals, 'files': rows, 'limits': LIMITS}


def from_directories(paths):
    if len(paths) != 4:
        raise ValueError('exactly four directories required')
    budget = [0]
    return inspect([tree.snapshot(path, budget) for path in paths])


def demo():
    base = 'Check the source.\nOutdated instruction.\nKeep the receipt.\n'
    ours = base.replace('Outdated instruction.\n', '')
    theirs = base + 'Review both contributions.\n'
    candidate = ours + 'Review both contributions.\n'
    return {'respected_deletion': audit_candidate('guide.md', base, ours, theirs, candidate),
            'accidental_restoration': audit_candidate('guide.md', base, ours, theirs, theirs),
            'limits': LIMITS}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*', help='BASE_DIR OURS_DIR THEIRS_DIR CANDIDATE_DIR')
    parser.add_argument('--demo', action='store_true')
    args = parser.parse_args(argv)
    if (args.demo and args.paths) or (not args.demo and len(args.paths) != 4):
        parser.error('provide four directories or --demo')
    try:
        report = demo() if args.demo else from_directories(args.paths)
    except (OSError, UnicodeError, ValueError, RecursionError, OverflowError) as error:
        print('deletion-audit: ' + ascii(str(error)), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if args.demo:
        return 0 if (report['respected_deletion']['status'] == 'checked' and
                     report['accidental_restoration']['status'] == 'review') else 1
    return 1 if report['needs_review'] else 0


if __name__ == '__main__':
    sys.exit(main())
