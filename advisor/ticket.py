"""Render reviewed assessments without pretending that review grants authorization."""

def render_ticket(result: dict, reviewed: bool) -> str:
    if not reviewed or result.get('route') != 'answer' or not result.get('assessment'):
        raise ValueError('A supported assessment and explicit risk review are required.')
    a = result['assessment']
    lines = ['# AI integration request — service desk review',
             'Status: DRAFT / AUTHORIZATION PENDING',
             'Risk review acknowledged. This does not authorize provisioning.',
             '\n## Requested context']
    for key, value in result.get('scenario', {}).items():
        lines.append(f'- {key}: {value}')
    lines += ['\n## Business request', result.get('question', ''), '\n## Conditional business risks']
    lines += ['- ' + x for x in a.get('risks', [])] or ['- Risk assessment incomplete; escalate.']
    lines += ['\n## Documented facts and plan guidance']
    for item in a.get('facts', []) + a.get('plan_guidance', []):
        lines.append(f"- {item['text']} [{', '.join(item['citations'])}]")
    lines += ['\n## Proposed implementation checklist']
    for c in a.get('controls', []):
        lines += [f"- [ ] {c['action']} [{', '.join(c['citations'])}]",
                  f"  Location: {c['location']}", f"  Prerequisites: {c['prerequisites']}",
                  f"  Owner: {c['owner']}", f"  Verification: {c['verification']}", f"  Rollback: {c['rollback']}"]
    if not a.get('controls'):
        lines.append('- [ ] Controls are incomplete. Obtain an implementation review before provisioning.')
    lines += ['\n## Advisory recommendations'] + ['- '+x for x in a.get('recommendations', [])]
    lines += ['\n## Blockers / verification required'] + ['- '+x for x in a.get('unknowns', [])]
    lines += ['- Confirm exact scopes, permission types, application identity and license availability.',
              '- Obtain authorized customer/data-owner approval and assign a change owner.',
              '- Record test evidence, residual risk acceptance and rollback owner before production access.',
              '\n## Evidence']
    lines += [f"- {d['chunk_id']}: {d['title']} — {d['url']} (reviewed {d['reviewed']})" for d in result.get('evidence', [])]
    return '\n'.join(lines) + '\n'
