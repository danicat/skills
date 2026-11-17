// Copyright 2026 Daniela Petruzalek
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"math"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/hajimehoshi/ebiten/v2"
)

// PremultiplyRGBA converts straight 8-bit R, G, B, A channels into an
// Ebitengine-compliant premultiplied color.RGBA where R, G, B <= A.
func PremultiplyRGBA(r, g, b, a uint8) color.RGBA {
	if a == 0 {
		return color.RGBA{0, 0, 0, 0}
	}
	if a == 255 {
		return color.RGBA{R: r, G: g, B: b, A: 255}
	}
	af := uint16(a)
	return color.RGBA{
		R: uint8((uint16(r)*af + 127) / 255),
		G: uint8((uint16(g)*af + 127) / 255),
		B: uint8((uint16(b)*af + 127) / 255),
		A: a,
	}
}

// ValidatePremultipliedRGBA checks that every pixel in an *image.RGBA buffer
// obeys Ebitengine's premultiplied alpha invariant (R <= A, G <= A, B <= A).
func ValidatePremultipliedRGBA(img *image.RGBA) error {
	if img == nil {
		return fmt.Errorf("validate premultiplied RGBA: image is nil")
	}
	b := img.Bounds()
	for y := b.Min.Y; y < b.Max.Y; y++ {
		for x := b.Min.X; x < b.Max.X; x++ {
			c := img.RGBAAt(x, y)
			if c.R > c.A || c.G > c.A || c.B > c.A {
				return fmt.Errorf("invalid un-premultiplied pixel at (%d, %d): RGBA(%d, %d, %d, %d) violates R,G,B <= A",
					x, y, c.R, c.G, c.B, c.A)
			}
		}
	}
	return nil
}

// ParseHexColor parses "#RRGGBB" or "#RRGGBBAA" into a premultiplied color.RGBA.
func ParseHexColor(hexStr string) (color.RGBA, error) {
	s := strings.TrimSpace(hexStr)
	s = strings.TrimPrefix(s, "#")
	if len(s) != 6 && len(s) != 8 {
		return color.RGBA{}, fmt.Errorf("invalid hex color %q: expected #RRGGBB or #RRGGBBAA", hexStr)
	}
	rv, err := strconv.ParseUint(s[0:2], 16, 8)
	if err != nil {
		return color.RGBA{}, fmt.Errorf("invalid red hex in %q: %w", hexStr, err)
	}
	gv, err := strconv.ParseUint(s[2:4], 16, 8)
	if err != nil {
		return color.RGBA{}, fmt.Errorf("invalid green hex in %q: %w", hexStr, err)
	}
	bv, err := strconv.ParseUint(s[4:6], 16, 8)
	if err != nil {
		return color.RGBA{}, fmt.Errorf("invalid blue hex in %q: %w", hexStr, err)
	}
	av := uint64(255)
	if len(s) == 8 {
		av, err = strconv.ParseUint(s[6:8], 16, 8)
		if err != nil {
			return color.RGBA{}, fmt.Errorf("invalid alpha hex in %q: %w", hexStr, err)
		}
	}
	return PremultiplyRGBA(uint8(rv), uint8(gv), uint8(bv), uint8(av)), nil
}

// FormatHexColor formats a color.RGBA as "#RRGGBB".
func FormatHexColor(c color.RGBA) string {
	return fmt.Sprintf("#%02X%02X%02X", c.R, c.G, c.B)
}

// MaterialRamp defines a 4-step retro-HD color ramp from deep shadow to specular highlight.
// Index 0 = Deep Shadow, Index 1 = Base Midtone, Index 2 = Lit Surface, Index 3 = Specular Highlight.
type MaterialRamp [4]color.RGBA

// NamedRamp associates a ramp name with its 4 color steps.
type NamedRamp struct {
	Name  string       `json:"name"`
	Steps [4]string    `json:"steps"`
	Ramp  MaterialRamp `json:"-"`
}

// SampleMaterialRamp maps a normalized illumination value [0.0, 1.0] to a discrete pixel color.
func SampleMaterialRamp(ramp MaterialRamp, lightDot float64) color.RGBA {
	switch {
	case lightDot < 0.25:
		return ramp[0]
	case lightDot < 0.62:
		return ramp[1]
	case lightDot < 0.86:
		return ramp[2]
	default:
		return ramp[3]
	}
}

// Bayer2x2 is a normalized 2x2 ordered dithering threshold matrix centered around 0.
var Bayer2x2 = [2][2]float64{
	{-0.375, 0.125},
	{0.375, -0.125},
}

// Bayer4x4 is a normalized 4x4 ordered dithering threshold matrix centered around 0.
var Bayer4x4 = [4][4]float64{
	{-0.46875, 0.03125, -0.34375, 0.15625},
	{0.28125, -0.21875, 0.40625, -0.09375},
	{-0.28125, 0.21875, -0.40625, 0.09375},
	{0.46875, -0.03125, 0.34375, -0.15625},
}

// SampleMaterialRampDithered samples a 4-step MaterialRamp with optional Bayer ordered dithering.
func SampleMaterialRampDithered(ramp MaterialRamp, lightDot float64, x, y int, ditherMode string) color.RGBA {
	offset := 0.0
	switch ditherMode {
	case "bayer2":
		offset = Bayer2x2[y&1][x&1] * 0.18
	case "bayer4":
		offset = Bayer4x4[y&3][x&3] * 0.18
	}
	v := math.Max(0.0, math.Min(1.0, lightDot+offset))
	return SampleMaterialRamp(ramp, v)
}

// PaletteDef describes one of the 12 built-in Retro-HD palettes and its material adjustments.
type PaletteDef struct {
	Name        string
	Description string
	OutlineHex  string
	WarmShift   [3]int // RGB tint applied to base material ramps
	ContrastMul float64
}

var builtinPalettes = map[string]PaletteDef{
	"genesis": {
		Name:        "genesis",
		Description: "SEGA Mega Drive high-contrast 9-bit punchy arcade palette",
		OutlineHex:  "#0F0C1C",
		WarmShift:   [3]int{0, 0, 6},
		ContrastMul: 1.08,
	},
	"snes": {
		Name:        "snes",
		Description: "16-bit JRPG rich warm fantasy palette with hue-shifted shadows",
		OutlineHex:  "#141020",
		WarmShift:   [3]int{6, 2, -2},
		ContrastMul: 1.02,
	},
	"neogeo": {
		Name:        "neogeo",
		Description: "SNK arcade heavy metallic cabinet palette with bright speculars",
		OutlineHex:  "#0A0A14",
		WarmShift:   [3]int{8, 4, 0},
		ContrastMul: 1.12,
	},
	"cyber": {
		Name:        "cyber",
		Description: "Neon synthwave cyberpunk palette with deep indigo shadows",
		OutlineHex:  "#090619",
		WarmShift:   [3]int{-4, 2, 14},
		ContrastMul: 1.10,
	},
	"noir": {
		Name:        "noir",
		Description: "High-contrast gothic ink and cold moonlight palette",
		OutlineHex:  "#08080C",
		WarmShift:   [3]int{-8, -6, 4},
		ContrastMul: 1.15,
	},
	"forest": {
		Name:        "forest",
		Description: "Woodland moss, bark, and sun-dappled canopy palette",
		OutlineHex:  "#0D1712",
		WarmShift:   [3]int{-4, 8, -4},
		ContrastMul: 1.00,
	},
	"ember": {
		Name:        "ember",
		Description: "Volcanic magma, charred obsidian, and forge gold palette",
		OutlineHex:  "#1A0B0E",
		WarmShift:   [3]int{14, -2, -6},
		ContrastMul: 1.08,
	},
	"ocean": {
		Name:        "ocean",
		Description: "Abyssal trench teal, bioluminescent cyan, and seafoam palette",
		OutlineHex:  "#07131E",
		WarmShift:   [3]int{-8, 6, 12},
		ContrastMul: 1.04,
	},
	"pastel": {
		Name:        "pastel",
		Description: "Cozy storybook soft highlight and plum outline palette",
		OutlineHex:  "#23192D",
		WarmShift:   [3]int{10, 8, 12},
		ContrastMul: 0.94,
	},
	"bloodmoon": {
		Name:        "bloodmoon",
		Description: "Dark fantasy crimson eclipse, bone, and cursed steel palette",
		OutlineHex:  "#16070F",
		WarmShift:   [3]int{12, -8, 2},
		ContrastMul: 1.10,
	},
	"arcane": {
		Name:        "arcane",
		Description: "Astral violet, mystic rune gold, and mana crystal palette",
		OutlineHex:  "#120924",
		WarmShift:   [3]int{6, -4, 14},
		ContrastMul: 1.06,
	},
	"desert": {
		Name:        "desert",
		Description: "Sun-bleached sandstone, bronze, and lapis lazuli oasis palette",
		OutlineHex:  "#1C120C",
		WarmShift:   [3]int{12, 6, -8},
		ContrastMul: 1.03,
	},
}

var baseMaterialRampHex = map[string][4]string{
	"steel":    {"#2A2E45", "#546382", "#8FA3C7", "#DCE8FC"},
	"crimson":  {"#4A1228", "#8F1E38", "#D9384A", "#FF8A73"},
	"gold":     {"#5C3409", "#A86614", "#E8AD28", "#FFF294"},
	"flesh":    {"#5E2C28", "#A35743", "#E08B6B", "#FFD1B3"},
	"emerald":  {"#133E2B", "#227544", "#44B861", "#9BF09E"},
	"plasma":   {"#1D1B5E", "#2C5CC9", "#42B6F5", "#C7F9FF"},
	"obsidian": {"#14111F", "#28243D", "#474166", "#78719E"},
	"bone":     {"#4A3E42", "#877875", "#C7B8AC", "#F7F0E4"},
	"slime":    {"#194538", "#2B8A56", "#6CD968", "#D7FF94"},
	"leather":  {"#361B17", "#663626", "#9E5B3B", "#CFA37E"},
	"wood":     {"#2B1612", "#522C1E", "#824A2E", "#B57950"},
	"water":    {"#10264A", "#1D4E89", "#348AC7", "#8CE2FF"},
}

// ListPalettes returns the sorted list of 12 built-in palette names.
func ListPalettes() []string {
	out := make([]string, 0, len(builtinPalettes))
	for k := range builtinPalettes {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}

// GetPalette looks up a built-in palette by name.
func GetPalette(name string) (PaletteDef, bool) {
	p, ok := builtinPalettes[strings.ToLower(strings.TrimSpace(name))]
	return p, ok
}

// ListMaterialRamps returns the sorted list of 12 built-in 4-step material ramp names.
func ListMaterialRamps() []string {
	out := make([]string, 0, len(baseMaterialRampHex))
	for k := range baseMaterialRampHex {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}

func clampUint8(v int) uint8 {
	if v < 0 {
		return 0
	}
	if v > 255 {
		return 255
	}
	return uint8(v)
}

// BuildPaletteRamps builds the 12 default material ramps tinted for the given palette name.
func BuildPaletteRamps(paletteName string) map[string]MaterialRamp {
	pal, ok := GetPalette(paletteName)
	if !ok {
		pal = builtinPalettes["genesis"]
	}
	ramps := make(map[string]MaterialRamp, len(baseMaterialRampHex))
	for name, hexes := range baseMaterialRampHex {
		var mr MaterialRamp
		for i := 0; i < 4; i++ {
			c, _ := ParseHexColor(hexes[i])
			r := int(float64(int(c.R)-128)*pal.ContrastMul+128) + pal.WarmShift[0]
			g := int(float64(int(c.G)-128)*pal.ContrastMul+128) + pal.WarmShift[1]
			b := int(float64(int(c.B)-128)*pal.ContrastMul+128) + pal.WarmShift[2]
			mr[i] = PremultiplyRGBA(clampUint8(r), clampUint8(g), clampUint8(b), 255)
		}
		ramps[name] = mr
	}
	return ramps
}

// SDFCircle returns the signed distance from (px, py) to a circle at (cx, cy) with radius r.
func SDFCircle(px, py, cx, cy, r float64) float64 {
	return math.Hypot(px-cx, py-cy) - r
}

// SDFBox returns the signed distance from (px, py) to a rounded box centered at (cx, cy)
// with half-extents (halfW, halfH) and corner radius cornerR.
func SDFBox(px, py, cx, cy, halfW, halfH, cornerR float64) float64 {
	dx := math.Abs(px-cx) - halfW + cornerR
	dy := math.Abs(py-cy) - halfH + cornerR
	outside := math.Hypot(math.Max(dx, 0), math.Max(dy, 0))
	inside := math.Min(math.Max(dx, dy), 0)
	return outside + inside - cornerR
}

// SDFCapsule returns the signed distance from (px, py) to a line capsule between (ax, ay) and (bx, by).
func SDFCapsule(px, py, ax, ay, bx, by, r float64) float64 {
	pax, pay := px-ax, py-ay
	bax, bay := bx-ax, by-ay
	denom := bax*bax + bay*bay
	h := 0.0
	if denom > 1e-9 {
		h = math.Max(0.0, math.Min(1.0, (pax*bax+pay*bay)/denom))
	}
	return math.Hypot(pax-bax*h, pay-bay*h) - r
}

// SDFRing returns the signed distance from (px, py) to a ring centered at (cx, cy) with radius r and wall thickness.
func SDFRing(px, py, cx, cy, r, thickness float64) float64 {
	return math.Abs(math.Hypot(px-cx, py-cy)-r) - thickness*0.5
}

// SDFPolygon returns the signed distance from (px, py) to a closed 2D polygon with optional corner rounding.
func SDFPolygon(px, py float64, pts [][2]float64, roundR float64) float64 {
	n := len(pts)
	if n < 3 {
		return 1e6
	}
	d := (px-pts[0][0])*(px-pts[0][0]) + (py-pts[0][1])*(py-pts[0][1])
	s := 1.0
	j := n - 1
	for i := 0; i < n; i++ {
		ex := pts[j][0] - pts[i][0]
		ey := pts[j][1] - pts[i][1]
		wx := px - pts[i][0]
		wy := py - pts[i][1]
		denom := ex*ex + ey*ey
		h := 0.0
		if denom > 1e-9 {
			h = math.Max(0.0, math.Min(1.0, (wx*ex+wy*ey)/denom))
		}
		bx := wx - ex*h
		by := wy - ey*h
		distSq := bx*bx + by*by
		if distSq < d {
			d = distSq
		}
		c1 := py >= pts[i][1]
		c2 := py < pts[j][1]
		c3 := ex*wy > ey*wx
		if (c1 && c2 && c3) || (!c1 && !c2 && !c3) {
			s = -s
		}
		j = i
	}
	return s*math.Sqrt(d) - roundR
}

// SDFSmoothMin blends two signed distances d1 and d2 smoothly using smoothing factor k.
func SDFSmoothMin(d1, d2, k float64) float64 {
	if k <= 1e-6 {
		return math.Min(d1, d2)
	}
	h := math.Max(k-math.Abs(d1-d2), 0.0) / k
	return math.Min(d1, d2) - h*h*k*0.25
}

// Transform2D represents a 2D sprite or part transform with pivot, scale, squash, and rotation.
type Transform2D struct {
	X, Y             float64
	OriginX, OriginY float64
	ScaleX, ScaleY   float64
	Rotation         float64 // Radians
	Squash           float64 // Positive stretches Y and compresses X keeping area constant
}

// GetGeoM builds an ebiten.GeoM matrix applying pivot shift, volume-preserving squash-and-stretch,
// rotation, and world translation in the proper order.
func (t Transform2D) GetGeoM() ebiten.GeoM {
	var m ebiten.GeoM
	m.Translate(-t.OriginX, -t.OriginY)
	sx := t.ScaleX
	if sx == 0 {
		sx = 1.0
	}
	sy := t.ScaleY
	if sy == 0 {
		sy = 1.0
	}
	if t.Squash != 0 {
		factor := math.Max(0.25, 1.0+t.Squash)
		sy *= factor
		sx /= factor
	}
	m.Scale(sx, sy)
	if t.Rotation != 0 {
		m.Rotate(t.Rotation)
	}
	m.Translate(t.OriginX+t.X, t.OriginY+t.Y)
	return m
}

// InversePoint transforms a canvas point (px, py) into local untransformed part space.
func (t Transform2D) InversePoint(px, py float64) (float64, float64) {
	lx := px - (t.OriginX + t.X)
	ly := py - (t.OriginY + t.Y)
	if t.Rotation != 0 {
		cosR := math.Cos(-t.Rotation)
		sinR := math.Sin(-t.Rotation)
		rx := lx*cosR - ly*sinR
		ry := lx*sinR + ly*cosR
		lx, ly = rx, ry
	}
	sx := t.ScaleX
	if sx == 0 {
		sx = 1.0
	}
	sy := t.ScaleY
	if sy == 0 {
		sy = 1.0
	}
	if t.Squash != 0 {
		factor := math.Max(0.25, 1.0+t.Squash)
		sy *= factor
		sx /= factor
	}
	if math.Abs(sx) > 1e-6 {
		lx /= sx
	}
	if math.Abs(sy) > 1e-6 {
		ly /= sy
	}
	return lx + t.OriginX, ly + t.OriginY
}

// Easing functions for keyframe interpolation.
func EaseLinear(t float64) float64     { return t }
func EaseInQuad(t float64) float64     { return t * t }
func EaseOutQuad(t float64) float64    { return 1.0 - (1.0-t)*(1.0-t) }
func EaseInOutCubic(t float64) float64 {
	if t < 0.5 {
		return 4.0 * t * t * t
	}
	return 1.0 - math.Pow(-2.0*t+2.0, 3)/2.0
}
func EaseElasticOut(t float64) float64 {
	if t <= 0 {
		return 0
	}
	if t >= 1 {
		return 1
	}
	const c4 = (2.0 * math.Pi) / 3.0
	return math.Pow(2.0, -10.0*t)*math.Sin((t*10.0-0.75)*c4) + 1.0
}

// EvalEasing evaluates a named easing function at t in [0, 1].
func EvalEasing(name string, t float64) (float64, error) {
	t = math.Max(0.0, math.Min(1.0, t))
	switch strings.ToLower(strings.TrimSpace(name)) {
	case "", "linear":
		return EaseLinear(t), nil
	case "in_quad":
		return EaseInQuad(t), nil
	case "out_quad":
		return EaseOutQuad(t), nil
	case "in_out_cubic":
		return EaseInOutCubic(t), nil
	case "elastic_out":
		return EaseElasticOut(t), nil
	default:
		return 0, fmt.Errorf("unknown ease mode %q (supported: linear, in_quad, out_quad, in_out_cubic, elastic_out)", name)
	}
}

// LoopMode controls how an Ebitengine AnimationTag advances through its frames.
type LoopMode int

const (
	LoopForward LoopMode = iota
	LoopReverse
	LoopPingPong
	LoopOnce
)

// ParseLoopMode converts a DSL loop mode string to LoopMode.
// Accepts "loop" (standard) and "forward" (Aseprite alias) for LoopForward,
// "reverse" for LoopReverse, "pingpong" for LoopPingPong, and "once" for LoopOnce.
func ParseLoopMode(s string) (LoopMode, error) {
	switch strings.ToLower(strings.TrimSpace(s)) {
	case "", "loop", "forward":
		return LoopForward, nil
	case "reverse":
		return LoopReverse, nil
	case "pingpong":
		return LoopPingPong, nil
	case "once":
		return LoopOnce, nil
	default:
		return LoopForward, fmt.Errorf("invalid loop mode %q (supported: loop, once, pingpong, reverse)", s)
	}
}

// FormatLoopMode normalizes a loop mode string to its canonical DSL keyword ("loop", "once", "pingpong", "reverse").
func FormatLoopMode(s string) string {
	switch strings.ToLower(strings.TrimSpace(s)) {
	case "reverse":
		return "reverse"
	case "pingpong":
		return "pingpong"
	case "once":
		return "once"
	default:
		return "loop"
	}
}

// GridSpriteSheet slices a single atlas *ebiten.Image into uniform sub-image frames.
type GridSpriteSheet struct {
	Sheet       *ebiten.Image
	FrameWidth  int
	FrameHeight int
	Cols        int
	Rows        int
	Frames      []*ebiten.Image
}

// NewGridSpriteSheet validates and slices an *ebiten.Image atlas into uniform grid cells.
func NewGridSpriteSheet(sheet *ebiten.Image, frameW, frameH int) (*GridSpriteSheet, error) {
	if sheet == nil {
		return nil, fmt.Errorf("sprite sheet image is nil")
	}
	if frameW <= 0 || frameH <= 0 {
		return nil, fmt.Errorf("invalid frame dimensions %dx%d: must be positive", frameW, frameH)
	}
	b := sheet.Bounds()
	w, h := b.Dx(), b.Dy()
	if w < frameW || h < frameH {
		return nil, fmt.Errorf("sheet size %dx%d is smaller than single frame %dx%d", w, h, frameW, frameH)
	}
	if w%frameW != 0 || h%frameH != 0 {
		return nil, fmt.Errorf("sheet size %dx%d is not an exact multiple of frame size %dx%d", w, h, frameW, frameH)
	}
	cols := w / frameW
	rows := h / frameH
	frames := make([]*ebiten.Image, 0, cols*rows)
	for r := 0; r < rows; r++ {
		for c := 0; c < cols; c++ {
			x0 := b.Min.X + c*frameW
			y0 := b.Min.Y + r*frameH
			rect := image.Rect(x0, y0, x0+frameW, y0+frameH)
			sub, ok := sheet.SubImage(rect).(*ebiten.Image)
			if !ok || sub == nil {
				return nil, fmt.Errorf("failed to slice sub-image at col=%d row=%d", c, r)
			}
			frames = append(frames, sub)
		}
	}
	return &GridSpriteSheet{
		Sheet:       sheet,
		FrameWidth:  frameW,
		FrameHeight: frameH,
		Cols:        cols,
		Rows:        rows,
		Frames:      frames,
	}, nil
}

// Frame returns the sub-image for the given frame index, or nil if out of range.
func (s *GridSpriteSheet) Frame(index int) *ebiten.Image {
	if s == nil || index < 0 || index >= len(s.Frames) {
		return nil
	}
	return s.Frames[index]
}

// FrameCount returns the total number of sliced frames in the sheet.
func (s *GridSpriteSheet) FrameCount() int {
	if s == nil {
		return 0
	}
	return len(s.Frames)
}

// AnimationTag defines a named animation sequence across a range of frames.
// When LoopStartFrame > StartFrame, frames [StartFrame..LoopStartFrame-1] play once as a lead-in
// before looping across [LoopStartFrame..EndFrame].
type AnimationTag struct {
	Name           string
	StartFrame     int
	LoopStartFrame int
	EndFrame       int
	FrameDuration  time.Duration
	LoopMode       LoopMode
}

// AnimationController manages active animation tag playback and rendering for a GridSpriteSheet.
type AnimationController struct {
	Sheet        *GridSpriteSheet
	Tags         map[string]*AnimationTag
	ActiveTag    *AnimationTag
	CurrentFrame int
	Elapsed      time.Duration
	PingPongDir  int
	Finished     bool
	OnComplete   func(tagName string)
	drawOp       ebiten.DrawImageOptions
}

// NewAnimationController constructs a new AnimationController for a sliced GridSpriteSheet.
func NewAnimationController(sheet *GridSpriteSheet) *AnimationController {
	return &AnimationController{
		Sheet:       sheet,
		Tags:        make(map[string]*AnimationTag),
		PingPongDir: 1,
	}
}

// AddTag registers a named animation tag after validating frame bounds and timing.
func (ac *AnimationController) AddTag(name string, startFrame, endFrame int, frameDuration time.Duration, mode LoopMode) error {
	return ac.AddTagWithIntro(name, startFrame, startFrame, endFrame, frameDuration, mode)
}

// AddTagWithIntro registers a named animation tag where frames [startFrame..loopStartFrame-1]
// play once as a lead-in before looping across [loopStartFrame..endFrame].
func (ac *AnimationController) AddTagWithIntro(name string, startFrame, loopStartFrame, endFrame int, frameDuration time.Duration, mode LoopMode) error {
	if ac.Sheet == nil {
		return fmt.Errorf("cannot add tag %q: sprite sheet is nil", name)
	}
	if startFrame < 0 || endFrame < startFrame || endFrame >= ac.Sheet.FrameCount() {
		return fmt.Errorf("invalid frame range [%d..%d] for tag %q (sheet has %d frames)",
			startFrame, endFrame, name, ac.Sheet.FrameCount())
	}
	if loopStartFrame < startFrame || loopStartFrame > endFrame {
		loopStartFrame = startFrame
	}
	if frameDuration <= 0 {
		return fmt.Errorf("invalid frame duration %v for tag %q: must be > 0", frameDuration, name)
	}
	ac.Tags[name] = &AnimationTag{
		Name:           name,
		StartFrame:     startFrame,
		LoopStartFrame: loopStartFrame,
		EndFrame:       endFrame,
		FrameDuration:  frameDuration,
		LoopMode:       mode,
	}
	return nil
}

// Play switches to the named animation tag if it is not already playing.
func (ac *AnimationController) Play(name string) error {
	tag, ok := ac.Tags[name]
	if !ok {
		return fmt.Errorf("animation tag %q not found", name)
	}
	if ac.ActiveTag == tag && !ac.Finished {
		return nil
	}
	ac.ActiveTag = tag
	ac.Elapsed = 0
	ac.Finished = false
	ac.PingPongDir = 1
	if tag.LoopMode == LoopReverse {
		ac.CurrentFrame = tag.EndFrame
	} else {
		ac.CurrentFrame = tag.StartFrame
	}
	return nil
}

// Update advances the animation timer by dt.
func (ac *AnimationController) Update(dt time.Duration) {
	if ac.ActiveTag == nil || ac.Finished {
		return
	}
	tag := ac.ActiveTag
	if tag.StartFrame == tag.EndFrame {
		if tag.LoopMode == LoopOnce {
			ac.Elapsed += dt
			if ac.Elapsed >= tag.FrameDuration {
				ac.Elapsed -= tag.FrameDuration
				ac.Finished = true
				if ac.OnComplete != nil {
					ac.OnComplete(tag.Name)
				}
			}
		}
		return
	}
	loopStart := tag.LoopStartFrame
	if loopStart <= tag.StartFrame || loopStart > tag.EndFrame {
		loopStart = tag.StartFrame
	}
	ac.Elapsed += dt
	for ac.Elapsed >= tag.FrameDuration && !ac.Finished {
		ac.Elapsed -= tag.FrameDuration
		switch tag.LoopMode {
		case LoopForward:
			ac.CurrentFrame++
			if ac.CurrentFrame > tag.EndFrame {
				ac.CurrentFrame = loopStart
			}
		case LoopReverse:
			ac.CurrentFrame--
			if ac.CurrentFrame < loopStart {
				ac.CurrentFrame = tag.EndFrame
			}
		case LoopOnce:
			if ac.CurrentFrame < tag.EndFrame {
				ac.CurrentFrame++
			} else {
				ac.Finished = true
				if ac.OnComplete != nil {
					ac.OnComplete(tag.Name)
				}
			}
		case LoopPingPong:
			ac.CurrentFrame += ac.PingPongDir
			if ac.CurrentFrame >= tag.EndFrame {
				ac.CurrentFrame = tag.EndFrame
				ac.PingPongDir = -1
			} else if ac.CurrentFrame <= loopStart && ac.PingPongDir < 0 {
				ac.CurrentFrame = loopStart
				ac.PingPongDir = 1
			}
		}
	}
}

// Draw draws the current animation frame at (x, y) with optional horizontal flipping.
func (ac *AnimationController) Draw(screen *ebiten.Image, x, y float64, flipX bool) {
	if ac.Sheet == nil || screen == nil {
		return
	}
	frame := ac.Sheet.Frame(ac.CurrentFrame)
	if frame == nil {
		return
	}
	ac.drawOp.GeoM.Reset()
	if flipX {
		ac.drawOp.GeoM.Scale(-1, 1)
		ac.drawOp.GeoM.Translate(float64(ac.Sheet.FrameWidth), 0)
	}
	ac.drawOp.GeoM.Translate(math.Round(x), math.Round(y))
	screen.DrawImage(frame, &ac.drawOp)
}

// Declarative .sprite DSL AST and Compiler

// PrimitiveKind enumerates SDF and pixel drawing primitives inside a part block.
type PrimitiveKind string

const (
	PrimCircle  PrimitiveKind = "circle"
	PrimBox     PrimitiveKind = "box"
	PrimCapsule PrimitiveKind = "capsule"
	PrimRing    PrimitiveKind = "ring"
	PrimPoly    PrimitiveKind = "poly"
	PrimLine    PrimitiveKind = "line"
	PrimPixel   PrimitiveKind = "pixel"
)

// PrimitiveSpec defines one shape command inside a part block.
type PrimitiveSpec struct {
	Kind       PrimitiveKind
	LineNum    int
	CX, CY     float64
	BX, BY     float64
	HalfW      float64
	HalfH      float64
	Radius     float64
	Thick      float64
	Points     [][2]float64
	Op         string // "union", "smin", "sub"
	SmoothK    float64
	Ramp       string
	PixelW     int
	PixelH     int
	HasStep    bool
	Step       int // 0..3 explicit ramp step
}

// PartSpec represents a named, Z-ordered body or prop part composed of primitives.
type PartSpec struct {
	Name       string
	LineNum    int
	Ramp       string
	Z          int
	MirrorX    bool
	Hidden     bool // When true, hidden by default unless enabled by a pose with visible=true
	HasPivot   bool
	PivotX     float64
	PivotY     float64
	Dither     string // "none", "bayer2", "bayer4"
	Primitives []PrimitiveSpec
}

// ExprKind enumerates animation pose expression types.
type ExprKind int

const (
	ExprConst ExprKind = iota
	ExprRange
	ExprSin
	ExprCos
	ExprAbsSin
)

// PoseExpr represents a constant, range interpolation (a->b), or periodic wave function.
type PoseExpr struct {
	Kind  ExprKind
	Start float64
	End   float64
	Amp   float64
}

// Eval evaluates the expression at normalized progress t in [0, 1] and cycle progress cycleT in [0, 1).
func (e PoseExpr) Eval(t, cycleT float64, ease string) float64 {
	switch e.Kind {
	case ExprConst:
		return e.Start
	case ExprRange:
		et, err := EvalEasing(ease, t)
		if err != nil {
			et = t
		}
		return e.Start + (e.End-e.Start)*et
	case ExprSin:
		return e.Amp * math.Sin(2.0*math.Pi*cycleT)
	case ExprCos:
		return e.Amp * math.Cos(2.0*math.Pi*cycleT)
	case ExprAbsSin:
		return e.Amp * math.Abs(math.Sin(2.0*math.Pi*cycleT))
	default:
		return 0
	}
}

// PoseDirective specifies a keyframe or procedural pose transform for a part within an animation tag.
type PoseDirective struct {
	PartName   string
	LineNum    int
	FrameStart int // 0-indexed within the tag
	FrameEnd   int // inclusive, 0-indexed within the tag
	AllFrames  bool
	HasDX      bool
	DX         PoseExpr
	HasDY      bool
	DY         PoseExpr
	HasRot     bool
	Rot        PoseExpr // degrees
	HasScale   bool
	ScaleX     float64
	ScaleY     float64
	HasSquash  bool
	Squash     PoseExpr
	HasVisible bool
	Visible    bool
	Ease       string
}

// TagSpec defines a named animation tag in the .sprite DSL.
type TagSpec struct {
	Name          string
	LineNum       int
	Frames        int
	HasFrameRange bool
	FromFrame     int
	LoopFromFrame int
	ToFrame       int
	DurationMs    int
	Loop          string
	Poses         []PoseDirective
}

// SpriteSpec is the parsed AST of a .sprite DSL source file.
type SpriteSpec struct {
	Title             string
	Type              string // "sprite" or "tileset"
	SheetPath         string // Optional external .png or .aseprite sprite sheet path (container mode)
	BaseDir           string // Base directory of the .sprite file for resolving relative SheetPath
	GridCols          int    // Optional grid columns when SheetPath is set
	GridRows          int    // Optional grid rows when SheetPath is set
	Width             int
	Height            int
	DefaultDurationMs int // Sprite-wide default frame duration in ms (default 100ms = 10 FPS)
	Palette           string
	OutlineMode       string // "color" or "none"
	OutlineRGBA       color.RGBA
	LightX            float64
	LightY            float64
	CustomRamps       map[string]MaterialRamp
	Parts             []*PartSpec
	Tags              []*TagSpec
}

// CompiledTag describes a tag's frame range and metadata in a CompiledSprite.
type CompiledTag struct {
	Name          string `json:"name"`
	FromFrame     int    `json:"fromFrame"`
	LoopFromFrame int    `json:"loopFromFrame,omitempty"`
	ToFrame       int    `json:"toFrame"`
	Frames        int    `json:"frames"`
	DurationMs    int    `json:"durationMs"`
	Loop          string `json:"loop"`
}

// PartSummary describes a part's metadata for JSON reporting.
type PartSummary struct {
	Name           string `json:"name"`
	Ramp           string `json:"ramp"`
	Z              int    `json:"z"`
	PrimitiveCount int    `json:"primitiveCount"`
}

// CompiledSprite holds the rendered frames, packed grid sheet, and metadata produced by compiling a .sprite spec.
type CompiledSprite struct {
	Spec           *SpriteSpec
	Title          string
	Type           string
	FrameW         int
	FrameH         int
	Palette        string
	Frames         []*image.RGBA
	FrameDurations []int
	Tags           []CompiledTag
	Parts          []PartSummary
	PaletteColors  []color.RGBA
	SheetRGBA      *image.RGBA
	SheetCols      int
	SheetRows      int
}

// ToEbitenController converts a CompiledSprite into an Ebitengine AnimationController ready for playback.
func (cs *CompiledSprite) ToEbitenController() (*AnimationController, error) {
	if cs == nil || cs.SheetRGBA == nil {
		return nil, fmt.Errorf("compiled sprite or SheetRGBA is nil")
	}
	if err := ValidatePremultipliedRGBA(cs.SheetRGBA); err != nil {
		return nil, err
	}
	ebitenImg := ebiten.NewImageFromImage(cs.SheetRGBA)
	grid, err := NewGridSpriteSheet(ebitenImg, cs.FrameW, cs.FrameH)
	if err != nil {
		return nil, err
	}
	ctrl := NewAnimationController(grid)
	for _, t := range cs.Tags {
		mode, err := ParseLoopMode(t.Loop)
		if err != nil {
			return nil, err
		}
		dur := time.Duration(t.DurationMs) * time.Millisecond
		if dur <= 0 {
			dur = 100 * time.Millisecond
		}
		if err := ctrl.AddTagWithIntro(t.Name, t.FromFrame, t.LoopFromFrame, t.ToFrame, dur, mode); err != nil {
			return nil, err
		}
	}
	if len(cs.Tags) > 0 {
		_ = ctrl.Play(cs.Tags[0].Name)
	}
	return ctrl, nil
}

// LoadSpriteFile reads and parses a .sprite DSL file from disk.
func LoadSpriteFile(path string) (*SpriteSpec, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read sprite DSL file %q: %w", path, err)
	}
	spec, err := ParseSpriteDSL(string(data))
	if err != nil {
		return nil, err
	}
	spec.BaseDir = filepath.Dir(path)
	return spec, nil
}

// CompileSpriteDSL parses and compiles a .sprite DSL string into a CompiledSprite.
func CompileSpriteDSL(dsl string) (*CompiledSprite, error) {
	spec, err := ParseSpriteDSL(dsl)
	if err != nil {
		return nil, err
	}
	return CompileSprite(spec)
}

func parsePairFloat(token string) (float64, float64, error) {
	parts := strings.Split(token, ",")
	if len(parts) != 2 {
		return 0, 0, fmt.Errorf("expected <x>,<y> pair, got %q", token)
	}
	x, err := strconv.ParseFloat(strings.TrimSpace(parts[0]), 64)
	if err != nil {
		return 0, 0, fmt.Errorf("invalid first number in %q: %w", token, err)
	}
	y, err := strconv.ParseFloat(strings.TrimSpace(parts[1]), 64)
	if err != nil {
		return 0, 0, fmt.Errorf("invalid second number in %q: %w", token, err)
	}
	return x, y, nil
}

func parsePoseExpr(val string) (PoseExpr, error) {
	s := strings.TrimSpace(val)
	if strings.HasPrefix(s, "sin(") && strings.HasSuffix(s, ")") {
		inner := s[4 : len(s)-1]
		amp, err := strconv.ParseFloat(strings.TrimSpace(inner), 64)
		if err != nil {
			return PoseExpr{}, fmt.Errorf("invalid sin() amplitude %q: %w", s, err)
		}
		return PoseExpr{Kind: ExprSin, Amp: amp}, nil
	}
	if strings.HasPrefix(s, "cos(") && strings.HasSuffix(s, ")") {
		inner := s[4 : len(s)-1]
		amp, err := strconv.ParseFloat(strings.TrimSpace(inner), 64)
		if err != nil {
			return PoseExpr{}, fmt.Errorf("invalid cos() amplitude %q: %w", s, err)
		}
		return PoseExpr{Kind: ExprCos, Amp: amp}, nil
	}
	if strings.HasPrefix(s, "abs_sin(") && strings.HasSuffix(s, ")") {
		inner := s[8 : len(s)-1]
		amp, err := strconv.ParseFloat(strings.TrimSpace(inner), 64)
		if err != nil {
			return PoseExpr{}, fmt.Errorf("invalid abs_sin() amplitude %q: %w", s, err)
		}
		return PoseExpr{Kind: ExprAbsSin, Amp: amp}, nil
	}
	if idx := strings.Index(s, "->"); idx >= 0 {
		a, err := strconv.ParseFloat(strings.TrimSpace(s[:idx]), 64)
		if err != nil {
			return PoseExpr{}, fmt.Errorf("invalid range start in %q: %w", s, err)
		}
		b, err := strconv.ParseFloat(strings.TrimSpace(s[idx+2:]), 64)
		if err != nil {
			return PoseExpr{}, fmt.Errorf("invalid range end in %q: %w", s, err)
		}
		return PoseExpr{Kind: ExprRange, Start: a, End: b}, nil
	}
	v, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return PoseExpr{}, fmt.Errorf("invalid numeric expression %q: %w", s, err)
	}
	return PoseExpr{Kind: ExprConst, Start: v, End: v}, nil
}

// ParseSpriteDSL parses a .sprite DSL string into a validated SpriteSpec AST.
// Returns detailed line-indexed error messages on any syntax or parameter error.
func ParseSpriteDSL(dsl string) (*SpriteSpec, error) {
	defaultOutline, _ := ParseHexColor("#0F0C1C")
	spec := &SpriteSpec{
		Title:             "Untitled Sprite",
		Type:              "sprite",
		Width:             32,
		Height:            32,
		DefaultDurationMs: 100,
		Palette:           "genesis",
		OutlineMode:       "default",
		OutlineRGBA:       defaultOutline,
		LightX:            -0.5,
		LightY:            -0.7,
		CustomRamps:       make(map[string]MaterialRamp),
	}

	// Normalize default light vector
	lMag := math.Hypot(spec.LightX, spec.LightY)
	spec.LightX /= lMag
	spec.LightY /= lMag

	var currentPart *PartSpec
	var currentTag *TagSpec

	lines := strings.Split(dsl, "\n")
	for idx, rawLine := range lines {
		lineNum := idx + 1
		// Strip comments starting with // or # (unless # is preceded by space/equals as a hex literal)
		line := stripDSLComment(rawLine)
		trimmed := strings.TrimSpace(line)
		if trimmed == "" {
			continue
		}

		isIndented := len(line) > 0 && (line[0] == ' ' || line[0] == '\t')
		if !isIndented {
			currentPart = nil
			currentTag = nil
		}

		tokens := tokenizeDSLLine(trimmed)
		if len(tokens) == 0 {
			continue
		}
		head := strings.ToLower(tokens[0])

		// Handle top-level headers and blocks
		switch head {
		case "title":
			if len(tokens) < 2 {
				return nil, fmt.Errorf("line %d: title directive requires a quoted string", lineNum)
			}
			firstQuote := strings.Index(trimmed, "\"")
			lastQuote := strings.LastIndex(trimmed, "\"")
			if firstQuote >= 0 && lastQuote > firstQuote {
				spec.Title = trimmed[firstQuote+1 : lastQuote]
			} else {
				spec.Title = strings.Join(tokens[1:], " ")
			}

		case "type":
			if len(tokens) != 2 {
				return nil, fmt.Errorf("line %d: type requires 'sprite' or 'tileset'", lineNum)
			}
			tVal := strings.ToLower(tokens[1])
			switch tVal {
			case "sprite", "character", "prop", "vfx", "ui":
				spec.Type = "sprite"
			case "tileset", "tile":
				spec.Type = "tileset"
			default:
				return nil, fmt.Errorf("line %d: unsupported type %q (expected 'sprite' or 'tileset')", lineNum, tokens[1])
			}

		case "sheet", "image":
			if len(tokens) < 2 {
				return nil, fmt.Errorf("line %d: sheet directive requires a file path", lineNum)
			}
			firstQuote := strings.Index(trimmed, "\"")
			lastQuote := strings.LastIndex(trimmed, "\"")
			if firstQuote >= 0 && lastQuote > firstQuote {
				spec.SheetPath = strings.TrimSpace(trimmed[firstQuote+1 : lastQuote])
			} else {
				spec.SheetPath = strings.Trim(tokens[1], "\"'")
			}
			if spec.SheetPath == "" {
				return nil, fmt.Errorf("line %d: sheet path cannot be empty", lineNum)
			}

		case "grid":
			if len(tokens) != 2 {
				return nil, fmt.Errorf("line %d: grid requires <Cols>x<Rows> (e.g. grid 4x8)", lineNum)
			}
			dims := strings.Split(strings.ToLower(tokens[1]), "x")
			if len(dims) != 2 {
				return nil, fmt.Errorf("line %d: invalid grid %q (expected <Cols>x<Rows>)", lineNum, tokens[1])
			}
			gc, err1 := strconv.Atoi(dims[0])
			gr, err2 := strconv.Atoi(dims[1])
			if err1 != nil || err2 != nil || gc < 1 || gc > 128 || gr < 1 || gr > 128 {
				return nil, fmt.Errorf("line %d: invalid grid %q: cols and rows must be in 1..128", lineNum, tokens[1])
			}
			spec.GridCols = gc
			spec.GridRows = gr

		case "size":
			if len(tokens) != 2 {
				return nil, fmt.Errorf("line %d: size requires <W>x<H> (e.g. size 32x32)", lineNum)
			}
			dims := strings.Split(strings.ToLower(tokens[1]), "x")
			if len(dims) != 2 {
				return nil, fmt.Errorf("line %d: invalid size %q (expected <W>x<H>)", lineNum, tokens[1])
			}
			w, err1 := strconv.Atoi(dims[0])
			h, err2 := strconv.Atoi(dims[1])
			if err1 != nil || err2 != nil || w < 8 || w > 1024 || h < 8 || h > 1024 {
				return nil, fmt.Errorf("line %d: invalid size %q: width and height must be integers in 8..1024", lineNum, tokens[1])
			}
			spec.Width = w
			spec.Height = h

		case "fps":
			if len(tokens) != 2 {
				return nil, fmt.Errorf("line %d: fps requires a positive number (e.g. fps 10)", lineNum)
			}
			fps, err := strconv.ParseFloat(tokens[1], 64)
			if err != nil || fps <= 0 || fps > 240 {
				return nil, fmt.Errorf("line %d: invalid fps %q (must be > 0 and <= 240)", lineNum, tokens[1])
			}
			spec.DefaultDurationMs = int(math.Round(1000.0 / fps))

		case "duration":
			if len(tokens) != 2 {
				return nil, fmt.Errorf("line %d: duration requires a millisecond value (e.g. duration 100ms)", lineNum)
			}
			dStr := strings.TrimSuffix(strings.ToLower(tokens[1]), "ms")
			d, err := strconv.Atoi(dStr)
			if err != nil || d <= 0 {
				return nil, fmt.Errorf("line %d: invalid duration %q (must be > 0 ms)", lineNum, tokens[1])
			}
			spec.DefaultDurationMs = d

		case "palette":
			if len(tokens) != 2 {
				return nil, fmt.Errorf("line %d: palette requires a palette name", lineNum)
			}
			pName := strings.ToLower(tokens[1])
			pDef, ok := GetPalette(pName)
			if !ok {
				return nil, fmt.Errorf("line %d: unknown palette %q (supported: %s)", lineNum, tokens[1], strings.Join(ListPalettes(), ", "))
			}
			spec.Palette = pName
			if spec.OutlineMode == "default" {
				if c, err := ParseHexColor(pDef.OutlineHex); err == nil {
					spec.OutlineRGBA = c
				}
			}

		case "outline":
			if len(tokens) != 2 {
				return nil, fmt.Errorf("line %d: outline requires 'none' or #<RRGGBB>", lineNum)
			}
			if strings.ToLower(tokens[1]) == "none" {
				spec.OutlineMode = "none"
			} else {
				c, err := ParseHexColor(tokens[1])
				if err != nil {
					return nil, fmt.Errorf("line %d: invalid outline color: %w", lineNum, err)
				}
				spec.OutlineMode = "color"
				spec.OutlineRGBA = c
			}

		case "light":
			if len(tokens) != 2 {
				return nil, fmt.Errorf("line %d: light requires <dx>,<dy> vector", lineNum)
			}
			lx, ly, err := parsePairFloat(tokens[1])
			if err != nil {
				return nil, fmt.Errorf("line %d: invalid light vector: %w", lineNum, err)
			}
			mag := math.Hypot(lx, ly)
			if mag < 1e-6 {
				return nil, fmt.Errorf("line %d: light vector cannot be zero", lineNum)
			}
			spec.LightX = lx / mag
			spec.LightY = ly / mag

		case "ramp":
			if len(tokens) != 6 {
				return nil, fmt.Errorf("line %d: ramp requires <name> #<shadow> #<base> #<light> #<spec>", lineNum)
			}
			rName := strings.ToLower(tokens[1])
			var mr MaterialRamp
			for i := 0; i < 4; i++ {
				c, err := ParseHexColor(tokens[2+i])
				if err != nil {
					return nil, fmt.Errorf("line %d: ramp %q step %d: %w", lineNum, rName, i, err)
				}
				mr[i] = c
			}
			spec.CustomRamps[rName] = mr

		case "part":
			currentTag = nil
			p, err := parsePartHeader(lineNum, tokens)
			if err != nil {
				return nil, err
			}
			spec.Parts = append(spec.Parts, p)
			currentPart = p

		case "tag":
			currentPart = nil
			t, err := parseTagHeader(lineNum, tokens, spec.DefaultDurationMs)
			if err != nil {
				return nil, err
			}
			spec.Tags = append(spec.Tags, t)
			currentTag = t

		case "circle", "box", "capsule", "ring", "poly", "line", "pixel", "dither":
			if currentPart == nil {
				return nil, fmt.Errorf("line %d: primitive %q must be indented inside a 'part' block", lineNum, head)
			}
			if head == "dither" {
				if len(tokens) != 2 {
					return nil, fmt.Errorf("line %d: dither requires none, bayer2, or bayer4", lineNum)
				}
				dm := strings.ToLower(tokens[1])
				if dm != "none" && dm != "bayer2" && dm != "bayer4" {
					return nil, fmt.Errorf("line %d: invalid dither mode %q (expected none, bayer2, or bayer4)", lineNum, tokens[1])
				}
				currentPart.Dither = dm
				continue
			}
			prim, err := parsePrimitive(lineNum, tokens, currentPart.Ramp)
			if err != nil {
				return nil, err
			}
			currentPart.Primitives = append(currentPart.Primitives, prim)

		case "pose":
			if currentTag == nil {
				return nil, fmt.Errorf("line %d: 'pose' directive must be indented inside a 'tag' block", lineNum)
			}
			pose, err := parsePoseDirective(lineNum, tokens, currentTag.Frames)
			if err != nil {
				return nil, err
			}
			currentTag.Poses = append(currentTag.Poses, pose)

		default:
			return nil, fmt.Errorf("line %d: unknown directive %q", lineNum, tokens[0])
		}
	}

	if len(spec.Parts) == 0 && spec.SheetPath == "" {
		return nil, fmt.Errorf("sprite specification has no 'part' blocks or 'sheet' defined")
	}

	// Default outline for tileset is none unless explicitly set
	if spec.Type == "tileset" && spec.OutlineMode == "default" {
		spec.OutlineMode = "none"
	} else if spec.OutlineMode == "default" {
		spec.OutlineMode = "color"
	}

	// Default tag if none specified
	if len(spec.Tags) == 0 {
		dur := spec.DefaultDurationMs
		if dur <= 0 {
			dur = 100
		}
		spec.Tags = append(spec.Tags, &TagSpec{
			Name:       "idle",
			LineNum:    1,
			Frames:     1,
			DurationMs: dur,
			Loop:       "loop",
		})
	}

	// Validate all referenced ramps and parts
	availableRamps := BuildPaletteRamps(spec.Palette)
	for k, v := range spec.CustomRamps {
		availableRamps[k] = v
	}
	partNames := make(map[string]bool, len(spec.Parts))
	for _, p := range spec.Parts {
		partNames[p.Name] = true
		if len(p.Primitives) == 0 {
			return nil, fmt.Errorf("line %d: part %q has no primitives", p.LineNum, p.Name)
		}
		if _, ok := availableRamps[p.Ramp]; !ok {
			return nil, fmt.Errorf("line %d: part %q references unknown material ramp %q", p.LineNum, p.Name, p.Ramp)
		}
		for _, pr := range p.Primitives {
			if _, ok := availableRamps[pr.Ramp]; !ok {
				return nil, fmt.Errorf("line %d: primitive %q in part %q references unknown material ramp %q", pr.LineNum, pr.Kind, p.Name, pr.Ramp)
			}
		}
	}
	for _, t := range spec.Tags {
		for _, ps := range t.Poses {
			if !partNames[ps.PartName] {
				return nil, fmt.Errorf("line %d: pose in tag %q references unknown part %q", ps.LineNum, t.Name, ps.PartName)
			}
		}
	}

	return spec, nil
}

func stripDSLComment(raw string) string {
	inQuotes := false
	for i := 0; i < len(raw); i++ {
		ch := raw[i]
		if ch == '"' {
			inQuotes = !inQuotes
			continue
		}
		if inQuotes {
			continue
		}
		if ch == '/' && i+1 < len(raw) && raw[i+1] == '/' {
			return raw[:i]
		}
		if ch == '#' {
			// Treat # at start of trimmed line or after whitespace as comment ONLY if not followed by 6/8 hex digits
			if i == 0 || (raw[i-1] != '=' && !isHexColorToken(raw[i:])) {
				if !isHexColorToken(raw[i:]) {
					return raw[:i]
				}
			}
		}
	}
	return raw
}

func isHexColorToken(s string) bool {
	if len(s) < 7 || s[0] != '#' {
		return false
	}
	count := 0
	for i := 1; i < len(s) && i <= 8; i++ {
		c := s[i]
		if (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F') {
			count++
		} else {
			break
		}
	}
	return count == 6 || count == 8
}

func tokenizeDSLLine(s string) []string {
	var out []string
	var cur strings.Builder
	inQuotes := false
	for i := 0; i < len(s); i++ {
		ch := s[i]
		if ch == '"' {
			inQuotes = !inQuotes
			cur.WriteByte(ch)
			continue
		}
		if !inQuotes && (ch == ' ' || ch == '\t') {
			if cur.Len() > 0 {
				out = append(out, cur.String())
				cur.Reset()
			}
			continue
		}
		cur.WriteByte(ch)
	}
	if cur.Len() > 0 {
		out = append(out, cur.String())
	}
	return out
}

func parsePartHeader(lineNum int, tokens []string) (*PartSpec, error) {
	if len(tokens) < 2 {
		return nil, fmt.Errorf("line %d: part directive requires a name", lineNum)
	}
	name := strings.TrimSuffix(tokens[1], ":")
	p := &PartSpec{
		Name:    name,
		LineNum: lineNum,
		Ramp:    "steel",
		Z:       0,
		Dither:  "none",
	}
	for _, tok := range tokens[2:] {
		tok = strings.TrimSuffix(tok, ":")
		if tok == "" {
			continue
		}
		kv := strings.SplitN(tok, "=", 2)
		if len(kv) != 2 {
			return nil, fmt.Errorf("line %d: invalid part attribute %q (expected key=value)", lineNum, tok)
		}
		key, val := strings.ToLower(kv[0]), kv[1]
		switch key {
		case "ramp":
			p.Ramp = strings.ToLower(val)
		case "z":
			z, err := strconv.Atoi(val)
			if err != nil {
				return nil, fmt.Errorf("line %d: invalid z value %q: %w", lineNum, val, err)
			}
			p.Z = z
		case "mirror_x":
			b, err := strconv.ParseBool(val)
			if err != nil {
				return nil, fmt.Errorf("line %d: invalid mirror_x value %q: %w", lineNum, val, err)
			}
			p.MirrorX = b
		case "hidden":
			b, err := strconv.ParseBool(val)
			if err != nil {
				return nil, fmt.Errorf("line %d: invalid hidden value %q: %w", lineNum, val, err)
			}
			p.Hidden = b
		case "pivot":
			px, py, err := parsePairFloat(val)
			if err != nil {
				return nil, fmt.Errorf("line %d: invalid pivot %q: %w", lineNum, val, err)
			}
			p.HasPivot = true
			p.PivotX = px
			p.PivotY = py
		case "dither":
			dm := strings.ToLower(val)
			if dm != "none" && dm != "bayer2" && dm != "bayer4" {
				return nil, fmt.Errorf("line %d: invalid dither mode %q", lineNum, val)
			}
			p.Dither = dm
		default:
			return nil, fmt.Errorf("line %d: unknown part attribute %q", lineNum, key)
		}
	}
	return p, nil
}

func parsePrimitive(lineNum int, tokens []string, defaultRamp string) (PrimitiveSpec, error) {
	kind := PrimitiveKind(strings.ToLower(tokens[0]))
	pr := PrimitiveSpec{
		Kind:    kind,
		LineNum: lineNum,
		Op:      "union",
		SmoothK: 2.0,
		Ramp:    defaultRamp,
		Thick:   1.5,
		PixelW:  1,
		PixelH:  1,
	}

	var posArgs []string
	var kvArgs [][2]string
	for _, tok := range tokens[1:] {
		if idx := strings.IndexByte(tok, '='); idx > 0 {
			kvArgs = append(kvArgs, [2]string{strings.ToLower(tok[:idx]), tok[idx+1:]})
		} else {
			posArgs = append(posArgs, tok)
		}
	}

	for _, kv := range kvArgs {
		k, v := kv[0], kv[1]
		switch k {
		case "r":
			f, err := strconv.ParseFloat(v, 64)
			if err != nil || f < 0 {
				return pr, fmt.Errorf("line %d: invalid radius r=%q", lineNum, v)
			}
			pr.Radius = f
		case "thick":
			f, err := strconv.ParseFloat(v, 64)
			if err != nil || f <= 0 {
				return pr, fmt.Errorf("line %d: invalid thickness thick=%q", lineNum, v)
			}
			pr.Thick = f
		case "op":
			op := strings.ToLower(v)
			if op != "union" && op != "smin" && op != "sub" {
				return pr, fmt.Errorf("line %d: invalid CSG op %q (supported: union, smin, sub)", lineNum, v)
			}
			pr.Op = op
		case "k":
			f, err := strconv.ParseFloat(v, 64)
			if err != nil || f < 0 {
				return pr, fmt.Errorf("line %d: invalid smooth factor k=%q", lineNum, v)
			}
			pr.SmoothK = f
		case "ramp":
			pr.Ramp = strings.ToLower(v)
		case "w":
			w, err := strconv.Atoi(v)
			if err != nil || w <= 0 {
				return pr, fmt.Errorf("line %d: invalid pixel width w=%q", lineNum, v)
			}
			pr.PixelW = w
		case "h":
			h, err := strconv.Atoi(v)
			if err != nil || h <= 0 {
				return pr, fmt.Errorf("line %d: invalid pixel height h=%q", lineNum, v)
			}
			pr.PixelH = h
		case "step":
			st, err := strconv.Atoi(v)
			if err != nil || st < 0 || st > 3 {
				return pr, fmt.Errorf("line %d: invalid ramp step=%q (expected 0..3)", lineNum, v)
			}
			pr.HasStep = true
			pr.Step = st
		default:
			return pr, fmt.Errorf("line %d: unknown primitive attribute %q", lineNum, k)
		}
	}

	switch kind {
	case PrimCircle:
		if len(posArgs) != 1 {
			return pr, fmt.Errorf("line %d: circle requires <cx>,<cy> and r=<radius>", lineNum)
		}
		cx, cy, err := parsePairFloat(posArgs[0])
		if err != nil {
			return pr, fmt.Errorf("line %d: circle center: %w", lineNum, err)
		}
		if pr.Radius <= 0 {
			return pr, fmt.Errorf("line %d: circle requires positive r=<radius>", lineNum)
		}
		pr.CX, pr.CY = cx, cy

	case PrimBox:
		if len(posArgs) != 2 {
			return pr, fmt.Errorf("line %d: box requires <cx>,<cy> and <halfW>,<halfH>", lineNum)
		}
		cx, cy, err := parsePairFloat(posArgs[0])
		if err != nil {
			return pr, fmt.Errorf("line %d: box center: %w", lineNum, err)
		}
		hw, hh, err := parsePairFloat(posArgs[1])
		if err != nil || hw <= 0 || hh <= 0 {
			return pr, fmt.Errorf("line %d: box half-extents must be positive <halfW>,<halfH>", lineNum)
		}
		pr.CX, pr.CY = cx, cy
		pr.HalfW, pr.HalfH = hw, hh

	case PrimCapsule:
		if len(posArgs) != 2 {
			return pr, fmt.Errorf("line %d: capsule requires <ax>,<ay> <bx>,<by> and r=<radius>", lineNum)
		}
		ax, ay, err := parsePairFloat(posArgs[0])
		if err != nil {
			return pr, fmt.Errorf("line %d: capsule start: %w", lineNum, err)
		}
		bx, by, err := parsePairFloat(posArgs[1])
		if err != nil {
			return pr, fmt.Errorf("line %d: capsule end: %w", lineNum, err)
		}
		if pr.Radius <= 0 {
			return pr, fmt.Errorf("line %d: capsule requires positive r=<radius>", lineNum)
		}
		pr.CX, pr.CY = ax, ay
		pr.BX, pr.BY = bx, by

	case PrimRing:
		if len(posArgs) != 1 {
			return pr, fmt.Errorf("line %d: ring requires <cx>,<cy>, r=<radius>, and thick=<thickness>", lineNum)
		}
		cx, cy, err := parsePairFloat(posArgs[0])
		if err != nil {
			return pr, fmt.Errorf("line %d: ring center: %w", lineNum, err)
		}
		if pr.Radius <= 0 {
			return pr, fmt.Errorf("line %d: ring requires positive r=<radius>", lineNum)
		}
		pr.CX, pr.CY = cx, cy

	case PrimPoly:
		if len(posArgs) < 3 {
			return pr, fmt.Errorf("line %d: poly requires at least 3 <x>,<y> vertices", lineNum)
		}
		pts := make([][2]float64, 0, len(posArgs))
		for _, pa := range posArgs {
			px, py, err := parsePairFloat(pa)
			if err != nil {
				return pr, fmt.Errorf("line %d: poly vertex %q: %w", lineNum, pa, err)
			}
			pts = append(pts, [2]float64{px, py})
		}
		pr.Points = pts

	case PrimLine:
		if len(posArgs) != 2 {
			return pr, fmt.Errorf("line %d: line requires <ax>,<ay> <bx>,<by>", lineNum)
		}
		ax, ay, err := parsePairFloat(posArgs[0])
		if err != nil {
			return pr, fmt.Errorf("line %d: line start: %w", lineNum, err)
		}
		bx, by, err := parsePairFloat(posArgs[1])
		if err != nil {
			return pr, fmt.Errorf("line %d: line end: %w", lineNum, err)
		}
		pr.CX, pr.CY = ax, ay
		pr.BX, pr.BY = bx, by
		pr.Radius = pr.Thick * 0.5

	case PrimPixel:
		if len(posArgs) != 1 {
			return pr, fmt.Errorf("line %d: pixel requires <x>,<y>", lineNum)
		}
		px, py, err := parsePairFloat(posArgs[0])
		if err != nil {
			return pr, fmt.Errorf("line %d: pixel coords: %w", lineNum, err)
		}
		pr.CX, pr.CY = px, py
	}

	return pr, nil
}

func parseTagHeader(lineNum int, tokens []string, defaultDurationMs int) (*TagSpec, error) {
	if len(tokens) < 2 {
		return nil, fmt.Errorf("line %d: tag directive requires a name", lineNum)
	}
	if defaultDurationMs <= 0 {
		defaultDurationMs = 100
	}
	name := strings.TrimSuffix(tokens[1], ":")
	t := &TagSpec{
		Name:       name,
		LineNum:    lineNum,
		Frames:     1,
		DurationMs: defaultDurationMs,
		Loop:       "loop",
	}
	for _, tok := range tokens[2:] {
		tok = strings.TrimSuffix(strings.TrimSuffix(tok, ":"), ",")
		if tok == "" {
			continue
		}
		kv := strings.SplitN(tok, "=", 2)
		if len(kv) != 2 {
			lowTok := strings.ToLower(tok)
			if idx := strings.Index(lowTok, ".."); idx >= 0 {
				fromF, err1 := strconv.Atoi(lowTok[:idx])
				toF, err2 := strconv.Atoi(lowTok[idx+2:])
				if err1 != nil || err2 != nil || fromF < 0 || toF < fromF {
					return nil, fmt.Errorf("line %d: invalid tag frame range %q", lineNum, tok)
				}
				if t.HasFrameRange {
					if fromF <= t.FromFrame || toF < fromF {
						return nil, fmt.Errorf("line %d: invalid tag loop range %q after intro range %d..%d", lineNum, tok, t.FromFrame, t.ToFrame)
					}
					t.LoopFromFrame = fromF
					t.ToFrame = toF
					t.Frames = t.ToFrame - t.FromFrame + 1
					if t.Loop == "once" {
						t.Loop = "loop"
					}
				} else {
					t.HasFrameRange = true
					t.FromFrame = fromF
					t.ToFrame = toF
					t.Frames = toF - fromF + 1
				}
				continue
			}
			if singleFrame, err := strconv.Atoi(lowTok); err == nil && singleFrame >= 0 {
				if t.HasFrameRange {
					if singleFrame <= t.FromFrame {
						return nil, fmt.Errorf("line %d: invalid tag loop frame %q after intro range %d..%d", lineNum, tok, t.FromFrame, t.ToFrame)
					}
					t.LoopFromFrame = singleFrame
					t.ToFrame = singleFrame
					t.Frames = t.ToFrame - t.FromFrame + 1
					if t.Loop == "once" {
						t.Loop = "loop"
					}
				} else {
					t.HasFrameRange = true
					t.FromFrame = singleFrame
					t.ToFrame = singleFrame
					t.Frames = 1
				}
				continue
			}
			if strings.HasSuffix(lowTok, "ms") {
				d, err := strconv.Atoi(strings.TrimSuffix(lowTok, "ms"))
				if err != nil || d <= 0 {
					return nil, fmt.Errorf("line %d: invalid tag duration %q", lineNum, tok)
				}
				t.DurationMs = d
				continue
			}
			if _, err := ParseLoopMode(lowTok); err == nil {
				t.Loop = FormatLoopMode(lowTok)
				continue
			}
			return nil, fmt.Errorf("line %d: invalid tag attribute %q (expected key=value, <from>..<to>, <N>ms, or loop mode)", lineNum, tok)
		}
		key, val := strings.ToLower(kv[0]), kv[1]
		switch key {
		case "frames", "range":
			if idx := strings.Index(val, ".."); idx >= 0 {
				fromF, err1 := strconv.Atoi(val[:idx])
				toF, err2 := strconv.Atoi(val[idx+2:])
				if err1 != nil || err2 != nil || fromF < 0 || toF < fromF {
					return nil, fmt.Errorf("line %d: invalid frames=%q", lineNum, val)
				}
				t.HasFrameRange = true
				t.FromFrame = fromF
				t.ToFrame = toF
				t.Frames = toF - fromF + 1
			} else {
				n, err := strconv.Atoi(val)
				if err != nil || n < 1 || n > 256 {
					return nil, fmt.Errorf("line %d: invalid frames=%q (must be 1..256 or <from>..<to>)", lineNum, val)
				}
				t.Frames = n
			}
		case "loop_from", "loopfrom":
			lf, err := strconv.Atoi(val)
			if err != nil || lf < 0 {
				return nil, fmt.Errorf("line %d: invalid loop_from=%q", lineNum, val)
			}
			t.LoopFromFrame = lf
		case "duration":
			val = strings.TrimSuffix(strings.ToLower(val), "ms")
			d, err := strconv.Atoi(val)
			if err != nil || d <= 0 {
				return nil, fmt.Errorf("line %d: invalid duration=%q (must be > 0 ms)", lineNum, val)
			}
			t.DurationMs = d
		case "fps":
			fps, err := strconv.ParseFloat(val, 64)
			if err != nil || fps <= 0 {
				return nil, fmt.Errorf("line %d: invalid fps=%q", lineNum, val)
			}
			t.DurationMs = int(math.Round(1000.0 / fps))
		case "loop":
			if _, err := ParseLoopMode(val); err != nil {
				return nil, fmt.Errorf("line %d: %w", lineNum, err)
			}
			t.Loop = FormatLoopMode(val)
		default:
			return nil, fmt.Errorf("line %d: unknown tag attribute %q", lineNum, key)
		}
	}
	return t, nil
}

func parsePoseDirective(lineNum int, tokens []string, totalTagFrames int) (PoseDirective, error) {
	if len(tokens) < 2 {
		return PoseDirective{}, fmt.Errorf("line %d: pose directive requires a part name", lineNum)
	}
	pd := PoseDirective{
		PartName:   tokens[1],
		LineNum:    lineNum,
		FrameStart: 0,
		FrameEnd:   totalTagFrames - 1,
		AllFrames:  true,
		ScaleX:     1.0,
		ScaleY:     1.0,
		Ease:       "linear",
	}

	for _, tok := range tokens[2:] {
		kv := strings.SplitN(tok, "=", 2)
		if len(kv) != 2 {
			return pd, fmt.Errorf("line %d: invalid pose attribute %q (expected key=value)", lineNum, tok)
		}
		k, v := strings.ToLower(kv[0]), kv[1]
		switch k {
		case "f", "frame", "frames":
			if strings.ToLower(v) == "all" {
				pd.FrameStart = 0
				pd.FrameEnd = totalTagFrames - 1
				pd.AllFrames = true
			} else if idx := strings.Index(v, ".."); idx >= 0 {
				s, err1 := strconv.Atoi(v[:idx])
				e, err2 := strconv.Atoi(v[idx+2:])
				if err1 != nil || err2 != nil || s < 0 || e < s || e >= totalTagFrames {
					return pd, fmt.Errorf("line %d: invalid frame range f=%q for tag with %d frames", lineNum, v, totalTagFrames)
				}
				pd.FrameStart = s
				pd.FrameEnd = e
				pd.AllFrames = false
			} else {
				fIdx, err := strconv.Atoi(v)
				if err != nil || fIdx < 0 || fIdx >= totalTagFrames {
					return pd, fmt.Errorf("line %d: invalid frame index f=%q for tag with %d frames", lineNum, v, totalTagFrames)
				}
				pd.FrameStart = fIdx
				pd.FrameEnd = fIdx
				pd.AllFrames = false
			}
		case "dx":
			ex, err := parsePoseExpr(v)
			if err != nil {
				return pd, fmt.Errorf("line %d: invalid dx=%q: %w", lineNum, v, err)
			}
			pd.HasDX = true
			pd.DX = ex
		case "dy":
			ex, err := parsePoseExpr(v)
			if err != nil {
				return pd, fmt.Errorf("line %d: invalid dy=%q: %w", lineNum, v, err)
			}
			pd.HasDY = true
			pd.DY = ex
		case "rot":
			ex, err := parsePoseExpr(v)
			if err != nil {
				return pd, fmt.Errorf("line %d: invalid rot=%q: %w", lineNum, v, err)
			}
			pd.HasRot = true
			pd.Rot = ex
		case "scale":
			if strings.Contains(v, ",") {
				sx, sy, err := parsePairFloat(v)
				if err != nil || sx == 0 || sy == 0 {
					return pd, fmt.Errorf("line %d: invalid scale=%q", lineNum, v)
				}
				pd.HasScale = true
				pd.ScaleX = sx
				pd.ScaleY = sy
			} else {
				s, err := strconv.ParseFloat(v, 64)
				if err != nil || s == 0 {
					return pd, fmt.Errorf("line %d: invalid scale=%q", lineNum, v)
				}
				pd.HasScale = true
				pd.ScaleX = s
				pd.ScaleY = s
			}
		case "squash":
			ex, err := parsePoseExpr(v)
			if err != nil {
				return pd, fmt.Errorf("line %d: invalid squash=%q: %w", lineNum, v, err)
			}
			pd.HasSquash = true
			pd.Squash = ex
		case "visible":
			b, err := strconv.ParseBool(v)
			if err != nil {
				return pd, fmt.Errorf("line %d: invalid visible=%q: %w", lineNum, v, err)
			}
			pd.HasVisible = true
			pd.Visible = b
		case "ease":
			if _, err := EvalEasing(v, 0.5); err != nil {
				return pd, fmt.Errorf("line %d: %w", lineNum, err)
			}
			pd.Ease = strings.ToLower(v)
		default:
			return pd, fmt.Errorf("line %d: unknown pose attribute %q", lineNum, k)
		}
	}
	return pd, nil
}

// CompileSprite rasterizes all tags and frames of a validated SpriteSpec into a CompiledSprite.
func CompileSprite(spec *SpriteSpec) (*CompiledSprite, error) {
	if spec == nil {
		return nil, fmt.Errorf("compile sprite: spec is nil")
	}
	if spec.SheetPath != "" && len(spec.Parts) == 0 {
		return compileSheetBackedSprite(spec)
	}

	ramps := BuildPaletteRamps(spec.Palette)
	for k, v := range spec.CustomRamps {
		ramps[k] = v
	}

	// Sort parts stably by Z order (back to front)
	sortedParts := make([]*PartSpec, len(spec.Parts))
	copy(sortedParts, spec.Parts)
	sort.SliceStable(sortedParts, func(i, j int) bool {
		return sortedParts[i].Z < sortedParts[j].Z
	})

	partSummaries := make([]PartSummary, 0, len(sortedParts))
	for _, p := range sortedParts {
		partSummaries = append(partSummaries, PartSummary{
			Name:           p.Name,
			Ramp:           p.Ramp,
			Z:              p.Z,
			PrimitiveCount: len(p.Primitives),
		})
	}

	var allFrames []*image.RGBA
	var allDurations []int
	var compiledTags []CompiledTag

	for _, tag := range spec.Tags {
		fromIdx := len(allFrames)
		for fIdx := 0; fIdx < tag.Frames; fIdx++ {
			frameImg := renderSpriteFrame(spec, sortedParts, ramps, tag, fIdx)
			allFrames = append(allFrames, frameImg)
			allDurations = append(allDurations, tag.DurationMs)
		}
		toIdx := len(allFrames) - 1
		loopFrom := fromIdx
		if tag.LoopFromFrame > tag.FromFrame && tag.LoopFromFrame <= tag.ToFrame {
			loopFrom = fromIdx + (tag.LoopFromFrame - tag.FromFrame)
		}
		var outLoopFrom int
		if loopFrom > fromIdx {
			outLoopFrom = loopFrom
		}
		compiledTags = append(compiledTags, CompiledTag{
			Name:          tag.Name,
			FromFrame:     fromIdx,
			LoopFromFrame: outLoopFrom,
			ToFrame:       toIdx,
			Frames:        tag.Frames,
			DurationMs:    tag.DurationMs,
			Loop:          FormatLoopMode(tag.Loop),
		})
	}

	totalFrames := len(allFrames)
	cols := totalFrames
	if cols > 8 {
		cols = 8
	}
	if cols < 1 {
		cols = 1
	}
	rows := (totalFrames + cols - 1) / cols
	sheetW := cols * spec.Width
	sheetH := rows * spec.Height
	sheetRGBA := image.NewRGBA(image.Rect(0, 0, sheetW, sheetH))

	for i, fr := range allFrames {
		c := i % cols
		r := i / cols
		dstRect := image.Rect(c*spec.Width, r*spec.Height, (c+1)*spec.Width, (r+1)*spec.Height)
		draw.Draw(sheetRGBA, dstRect, fr, image.Point{0, 0}, draw.Src)
	}

	paletteColors := collectUniqueColors(sheetRGBA)

	return &CompiledSprite{
		Spec:           spec,
		Title:          spec.Title,
		Type:           spec.Type,
		FrameW:         spec.Width,
		FrameH:         spec.Height,
		Palette:        spec.Palette,
		Frames:         allFrames,
		FrameDurations: allDurations,
		Tags:           compiledTags,
		Parts:          partSummaries,
		PaletteColors:  paletteColors,
		SheetRGBA:      sheetRGBA,
		SheetCols:      cols,
		SheetRows:      rows,
	}, nil
}

func compileSheetBackedSprite(spec *SpriteSpec) (*CompiledSprite, error) {
	sheetPath := spec.SheetPath
	if !filepath.IsAbs(sheetPath) && spec.BaseDir != "" {
		cand := filepath.Join(spec.BaseDir, sheetPath)
		if _, err := os.Stat(cand); err == nil {
			sheetPath = cand
		}
	}

	var rgba *image.RGBA
	var allFrames []*image.RGBA
	var allDurations []int
	cols, rows := spec.GridCols, spec.GridRows
	fw, fh := spec.Width, spec.Height
	defDur := spec.DefaultDurationMs
	if defDur <= 0 {
		defDur = 100
	}

	lowSheet := strings.ToLower(sheetPath)
	if strings.HasSuffix(lowSheet, ".aseprite") || strings.HasSuffix(lowSheet, ".ase") {
		aseCS, err := ImportAseprite(sheetPath)
		if err != nil {
			return nil, fmt.Errorf("import aseprite sheet %q: %w", spec.SheetPath, err)
		}
		allFrames = aseCS.Frames
		fw = aseCS.FrameW
		fh = aseCS.FrameH
		if cols <= 0 {
			cols = aseCS.SheetCols
		}
		if rows <= 0 {
			rows = (len(allFrames) + cols - 1) / maxInt(1, cols)
		}
		rgba = image.NewRGBA(image.Rect(0, 0, cols*fw, rows*fh))
		for i, fr := range allFrames {
			c := i % cols
			r := i / cols
			dstRect := image.Rect(c*fw, r*fh, (c+1)*fw, (r+1)*fh)
			draw.Draw(rgba, dstRect, fr, image.Point{0, 0}, draw.Src)
			allDurations = append(allDurations, defDur)
		}
	} else {
		f, err := os.Open(sheetPath)
		if err != nil {
			return nil, fmt.Errorf("open sprite sheet %q: %w", spec.SheetPath, err)
		}
		defer f.Close()
		srcImg, _, err := image.Decode(f)
		if err != nil {
			return nil, fmt.Errorf("decode sprite sheet %q: %w", spec.SheetPath, err)
		}

		rgba = toPremultipliedRGBA(srcImg)
		b := rgba.Bounds()
		w, h := b.Dx(), b.Dy()

		if cols > 0 && rows > 0 && (fw == 32 && fh == 32 && (w != 32*cols || h != 32*rows)) {
			fw = w / cols
			fh = h / rows
		}
		if cols <= 0 && fw > 0 {
			cols = maxInt(1, w/fw)
		}
		if rows <= 0 && fh > 0 {
			rows = maxInt(1, h/fh)
		}
		if fw <= 0 && cols > 0 {
			fw = w / cols
		}
		if fh <= 0 && rows > 0 {
			fh = h / rows
		}

		for r := 0; r < rows; r++ {
			for c := 0; c < cols; c++ {
				cell := image.NewRGBA(image.Rect(0, 0, fw, fh))
				for y := 0; y < fh && r*fh+y < h; y++ {
					for x := 0; x < fw && c*fw+x < w; x++ {
						cell.SetRGBA(x, y, rgba.RGBAAt(c*fw+x, r*fh+y))
					}
				}
				allFrames = append(allFrames, cell)
				allDurations = append(allDurations, defDur)
			}
		}
	}

	var compiledTags []CompiledTag
	cursor := 0
	for _, t := range spec.Tags {
		var fromIdx, toIdx int
		if t.HasFrameRange {
			fromIdx = t.FromFrame
			toIdx = t.ToFrame
		} else {
			fromIdx = cursor
			toIdx = cursor + t.Frames - 1
			cursor = toIdx + 1
		}
		if fromIdx < 0 {
			fromIdx = 0
		}
		if toIdx >= len(allFrames) && len(allFrames) > 0 {
			toIdx = len(allFrames) - 1
		}
		if toIdx < fromIdx {
			toIdx = fromIdx
		}
		for fi := fromIdx; fi <= toIdx && fi < len(allDurations); fi++ {
			allDurations[fi] = t.DurationMs
		}
		var loopFrom int
		if t.LoopFromFrame > fromIdx && t.LoopFromFrame <= toIdx {
			loopFrom = t.LoopFromFrame
		}
		compiledTags = append(compiledTags, CompiledTag{
			Name:          t.Name,
			FromFrame:     fromIdx,
			LoopFromFrame: loopFrom,
			ToFrame:       toIdx,
			Frames:        toIdx - fromIdx + 1,
			DurationMs:    t.DurationMs,
			Loop:          FormatLoopMode(t.Loop),
		})
	}

	return &CompiledSprite{
		Spec:           spec,
		Title:          spec.Title,
		Type:           spec.Type,
		FrameW:         fw,
		FrameH:         fh,
		Palette:        spec.Palette,
		Frames:         allFrames,
		FrameDurations: allDurations,
		Tags:           compiledTags,
		Parts:          []PartSummary{},
		PaletteColors:  collectUniqueColors(rgba),
		SheetRGBA:      rgba,
		SheetCols:      cols,
		SheetRows:      rows,
	}, nil
}

func computePartPivot(p *PartSpec, frameW, frameH int) (float64, float64) {
	if p.HasPivot {
		return p.PivotX, p.PivotY
	}
	if len(p.Primitives) == 0 {
		return float64(frameW) * 0.5, float64(frameH) * 0.5
	}
	var sumX, sumY float64
	count := 0.0
	for _, pr := range p.Primitives {
		switch pr.Kind {
		case PrimPoly:
			for _, pt := range pr.Points {
				sumX += pt[0]
				sumY += pt[1]
				count++
			}
		case PrimCapsule, PrimLine:
			sumX += (pr.CX + pr.BX) * 0.5
			sumY += (pr.CY + pr.BY) * 0.5
			count++
		default:
			sumX += pr.CX
			sumY += pr.CY
			count++
		}
	}
	if count > 0 {
		return sumX / count, sumY / count
	}
	return float64(frameW) * 0.5, float64(frameH) * 0.5
}

func evalPartTransform(p *PartSpec, tag *TagSpec, fIdx int, frameW, frameH int) (Transform2D, bool) {
	pivX, pivY := computePartPivot(p, frameW, frameH)
	tr := Transform2D{
		OriginX: pivX,
		OriginY: pivY,
		ScaleX:  1.0,
		ScaleY:  1.0,
	}
	visible := !p.Hidden
	if tag == nil || tag.Frames <= 0 {
		return tr, visible
	}
	cycleT := float64(fIdx) / float64(tag.Frames)

	for _, ps := range tag.Poses {
		if ps.PartName != p.Name {
			continue
		}
		if fIdx < ps.FrameStart || fIdx > ps.FrameEnd {
			continue
		}
		span := ps.FrameEnd - ps.FrameStart
		localT := 0.0
		if span > 0 {
			localT = float64(fIdx-ps.FrameStart) / float64(span)
		} else if tag.Frames > 1 && ps.AllFrames {
			localT = float64(fIdx) / float64(tag.Frames-1)
		}
		if ps.HasDX {
			tr.X += ps.DX.Eval(localT, cycleT, ps.Ease)
		}
		if ps.HasDY {
			tr.Y += ps.DY.Eval(localT, cycleT, ps.Ease)
		}
		if ps.HasRot {
			deg := ps.Rot.Eval(localT, cycleT, ps.Ease)
			tr.Rotation += deg * math.Pi / 180.0
		}
		if ps.HasScale {
			tr.ScaleX *= ps.ScaleX
			tr.ScaleY *= ps.ScaleY
		}
		if ps.HasSquash {
			tr.Squash += ps.Squash.Eval(localT, cycleT, ps.Ease)
		}
		if ps.HasVisible {
			visible = ps.Visible
		}
	}
	// Snap translation to integer pixels so pixel-art details never shimmer between frames
	tr.X = math.Round(tr.X)
	tr.Y = math.Round(tr.Y)
	return tr, visible
}

func evalPrimSDF(pr PrimitiveSpec, lx, ly float64) float64 {
	switch pr.Kind {
	case PrimCircle:
		return SDFCircle(lx, ly, pr.CX, pr.CY, pr.Radius)
	case PrimBox:
		return SDFBox(lx, ly, pr.CX, pr.CY, pr.HalfW, pr.HalfH, pr.Radius)
	case PrimCapsule, PrimLine:
		return SDFCapsule(lx, ly, pr.CX, pr.CY, pr.BX, pr.BY, pr.Radius)
	case PrimRing:
		return SDFRing(lx, ly, pr.CX, pr.CY, pr.Radius, pr.Thick)
	case PrimPoly:
		return SDFPolygon(lx, ly, pr.Points, pr.Radius)
	default:
		return 1e6
	}
}

func evalPartSDFAt(p *PartSpec, lx, ly float64) (float64, string, bool, int) {
	d := 1e6
	activeRamp := p.Ramp
	hasExplicitStep := false
	explicitStep := 0
	hasShape := false
	for _, pr := range p.Primitives {
		if pr.Kind == PrimPixel {
			continue
		}
		hasShape = true
		pd := evalPrimSDF(pr, lx, ly)
		switch pr.Op {
		case "sub":
			d = math.Max(d, -pd)
		case "smin":
			if pd <= 0.0 || pd < d {
				activeRamp = pr.Ramp
				hasExplicitStep = pr.HasStep
				explicitStep = pr.Step
			}
			d = SDFSmoothMin(d, pd, pr.SmoothK)
		default: // union
			if pd <= 0.0 || pd < d {
				activeRamp = pr.Ramp
				hasExplicitStep = pr.HasStep
				explicitStep = pr.Step
			}
			if pd < d {
				d = pd
			}
		}
	}
	if !hasShape {
		return 1e6, activeRamp, false, 0
	}
	return d, activeRamp, hasExplicitStep, explicitStep
}

func renderSpriteFrame(spec *SpriteSpec, parts []*PartSpec, ramps map[string]MaterialRamp, tag *TagSpec, fIdx int) *image.RGBA {
	w, h := spec.Width, spec.Height
	img := image.NewRGBA(image.Rect(0, 0, w, h))
	partLayer := make([]int, w*h)
	partZ := make([]int, w*h)
	for i := range partLayer {
		partLayer[i] = -1
		partZ[i] = -999999
	}

	centerX := float64(w) * 0.5

	for pIdx, p := range parts {
		tr, visible := evalPartTransform(p, tag, fIdx, w, h)
		if !visible {
			continue
		}

		// 1. Evaluate SDF primitives across frame pixels
		for y := 0; y < h; y++ {
			py := float64(y) + 0.5
			for x := 0; x < w; x++ {
				px := float64(x) + 0.5
				lx, ly := tr.InversePoint(px, py)
				d, rampName, hasStep, expStep := evalPartSDFAt(p, lx, ly)

				if p.MirrorX {
					mx := 2.0*centerX - px
					mlx, mly := tr.InversePoint(mx, py)
					md, mramp, mHasStep, mExpStep := evalPartSDFAt(p, mlx, mly)
					if md < d {
						d = md
						rampName = mramp
						hasStep = mHasStep
						expStep = mExpStep
						lx, ly = mlx, mly
					}
				}

				if d <= 0.0 {
					ramp, ok := ramps[rampName]
					if !ok {
						ramp = ramps[p.Ramp]
					}
					var col color.RGBA
					if hasStep && expStep >= 0 && expStep <= 3 {
						col = ramp[expStep]
					} else {
						// Estimate surface normal from SDF gradient
						const eps = 0.65
						dx1, _, _, _ := evalPartSDFAt(p, lx+eps, ly)
						dx0, _, _, _ := evalPartSDFAt(p, lx-eps, ly)
						dy1, _, _, _ := evalPartSDFAt(p, lx, ly+eps)
						dy0, _, _, _ := evalPartSDFAt(p, lx, ly-eps)
						nx := (dx1 - dx0) / (2.0 * eps)
						ny := (dy1 - dy0) / (2.0 * eps)
						nLen := math.Hypot(nx, ny)
						if nLen > 1e-6 {
							nx /= nLen
							ny /= nLen
						}

						// Combine normal alignment with light and interior volume height
						depthFactor := math.Min(1.0, -d/4.5)
						nz := math.Sqrt(math.Max(0.0, 1.0-0.65*(1.0-depthFactor)*(1.0-depthFactor)))
						lightDot := nx*spec.LightX*(1.0-0.35*depthFactor) + ny*spec.LightY*(1.0-0.35*depthFactor) + nz*0.58
						illum := math.Max(0.0, math.Min(1.0, (lightDot+0.35)/1.25))
						col = SampleMaterialRampDithered(ramp, illum, int(math.Floor(lx)), int(math.Floor(ly)), p.Dither)

						// Internal depth crease when overlapping a lower Z part right near the boundary
						idx := y*w + x
						if partLayer[idx] >= 0 && partZ[idx] < p.Z && d > -1.15 {
							if nx*spec.LightX+ny*spec.LightY < 0.15 {
								col = ramp[0]
							}
						}
					}

					idx := y*w + x
					img.SetRGBA(x, y, col)
					partLayer[idx] = pIdx
					partZ[idx] = p.Z
				}
			}
		}

		// 2. Render explicit pixel primitives in inverse-transformed part space so they stay locked to the part
		for y := 0; y < h; y++ {
			py := float64(y) + 0.5
			for x := 0; x < w; x++ {
				px := float64(x) + 0.5
				lx, ly := tr.InversePoint(px, py)
				ix, iy := int(math.Floor(lx)), int(math.Floor(ly))
				for _, pr := range p.Primitives {
					if pr.Kind != PrimPixel {
						continue
					}
					p0x, p0y := int(math.Floor(pr.CX)), int(math.Floor(pr.CY))
					matched := ix >= p0x && ix < p0x+pr.PixelW && iy >= p0y && iy < p0y+pr.PixelH
					if !matched && p.MirrorX {
						mx := 2.0*centerX - px
						mlx, mly := tr.InversePoint(mx, py)
						mix, miy := int(math.Floor(mlx)), int(math.Floor(mly))
						matched = mix >= p0x && mix < p0x+pr.PixelW && miy >= p0y && miy < p0y+pr.PixelH
					}
					if matched {
						ramp, ok := ramps[pr.Ramp]
						if !ok {
							ramp = ramps[p.Ramp]
						}
						step := 3
						if pr.HasStep {
							step = pr.Step
						}
						img.SetRGBA(x, y, ramp[step])
						partLayer[y*w+x] = pIdx
						partZ[y*w+x] = p.Z
					}
				}
			}
		}
	}

	// 3. Apply crisp 1px outer silhouette outline if enabled
	if spec.OutlineMode == "color" {
		applyOuterOutline(img, spec.OutlineRGBA)
	}

	return img
}

func applyOuterOutline(img *image.RGBA, outlineCol color.RGBA) {
	b := img.Bounds()
	w, h := b.Dx(), b.Dy()
	opaque := make([]bool, w*h)
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			if img.RGBAAt(x, y).A > 0 {
				opaque[y*w+x] = true
			}
		}
	}
	dirs := [4][2]int{{-1, 0}, {1, 0}, {0, -1}, {0, 1}}
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			if opaque[y*w+x] {
				continue
			}
			// Do not draw outline into the extreme border pixel if it would clip the sprite's silhouette,
			// or draw cleanly within bounds where adjacent to an interior opaque pixel.
			touchOpaque := false
			for _, d := range dirs {
				nx, ny := x+d[0], y+d[1]
				if nx >= 0 && nx < w && ny >= 0 && ny < h && opaque[ny*w+nx] {
					touchOpaque = true
					break
				}
			}
			if touchOpaque {
				img.SetRGBA(x, y, outlineCol)
			}
		}
	}
}

func collectUniqueColors(img *image.RGBA) []color.RGBA {
	seen := make(map[color.RGBA]bool)
	var out []color.RGBA
	// Always put transparent color at index 0
	trans := color.RGBA{0, 0, 0, 0}
	seen[trans] = true
	out = append(out, trans)

	b := img.Bounds()
	for y := b.Min.Y; y < b.Max.Y; y++ {
		for x := b.Min.X; x < b.Max.X; x++ {
			c := img.RGBAAt(x, y)
			if !seen[c] {
				seen[c] = true
				out = append(out, c)
			}
		}
	}
	return out
}

// Visual QA Validator

// SpriteValidationReport summarizes automated visual QA checks for a CompiledSprite.
type SpriteValidationReport struct {
	Passed             bool     `json:"passed"`
	PremultipliedClean bool     `json:"premultipliedClean"`
	FillRatioPct       float64  `json:"fillRatioPct"`
	OpaquePixelPct     float64  `json:"opaquePixelPct"`
	CenterOfMassX      float64  `json:"centerOfMassX"`
	CenterOfMassY      float64  `json:"centerOfMassY"`
	LuminanceSteps     int      `json:"luminanceSteps"`
	ClippedEdges       int      `json:"clippedEdges"`
	Issues             []string `json:"issues"`
}

// ValidateSprite performs automated visual QA checks on a CompiledSprite:
// 1. Premultiplied alpha invariant (R, G, B <= A) across all frames and SheetRGBA
// 2. Frame fill ratio (bounding box area / frame area in 8%..92% for sprites or 50%..100% for tilesets)
// 3. Center-of-mass / pivot stability across frames
// 4. Silhouette and material ramp contrast (>= 3 distinct luminance levels)
// 5. Animation tag integrity
func ValidateSprite(cs *CompiledSprite) SpriteValidationReport {
	rep := SpriteValidationReport{
		Passed:             true,
		PremultipliedClean: true,
		Issues:             []string{},
	}
	if cs == nil || len(cs.Frames) == 0 || cs.SheetRGBA == nil {
		rep.Passed = false
		rep.PremultipliedClean = false
		rep.Issues = append(rep.Issues, "compiled sprite has no frames or nil SheetRGBA")
		return rep
	}

	if err := ValidatePremultipliedRGBA(cs.SheetRGBA); err != nil {
		rep.Passed = false
		rep.PremultipliedClean = false
		rep.Issues = append(rep.Issues, err.Error())
	}

	w, h := cs.FrameW, cs.FrameH
	frameArea := float64(w * h)
	if frameArea <= 0 {
		rep.Passed = false
		rep.Issues = append(rep.Issues, "invalid frame dimensions")
		return rep
	}

	var sumBBoxRatio, sumOpaqueRatio float64
	var sumComX, sumComY float64
	validComFrames := 0
	lumBuckets := make(map[int]bool)

	for fIdx, fr := range cs.Frames {
		if err := ValidatePremultipliedRGBA(fr); err != nil && rep.PremultipliedClean {
			rep.Passed = false
			rep.PremultipliedClean = false
			rep.Issues = append(rep.Issues, fmt.Sprintf("frame %d: %v", fIdx, err))
		}

		minX, minY := w, h
		maxX, maxY := -1, -1
		opaqueCount := 0
		var wx, wy float64

		for y := 0; y < h; y++ {
			for x := 0; x < w; x++ {
				c := fr.RGBAAt(x, y)
				if c.A > 0 {
					opaqueCount++
					if x < minX {
						minX = x
					}
					if x > maxX {
						maxX = x
					}
					if y < minY {
						minY = y
					}
					if y > maxY {
						maxY = y
					}
					wx += float64(x) + 0.5
					wy += float64(y) + 0.5

					// Quantize perceived luminance into 16 buckets (0..15)
					lum := int((0.299*float64(c.R) + 0.587*float64(c.G) + 0.114*float64(c.B)) / 16.0)
					lumBuckets[lum] = true
				}
			}
		}

		if opaqueCount == 0 {
			rep.Passed = false
			rep.Issues = append(rep.Issues, fmt.Sprintf("frame %d is completely empty (0 opaque pixels)", fIdx))
			continue
		}

		bboxW := float64(maxX - minX + 1)
		bboxH := float64(maxY - minY + 1)
		sumBBoxRatio += (bboxW * bboxH) / frameArea
		sumOpaqueRatio += float64(opaqueCount) / frameArea

		sumComX += wx / float64(opaqueCount)
		sumComY += wy / float64(opaqueCount)
		validComFrames++
	}

	nFrames := float64(len(cs.Frames))
	rep.FillRatioPct = math.Round((sumBBoxRatio/nFrames)*10000.0) / 100.0
	rep.OpaquePixelPct = math.Round((sumOpaqueRatio/nFrames)*10000.0) / 100.0
	if validComFrames > 0 {
		rep.CenterOfMassX = math.Round((sumComX/float64(validComFrames))*100.0) / 100.0
		rep.CenterOfMassY = math.Round((sumComY/float64(validComFrames))*100.0) / 100.0
	}
	rep.LuminanceSteps = len(lumBuckets)

	if cs.Type == "tileset" {
		if rep.FillRatioPct < 50.0 {
			rep.Passed = false
			rep.Issues = append(rep.Issues, fmt.Sprintf("tileset fill ratio %.1f%% is below minimum 50.0%%", rep.FillRatioPct))
		}
	} else {
		if rep.FillRatioPct < 8.0 || rep.FillRatioPct > 92.0 {
			rep.Passed = false
			rep.Issues = append(rep.Issues, fmt.Sprintf("sprite bounding-box fill ratio %.1f%% is outside target range [8.0%%, 92.0%%]", rep.FillRatioPct))
		}
		if validComFrames > 0 {
			minComX := float64(w) * 0.18
			maxComX := float64(w) * 0.82
			if rep.CenterOfMassX < minComX || rep.CenterOfMassX > maxComX {
				rep.Passed = false
				rep.Issues = append(rep.Issues, fmt.Sprintf("horizontal center of mass %.2f is severely off-center for frame width %d (expected %.1f..%.1f)",
					rep.CenterOfMassX, w, minComX, maxComX))
			}
		}
	}

	if rep.LuminanceSteps < 3 {
		rep.Passed = false
		rep.Issues = append(rep.Issues, fmt.Sprintf("insufficient shading contrast: found %d distinct luminance steps (minimum 3 required)", rep.LuminanceSteps))
	}

	if len(cs.Tags) == 0 {
		rep.Passed = false
		rep.Issues = append(rep.Issues, "sprite has no animation tags")
	}
	for _, t := range cs.Tags {
		if t.FromFrame < 0 || t.ToFrame < t.FromFrame || t.ToFrame >= len(cs.Frames) {
			rep.Passed = false
			rep.Issues = append(rep.Issues, fmt.Sprintf("tag %q has out-of-bounds frame range [%d..%d]", t.Name, t.FromFrame, t.ToFrame))
		}
		if t.DurationMs <= 0 {
			rep.Passed = false
			rep.Issues = append(rep.Issues, fmt.Sprintf("tag %q has non-positive frame duration %dms", t.Name, t.DurationMs))
		}
	}

	return rep
}
