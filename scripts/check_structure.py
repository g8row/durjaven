#!/usr/bin/env python3
"""Validate statement/proof structure; report coverage, not mathematical truth."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = {'thm', 'keythm', 'lem', 'keylem', 'prop', 'cor'}
DEFINITIONS = {'defn', 'keydefn'}
FORMAL = RESULTS | DEFINITIONS | {'keyaxiom', 'keyscheme'}
ENV = re.compile(r'\\(begin|end)\{([^}]+)\}')

def clean(text):
    # Preserve offsets, while ignoring code examples and escaped percent signs.
    text = re.sub(r'\\begin\{verbatim\}.*?\\end\{verbatim\}',
                  lambda m: ' ' * len(m[0]), text, flags=re.S)
    return re.sub(r'(?<!\\)%[^\n]*', lambda m: ' ' * len(m[0]), text)

def inspect(path):
    source = path.read_text()
    text = clean(source)
    errors, blocks, stack = [], [], []
    for match in ENV.finditer(text):
        action, name = match.groups()
        if action == 'begin':
            stack.append((name, match.start(), match.end()))
        elif not stack or stack[-1][0] != name:
            errors.append(f'unmatched end of {name} at line {text.count(chr(10), 0, match.start()) + 1}')
        else:
            kind, start, body_start = stack.pop()
            if kind in FORMAL | {'proof'}:
                blocks.append({'kind': kind, 'start': start, 'body_start': body_start,
                               'end': match.end(), 'line': text.count('\n', 0, start) + 1,
                               'body': text[body_start:match.start()]})
    errors.extend(f'unclosed {name}' for name, _, _ in stack)
    if re.search(r'\\(?:keydefn|defn|keythm|thm|prop|lem|cor)\{', text):
        errors.append('theorem environment invoked as a two-argument macro')
    blocks.sort(key=lambda b: b['start'])
    for block in blocks:
        if block['kind'] in RESULTS:
            next_formal = next((b['start'] for b in blocks
                                if b['start'] >= block['end'] and b['kind'] in FORMAL), len(text))
            proofs = [b for b in blocks if b['kind'] == 'proof'
                      and block['end'] <= b['start'] < next_formal]
            if not proofs:
                errors.append(f"{block['kind']} at line {block['line']} has no proof before the next statement")
        if not re.sub(r'\\label\{[^}]*\}|\s+', '', block['body']):
            errors.append(f"empty {block['kind']} at line {block['line']}")
    counts = {key: sum(b['kind'] in kinds for b in blocks)
              for key, kinds in [('definitions', DEFINITIONS), ('results', RESULTS), ('proofs', {'proof'})]}
    return counts, errors

def check():
    rows, errors = [], []
    for n in range(1, 36):
        path = ROOT / f'topics/bodies/topic_{n:02}.tex'
        if not path.exists():
            errors.append(f'missing topic {n}')
            continue
        counts, issues = inspect(path)
        rows.append({'topic': n, **counts})
        errors.extend(f'{path.name}: {issue}' for issue in issues)
    preamble = (ROOT / 'topics/preamble.tex').read_text()
    for name in FORMAL | {'proof'}:
        if not re.search(r'\\tcolorboxenvironment\{' + name + r'\}', preamble):
            errors.append(f'{name} has no box style')
    return rows, errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    rows, errors = check()
    totals = {key: sum(r[key] for r in rows) for key in ['definitions', 'results', 'proofs']}
    if args.report:
        args.report.write_text(json.dumps({'topics': rows, 'totals': totals, 'errors': errors,
            'scope': 'Checks LaTeX structure and proof presence; does not certify mathematical correctness or full syllabus coverage.'}, ensure_ascii=False, indent=2) + '\n')
    print(f'Topics: {len(rows)}; ' + '; '.join(f'{k}: {v}' for k, v in totals.items()))
    for error in errors:
        print(error)
    if not errors:
        print('All numbered results have proof blocks; all definition/result/proof environments have box styles.')
    return bool(errors)

if __name__ == '__main__':
    raise SystemExit(main())
