# ASH Front Plate Builder

Browser tool for laying out the front plate of an ASH steering wheel. Pick a back plate, place buttons, encoders, rotary switches, toggles, LEDs and an OLED window, and export the plate.

Everything runs client-side, so it can be hosted as a static site on GitHub Pages.

## Run on GitHub Pages
1. Create a repository and commit `index.html`, `.nojekyll` and this README to `main`.
2. In the repository, open **Settings → Pages**.
3. Under **Source**, choose *Deploy from a branch*, then pick `main` and `/ (root)`.
4. The site appears at `https://<user>.github.io/<repo>/`.

To run it locally, open `index.html` in a browser. It needs internet access to load three.js and JSZip from a CDN.

## Exports
| File | Use |
|---|---|
| `.stl` | Front plate for 3D printing (binary STL, mm) |
| `-deco.stl` | The deco piece on its own, in the same position as the plate |
| `.dxf` | Cut outline with layers `OUTLINE`, `CUTOUTS` and `MOUNTING` (mm) |
| `.svg` | Same outline at 1:1 in mm, for laser cutting |
| `-parts.csv` | Every part with its position, plus quantities per part type |
| `-layout.json` | The layout itself; reopen it with **Open layout** |

If any check fails (edge margin, mounting hole, no-go area or keep-out overlap), exporting the plate asks for confirmation first.

## Editing the data
Units are mm throughout, and +Y points up.

### Wheels: `wheels/`
Each wheel has its own folder containing its back plate DXF and a `wheel.json` with its settings:

```
wheels/
  index.json            list of wheel folders; the first one is the default
  backplate-5/
    wheel.json
    backplate.dxf
```

The DXF is read straight in the browser, with no conversion step:
- The largest closed shape becomes the outline.
- Circles become holes.
- Other closed shapes inside the outline become no-go areas.

Supported DXF elements are lines, arcs, circles, ellipses, polylines (including arc segments) and splines. Export the drawing in mm with the wheel centre at 0,0, or set `origin` instead. For the most accurate curves, export splines with control points, which Onshape, Fusion and SolidWorks do by default.

Main `wheel.json` settings (the `_help` block in each file lists them all):
- `edgeMargin`: how far parts must stay from the wheel's border. Backplate 5 uses 4.5 mm.
- `holes.mount.diameters`: circle sizes that are front plate screws. These are cut through the front plate and keep `clearance` free around them.
- `holes.noGo.diameters`: circle sizes that are no-go areas, such as the hub. These aren't cut, and parts stay `clearance` away.
- `plateSpacing` and `frontPlateThickness`: the defaults applied when the wheel is picked.
- `chamfer`: a 45° chamfer on the top edge of the front plate, in mm. `outline` covers the outer edge and `mountHoles` the mounting holes. Backplate 5 uses 0.8 and 0.5.
- `example`: the layout loaded by **Load example**.

A wheel without a DXF can set `outline` and `extraHoles` directly; `wheels/gt3-placeholder` is an example.

To add a wheel:
1. Create a folder.
2. Put the DXF and a `wheel.json` in it (copy one from `backplate-5`).
3. Add the folder name to `wheels/index.json`.

Any problems with a wheel are listed under the wheel picker in the app.

### Parts: `parts.json`
The part library. For each part it sets:
- `hole`: exactly what's cut in the front plate. That's the whole body for some parts and only the shaft for others, like the rotary switch. For buttons with a deco ring, make it larger than the cap; the deco sleeve fills the gap.
- `cap`: the button cap, knob, lever or LED on top, including its height
- `pcb`: the board or switch body underneath, including its depth behind the plate
- `clearance`: the safe space around the part. The keep-out zone is the largest of the hole, cap and PCB, plus the clearance on every side.
- optional `keepout`, to set the keep-out shape exactly instead
- `allowOverNoGo` and `display`, plus `rotatable: false` to lock rotation (every part rotates by default)

The `_help` block in the file explains every field. The sizes are typical values, so check them against your parts' datasheets.

### Custom parts
For a one-off part that isn't in `parts.json`, use **Custom circle** or **Custom rectangle** under *Custom* in the parts list. Each one you place has its own sizes, which you set in the side panel when it's selected:
- the cut-out: a diameter, or a width, height and corner radius
- the keep-out: the zone other parts, holes and the edge margin must stay clear of. It can't be smaller than the cut-out.

Custom parts rotate, mirror and duplicate like any other part. They're saved with the layout and listed with their sizes in the parts list (CSV). They have no depth, so the plate-spacing check doesn't apply to them.

### Deco
The deco is a separate printed piece that sits on top of the front plate, exported as its own STL (`-deco.stl`). It uses the same coordinates as the plate STL, so importing both into a slicer lines them up, for example for a multi-colour print. It's generated from the layout. For now it has one feature, set in the **Deco** panel:
- **Rings around buttons:** a ring around every part whose cap style is `button`. Its opening is the button's element (the `cap` in `parts.json`), so the cap passes through. Defaults are 2 mm high and 4 mm wide, with a 1 mm 45° chamfer on the top outer edge.
- **Sleeve:** each ring has a sleeve, part of the same piece, that goes down into the button's hole and fills the gap between the cap and the hole. It locates the deco on the plate. The sleeve's wall is (hole − cap) / 2: the 12 mm button has a Ø14 cap in a Ø15 hole, so its wall is 0.5 mm. The plate hole is never enlarged; it's always the `hole` from `parts.json`. A button whose hole leaves less than 0.3 mm around the cap gets no sleeve, and the Deco panel says so. Default sleeve depth is 3 mm, limited to the plate thickness, and 0 turns sleeves off.
- **Bridges:** buttons whose rings are at most 6 mm apart, edge to edge, are joined automatically by a bar. You can change the distance or turn bridges off.
  - **Bar width** sets how wide the bar is. Leave it empty for the widest allowed: the smaller ring's diameter minus the chamfer on both sides, for example 24 mm for two 16 mm buttons and 20 mm for two 12 mm buttons. Any value is kept between 2 mm and that maximum, per pair.
  - The joints are rounded with a 1.5 mm radius, so across a short gap a narrow bar looks wider in the middle.
  - A bar narrower than twice the chamfer ends in a ridge on top, with no flat top.
  - The chamfer runs continuously around the whole outline.
  - A bridge that would cover another part or a mounting hole is skipped, and the Deco panel says which.
- Rings that touch are merged into one piece.
- The deco stays on the flat top of the plate, inside the outline chamfer. It leaves other parts' cut-outs and caps (plus 0.5 mm) and the mounting holes clear.
- The sleeve and the plate hole have the same nominal size. For printing clearance, make the `hole` slightly larger in `parts.json`.

The deco settings are saved with the layout.

### Handles (3D preview only)
A wheel can define handles in its `wheel.json`, so the style follows the wheel. For now they're a cosmetic addition to the 3D preview, to judge how the wheel looks, and aren't exported. Backplate 5 has simple F1-style grips:
- **Grip:** a 30 × 38 mm oval tube (width in the plate's plane × depth front to back) with rounded ends, along a smooth curve through `left.path`. The curve starts at the bottom-corner mount hole, runs beside the wheel, and ends over the two top mount holes. The top of the grip always sits just below the underside of the front plate (`grip.gapBelowFrontPlate`, 0.5 mm), whatever the plate spacing.
- **Bolting:** the grip shows bolt holes where it covers a mount hole, here the bottom hole and both top holes. The Handles panel lists the holes it doesn't cover.
- **Mirroring:** the right handle is the left one mirrored.

The **Handles** panel can hide them and change the grip width and depth. To reshape a grip, edit the `path` points in `wheel.json`.

### Built-in copy
`index.html` carries a built-in copy of `parts.json` and `wheels/`. It's only used when those files can't be loaded, for example when the page is opened straight from disk.

After editing, run `python3 tools/sync_builtin.py` to refresh the copy. GitHub Pages always uses the files themselves, so this is optional there.

### Chamfers and the 3D engine
The chamfered plate is built with [manifold-3d](https://github.com/elalish/manifold) 3.5.4, which is vendored in `vendor/` so the app doesn't depend on a CDN. The chamfer only changes the STL and the 3D preview; the DXF and SVG stay 2D outlines. If the engine can't load, the app falls back to a plain extrusion and says so under Export.

## Views
The app has two views, switched at the top. It remembers the last one; add `#design` or `#preview` to the link to open a specific view.
- **2D design:** wheel selection, the parts list, the plate editor, the selected part and the checks.
- **3D preview:** a large 3D view of the plate, deco and handles, with the Export, Deco and Handles panels.

## Controls
In the editor:
- the black shapes are the caps (button caps, knobs, levers, LEDs), as seen from the front; parts without a cap, like the display, show their cut-out
- the dotted line is the hole cut in the front plate (`hole` in `parts.json`)
- the dashed line around a part is its keep-out zone
- light circles are mounting holes; hatched areas are no-go zones

- Drag parts on the plate. They snap to the grid set by **Snap**.
- Drag the blue handle on the selected part to rotate it. It snaps to 5°; hold <kbd>Shift</kbd> for 1° steps. The keep-out zone rotates with the part.
- <kbd>Del</kbd> removes the selected part, <kbd>R</kbd> rotates it 90° (<kbd>Shift</kbd>+<kbd>R</kbd> 5°), and <kbd>M</kbd> adds a mirrored copy.
- The arrow keys nudge the selected part; hold <kbd>Shift</kbd> to move 5× as far.
- <kbd>Ctrl</kbd>+<kbd>Z</kbd> undoes and <kbd>Ctrl</kbd>+<kbd>Y</kbd> redoes.
- The layout is autosaved in the browser.
