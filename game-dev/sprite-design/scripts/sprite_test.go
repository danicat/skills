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
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"math"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func TestPremultiplyAndValidateRGBA(t *testing.T) {
	c0 := PremultiplyRGBA(255, 128, 64, 0)
	if c0 != (color.RGBA{0, 0, 0, 0}) {
		t.Fatalf("expected transparent zero RGBA, got %+v", c0)
	}

	cHalf := PremultiplyRGBA(200, 100, 50, 128)
	if cHalf.R > cHalf.A || cHalf.G > cHalf.A || cHalf.B > cHalf.A {
		t.Fatalf("premultiplied color %+v violates R,G,B <= A", cHalf)
	}

	img := image.NewRGBA(image.Rect(0, 0, 4, 4))
	img.SetRGBA(1, 1, cHalf)
	if err := ValidatePremultipliedRGBA(img); err != nil {
		t.Fatalf("expected valid premultiplied image, got error: %v", err)
	}

	// Inject invalid un-premultiplied pixel
	img.SetRGBA(2, 2, color.RGBA{R: 255, G: 0, B: 0, A: 128})
	if err := ValidatePremultipliedRGBA(img); err == nil {
		t.Fatalf("expected error for un-premultiplied pixel RGBA(255,0,0,128), got nil")
	}
}

func TestPalettesAndMaterialRamps(t *testing.T) {
	palettes := ListPalettes()
	if len(palettes) != 12 {
		t.Fatalf("expected 12 built-in palettes, got %d", len(palettes))
	}
	ramps := ListMaterialRamps()
	if len(ramps) != 12 {
		t.Fatalf("expected 12 built-in material ramps, got %d", len(ramps))
	}

	for _, pName := range palettes {
		pMap := BuildPaletteRamps(pName)
		for _, rName := range ramps {
			mr, ok := pMap[rName]
			if !ok {
				t.Fatalf("palette %q missing material ramp %q", pName, rName)
			}
			c0 := SampleMaterialRamp(mr, 0.1)
			c1 := SampleMaterialRamp(mr, 0.4)
			c2 := SampleMaterialRamp(mr, 0.7)
			c3 := SampleMaterialRamp(mr, 0.95)
			if c0 != mr[0] || c1 != mr[1] || c2 != mr[2] || c3 != mr[3] {
				t.Fatalf("SampleMaterialRamp step mismatch for %s/%s", pName, rName)
			}
			cd := SampleMaterialRampDithered(mr, 0.62, 1, 1, "bayer4")
			if cd.A != 255 {
				t.Fatalf("expected opaque dithered color, got %+v", cd)
			}
		}
	}
}

func TestSDFPrimitivesAndCSG(t *testing.T) {
	if d := SDFCircle(10, 10, 10, 10, 5); math.Abs(d+5) > 1e-6 {
		t.Fatalf("expected SDFCircle center distance -5, got %f", d)
	}
	if d := SDFBox(8, 8, 8, 8, 4, 3, 0); math.Abs(d+3) > 1e-6 {
		t.Fatalf("expected SDFBox center distance -3, got %f", d)
	}
	if d := SDFCapsule(5, 5, 2, 5, 8, 5, 2); math.Abs(d+2) > 1e-6 {
		t.Fatalf("expected SDFCapsule axis distance -2, got %f", d)
	}
	if d := SDFRing(15, 10, 10, 10, 5, 2); math.Abs(d+1) > 1e-6 {
		t.Fatalf("expected SDFRing perimeter distance -1, got %f", d)
	}
	tri := [][2]float64{{4, 4}, {12, 4}, {8, 12}}
	if d := SDFPolygon(8, 6, tri, 0); d >= 0 {
		t.Fatalf("expected point (8,6) to be inside triangle (d < 0), got %f", d)
	}
	sm := SDFSmoothMin(0.5, 0.6, 2.0)
	if sm >= 0.5 {
		t.Fatalf("expected SDFSmoothMin(0.5, 0.6, 2.0) < 0.5, got %f", sm)
	}
}

func TestTransform2DAndEasing(t *testing.T) {
	tr := Transform2D{
		X:        3,
		Y:        -2,
		OriginX:  16,
		OriginY:  16,
		ScaleX:   1.0,
		ScaleY:   1.0,
		Rotation: math.Pi / 4.0,
		Squash:   0.15,
	}
	m := tr.GetGeoM()
	wx, wy := m.Apply(12, 20)
	lx, ly := tr.InversePoint(wx, wy)
	if math.Hypot(lx-12, ly-20) > 1e-5 {
		t.Fatalf("Transform2D InversePoint round-trip mismatch: got (%f, %f), want (12, 20)", lx, ly)
	}

	eases := []string{"linear", "in_quad", "out_quad", "in_out_cubic", "elastic_out"}
	for _, name := range eases {
		v0, err0 := EvalEasing(name, 0.0)
		v1, err1 := EvalEasing(name, 1.0)
		if err0 != nil || err1 != nil {
			t.Fatalf("EvalEasing(%q) returned unexpected error: %v %v", name, err0, err1)
		}
		if math.Abs(v0) > 1e-5 || math.Abs(v1-1.0) > 1e-5 {
			t.Fatalf("EvalEasing(%q) endpoints should be 0 and 1, got %f and %f", name, v0, v1)
		}
	}
}

func TestSheetContainerLeadInOnceAndAsepriteRoundTrip(t *testing.T) {
	tmpDir := t.TempDir()

	// Synthesize a 4x2 grid of 32x32 cells (128x64) with 4 luminance steps per cell
	ramps := BuildPaletteRamps("snes")
	steel := ramps["steel"]
	sheet := image.NewRGBA(image.Rect(0, 0, 128, 64))
	for idx := 0; idx < 8; idx++ {
		cellX := (idx % 4) * 32
		cellY := (idx / 4) * 32
		for y := 0; y < 32; y++ {
			for x := 0; x < 32; x++ {
				dx := float64(x) + 0.5 - 16.0
				dy := float64(y) + 0.5 - 16.0
				if math.Hypot(dx, dy) <= 9.0 {
					illum := math.Max(0.0, math.Min(1.0, 0.55+0.45*(-dx*0.5-dy*0.7)/9.0))
					sheet.SetRGBA(cellX+x, cellY+y, SampleMaterialRamp(steel, illum))
				}
			}
		}
	}

	sheetPath := filepath.Join(tmpDir, "hero_sheet.png")
	f, err := os.Create(sheetPath)
	if err != nil {
		t.Fatalf("create synthetic sheet png: %v", err)
	}
	if err := png.Encode(f, sheet); err != nil {
		_ = f.Close()
		t.Fatalf("encode synthetic sheet png: %v", err)
	}
	if err := f.Close(); err != nil {
		t.Fatalf("close synthetic sheet png: %v", err)
	}

	spriteDSL := `title "hero_cat"
type sprite
sheet "hero_sheet.png"
size 32x32
grid 4x2
fps 10

tag idle 0..3 pingpong
tag run  4 once, 5..7 loop
`
	spritePath := filepath.Join(tmpDir, "hero.sprite")
	if err := os.WriteFile(spritePath, []byte(spriteDSL), 0o600); err != nil {
		t.Fatalf("write container .sprite: %v", err)
	}

	spec, err := LoadSpriteFile(spritePath)
	if err != nil {
		t.Fatalf("LoadSpriteFile failed: %v", err)
	}
	cs, err := CompileSprite(spec)
	if err != nil {
		t.Fatalf("CompileSprite failed: %v", err)
	}
	rep := ValidateSprite(cs)
	if !rep.Passed {
		t.Fatalf("container sprite failed ValidateSprite: %v", rep.Issues)
	}
	if cs.FrameW != 32 || cs.FrameH != 32 || len(cs.Frames) != 8 || len(cs.Tags) != 2 {
		t.Fatalf("unexpected dimensions/frames/tags: %dx%d, %d frames, %d tags",
			cs.FrameW, cs.FrameH, len(cs.Frames), len(cs.Tags))
	}

	ctrl, err := cs.ToEbitenController()
	if err != nil {
		t.Fatalf("ToEbitenController failed: %v", err)
	}
	if err := ctrl.Play("run"); err != nil {
		t.Fatalf("Play('run') failed: %v", err)
	}
	wantSeq := []int{4, 5, 6, 7, 5, 6, 7, 5}
	for step, wantFrame := range wantSeq {
		if ctrl.CurrentFrame != wantFrame {
			t.Fatalf("run step %d: expected frame %d (4 once then 5..7 loop), got %d", step, wantFrame, ctrl.CurrentFrame)
		}
		ctrl.Update(100 * time.Millisecond)
	}

	asePath := filepath.Join(tmpDir, "hero.aseprite")
	if err := ExportAseprite(asePath, cs); err != nil {
		t.Fatalf("ExportAseprite failed: %v", err)
	}
	aseCS, err := ImportAseprite(asePath)
	if err != nil {
		t.Fatalf("ImportAseprite failed: %v", err)
	}
	if aseCS.FrameW != 32 || aseCS.FrameH != 32 || len(aseCS.Frames) != 8 || len(aseCS.Tags) != 2 {
		t.Fatalf("unexpected imported .aseprite: %dx%d, %d frames, %d tags",
			aseCS.FrameW, aseCS.FrameH, len(aseCS.Frames), len(aseCS.Tags))
	}
	if aseCS.Tags[1].Name != "run" || aseCS.Tags[1].FromFrame != 4 || aseCS.Tags[1].LoopFromFrame != 5 || aseCS.Tags[1].ToFrame != 7 {
		t.Fatalf("expected .aseprite 'run' tag to preserve LoopFromFrame=5, got %+v", aseCS.Tags[1])
	}
}

const sampleProceduralDSL = `title "Test Sprite"
type sprite
size 32x32
palette snes

part body ramp=steel z=0:
  circle 16,16 r=9

part visor ramp=gold z=1:
  box 16,12 4,2 r=1

tag idle frames=2 duration=100 loop=forward:
  pose body dy=-1

tag run frames=2 duration=90 loop=forward:
  pose body dx=1

tag attack frames=2 duration=80 loop=once:
  pose visor dx=2

tag bank_left frames=2 duration=85 loop=pingpong:
  pose body rot=-10
`

func TestAnimationControllerLifecycle(t *testing.T) {
	cs, err := CompileSpriteDSL(sampleProceduralDSL)
	if err != nil {
		t.Fatalf("compile sampleProceduralDSL: %v", err)
	}
	ctrl, err := cs.ToEbitenController()
	if err != nil {
		t.Fatalf("ToEbitenController failed: %v", err)
	}

	// Test forward looping tag ("run")
	if err := ctrl.Play("run"); err != nil {
		t.Fatalf("Play('run') failed: %v", err)
	}
	startFrame := ctrl.CurrentFrame
	ctrl.Update(90 * time.Millisecond)
	if ctrl.CurrentFrame != startFrame+1 {
		t.Fatalf("expected frame to advance from %d to %d, got %d", startFrame, startFrame+1, ctrl.CurrentFrame)
	}

	// Test once tag ("attack") finishes, invokes OnComplete once, and holds final frame
	var completedTag string
	completedCount := 0
	ctrl.OnComplete = func(name string) {
		completedTag = name
		completedCount++
	}
	if err := ctrl.Play("attack"); err != nil {
		t.Fatalf("Play('attack') failed: %v", err)
	}
	for i := 0; i < 10; i++ {
		ctrl.Update(80 * time.Millisecond)
	}
	if !ctrl.Finished {
		t.Fatalf("expected LoopOnce tag 'attack' to mark Finished=true")
	}
	if completedCount != 1 || completedTag != "attack" {
		t.Fatalf("expected OnComplete('attack') once, got %q x%d", completedTag, completedCount)
	}
	if ctrl.CurrentFrame != ctrl.ActiveTag.EndFrame {
		t.Fatalf("expected LoopOnce tag to hold EndFrame %d, got %d", ctrl.ActiveTag.EndFrame, ctrl.CurrentFrame)
	}

	// Test pingpong tag ("bank_left")
	if err := ctrl.Play("bank_left"); err != nil {
		t.Fatalf("Play('bank_left') failed: %v", err)
	}
	for i := 0; i < 3; i++ {
		ctrl.Update(85 * time.Millisecond)
	}
	if ctrl.PingPongDir != -1 {
		t.Fatalf("expected PingPongDir to reverse to -1 after hitting EndFrame, got %d", ctrl.PingPongDir)
	}
	for i := 0; i < 3; i++ {
		ctrl.Update(85 * time.Millisecond)
	}
	if ctrl.PingPongDir != 1 {
		t.Fatalf("expected PingPongDir to return to 1 after bouncing back to StartFrame, got %d", ctrl.PingPongDir)
	}
}

func TestAsepriteBinaryExportAndRoundTrip(t *testing.T) {
	cs, err := CompileSpriteDSL(sampleProceduralDSL)
	if err != nil {
		t.Fatalf("compile sampleProceduralDSL: %v", err)
	}

	tmpDir := t.TempDir()
	asePath := filepath.Join(tmpDir, "test_sprite.aseprite")
	if err := ExportAseprite(asePath, cs); err != nil {
		t.Fatalf("ExportAseprite failed: %v", err)
	}

	info, err := ReadAsepriteHeader(asePath)
	if err != nil {
		t.Fatalf("ReadAsepriteHeader failed: %v", err)
	}
	if info.Magic != 0xA5E0 {
		t.Fatalf("unexpected ASE magic 0x%04X", info.Magic)
	}
	if int(info.FrameCount) != len(cs.Frames) {
		t.Fatalf("expected %d frames in .aseprite header, got %d", len(cs.Frames), info.FrameCount)
	}
	if int(info.Width) != cs.FrameW || int(info.Height) != cs.FrameH {
		t.Fatalf("expected dimensions %dx%d, got %dx%d", cs.FrameW, cs.FrameH, info.Width, info.Height)
	}
	if info.ColorDepth != 32 {
		t.Fatalf("expected 32 bpp color depth, got %d", info.ColorDepth)
	}
	if info.CelCount != len(cs.Frames) {
		t.Fatalf("expected %d cel chunks, got %d", len(cs.Frames), info.CelCount)
	}
	if len(info.TagNames) != len(cs.Tags) {
		t.Fatalf("expected %d tags in .aseprite, got %d (%v)", len(cs.Tags), len(info.TagNames), info.TagNames)
	}
}

func TestExportPNGAndJSONManifest(t *testing.T) {
	cs, err := CompileSpriteDSL(sampleProceduralDSL)
	if err != nil {
		t.Fatalf("compile sampleProceduralDSL: %v", err)
	}

	tmpDir := t.TempDir()
	pngPath := filepath.Join(tmpDir, "test_sprite.png")
	jsonPath := filepath.Join(tmpDir, "test_sprite.json")
	if err := ExportPNGSheet(pngPath, jsonPath, cs); err != nil {
		t.Fatalf("ExportPNGSheet failed: %v", err)
	}

	img, err := loadImageFile(pngPath)
	if err != nil {
		t.Fatalf("load exported PNG failed: %v", err)
	}
	if img.Bounds() != cs.SheetRGBA.Bounds() {
		t.Fatalf("exported PNG bounds %v != SheetRGBA bounds %v", img.Bounds(), cs.SheetRGBA.Bounds())
	}

	jb, err := os.ReadFile(jsonPath)
	if err != nil {
		t.Fatalf("read exported JSON failed: %v", err)
	}
	var manifest AsepriteSheetJSON
	if err := json.Unmarshal(jb, &manifest); err != nil {
		t.Fatalf("unmarshal exported JSON failed: %v", err)
	}
	if len(manifest.Frames) != len(cs.Frames) {
		t.Fatalf("expected %d JSON frames, got %d", len(cs.Frames), len(manifest.Frames))
	}
	if len(manifest.Meta.FrameTags) != len(cs.Tags) {
		t.Fatalf("expected %d JSON frameTags, got %d", len(cs.Tags), len(manifest.Meta.FrameTags))
	}
}

func TestNormalizeSpriteSheetAndExtractPalette(t *testing.T) {
	// Build a synthetic 2-frame raw AI sprite sheet (64x32 for two 32x32 cells)
	// with a 2-tone checkerboard background and off-center character silhouettes.
	raw := image.NewRGBA(image.Rect(0, 0, 64, 32))
	bg1 := color.RGBA{R: 240, G: 240, B: 240, A: 255}
	bg2 := color.RGBA{R: 228, G: 228, B: 228, A: 255}
	for y := 0; y < 32; y++ {
		for x := 0; x < 64; x++ {
			if ((x/4)+(y/4))%2 == 0 {
				raw.SetRGBA(x, y, bg1)
			} else {
				raw.SetRGBA(x, y, bg2)
			}
		}
	}

	// Draw character in frame 0 shifted left (around x=6..16) and in frame 1 shifted right (around x=48..58)
	shCol := color.RGBA{R: 30, G: 40, B: 90, A: 255}
	mdCol := color.RGBA{R: 60, G: 110, B: 190, A: 255}
	hiCol := color.RGBA{R: 130, G: 200, B: 250, A: 255}
	spCol := color.RGBA{R: 230, G: 248, B: 255, A: 255}
	cols := []color.RGBA{shCol, mdCol, hiCol, spCol}

	for f, xOff := range []int{6, 48} {
		_ = f
		for y := 8; y < 26; y++ {
			for x := xOff; x < xOff+10; x++ {
				step := (y - 8) * 4 / 18
				raw.SetRGBA(x, y, cols[step])
			}
		}
	}

	normCS, err := NormalizeSpriteSheet(raw, NormalizeOptions{
		Title:          "AI Knight Test",
		FrameWidth:     32,
		FrameHeight:    32,
		ColorTolerance: 20,
		AutoCenterX:    true,
		GroundBottom:   true,
		BottomPadding:  2,
	})
	if err != nil {
		t.Fatalf("NormalizeSpriteSheet failed: %v", err)
	}
	if len(normCS.Frames) != 2 {
		t.Fatalf("expected 2 normalized frames, got %d", len(normCS.Frames))
	}
	// Verify corner background was stripped to transparent RGBA(0,0,0,0)
	if c := normCS.Frames[0].RGBAAt(0, 0); c.A != 0 {
		t.Fatalf("expected transparent corner after background strip, got %+v", c)
	}
	rep := ValidateSprite(normCS)
	if !rep.Passed {
		t.Fatalf("normalized sprite failed ValidateSprite: %v", rep.Issues)
	}
	if math.Abs(rep.CenterOfMassX-16.0) > 1.5 {
		t.Fatalf("expected auto-centered CenterOfMassX near 16.0, got %.2f", rep.CenterOfMassX)
	}

	// Test ExtractPaletteRamps on the normalized sheet
	extracted, err := ExtractPaletteRamps(normCS.SheetRGBA, 4)
	if err != nil {
		t.Fatalf("ExtractPaletteRamps failed: %v", err)
	}
	if len(extracted) == 0 {
		t.Fatalf("expected at least 1 extracted material ramp")
	}

	// Verify extracted ramp directive parses and compiles cleanly in a .sprite spec
	r0 := extracted[0]
	customDSL := fmt.Sprintf(`title "Extracted Ramp Test"
type sprite
size 16x16
palette genesis
ramp %s %s %s %s %s
part orb ramp=%s z=0:
  circle 8,8 r=5.0
`, r0.Name, r0.Steps[0], r0.Steps[1], r0.Steps[2], r0.Steps[3], r0.Name)
	if _, err := CompileSpriteDSL(customDSL); err != nil {
		t.Fatalf("failed to compile .sprite with extracted ramp: %v", err)
	}
}

func TestParserFailFastErrors(t *testing.T) {
	badCases := []struct {
		name    string
		dsl     string
		wantSub string
	}{
		{
			name:    "invalid size",
			dsl:     "size 2048x2048\npart a ramp=steel:\n  circle 8,8 r=4\n",
			wantSub: "line 1: invalid size",
		},
		{
			name:    "unknown palette",
			dsl:     "palette unknown_pal\npart a ramp=steel:\n  circle 8,8 r=4\n",
			wantSub: "line 1: unknown palette",
		},
		{
			name:    "unindented primitive",
			dsl:     "part a ramp=steel:\ncircle 8,8 r=4\n",
			wantSub: "line 2: primitive \"circle\" must be indented",
		},
		{
			name:    "unknown ramp reference",
			dsl:     "part a ramp=nonexistent:\n  circle 8,8 r=4\n",
			wantSub: "unknown material ramp",
		},
		{
			name:    "unknown part in pose",
			dsl:     "part a ramp=steel:\n  circle 8,8 r=4\ntag idle frames=2:\n  pose missing_part dy=1\n",
			wantSub: "unknown part \"missing_part\"",
		},
	}

	for _, tc := range badCases {
		t.Run(tc.name, func(t *testing.T) {
			_, err := ParseSpriteDSL(tc.dsl)
			if err == nil {
				t.Fatalf("expected fail-fast error containing %q, got nil", tc.wantSub)
			}
			if !strings.Contains(err.Error(), tc.wantSub) {
				t.Fatalf("expected error containing %q, got %q", tc.wantSub, err.Error())
			}
		})
	}
}
