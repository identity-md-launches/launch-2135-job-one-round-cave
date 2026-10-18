# Catalog Health

Catalog Health is a small offline, standard-library checker for finite dependency
catalog JSON. It reports whether the catalog is structurally usable before a
worker asks the resolver to select versions: package names, release labels, and
dependency strings must be non-empty strings, and every dependency must name a
package present in the catalog.

One command shows it working:

```sh
python3 -B line-4/tools/catalog-health/health.py demo
```

The demo uses an in-memory finite catalog and prints a JSON report with the
package/release counts and zero missing dependency targets. For a workspace
catalog, run `python3 -B line-4/tools/catalog-health/health.py catalog.json`.
The tool reads only the named file, does not install or download packages, and
exits 0 for a healthy catalog and 2 for invalid input.
