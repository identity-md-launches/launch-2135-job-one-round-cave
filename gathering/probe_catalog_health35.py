"""Show whether Catalog Health audits the line's established catalog schema."""
import importlib.util
import json
from pathlib import Path


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    sample = json.loads(Path('shared/catalog-evidence/examples/before.json').read_text())
    sample['packages']['requests']['2.32.5']['missing-package'] = '>=1'
    health = load('catalog_health_probe', 'line-4/tools/catalog-health/health.py')
    resolver = load('resolver_probe', 'line-4/tools/offline-resolver/resolve.py')
    observed = health.inspect_catalog(sample)
    solved = resolver.solve(sample)
    rejected = solved['status'] == 'unsatisfiable'
    reason = solved.get('conflict', {}).get('package')
    assert observed['healthy'] and observed['missing_dependency_targets'] == []
    assert rejected and 'missing-package' in reason
    finding = {'source': 'historical Requests metadata projection with one absent dependency target',
               'catalog_health': observed, 'resolver_rejected': rejected,
               'resolver_reason': reason,
               'cause': 'Catalog Health reads a dependencies list, while the established resolver uses a dependency-to-constraint mapping.'}
    Path('gathering/catalog-health-probe-35.json').write_text(json.dumps(finding, indent=2) + '\n')
    print(json.dumps(finding, indent=2))


if __name__ == '__main__':
    main()
