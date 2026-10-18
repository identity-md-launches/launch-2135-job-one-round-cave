# Deletion Audit

Review a proposed text merge for base lines that a contributor removed but the
candidate still contains. This complements Addition Audit: a merge can preserve
all additions while accidentally restoring an obsolete instruction. Python 3.10+
and the standard library only. No network, installation or coin is needed.

From the repository root, see a respected deletion and an accidental restoration:

```sh
python3 -B line-1/tools/deletion-audit/deletion_audit.py --demo
```

When tried, this returned 0: `respected_deletion` was `checked` and
`accidental_restoration` was `review`, identifying the removed line by SHA-256.
The tool writes only JSON to stdout, never changes inputs and never executes
candidate code. It does not run the merger: supply the actual candidate you
intend to review, including a manually resolved candidate.

For real inputs, replace the four arguments with existing workspace directories:

```sh
python3 -B line-1/tools/deletion-audit/deletion_audit.py BASE_DIR OURS_DIR THEIRS_DIR CANDIDATE_DIR
```

Exit **0** means no deletion flag, **1** means review or blocked paths, **2**
means invalid input with no partial JSON on stdout. Zero is never merge approval.
Do not redirect stdout over an input or into one of the input directories.

For every exact base line (including its line ending), the review threshold is
the minimum of its base, ours and theirs occurrence counts. If either branch
reduced its count and the candidate exceeds that threshold, a `retained_lines`
entry records the line hash, all counts and which branches removed occurrences.
This handles repeated lines without requiring all copies to disappear. A file
deleted by either branch but present in the candidate is separately flagged as
`retained_deleted_file`, including when it was empty. Intentional retention after
a delete/modify conflict still needs review. New files have no base deletions.

The `deletion-audit/v1` report includes sorted file rows, counts, `needs_review`,
and four content manifests binding the supplied trees. A file/directory collision
or its descendants are `blocked`; no deletion inference is made there. Manifests
identify bytes, not author identity or approval. File text is not printed.

## Checks and limits

```sh
python3 -B line-1/tools/deletion-audit/test_deletion_audit.py
```

Thirteen tests passed, including repeated-line reductions, replacements, moves,
CRLF and missing-final-newline distinctions, Unicode, empty-file deletion,
path collisions, CLI statuses and symlink rejection. A real-file trial uses
the inherited Threeway README: one branch removes its first line and another
adds a review receipt. The supplied combined candidate passes; restoring the
removed heading returns 1. Reads leave all four trees byte-identical.

Copy this folder together with sibling `tree-review`, `merge-review`, and
`threeway`. Only Tree Review's bounded snapshots and manifests are called.
Each tree allows 128 files, 256 directories and 16 levels. Each file is at most
1 MiB / 4,000 lines; the **four** trees together have an 8 MiB budget. UTF-8
without NUL is required. Symlinks, special files, parent traversal and inputs
outside the current workspace are rejected. Inherited budget error text says
“three trees”; the shared budget actually covers all four here.

Reads require stable trusted trees; there is no atomic filesystem snapshot or
defense against path replacement during reading. Per-file exact counts do not
track line identity or position, renames, cross-file moves or meaning. A moved,
edited or intentionally reintroduced line can require review. Deletions from
different identical occurrences are ambiguous. No additions, syntax, conflict
markers, semantic correctness or author approval are checked. Pair with the
other merge review tools and human review; never automatically delete flagged
text. No signing, sending, payment or application operation is provided.
