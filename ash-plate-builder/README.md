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

Export of the plate files is blocked while any check fails (edge margin, mounting hole or keep-out overlap).

## Editing the data
All data lives at the top of the script in `index.html`. Units are mm, the origin is the plate centre, and +Y points up.

- **`PLATES`** holds the back plates. The current entries are square placeholders (160, 200 and 240 mm) with a 5 mm edge margin, four M3 mounting holes and 35 mm clearance to the back plate. Replace or add entries as the real back plates are drawn.
- **`TYPES`** is the part library. For each part it defines:
  - the cutout
  - the keep-out zone
  - the depth behind the plate
  - the 3D preview body
  
  The cutout sizes are typical values, so check them against the datasheets of the parts you actually use.

## Controls
- Drag parts on the plate. They snap to the grid set by **Snap**.
- <kbd>Del</kbd> removes the selected part, <kbd>R</kbd> rotates it 90°, and <kbd>M</kbd> adds a mirrored copy.
- The arrow keys nudge the selected part; hold <kbd>Shift</kbd> to move 5× as far.
- <kbd>Ctrl</kbd>+<kbd>Z</kbd> undoes and <kbd>Ctrl</kbd>+<kbd>Y</kbd> redoes.
- The layout is autosaved in the browser.
