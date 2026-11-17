# Aseprite File Format (.ase / .aseprite) & GIMP Palette (.gpl) Specifications

Official Aseprite Specifications: [aseprite/aseprite](https://github.com/aseprite/aseprite)
Recommended Ebitengine Integration Library: [SolarLune/goaseprite](https://github.com/SolarLune/goaseprite)

---

## 1. Primitive Types & Byte Order

ASE files use Intel (little-endian) byte order across all headers and chunks.

- `BYTE`: 8-bit unsigned integer (`uint8`)
- `WORD`: 16-bit unsigned integer (`uint16`)
- `SHORT`: 16-bit signed integer (`int16`)
- `DWORD`: 32-bit unsigned integer (`uint32`)
- `LONG`: 32-bit signed integer (`int32`)
- `FIXED`: 32-bit fixed-point (`16.16`) value
- `FLOAT`: 32-bit single-precision value (`float32`)
- `DOUBLE`: 64-bit double-precision value (`float64`)
- `QWORD`: 64-bit unsigned integer (`uint64`)
- `LONG64`: 64-bit signed integer (`int64`)
- `BYTE[n]`: Sequence of `n` raw bytes
- `STRING`:
  - `WORD`: String length in bytes
  - `BYTE[length]`: UTF-8 characters (no trailing `'\0'` byte)
- `POINT`:
  - `LONG`: X coordinate
  - `LONG`: Y coordinate
- `SIZE`:
  - `LONG`: Width in pixels
  - `LONG`: Height in pixels
- `RECT`:
  - `POINT`: Origin coordinates
  - `SIZE`: Rectangle dimensions
- `PIXEL`: Single pixel value matching the header color depth:
  - **RGBA (32 bpp)**: `BYTE[4]` in order Red, Green, Blue, Alpha
  - **Grayscale (16 bpp)**: `BYTE[2]` in order Value, Alpha
  - **Indexed (8 bpp)**: `BYTE` palette index
- `TILE`: Tilemap entry stored as `BYTE`, `WORD`, or `DWORD` with bit masks
- `UUID`: 16-byte Universally Unique Identifier (`BYTE[16]`)

---

## 2. File Architecture

An `.aseprite` file starts with a fixed 128-byte file header followed immediately by one or more frames. Each frame begins with a 16-byte frame header followed by a sequence of typed chunks.

To read or write an `.aseprite` file:
1. Read or write the **128-byte File Header** (magic number `0xA5E0`).
2. Iterate through each frame (`0 .. Frames - 1`):
   - Read or write the **16-byte Frame Header** (magic number `0xF1FA`).
   - Read or write each chunk in the frame:
     - Frame 0 typically defines the **Palette Chunk (`0x2019`)**, **Layer Chunk(s) (`0x2004`)**, and **Tags Chunk (`0x2018`)**, followed by the frame's **Cel Chunk(s) (`0x2005`)**.
     - Subsequent frames store their per-frame **Cel Chunk(s) (`0x2005`)** containing ZLIB-compressed pixel buffers.

---

## 3. File Header Specification (128 Bytes)

```text
Offset  Type        Description
0       DWORD       Total file size in bytes
4       WORD        Magic number (0xA5E0)
6       WORD        Number of frames
8       WORD        Width in pixels
10      WORD        Height in pixels
12      WORD        Color depth (32 = RGBA, 16 = Grayscale, 8 = Indexed)
14      DWORD       Flags:
                      1 = Layer opacity has valid value
                      2 = Layer blend mode/opacity is valid for groups
                      4 = Layers have a UUID
18      WORD        Speed in ms between frames (deprecated: use frame duration)
20      DWORD       Reserved (set to 0)
24      DWORD       Reserved (set to 0)
28      BYTE        Transparent palette index (for 8 bpp Indexed sprites)
29      BYTE[3]     Ignore (set to 0)
32      WORD        Number of colors (0 means 256 for legacy sprites)
34      BYTE        Pixel width ratio (default 1)
35      BYTE        Pixel height ratio (default 1)
36      SHORT       X position of grid
38      SHORT       Y position of grid
40      WORD        Grid width (default 16)
42      WORD        Grid height (default 16)
44      BYTE[84]    Reserved for future use (set to 0)
```

---

## 4. Frame Header (16 Bytes) & Chunk Envelope

```text
Offset  Type        Description
0       DWORD       Total bytes in this frame (including the 16-byte frame header)
4       WORD        Magic number (0xF1FA)
6       WORD        Old chunk count (if 0xFFFF, read the 32-bit New chunk count)
8       WORD        Frame duration in milliseconds (for example, 100 for 10 FPS)
10      BYTE[2]     Reserved (set to 0)
12      DWORD       New chunk count (if 0, use Old chunk count)
```

Every chunk inside a frame starts with a 6-byte envelope:
```text
Offset  Type        Description
0       DWORD       Chunk size in bytes (includes these 6 header bytes)
4       WORD        Chunk type identifier
6       BYTE[]      Chunk payload (Chunk size - 6 bytes)
```

---

## 5. Primary Chunk Types

### 5.1 Layer Chunk (`0x2004`)
Defines a sprite layer in the layer stack (ordered bottom to top):
- `WORD`: Flags (`1` = Visible, `2` = Editable, `4` = Lock movement, `8` = Background)
- `WORD`: Layer type (`0` = Normal image layer, `1` = Group, `2` = Tilemap)
- `WORD`: Child nesting level
- `WORD`: Default width (ignored, set to `0`)
- `WORD`: Default height (ignored, set to `0`)
- `WORD`: Blend mode (`0` = Normal)
- `BYTE`: Opacity (`0..255`, valid when file header flag `1` is set)
- `BYTE[3]`: Reserved (`0`)
- `STRING`: Layer name (for example, `"Base"`)

### 5.2 Cel Chunk (`0x2005`)
Stores pixel data for a specific layer in the current frame:
- `WORD`: Layer index (`0` for the first layer)
- `SHORT`: X position in canvas coordinates
- `SHORT`: Y position in canvas coordinates
- `BYTE`: Opacity level (`255` = opaque)
- `WORD`: Cel type:
  - `0`: Raw Image Data (uncompressed)
  - `1`: Linked Cel
  - `2`: Compressed Image (ZLIB-compressed pixels, standard for `.aseprite` export)
  - `3`: Compressed Tilemap
- `SHORT`: Z-Index (`0` = default layer order)
- `BYTE[5]`: Reserved (`0`)
- For Cel type `2` (Compressed Image):
  - `WORD`: Cel width in pixels
  - `WORD`: Cel height in pixels
  - `BYTE[]`: ZLIB stream (`compress/zlib` in Go) of `width * height * 4` RGBA bytes

### 5.3 Tags Chunk (`0x2018`)
Stores named animation frame ranges (`idle`, `run`, `attack`, `hit`, `death`):
- `WORD`: Number of tags
- `BYTE[8]`: Reserved (`0`)
- For each tag:
  - `WORD`: From frame index (inclusive, 0-based)
  - `WORD`: To frame index (inclusive, 0-based)
  - `BYTE`: Loop animation direction (`0` = Forward/Loop, `1` = Reverse, `2` = Ping-pong, `3` = Ping-pong Reverse)
  - `WORD`: Repeat count (`0` = infinite loop, `1` = play once, `N` = repeat `N` times)
  - `BYTE[6]`: Reserved (`0` by default; `sprite-design` stores `0xA5` at byte `0` followed by `WORD` `LoopFromFrame` at bytes `1..2` when a tag defines lead-in `once` intro frames such as `tag run 8 once, 9..11 loop`, remaining 100% compatible with standard Aseprite readers)
  - `BYTE[3]`: Tag RGB color (deprecated, still written for compatibility)
  - `BYTE`: Extra byte (`0`)
  - `STRING`: Tag name (UTF-8)

### 5.4 Palette Chunk (`0x2019`)
Stores the sprite's color swatches:
- `DWORD`: New palette size (total number of entries)
- `DWORD`: First color index to change
- `DWORD`: Last color index to change
- `BYTE[8]`: Reserved (`0`)
- For each palette entry (`First .. Last`):
  - `WORD`: Entry flags (`1` = Has color name string)
  - `BYTE`: Red (`0..255`)
  - `BYTE`: Green (`0..255`)
  - `BYTE`: Blue (`0..255`)
  - `BYTE`: Alpha (`0..255`)
  - Optional `STRING`: Color name (present only if bit `1` of Entry flags is set)

### 5.5 Slice Chunk (`0x2022`) & Tileset Chunk (`0x2023`)
- **Slice Chunk (`0x2022`)**: Defines named rectangular regions, 9-patch UI borders, and custom pivot coordinates (`Pivot X`, `Pivot Y`) relative to the slice origin.
- **Tileset Chunk (`0x2023`)**: Stores tileset ID, tile dimensions (`Width x Height`), and compressed tile imagery for tilemap layers.

---

## 6. GIMP Palette File Format Extension (`.gpl`)

Aseprite reads and writes GIMP Palette (`.gpl`) files extended with RGBA alpha values:

```text
GIMP Palette
Channels: RGBA
#
  0   0   0   0 Transparent
 15  12  28 255 Outline
 48  56  82 255 SteelShadow
 92 108 142 255 SteelBase
156 178 214 255 SteelLight
232 242 255 255 SteelSpec
```

The header must declare `Channels: RGBA`, and each color line lists `Red Green Blue Alpha Name`.

---

## 7. Zero-Allocation `goaseprite` Integration Pattern

When loading exported Aseprite JSON manifests and sprite sheet atlases with [SolarLune/goaseprite](https://github.com/SolarLune/goaseprite) in Ebitengine, pre-slice all frame sub-images during initialization and reuse a struct-level `ebiten.DrawImageOptions` value so `Draw()` performs zero heap allocations per frame:

```go
package entity

import (
	"fmt"
	"image"

	"github.com/SolarLune/goaseprite"
	"github.com/hajimehoshi/ebiten/v2"
)

type AsepriteActor struct {
	File   *goaseprite.File
	Frames []*ebiten.Image
	X, Y   float64
	drawOp ebiten.DrawImageOptions
}

func NewAsepriteActor(jsonBytes []byte, atlas *ebiten.Image) (*AsepriteActor, error) {
	if len(jsonBytes) == 0 {
		return nil, fmt.Errorf("sprite-design: empty Aseprite JSON manifest")
	}
	if atlas == nil {
		return nil, fmt.Errorf("sprite-design: nil atlas image")
	}
	file := goaseprite.Read(jsonBytes)
	if file == nil || len(file.Frames) == 0 {
		return nil, fmt.Errorf("sprite-design: failed to parse Aseprite frames from JSON")
	}

	// Pre-slice every frame at load time (zero SubImage allocations in Draw)
	frames := make([]*ebiten.Image, len(file.Frames))
	for i, f := range file.Frames {
		rect := image.Rect(f.X, f.Y, f.X+f.Width, f.Y+f.Height)
		frames[i] = atlas.SubImage(rect).(*ebiten.Image)
	}

	return &AsepriteActor{
		File:   file,
		Frames: frames,
	}, nil
}

func (a *AsepriteActor) Update(dt float32) {
	a.File.Update(dt)
}

func (a *AsepriteActor) Draw(screen *ebiten.Image) error {
	idx := a.File.CurrentFrame
	if idx < 0 || idx >= len(a.Frames) {
		return fmt.Errorf("sprite-design: frame index %d out of bounds [0, %d)", idx, len(a.Frames))
	}
	a.drawOp.GeoM.Reset()
	a.drawOp.GeoM.Translate(a.X, a.Y)
	screen.DrawImage(a.Frames[idx], &a.drawOp)
	return nil
}
```
