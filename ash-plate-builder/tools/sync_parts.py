#!/usr/bin/env python3
"""Copy parts.json into the built-in fallback inside index.html (between the PARTS_JSON markers)."""
import json, sys
html_path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
parts_path = sys.argv[2] if len(sys.argv) > 2 else 'parts.json'
s = open(html_path, encoding='utf-8').read()
cfg = json.load(open(parts_path, encoding='utf-8'))
a, b = s.index('/*PARTS_JSON*/') + len('/*PARTS_JSON*/'), s.index('/*END_PARTS_JSON*/')
open(html_path, 'w', encoding='utf-8').write(s[:a] + json.dumps(cfg, ensure_ascii=False, separators=(',', ':')) + s[b:])
print(f'{len(cfg["parts"])} parts copied into {html_path}')
