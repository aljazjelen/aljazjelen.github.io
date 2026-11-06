# ASH Front Plate Builder

Browser tool for laying out the front plate of an ASH steering wheel. Pick a core plate, place buttons, encoders, rotary switches, toggles, LEDs and an OLED window, and export the plate.

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
| `.dxf` | Cut outline with layers `OUTLINE`, `CUTOUTS` and `MOUNTING` (mm), plus `COUNTERBORE` for blind pockets |
| `.svg` | Same outline at 1:1 in mm, for laser cutting |
| `-parts.csv` | Every part with its position, plus quantities per part type |
| `-layout.json` | The layout itself; reopen it with **Open layout** |

If any check fails (edge margin, mounting hole, no-go area or keep-out overlap), exporting the plate asks for confirmation first.

## Editing the data
Units are mm throughout, and +Y points up.

### Wheels: `wheels/`
Each wheel has its own folder containing its core plate DXF and a `wheel.json` with its settings:

```
wheels/
  index.json            list of wheel folders; the first one is the default
  zeus/
    wheel.json
    coreplate.dxf
  hermes/
    wheel.json
    coreplate.dxf
  merida/
    wheel.json
    coreplate.dxf
```

There are three categories: GT3 and rally wheels, and button boxes. The plates are:
- **Zeus · GT3** (`zeus`): 267 × 142 mm plate with 13 mounting holes, with the GT3 Closed handles.
- **Hermes · Rally** (`hermes`): compact 147 × 108 mm plate with 6 mounting holes. No handles until there's a rally handle set.
- **Merida · Button box** (`merida`): a 120 × 120 mm button box plate with 4 corner mounting holes and no handles.
- **Ares · GT3 wide** (`ares`): a placeholder defined without a DXF.

Layouts saved with the old folder names (`backplate-5`, `rally`, `gt3-placeholder`) still open on the right wheel.

The DXF is read straight in the browser, with no conversion step:
- The largest closed shape becomes the outline.
- Circles become holes.
- Other closed shapes inside the outline become no-go areas.

Supported DXF elements are lines, arcs, circles, ellipses, polylines (including arc segments) and splines. Export the drawing in mm with the wheel centre at 0,0, or set `origin` instead. For the most accurate curves, export splines with control points, which Onshape, Fusion and SolidWorks do by default.

Main `wheel.json` settings (the `_help` block in each file lists them all):
- `edgeMargin`: how far parts must stay from the wheel's border. Zeus and Hermes use 4.5 mm.
- `holes.mount.diameters`: circle sizes that are front plate screws. These are cut through the front plate and keep `clearance` free around them.
- `holes.noGo.diameters`: circle sizes that are no-go areas, such as the hub. These aren't cut, and parts stay `clearance` away.
- `plateSpacing` and `frontPlateThickness`: the defaults applied when the wheel is picked.
- `chamfer`: a 45° chamfer on the top edge of the front plate, in mm. `outline` covers the outer edge and `mountHoles` the mounting holes. Zeus and Hermes use 0.5 on the outline and 1.7 on the mounting holes.
- `example`: the layout loaded by **Load example**.

A wheel without a DXF can set `outline` and `extraHoles` directly; `wheels/ares` is an example.

To add a wheel:
1. Create a folder.
2. Put the DXF and a `wheel.json` in it (copy one from `zeus`).
3. Add the folder name to `wheels/index.json`.

Any problems with a wheel are listed under the wheel picker in the app.

### Parts: `parts.json`
The part library. For each part it sets:
- `hole`: exactly what's cut in the front plate. That's the whole body for some parts and only the shaft for others, like the rotary switch. For buttons with a deco ring, make it larger than the cap; the deco sleeve fills the gap.
- `cap`: the button cap, knob, lever or LED on top, including its height
- `pcb`: the board or switch body underneath, including its depth behind the plate
- `clearance`: the safe space around the part. The keep-out zone is the largest of the hole, cap and PCB, plus the clearance on every side.
- optional `keepout`, to set the keep-out shape exactly instead. The keep-out is the only thing the fit checks use (edge margin, mounting holes, no-go areas, other parts), so the hole, cap or counterbore may reach beyond it. The rotary switch uses a 27.5 × 27.5 mm keep-out.
- optional `counterbore`, a wider blind pocket cut from the top of the plate around the hole, with its own `depth`. The hole still goes all the way through, and at least 0.4 mm of plate is left under the pocket. The rotary switch has a Ø30 hole with a Ø32 × 1 mm counterbore. Counterbores are in the STL, and in the DXF on their own `COUNTERBORE` layer; the SVG only has through-cuts.
- `allowOverNoGo` and `display`, plus `rotatable: false` to lock rotation (every part rotates by default)
- optional `row`, for a symmetric row of identical elements such as LEDs: `pitch` is the default centre-to-centre spacing, `maxPerSide` how many can be added on each side of the middle one

The `_help` block in the file explains every field. The sizes are typical values, so check them against your parts' datasheets.

### LED rows
The *Indicators* group has **Single LED 5 mm**, **Single LED 3 mm** and **Multiple LED 5 mm**. A Multiple LED part starts as one LED. In the **Selected part** panel, **+ LEDs** adds one LED on each side and **− LEDs** removes one from each side, up to 5 per side (11 in total). You can also set the spacing there, 8 mm by default.
- The part's X and Y are the centre of the middle LED. Rotating the part turns the whole row.
- The keep-out is one rounded strip around the whole row.
- Every LED gets its own hole in the STL, DXF and SVG. The parts list (CSV) gives the row's LED count and spacing, and the quantity counts LEDs.

### Custom parts
For a one-off part that isn't in `parts.json`, use **Custom circle** or **Custom rectangle** under *Custom* in the parts list. Each one you place has its own sizes, which you set in the side panel when it's selected:
- the cut-out: a diameter, or a width, height and corner radius
- the keep-out: the zone other parts, holes and the edge margin must stay clear of. It can't be smaller than the cut-out.

Custom parts rotate, mirror and duplicate like any other part. They're saved with the layout and listed with their sizes in the parts list (CSV). They have no depth, so the plate-spacing check doesn't apply to them.

### Deco
The deco is a separate printed piece that sits on top of the front plate, exported as its own STL (`-deco.stl`). It uses the same coordinates as the plate STL, so importing both into a slicer lines them up, for example for a multi-colour print. It's generated from the layout. The **Deco** panel has two sections, opened one at a time like the parts list: **Buttons** and **Encoders**. Button and encoder rings come out as one piece.

**Buttons:**
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

**Encoders:** a ring around the knob of every encoder. Rotary switches get no deco (`"deco": false` in `parts.json`).
- The ring has its own height, width and chamfer (defaults 2, 3 and 1 mm), and the **Gap to knob** (1 mm by default) is the free space between the knob and the ring, so the knob turns freely.
- There's no sleeve, because the knob sits above the plate on its shaft.
- Encoder rings aren't bridged.

The deco settings are saved with the layout.

### Handles: `handles/`
There's one way to do handles: a **handle set** designed in CAD, one folder per set, listed in `handles/index.json`. Your own outline picks a set in the Outline tab; a preset core plate names one in its `wheel.json` as `"handles": { "set": "gt3" }` (Zeus does).
```
handles/
  index.json
  gt3/
    handle.json
    core.dxf        the handle core seen from the front: outline + holes
    area1.dxf ...   the mounting areas, each a closed shape with its holes as circles
    grip.stl        optional: one whole handle (core + grip) for the 3D preview
```
`handle.json` (its `_help` explains every field):
- `name` ("GT3 Closed"), `mirror: true` for both sides from one.
- `offset` [x, y]: moves everything from the CAD's coordinates to the wheel's, where the hub is at 0,0. GT3 Closed uses [0, −12.75], which puts its holes exactly on Zeus' handle holes.
- `core.thickness`: the handle core's thickness at the mounting areas (7 mm, measured from the STL). The core plate is lowered by this much there, so the handle core is clamped between core plate and front plate.
- `mountAreas`: closed shapes with their screw holes. Corners rounded with **R0.1** mark the fixed outline points.
- `grip`: `{ "stl": "grip.stl", "plateFaceY": -7.5 }`. The STL is one handle in the same CAD coordinates as the DXFs: the DXFs' plane is the STL's XZ plane (Onshape's Front plane), the driver looks from −Y, and `plateFaceY` is the Y of the core face that touches the front plate. It's shown on both sides and follows Spread / Up / down / Tilt. The supplied model was reduced to about 20,000 triangles (1 MB) to keep the page light. Without a grip the handle cores are shown.

What a handle set does, on a preset core plate and on your own outline alike:
- **Front plate:** the areas' holes are mounting holes (on a preset only where its DXF doesn't already have them), and the areas are no-go zones for parts, because the core sits behind the plate there.
- **Core plate:** a pad at each mounting area (see below).
- **3D preview:** the grips, toggled with Handles above the preview. Handles aren't exported: they're your CAD parts.

### Core plate (tray)
The core plate is generated as a tray from the same outline as the front plate, and exported as its own STL (`-core.stl`, also in the zip), in the same coordinates as the plate STL. Its top touches the underside of the front plate, which sits on its wall like a lid.
- **Sloped sides:** the outside leans inward towards the bottom, 7° from vertical over the lowest 20 mm (with the 20 mm spacing that's most of the 25 mm height), so the bottom is about 2.5 mm smaller all round. The inside stays straight, so the wall gets thinner towards the bottom: 4 mm at the top, about 2.2 mm where it meets the floor (with the defaults). Set per wheel in `wheel.json` under `tray.taper` (`angle`, `height`), or `"taper": false` for straight sides.
- **Wall:** 4 mm thick at the top, all round the outline. **Floor:** 5 mm (it carries the hub and the quick-release bolts). The plate spacing is the tray's inside depth, so the tray is spacing + 5 mm tall and the part depth check still applies.
- **Screw bosses:** a Ø8 post at every front plate mounting hole, from the floor up to the front plate, with a Ø2.8 pilot hole for an M3 self-tapping screw. Posts near the outline are trimmed to it.
- **Hub:** wherever the plate has a round Ø46 no-go zone, the floor gets that opening (for the electronics) plus the quick-release pattern: 6 × Ø5.3 holes on a 70 mm circle. Merida, which has no hub zone, gets a plain floor.
- Every size can be changed per wheel in `wheel.json` under `tray`: `wall`, `floor`, `boss`, `pilot`, `taper`, and `hub` (`bore`, `pcd`, `bolts`, `bolt`, `angle`), or `"hub": false`.
- The tray's interior (the outline minus the 4 mm wall) is where everything behind the front plate has to fit. The existing checks already keep parts there: the 4.5 mm edge margin is wider than the wall, and a mounting hole's keep-out is wider than its boss.
- **Handle mounting areas:** with a handle set, the tray is solid at each mounting area up to the handle core's thickness (7 mm for GT3 Closed) below its top, and the wall there is lowered by the same amount, so the handle core is clamped between the tray and the front plate. The screws go through the front plate and the core into pilot holes in these pads.


### Back plate (test)
A first test of the part that attaches behind the core plate, shown in the 3D preview (**Back plate** checkbox) and exported as `-back.stl` (also in the zip), in the same coordinates as the other STLs.
- **Outline:** the core plate's bottom outline (after its outside slope), so the two line up.
- **Thickness:** 5 mm, right under the core plate.
- **Chamfer:** an aggressive one on the bottom edge: 10 mm inward at 70° from vertical, so it rises about 3.6 mm of the 5 mm.
- **Hub recess:** a Ø84 mm blind hole centred on the hub, 2 mm deep from the bottom (outside) face, so 3 mm of plate stays behind it (wherever the plate has the Ø46 hub zone; Merida has none).
- Per wheel in `wheel.json` under `back`: `thickness`, `chamfer` (`width`, `angle`), `hole` and `holeDepth` (0 = straight through).
- Where a 10 mm inset closes up narrow parts of the outline (Zeus' handle notches), the chamfer is built from thin 0.2 mm steps instead of one smooth surface.
- Not yet: fixing to the core plate (screws or clips).

### Built-in copy
`index.html` carries a built-in copy of `parts.json` and `wheels/`. It's only used when those files can't be loaded, for example when the page is opened straight from disk.

After editing, run `python3 tools/sync_builtin.py` to refresh the copy. GitHub Pages always uses the files themselves, so this is optional there.

### Chamfers and the 3D engine
The chamfered plate is built with [manifold-3d](https://github.com/elalish/manifold) 3.5.4, which is vendored in `vendor/` so the app doesn't depend on a CDN. The chamfer only changes the STL and the 3D preview; the DXF and SVG stay 2D outlines. If the engine can't load, the app falls back to a plain extrusion and says so under Export.

## Views
The app has three views, switched at the top. It remembers the last one; add `#outline`, `#design` or `#preview` to the link to open a specific view. A first visit starts on Outline.
- **Outline:** where the core plate comes from. Either pick an **existing design** (the wheels in `wheels/`, shown as cards with a small picture), or draw **your own outline**:
  - The drawing area is 320 × 200 mm, with the Ø46 mm electronics zone in the middle (a no-go area, like the hub on the other plates).
  - Click to place points, drag a point to move it, double-click it or press <kbd>Del</kbd> to remove it, and use the arrow keys to nudge the selected point. A click within 6 mm of an edge adds a point into that edge; otherwise it's added after the last point.
  - **Symmetric** (on by default): you draw the right half from top to bottom, its ends join the centre line, and the left half is mirrored.
  - **Round corners** rounds every corner, inner and outer, with one radius (5 mm by default).
  - **Start from** fills the canvas with a rectangle, a round shape, or a simplified copy of one of the existing designs to modify.
  - The outline must not cross itself. It should go around the electronics zone with at least 4.5 mm to spare; the panel on the right says when it doesn't.
  - **Handle mounting** (right column) picks a handle set from `handles/` (or None). A handle set comes from CAD (see *Handle sets* below):
    - **Spread / Up / down / Tilt** sliders move the handles (the outline and handles follow while you drag, and each drag is one undo step). Spread shows the overall width across both handles (e.g. 292 mm for GT3 open) and can change it by ±20 mm, moving both handles outwards or inwards symmetrically; Up / down ±10 mm; Tilt ±15°. Tilt turns them around the middle of their mounting areas (+ leans the tops outwards). Everything moves with them: core, mounting areas, holes and fixed points. Reset position puts them back where the CAD has them.
    - **Fixed points** (filled squares): the handle set puts points on your outline that you can't move or delete: marked in CAD by rounding a mounting area's corner with **R0.1**: the centre of each R0.1 arc becomes a fixed point. Without R0.1 corners, the points listed as `"anchors": [[x, y], ...]` in `handle.json` (right side; mirrored like the rest), else the outermost corners of the mounting areas (the corners of the convex hull around them). Your own points are added around them, and Clear keeps them. Round corners leaves the fixed points sharp.
    - Its **mounting areas** are always part of your outline: they're joined to what you draw and can't be deleted by editing points. An area your outline doesn't touch shows in red, and the handles wait until the outline reaches it.
    - The areas' holes become mounting holes through the front plate and into the core plate. Parts keep clear of the areas (they're no-go zones), because the handle core sits behind the plate there.
    - The handle cores are drawn around your outline, and the 3D preview shows the handles' grip model.
  - Your own outline uses a 4.5 mm edge margin, 20 mm plate spacing, 4 mm thickness, and a 0.5 mm top chamfer. Other mounting points for the front plate are still to do.
  - **Import / Export:** *Export .json* saves the outline as you edited it (points, fixed points, symmetry, rounding, handle set and its position) to open again exactly; *Export .dxf* writes the finished outline (rounded, joined with the handle mounting areas) with the mounting holes and the hub zone, for CAD. *Import…* opens either: a DXF's largest closed shape becomes your points (wheel centre at 0,0, simplified to within 0.2 mm; a shape that's symmetric about the centre line opens with Symmetric on, and the chosen handle set's fixed points are added).
  - The outline is saved with the layout. Until it's usable, the 2D design keeps showing the previous core plate and says so.
- **2D design:** the chosen core plate (**Change** goes back to Outline), the parts list, the plate editor, the selected part and the checks. The parts list shows its groups (Buttons/Rotaries, Encoders & switches, Indicators, Displays, Custom) collapsed. Click a group to open it; only one is open at a time.
- **3D preview:** a large 3D view of the plate, deco and handles, with the Export, Deco and Handles panels (Handles only describes the wheel's handle set).

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
