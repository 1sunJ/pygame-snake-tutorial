# Sprite Asset Specification

Plan for replacing the plain `pygame.draw.rect` visuals with pixel art sprites.

**Scope of this document: assets only.** No game code is modified until every
asset exists and has been reviewed.

---

## 1. Decisions made

| Topic | Decision | Reason |
|---|---|---|
| Art style | 32px pixel art | Vector art blurs at 32px and leaves seams between tiles |
| Cell size | `CELL_SIZE` 20 -> 32 | 20px leaves no room for an eye or a highlight |
| Background | Repeating 64x64 tile | One large image cannot survive a grid size change |
| Production | Generated programmatically | Uses the already-installed `pygame`, no new dependency |

### Why pixel art over vector

- **Vector gains nothing at 32px.** Its selling point is smooth curves at any
  scale, but the final output is a 32x32 grid either way.
- **Tile seams.** Snake body segments must butt together into one continuous
  tube. Pixel art edges land exactly on pixel boundaries. Vector art leaves
  semi-transparent edge pixels, drawing a faint line at every cell boundary.
- **The motion is already retro.** `main.py` starts at 10 FPS, so the snake
  teleports one cell at a time. Smooth artwork fights that; pixel art embraces it.

---

## 2. Common requirements

Every file must satisfy these.

| Property | Value |
|---|---|
| Dimensions | 32x32, square, no exceptions (background tile is 64x64) |
| Format | PNG-32 with alpha channel |
| Background | Transparent, so the board tile shows through |
| Anti-aliasing | Off. No blended pixels on any edge |
| Body thickness | 28px, centred, leaving a 2px margin on each side |

The 28px body thickness is the critical number. Head, body, corner and tail must
all use it, or the snake will change width as it moves.

---

## 3. Asset list

Six files total.

| File | Size | Purpose |
|---|---|---|
| `snake_head.png` | 32x32 | Head, facing right |
| `snake_body.png` | 32x32 | Straight body, horizontal |
| `snake_corner.png` | 32x32 | 90-degree turn, left <-> down |
| `snake_tail.png` | 32x32 | Tail tip, body to the right |
| `food_apple.png` | 32x32 | Food item |
| `bg_tile.png` | 64x64 | Board background, covers 2x2 cells |

Target layout:

```
assets/
  sprites/          moving objects
    snake_head.png
    snake_body.png
    snake_corner.png
    snake_tail.png
    food_apple.png
  tiles/            repeating background
    bg_tile.png
```

The split follows the original meaning of the terms. A *sprite* is a movable
image drawn over the background; a *tile* is a fixed piece repeated to build the
background itself. `bg_tile.png` is the only tile here.

Note that "sprite" in this document means an image file, in the general sense.
It does **not** refer to `pygame.sprite.Sprite`, the class-based helper with
built-in collision handling. `snake_game.py` already tracks the snake as a list
of coordinate tuples and does its own collision checks, so that class is not
used.

`.gitignore` does not exclude `assets/`, so these will be committed. At roughly
1 KB each that is fine.

---

## 4. Per-asset specification

### 4-1. `snake_body.png` — straight body

```
x=0                              x=31
 +--------------------------------+
 |                                |  y=0,1    transparent
 |################################|  y=2      outline
 |################################|  y=3-5    light green
 |################################|  y=6-19   base green
 |################################|  y=20-28  dark green
 |################################|  y=29     outline
 |                                |  y=30,31  transparent
 +--------------------------------+
   ^ full bleed left and right, zero margin
```

- **Left and right edges must be filled to x=0 and x=31.** Any margin makes the
  snake look dashed instead of continuous.
- The 2px transparent margin on top and bottom is required. It is what separates
  two body rows running side by side.

### 4-2. `snake_corner.png` — turn, connecting left and down

```
 +--------------------------------+
 |###################@@           |  enters from the left,
 |################### @@          |  exits through the bottom
 |############@@@     @@          |
 |#####@@@            @@          |  <- outer arc
 |      @@@@@@        @@          |
 |          @@@       @@          |  <- inner arc
 |            @@      @@          |
 +--------------------------------+
   ^ left edge filled    ^ bottom edge filled
```

- Use a smooth arc, not a hard right angle.
- Only the left and bottom edges are full bleed. The top and right edges keep
  their margin.

### 4-3. `snake_head.png` — head, facing right

```
 +--------------------------------+
 |####################@@@         |
 |### oo ###############@@        |  o  upper eye
 |######################@@   ~~   |  ~  tongue (optional)
 |### oo ###############@@        |  o  lower eye
 |####################@@@         |
 +--------------------------------+
   ^ left edge filled   rounded snout
```

- Top-down view, so **both eyes are visible**, one above and one below the
  centre line.
- Eye: a 4x4 dark blob with the corners cut, plus a **single** white pixel as a
  highlight. A white eyeball with a dark pupil was tried first and read as two
  white squares; two highlight pixels instead of one read as a bullseye.
- Only the left edge is full bleed; it is the only side that meets the body.
- **Same thickness as the body.** Making the head wider was tried and abandoned:
  at 32px there is room for exactly 1px of extra width, and a 1px change renders
  as a visible step at the neck rather than a curve. The head is distinguished
  by its eyes and rounded snout instead.

### 4-4. `snake_tail.png` — tail tip, body to the right

```
 +--------------------------------+
 |                    ############|
 |             ###################|
 |      ##########################|  narrows toward
 |      ##########################|  the left
 |             ###################|
 |                    ############|
 +--------------------------------+
   ^ blunt tip            ^ right edge filled
```

- Right edge is the full 28px so it matches the body exactly.
- Left tip narrows to roughly 6px and stays rounded, not pointed.

### 4-5. `food_apple.png` — food

```
 +--------------------------------+
 |           |  <<<               |  stem and leaf
 |        ###########             |
 |      ###*#############         |  *  specular highlight (upper left)
 |     #################          |
 |      ###############           |
 |        ###########             |
 +--------------------------------+
   2-3px margin on all four sides
```

This is the only sprite with no full-bleed edge. Food is a discrete object and
needs margin on every side to read as sitting inside a cell.

### 4-6. `bg_tile.png` — board background

64x64, covering a 2x2 block of cells. Repeated 10x10 times to fill the 20x20
grid.

```
+------+------+
| dark | lite |   this 64x64 tile repeats
+------+------+   across the whole board
| lite | dark |
+------+------+
```

Requirements:

- **Seamless.** The left edge must continue into the right edge, and the top
  into the bottom, or every repetition shows a visible join.
- **Very low contrast.** The tile appears 100 times on screen. Anything more
  than 2-3 brightness steps between the two shades makes the repetition obvious
  and pulls attention away from the snake.
- **Not green.** The snake is the green element. A grass background would bury
  it. Neutral or dark earth tones keep the snake readable.

The checkerboard is functional as well as decorative: visible cells let the
player count the distance between the head and the food.

---

## 5. Rotation convention

Only 5 sprites are drawn, but 15 on-screen variants are produced by rotating
them at load time.

| Source | Default orientation | Derived by rotation | Total |
|---|---|---|---|
| `snake_head` | faces right | up, down, left | 4 |
| `snake_body` | horizontal | vertical | 2 |
| `snake_corner` | left <-> down | 3 remaining turns | 4 |
| `snake_tail` | body to the right | up, down, left | 4 |
| `food_apple` | none | none | 1 |
| | | | **15** |

Rotation angles, using `pygame.transform.rotate` (counter-clockwise):

| Direction | Angle |
|---|---|
| right | 0 |
| up | 90 |
| left | 180 |
| down | 270 |

For corners, the angle is chosen by which two sides the segment connects:

| Connects | Angle |
|---|---|
| left + down | 0 |
| down + right | 90 |
| right + up | 180 |
| up + left | 270 |

### Two constraints this imposes

**Sprites must be symmetric about the centre line.** If the body is not
perfectly centred, the snake changes thickness when it turns vertical.

**Shading must be symmetric across the tube as well.** This one is easy to get
wrong. A tube lit from the top looks correct on its own, but the highlight
rotates with the sprite: horizontal body lit on top, vertical body lit on the
left, corner lit on its outer arc. Every joint then shows the bright band
jumping to a different side, and corners grow a dark patch where the inner edge
meets a neighbouring segment.

The fix is to shade the tube symmetrically — bright along the centre line,
darker toward both edges. That reads as a cylinder, and because it is identical
under 90-degree rotation, every joint lines up. This was caught during the first
render and the generator now shades this way.

---

## 6. Deliberately not created

| Item | Reason |
|---|---|
| Full-board background image | 640x640 is 400k pixels; it also breaks whenever the grid size changes |
| Wall / border art | `snake_game.py` has no wall concept, it just checks whether the head left the grid |

---

## 7. Art direction

| Decision | Choice |
|---|---|
| Palette | Vivid modern — high chroma green on dark navy |
| Background texture | Fine per-pixel noise plus a faint 1px cell border |
| Food | Apple |

Stone-slab texture was rejected: it reads as a natural material and clashes with
the flat, saturated style. Pure noise alone was not enough either, because
without cell borders the player cannot count the distance to the food. The
combination keeps both the modern look and the readable grid.

### Palette

| Role | Hex |
|---|---|
| Snake outline | `#1B5E3A` |
| Snake edge | `#249E63` |
| Snake body | `#3DD68C` |
| Snake centre highlight | `#7FF5B8` |
| Apple body | `#FF4757` |
| Apple highlight | `#FF8A94` |
| Board gap | `#0F162A` |
| Board dark cell | `#1C2746` |
| Board light cell | `#222F54` |
| Cell top edge | `#293862` |

### Board tile revision

The first attempt was a flat checkerboard with per-pixel noise and a 1px lighter
line on two sides of each cell. It looked muddy: the noise read as smudging
rather than texture, and because the line only ran along two edges the grid
looked misaligned, like graph paper printed off-register.

The current tile instead draws each cell as a rounded plate with a darker gap
between plates, and lifts the top edge of each plate by one shade. The grid now
reads as a deliberate pattern rather than dirt, and the gap is uniform on all
four sides.

---

## 8. Follow-up code changes

Deferred until all six assets exist.

| File | Change | Size |
|---|---|---|
| `settings.py` | `CELL_SIZE` 20 -> 32, window becomes 640x640 | 1 line |
| `renderer.py` | Replace the rect loop with sprite blitting; derive head / body / corner / tail from neighbouring segments | ~40 lines |
| `snake_game.py` | None | — |

The renderer can work out every segment type by comparing each cell against its
neighbours in the `snake` list, so **the game logic stays untouched**. That
preserves the separation already described at the top of `renderer.py`.

Sprites are loaded once in `Renderer.__init__` with `pygame.image.load(...)`
followed by `.convert_alpha()`, then blitted each frame. Loading inside the draw
loop would hit the disk every frame.

---

## 9. Later candidates

Not needed now, recorded so they are not forgotten.

- Sparkle effect when food is eaten (3-4 frames)
- Alternate head sprite for the death frame
- Additional food types, e.g. a score multiplier item

---

## 10. Production notes

**Status: all six assets are generated and reviewed.** Game code is still
untouched; section 8 is the remaining work.

Sprites are generated by a script kept at `tools/make_sprites.py`. It draws
pixels by coordinate and writes PNG files using `pygame`, so no extra dependency
is required. Re-run it after editing any colour or shape:

```bash
python3 tools/make_sprites.py
```

The generator is a build tool, not game code. The game only needs the PNG files;
the script exists so colours and shapes can be adjusted and re-exported later.

A caveat worth recording: coordinate-generated art is clean and regular, but it
does not carry the character of hand-drawn work. The output is best treated as a
solid starting point that can be refined by hand in Piskel or Aseprite.
