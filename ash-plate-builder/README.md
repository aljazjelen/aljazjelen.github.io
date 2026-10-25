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
- `hole`: the cutout in the front plate
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

### Built-in copy
`index.html` carries a built-in copy of `parts.json` and `wheels/`. It's only used when those files can't be loaded, for example when the page is opened straight from disk.

After editing, run `python3 tools/sync_builtin.py` to refresh the copy. GitHub Pages always uses the files themselves, so this is optional there.

### Chamfers and the 3D engine
The chamfered plate is built with [manifold-3d](https://github.com/elalish/manifold) 3.5.4, which is vendored in `vendor/` so the app doesn't depend on a CDN. The chamfer only changes the STL and the 3D preview; the DXF and SVG stay 2D outlines. If the engine can't load, the app falls back to a plain extrusion and says so under Export.

## Controls
- Drag parts on the plate. They snap to the grid set by **Snap**.
- Drag the blue handle on the selected part to rotate it. It snaps to 5°; hold <kbd>Shift</kbd> for 1° steps. The keep-out zone rotates with the part.
- <kbd>Del</kbd> removes the selected part, <kbd>R</kbd> rotates it 90° (<kbd>Shift</kbd>+<kbd>R</kbd> 5°), and <kbd>M</kbd> adds a mirrored copy.
- The arrow keys nudge the selected part; hold <kbd>Shift</kbd> to move 5× as far.
- <kbd>Ctrl</kbd>+<kbd>Z</kbd> undoes and <kbd>Ctrl</kbd>+<kbd>Y</kbd> redoes.
- The layout is autosaved in the browser.
