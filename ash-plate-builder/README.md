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
All data lives at the top of the script in `index.html`. Units are mm, the origin is the plate centre, and +Y points up.

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
- **`TYPES`** is the part library. For each part it defines:
  - the cutout
  - the keep-out zone
  - the depth behind the plate
  - the 3D preview body
  
  The cutout sizes are typical values, so check them against the datasheets of the parts you actually use.

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
- <kbd>Del</kbd> removes the selected part, <kbd>R</kbd> rotates it 90°, and <kbd>M</kbd> adds a mirrored copy.
- The arrow keys nudge the selected part; hold <kbd>Shift</kbd> to move 5× as far.
- <kbd>Ctrl</kbd>+<kbd>Z</kbd> undoes and <kbd>Ctrl</kbd>+<kbd>Y</kbd> redoes.
- The layout is autosaved in the browser.
