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
	"bufio"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"math"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/hajimehoshi/ebiten/v2/audio"
)

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	command := os.Args[1]

	switch command {
	case "play":
		playCmd := flag.NewFlagSet("play", flag.ExitOnError)
		loopFlag := playCmd.Bool("loop", false, "Loop SFX audio playback")
		if err := playCmd.Parse(os.Args[2:]); err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing play flags: %v\n", err)
			os.Exit(1)
		}

		if playCmd.NArg() < 1 {
			fmt.Fprintln(os.Stderr, "Error: Missing DSL sound effect file.")
			fmt.Fprintln(os.Stderr, "Usage: go run ./scripts play [-loop] <cue.sfx>")
			os.Exit(1)
		}
		dslFile := playCmd.Arg(0)
		score, err := LoadDSLFile(dslFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error loading DSL file '%s': %v\n", dslFile, err)
			os.Exit(1)
		}

		pcm, err := SynthesizeScore(score)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error synthesizing SFX '%s': %v\n", score.Title, err)
			os.Exit(1)
		}
		pcm = pcm[:len(pcm)&^3]
		fmt.Printf("Playing SFX: '%s' (%s, %d tracks, %.2fs duration, loop=%v)...\n",
			score.Title, score.Type, len(score.Tracks), float64(len(pcm))/float64(BytesPerSecond), *loopFlag)
		playAudio(pcm, *loopFlag)

	case "demo":
		demoCmd := flag.NewFlagSet("demo", flag.ExitOnError)
		loopFlag := demoCmd.Bool("loop", false, "Loop SFX showcase playback")
		if err := demoCmd.Parse(os.Args[2:]); err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing demo flags: %v\n", err)
			os.Exit(1)
		}

		score, err := ParseDSL(DemoSFXShowcaseDSL)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing built-in demo SFX DSL: %v\n", err)
			os.Exit(1)
		}
		pcm, err := SynthesizeScore(score)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error synthesizing demo SFX showcase: %v\n", err)
			os.Exit(1)
		}
		pcm = pcm[:len(pcm)&^3]

		fmt.Printf("Playing Demo SFX Showcase: '%s' (%.2fs duration, loop=%v)...\n",
			score.Title, float64(len(pcm))/float64(BytesPerSecond), *loopFlag)
		playAudio(pcm, *loopFlag)

	case "validate":
		validateCmd := flag.NewFlagSet("validate", flag.ExitOnError)
		if err := validateCmd.Parse(os.Args[2:]); err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing validate flags: %v\n", err)
			os.Exit(1)
		}

		var files []string
		if validateCmd.NArg() > 0 {
			files = validateCmd.Args()
		} else {
			// Find all .sfx files in current directory or parent directories
			matches, _ := filepath.Glob("*.sfx")
			if len(matches) == 0 {
				matches, _ = filepath.Glob("scripts/*.sfx")
			}
			files = matches
		}

		if len(files) == 0 {
			fmt.Println("No .sfx files found to validate. Validating built-in demo SFX showcase:")
			score, err := ParseDSL(DemoSFXShowcaseDSL)
			if err != nil {
				fmt.Fprintf(os.Stderr, "FAIL: ParseDSL failed: %v\n", err)
				os.Exit(1)
			}
			pcm, err := SynthesizeScore(score)
			if err != nil {
				fmt.Fprintf(os.Stderr, "FAIL: SynthesizeScore failed: %v\n", err)
				os.Exit(1)
			}
			rep, err := ValidateProductionSFX(pcm)
			printValidationRow("DemoSFXShowcase", rep, err)
			if err != nil {
				os.Exit(1)
			}
			os.Exit(0)
		}

		hasErrors := false
		fmt.Printf("%-7s | %-24s | %-8s | %-15s | %-10s | %-10s | %-8s\n",
			"STATUS", "CUE / FILE", "DURATION", "PEAK L/R (dBFS)", "RMS (dBFS)", "DC OFFSET", "BOUNDARY")
		fmt.Println(strings.Repeat("-", 95))

		for _, file := range files {
			score, err := LoadDSLFile(file)
			if err != nil {
				fmt.Printf("FAIL    | %-24s | LOAD ERROR: %v\n", filepath.Base(file), err)
				hasErrors = true
				continue
			}
			if err := ValidateScore(score); err != nil {
				fmt.Printf("FAIL    | %-24s | SCORE ERROR: %v\n", filepath.Base(file), err)
				hasErrors = true
				continue
			}
			pcm, err := SynthesizeScore(score)
			if err != nil {
				fmt.Printf("FAIL    | %-24s | SYNTH ERROR: %v\n", filepath.Base(file), err)
				hasErrors = true
				continue
			}
			rep, err := ValidateProductionSFX(pcm)
			printValidationRow(filepath.Base(file), rep, err)
			if err != nil {
				hasErrors = true
				for _, iss := range rep.Issues {
					fmt.Printf("        | -> Issue: %s\n", iss)
				}
			}
		}
		if hasErrors {
			os.Exit(1)
		}

	case "presets", "list-presets":
		presets := ListSFXPresets()
		fmt.Printf("Built-in SFX Archetype Presets (%d available):\n", len(presets))
		fmt.Printf("%-18s | %-10s | %-16s | %-16s | %-8s\n", "PRESET NAME", "WAVE", "SWEEP", "FILTER", "CURVE")
		fmt.Println(strings.Repeat("-", 80))
		for _, name := range presets {
			p, _ := GetSFXPreset(name)
			sweep := "-"
			if p.DefaultStartFreq > 0 && p.DefaultEndFreq > 0 {
				sweep = fmt.Sprintf("%.0f->%.0fHz", p.DefaultStartFreq, p.DefaultEndFreq)
			}
			filter := "-"
			if p.LPFStart > 0 && p.LPFEnd > 0 {
				filter = fmt.Sprintf("LPF:%.0f->%.0f", p.LPFStart, p.LPFEnd)
			} else if p.HPFStart > 0 && p.HPFEnd > 0 {
				filter = fmt.Sprintf("HPF:%.0f->%.0f", p.HPFStart, p.HPFEnd)
			}
			curve := p.PitchCurve
			if curve == "" {
				curve = "exp"
			}
			fmt.Printf("%-18s | %-10s | %-16s | %-16s | %-8s\n", name, p.WaveType, sweep, filter, curve)
		}

	case "export":
		exportCmd := flag.NewFlagSet("export", flag.ExitOnError)
		if err := exportCmd.Parse(os.Args[2:]); err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing export flags: %v\n", err)
			os.Exit(1)
		}

		if exportCmd.NArg() < 2 {
			fmt.Fprintln(os.Stderr, "Error: Missing arguments.")
			fmt.Fprintln(os.Stderr, "Usage: go run ./scripts export <cue.sfx> <output.wav>")
			os.Exit(1)
		}
		dslFile := exportCmd.Arg(0)
		wavFile := exportCmd.Arg(1)

		score, err := LoadDSLFile(dslFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error loading DSL file '%s': %v\n", dslFile, err)
			os.Exit(1)
		}

		pcm, err := SynthesizeScore(score)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error synthesizing SFX '%s': %v\n", score.Title, err)
			os.Exit(1)
		}
		pcm = pcm[:len(pcm)&^3]
		if err := ExportWAV(wavFile, pcm); err != nil {
			fmt.Fprintf(os.Stderr, "Error exporting WAV: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Successfully exported '%s' (%.2fs duration) to '%s'\n",
			score.Title, float64(len(pcm))/float64(BytesPerSecond), wavFile)

	case "synth-json":
		runSFXSynthJSON(os.Args[2:])

	case "presets-json":
		runSFXPresetsJSON()

	default:
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println("Procedural SFX DSL Player, Validator & WAV Exporter CLI")
	fmt.Println()
	fmt.Println("Commands:")
	fmt.Println("  go run ./scripts play [-loop] <cue.sfx>                        Play a .sfx DSL file (one-off default)")
	fmt.Println("  go run ./scripts demo [-loop]                                  Play built-in arcade SFX showcase")
	fmt.Println("  go run ./scripts validate [cue.sfx...]                         Audit and validate SFX against production standards")
	fmt.Println("  go run ./scripts presets                                       List all 18 built-in archetype presets")
	fmt.Println("  go run ./scripts export <cue.sfx> <out.wav>                    Compile .sfx DSL file and export to WAV")
	fmt.Println("  go run ./scripts synth-json [-out <out.wav>] <cue.sfx>         Synthesize and emit JSON report")
	fmt.Println("  go run ./scripts presets-json                                  Emit JSON array of all 18 SFX presets")
}

// TrackMetadataJSON describes a single polyphonic track in an SFX Score for the Sound Studio UI.
type TrackMetadataJSON struct {
	Name        string  `json:"name"`
	DefaultInst string  `json:"defaultInst"`
	WaveType    string  `json:"waveType"`
	Volume      float64 `json:"volume"`
	Pan         float64 `json:"pan"`
	EventCount  int     `json:"eventCount"`
}

// SFXSynthReportJSON is the single-line JSON output emitted by `synth-json`.
type SFXSynthReportJSON struct {
	Passed           bool                `json:"passed"`
	Error            string              `json:"error,omitempty"`
	Title            string              `json:"title"`
	Type             string              `json:"type"`
	BPM              float64             `json:"bpm"`
	DurationSec      float64             `json:"durationSec"`
	PeakLeftDBFS     float64             `json:"peakLeftDBFS"`
	PeakRightDBFS    float64             `json:"peakRightDBFS"`
	PeakDBFS         float64             `json:"peakDBFS"`
	RMSLeftDBFS      float64             `json:"rmsLeftDBFS"`
	RMSRightDBFS     float64             `json:"rmsRightDBFS"`
	RMSDBFS          float64             `json:"rmsDBFS"`
	DCOffset         float64             `json:"dcOffset"`
	DCOffsetL        float64             `json:"dcOffsetL"`
	DCOffsetR        float64             `json:"dcOffsetR"`
	LowFreqEnergyPct float64             `json:"lowFreqEnergyPct"`
	BoundaryClean    bool                `json:"boundaryClean"`
	Issues           []string            `json:"issues"`
	Tracks           []TrackMetadataJSON `json:"tracks"`
	WavPath          string              `json:"wavPath,omitempty"`
}

// SFXPresetJSON describes one built-in SFX archetype preset in `presets-json`.
type SFXPresetJSON struct {
	Name       string  `json:"name"`
	Wave       string  `json:"wave"`
	StartFreq  float64 `json:"startFreq"`
	EndFreq    float64 `json:"endFreq"`
	PitchCurve string  `json:"pitchCurve"`
	DutyStart  float64 `json:"dutyStart"`
	DutyEnd    float64 `json:"dutyEnd"`
	LPFStart   float64 `json:"lpfStart"`
	LPFEnd     float64 `json:"lpfEnd"`
	HPFStart   float64 `json:"hpfStart"`
	HPFEnd     float64 `json:"hpfEnd"`
	Q          float64 `json:"q"`
	Attack     float64 `json:"attack"`
	Decay      float64 `json:"decay"`
	Sustain    float64 `json:"sustain"`
	Release    float64 `json:"release"`
	Volume     float64 `json:"volume"`
}

func safeDBFS(amp float64) float64 {
	if amp <= 1e-6 || math.IsNaN(amp) || math.IsInf(amp, 0) {
		return -120.0
	}
	return math.Round(20.0*math.Log10(amp)*100.0) / 100.0
}

func safeRound(val float64, decimals int) float64 {
	if math.IsNaN(val) || math.IsInf(val, 0) {
		return 0.0
	}
	pow := math.Pow(10, float64(decimals))
	return math.Round(val*pow) / pow
}

func emitSFXJSONError(err error) {
	msg := "unknown error"
	if err != nil {
		msg = err.Error()
	}
	rep := SFXSynthReportJSON{
		Passed: false,
		Error:  msg,
		Issues: []string{msg},
		Tracks: []TrackMetadataJSON{},
	}
	b, _ := json.Marshal(rep)
	fmt.Println(string(b))
}

func extractSFXTrackMetadata(score *Score) []TrackMetadataJSON {
	if score == nil || len(score.Tracks) == 0 {
		return []TrackMetadataJSON{}
	}
	tracks := make([]TrackMetadataJSON, 0, len(score.Tracks))
	for _, tr := range score.Tracks {
		meta := TrackMetadataJSON{
			Name:        tr.Name,
			DefaultInst: tr.DefaultInst,
			WaveType:    "sine",
			Volume:      0.2,
			Pan:         0.0,
			EventCount:  len(tr.Events),
		}
		if tr.DefaultInst != "" {
			if inst, ok := score.Instruments[tr.DefaultInst]; ok {
				meta.WaveType = inst.WaveType
				meta.Volume = safeRound(inst.Volume, 4)
				meta.Pan = safeRound(inst.Pan, 4)
			}
		} else {
			for _, ev := range tr.Events {
				if !ev.IsRest && ev.Inst.WaveType != "" {
					if meta.DefaultInst == "" {
						meta.DefaultInst = ev.Inst.Name
					}
					meta.WaveType = ev.Inst.WaveType
					meta.Volume = safeRound(ev.Inst.Volume, 4)
					meta.Pan = safeRound(ev.Inst.Pan, 4)
					break
				}
			}
		}
		tracks = append(tracks, meta)
	}
	return tracks
}

func runSFXSynthJSON(args []string) {
	synthCmd := flag.NewFlagSet("synth-json", flag.ContinueOnError)
	synthCmd.SetOutput(io.Discard)
	outFlag := synthCmd.String("out", "", "Optional output WAV path")
	if err := synthCmd.Parse(args); err != nil {
		emitSFXJSONError(fmt.Errorf("parse synth-json flags: %w", err))
		return
	}
	if synthCmd.NArg() < 1 {
		emitSFXJSONError(fmt.Errorf("missing DSL SFX file path"))
		return
	}

	dslFile := synthCmd.Arg(0)
	score, err := LoadDSLFile(dslFile)
	if err != nil {
		emitSFXJSONError(err)
		return
	}

	issues := []string{}
	if err := ValidateScore(score); err != nil {
		issues = append(issues, err.Error())
	}

	pcm, err := SynthesizeScore(score)
	if err != nil {
		emitSFXJSONError(err)
		return
	}
	pcm = pcm[:len(pcm)&^3]

	if *outFlag != "" {
		if err := ExportWAV(*outFlag, pcm); err != nil {
			emitSFXJSONError(fmt.Errorf("export WAV: %w", err))
			return
		}
	}

	valRep, _ := ValidateProductionSFX(pcm)
	if len(valRep.Issues) > 0 {
		issues = append(issues, valRep.Issues...)
	}

	alignedLen := len(pcm) &^ 3
	var lpState, sumSqLow, sumSqMono float64
	const lpAlpha = 0.035
	for i := 0; i < alignedLen; i += 4 {
		sL := float64(int16(uint16(pcm[i])|(uint16(pcm[i+1])<<8))) / 32768.0
		sR := float64(int16(uint16(pcm[i+2])|(uint16(pcm[i+3])<<8))) / 32768.0
		mono := (sL + sR) * 0.5
		lpState += lpAlpha * (mono - lpState)
		sumSqLow += lpState * lpState
		sumSqMono += mono * mono
	}
	lowFreqEnergyPct := 0.0
	if sumSqMono > 1e-12 {
		lowFreqEnergyPct = (sumSqLow / sumSqMono) * 100.0
	}

	boundaryClean := math.Abs(float64(valRep.StartSampleLeft)) <= 300 &&
		math.Abs(float64(valRep.StartSampleRight)) <= 300 &&
		math.Abs(float64(valRep.EndSampleLeft)) <= 300 &&
		math.Abs(float64(valRep.EndSampleRight)) <= 300

	rep := SFXSynthReportJSON{
		Passed:           len(issues) == 0 && valRep.Passed,
		Title:            score.Title,
		Type:             score.Type,
		BPM:              safeRound(score.BPM, 2),
		DurationSec:      safeRound(valRep.DurationSec, 4),
		PeakLeftDBFS:     safeDBFS(valRep.PeakLeft),
		PeakRightDBFS:    safeDBFS(valRep.PeakRight),
		PeakDBFS:         safeRound(valRep.PeakDBFS, 2),
		RMSLeftDBFS:      safeDBFS(valRep.RMSLeft),
		RMSRightDBFS:     safeDBFS(valRep.RMSRight),
		RMSDBFS:          safeRound(valRep.RMSDBFS, 2),
		DCOffset:         safeRound((valRep.DCOffsetLeft+valRep.DCOffsetRight)/2.0, 5),
		DCOffsetL:        safeRound(valRep.DCOffsetLeft, 5),
		DCOffsetR:        safeRound(valRep.DCOffsetRight, 5),
		LowFreqEnergyPct: safeRound(lowFreqEnergyPct, 2),
		BoundaryClean:    boundaryClean,
		Issues:           issues,
		Tracks:           extractSFXTrackMetadata(score),
		WavPath:          *outFlag,
	}
	b, _ := json.Marshal(rep)
	fmt.Println(string(b))
}

func runSFXPresetsJSON() {
	names := ListSFXPresets()
	out := make([]SFXPresetJSON, 0, len(names))
	for _, name := range names {
		p, ok := GetSFXPreset(name)
		if !ok {
			continue
		}
		curve := p.PitchCurve
		if curve == "" {
			curve = "exp"
		}
		q := p.ResonanceQ
		if q <= 0 {
			q = 0.707
		}
		dutyStart := p.DutyStart
		dutyEnd := p.DutyEnd
		if dutyStart <= 0 && p.DutyCycle > 0 {
			dutyStart = p.DutyCycle
		}
		if dutyEnd <= 0 && dutyStart > 0 {
			dutyEnd = dutyStart
		}
		out = append(out, SFXPresetJSON{
			Name:       name,
			Wave:       p.WaveType,
			StartFreq:  safeRound(p.DefaultStartFreq, 2),
			EndFreq:    safeRound(p.DefaultEndFreq, 2),
			PitchCurve: curve,
			DutyStart:  safeRound(dutyStart, 3),
			DutyEnd:    safeRound(dutyEnd, 3),
			LPFStart:   safeRound(p.LPFStart, 2),
			LPFEnd:     safeRound(p.LPFEnd, 2),
			HPFStart:   safeRound(p.HPFStart, 2),
			HPFEnd:     safeRound(p.HPFEnd, 2),
			Q:          safeRound(q, 3),
			Attack:     safeRound(p.Attack, 4),
			Decay:      safeRound(p.Decay, 4),
			Sustain:    safeRound(p.Sustain, 4),
			Release:    safeRound(p.Release, 4),
			Volume:     safeRound(p.Volume, 4),
		})
	}
	b, _ := json.Marshal(out)
	fmt.Println(string(b))
}

func printValidationRow(name string, rep *SFXValidationReport, err error) {
	if rep == nil {
		fmt.Printf("FAIL    | %-24s | NO REPORT: %v\n", name, err)
		return
	}
	status := "PASS"
	if !rep.Passed || err != nil {
		status = "FAIL"
	}
	boundary := "Clean"
	if math.Abs(float64(rep.StartSampleLeft)) > 300 || math.Abs(float64(rep.EndSampleLeft)) > 300 {
		boundary = "Click"
	}
	peakStr := fmt.Sprintf("%.1f / %.1f", rep.PeakDBFS, rep.PeakDBFS)
	if rep.PeakLeft > 0 && rep.PeakRight > 0 {
		peakStr = fmt.Sprintf("%.1f / %.1f", 20.0*math.Log10(rep.PeakLeft), 20.0*math.Log10(rep.PeakRight))
	}
	dcStr := fmt.Sprintf("%+.4f", (rep.DCOffsetLeft+rep.DCOffsetRight)/2.0)
	fmt.Printf("%-7s | %-24s | %-7.2fs | %-15s | %-9.1f | %-10s | %-8s\n",
		status, name, rep.DurationSec, peakStr, rep.RMSDBFS, dcStr, boundary)
}

func playAudio(pcm []byte, loop bool) {
	alignedLen := len(pcm) &^ 3
	if alignedLen == 0 {
		fmt.Fprintf(os.Stderr, "Playback error: PCM buffer is empty or smaller than 4-byte stereo frame (%d bytes)\n", len(pcm))
		os.Exit(1)
	}
	pcm = pcm[:alignedLen]

	audioCtx := audio.NewContext(SampleRate)
	sys := NewSoundSystem(audioCtx)
	if err := sys.Play(pcm, loop); err != nil {
		fmt.Fprintf(os.Stderr, "Playback error: %v\n", err)
		os.Exit(1)
	}

	if loop {
		fmt.Println("Looping playback active. Press ENTER to stop...")
		reader := bufio.NewReader(os.Stdin)
		if _, err := reader.ReadString('\n'); err != nil && !errors.Is(err, io.EOF) {
			sys.Stop()
			fmt.Fprintf(os.Stderr, "Error reading stdin: %v\n", err)
			os.Exit(1)
		}
		sys.Stop()
	} else {
		duration := time.Duration(float64(alignedLen)/float64(BytesPerSecond)*1000) * time.Millisecond
		time.Sleep(duration + 100*time.Millisecond)
	}
}

// DemoSFXShowcaseDSL demonstrates classic arcade sound effects (Laser, Coin, Jump, FM Armor Hit, Explosion) in the DSL.
const DemoSFXShowcaseDSL = `
title "Arcade SFX Showcase (Laser, Coin, Jump, Armor Clang, Explosion)"
type sfx

inst laser     wave=square   duty=0.25 vol=0.30 adsr=0.005,0.04,0.20,0.085
inst coin      wave=square   duty=0.50 vol=0.25 adsr=0.005,0.02,0.50,0.045
inst jump      wave=square   duty=0.25 vol=0.28 adsr=0.005,0.05,0.60,0.060
inst clang     wave=fm       mod_freq=587Hz mod_index=4.5 vol=0.30 adsr=0.002,0.06,0.15,0.12
inst boom      wave=noise    noise_filter=0.12 vol=0.40 adsr=0.010,0.25,0.20,0.59 lpf=0.30

seq:
  laser(950Hz->120Hz):150ms R:150ms |
  coin(B5):70ms coin(E6):220ms R:150ms |
  jump(180Hz->620Hz):180ms R:150ms |
  clang(420Hz->190Hz):200ms R:150ms |
  boom:850ms
`
