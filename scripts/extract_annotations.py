#!/usr/bin/env python3
"""Extract syllabus annotations by bold heading numbers, never exercise numbers."""
import argparse
import json
import re
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parents[1]

def extract(source):
    annotations = {}
    current = None
    active = False
    with pymupdf.open(source) as document:
        for page in document:
            text = page.get_text()
            if 'АНОТАЦИИ НА ВЪПРОСИТЕ' in text and 'СЪДЪРЖАНИЕ' not in text:
                active = True
            if not active:
                continue
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines', []):
                    spans = line['spans']
                    value = ''.join(span['text'] for span in spans).strip()
                    if value == 'ЛИТЕРАТУРА':
                        active = False
                        break
                    if not active:
                        break
                    first = next((s for s in spans if s['text'].strip()), None)
                    heading = re.match(r'^(\d+)\.', value)
                    if heading and first and 'Bold' in first['font']:
                        number = int(heading[1])
                        if number == len(annotations) + 1:
                            current = str(number)
                            annotations[current] = []
                            value = value[heading.end():].strip()
                    if current and value and not value.isdigit() and value != 'АНОТАЦИИ НА ВЪПРОСИТЕ':
                        annotations[current].append(value)
    if list(annotations) != [str(n) for n in range(1, 36)]:
        raise ValueError('Expected all 35 ordered syllabus headings')
    return {n: re.sub(r'\s+', ' ', ' '.join(lines)) for n, lines in annotations.items()}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/konspekt_annotations.json')
    args = parser.parse_args()
    annotations = extract(args.source)
    args.output.write_text(json.dumps(annotations, ensure_ascii=False, indent=2) + '\n')
    print(f'Extracted {len(annotations)} annotations: {args.output}')

if __name__ == '__main__':
    main()
