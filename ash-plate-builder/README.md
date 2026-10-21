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
Back plates live at the top of the script in `index.html`. Part sizes live in `parts.json`. Units are mm, the origin is the plate centre, and +Y points up.

- **`PLATES`** holds the back plates. Each one has:
  - `outline`, a closed polygon of any shape
  - `inset`, the edge margin
  - `holes`, the mounting holes

  - **Backplate 5** (the default) was imported from CAD.
  - **GT3 wide** and the squares are placeholder shapes.

  Each hole has a `role`:
  - `mount` is a front plate screw. It's cut through the front plate and keeps parts clear.
  - `keepout` is a no-go area such as a handle bolt or the hub. It isn't cut, and parts must stay clear of the hole plus the edge margin.

  A part type with `ignoresNoGo: true` (the OLED for now) only has to avoid `mount` holes.

  The distance between the front and back plates is the **Plate spacing** setting (default 20 mm). Parts deeper than that get a warning.
- **`parts.json`** (next to `index.html`) is the part library. Edit it on GitHub and the site picks it up on the next load, with no rebuild needed. Each part sets:
  - `hole`: the cutout in the front plate
  - `cap`: the button cap, knob, lever or LED on top, including its height
  - `pcb`: the board or switch body underneath, including its depth behind the plate
  - `clearance`: the safe space around the part. The keep-out zone is the largest of the hole, cap and PCB, plus the clearance on every side.
  - optional `keepout`, to set the keep-out shape exactly instead
  - `allowOverNoGo` and `display`, plus `rotatable: false` to lock rotation (every part rotates by default)

  The `_help` block at the top of the file explains every field. The sizes are typical values, so check them against your parts' datasheets.

  `index.html` also carries a built-in copy of the library, used when `parts.json` can't be loaded, for example when the page is opened as a local file. To refresh that copy after editing `parts.json`, run `python3 tools/sync_parts.py`.

## Adding a back plate from CAD
Export the back plate as a DXF in mm, with the wheel centre at the origin. Then run:

```
pip install ezdxf
python3 tools/dxf2plate.py backplate.dxf --id bp6 --name "Backplate 6" \
    --mount 3.3 --keepout 4.2 --keepout 46 > bp6.json
```

The script works like this:
- The largest closed loop of lines and arcs becomes the outline.
- Each circle becomes a hole, and its role comes from its diameter.
- Circles that match neither `--mount` nor `--keepout` are reported and treated as keep-out.

Paste the JSON into `index.html` as a constant and add it to `PLATES`.

## Controls
- Drag parts on the plate. They snap to the grid set by **Snap**.
- Drag the orange handle on the selected part to rotate it. It snaps to 15°; hold <kbd>Shift</kbd> for 1° steps. The keep-out zone rotates with the part.
- <kbd>Del</kbd> removes the selected part, <kbd>R</kbd> rotates it 90° (<kbd>Shift</kbd>+<kbd>R</kbd> 15°), and <kbd>M</kbd> adds a mirrored copy.
- The arrow keys nudge the selected part; hold <kbd>Shift</kbd> to move 5× as far.
- <kbd>Ctrl</kbd>+<kbd>Z</kbd> undoes and <kbd>Ctrl</kbd>+<kbd>Y</kbd> redoes.
- The layout is autosaved in the browser.
