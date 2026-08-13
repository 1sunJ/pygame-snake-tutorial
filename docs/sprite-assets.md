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

Five files total. The board background is **not** a file — see section 4-6.

| File | Size | Purpose |
|---|---|---|
| `snake_head.png` | 32x32 | Head, facing right |
| `snake_body.png` | 32x32 | Straight body, horizontal |
| `snake_corner.png` | 32x32 | 90-degree turn, left <-> down |
| `snake_tail.png` | 32x32 | Tail tip, body to the right |
| `food_apple.png` | 32x32 | Food item |

Target layout:

```
assets/
  sprites/
    snake_head.png
    snake_body.png
    snake_corner.png
    snake_tail.png
    food_apple.png
```

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

### 4-6. Board background — no file

The background went through three versions and ended up with no asset at all.

| Version | Result |
|---|---|
| Flat checkerboard + per-pixel noise | Noise read as smudging; the 1px line ran along only two sides of each cell, so the grid looked off-register |
| Rounded plates with a darker gap | Clean, but 400 repeating plates competed with one snake and one apple for attention |
| Flat board + corner dots + vignette | Background finally recedes; the dots keep just enough spatial reference |

**The tile was the problem, not its colours.** Any repeating pattern at 400
repetitions asserts itself. What the player actually needs from the background
is the ability to judge whether the head and the food are on the same line, and
a single dot at each cell corner does that without drawing attention.

The current background is a flat fill, one dot at each cell corner, a vignette,
and a frame around the play area. It is built in `Renderer._build_board` rather
than loaded, because **a vignette cannot be a repeating tile** — its value
depends on distance from the centre of the screen, so no repeated piece can
produce it.

Two things follow from dropping the file:

- The background adapts to any grid size on its own. Only the five sprites are
  still tied to `CELL_SIZE` being 32.
- Computing the vignette per pixel would be 400k iterations and a visible
  startup pause. It is computed at 128x128 and smooth-scaled up instead. At
  48x48 the upscale left a faint square plateau in the middle of the screen.

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
| Palette | Leaf green on a warm charcoal board |
| Background | Flat board, corner dots, vignette, frame — generated in code |
| Food | Apple |

### Palette revision

The first palette was a mint-green snake on dark navy. It did not work. Navy
carries a lot of chroma, so the board asserted its own colour instead of
receding, and since blue and green are both cool the two fought rather than
separated. The red apple also sat awkwardly on it.

Dropping the board to a warm, low-chroma charcoal fixes both problems at once:
green reads naturally against warm neutrals, and the red apple settles into the
scene instead of floating on top of it. The snake green was pulled away from
cyan toward yellow at the same time, so it reads as foliage rather than neon.

The apple's leaf had to move too — once the snake became leaf-green the two were
close enough to confuse, so the leaf was pushed further toward yellow.

Stone-slab texture was rejected: it reads as a natural material and clashes with
the flat, saturated style. Pure noise alone was not enough either, because
without cell borders the player cannot count the distance to the food. The
combination keeps both the modern look and the readable grid.

### Palette

| Role | Hex |
|---|---|
| Snake outline | `#1D5226` |
| Snake edge | `#2E8C3C` |
| Snake body | `#4FC259` |
| Snake centre highlight | `#8ADE7C` |
| Apple body | `#FF4757` |
| Apple highlight | `#FF8A94` |
| Apple leaf | `#A5E063` |
| Board | `#26201A` |
| Cell corner dot | `#483E32` |
| Frame | `#181410` |
| Frame inner line | `#3C3329` |

Board colours live in `settings.py`, not in the generator, since the background
is drawn at runtime.

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
