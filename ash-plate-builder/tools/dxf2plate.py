#!/usr/bin/env python3
"""Convert a back plate DXF into a PLATES entry for the ASH Front Plate Builder.

Usage:
  python3 dxf2plate.py backplate.dxf --id bp5 --name "Backplate 5" \
      --mount 3.3 --keepout 4.2 --keepout 46 > plate.json

- The outline is the largest closed loop built from LINE / ARC / ELLIPSE /
  LWPOLYLINE / POLYLINE / SPLINE entities (arcs are flattened to <= 0.05 mm error).
- Every CIRCLE becomes a hole. Its role comes from its diameter:
    --mount D    : front plate screw hole, cut through the front plate
    --keepout D  : no-go area (handle bolts, hub), not cut, parts must stay clear
  Circles matching neither are reported on stderr and treated as keep-out.
- Coordinates are kept as drawn (mm). Re-centre in CAD if the origin is not the
  wheel centre.
"""
import argparse, json, math, sys
import ezdxf
from ezdxf import path as zpath

TOL = 0.05   # flattening tolerance, mm
JOIN = 0.02  # endpoint match tolerance, mm


def segments(msp):
    segs = []
    for e in msp:
        t = e.dxftype()
        if t in ('LINE', 'ARC', 'ELLIPSE', 'LWPOLYLINE', 'POLYLINE', 'SPLINE'):
            pts = [(v.x, v.y) for v in zpath.make_path(e).flattening(TOL)]
            if len(pts) >= 2:
                segs.append(pts)
    return segs


def chain(segs):
    """Join open polylines end to end into closed loops."""
    loops, pool = [], [list(s) for s in segs]
    close = lambda a, b: math.dist(a, b) <= JOIN
    while pool:
        cur = pool.pop()
        grew = True
        while grew and not close(cur[0], cur[-1]):
            grew = False
            for i, s in enumerate(pool):
                if close(cur[-1], s[0]):   cur += s[1:]
                elif close(cur[-1], s[-1]): cur += s[::-1][1:]
                elif close(cur[0], s[-1]):  cur = s[:-1] + cur
                elif close(cur[0], s[0]):   cur = s[::-1][:-1] + cur
                else: continue
                pool.pop(i); grew = True; break
        if close(cur[0], cur[-1]) and len(cur) > 3:
            loops.append(cur[:-1])
        else:
            print(f'warning: open contour with {len(cur)} points ignored', file=sys.stderr)
    return loops


def area(p):
    return 0.5 * sum(p[i][0]*p[(i+1) % len(p)][1] - p[(i+1) % len(p)][0]*p[i][1] for i in range(len(p)))


def dedupe(p, eps=0.01):
    out = []
    for q in p:
        if not out or math.dist(out[-1], q) > eps:
            out.append(q)
    if len(out) > 1 and math.dist(out[0], out[-1]) <= eps:
        out.pop()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dxf')
    ap.add_argument('--id', required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--inset', type=float, default=5)
    ap.add_argument('--max-depth', type=float, default=35)
    ap.add_argument('--mount', type=float, action='append', default=[], help='diameter of front plate screw holes')
    ap.add_argument('--keepout', type=float, action='append', default=[], help='diameter of no-go holes')
    ap.add_argument('--mount-ko', type=float, default=9, help='keep-out diameter around screw holes')
    a = ap.parse_args()

    msp = ezdxf.readfile(a.dxf).modelspace()
    loops = chain(segments(msp))
    if not loops:
        sys.exit('no closed outline found')
    outline = dedupe(max(loops, key=lambda l: abs(area(l))))
    if area(outline) < 0:
        outline.reverse()

    holes, match = [], lambda d, lst: any(abs(d - x) < 0.05 for x in lst)
    for e in msp.query('CIRCLE'):
        d = round(2 * e.dxf.radius, 3); x, y = round(e.dxf.center.x, 3), round(e.dxf.center.y, 3)
        if match(d, a.mount):
            holes.append({'x': x, 'y': y, 'd': d, 'ko': a.mount_ko, 'role': 'mount'})
        else:
            if not match(d, a.keepout):
                print(f'note: circle d{d} at ({x}, {y}) not classified, using keep-out', file=sys.stderr)
            holes.append({'x': x, 'y': y, 'd': d, 'ko': round(d + 2 * a.inset, 3), 'role': 'keepout'})

    plate = {'id': a.id, 'name': a.name, 'inset': a.inset, 'maxDepth': a.max_depth,
             'outline': [[round(x, 3), round(y, 3)] for x, y in outline], 'holes': holes}
    xs = [p[0] for p in outline]; ys = [p[1] for p in outline]
    print(f'outline: {len(outline)} points, {max(xs)-min(xs):.1f} x {max(ys)-min(ys):.1f} mm; '
          f'holes: {sum(h["role"]=="mount" for h in holes)} mount, {sum(h["role"]=="keepout" for h in holes)} keep-out',
          file=sys.stderr)
    json.dump(plate, sys.stdout, separators=(',', ':'))


if __name__ == '__main__':
    main()
