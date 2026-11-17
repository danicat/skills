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
	"encoding/binary"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"math"
	"os"
	"sort"
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
		loopFlag := playCmd.Bool("loop", false, "Loop BGM audio playback")
		appleFlag := playCmd.Bool("apple", false, "Render using macOS Apple CoreAudio real instruments")
		if err := playCmd.Parse(os.Args[2:]); err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing play flags: %v\n", err)
			os.Exit(1)
		}

		if playCmd.NArg() < 1 {
			fmt.Fprintln(os.Stderr, "Error: Missing DSL music file.")
			fmt.Fprintln(os.Stderr, "Usage: go run ./scripts play [-loop] [-apple] <song.music>")
			os.Exit(1)
		}
		dslFile := playCmd.Arg(0)
		score, err := LoadDSLFile(dslFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error loading DSL file '%s': %v\n", dslFile, err)
			os.Exit(1)
		}
		if *appleFlag {
			score.SynthEngine = "apple"
		}

		pcm, err := SynthesizeScore(score)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error synthesizing score '%s': %v\n", score.Title, err)
			os.Exit(1)
		}
		pcm = pcm[:len(pcm)&^3]
		engineName := score.SynthEngine
		if engineName == "" {
			engineName = "default"
		}
		fmt.Printf("Playing music: '%s' (%s, synth=%s, %.0f BPM, %d tracks, %.2fs duration, loop=%v)...\n",
			score.Title, score.Type, engineName, score.BPM, len(score.Tracks), float64(len(pcm))/float64(BytesPerSecond), *loopFlag)
		playAudio(pcm, *loopFlag)

	case "demo":
		demoCmd := flag.NewFlagSet("demo", flag.ExitOnError)
		loopFlag := demoCmd.Bool("loop", false, "Loop BGM audio playback")
		appleFlag := demoCmd.Bool("apple", false, "Render using macOS Apple CoreAudio real instruments")
		if err := demoCmd.Parse(os.Args[2:]); err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing demo flags: %v\n", err)
			os.Exit(1)
		}

		score, err := ParseDSL(DemoStageBGMDSL)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing built-in demo DSL: %v\n", err)
			os.Exit(1)
		}
		if *appleFlag {
			score.SynthEngine = "apple"
		}
		pcm, err := SynthesizeScore(score)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error synthesizing demo soundtrack: %v\n", err)
			os.Exit(1)
		}
		pcm = pcm[:len(pcm)&^3]
		engineName := score.SynthEngine
		if engineName == "" {
			engineName = "default"
		}

		fmt.Printf("Playing Demo Soundtrack: '%s' (synth=%s, %.0f BPM, %.2fs duration, loop=%v)...\n",
			score.Title, engineName, score.BPM, float64(len(pcm))/float64(BytesPerSecond), *loopFlag)
		playAudio(pcm, *loopFlag)

	case "export":
		exportCmd := flag.NewFlagSet("export", flag.ExitOnError)
		appleFlag := exportCmd.Bool("apple", false, "Render using macOS Apple CoreAudio real instruments")
		if err := exportCmd.Parse(os.Args[2:]); err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing export flags: %v\n", err)
			os.Exit(1)
		}

		if exportCmd.NArg() < 2 {
			fmt.Fprintln(os.Stderr, "Error: Missing arguments.")
			fmt.Fprintln(os.Stderr, "Usage: go run ./scripts export [-apple] <song.music> <output.wav>")
			os.Exit(1)
		}
		dslFile := exportCmd.Arg(0)
		wavFile := exportCmd.Arg(1)

		score, err := LoadDSLFile(dslFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error loading DSL file '%s': %v\n", dslFile, err)
			os.Exit(1)
		}
		if *appleFlag {
			score.SynthEngine = "apple"
		}

		pcm, err := SynthesizeScore(score)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error synthesizing score '%s': %v\n", score.Title, err)
			os.Exit(1)
		}
		pcm = pcm[:len(pcm)&^3]
		if err := ExportWAV(wavFile, pcm); err != nil {
			fmt.Fprintf(os.Stderr, "Error exporting WAV: %v\n", err)
			os.Exit(1)
		}
		engineName := score.SynthEngine
		if engineName == "" {
			engineName = "default"
		}
		fmt.Printf("Successfully exported '%s' (synth=%s, %.2fs duration) to '%s'\n",
			score.Title, engineName, float64(len(pcm))/float64(BytesPerSecond), wavFile)

	case "validate":
		valCmd := flag.NewFlagSet("validate", flag.ExitOnError)
		minCh := valCmd.Int("min-channels", 8, "Minimum required channels for production BGM")
		minDur := valCmd.Float64("min-duration", 30.0, "Minimum required duration in seconds for production BGM")
		if err := valCmd.Parse(os.Args[2:]); err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing validate flags: %v\n", err)
			os.Exit(1)
		}
		if valCmd.NArg() < 1 {
			fmt.Fprintln(os.Stderr, "Error: Missing DSL music file.")
			fmt.Fprintln(os.Stderr, "Usage: go run ./scripts validate [-min-channels 8] [-min-duration 30] <song.music>")
			os.Exit(1)
		}
		dslFile := valCmd.Arg(0)
		score, err := LoadDSLFile(dslFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error loading DSL file '%s': %v\n", dslFile, err)
			os.Exit(1)
		}
		if err := ValidateProductionBGM(score, *minCh, *minDur); err != nil {
			fmt.Fprintf(os.Stderr, "Validation FAILED for '%s': %v\n", dslFile, err)
			os.Exit(1)
		}
		var totalSec float64
		if len(score.Tracks) > 0 {
			for _, ev := range score.Tracks[0].Events {
				totalSec += ev.DurationSec
			}
		}
		fmt.Printf("Validation PASSED: '%s' (%d channels, %.2fs duration, zero drift, zero harmonic clashes)\n",
			score.Title, len(score.Tracks), totalSec)

	case "synth-json":
		runMusicSynthJSON(os.Args[2:])

	case "presets-json":
		runMusicPresetsJSON()

	default:
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println("Procedural Music DSL Player, Validator & WAV Exporter CLI")
	fmt.Println()
	fmt.Println("Commands:")
	fmt.Println("  go run ./scripts play [-loop] [-apple] <song.music>            Play a .music DSL file")
	fmt.Println("  go run ./scripts demo [-loop] [-apple]                         Play built-in 16-bar Genesis soundtrack")
	fmt.Println("  go run ./scripts export [-apple] <song.music> <out.wav>        Compile .music DSL file and export to WAV")
	fmt.Println("  go run ./scripts validate <song.music>                         Validate music theory, consonance, channels & duration")
	fmt.Println("  go run ./scripts synth-json [-apple] [-out <out.wav>] <song.music> Synthesize and emit JSON report")
	fmt.Println("  go run ./scripts presets-json                                  Emit JSON catalog of wave types, YM2612 presets & tempo markings")
}

// TrackMetadataJSON describes a single polyphonic track in a Score for the Sound Studio UI.
type TrackMetadataJSON struct {
	Name        string  `json:"name"`
	DefaultInst string  `json:"defaultInst"`
	WaveType    string  `json:"waveType"`
	Volume      float64 `json:"volume"`
	Pan         float64 `json:"pan"`
	EventCount  int     `json:"eventCount"`
}

// MusicSynthReportJSON is the single-line JSON output emitted by `synth-json`.
type MusicSynthReportJSON struct {
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

// SynthesizeScoreWithOptions renders a parsed Score using either the default YM2612/PSG engine or Apple CoreAudio.
func SynthesizeScoreWithOptions(score *Score, useApple bool) ([]byte, error) {
	mixed, _, err := SynthesizeScoreStemsWithOptions(score, useApple)
	return mixed, err
}

// SynthesizeScoreStemsWithOptions renders a parsed Score into both a master mix and per-track stem buffers.
func SynthesizeScoreStemsWithOptions(score *Score, useApple bool) ([]byte, [][]byte, error) {
	if score == nil {
		return nil, nil, fmt.Errorf("synthesize score: score is nil")
	}
	sc := *score
	if useApple {
		sc.SynthEngine = "apple"
	}
	return SynthesizeScoreWithStems(&sc)
}

// ExportStemsBinary writes all rendered per-track 16-bit 44.1kHz stereo PCM stems into a single framed binary file.
// Format:
//   [0..3]   "STEM" magic bytes
//   [4..7]   uint32 sampleRate (44100)
//   [8..11]  uint32 trackCount
//   For each track:
//     uint16 nameByteLen
//     []byte trackName (UTF-8)
//     uint32 pcmByteLen (4-byte aligned)
//     []byte pcmBytes (16-bit little-endian stereo interleaved L,R)
func ExportStemsBinary(filename string, tracks []Track, trackPCMs [][]byte) (retErr error) {
	f, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer func() {
		if closeErr := f.Close(); closeErr != nil && retErr == nil {
			retErr = closeErr
		}
	}()

	bw := bufio.NewWriterSize(f, 256*1024)
	if _, err := bw.WriteString("STEM"); err != nil {
		return err
	}
	var hdr [8]byte
	binary.LittleEndian.PutUint32(hdr[0:4], uint32(SampleRate))
	count := len(tracks)
	if len(trackPCMs) < count {
		count = len(trackPCMs)
	}
	binary.LittleEndian.PutUint32(hdr[4:8], uint32(count))
	if _, err := bw.Write(hdr[:]); err != nil {
		return err
	}

	var lenBuf [4]byte
	var nameLenBuf [2]byte
	for i := 0; i < count; i++ {
		nameBytes := []byte(tracks[i].Name)
		if len(nameBytes) > 65535 {
			nameBytes = nameBytes[:65535]
		}
		binary.LittleEndian.PutUint16(nameLenBuf[:], uint16(len(nameBytes)))
		if _, err := bw.Write(nameLenBuf[:]); err != nil {
			return err
		}
		if _, err := bw.Write(nameBytes); err != nil {
			return err
		}

		pcm := trackPCMs[i]
		alignedLen := len(pcm) &^ 3
		binary.LittleEndian.PutUint32(lenBuf[:], uint32(alignedLen))
		if _, err := bw.Write(lenBuf[:]); err != nil {
			return err
		}
		if alignedLen > 0 {
			if _, err := bw.Write(pcm[:alignedLen]); err != nil {
				return err
			}
		}
	}
	return bw.Flush()
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

func emitMusicJSONError(err error) {
	msg := "unknown error"
	if err != nil {
		msg = err.Error()
	}
	rep := MusicSynthReportJSON{
		Passed: false,
		Error:  msg,
		Issues: []string{msg},
		Tracks: []TrackMetadataJSON{},
	}
	b, _ := json.Marshal(rep)
	fmt.Println(string(b))
}

func extractMusicTrackMetadata(score *Score) []TrackMetadataJSON {
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

func runMusicSynthJSON(args []string) {
	synthCmd := flag.NewFlagSet("synth-json", flag.ContinueOnError)
	synthCmd.SetOutput(io.Discard)
	appleFlag := synthCmd.Bool("apple", false, "Render using macOS Apple CoreAudio real instruments")
	outFlag := synthCmd.String("out", "", "Optional output WAV path")
	stemsFlag := synthCmd.String("stems", "", "Optional output packed binary stems path")
	soloFlag := synthCmd.String("solo", "", "Optional comma-separated track names to solo")
	muteFlag := synthCmd.String("mute", "", "Optional comma-separated track names to mute")
	if err := synthCmd.Parse(args); err != nil {
		emitMusicJSONError(fmt.Errorf("parse synth-json flags: %w", err))
		return
	}
	if synthCmd.NArg() < 1 {
		emitMusicJSONError(fmt.Errorf("missing DSL music file path"))
		return
	}

	dslFile := synthCmd.Arg(0)
	score, err := LoadDSLFile(dslFile)
	if err != nil {
		emitMusicJSONError(err)
		return
	}

	issues := []string{}
	if err := ValidateScoreTheory(score); err != nil {
		issues = append(issues, err.Error())
	}

	pcm, trackPCMs, err := SynthesizeScoreStemsWithOptions(score, *appleFlag)
	if err != nil {
		emitMusicJSONError(err)
		return
	}
	pcm = pcm[:len(pcm)&^3]

	// Always export all unfiltered per-track stems so the WebAudio mixer has every channel.
	if *stemsFlag != "" {
		if err := ExportStemsBinary(*stemsFlag, score.Tracks, trackPCMs); err != nil {
			emitMusicJSONError(fmt.Errorf("export stems: %w", err))
			return
		}
	}

	soloSet := make(map[string]bool)
	for _, s := range strings.Split(*soloFlag, ",") {
		if trimmed := strings.TrimSpace(s); trimmed != "" {
			soloSet[trimmed] = true
		}
	}
	muteSet := make(map[string]bool)
	for _, m := range strings.Split(*muteFlag, ",") {
		if trimmed := strings.TrimSpace(m); trimmed != "" {
			muteSet[trimmed] = true
		}
	}
	hasSoloOrMute := len(soloSet) > 0 || len(muteSet) > 0
	if hasSoloOrMute {
		maxLen := len(pcm) &^ 3
		audiblePCMs := make([][]byte, 0, len(trackPCMs))
		for i, tr := range score.Tracks {
			if i >= len(trackPCMs) {
				break
			}
			if aligned := len(trackPCMs[i]) &^ 3; aligned > maxLen {
				maxLen = aligned
			}
			if len(soloSet) > 0 && !soloSet[tr.Name] {
				continue
			}
			if muteSet[tr.Name] {
				continue
			}
			audiblePCMs = append(audiblePCMs, trackPCMs[i])
		}
		if len(audiblePCMs) == 0 {
			pcm = make([]byte, maxLen)
		} else {
			pcm = MixTracksPCM(audiblePCMs)
			pcm = pcm[:len(pcm)&^3]
		}
	}

	if *outFlag != "" {
		if err := ExportWAV(*outFlag, pcm); err != nil {
			emitMusicJSONError(fmt.Errorf("export WAV: %w", err))
			return
		}
	}

	alignedLen := len(pcm) &^ 3
	numFrames := alignedLen / BytesPerFrame
	durationSec := float64(numFrames) / float64(SampleRate)

	var sumL, sumR float64
	var sumSqL, sumSqR float64
	var maxAbsL, maxAbsR float64
	var lpState, sumSqLow, sumSqMono float64
	const lpAlpha = 0.035 // ~250 Hz cutoff at 44.1 kHz

	for i := 0; i < alignedLen; i += 4 {
		sL := float64(int16(uint16(pcm[i])|(uint16(pcm[i+1])<<8))) / 32768.0
		sR := float64(int16(uint16(pcm[i+2])|(uint16(pcm[i+3])<<8))) / 32768.0

		sumL += sL
		sumR += sR
		sumSqL += sL * sL
		sumSqR += sR * sR

		absL := math.Abs(sL)
		if absL > maxAbsL {
			maxAbsL = absL
		}
		absR := math.Abs(sR)
		if absR > maxAbsR {
			maxAbsR = absR
		}

		mono := (sL + sR) * 0.5
		lpState += lpAlpha * (mono - lpState)
		sumSqLow += lpState * lpState
		sumSqMono += mono * mono
	}

	var dcL, dcR, rmsL, rmsR float64
	if numFrames > 0 {
		dcL = sumL / float64(numFrames)
		dcR = sumR / float64(numFrames)
		rmsL = math.Sqrt(sumSqL / float64(numFrames))
		rmsR = math.Sqrt(sumSqR / float64(numFrames))
	}
	peakMax := math.Max(maxAbsL, maxAbsR)
	rmsMax := math.Max(rmsL, rmsR)

	lowFreqEnergyPct := 0.0
	if sumSqMono > 1e-12 {
		lowFreqEnergyPct = (sumSqLow / sumSqMono) * 100.0
	}

	boundaryClean := true
	if numFrames > 0 {
		startL := int16(uint16(pcm[0]) | (uint16(pcm[1]) << 8))
		startR := int16(uint16(pcm[2]) | (uint16(pcm[3]) << 8))
		lastIdx := (numFrames - 1) * BytesPerFrame
		endL := int16(uint16(pcm[lastIdx]) | (uint16(pcm[lastIdx+1]) << 8))
		endR := int16(uint16(pcm[lastIdx+2]) | (uint16(pcm[lastIdx+3]) << 8))
		if math.Abs(float64(startL)) > 4000 || math.Abs(float64(startR)) > 4000 ||
			math.Abs(float64(endL)) > 4000 || math.Abs(float64(endR)) > 4000 {
			boundaryClean = false
		}
	}

	if alignedLen == 0 {
		issues = append(issues, "PCM buffer is empty (0 bytes)")
	} else if peakMax < 0.005 && !hasSoloOrMute {
		issues = append(issues, fmt.Sprintf("signal is effectively silent (peak: %.4f, %.1f dBFS)", peakMax, safeDBFS(peakMax)))
	}
	if math.Abs(dcL) > 0.05 || math.Abs(dcR) > 0.05 {
		issues = append(issues, fmt.Sprintf("excessive DC offset (L: %+.4f, R: %+.4f)", dcL, dcR))
	}

	rep := MusicSynthReportJSON{
		Passed:           len(issues) == 0,
		Title:            score.Title,
		Type:             score.Type,
		BPM:              safeRound(score.BPM, 2),
		DurationSec:      safeRound(durationSec, 4),
		PeakLeftDBFS:     safeDBFS(maxAbsL),
		PeakRightDBFS:    safeDBFS(maxAbsR),
		PeakDBFS:         safeDBFS(peakMax),
		RMSLeftDBFS:      safeDBFS(rmsL),
		RMSRightDBFS:     safeDBFS(rmsR),
		RMSDBFS:          safeDBFS(rmsMax),
		DCOffset:         safeRound((dcL+dcR)/2.0, 5),
		DCOffsetL:        safeRound(dcL, 5),
		DCOffsetR:        safeRound(dcR, 5),
		LowFreqEnergyPct: safeRound(lowFreqEnergyPct, 2),
		BoundaryClean:    boundaryClean,
		Issues:           issues,
		Tracks:           extractMusicTrackMetadata(score),
		WavPath:          *outFlag,
	}
	b, _ := json.Marshal(rep)
	fmt.Println(string(b))
}

func runMusicPresetsJSON() {
	type ymPresetInfo struct {
		Name      string  `json:"name"`
		Algorithm uint8   `json:"algorithm"`
		Feedback  uint8   `json:"feedback"`
		Gain      float64 `json:"gain"`
		IsPSG     bool    `json:"isPSG"`
	}
	type tempoInfo struct {
		Marking string  `json:"marking"`
		BPM     float64 `json:"bpm"`
	}
	type curatedMusicInfo struct {
		File  string  `json:"file"`
		Title string  `json:"title"`
		BPM   float64 `json:"bpm"`
	}

	waveTypes := []string{
		"sine", "square", "pulse", "triangle", "sawtooth", "noise", "fm",
		"piano", "epiano", "organ", "guitar", "overdriven_guitar", "rhythm_guitar",
		"synth_bass", "sub_bass", "slap_bass", "harp", "violin", "cello", "strings",
		"voice", "flute", "oboe", "clarinet", "shakuhachi", "brass", "trumpet", "horn",
		"koto", "shamisen", "bell",
		"ym2612_guitar", "ym2612_rhythm_guitar", "ym2612_bass", "ym2612_slap_bass",
		"ym2612_brass", "ym2612_epiano", "ym2612_strings", "ym2612_choir", "ym2612_flute", "ym2612_bell",
		"psg_square", "psg_arp",
		"kick", "snare", "tom", "hat", "open_hat", "crash",
		"ym2612_kick", "ym2612_snare", "ym2612_tom", "ym2612_hat", "ym2612_open_hat", "ym2612_crash",
	}

	ymKeys := make([]string, 0, len(ym2612PatchCatalog))
	for k := range ym2612PatchCatalog {
		ymKeys = append(ymKeys, k)
	}
	sort.Strings(ymKeys)
	ymPresets := make([]ymPresetInfo, 0, len(ymKeys))
	for _, k := range ymKeys {
		p := ym2612PatchCatalog[k]
		ymPresets = append(ymPresets, ymPresetInfo{
			Name:      p.Name,
			Algorithm: p.ALG,
			Feedback:  p.FB,
			Gain:      p.Gain,
			IsPSG:     p.IsPSG,
		})
	}

	tempoKeys := make([]string, 0, len(classicalTempoMarkings))
	for k := range classicalTempoMarkings {
		tempoKeys = append(tempoKeys, k)
	}
	sort.Slice(tempoKeys, func(i, j int) bool {
		return classicalTempoMarkings[tempoKeys[i]] < classicalTempoMarkings[tempoKeys[j]]
	})
	tempos := make([]tempoInfo, 0, len(tempoKeys))
	for _, k := range tempoKeys {
		tempos = append(tempos, tempoInfo{
			Marking: k,
			BPM:     classicalTempoMarkings[k],
		})
	}

	curated := []curatedMusicInfo{
		{File: "bare_knuckle_intro.music", Title: "Bare Knuckle / Streets of Rage - Intro", BPM: 100},
		{File: "battle_theme.music", Title: "Battle Theme", BPM: 160},
		{File: "credits_theme.music", Title: "Credits Theme", BPM: 96},
		{File: "dawn_strategy_battle.music", Title: "Dawn Strategy Battle", BPM: 132},
		{File: "despair_theme.music", Title: "Despair Theme", BPM: 76},
		{File: "elemental_master_stage1.music", Title: "Elemental Master - Stage 1", BPM: 150},
		{File: "gaiares_level2.music", Title: "Gaiares - Mission 2", BPM: 148},
		{File: "ground_zero.music", Title: "Ground Zero", BPM: 96},
		{File: "shinobi2_stage2.music", Title: "The Revenge of Shinobi - Stage 2", BPM: 134},
	}

	out := map[string]any{
		"waveTypes":      waveTypes,
		"ym2612Presets":  ymPresets,
		"tempoMarkings":  tempos,
		"curatedLibrary": curated,
	}
	b, _ := json.Marshal(out)
	fmt.Println(string(b))
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

// DemoStageBGMDSL defines a complete 16-bar, 6-channel YM2612-style stage theme in the Music DSL.
const DemoStageBGMDSL = `
title "16-Bit Genesis Stage Theme"
type song
bpm 130
time 4/4

# 1. YM2612 6-Channel Instrument Palette
inst lead    wave=sawtooth vol=0.12 pan=-0.20 adsr=0.02,0.05,0.70,0.05 vib=5.5,4.5
inst counter wave=square   vol=0.08 pan=0.25  adsr=0.02,0.05,0.60,0.05 duty=0.25
inst pad     wave=sawtooth vol=0.06 pan=0.00  adsr=0.20,0.20,0.85,0.25 lpf=0.35
inst bass    wave=square   vol=0.13 pan=0.00  adsr=0.01,0.05,0.50,0.03 duty=0.50
inst arp     wave=triangle vol=0.07 pan=-0.40 adsr=0.008,0.04,0.35,0.02
inst kick    wave=sine     vol=0.14 pan=0.00  adsr=0.002,0.05,0.10,0.03 freq=130Hz->38Hz noise=0.10,0.25
inst snare   wave=noise    vol=0.08 pan=0.20  adsr=0.002,0.05,0.10,0.03 noise_filter=0.50
inst hat     wave=noise    vol=0.04 pan=0.30  adsr=0.001,0.02,0.05,0.01 noise_filter=0.95

# 2. Reusable 4-Bar Phrase Patterns (Am -> F -> Dm -> E7)
pattern lead_theme_a =
  A4:8 C5:8 E5:8 A5:8 C5:8 E5:8 A4:8 E5:8 |
  F4:8 A4:8 C5:8 F5:8 A4:8 C5:8 F4:8 C5:8 |
  D4:8 F4:8 A4:8 D5:8 F4:8 A4:8 D4:8 A4:8 |
  E4:8 G#4:8 B4:8 E5:8 G#4:8 B4:8 E4:8 B4:8

pattern lead_theme_b =
  A5:8 E5:8 C5:8 A5:8 E6:8 C6:8 B5:8 A5:8 |
  F5:8 C5:8 A4:8 F5:8 C6:8 A5:8 G5:8 F5:8 |
  D5:8 A4:8 F4:8 D5:8 A5:8 F5:8 E5:8 D5:8 |
  E5:8 B4:8 G#4:8 E5:8 B5:8 G#5:8 F#5:8 E5:8

pattern counter_phrase =
  E4:8 C4:8 A4:8 E4:8 C4:8 A4:8 E4:8 E4:8 |
  C4:8 A3:8 F4:8 C4:8 A3:8 F4:8 C4:8 C4:8 |
  A3:8 F3:8 D4:8 A3:8 F3:8 D4:8 A3:8 A3:8 |
  B3:8 G#3:8 E4:8 B3:8 G#3:8 E4:8 B3:8 B3:8

pattern pad_chords =
  [A3 C4 E4]:1 | [F3 A3 C4]:1 | [D3 F3 A3]:1 | [E3 G#3 B3]:1

pattern bass_gallop =
  (A1:16 A2:16)*8 | (F1:16 F2:16)*8 | (D1:16 D2:16)*8 | (E1:16 E2:16)*8

pattern arp_motion =
  (A4:16 C5:16 E5:16 A5:16 A5:16 E5:16 C5:16 A4:16)*2 |
  (F4:16 A4:16 C5:16 F5:16 F5:16 C5:16 A4:16 F4:16)*2 |
  (D4:16 F4:16 A4:16 D5:16 D5:16 A4:16 F4:16 D4:16)*2 |
  (E4:16 G#4:16 B4:16 E5:16 E5:16 B4:16 G#4:16 E4:16)*2

pattern drums_groove =
  (kick:16 hat:32 R:32 snare:16 hat:32 R:32)*16

# 3. 16-Bar Polyphonic Arrangement (4 x 4-Bar Sections)
track ch1_lead    lead:    lead_theme_a * 2 | lead_theme_b * 2
track ch2_counter counter: counter_phrase * 4
track ch3_pad     pad:     pad_chords * 4
track ch4_bass    bass:    bass_gallop * 4
track ch5_arp     arp:     arp_motion * 4
track ch6_drums:           drums_groove * 4
`
