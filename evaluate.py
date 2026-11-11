"""Run actual model evaluations; never substitute fixture answers for live results."""
import argparse
import csv
import json
import os
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from advisor.pipeline import MODEL, ROOT, Scenario, create_graph, run


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['baseline', 'filtered', 'both'], default='both')
    args = p.parse_args()
    secrets_path = ROOT / '.streamlit' / 'secrets.toml'
    secrets = tomllib.loads(secrets_path.read_text()) if secrets_path.exists() else {}
    key = os.getenv('OPENAI_API_KEY') or secrets.get('OPENAI_API_KEY')
    if not key:
        raise SystemExit('OPENAI_API_KEY is required. No live evaluation was run.')
    cases = json.loads((ROOT / 'evals/cases.json').read_text())
    model = os.getenv('OPENAI_MODEL') or secrets.get('OPENAI_MODEL', MODEL)
    graph = create_graph(key, model)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder = ROOT / 'evals' / 'results' / stamp
    folder.mkdir(parents=True)
    modes = ['baseline', 'filtered'] if args.mode == 'both' else [args.mode]
    rows = []
    for mode in modes:
        for c in cases:
            scenario = Scenario(vendor=c.get('vendor','ChatGPT'), platform=c.get('platform','Microsoft 365'), plan=c.get('plan', 'Business'), method=c.get('method', 'Live SharePoint access'),
                                sensitivity=c.get('sensitivity', 'Internal'),
                                requested_permissions=c.get('requested_permissions', ''),
                                permissions_reviewed=c.get('permissions_reviewed', 'Unknown'),
                                consent_authorized=c.get('consent_authorized', 'Unknown'))
            try:
                result = run(graph, c['question'], scenario, mode)
                (folder / f'{mode}-{c["id"]}.json').write_text(json.dumps(result, indent=2))
                retrieved = {d['id'] for d in result['evidence']}
                expected = set(c['sources']) if c['route'] == 'answer' else set()
                citations_valid = ''
                if result['assessment']:
                    allowed = {d['chunk_id'] for d in result['evidence']}
                    citations_valid = all(f['citations'] and set(f['citations']) <= allowed for f in (result['assessment']['facts'] + result['assessment'].get('controls', []) + result['assessment'].get('plan_guidance', [])))
                rows.append({'id': c['id'], 'configuration': mode, 'execution': 'Completed',
                             'route': result['route'], 'route_match': result['route'] == c['route'],
                             'source_recall': len(retrieved & expected) / len(expected) if expected else '',
                             'latency_seconds': result['latency_seconds'], 'citation_ids_valid': citations_valid,
                             'actual_answer': json.dumps(result['assessment']) if result['assessment'] else result['message'],
                             'expected': c['expected'], 'retrieved_ids': ','.join(sorted(retrieved)),
                             'human_verdict': 'Not reviewed'})
            except Exception as exc:
                rows.append({'id': c['id'], 'configuration': mode, 'execution': 'Error:' + type(exc).__name__,
                             'route': '', 'route_match': '', 'source_recall': '', 'latency_seconds': '',
                             'citation_ids_valid': '', 'actual_answer': '', 'expected': c['expected'],
                             'retrieved_ids': '', 'human_verdict': 'Not reviewed'})
            print(mode, c['id'], rows[-1]['execution'])
    # Protect spreadsheet users against formula-like model outputs in exported CSV.
    def cell(v):
        return "'" + v if isinstance(v, str) and v.startswith(('=', '+', '-', '@')) else v
    with (folder / 'comparison.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows([{k: cell(v) for k, v in row.items()} for row in rows])
    summary = {'model': model, 'utc_run_time': stamp, 'cases_per_configuration': len(cases),
               'note': 'Source recall is expected-source coverage, not RAGAS context recall. No automatic correctness or faithfulness score.',
               'configurations': {}}
    for mode in modes:
        subset = [r for r in rows if r['configuration'] == mode]
        done = [r for r in subset if r['execution'] == 'Completed']
        scores = [r['source_recall'] for r in done if r['source_recall'] != '']
        summary['configurations'][mode] = {'completed': len(done), 'errors': len(subset) - len(done),
                    'route_match_rate_completed': sum(r['route_match'] for r in done) / len(done) if done else None,
                    'mean_expected_source_recall': sum(scores) / len(scores) if scores else None}
    (folder / 'summary.json').write_text(json.dumps(summary, indent=2))
    print('Results:', folder)


if __name__ == '__main__':
    main()
