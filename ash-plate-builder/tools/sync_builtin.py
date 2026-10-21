#!/usr/bin/env python3
"""Copy parts.json and the wheels/ folder into the built-in fallback inside index.html.

index.html normally loads parts.json and wheels/ at start. The built-in copy is only used when
those files can't be fetched (for example when index.html is opened straight from disk).
Run from the folder that holds index.html:  python3 tools/sync_builtin.py
"""
import json, os, sys

root = sys.argv[1] if len(sys.argv) > 1 else '.'
html_path = os.path.join(root, 'index.html')


def dxf_keep_header_and_entities(text):
    """Drop the DXF sections the app doesn't read (TABLES, BLOCKS, OBJECTS, ...) to keep index.html small."""
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    out, keep, i = [], False, 0
    while i + 1 < len(lines):
        code, value = lines[i].strip(), lines[i + 1]
        if code == '0' and value.strip() == 'SECTION' and i + 3 < len(lines):
            keep = lines[i + 3].strip() in ('HEADER', 'ENTITIES')
        if keep:
            out += [lines[i], value]
        if code == '0' and value.strip() == 'ENDSEC':
            keep = False
        i += 2
    return '\n'.join(out + ['  0', 'EOF']) + '\n'


def replace_between(s, start, end, payload):
    a, b = s.index(start) + len(start), s.index(end)
    return s[:a] + payload + s[b:]


s = open(html_path, encoding='utf-8').read()
parts = json.load(open(os.path.join(root, 'parts.json'), encoding='utf-8'))
s = replace_between(s, '/*PARTS_JSON*/', '/*END_PARTS_JSON*/', json.dumps(parts, ensure_ascii=False, separators=(',', ':')))

wheels = {}
index = json.load(open(os.path.join(root, 'wheels', 'index.json'), encoding='utf-8'))
for folder in index['wheels']:
    cfg = json.load(open(os.path.join(root, 'wheels', folder, 'wheel.json'), encoding='utf-8'))
    cfg.pop('_help', None)
    entry = {'config': cfg}
    if cfg.get('dxf'):
        entry['dxf'] = dxf_keep_header_and_entities(open(os.path.join(root, 'wheels', folder, cfg['dxf']), encoding='utf-8', errors='replace').read())
    wheels[folder] = entry
payload = json.dumps(wheels, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
s = replace_between(s, '/*WHEELS_JSON*/', '/*END_WHEELS_JSON*/', payload)
open(html_path, 'w', encoding='utf-8').write(s)
print(f'{len(parts["parts"])} parts and {len(wheels)} wheels copied into {html_path}')
