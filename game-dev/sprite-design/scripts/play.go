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
	"flag"
	"fmt"
	"image"
	"image/color"
	_ "image/jpeg"
	_ "image/png"
	"io"
	"os"
	"path/filepath"
	"strings"
)

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	command := os.Args[1]
	switch command {
	case "validate":
		runValidateCmd(os.Args[2:])
	case "export":
		runExportCmd(os.Args[2:])
	case "normalize":
		runNormalizeCmd(os.Args[2:])
	case "extract-palette":
		runExtractPaletteCmd(os.Args[2:])
	case "synth-json":
		runSynthJSONCmd(os.Args[2:])
	case "inspect-json":
		runInspectJSONCmd(os.Args[2:])
	default:
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println("Sprite Container, Aseprite Exporter & AI Sheet Normalizer CLI")
	fmt.Println()
	fmt.Println("Commands:")
	fmt.Println("  go run ./scripts validate [file.sprite|file.aseprite|sheet.png...]                  Audit and validate sprites or PNG sheets")
	fmt.Println("  go run ./scripts export [-aseprite <out.aseprite>] [-png <out.png>] [-json <out.json>] <file.sprite>")
	fmt.Println("  go run ./scripts normalize -fw <W> -fh <H> [-out <clean.png>] [-json <out.json>] [-aseprite <out.aseprite>] <raw_sheet.png>")
	fmt.Println("  go run ./scripts extract-palette [-ramps 4] <character_sheet.png>                   Extract 4-step material ramps from image")
	fmt.Println("  go run ./scripts synth-json [-png <out.png>] [-aseprite <out.aseprite>] <file.sprite>")
	fmt.Println("  go run ./scripts inspect-json [-png <out.png>] <file.sprite|file.aseprite>")
}

func runValidateCmd(args []string) {
	valCmd := flag.NewFlagSet("validate", flag.ExitOnError)
	fwFlag := valCmd.Int("fw", 32, "Frame width when validating a raw .png sprite sheet")
	fhFlag := valCmd.Int("fh", 32, "Frame height when validating a raw .png sprite sheet")
	if err := valCmd.Parse(args); err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing validate flags: %v\n", err)
		os.Exit(1)
	}

	var files []string
	if valCmd.NArg() > 0 {
		files = valCmd.Args()
	} else {
		matches, _ := filepath.Glob("*.sprite")
		if len(matches) == 0 {
			matches, _ = filepath.Glob("scripts/*.sprite")
		}
		files = matches
	}

	if len(files) == 0 {
		fmt.Fprintln(os.Stderr, "No .sprite files found to validate.")
		os.Exit(1)
	}

	hasErrors := false
	fmt.Printf("%-7s | %-24s | %-7s | %-7s | %-6s | %-10s | %-9s | %-12s\n",
		"STATUS", "SPRITE / FILE", "TYPE", "SIZE", "FRAMES", "FILL RATIO", "LUM STEPS", "CENTER X,Y")
	fmt.Println(strings.Repeat("-", 98))

	for _, file := range files {
		label := filepath.Base(file)
		var cs *CompiledSprite
		var err error

		if strings.HasSuffix(strings.ToLower(file), ".aseprite") || strings.HasSuffix(strings.ToLower(file), ".ase") {
			cs, err = ImportAseprite(file)
		} else if strings.HasSuffix(strings.ToLower(file), ".png") {
			img, loadErr := loadImageFile(file)
			if loadErr != nil {
				fmt.Printf("FAIL    | %-24s | IMAGE ERROR: %v\n", label, loadErr)
				hasErrors = true
				continue
			}
			cs, err = NormalizeSpriteSheet(img, NormalizeOptions{
				Title:       label,
				FrameWidth:  *fwFlag,
				FrameHeight: *fhFlag,
			})
		} else {
			spec, parseErr := LoadSpriteFile(file)
			if parseErr != nil {
				fmt.Printf("FAIL    | %-24s | PARSE ERROR: %v\n", label, parseErr)
				hasErrors = true
				continue
			}
			cs, err = CompileSprite(spec)
		}

		if err != nil {
			fmt.Printf("FAIL    | %-24s | COMPILE ERROR: %v\n", label, err)
			hasErrors = true
			continue
		}

		rep := ValidateSprite(cs)
		status := "PASS"
		if !rep.Passed {
			status = "FAIL"
			hasErrors = true
		}
		fmt.Printf("%-7s | %-24s | %-7s | %-7s | %-6d | %8.1f%%  | %-9d | %5.1f, %5.1f\n",
			status,
			label,
			cs.Type,
			fmt.Sprintf("%dx%d", cs.FrameW, cs.FrameH),
			len(cs.Frames),
			rep.FillRatioPct,
			rep.LuminanceSteps,
			rep.CenterOfMassX,
			rep.CenterOfMassY,
		)
		for _, iss := range rep.Issues {
			fmt.Printf("        | -> Issue: %s\n", iss)
		}
	}

	if hasErrors {
		os.Exit(1)
	}
}

type stringSliceFlag []string

func (s *stringSliceFlag) String() string {
	return strings.Join(*s, ",")
}

func (s *stringSliceFlag) Set(val string) error {
	*s = append(*s, val)
	return nil
}

func runExportCmd(args []string) {
	expCmd := flag.NewFlagSet("export", flag.ExitOnError)
	aseFlag := expCmd.String("aseprite", "", "Output binary .aseprite file path")
	pngFlag := expCmd.String("png", "", "Output packed .png sprite sheet path")
	jsonFlag := expCmd.String("json", "", "Output Aseprite-compatible .json metadata manifest path")
	previewFlag := expCmd.String("preview", "", "Output magnified nearest-neighbor preview .png path")
	gifDirFlag := expCmd.String("gif-dir", "", "Output directory for per-tag animated .gif motion previews")
	gifPrefixFlag := expCmd.String("gif-prefix", "", "Filename prefix for exported .gif files (default: input stem)")
	scaleFlag := expCmd.Int("scale", 4, "Magnification scale for -preview and -gif-dir (1..16)")
	if err := expCmd.Parse(args); err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing export flags: %v\n", err)
		os.Exit(1)
	}
	if expCmd.NArg() < 1 {
		fmt.Fprintln(os.Stderr, "Error: Missing .sprite file argument.")
		fmt.Fprintln(os.Stderr, "Usage: go run ./scripts export [-aseprite <out.aseprite>] [-png <out.png>] [-json <out.json>] [-preview <out_4x.png>] [-gif-dir <dir>] [-scale 4] <file.sprite>")
		os.Exit(1)
	}

	inputPath := expCmd.Arg(0)
	spec, err := LoadSpriteFile(inputPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error loading .sprite file %q: %v\n", inputPath, err)
		os.Exit(1)
	}

	cs, err := CompileSprite(spec)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error compiling sprite %q: %v\n", spec.Title, err)
		os.Exit(1)
	}

	rep := ValidateSprite(cs)
	if !rep.Passed {
		fmt.Fprintf(os.Stderr, "Error: Sprite %q failed visual QA validation:\n", cs.Title)
		for _, iss := range rep.Issues {
			fmt.Fprintf(os.Stderr, "  - %s\n", iss)
		}
		os.Exit(1)
	}

	stem := strings.TrimSuffix(filepath.Base(inputPath), filepath.Ext(inputPath))
	if *aseFlag == "" && *pngFlag == "" && *jsonFlag == "" && *previewFlag == "" && *gifDirFlag == "" {
		*pngFlag = stem + ".png"
		*aseFlag = stem + ".aseprite"
	}

	if *aseFlag != "" {
		if err := ExportAseprite(*aseFlag, cs); err != nil {
			fmt.Fprintf(os.Stderr, "Error exporting .aseprite: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Exported binary .aseprite (%d frames, %dx%d, %d tags) to %q\n",
			len(cs.Frames), cs.FrameW, cs.FrameH, len(cs.Tags), *aseFlag)
	}

	if *pngFlag != "" || *jsonFlag != "" {
		if err := ExportPNGSheet(*pngFlag, *jsonFlag, cs); err != nil {
			fmt.Fprintf(os.Stderr, "Error exporting PNG/JSON sheet: %v\n", err)
			os.Exit(1)
		}
		if *pngFlag != "" {
			fmt.Printf("Exported premultiplied RGBA PNG sheet (%dx%d, %d cols x %d rows) to %q\n",
				cs.SheetRGBA.Bounds().Dx(), cs.SheetRGBA.Bounds().Dy(), cs.SheetCols, cs.SheetRows, *pngFlag)
		}
		if *jsonFlag != "" {
			fmt.Printf("Exported Aseprite JSON manifest to %q\n", *jsonFlag)
		}
	}

	if *previewFlag != "" {
		if err := ExportPreviewPNG(*previewFlag, *scaleFlag, cs); err != nil {
			fmt.Fprintf(os.Stderr, "Error exporting preview PNG: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Exported %dx magnified preview PNG (%dx%d) to %q\n",
			*scaleFlag, cs.SheetRGBA.Bounds().Dx()**scaleFlag, cs.SheetRGBA.Bounds().Dy()**scaleFlag, *previewFlag)
	}

	if *gifDirFlag != "" {
		prefix := *gifPrefixFlag
		if prefix == "" {
			prefix = stem
		}
		gifs, err := ExportTagGIFs(*gifDirFlag, prefix, *scaleFlag, cs)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error exporting tag GIFs: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Exported %d animated motion GIFs (%dx scale) to %q:\n", len(gifs), *scaleFlag, *gifDirFlag)
		for _, gp := range gifs {
			fmt.Printf("  - %s\n", gp)
		}
	}
}

func runNormalizeCmd(args []string) {
	normCmd := flag.NewFlagSet("normalize", flag.ExitOnError)
	fwFlag := normCmd.Int("fw", 0, "Target frame width in pixels (0 = preserve native cell width w/cols, or 32 if cols=0)")
	fhFlag := normCmd.Int("fh", 0, "Target frame height in pixels (0 = preserve native cell height h/rows, or 32 if rows=0)")
	colsFlag := normCmd.Int("cols", 0, "Grid columns in each input image (0 = infer w / fw)")
	rowsFlag := normCmd.Int("rows", 0, "Grid rows in each input image (0 = infer h / fh)")
	tolFlag := normCmd.Int("tol", 18, "Background color key Manhattan tolerance (0..255)")
	centerFlag := normCmd.Bool("center", true, "Auto-center each frame's opaque bounding box horizontally")
	groundFlag := normCmd.Bool("ground", false, "Ground each frame's bottom edge to (fh - pad)")
	padFlag := normCmd.Int("pad", 2, "Bottom padding in pixels when -ground is true")
	durFlag := normCmd.Int("duration", 100, "Default frame duration in ms")
	outPNG := normCmd.String("out", "", "Output normalized .png sprite sheet path")
	outSprite := normCmd.String("sprite", "", "Optional output .sprite container file path (auto-created alongside -out)")
	outJSON := normCmd.String("json", "", "Optional output .json manifest path")
	outAse := normCmd.String("aseprite", "", "Optional output binary .aseprite file path")
	previewFlag := normCmd.String("preview", "", "Optional output magnified preview .png path")
	gifDirFlag := normCmd.String("gif-dir", "", "Optional output directory for per-tag animated .gif motion previews")
	gifPrefixFlag := normCmd.String("gif-prefix", "", "Filename prefix for exported .gif files")
	scaleFlag := normCmd.Int("scale", 0, "Magnification scale for -preview and -gif-dir (0 = auto: 1x for HD >=128px, 4x for <=64px)")
	reportJSONFlag := normCmd.Bool("report-json", false, "Emit single-line SpriteSynthReportJSON to stdout")
	var tagSpecs stringSliceFlag
	normCmd.Var(&tagSpecs, "tag", "Animation tag spec 'name:from:to[:duration_ms[:loop]]' (repeatable)")

	if err := normCmd.Parse(args); err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing normalize flags: %v\n", err)
		os.Exit(1)
	}
	if normCmd.NArg() < 1 {
		fmt.Fprintln(os.Stderr, "Error: Missing input raw sprite sheet image path(s).")
		fmt.Fprintln(os.Stderr, "Usage: go run ./scripts normalize [-fw <W> -fh <H>] [-cols <C> -rows <R>] [-tag name:from:to:ms:loop ...] [-out <clean.png>] [-gif-dir <dir>] <raw_sheet.png...>")
		os.Exit(1)
	}

	inPaths := normCmd.Args()
	var srcImgs []image.Image
	for _, p := range inPaths {
		img, err := loadImageFile(p)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error reading image %q: %v\n", p, err)
			os.Exit(1)
		}
		srcImgs = append(srcImgs, img)
	}

	var parsedTags []CompiledTag
	for _, ts := range tagSpecs {
		ct, err := ParseNormalizeTagFlag(ts, *durFlag)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing -tag %q: %v\n", ts, err)
			os.Exit(1)
		}
		parsedTags = append(parsedTags, ct)
	}

	fw, fh := *fwFlag, *fhFlag
	if *colsFlag <= 0 && *rowsFlag <= 0 {
		if fw <= 0 {
			fw = 32
		}
		if fh <= 0 {
			fh = 32
		}
	}

	stem := strings.TrimSuffix(filepath.Base(inPaths[0]), filepath.Ext(inPaths[0]))
	cs, err := NormalizeMultiSpriteSheets(srcImgs, NormalizeOptions{
		Title:           stem,
		FrameWidth:      fw,
		FrameHeight:     fh,
		GridCols:        *colsFlag,
		GridRows:        *rowsFlag,
		ColorTolerance:  uint8(*tolFlag),
		AutoCenterX:     *centerFlag,
		GroundBottom:    *groundFlag,
		BottomPadding:   *padFlag,
		DefaultDuration: *durFlag,
		Tags:            parsedTags,
	})
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error normalizing sprite sheet: %v\n", err)
		os.Exit(1)
	}

	effScale := *scaleFlag
	if effScale <= 0 {
		if cs.FrameW >= 128 || cs.FrameH >= 128 {
			effScale = 1
		} else if cs.FrameW >= 64 || cs.FrameH >= 64 {
			effScale = 2
		} else {
			effScale = 4
		}
	}

	if *outPNG != "" || *outJSON != "" {
		if err := ExportPNGSheet(*outPNG, *outJSON, cs); err != nil {
			fmt.Fprintf(os.Stderr, "Error writing normalized PNG/JSON: %v\n", err)
			os.Exit(1)
		}
	}
	spriteOutPath := *outSprite
	if spriteOutPath == "" && *outPNG != "" && !strings.HasPrefix(filepath.Clean(*outPNG), filepath.Clean(os.TempDir())) {
		ext := filepath.Ext(*outPNG)
		spriteOutPath = strings.TrimSuffix(*outPNG, ext) + ".sprite"
	}
	if spriteOutPath != "" && *outPNG != "" {
		if err := ExportSpriteContainer(spriteOutPath, filepath.Base(*outPNG), cs); err != nil {
			fmt.Fprintf(os.Stderr, "Error writing .sprite container: %v\n", err)
			os.Exit(1)
		}
	}
	if *outAse != "" {
		if err := ExportAseprite(*outAse, cs); err != nil {
			fmt.Fprintf(os.Stderr, "Error writing normalized .aseprite: %v\n", err)
			os.Exit(1)
		}
	}
	if *previewFlag != "" {
		if err := ExportPreviewPNG(*previewFlag, effScale, cs); err != nil {
			fmt.Fprintf(os.Stderr, "Error writing preview PNG: %v\n", err)
			os.Exit(1)
		}
	}
	if *gifDirFlag != "" {
		prefix := *gifPrefixFlag
		if prefix == "" {
			prefix = stem
		}
		gifs, err := ExportTagGIFs(*gifDirFlag, prefix, effScale, cs)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error writing tag GIFs: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Exported %d animated motion GIFs (%dx scale, %dx%d) to %q:\n",
			len(gifs), effScale, cs.FrameW*effScale, cs.FrameH*effScale, *gifDirFlag)
		for _, gp := range gifs {
			fmt.Printf("  - %s\n", gp)
		}
	}

	rep := ValidateSprite(cs)
	if *reportJSONFlag {
		b := cs.SheetRGBA.Bounds()
		out := SpriteSynthReportJSON{
			Passed:             rep.Passed,
			Title:              cs.Title,
			Type:               cs.Type,
			Width:              cs.FrameW,
			Height:             cs.FrameH,
			SheetWidth:         b.Dx(),
			SheetHeight:        b.Dy(),
			SheetCols:          cs.SheetCols,
			SheetRows:          cs.SheetRows,
			Palette:            cs.Palette,
			TotalFrames:        len(cs.Frames),
			FillRatioPct:       rep.FillRatioPct,
			OpaquePixelPct:     rep.OpaquePixelPct,
			CenterOfMassX:      rep.CenterOfMassX,
			CenterOfMassY:      rep.CenterOfMassY,
			LuminanceSteps:     rep.LuminanceSteps,
			PremultipliedClean: rep.PremultipliedClean,
			Tags:               cs.Tags,
			Parts:              cs.Parts,
			PaletteColors:      formatPaletteHexes(cs.PaletteColors, 32),
			Issues:             rep.Issues,
			PNGPath:            *outPNG,
			AsepritePath:       *outAse,
		}
		jb, _ := json.Marshal(out)
		fmt.Println(string(jb))
		return
	}
	fmt.Printf("Normalized %d input sheet(s): %d frames (%dx%d), %d tags, fill=%.1f%%, lumSteps=%d, premultipliedClean=%v\n",
		len(inPaths), len(cs.Frames), cs.FrameW, cs.FrameH, len(cs.Tags), rep.FillRatioPct, rep.LuminanceSteps, rep.PremultipliedClean)
}

func runExtractPaletteCmd(args []string) {
	extCmd := flag.NewFlagSet("extract-palette", flag.ExitOnError)
	rampsFlag := extCmd.Int("ramps", 4, "Maximum number of 4-step material ramps to extract (1..12)")
	if err := extCmd.Parse(args); err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing extract-palette flags: %v\n", err)
		os.Exit(1)
	}
	if extCmd.NArg() < 1 {
		fmt.Fprintln(os.Stderr, "Error: Missing reference image path.")
		fmt.Fprintln(os.Stderr, "Usage: go run ./scripts extract-palette [-ramps 4] <character_sheet.png>")
		os.Exit(1)
	}

	imgPath := extCmd.Arg(0)
	img, err := loadImageFile(imgPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error loading image %q: %v\n", imgPath, err)
		os.Exit(1)
	}

	ramps, err := ExtractPaletteRamps(img, *rampsFlag)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error extracting palette ramps: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("// Extracted %d material ramps from %s\n", len(ramps), filepath.Base(imgPath))
	for _, r := range ramps {
		fmt.Printf("ramp %-10s %s %s %s %s\n", r.Name, r.Steps[0], r.Steps[1], r.Steps[2], r.Steps[3])
	}
}

// SpriteSynthReportJSON is the single-line JSON report emitted by `synth-json` and `inspect-json`.
type SpriteSynthReportJSON struct {
	Passed             bool          `json:"passed"`
	Error              string        `json:"error,omitempty"`
	Title              string        `json:"title"`
	Type               string        `json:"type"`
	Width              int           `json:"width"`
	Height             int           `json:"height"`
	SheetWidth         int           `json:"sheetWidth"`
	SheetHeight        int           `json:"sheetHeight"`
	SheetCols          int           `json:"sheetCols"`
	SheetRows          int           `json:"sheetRows"`
	Palette            string        `json:"palette"`
	TotalFrames        int           `json:"totalFrames"`
	FillRatioPct       float64       `json:"fillRatioPct"`
	OpaquePixelPct     float64       `json:"opaquePixelPct"`
	CenterOfMassX      float64       `json:"centerOfMassX"`
	CenterOfMassY      float64       `json:"centerOfMassY"`
	LuminanceSteps     int           `json:"luminanceSteps"`
	PremultipliedClean bool          `json:"premultipliedClean"`
	Tags               []CompiledTag `json:"tags"`
	Parts              []PartSummary `json:"parts"`
	PaletteColors      []string      `json:"paletteColors,omitempty"`
	Issues             []string      `json:"issues"`
	PNGPath            string        `json:"pngPath,omitempty"`
	AsepritePath       string        `json:"asepritePath,omitempty"`
}

func formatPaletteHexes(cols []color.RGBA, maxCount int) []string {
	if maxCount <= 0 {
		maxCount = 24
	}
	var picked []color.RGBA
	out := make([]string, 0, maxCount)
	seen := make(map[string]bool)
	for _, minDist := range []int{36, 18, 0} {
		for _, c := range cols {
			if c.A < 200 {
				continue
			}
			hex := fmt.Sprintf("#%02X%02X%02X", c.R, c.G, c.B)
			if seen[hex] {
				continue
			}
			if minDist > 0 {
				tooClose := false
				for _, p := range picked {
					if colorDistManhattan(c, p) < minDist {
						tooClose = true
						break
					}
				}
				if tooClose {
					continue
				}
			}
			seen[hex] = true
			picked = append(picked, c)
			out = append(out, hex)
			if len(out) >= maxCount {
				return out
			}
		}
	}
	return out
}

func emitSynthJSONError(err error) {
	msg := "unknown error"
	if err != nil {
		msg = err.Error()
	}
	rep := SpriteSynthReportJSON{
		Passed: false,
		Error:  msg,
		Tags:   []CompiledTag{},
		Parts:  []PartSummary{},
		Issues: []string{msg},
	}
	b, _ := json.Marshal(rep)
	fmt.Println(string(b))
}

func runSynthJSONCmd(args []string) {
	sCmd := flag.NewFlagSet("synth-json", flag.ContinueOnError)
	sCmd.SetOutput(io.Discard)
	pngFlag := sCmd.String("png", "", "Optional output PNG sprite sheet path")
	aseFlag := sCmd.String("aseprite", "", "Optional output binary .aseprite path")
	if err := sCmd.Parse(args); err != nil {
		emitSynthJSONError(fmt.Errorf("parse synth-json flags: %w", err))
		return
	}
	if sCmd.NArg() < 1 {
		emitSynthJSONError(fmt.Errorf("missing .sprite file path"))
		return
	}

	inputPath := sCmd.Arg(0)
	spec, err := LoadSpriteFile(inputPath)
	if err != nil {
		emitSynthJSONError(err)
		return
	}

	cs, err := CompileSprite(spec)
	if err != nil {
		emitSynthJSONError(err)
		return
	}

	if *pngFlag != "" {
		if err := ExportPNGSheet(*pngFlag, "", cs); err != nil {
			emitSynthJSONError(err)
			return
		}
	}
	if *aseFlag != "" {
		if err := ExportAseprite(*aseFlag, cs); err != nil {
			emitSynthJSONError(err)
			return
		}
	}

	valRep := ValidateSprite(cs)
	b := cs.SheetRGBA.Bounds()
	out := SpriteSynthReportJSON{
		Passed:             valRep.Passed,
		Title:              cs.Title,
		Type:               cs.Type,
		Width:              cs.FrameW,
		Height:             cs.FrameH,
		SheetWidth:         b.Dx(),
		SheetHeight:        b.Dy(),
		SheetCols:          cs.SheetCols,
		SheetRows:          cs.SheetRows,
		Palette:            cs.Palette,
		TotalFrames:        len(cs.Frames),
		FillRatioPct:       valRep.FillRatioPct,
		OpaquePixelPct:     valRep.OpaquePixelPct,
		CenterOfMassX:      valRep.CenterOfMassX,
		CenterOfMassY:      valRep.CenterOfMassY,
		LuminanceSteps:     valRep.LuminanceSteps,
		PremultipliedClean: valRep.PremultipliedClean,
		Tags:               cs.Tags,
		Parts:              cs.Parts,
		PaletteColors:      formatPaletteHexes(cs.PaletteColors, 32),
		Issues:             valRep.Issues,
		PNGPath:            *pngFlag,
		AsepritePath:       *aseFlag,
	}
	jb, _ := json.Marshal(out)
	fmt.Println(string(jb))
}

func runInspectJSONCmd(args []string) {
	iCmd := flag.NewFlagSet("inspect-json", flag.ContinueOnError)
	iCmd.SetOutput(io.Discard)
	fwFlag := iCmd.Int("fw", 0, "Optional explicit frame width")
	fhFlag := iCmd.Int("fh", 0, "Optional explicit frame height")
	colsFlag := iCmd.Int("cols", 0, "Optional explicit grid columns")
	rowsFlag := iCmd.Int("rows", 0, "Optional explicit grid rows")
	jsonFlag := iCmd.String("json", "", "Optional companion Aseprite JSON manifest path")
	pngOutFlag := iCmd.String("png", "", "Optional output PNG path when inspecting .aseprite or .sprite containers")
	if err := iCmd.Parse(args); err != nil {
		emitSynthJSONError(fmt.Errorf("parse inspect-json flags: %w", err))
		return
	}
	if iCmd.NArg() < 1 {
		emitSynthJSONError(fmt.Errorf("missing sprite container or sheet path"))
		return
	}

	imgPath := iCmd.Arg(0)
	lowerPath := strings.ToLower(imgPath)

	// Container branch 1: .aseprite / .ase binary file
	if strings.HasSuffix(lowerPath, ".aseprite") || strings.HasSuffix(lowerPath, ".ase") {
		cs, err := ImportAseprite(imgPath)
		if err != nil {
			emitSynthJSONError(err)
			return
		}
		if *pngOutFlag != "" {
			if err := ExportPNGSheet(*pngOutFlag, "", cs); err != nil {
				emitSynthJSONError(err)
				return
			}
		}
		valRep := ValidateSprite(cs)
		b := cs.SheetRGBA.Bounds()
		out := SpriteSynthReportJSON{
			Passed:             valRep.Passed,
			Title:              cs.Title,
			Type:               cs.Type,
			Width:              cs.FrameW,
			Height:             cs.FrameH,
			SheetWidth:         b.Dx(),
			SheetHeight:        b.Dy(),
			SheetCols:          cs.SheetCols,
			SheetRows:          cs.SheetRows,
			Palette:            cs.Palette,
			TotalFrames:        len(cs.Frames),
			FillRatioPct:       valRep.FillRatioPct,
			OpaquePixelPct:     valRep.OpaquePixelPct,
			CenterOfMassX:      valRep.CenterOfMassX,
			CenterOfMassY:      valRep.CenterOfMassY,
			LuminanceSteps:     valRep.LuminanceSteps,
			PremultipliedClean: valRep.PremultipliedClean,
			Tags:               cs.Tags,
			Parts:              []PartSummary{},
			PaletteColors:      formatPaletteHexes(cs.PaletteColors, 32),
			Issues:             valRep.Issues,
			PNGPath:            *pngOutFlag,
			AsepritePath:       imgPath,
		}
		jb, _ := json.Marshal(out)
		fmt.Println(string(jb))
		return
	}

	// Container branch 2: .sprite container or procedural DSL file
	if strings.HasSuffix(lowerPath, ".sprite") {
		spec, err := LoadSpriteFile(imgPath)
		if err != nil {
			emitSynthJSONError(err)
			return
		}
		if *fwFlag > 0 && *fhFlag > 0 {
			spec.Width = *fwFlag
			spec.Height = *fhFlag
		}
		if *colsFlag > 0 && *rowsFlag > 0 {
			spec.GridCols = *colsFlag
			spec.GridRows = *rowsFlag
		}
		cs, err := CompileSprite(spec)
		if err != nil {
			emitSynthJSONError(err)
			return
		}
		pngPath := ""
		if *pngOutFlag != "" {
			if err := ExportPNGSheet(*pngOutFlag, "", cs); err != nil {
				emitSynthJSONError(err)
				return
			}
			pngPath = *pngOutFlag
		} else if spec.SheetPath != "" {
			if filepath.IsAbs(spec.SheetPath) {
				pngPath = spec.SheetPath
			} else {
				pngPath = filepath.Join(spec.BaseDir, spec.SheetPath)
			}
		}
		valRep := ValidateSprite(cs)
		b := cs.SheetRGBA.Bounds()
		out := SpriteSynthReportJSON{
			Passed:             valRep.Passed,
			Title:              cs.Title,
			Type:               cs.Type,
			Width:              cs.FrameW,
			Height:             cs.FrameH,
			SheetWidth:         b.Dx(),
			SheetHeight:        b.Dy(),
			SheetCols:          cs.SheetCols,
			SheetRows:          cs.SheetRows,
			Palette:            cs.Palette,
			TotalFrames:        len(cs.Frames),
			FillRatioPct:       valRep.FillRatioPct,
			OpaquePixelPct:     valRep.OpaquePixelPct,
			CenterOfMassX:      valRep.CenterOfMassX,
			CenterOfMassY:      valRep.CenterOfMassY,
			LuminanceSteps:     valRep.LuminanceSteps,
			PremultipliedClean: valRep.PremultipliedClean,
			Tags:               cs.Tags,
			Parts:              cs.Parts,
			PaletteColors:      formatPaletteHexes(cs.PaletteColors, 32),
			Issues:             valRep.Issues,
			PNGPath:            pngPath,
		}
		jb, _ := json.Marshal(out)
		fmt.Println(string(jb))
		return
	}

	img, err := loadImageFile(imgPath)
	if err != nil {
		emitSynthJSONError(fmt.Errorf("read image %q: %w", imgPath, err))
		return
	}
	rgba := toPremultipliedRGBA(img)
	b := rgba.Bounds()
	w, h := b.Dx(), b.Dy()

	stem := strings.TrimSuffix(filepath.Base(imgPath), filepath.Ext(imgPath))
	manifestPath := *jsonFlag
	if manifestPath == "" {
		cand := strings.TrimSuffix(imgPath, filepath.Ext(imgPath)) + ".json"
		if fileExists(cand) {
			manifestPath = cand
		}
	}

	fw, fh := *fwFlag, *fhFlag
	cols, rows := *colsFlag, *rowsFlag
	var tags []CompiledTag

	if manifestPath != "" && fileExists(manifestPath) {
		if jb, readErr := os.ReadFile(manifestPath); readErr == nil {
			var man AsepriteSheetJSON
			if json.Unmarshal(jb, &man) == nil {
				if fw <= 0 && man.Meta.FrameWidth > 0 {
					fw = man.Meta.FrameWidth
				}
				if fh <= 0 && man.Meta.FrameHeight > 0 {
					fh = man.Meta.FrameHeight
				}
				if cols <= 0 && man.Meta.Cols > 0 {
					cols = man.Meta.Cols
				}
				if rows <= 0 && man.Meta.Rows > 0 {
					rows = man.Meta.Rows
				}
				if len(man.Meta.FrameTags) > 0 {
					tags = man.Meta.FrameTags
				}
			}
		}
	}

	if fw <= 0 || fh <= 0 {
		if cols > 0 && rows > 0 {
			fw = w / cols
			fh = h / rows
		} else if w == h && w%4 == 0 {
			cols, rows = 4, 4
			fw, fh = w/4, h/4
		} else if h > 0 && w >= h && w%h == 0 {
			cols = w / h
			rows = 1
			fw, fh = h, h
		} else if w%4 == 0 && h%4 == 0 {
			cols, rows = 4, 4
			fw, fh = w/4, h/4
		} else {
			cols, rows = 1, 1
			fw, fh = w, h
		}
	}
	if cols <= 0 && fw > 0 {
		cols = maxInt(1, w/fw)
	}
	if rows <= 0 && fh > 0 {
		rows = maxInt(1, h/fh)
	}

	var frames []*image.RGBA
	var durations []int
	for r := 0; r < rows; r++ {
		for c := 0; c < cols; c++ {
			cell := image.NewRGBA(image.Rect(0, 0, fw, fh))
			hasOpaque := false
			for y := 0; y < fh && r*fh+y < h; y++ {
				for x := 0; x < fw && c*fw+x < w; x++ {
					px := rgba.RGBAAt(c*fw+x, r*fh+y)
					if px.A > 0 {
						hasOpaque = true
					}
					cell.SetRGBA(x, y, px)
				}
			}
			if hasOpaque || len(tags) > 0 {
				frames = append(frames, cell)
				durations = append(durations, 100)
			}
		}
	}
	if len(frames) == 0 {
		frames = append(frames, rgba)
		durations = append(durations, 100)
	}
	if len(tags) == 0 {
		tags = []CompiledTag{
			{
				Name:       "all",
				FromFrame:  0,
				ToFrame:    len(frames) - 1,
				Frames:     len(frames),
				DurationMs: 100,
				Loop:       "forward",
			},
		}
	}

	cs := &CompiledSprite{
		Title:          stem,
		Type:           "sprite",
		FrameW:         fw,
		FrameH:         fh,
		Palette:        "custom",
		Frames:         frames,
		FrameDurations: durations,
		Tags:           tags,
		PaletteColors:  collectUniqueColors(rgba),
		SheetRGBA:      rgba,
		SheetCols:      cols,
		SheetRows:      rows,
	}
	valRep := ValidateSprite(cs)
	out := SpriteSynthReportJSON{
		Passed:             valRep.Passed,
		Title:              cs.Title,
		Type:               cs.Type,
		Width:              cs.FrameW,
		Height:             cs.FrameH,
		SheetWidth:         w,
		SheetHeight:        h,
		SheetCols:          cols,
		SheetRows:          rows,
		Palette:            cs.Palette,
		TotalFrames:        len(cs.Frames),
		FillRatioPct:       valRep.FillRatioPct,
		OpaquePixelPct:     valRep.OpaquePixelPct,
		CenterOfMassX:      valRep.CenterOfMassX,
		CenterOfMassY:      valRep.CenterOfMassY,
		LuminanceSteps:     valRep.LuminanceSteps,
		PremultipliedClean: valRep.PremultipliedClean,
		Tags:               cs.Tags,
		Parts:              []PartSummary{},
		PaletteColors:      formatPaletteHexes(cs.PaletteColors, 32),
		Issues:             valRep.Issues,
		PNGPath:            imgPath,
	}
	jb, _ := json.Marshal(out)
	fmt.Println(string(jb))
}

func loadImageFile(path string) (image.Image, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	img, _, err := image.Decode(f)
	return img, err
}

func fileExists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}
