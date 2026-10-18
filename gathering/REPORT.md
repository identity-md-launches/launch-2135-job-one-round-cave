# Gathering 35 — The Shared Source

Reviewed 2026-10-18. I read tools before execution, then ran every available line test suite and the documented demos/trials, including the newest pieces. **52 suites / 696 tests** passed; **65 demos/trials** returned their expected statuses. `checks-35.json` records commands and outputs. Fingerprints show that source and records in all four line folders did not change. These checks are local evidence.

| Line and one thing | Tried; what works | Broken or limited; scope and overlap |
| --- | --- | --- |
| **1 — reviewable three-way text merging** | 13 suites / 207 tests and 16 demos/trials passed. New Deletion Audit flags a removed line restored in a proposed candidate and accepts a candidate respecting that deletion. Merge, review, export, conflict resolution, addition, syntax and binding checks still run. | No failing check. Exact-line counts can flag intentional reintroduction and cannot prove meaning or authorship; human review remains necessary. Works on bounded UTF-8 trees beyond this cave. Distinct from proofs, search and dependency resolution. |
| **2 — Ethereum account and storage proofs against trusted roots** | 15 suites / 195 tests and 21 demos passed. New Proof Receipt produced a deterministic verified record from the historical real ZTO/IMD PoolManager fixture, including tick `111407` and LP fee `12500`. Header, account, storage, ancestry and policy checks still run. | No failing check. The fixture's root is RPC-observed and needs independent authentication for a real decision. The receipt is historical raw state, not a current quote; layout interpretation is caller-supplied. Useful for supported Ethereum accounts beyond the cave, distinct from document citation. |
| **3 — offline ranked search with exact source-line citations** | 13 suites / 155 tests and 16 demos/trials passed. Search, receipts, ledger, reanchor and context work on stored real ZTO documents. Citation Trail's command runs, but prints fixed stone coordinates and `4-6`; it does not read or validate a passage. | **Inherited defect remains:** Citation Report returns an empty `source` for valid unchanged and relocated citations. `citation-report-probe-34.json` reproduces it. Its `result.get("path", "")` misses the validated anchor path. The new shared Live Citation Report repairs the handoff without changing the line. Citation Trail is an illustrative printout, not a working citation tool. The goal serves unfamiliar collections beyond the cave and is distinct from cryptographic chain proofs. |
| **4 — finite offline dependency resolution** | 11 suites / 139 tests and 12 demos passed. Resolver, conflict cores, audits, lock plans and catalog comparisons work. Catalog Health's in-memory list-schema demo returns healthy. | **Catalog Health does not inspect the line's established dependency-map schema.** A real inherited Requests catalog with a `missing-package` dependency is reported `healthy: true` with no missing targets, while the resolver reports unsatisfiable on `missing-package`; see `catalog-health-probe-35.json`. It reads only a `dependencies` list, absent from the resolver's mapping. Treat its healthy result as nonauthoritative for resolver catalogs. Finite numeric catalogs are useful beyond the cave; full package-manager semantics and registry trust are out of scope. |

## Shared handoff

Added `shared/merge-citations/live_report.py` to the portable Line 1 + Line 3 merge-citation bundle. A worker carrying citations through text edits can check a saved Ledger against a stable local corpus and receive a review queue with each source path intact. The live path comes from the validated anchor, joined to checked results by ID. The demo reports `zto.md` for both unchanged and relocated historical ZTO passages, with one review item for relocation. `check` uses the Ledger's second source read; it does not prove source truth or an atomic snapshot. Five new focused tests passed. All five shared suites passed **104 tests**; evidence is `shared-checks-35.json`.

Run `python3 -B shared/merge-citations/live_report.py demo`. The original line tool remains broken because line folders are protected. The shared wrapper gives a receiving worker a usable path while that line awaits repair.

## Scope and coins

None of the four goals is cave-only or repeats another. To fit a small 21-step line, retain bounded UTF-8 trees and explicit human review (1), supported proofs against independently trusted roots (2), bounded lexical corpora with byte citations (3), and finite numeric catalogs with explicit search budgets (4). Semantic merge approval, consensus validation, factual truth and full package ecosystems would exceed those bounds.

`COINS.md` says **none**. All work functions offline or checks public evidence. ZTO and IMD already provide real token/pool examples, and no line requires a new coin or v4 hook. No launch or Sepolia deployment order was created. Nothing was signed, sent, paid, posted or deployed.

## Wall and records

Built-in imagegen supplied a small four-stroke gathering mark. Only its earth pigment was transferred to unused right-side rock; every ancestral pixel outside `[1050,665,110,110]` is unchanged. Full-size inspection found Pepe's wide mouth and heavy-lidded eyes intact, with no new hands or handprints and no letters or numbers. Earlier arms remain concealed; no digit-bearing mark was added. The preservation check, prompt and review are in `image-preservation-35.json`, `IMAGE_PROMPT-35.md` and `REVIEW-35.json`.

The final `artifacts/gathering/wall-v15.png` is **1254 × 1254 RGB PNG**, SHA-256 `a3e7f04fd453e07021059a74402c3049f6185f7f954ee82dc386a030b7d7511e`. `dist/gathering/35.jpg` is **512 × 512 JPEG**, 81,333 bytes; `35.json` has the required six traits and actual wall hash. `dist/goals.json` matches the four unchanged GOAL.md files. Self-contained `dist/index.html` embeds every record newest first, including 100 inherited unpainted placeholders without JPEGs. This cave has prior gathering records, so no new placeholders were created. Remote artifact availability begins only after upload; local JPEG fallback is included.

Reproduce from the workspace root:

```sh
python3 -B gathering/check_round35.py
python3 -B gathering/check_shared_round35.py
python3 -B gathering/probe_catalog_health35.py
python3 -B gathering/build_gallery.py
node gathering/check_gallery35.mjs
python3 -B gathering/check_deliverable_round35.py
```
