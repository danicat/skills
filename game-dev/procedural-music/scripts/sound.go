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
	"bytes"
	"encoding/binary"
	"fmt"
	"io"
	"math"
	"math/rand/v2"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/hajimehoshi/ebiten/v2/audio"
)

const (
	SampleRate      = 44100
	NumChannels     = 2
	BytesPerSample  = 2
	BytesPerFrame   = NumChannels * BytesPerSample // 4 bytes per stereo frame
	BytesPerSecond  = SampleRate * BytesPerFrame   // 176,400 bytes/sec
	maxRepeatFactor = 1024
	maxPatternDepth = 32
)

// ============================================================================
// 1. PROCEDURAL AUDIO & MUSIC DSL AST DEFINITIONS
// ============================================================================

// Instrument defines a reusable synthesizer patch in the DSL (`inst <name> ...`).
type Instrument struct {
	Name               string
	WaveType           string  // "sine", "square", "triangle", "sawtooth", "noise", "fm"
	Volume             float64 // 0.0 to 1.0
	Muted              bool    // True when explicitly set to vol=0.0
	Pan                float64 // -1.0 (left) to +1.0 (right)
	DutyCycle          float64 // Pulse width (0.0 to 1.0) for square waves
	Attack             float64 // ADSR Attack in seconds
	Decay              float64 // ADSR Decay in seconds
	Sustain            float64 // ADSR Sustain amplitude (0.0 to 1.0)
	Release            float64 // ADSR Release in seconds
	VibratoFreq        float64 // Vibrato LFO rate in Hz
	VibratoDepth       float64 // Vibrato LFO depth in Hz
	ModRatio           float64 // FM modulator frequency multiplier relative to carrier
	ModFreq            float64 // Fixed FM modulator frequency in Hz (if ModRatio == 0)
	ModIndex           float64 // FM modulation index
	NoiseFilter        float64 // Single-pole LPF coefficient for noise (0.0 to 1.0]
	NoiseBlend         float64 // Blend between oscillator (0.0) and filtered noise (1.0)
	DefaultStartFreq   float64 // Default starting frequency in Hz (for drum/SFX triggers)
	DefaultEndFreq     float64 // Default ending frequency in Hz (for frequency sweeps)
	LPF                float64 // Optional per-instrument low-pass filter alpha (0.0 to 1.0]
	HPF                float64 // Optional per-instrument high-pass filter alpha (0.0 to 1.0)
	BitcrushBits       int     // Optional per-instrument bit depth (1..16)
	BitcrushDownsample int     // Optional per-instrument downsample factor (>=1)
	GMProgram          int     // General MIDI program number (0..127) for Apple CoreAudio synthesis
	HasGMProgram       bool    // True if GMProgram was explicitly configured via gm=/program=
	GMDrumNote         int     // General MIDI percussion note (27..87) on Channel 10 when > 0
}

// PitchSweep represents a stationary note (StartFreq == EndFreq) or a continuous pitch glide.
type PitchSweep struct {
	StartFreq float64
	EndFreq   float64
}

// NoteEvent represents a single resolved musical note, chord, sweep, or rest on a timeline.
type NoteEvent struct {
	IsRest        bool
	Inst          Instrument
	Pitches       []PitchSweep
	DurationSec   float64
	GainStart     float64 // Multiplier on Inst.Volume at start of note (default 1.0 when HasCustomGain is false)
	GainMid       float64 // Optional midpoint multiplier if HasGainMid is true (e.g. @swell)
	GainEnd       float64 // Multiplier on Inst.Volume at end of note (default 1.0 when HasCustomGain is false)
	HasCustomGain bool    // True if GainStart/GainEnd are explicitly set
	HasGainMid    bool    // True if a 3-point envelope (e.g. @swell) is active on this note
	GateRatio     float64 // Articulation gate ratio in (0.0, 1.0] (default 1.0; staccato = 0.40)
	AttackScale   float64 // Multiplier on Inst.Attack (default 1.0; pizzicato = 0.15, spiccato/marcato = 0.50)
	PanStart      float64 // Per-event stereo pan at start (-1.0 to +1.0)
	PanEnd        float64 // Per-event stereo pan at end (-1.0 to +1.0)
	HasCustomPan  bool    // True if stereo pan is overridden per-segment/event
	LPFOverride   float64 // Optional per-event low-pass filter alpha override (0.0 to 1.0]
	HPFOverride   float64 // Optional per-event high-pass filter alpha override (0.0 to 1.0)
}

// Track represents a named polyphonic channel in a Score.
type Track struct {
	Name        string
	DefaultInst string
	Events      []NoteEvent
}

// Score represents a parsed and validated DSL script (`.music` or `.sfx`).
type Score struct {
	Title                    string
	Type                     string // "song" or "sfx"
	BPM                      float64
	TempoMarking             string // Optional classical tempo marking (e.g. "allegro", "andantino")
	TimeSigNum               int
	TimeSigDen               int
	Instruments              map[string]Instrument
	ExplicitInstruments      map[string]bool
	Patterns                 map[string][]dslNode
	Tracks                   []Track
	GlobalLPF                float64
	GlobalHPF                float64
	GlobalBitcrushBits       int
	GlobalBitcrushDownsample int
	HasLoopSlice             bool
	LoopStartSec             float64
	LoopEndSec               float64
	SynthEngine              string // "default" (pure-Go YM2612/PSG/DSP) or "apple" (macOS CoreAudio real instruments)
	ValidateBarlines         bool
}

// ============================================================================
// 2. DSL LEXER & RECURSIVE-DESCENT PARSER
// ============================================================================

type dslTokenKind int

const (
	tokAtom dslTokenKind = iota
	tokPipe
	tokLParen
	tokRParen
	tokLAngle
	tokRAngle
	tokRepeat
	tokModifier
)

type dslToken struct {
	kind   dslTokenKind
	text   string
	number int
}

type dslNode struct {
	isGroup        bool
	isAlternate    bool
	isPipe         bool
	atom           string
	groupDur       string
	tiePipeOffsets []string
	children       []dslNode
	repeat         int
	transpose      int
	modifiers      []string
}

// LoadDSLFile reads and parses a `.music` or `.sfx` DSL file from disk.
func LoadDSLFile(filepath string) (*Score, error) {
	data, err := os.ReadFile(filepath)
	if err != nil {
		return nil, fmt.Errorf("load DSL file %q: %w", filepath, err)
	}
	return ParseDSL(string(data))
}

// CompileDSL parses a DSL script and synthesizes it into a 4-byte aligned 16-bit 44.1kHz stereo PCM buffer.
func CompileDSL(dslText string) ([]byte, error) {
	score, err := ParseDSL(dslText)
	if err != nil {
		return nil, err
	}
	return SynthesizeScore(score)
}

// ParseDSL parses a procedural music or SFX DSL script into a validated Score AST.
func ParseDSL(dslText string) (*Score, error) {
	return ParseDSLWithBarlines(dslText, true)
}

// ParseDSLWithBarlines parses a procedural music or SFX DSL script with optional '|' measure-boundary validation.
func ParseDSLWithBarlines(dslText string, validateBarlines bool) (*Score, error) {
	score := &Score{
		Title:               "Untitled",
		Type:                "song",
		BPM:                 120.0,
		TimeSigNum:          4,
		TimeSigDen:          4,
		Instruments:         defaultDrumInstrumentMap(),
		ExplicitInstruments: make(map[string]bool),
		Patterns:            make(map[string][]dslNode),
		ValidateBarlines:    validateBarlines,
	}
	explicitInsts := score.ExplicitInstruments

	rawLines := strings.Split(dslText, "\n")
	type logicalStatement struct {
		lineNum int
		keyword string
		rest    string
	}

	var stmts []logicalStatement
	for idx, raw := range rawLines {
		lineNum := idx + 1
		cleaned := stripDSLComment(raw)
		trimmed := strings.TrimSpace(cleaned)
		if trimmed == "" {
			continue
		}

		firstWord, remainder := splitFirstWord(trimmed)
		lowerWord := strings.ToLower(firstWord)

		if isTopLevelDirective(lowerWord) {
			stmts = append(stmts, logicalStatement{
				lineNum: lineNum,
				keyword: lowerWord,
				rest:    strings.TrimSpace(remainder),
			})
		} else {
			if len(stmts) == 0 {
				return nil, fmt.Errorf("line %d: unexpected token %q before any directive", lineNum, firstWord)
			}
			prev := &stmts[len(stmts)-1]
			if prev.keyword == "pattern" || prev.keyword == "track" {
				prev.rest += " " + trimmed
			} else {
				return nil, fmt.Errorf("line %d: unknown directive %q (or unexpected continuation after %q)", lineNum, firstWord, prev.keyword)
			}
		}
	}

	for _, st := range stmts {
		switch st.keyword {
		case "title":
			if st.rest == "" {
				return nil, fmt.Errorf("line %d: 'title' requires a non-empty string", st.lineNum)
			}
			score.Title = unquoteDSLString(st.rest)

		case "type":
			val := strings.ToLower(unquoteDSLString(st.rest))
			if val != "song" && val != "sfx" {
				return nil, fmt.Errorf("line %d: invalid type %q (must be 'song' or 'sfx')", st.lineNum, st.rest)
			}
			score.Type = val

		case "synth", "engine":
			val := strings.ToLower(strings.TrimSpace(unquoteDSLString(st.rest)))
			switch val {
			case "default", "ym2612", "megadrive", "genesis", "opn2", "procedural", "dsp", "native":
				score.SynthEngine = "default"
			case "apple", "coreaudio", "audiotoolbox", "dls", "macos":
				score.SynthEngine = "apple"
			default:
				return nil, fmt.Errorf("line %d: invalid synth engine %q (must be 'default' or 'apple')", st.lineNum, st.rest)
			}

		case "bpm", "tempo":
			bpm, marking, err := ParseTempoSpec(st.rest)
			if err != nil {
				return nil, fmt.Errorf("line %d: %w", st.lineNum, err)
			}
			score.BPM = bpm
			if marking != "" {
				score.TempoMarking = marking
			}

		case "time":
			parts := strings.Split(st.rest, "/")
			if len(parts) != 2 {
				return nil, fmt.Errorf("line %d: invalid time signature %q (expected <num>/<den>, e.g. 4/4)", st.lineNum, st.rest)
			}
			num, err1 := strconv.Atoi(strings.TrimSpace(parts[0]))
			den, err2 := strconv.Atoi(strings.TrimSpace(parts[1]))
			if err1 != nil || err2 != nil || num <= 0 || den <= 0 {
				return nil, fmt.Errorf("line %d: invalid time signature %q", st.lineNum, st.rest)
			}
			score.TimeSigNum = num
			score.TimeSigDen = den

		case "filter":
			fields := strings.Fields(st.rest)
			if len(fields) != 2 {
				return nil, fmt.Errorf("line %d: 'filter' requires '<lpf|hpf> <alpha>'", st.lineNum)
			}
			kind := strings.ToLower(fields[0])
			alpha, err := strconv.ParseFloat(fields[1], 64)
			if err != nil {
				return nil, fmt.Errorf("line %d: invalid filter alpha %q: %w", st.lineNum, fields[1], err)
			}
			switch kind {
			case "lpf":
				if alpha <= 0 || alpha > 1.0 {
					return nil, fmt.Errorf("line %d: lpf alpha must be in (0.0, 1.0], got %v", st.lineNum, alpha)
				}
				score.GlobalLPF = alpha
			case "hpf":
				if alpha <= 0 || alpha >= 1.0 {
					return nil, fmt.Errorf("line %d: hpf alpha must be in (0.0, 1.0), got %v", st.lineNum, alpha)
				}
				score.GlobalHPF = alpha
			default:
				return nil, fmt.Errorf("line %d: unknown filter type %q (expected 'lpf' or 'hpf')", st.lineNum, kind)
			}

		case "bitcrush":
			fields := strings.Fields(st.rest)
			if len(fields) != 2 {
				return nil, fmt.Errorf("line %d: 'bitcrush' requires '<bits 1..16> <downsample >=1>'", st.lineNum)
			}
			bits, err1 := strconv.Atoi(fields[0])
			down, err2 := strconv.Atoi(fields[1])
			if err1 != nil || err2 != nil || bits < 1 || bits > 16 || down < 1 {
				return nil, fmt.Errorf("line %d: invalid bitcrush arguments %q (bits must be 1..16, downsample >= 1)", st.lineNum, st.rest)
			}
			score.GlobalBitcrushBits = bits
			score.GlobalBitcrushDownsample = down

		case "loop":
			fields := strings.Fields(st.rest)
			if len(fields) != 2 {
				return nil, fmt.Errorf("line %d: 'loop' requires '<startDur> <endDur>'", st.lineNum)
			}
			startSec, err1 := ParseDuration(fields[0], score.BPM)
			endSec, err2 := ParseDuration(fields[1], score.BPM)
			if err1 != nil || err2 != nil || startSec < 0 || endSec <= startSec {
				return nil, fmt.Errorf("line %d: invalid loop range %q (expected 0 <= start < end)", st.lineNum, st.rest)
			}
			score.HasLoopSlice = true
			score.LoopStartSec = startSec
			score.LoopEndSec = endSec

		case "inst", "patch":
			instName, attrText := splitFirstWord(st.rest)
			if instName == "" {
				return nil, fmt.Errorf("line %d: 'inst' requires an instrument name and attributes", st.lineNum)
			}
			if explicitInsts[instName] {
				return nil, fmt.Errorf("line %d: duplicate instrument definition %q", st.lineNum, instName)
			}
			inst, err := parseInstrumentAttrs(instName, attrText, score.BPM)
			if err != nil {
				return nil, fmt.Errorf("line %d (inst %s): %w", st.lineNum, instName, err)
			}
			score.Instruments[instName] = inst
			explicitInsts[instName] = true

		case "pattern":
			eqIdx := strings.IndexByte(st.rest, '=')
			if eqIdx < 0 {
				return nil, fmt.Errorf("line %d: 'pattern' requires '<name> = <events...>'", st.lineNum)
			}
			patName := strings.TrimSpace(st.rest[:eqIdx])
			patBody := strings.TrimSpace(st.rest[eqIdx+1:])
			if patName == "" || patBody == "" {
				return nil, fmt.Errorf("line %d: 'pattern' requires both a name and a non-empty body", st.lineNum)
			}
			if _, exists := score.Patterns[patName]; exists {
				return nil, fmt.Errorf("line %d: duplicate pattern definition %q", st.lineNum, patName)
			}
			if explicitInsts[patName] {
				return nil, fmt.Errorf("line %d: pattern name %q conflicts with an instrument of the same name", st.lineNum, patName)
			}
			nodes, err := parsePatternNodes(patBody)
			if err != nil {
				return nil, fmt.Errorf("line %d (pattern %s): %w", st.lineNum, patName, err)
			}
			score.Patterns[patName] = nodes

		case "track":
			colonIdx := strings.IndexByte(st.rest, ':')
			if colonIdx < 0 {
				return nil, fmt.Errorf("line %d: 'track' requires '<name> [instrument]: <events...>'", st.lineNum)
			}
			headerFields := strings.Fields(st.rest[:colonIdx])
			bodyText := strings.TrimSpace(st.rest[colonIdx+1:])
			if len(headerFields) < 1 || len(headerFields) > 2 {
				return nil, fmt.Errorf("line %d: invalid track header %q (expected 'track <name> [instrument]:')", st.lineNum, st.rest[:colonIdx])
			}
			trackName := headerFields[0]
			defaultInst := ""
			if len(headerFields) == 2 {
				defaultInst = headerFields[1]
				if _, ok := score.Instruments[defaultInst]; !ok {
					return nil, fmt.Errorf("line %d: track %q references unknown instrument %q", st.lineNum, trackName, defaultInst)
				}
			}
			if bodyText == "" {
				return nil, fmt.Errorf("line %d: track %q has an empty body", st.lineNum, trackName)
			}
			nodes, err := parsePatternNodes(bodyText)
			if err != nil {
				return nil, fmt.Errorf("line %d (track %s): %w", st.lineNum, trackName, err)
			}
			events, err := score.expandNodesToEvents(nodes, defaultInst, 0, make(map[string]bool), 0)
			if err != nil {
				return nil, fmt.Errorf("line %d (track %s): %w", st.lineNum, trackName, err)
			}
			score.appendTrackEvents(trackName, defaultInst, events)
		}
	}

	if len(score.Tracks) == 0 {
		return nil, fmt.Errorf("parse DSL: score %q contains no tracks", score.Title)
	}

	return score, nil
}

func (s *Score) appendTrackEvents(name, defaultInst string, events []NoteEvent) {
	for i := range s.Tracks {
		if s.Tracks[i].Name == name {
			if s.Tracks[i].DefaultInst == "" && defaultInst != "" {
				s.Tracks[i].DefaultInst = defaultInst
			}
			s.Tracks[i].Events = append(s.Tracks[i].Events, events...)
			return
		}
	}
	s.Tracks = append(s.Tracks, Track{
		Name:        name,
		DefaultInst: defaultInst,
		Events:      events,
	})
}

func isTopLevelDirective(word string) bool {
	switch word {
	case "title", "type", "synth", "engine", "bpm", "tempo", "time", "filter", "bitcrush", "loop", "inst", "patch", "pattern", "track":
		return true
	default:
		return false
	}
}

var classicalTempoMarkings = map[string]float64{
	"larghissimo":      24,
	"grave":            42,
	"largo":            50,
	"lento":            56,
	"larghetto":        63,
	"adagio":           70,
	"adagietto":        76,
	"marcia_moderato":  84,
	"andante":          88,
	"andantino":        96,
	"moderato":         112,
	"allegretto":       120,
	"allegro_moderato": 124,
	"allegro":          138,
	"vivace":           160,
	"vivacissimo":      172,
	"allegrissimo":     176,
	"presto":           184,
	"prestissimo":      204,
}

// ParseTempoSpec parses a numeric BPM, a classical tempo marking (e.g. "allegro", "andantino"),
// or both (e.g. "andantino 96" or "138 allegro").
func ParseTempoSpec(spec string) (float64, string, error) {
	fields := strings.Fields(strings.TrimSpace(spec))
	if len(fields) == 0 || len(fields) > 2 {
		return 0, "", fmt.Errorf("invalid tempo/bpm %q (expected '<bpm>', '<marking>', or '<marking> <bpm>')", spec)
	}
	var bpm float64
	var hasBPM bool
	var marking string
	for _, f := range fields {
		lower := strings.ToLower(strings.TrimSpace(f))
		if presetBPM, ok := classicalTempoMarkings[lower]; ok {
			if marking != "" {
				return 0, "", fmt.Errorf("duplicate tempo marking in %q", spec)
			}
			marking = lower
			if !hasBPM {
				bpm = presetBPM
			}
			continue
		}
		val, err := strconv.ParseFloat(f, 64)
		if err != nil || val <= 0 || val > 1000 {
			return 0, "", fmt.Errorf("invalid tempo/bpm token %q in %q (expected BPM 1..1000 or classical marking like allegro, andantino, adagio, moderato, vivace, presto)", f, spec)
		}
		bpm = val
		hasBPM = true
	}
	return bpm, marking, nil
}

func stripDSLComment(line string) string {
	inQuotes := false
	for i := 0; i < len(line); i++ {
		if line[i] == '"' {
			inQuotes = !inQuotes
		} else if !inQuotes {
			if line[i] == '#' && (i == 0 || line[i-1] == ' ' || line[i-1] == '\t') {
				return line[:i]
			}
			if line[i] == '/' && i+1 < len(line) && line[i+1] == '/' {
				return line[:i]
			}
		}
	}
	return line
}

func splitFirstWord(s string) (string, string) {
	s = strings.TrimSpace(s)
	for i := 0; i < len(s); i++ {
		if s[i] == ' ' || s[i] == '\t' {
			return s[:i], strings.TrimSpace(s[i+1:])
		}
	}
	return s, ""
}

func unquoteDSLString(s string) string {
	s = strings.TrimSpace(s)
	if len(s) >= 2 && ((s[0] == '"' && s[len(s)-1] == '"') || (s[0] == '\'' && s[len(s)-1] == '\'')) {
		return s[1 : len(s)-1]
	}
	return s
}

func defaultDrumInstrumentMap() map[string]Instrument {
	drums := make(map[string]Instrument, 10)
	for _, spec := range []struct {
		name string
		wave string
		gm   int
	}{
		{"drums", "kick", 36},
		{"kick", "kick", 36},
		{"snare", "snare", 38},
		{"tom", "tom", 47},
		{"tom_hi", "tom", 50},
		{"tom_mid", "tom", 47},
		{"tom_low", "tom", 45},
		{"hat", "ym2612_hat", 42},
		{"open_hat", "ym2612_open_hat", 46},
		{"crash", "crash", 49},
	} {
		inst := Instrument{
			Name:        spec.name,
			WaveType:    spec.wave,
			Volume:      0.2,
			DutyCycle:   0.5,
			Attack:      0.005,
			Decay:       0.04,
			Sustain:     0.7,
			Release:     0.03,
			NoiseFilter: 1.0,
			GMDrumNote:  spec.gm,
		}
		applyWaveArchetypeDefaults(&inst)
		drums[spec.name] = inst
	}
	return drums
}

func isDrumKitWave(w string) bool {
	switch strings.ToLower(w) {
	case "kick", "ym2612_kick", "snare", "ym2612_snare", "tom", "ym2612_tom", "hat", "ym2612_hat", "open_hat", "ym2612_open_hat", "crash", "ym2612_crash", "noise":
		return true
	default:
		return false
	}
}

func applyWaveArchetypeDefaults(inst *Instrument) {
	switch inst.WaveType {
	case "ym2612_guitar":
		inst.Volume = 0.16
		inst.Pan = -0.12
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.003, 0.12, 0.88, 0.08
		inst.VibratoFreq, inst.VibratoDepth = 5.5, 3.50
		inst.LPF = 0.46
	case "ym2612_rhythm_guitar":
		inst.Volume = 0.10
		inst.Pan = 0.36
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.004, 0.12, 0.84, 0.09
		inst.VibratoFreq, inst.VibratoDepth = 5.5, 3.20
		inst.LPF = 0.42
	case "ym2612_bell":
		inst.Volume = 0.060
		inst.Pan = 0.25
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.002, 0.14, 0.80, 0.10
		inst.VibratoFreq, inst.VibratoDepth = 6.0, 4.80
		inst.LPF = 0.64
	case "ym2612_epiano":
		inst.Volume = 0.13
		inst.Pan = -0.24
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.003, 0.16, 0.78, 0.10
		inst.VibratoFreq, inst.VibratoDepth = 5.0, 0.06
		inst.LPF = 0.38
	case "ym2612_brass":
		inst.Volume = 0.12
		inst.Pan = 0.20
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.025, 0.16, 0.86, 0.14
		inst.VibratoFreq, inst.VibratoDepth = 4.8, 0.06
		inst.LPF = 0.36
	case "ym2612_strings", "ym2612_choir":
		inst.Volume = 0.10
		inst.Pan = -0.30
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.045, 0.18, 0.86, 0.16
		inst.VibratoFreq, inst.VibratoDepth = 4.5, 0.06
		inst.LPF = 0.32
	case "ym2612_flute":
		inst.Volume = 0.12
		inst.Pan = -0.15
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.018, 0.14, 0.82, 0.10
		inst.VibratoFreq, inst.VibratoDepth = 5.5, 2.20
		inst.LPF = 0.42
	case "psg_arp":
		inst.Volume = 0.072
		inst.Pan = -0.44
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.002, 0.10, 0.74, 0.05
		inst.VibratoFreq, inst.VibratoDepth = 6.0, 2.20
		inst.DutyCycle = 0.25
		inst.LPF = 0.44
	case "psg_square":
		inst.Volume = 0.050
		inst.Pan = 0.48
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.002, 0.10, 0.70, 0.05
		inst.VibratoFreq, inst.VibratoDepth = 6.0, 2.20
		inst.DutyCycle = 0.50
		inst.LPF = 0.40
	case "ym2612_bass":
		inst.Volume = 0.24
		inst.Pan = 0.00
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.002, 0.09, 0.86, 0.04
		inst.LPF = 0.055
	case "ym2612_slap_bass":
		inst.Volume = 0.25
		inst.Pan = 0.00
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.002, 0.09, 0.86, 0.04
		inst.LPF = 0.065
	case "sub_bass":
		inst.Volume = 0.22
		inst.Pan = 0.00
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.004, 0.12, 0.88, 0.06
		inst.LPF = 0.035
	case "kick", "ym2612_kick":
		inst.Volume = 0.19
		inst.Pan = 0.00
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.001, 0.09, 0.25, 0.04
		inst.DefaultStartFreq, inst.DefaultEndFreq = 158.0, 38.0
		if inst.GMDrumNote == 0 {
			inst.GMDrumNote = 36
		}
	case "snare", "ym2612_snare":
		inst.Volume = 0.14
		inst.Pan = 0.08
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.001, 0.08, 0.14, 0.04
		if inst.GMDrumNote == 0 {
			inst.GMDrumNote = 38
		}
	case "tom", "ym2612_tom":
		inst.Volume = 0.14
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.001, 0.09, 0.25, 0.04
		switch inst.Name {
		case "tom_hi":
			inst.Pan = -0.25
			inst.DefaultStartFreq, inst.DefaultEndFreq = 218.0, 95.0
			if inst.GMDrumNote == 0 {
				inst.GMDrumNote = 50
			}
		case "tom_low":
			inst.Pan = 0.25
			inst.Decay = 0.10
			inst.DefaultStartFreq, inst.DefaultEndFreq = 132.0, 48.0
			if inst.GMDrumNote == 0 {
				inst.GMDrumNote = 45
			}
		default:
			inst.Pan = 0.00
			inst.DefaultStartFreq, inst.DefaultEndFreq = 172.0, 72.0
			if inst.GMDrumNote == 0 {
				inst.GMDrumNote = 47
			}
		}
	case "ym2612_hat":
		inst.Volume = 0.08
		inst.Pan = -0.15
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.001, 0.04, 0.08, 0.02
		if inst.GMDrumNote == 0 {
			inst.GMDrumNote = 42
		}
	case "ym2612_open_hat":
		inst.Volume = 0.09
		inst.Pan = -0.15
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.001, 0.12, 0.18, 0.06
		if inst.GMDrumNote == 0 {
			inst.GMDrumNote = 46
		}
	case "crash":
		inst.Volume = 0.11
		inst.Pan = 0.20
		inst.Attack, inst.Decay, inst.Sustain, inst.Release = 0.001, 0.22, 0.20, 0.12
		if inst.GMDrumNote == 0 {
			inst.GMDrumNote = 49
		}
	}
}

func parseInstrumentAttrs(name, attrText string, bpm float64) (Instrument, error) {
	inst := Instrument{
		Name:        name,
		Volume:      0.2,
		Pan:         0.0,
		DutyCycle:   0.5,
		Attack:      0.005,
		Decay:       0.04,
		Sustain:     0.7,
		Release:     0.03,
		NoiseFilter: 1.0,
	}
	hasWave := false
	hasExplicitNoiseBlend := false

	fields := strings.Fields(attrText)
	if len(fields) == 0 {
		return inst, fmt.Errorf("missing attributes")
	}

	// Pass 1: resolve wave / gm / gm_drum so studio archetype defaults can be pre-populated before explicit overrides.
	for _, field := range fields {
		eq := strings.IndexByte(field, '=')
		if eq <= 0 || eq == len(field)-1 {
			return inst, fmt.Errorf("malformed attribute %q (expected key=value)", field)
		}
		key := strings.ToLower(field[:eq])
		val := field[eq+1:]
		switch key {
		case "wave", "wave_type":
			w, err := normalizeWaveType(val)
			if err != nil {
				return inst, err
			}
			inst.WaveType = w
			hasWave = true
		case "gm", "program", "midi_program":
			prog, err := ParseGMProgram(val)
			if err != nil {
				return inst, err
			}
			inst.GMProgram = prog
			inst.HasGMProgram = true
		case "drum_note", "gm_drum":
			dNote, err := ParseGMDrumNote(val)
			if err != nil {
				return inst, err
			}
			inst.GMDrumNote = dNote
		}
	}
	if !hasWave {
		if inst.HasGMProgram {
			inst.WaveType = inferWaveTypeFromGMProgram(inst.GMProgram)
			hasWave = true
		} else if inst.GMDrumNote > 0 {
			inst.WaveType = inferDrumWaveFromGMDrumNote(inst.GMDrumNote)
			hasWave = true
		}
	}
	if !hasWave {
		return inst, fmt.Errorf("missing required 'wave=<type>' attribute")
	}
	applyWaveArchetypeDefaults(&inst)

	// Pass 2: apply explicit key=value overrides.
	for _, field := range fields {
		eq := strings.IndexByte(field, '=')
		key := strings.ToLower(field[:eq])
		val := field[eq+1:]

		switch key {
		case "wave", "wave_type", "gm", "program", "midi_program", "drum_note", "gm_drum":
			// Handled in Pass 1.

		case "vol", "volume":
			v, err := strconv.ParseFloat(val, 64)
			if err != nil || v < 0.0 || v > 1.0 {
				return inst, fmt.Errorf("invalid volume %q (must be 0.0 to 1.0)", val)
			}
			inst.Volume = v
			inst.Muted = v == 0.0

		case "pan":
			p, err := strconv.ParseFloat(val, 64)
			if err != nil || p < -1.0 || p > 1.0 {
				return inst, fmt.Errorf("invalid pan %q (must be -1.0 to +1.0)", val)
			}
			inst.Pan = p

		case "duty", "duty_cycle":
			d, err := strconv.ParseFloat(val, 64)
			if err != nil || d <= 0.0 || d >= 1.0 {
				return inst, fmt.Errorf("invalid duty cycle %q (must be in (0.0, 1.0))", val)
			}
			inst.DutyCycle = d

		case "adsr":
			parts := strings.Split(val, ",")
			if len(parts) != 4 {
				return inst, fmt.Errorf("invalid adsr %q (expected attack,decay,sustain,release)", val)
			}
			a, err1 := parseSecondsOrDuration(parts[0], bpm)
			d, err2 := parseSecondsOrDuration(parts[1], bpm)
			s, err3 := strconv.ParseFloat(parts[2], 64)
			r, err4 := parseSecondsOrDuration(parts[3], bpm)
			if err1 != nil || err2 != nil || err3 != nil || err4 != nil || a < 0 || d < 0 || s < 0 || s > 1.0 || r < 0 {
				return inst, fmt.Errorf("invalid adsr values %q", val)
			}
			inst.Attack = a
			inst.Decay = d
			inst.Sustain = s
			inst.Release = r

		case "attack":
			a, err := parseSecondsOrDuration(val, bpm)
			if err != nil || a < 0 {
				return inst, fmt.Errorf("invalid attack %q", val)
			}
			inst.Attack = a

		case "decay":
			d, err := parseSecondsOrDuration(val, bpm)
			if err != nil || d < 0 {
				return inst, fmt.Errorf("invalid decay %q", val)
			}
			inst.Decay = d

		case "sustain":
			s, err := strconv.ParseFloat(val, 64)
			if err != nil || s < 0 || s > 1.0 {
				return inst, fmt.Errorf("invalid sustain %q (must be 0.0 to 1.0)", val)
			}
			inst.Sustain = s

		case "release":
			r, err := parseSecondsOrDuration(val, bpm)
			if err != nil || r < 0 {
				return inst, fmt.Errorf("invalid release %q", val)
			}
			inst.Release = r

		case "vib", "vibrato":
			parts := strings.Split(val, ",")
			if len(parts) != 2 {
				return inst, fmt.Errorf("invalid vibrato %q (expected rateHz,depthHz)", val)
			}
			vf, err1 := parseHzNumber(parts[0])
			vd, err2 := parseHzNumber(parts[1])
			if err1 != nil || err2 != nil || vf < 0 || vd < 0 {
				return inst, fmt.Errorf("invalid vibrato parameters %q", val)
			}
			inst.VibratoFreq = vf
			inst.VibratoDepth = vd

		case "freq", "sweep", "pitch":
			sweep, err := parsePitchOrSweep(val)
			if err != nil {
				return inst, fmt.Errorf("invalid freq/sweep %q: %w", val, err)
			}
			inst.DefaultStartFreq = sweep.StartFreq
			inst.DefaultEndFreq = sweep.EndFreq

		case "fm":
			parts := strings.Split(val, ",")
			if len(parts) != 2 {
				return inst, fmt.Errorf("invalid fm %q (expected ratioOrHz,modIndex)", val)
			}
			mi, err2 := strconv.ParseFloat(parts[1], 64)
			if err2 != nil || mi < 0 {
				return inst, fmt.Errorf("invalid fm mod_index in %q", val)
			}
			inst.ModIndex = mi
			if strings.HasSuffix(strings.ToLower(parts[0]), "hz") {
				mf, err1 := parseHzNumber(parts[0])
				if err1 != nil || mf <= 0 {
					return inst, fmt.Errorf("invalid fm mod_freq in %q", val)
				}
				inst.ModFreq = mf
			} else {
				mr, err1 := strconv.ParseFloat(parts[0], 64)
				if err1 != nil || mr <= 0 {
					return inst, fmt.Errorf("invalid fm mod_ratio in %q", val)
				}
				inst.ModRatio = mr
			}

		case "mod_ratio":
			mr, err := strconv.ParseFloat(val, 64)
			if err != nil || mr <= 0 {
				return inst, fmt.Errorf("invalid mod_ratio %q", val)
			}
			inst.ModRatio = mr

		case "mod_freq":
			mf, err := parseHzNumber(val)
			if err != nil || mf <= 0 {
				return inst, fmt.Errorf("invalid mod_freq %q", val)
			}
			inst.ModFreq = mf

		case "mod_index":
			mi, err := strconv.ParseFloat(val, 64)
			if err != nil || mi < 0 {
				return inst, fmt.Errorf("invalid mod_index %q", val)
			}
			inst.ModIndex = mi

		case "noise":
			parts := strings.Split(val, ",")
			if len(parts) != 2 {
				return inst, fmt.Errorf("invalid noise %q (expected filterCoeff,blend)", val)
			}
			nf, err1 := strconv.ParseFloat(parts[0], 64)
			nb, err2 := strconv.ParseFloat(parts[1], 64)
			if err1 != nil || err2 != nil || nf <= 0 || nf > 1.0 || nb < 0 || nb > 1.0 {
				return inst, fmt.Errorf("invalid noise parameters %q (filter in (0,1], blend in [0,1])", val)
			}
			inst.NoiseFilter = nf
			inst.NoiseBlend = nb
			hasExplicitNoiseBlend = true

		case "noise_filter":
			nf, err := strconv.ParseFloat(val, 64)
			if err != nil || nf <= 0 || nf > 1.0 {
				return inst, fmt.Errorf("invalid noise_filter %q (must be in (0.0, 1.0])", val)
			}
			inst.NoiseFilter = nf

		case "noise_blend":
			nb, err := strconv.ParseFloat(val, 64)
			if err != nil || nb < 0 || nb > 1.0 {
				return inst, fmt.Errorf("invalid noise_blend %q (must be in [0.0, 1.0])", val)
			}
			inst.NoiseBlend = nb
			hasExplicitNoiseBlend = true

		case "lpf":
			alpha, err := strconv.ParseFloat(val, 64)
			if err != nil || alpha <= 0 || alpha > 1.0 {
				return inst, fmt.Errorf("invalid lpf %q (must be in (0.0, 1.0])", val)
			}
			inst.LPF = alpha

		case "hpf":
			alpha, err := strconv.ParseFloat(val, 64)
			if err != nil || alpha <= 0 || alpha >= 1.0 {
				return inst, fmt.Errorf("invalid hpf %q (must be in (0.0, 1.0))", val)
			}
			inst.HPF = alpha

		case "bitcrush":
			parts := strings.Split(val, ",")
			if len(parts) != 2 {
				return inst, fmt.Errorf("invalid bitcrush %q (expected bits,downsample)", val)
			}
			bits, err1 := strconv.Atoi(parts[0])
			down, err2 := strconv.Atoi(parts[1])
			if err1 != nil || err2 != nil || bits < 1 || bits > 16 || down < 1 {
				return inst, fmt.Errorf("invalid bitcrush %q (bits 1..16, downsample >= 1)", val)
			}
			inst.BitcrushBits = bits
			inst.BitcrushDownsample = down

		default:
			return inst, fmt.Errorf("unknown attribute %q", key)
		}
	}

	if inst.WaveType == "noise" && !hasExplicitNoiseBlend {
		inst.NoiseBlend = 1.0
	}
	return inst, nil
}

func normalizeWaveType(w string) (string, error) {
	switch strings.ToLower(strings.TrimSpace(w)) {
	case "sine", "sin":
		return "sine", nil
	case "square", "sq":
		return "square", nil
	case "pulse":
		return "pulse", nil
	case "triangle", "tri":
		return "triangle", nil
	case "sawtooth", "saw":
		return "sawtooth", nil
	case "noise":
		return "noise", nil
	case "fm":
		return "fm", nil
	case "violin", "fiddle":
		return "violin", nil
	case "cello":
		return "cello", nil
	case "strings", "ensemble":
		return "strings", nil
	case "voice", "vocal", "choir":
		return "voice", nil
	case "flute", "woodwind":
		return "flute", nil
	case "oboe":
		return "oboe", nil
	case "clarinet":
		return "clarinet", nil
	case "shakuhachi":
		return "shakuhachi", nil
	case "brass":
		return "brass", nil
	case "trumpet":
		return "trumpet", nil
	case "horn", "french_horn":
		return "horn", nil
	case "organ":
		return "organ", nil
	case "piano", "grand_piano":
		return "piano", nil
	case "guitar":
		return "guitar", nil
	case "overdriven_guitar", "distortion_guitar", "electric_guitar", "fm_guitar":
		return "overdriven_guitar", nil
	case "rhythm_guitar", "power_guitar", "muted_guitar":
		return "rhythm_guitar", nil
	case "synth_bass", "fm_bass", "bass":
		return "synth_bass", nil
	case "sub_bass":
		return "sub_bass", nil
	case "slap_bass":
		return "slap_bass", nil
	case "koto":
		return "koto", nil
	case "shamisen":
		return "shamisen", nil
	case "harp", "pluck", "acoustic":
		return "harp", nil
	case "epiano", "rhodes":
		return "epiano", nil
	case "bell", "chime":
		return "bell", nil
	case "kick":
		return "kick", nil
	case "snare":
		return "snare", nil
	case "tom":
		return "tom", nil
	case "hat":
		return "hat", nil
	case "open_hat":
		return "open_hat", nil
	case "crash":
		return "crash", nil
	case "ym2612_guitar":
		return "ym2612_guitar", nil
	case "ym2612_rhythm_guitar":
		return "ym2612_rhythm_guitar", nil
	case "ym2612_bass":
		return "ym2612_bass", nil
	case "ym2612_slap_bass":
		return "ym2612_slap_bass", nil
	case "ym2612_brass", "fm_brass", "synth_brass", "polysynth":
		return "ym2612_brass", nil
	case "ym2612_epiano", "fm_epiano", "dx7":
		return "ym2612_epiano", nil
	case "ym2612_strings", "fm_strings", "synth_strings":
		return "ym2612_strings", nil
	case "ym2612_choir", "fm_choir", "ym2612_voice":
		return "ym2612_choir", nil
	case "ym2612_flute", "fm_flute":
		return "ym2612_flute", nil
	case "ym2612_bell", "fm_bell":
		return "ym2612_bell", nil
	case "psg_square", "psg_pulse", "sn76489":
		return "psg_square", nil
	case "psg_arp":
		return "psg_arp", nil
	case "ym2612_kick":
		return "ym2612_kick", nil
	case "ym2612_snare":
		return "ym2612_snare", nil
	case "ym2612_tom":
		return "ym2612_tom", nil
	case "ym2612_hat":
		return "ym2612_hat", nil
	case "ym2612_open_hat":
		return "ym2612_open_hat", nil
	case "ym2612_crash":
		return "ym2612_crash", nil
	default:
		return "", fmt.Errorf("unsupported wave type %q (valid: sine, square, pulse, triangle, sawtooth, noise, fm, piano, epiano, organ, guitar, harp, pluck, violin, cello, strings, voice, choir, flute, oboe, clarinet, shakuhachi, brass, trumpet, horn, koto, shamisen, bell, ym2612_guitar, ym2612_rhythm_guitar, ym2612_bass, ym2612_slap_bass, ym2612_brass, ym2612_epiano, ym2612_strings, ym2612_choir, ym2612_flute, ym2612_bell, psg_square, psg_arp, ym2612_kick, ym2612_snare, ym2612_tom, ym2612_hat, ym2612_open_hat, ym2612_crash)", w)
	}
}

func parseHzNumber(s string) (float64, error) {
	trimmed := strings.TrimSpace(s)
	lower := strings.ToLower(trimmed)
	if strings.HasSuffix(lower, "hz") {
		trimmed = strings.TrimSpace(trimmed[:len(trimmed)-2])
	}
	return strconv.ParseFloat(trimmed, 64)
}

func parseSecondsOrDuration(s string, bpm float64) (float64, error) {
	trimmed := strings.TrimSpace(s)
	lower := strings.ToLower(trimmed)
	if strings.HasSuffix(lower, "ms") || strings.HasSuffix(lower, "s") {
		return ParseDuration(trimmed, bpm)
	}
	return strconv.ParseFloat(trimmed, 64)
}

func gcdInt64(a, b int64) int64 {
	for b != 0 {
		a, b = b, a%b
	}
	if a < 0 {
		return -a
	}
	return a
}

func parseSingleDurationPartRat(token string) (num, den int64, beatsFloat float64, isRat bool, err error) {
	s := strings.TrimSpace(token)
	if s == "" {
		return 0, 0, 0, false, fmt.Errorf("empty duration token")
	}
	lower := strings.ToLower(s)
	if strings.HasSuffix(lower, "b") {
		beats, err := strconv.ParseFloat(strings.TrimSpace(s[:len(s)-1]), 64)
		if err != nil || beats <= 0 {
			return 0, 0, 0, false, fmt.Errorf("invalid beat duration %q", token)
		}
		return 0, 0, beats, false, nil
	}

	mulNum := int64(1)
	mulDen := int64(1)
	multiplier := 1.0
	for len(s) > 0 {
		if s[len(s)-1] == '.' {
			mulNum *= 3
			mulDen *= 2
			multiplier *= 1.5
			s = s[:len(s)-1]
		} else if s[len(s)-1] == 't' || s[len(s)-1] == 'T' {
			mulNum *= 2
			mulDen *= 3
			multiplier *= (2.0 / 3.0)
			s = s[:len(s)-1]
		} else {
			break
		}
	}

	if slashIdx := strings.IndexByte(s, '/'); slashIdx > 0 {
		nInt, err1 := strconv.ParseInt(s[:slashIdx], 10, 64)
		dInt, err2 := strconv.ParseInt(s[slashIdx+1:], 10, 64)
		if err1 == nil && err2 == nil && nInt > 0 && dInt > 0 {
			num = 4 * nInt * mulNum
			den = dInt * mulDen
			g := gcdInt64(num, den)
			return num / g, den / g, (4.0 * float64(nInt) / float64(dInt)) * multiplier, true, nil
		}
		nf, err1 := strconv.ParseFloat(s[:slashIdx], 64)
		df, err2 := strconv.ParseFloat(s[slashIdx+1:], 64)
		if err1 != nil || err2 != nil || nf <= 0 || df <= 0 {
			return 0, 0, 0, false, fmt.Errorf("invalid fractional duration %q", token)
		}
		return 0, 0, (4.0 * nf / df) * multiplier, false, nil
	}

	subInt, errInt := strconv.ParseInt(s, 10, 64)
	if errInt == nil && subInt > 0 {
		num = 4 * mulNum
		den = subInt * mulDen
		g := gcdInt64(num, den)
		return num / g, den / g, (4.0 / float64(subInt)) * multiplier, true, nil
	}

	subdiv, err := strconv.ParseFloat(s, 64)
	if err != nil || subdiv <= 0 {
		return 0, 0, 0, false, fmt.Errorf("invalid note subdivision duration %q", token)
	}
	return 0, 0, (4.0 / subdiv) * multiplier, false, nil
}

// ParseDuration converts a DSL duration token (e.g. "4", "8", "16.", "8t", "1/4", "1~1", "2.~8.", "2b", "150ms", "0.5s")
// into exact seconds at the given BPM.
func ParseDuration(token string, bpm float64) (float64, error) {
	s := strings.TrimSpace(token)
	if s == "" {
		return 0, fmt.Errorf("empty duration token")
	}
	if bpm <= 0 {
		bpm = 120.0
	}
	beatSec := 60.0 / bpm
	lower := strings.ToLower(s)

	if strings.Contains(s, "~") {
		parts := strings.Split(s, "~")
		sumNum := int64(0)
		sumDen := int64(1)
		allRat := true
		var sumBeats float64
		for _, p := range parts {
			n, d, bf, isRat, err := parseSingleDurationPartRat(p)
			if err != nil {
				return 0, fmt.Errorf("in tied duration %q: %w", token, err)
			}
			sumBeats += bf
			if isRat {
				num := sumNum*d + n*sumDen
				den := sumDen * d
				g := gcdInt64(num, den)
				sumNum = num / g
				sumDen = den / g
			} else {
				allRat = false
			}
		}
		if allRat {
			beats := float64(sumNum) / float64(sumDen)
			return beats * beatSec, nil
		}
		return sumBeats * beatSec, nil
	}

	if strings.HasSuffix(lower, "ms") {
		ms, err := strconv.ParseFloat(strings.TrimSpace(s[:len(s)-2]), 64)
		if err != nil || ms <= 0 {
			return 0, fmt.Errorf("invalid millisecond duration %q", token)
		}
		return ms / 1000.0, nil
	}
	if strings.HasSuffix(lower, "s") {
		sec, err := strconv.ParseFloat(strings.TrimSpace(s[:len(s)-1]), 64)
		if err != nil || sec <= 0 {
			return 0, fmt.Errorf("invalid second duration %q", token)
		}
		return sec, nil
	}
	if strings.HasSuffix(lower, "b") {
		beats, err := strconv.ParseFloat(strings.TrimSpace(s[:len(s)-1]), 64)
		if err != nil || beats <= 0 {
			return 0, fmt.Errorf("invalid beat duration %q", token)
		}
		return beats * beatSec, nil
	}

	multiplier := 1.0
	for len(s) > 0 {
		if s[len(s)-1] == '.' {
			multiplier *= 1.5
			s = s[:len(s)-1]
		} else if s[len(s)-1] == 't' || s[len(s)-1] == 'T' {
			multiplier *= (2.0 / 3.0)
			s = s[:len(s)-1]
		} else {
			break
		}
	}

	if slashIdx := strings.IndexByte(s, '/'); slashIdx > 0 {
		num, err1 := strconv.ParseFloat(s[:slashIdx], 64)
		den, err2 := strconv.ParseFloat(s[slashIdx+1:], 64)
		if err1 != nil || err2 != nil || num <= 0 || den <= 0 {
			return 0, fmt.Errorf("invalid fractional duration %q", token)
		}
		beats := (4.0 * num / den) * multiplier
		return beats * beatSec, nil
	}

	subdiv, err := strconv.ParseFloat(s, 64)
	if err != nil || subdiv <= 0 {
		return 0, fmt.Errorf("invalid note subdivision duration %q", token)
	}
	beats := (4.0 / subdiv) * multiplier
	return beats * beatSec, nil
}

// PitchToFreq converts scientific pitch notation (e.g. "A4", "C#5", "Bb3", "F2") or "<num>Hz" into Hz.
func PitchToFreq(pitch string) (float64, error) {
	s := strings.TrimSpace(pitch)
	if s == "" {
		return 0, fmt.Errorf("empty pitch")
	}
	lower := strings.ToLower(s)
	if strings.HasSuffix(lower, "hz") {
		hz, err := strconv.ParseFloat(strings.TrimSpace(s[:len(s)-2]), 64)
		if err != nil || hz <= 0 || hz > 22050 {
			return 0, fmt.Errorf("invalid frequency %q (must be in (0, 22050] Hz)", pitch)
		}
		return hz, nil
	}

	noteChar := s[0]
	var semitone int
	switch noteChar {
	case 'C', 'c':
		semitone = 0
	case 'D', 'd':
		semitone = 2
	case 'E', 'e':
		semitone = 4
	case 'F', 'f':
		semitone = 5
	case 'G', 'g':
		semitone = 7
	case 'A', 'a':
		semitone = 9
	case 'B', 'b':
		semitone = 11
	default:
		return 0, fmt.Errorf("invalid pitch %q (expected note A..G or <num>Hz)", pitch)
	}

	idx := 1
	if idx < len(s) {
		switch s[idx] {
		case '#', 's', 'S':
			semitone++
			idx++
		case 'b', 'B':
			semitone--
			idx++
		}
	}
	if idx >= len(s) {
		return 0, fmt.Errorf("pitch %q is missing octave number (e.g. %s4)", pitch, s)
	}
	octave, err := strconv.Atoi(s[idx:])
	if err != nil || octave < -1 || octave > 9 {
		return 0, fmt.Errorf("invalid octave in pitch %q (expected -1..9)", pitch)
	}

	midi := (octave+1)*12 + semitone
	freq := 440.0 * math.Pow(2.0, float64(midi-69)/12.0)
	return freq, nil
}

func parsePitchOrSweep(spec string) (PitchSweep, error) {
	if arrowIdx := strings.Index(spec, "->"); arrowIdx > 0 {
		left := strings.TrimSpace(spec[:arrowIdx])
		right := strings.TrimSpace(spec[arrowIdx+2:])
		startHz, err1 := PitchToFreq(left)
		if err1 != nil {
			return PitchSweep{}, err1
		}
		endHz, err2 := PitchToFreq(right)
		if err2 != nil {
			return PitchSweep{}, err2
		}
		return PitchSweep{StartFreq: startHz, EndFreq: endHz}, nil
	}
	hz, err := PitchToFreq(spec)
	if err != nil {
		return PitchSweep{}, err
	}
	return PitchSweep{StartFreq: hz, EndFreq: hz}, nil
}

func tokenizePatternBody(input string) ([]dslToken, error) {
	var tokens []dslToken
	i := 0
	n := len(input)

	for i < n {
		c := input[i]
		if c == ' ' || c == '\t' || c == '\r' || c == '\n' {
			i++
			continue
		}
		if c == '|' {
			tokens = append(tokens, dslToken{kind: tokPipe, text: "|"})
			i++
			continue
		}
		if c == '(' {
			tokens = append(tokens, dslToken{kind: tokLParen, text: "("})
			i++
			continue
		}
		if c == ')' {
			tokens = append(tokens, dslToken{kind: tokRParen, text: ")"})
			i++
			continue
		}
		if c == '<' {
			tokens = append(tokens, dslToken{kind: tokLAngle, text: "<"})
			i++
			continue
		}
		if c == '>' {
			tokens = append(tokens, dslToken{kind: tokRAngle, text: ">"})
			i++
			continue
		}
		if c == '*' {
			i++
			for i < n && (input[i] == ' ' || input[i] == '\t') {
				i++
			}
			startNum := i
			for i < n && input[i] >= '0' && input[i] <= '9' {
				i++
			}
			if startNum == i {
				return nil, fmt.Errorf("expected repeat count integer after '*'")
			}
			rep, err := strconv.Atoi(input[startNum:i])
			if err != nil || rep <= 0 || rep > maxRepeatFactor {
				return nil, fmt.Errorf("invalid repeat count %q (must be 1..%d)", input[startNum:i], maxRepeatFactor)
			}
			tokens = append(tokens, dslToken{kind: tokRepeat, number: rep})
			continue
		}
		if c == '@' {
			i++
			startMod := i
			for i < n {
				ch := input[i]
				if ch == ' ' || ch == '\t' || ch == '\r' || ch == '\n' || ch == '|' || ch == '(' || ch == ')' || ch == '<' || ch == '*' || ch == '@' {
					break
				}
				if ch == '>' {
					if i > startMod && input[i-1] == '-' {
						i++
						continue
					}
					break
				}
				i++
			}
			modText := strings.TrimSpace(input[startMod:i])
			if modText == "" {
				return nil, fmt.Errorf("expected modifier after '@' (e.g. @+12, @crescendo, @fade_in, @staccato, @mp->ff, @slow=2)")
			}
			tokens = append(tokens, dslToken{kind: tokModifier, text: modText})
			continue
		}

		// Scan an atom token (which may contain [...] chord brackets or inst(...) pitch/euclid args)
		start := i
		for i < n {
			ch := input[i]
			if ch == ' ' || ch == '\t' || ch == '\r' || ch == '\n' || ch == '|' || ch == ')' || ch == '<' || ch == '*' || ch == '@' {
				break
			}
			if ch == '>' {
				if i > start && input[i-1] == '-' {
					i++
					continue
				}
				break
			}
			if ch == '(' {
				// Attached '(' is an argument list like kick(150Hz->40Hz):8 or kick(3,8):1
				closeIdx := strings.IndexByte(input[i:], ')')
				if closeIdx < 0 {
					return nil, fmt.Errorf("unclosed '(' in token starting at %q", input[start:])
				}
				i += closeIdx + 1
				continue
			}
			if ch == '[' {
				closeIdx := strings.IndexByte(input[i:], ']')
				if closeIdx < 0 {
					return nil, fmt.Errorf("unclosed '[' in chord token starting at %q", input[start:])
				}
				i += closeIdx + 1
				continue
			}
			i++
		}
		atomText := strings.TrimSpace(input[start:i])
		if atomText == "" {
			return nil, fmt.Errorf("unexpected character %q", string(input[i]))
		}
		tokens = append(tokens, dslToken{kind: tokAtom, text: atomText})
	}
	return tokens, nil
}

func parsePatternNodes(body string) ([]dslNode, error) {
	tokens, err := tokenizePatternBody(body)
	if err != nil {
		return nil, err
	}
	pos := 0
	nodes, err := parseNodeList(tokens, &pos, tokAtom)
	if err != nil {
		return nil, err
	}
	if len(nodes) == 0 {
		return nil, fmt.Errorf("pattern or track contains no musical events")
	}
	return nodes, nil
}

func splitAtomHeadAndDur(atom string) (head, dur string, hasColon bool) {
	lastBracket := strings.LastIndexAny(atom, "])")
	colonIdx := -1
	if lastBracket >= 0 {
		if rel := strings.IndexByte(atom[lastBracket+1:], ':'); rel >= 0 {
			colonIdx = lastBracket + 1 + rel
		}
	} else {
		colonIdx = strings.IndexByte(atom, ':')
	}
	if colonIdx >= 0 {
		return strings.TrimSpace(atom[:colonIdx]), strings.TrimSpace(atom[colonIdx+1:]), true
	}
	return strings.TrimSpace(atom), "", false
}

func consumeNodePostfixes(tokens []dslToken, pos *int, node *dslNode) error {
	for *pos < len(tokens) {
		if tokens[*pos].kind == tokRepeat {
			node.repeat *= tokens[*pos].number
			*pos++
			continue
		}
		if tokens[*pos].kind == tokModifier {
			mod := tokens[*pos].text
			if semi, isSemi, err := parseSemitoneModifier(mod); isSemi {
				if err != nil {
					return err
				}
				node.transpose += semi
			} else {
				if err := validateDSLModifier(mod); err != nil {
					return err
				}
				node.modifiers = append(node.modifiers, mod)
			}
			*pos++
			continue
		}
		if node.isGroup && tokens[*pos].kind == tokAtom && strings.HasPrefix(tokens[*pos].text, ":") {
			durText := strings.TrimSpace(tokens[*pos].text[1:])
			if durText == "" {
				return fmt.Errorf("missing duration after ':' on group")
			}
			node.groupDur = durText
			*pos++
			continue
		}
		break
	}
	return nil
}

func parseSemitoneModifier(mod string) (int, bool, error) {
	if len(mod) < 2 || (mod[0] != '+' && mod[0] != '-') {
		return 0, false, nil
	}
	for i := 1; i < len(mod); i++ {
		if mod[i] < '0' || mod[i] > '9' {
			return 0, false, nil
		}
	}
	semi, err := strconv.Atoi(mod)
	if err != nil || semi < -48 || semi > 48 {
		return 0, true, fmt.Errorf("invalid semitone transpose '@%s' (must be in -48..+48)", mod)
	}
	return semi, true, nil
}

func parseNodeList(tokens []dslToken, pos *int, closeKind dslTokenKind) ([]dslNode, error) {
	var nodes []dslNode
	for *pos < len(tokens) {
		tok := tokens[*pos]
		switch tok.kind {
		case tokPipe:
			*pos++
			nodes = append(nodes, dslNode{isPipe: true, repeat: 1})
		case tokRParen:
			if closeKind != tokRParen {
				return nil, fmt.Errorf("unmatched ')' in pattern")
			}
			*pos++
			return nodes, nil
		case tokRAngle:
			if closeKind != tokRAngle {
				return nil, fmt.Errorf("unmatched '>' in pattern")
			}
			*pos++
			return nodes, nil
		case tokLParen:
			*pos++
			children, err := parseNodeList(tokens, pos, tokRParen)
			if err != nil {
				return nil, err
			}
			if len(children) == 0 {
				return nil, fmt.Errorf("empty group '()' is not allowed")
			}
			node := dslNode{isGroup: true, children: children, repeat: 1}
			if err := consumeNodePostfixes(tokens, pos, &node); err != nil {
				return nil, err
			}
			nodes = append(nodes, node)
		case tokLAngle:
			*pos++
			children, err := parseNodeList(tokens, pos, tokRAngle)
			if err != nil {
				return nil, err
			}
			if len(children) == 0 {
				return nil, fmt.Errorf("empty alternation '<>' is not allowed")
			}
			node := dslNode{isGroup: true, isAlternate: true, children: children, repeat: 1}
			if err := consumeNodePostfixes(tokens, pos, &node); err != nil {
				return nil, err
			}
			nodes = append(nodes, node)
		case tokAtom:
			*pos++
			node := dslNode{isGroup: false, atom: tok.text, repeat: 1}
			for strings.HasSuffix(node.atom, "~") {
				leftHead, leftDur, okL := splitAtomHeadAndDur(strings.TrimSuffix(node.atom, "~"))
				if !okL || leftDur == "" {
					return nil, fmt.Errorf("invalid tied token %q (requires explicit ':dur~')", node.atom)
				}
				sawPipe := false
				for *pos < len(tokens) && tokens[*pos].kind == tokPipe {
					sawPipe = true
					*pos++
				}
				if sawPipe {
					node.tiePipeOffsets = append(node.tiePipeOffsets, leftDur)
				}
				if *pos >= len(tokens) || tokens[*pos].kind != tokAtom {
					return nil, fmt.Errorf("dangling tie '~' after %q without continuation note or ':dur'", node.atom)
				}
				nextAtom := tokens[*pos].text
				*pos++
				rightHead, rightDur, okR := splitAtomHeadAndDur(nextAtom)
				if !okR || rightDur == "" {
					return nil, fmt.Errorf("invalid tie continuation %q after %q (expected '%s:<dur>' or ':<dur>')", nextAtom, node.atom, leftHead)
				}
				if rightHead != "" && rightHead != leftHead {
					return nil, fmt.Errorf("cannot tie %q to %q (mismatched pitch/instrument %q vs %q)", node.atom, nextAtom, leftHead, rightHead)
				}
				node.atom = leftHead + ":" + leftDur + "~" + rightDur
			}
			if err := consumeNodePostfixes(tokens, pos, &node); err != nil {
				return nil, err
			}
			nodes = append(nodes, node)
		case tokRepeat:
			return nil, fmt.Errorf("unexpected '*%d' without a preceding note, pattern, or group", tok.number)
		case tokModifier:
			return nil, fmt.Errorf("unexpected '@%s' without a preceding note, pattern, or group", tok.text)
		}
	}
	if closeKind == tokRParen {
		return nil, fmt.Errorf("unclosed '(' in pattern")
	}
	if closeKind == tokRAngle {
		return nil, fmt.Errorf("unclosed '<' in pattern")
	}
	return nodes, nil
}

var classicalDynamics = map[string]float64{
	"ppp": 0.20,
	"pp":  0.35,
	"p":   0.55,
	"mp":  0.75,
	"mf":  0.95,
	"f":   1.15,
	"ff":  1.35,
	"fff": 1.55,
}

type articulationPreset struct {
	gateRatio   float64
	attackScale float64
	accentScale float64
}

var classicalArticulations = map[string]articulationPreset{
	"staccato":       {gateRatio: 0.40, attackScale: 1.00, accentScale: 1.00},
	"stacc":          {gateRatio: 0.40, attackScale: 1.00, accentScale: 1.00},
	"spiccato":       {gateRatio: 0.28, attackScale: 0.50, accentScale: 1.00},
	"spicc":          {gateRatio: 0.28, attackScale: 0.50, accentScale: 1.00},
	"pizzicato":      {gateRatio: 0.35, attackScale: 0.15, accentScale: 1.00},
	"pizz":           {gateRatio: 0.35, attackScale: 0.15, accentScale: 1.00},
	"portato":        {gateRatio: 0.70, attackScale: 1.00, accentScale: 1.00},
	"mezzo_staccato": {gateRatio: 0.70, attackScale: 1.00, accentScale: 1.00},
	"legato":         {gateRatio: 1.00, attackScale: 1.00, accentScale: 1.00},
	"arco":           {gateRatio: 1.00, attackScale: 1.00, accentScale: 1.00},
	"ord":            {gateRatio: 1.00, attackScale: 1.00, accentScale: 1.00},
	"normal":         {gateRatio: 1.00, attackScale: 1.00, accentScale: 1.00},
	"tenuto":         {gateRatio: 1.00, attackScale: 1.00, accentScale: 1.06},
	"ten":            {gateRatio: 1.00, attackScale: 1.00, accentScale: 1.06},
	"marcato":        {gateRatio: 0.85, attackScale: 0.50, accentScale: 1.25},
	"marc":           {gateRatio: 0.85, attackScale: 0.50, accentScale: 1.25},
	"accent":         {gateRatio: 0.85, attackScale: 0.50, accentScale: 1.25},
}

func parseDynamicOrGainValue(s string) (float64, error) {
	lower := strings.ToLower(strings.TrimSpace(s))
	if d, ok := classicalDynamics[lower]; ok {
		return d, nil
	}
	v, err := strconv.ParseFloat(lower, 64)
	if err != nil || v < 0.0 || v > 3.0 {
		return 0, fmt.Errorf("invalid dynamic/gain value %q (expected ppp..fff or 0.0..3.0)", s)
	}
	return v, nil
}

func parseGainRampSpec(spec string) (start, mid, end float64, hasMid bool, err error) {
	parts := strings.Split(spec, "->")
	switch len(parts) {
	case 1:
		v, err := parseDynamicOrGainValue(parts[0])
		return v, v, v, false, err
	case 2:
		v0, err0 := parseDynamicOrGainValue(parts[0])
		v1, err1 := parseDynamicOrGainValue(parts[1])
		if err0 != nil {
			return 0, 0, 0, false, err0
		}
		if err1 != nil {
			return 0, 0, 0, false, err1
		}
		return v0, 0.5 * (v0 + v1), v1, false, nil
	case 3:
		v0, err0 := parseDynamicOrGainValue(parts[0])
		v1, err1 := parseDynamicOrGainValue(parts[1])
		v2, err2 := parseDynamicOrGainValue(parts[2])
		if err0 != nil {
			return 0, 0, 0, false, err0
		}
		if err1 != nil {
			return 0, 0, 0, false, err1
		}
		if err2 != nil {
			return 0, 0, 0, false, err2
		}
		return v0, v1, v2, true, nil
	default:
		return 0, 0, 0, false, fmt.Errorf("invalid gain ramp %q (expected val, start->end, or start->mid->end)", spec)
	}
}

func parsePanRampSpec(spec string) (start, end float64, err error) {
	if arrow := strings.Index(spec, "->"); arrow > 0 {
		p0, err0 := strconv.ParseFloat(strings.TrimSpace(spec[:arrow]), 64)
		p1, err1 := strconv.ParseFloat(strings.TrimSpace(spec[arrow+2:]), 64)
		if err0 != nil || err1 != nil || p0 < -1.0 || p0 > 1.0 || p1 < -1.0 || p1 > 1.0 {
			return 0, 0, fmt.Errorf("invalid pan sweep %q (must be in -1.0..+1.0)", spec)
		}
		return p0, p1, nil
	}
	p, err := strconv.ParseFloat(strings.TrimSpace(spec), 64)
	if err != nil || p < -1.0 || p > 1.0 {
		return 0, 0, fmt.Errorf("invalid pan %q (must be in -1.0..+1.0)", spec)
	}
	return p, p, nil
}

func parseEuclidTuple(spec string) (pulses, steps, rot int, err error) {
	parts := strings.Split(strings.TrimSpace(spec), ",")
	if len(parts) < 2 || len(parts) > 3 {
		return 0, 0, 0, fmt.Errorf("invalid Euclidean rhythm %q (expected pulses,steps or pulses,steps,rotation)", spec)
	}
	k, err1 := strconv.Atoi(strings.TrimSpace(parts[0]))
	n, err2 := strconv.Atoi(strings.TrimSpace(parts[1]))
	if err1 != nil || err2 != nil || k < 1 || n < 1 || k > n || n > 128 {
		return 0, 0, 0, fmt.Errorf("invalid Euclidean rhythm %q (expected 1 <= pulses <= steps <= 128)", spec)
	}
	r := 0
	if len(parts) == 3 {
		var err3 error
		r, err3 = strconv.Atoi(strings.TrimSpace(parts[2]))
		if err3 != nil {
			return 0, 0, 0, fmt.Errorf("invalid Euclidean rotation in %q", spec)
		}
	}
	return k, n, r, nil
}

func resolveGainModifier(mod string) (start, mid, end float64, hasMid, isGainMod bool, err error) {
	lower := strings.ToLower(strings.TrimSpace(mod))
	if d, ok := classicalDynamics[lower]; ok {
		return d, d, d, false, true, nil
	}
	switch lower {
	case "cresc", "crescendo":
		return 0.50, 0.875, 1.25, false, true, nil
	case "decresc", "decrescendo", "dim", "diminuendo":
		return 1.20, 0.825, 0.45, false, true, nil
	case "fade_in", "fadein":
		return 0.00, 0.50, 1.00, false, true, nil
	case "fade_out", "fadeout":
		return 1.00, 0.50, 0.00, false, true, nil
	case "swell":
		return 0.40, 1.25, 0.40, true, true, nil
	}
	if eq := strings.IndexByte(lower, '='); eq > 0 {
		key := lower[:eq]
		val := lower[eq+1:]
		switch key {
		case "vol", "volume", "gain", "cresc", "crescendo", "decresc", "decrescendo", "dim", "diminuendo", "fade_in", "fadein", "fade_out", "fadeout", "swell":
			s, m, e, hm, err := parseGainRampSpec(val)
			return s, m, e, hm, true, err
		}
		return 0, 0, 0, false, false, nil
	}
	if strings.Contains(lower, "->") {
		s, m, e, hm, err := parseGainRampSpec(lower)
		return s, m, e, hm, true, err
	}
	return 0, 0, 0, false, false, nil
}

func validateDSLModifier(mod string) error {
	lower := strings.ToLower(strings.TrimSpace(mod))
	if _, ok := classicalArticulations[lower]; ok {
		return nil
	}
	if _, _, _, _, isGain, err := resolveGainModifier(lower); isGain || err != nil {
		return err
	}
	if eq := strings.IndexByte(lower, '='); eq > 0 {
		key := lower[:eq]
		val := lower[eq+1:]
		switch key {
		case "gate", "clip":
			g, err := strconv.ParseFloat(val, 64)
			if err != nil || g <= 0.0 || g > 1.0 {
				return fmt.Errorf("invalid @%s=%s (must be in (0.0, 1.0])", key, val)
			}
			return nil
		case "slow", "fast":
			f, err := strconv.ParseFloat(val, 64)
			if err != nil || f <= 0.0 || f > 64.0 {
				return fmt.Errorf("invalid @%s=%s (must be in (0.0, 64.0])", key, val)
			}
			return nil
		case "pan":
			_, _, err := parsePanRampSpec(val)
			return err
		case "lpf":
			a, err := strconv.ParseFloat(val, 64)
			if err != nil || a <= 0.0 || a > 1.0 {
				return fmt.Errorf("invalid @lpf=%s (must be in (0.0, 1.0])", val)
			}
			return nil
		case "hpf":
			a, err := strconv.ParseFloat(val, 64)
			if err != nil || a <= 0.0 || a >= 1.0 {
				return fmt.Errorf("invalid @hpf=%s (must be in (0.0, 1.0))", val)
			}
			return nil
		case "euclid":
			_, _, _, err := parseEuclidTuple(val)
			return err
		}
	}
	return fmt.Errorf("unrecognized modifier '@%s' (valid: @+12, @-7, @crescendo, @diminuendo, @fade_in, @fade_out, @swell, @pp..@fff, @mp->ff, @vol=..., @staccato, @spiccato, @pizzicato, @portato, @legato, @tenuto, @marcato, @gate=..., @slow=..., @fast=..., @pan=..., @lpf=..., @hpf=..., @euclid=k,n)", mod)
}

func subdivideEuclideanEvent(ev NoteEvent, pulses, steps, rot int) []NoteEvent {
	stepDur := ev.DurationSec / float64(steps)
	out := make([]NoteEvent, 0, steps)
	for i := 0; i < steps; i++ {
		idx := ((i - rot) % steps + steps) % steps
		isHit := (idx*pulses)%steps < pulses
		stepEv := ev
		stepEv.DurationSec = stepDur
		if !isHit {
			stepEv.IsRest = true
			stepEv.Pitches = nil
		} else if len(ev.Pitches) > 0 {
			pitchesCopy := make([]PitchSweep, len(ev.Pitches))
			copy(pitchesCopy, ev.Pitches)
			stepEv.Pitches = pitchesCopy
		}
		out = append(out, stepEv)
	}
	return out
}

func evalGainCurve(u, start, mid, end float64, hasMid bool) float64 {
	if u < 0.0 {
		u = 0.0
	} else if u > 1.0 {
		u = 1.0
	}
	if hasMid {
		if u <= 0.5 {
			return start + (mid-start)*(u*2.0)
		}
		return mid + (end-mid)*((u-0.5)*2.0)
	}
	return start + (end-start)*u
}

func applyNodeModifiers(events []NoteEvent, modifiers []string) ([]NoteEvent, error) {
	if len(events) == 0 || len(modifiers) == 0 {
		return events, nil
	}
	out := make([]NoteEvent, len(events))
	copy(out, events)

	for _, mod := range modifiers {
		lower := strings.ToLower(strings.TrimSpace(mod))

		// 1. Articulation presets
		if art, ok := classicalArticulations[lower]; ok {
			for i := range out {
				if out[i].IsRest {
					continue
				}
				out[i].GateRatio = art.gateRatio
				out[i].AttackScale = art.attackScale
				if art.accentScale != 1.0 {
					if !out[i].HasCustomGain {
						out[i].GainStart = 1.0
						out[i].GainMid = 1.0
						out[i].GainEnd = 1.0
						out[i].HasCustomGain = true
					}
					out[i].GainStart *= art.accentScale
					out[i].GainMid *= art.accentScale
					out[i].GainEnd *= art.accentScale
				}
			}
			continue
		}

		// 2. Dynamics and volume envelopes (@pp..@fff, @crescendo, @fade_in, @fade_out, @swell, @mp->ff, @vol=...)
		if gStart, gMid, gEnd, hasMid, isGain, err := resolveGainModifier(lower); isGain || err != nil {
			if err != nil {
				return nil, err
			}
			var totalDur float64
			for _, ev := range out {
				totalDur += ev.DurationSec
			}
			if totalDur <= 0 {
				totalDur = 1.0
			}
			cursor := 0.0
			for i := range out {
				u0 := cursor / totalDur
				cursor += out[i].DurationSec
				u1 := cursor / totalDur
				uMid := 0.5 * (u0 + u1)
				if out[i].IsRest {
					continue
				}
				if !out[i].HasCustomGain {
					out[i].GainStart = 1.0
					out[i].GainMid = 1.0
					out[i].GainEnd = 1.0
					out[i].HasCustomGain = true
				} else if !out[i].HasGainMid {
					out[i].GainMid = 0.5 * (out[i].GainStart + out[i].GainEnd)
				}
				out[i].GainStart *= evalGainCurve(u0, gStart, gMid, gEnd, hasMid)
				out[i].GainMid *= evalGainCurve(uMid, gStart, gMid, gEnd, hasMid)
				out[i].GainEnd *= evalGainCurve(u1, gStart, gMid, gEnd, hasMid)
				if hasMid {
					out[i].HasGainMid = true
				}
			}
			continue
		}

		// 3. Key=Value modifiers (gate, slow, fast, pan, lpf, hpf, euclid)
		if eq := strings.IndexByte(lower, '='); eq > 0 {
			key := lower[:eq]
			val := lower[eq+1:]
			switch key {
			case "gate", "clip":
				g, err := strconv.ParseFloat(val, 64)
				if err != nil || g <= 0 || g > 1.0 {
					return nil, fmt.Errorf("invalid @%s=%s", key, val)
				}
				for i := range out {
					if !out[i].IsRest {
						out[i].GateRatio = g
					}
				}
			case "slow":
				f, err := strconv.ParseFloat(val, 64)
				if err != nil || f <= 0 {
					return nil, fmt.Errorf("invalid @slow=%s", val)
				}
				for i := range out {
					out[i].DurationSec *= f
				}
			case "fast":
				f, err := strconv.ParseFloat(val, 64)
				if err != nil || f <= 0 {
					return nil, fmt.Errorf("invalid @fast=%s", val)
				}
				for i := range out {
					out[i].DurationSec /= f
				}
			case "pan":
				pStart, pEnd, err := parsePanRampSpec(val)
				if err != nil {
					return nil, err
				}
				var totalDur float64
				for _, ev := range out {
					totalDur += ev.DurationSec
				}
				if totalDur <= 0 {
					totalDur = 1.0
				}
				cursor := 0.0
				for i := range out {
					u0 := cursor / totalDur
					cursor += out[i].DurationSec
					u1 := cursor / totalDur
					if !out[i].IsRest {
						out[i].HasCustomPan = true
						out[i].PanStart = pStart + (pEnd-pStart)*u0
						out[i].PanEnd = pStart + (pEnd-pStart)*u1
					}
				}
			case "lpf":
				a, err := strconv.ParseFloat(val, 64)
				if err != nil || a <= 0 || a > 1.0 {
					return nil, fmt.Errorf("invalid @lpf=%s", val)
				}
				for i := range out {
					if !out[i].IsRest {
						out[i].LPFOverride = a
					}
				}
			case "hpf":
				a, err := strconv.ParseFloat(val, 64)
				if err != nil || a <= 0 || a >= 1.0 {
					return nil, fmt.Errorf("invalid @hpf=%s", val)
				}
				for i := range out {
					if !out[i].IsRest {
						out[i].HPFOverride = a
					}
				}
			case "euclid":
				k, n, rot, err := parseEuclidTuple(val)
				if err != nil {
					return nil, err
				}
				var expanded []NoteEvent
				for _, ev := range out {
					if ev.IsRest {
						expanded = append(expanded, ev)
					} else {
						expanded = append(expanded, subdivideEuclideanEvent(ev, k, n, rot)...)
					}
				}
				out = expanded
			}
		}
	}
	return out, nil
}

func (s *Score) checkBarlineAlignment(cumSec float64) error {
	if !s.ValidateBarlines {
		return nil
	}
	beatSec := 60.0 / s.BPM
	cumBeats := cumSec / beatSec
	barBeats := 4.0 * float64(s.TimeSigNum) / float64(s.TimeSigDen)
	bars := cumBeats / barBeats
	nearestBars := math.Round(bars)
	if math.Abs(bars-nearestBars) > 1e-4 {
		return fmt.Errorf("barline '|' misalignment at %.4f beats (%.4f bars of %.2f beats; off by %+.4f beats)", cumBeats, bars, barBeats, cumBeats-nearestBars*barBeats)
	}
	return nil
}

func (s *Score) expandNodesToEvents(nodes []dslNode, defaultInst string, transposeSemi int, activePatterns map[string]bool, cycleIdx int) ([]NoteEvent, error) {
	evs, _, err := s.expandNodesToEventsWithDur(nodes, defaultInst, "4", false, transposeSemi, activePatterns, cycleIdx)
	return evs, err
}

func (s *Score) expandNodesToEventsWithDur(nodes []dslNode, defaultInst string, initialStepDur string, hasGroupScopedDur bool, transposeSemi int, activePatterns map[string]bool, cycleIdx int) ([]NoteEvent, string, error) {
	if len(activePatterns) > maxPatternDepth {
		return nil, "", fmt.Errorf("maximum pattern nesting depth (%d) exceeded", maxPatternDepth)
	}
	var out []NoteEvent
	defaultStepDur := initialStepDur
	if defaultStepDur == "" {
		defaultStepDur = "4"
	}

	for _, node := range nodes {
		if node.isPipe {
			var cumSec float64
			for _, ev := range out {
				cumSec += ev.DurationSec
			}
			if err := s.checkBarlineAlignment(cumSec); err != nil {
				return nil, "", err
			}
			continue
		}

		if s.ValidateBarlines && len(node.tiePipeOffsets) > 0 {
			var baseSec float64
			for _, ev := range out {
				baseSec += ev.DurationSec
			}
			for _, offDur := range node.tiePipeOffsets {
				offSec, err := ParseDuration(offDur, s.BPM)
				if err != nil {
					return nil, "", err
				}
				if err := s.checkBarlineAlignment(baseSec + offSec); err != nil {
					return nil, "", err
				}
			}
		}

		totalTranspose := transposeSemi + node.transpose
		var nodeEvents []NoteEvent

		childInitDur := defaultStepDur
		childScoped := hasGroupScopedDur
		if node.groupDur != "" {
			childInitDur = node.groupDur
			childScoped = true
		}

		for r := 0; r < node.repeat; r++ {
			subCycle := cycleIdx
			if node.repeat > 1 {
				subCycle = r
			}

			if node.isGroup && node.isAlternate {
				chosen := node.children[subCycle%len(node.children)]
				subEvents, nextDur, err := s.expandNodesToEventsWithDur([]dslNode{chosen}, defaultInst, childInitDur, childScoped, totalTranspose, activePatterns, subCycle)
				if err != nil {
					return nil, "", err
				}
				if r == 0 && !childScoped {
					defaultStepDur = nextDur
				}
				nodeEvents = append(nodeEvents, subEvents...)
				continue
			}

			if node.isGroup {
				subEvents, nextDur, err := s.expandNodesToEventsWithDur(node.children, defaultInst, childInitDur, childScoped, totalTranspose, activePatterns, subCycle)
				if err != nil {
					return nil, "", err
				}
				if r == 0 && !childScoped {
					defaultStepDur = nextDur
				}
				nodeEvents = append(nodeEvents, subEvents...)
				continue
			}

			// Check if node.atom is a pattern reference
			if patNodes, isPat := s.Patterns[node.atom]; isPat {
				if activePatterns[node.atom] {
					return nil, "", fmt.Errorf("cyclic pattern reference detected involving %q", node.atom)
				}
				activePatterns[node.atom] = true
				patEvents, _, err := s.expandNodesToEventsWithDur(patNodes, defaultInst, "4", false, totalTranspose, activePatterns, subCycle)
				delete(activePatterns, node.atom)
				if err != nil {
					return nil, "", fmt.Errorf("in pattern %q: %w", node.atom, err)
				}
				nodeEvents = append(nodeEvents, patEvents...)
				continue
			}

			// Otherwise parse atom as one or more events (supporting Euclidean rhythm atom(k,n[,rot]):dur)
			atomEvs, usedDurStr, err := s.parseAtomEvents(node.atom, defaultInst, defaultStepDur, totalTranspose)
			if err != nil {
				return nil, "", err
			}
			if r == 0 && usedDurStr != "" && !hasGroupScopedDur {
				defaultStepDur = usedDurStr
			}
			nodeEvents = append(nodeEvents, atomEvs...)
		}

		if len(node.modifiers) > 0 {
			var err error
			nodeEvents, err = applyNodeModifiers(nodeEvents, node.modifiers)
			if err != nil {
				return nil, "", err
			}
		}

		out = append(out, nodeEvents...)
	}
	return out, defaultStepDur, nil
}

func (s *Score) parseAtomEvents(atom, defaultInst, fallbackDur string, transposeSemi int) ([]NoteEvent, string, error) {
	head := atom
	durSuffix := ""
	lastBracket := strings.LastIndexAny(atom, "])")
	colonIdx := -1
	if lastBracket >= 0 {
		if rel := strings.IndexByte(atom[lastBracket+1:], ':'); rel >= 0 {
			colonIdx = lastBracket + 1 + rel
		}
	} else {
		colonIdx = strings.IndexByte(atom, ':')
	}
	if colonIdx >= 0 {
		head = strings.TrimSpace(atom[:colonIdx])
		durSuffix = atom[colonIdx:]
	}

	// Check for Euclidean rhythm suffix on head: e.g. kick(3,8):1, E3(5,8):1, [E4 G4 B4](3,8,1):1
	if openPar := strings.LastIndexByte(head, '('); openPar > 0 && strings.HasSuffix(head, ")") {
		inner := strings.TrimSpace(head[openPar+1 : len(head)-1])
		if strings.Contains(inner, ",") {
			k, n, rot, err := parseEuclidTuple(inner)
			if err != nil {
				return nil, "", fmt.Errorf("in token %q: %w", atom, err)
			}
			baseAtom := strings.TrimSpace(head[:openPar]) + durSuffix
			baseEv, usedDurStr, err := s.parseSingleAtomEvent(baseAtom, defaultInst, fallbackDur, transposeSemi)
			if err != nil {
				return nil, "", err
			}
			return subdivideEuclideanEvent(baseEv, k, n, rot), usedDurStr, nil
		}
	}

	ev, usedDurStr, err := s.parseSingleAtomEvent(atom, defaultInst, fallbackDur, transposeSemi)
	if err != nil {
		return nil, "", err
	}
	return []NoteEvent{ev}, usedDurStr, nil
}

func (s *Score) parseSingleAtomEvent(atom, defaultInst, fallbackDur string, transposeSemi int) (NoteEvent, string, error) {
	head := atom
	durStr := ""

	// Split ':duration' suffix (making sure we split outside ']' or ')')
	lastBracket := strings.LastIndexAny(atom, "])")
	colonIdx := -1
	if lastBracket >= 0 {
		if rel := strings.IndexByte(atom[lastBracket+1:], ':'); rel >= 0 {
			colonIdx = lastBracket + 1 + rel
		}
	} else {
		colonIdx = strings.IndexByte(atom, ':')
	}

	if colonIdx >= 0 {
		head = strings.TrimSpace(atom[:colonIdx])
		durStr = strings.TrimSpace(atom[colonIdx+1:])
		if durStr == "" {
			return NoteEvent{}, "", fmt.Errorf("missing duration after ':' in token %q", atom)
		}
	}

	effectiveDurStr := durStr
	if effectiveDurStr == "" {
		effectiveDurStr = fallbackDur
	}
	durSec, err := ParseDuration(effectiveDurStr, s.BPM)
	if err != nil {
		return NoteEvent{}, "", fmt.Errorf("in token %q: %w", atom, err)
	}

	// 1. Check for Rest ('R', 'r', '_', '.')
	if head == "R" || head == "r" || head == "_" || head == "." {
		return NoteEvent{
			IsRest:      true,
			DurationSec: durSec,
		}, durStr, nil
	}

	transposeMultiplier := 1.0
	if transposeSemi != 0 {
		transposeMultiplier = math.Pow(2.0, float64(transposeSemi)/12.0)
	}

	// 2. Check for Chord '[p1 p2 ...]' or 'inst[p1 p2 ...]'
	if openBr := strings.IndexByte(head, '['); openBr >= 0 && strings.HasSuffix(head, "]") {
		instName := strings.TrimSpace(head[:openBr])
		if instName == "" {
			instName = defaultInst
		}
		if instName == "" {
			return NoteEvent{}, "", fmt.Errorf("chord token %q requires a track default instrument or 'inst[...]' prefix", atom)
		}
		inst, ok := s.Instruments[instName]
		if !ok {
			return NoteEvent{}, "", fmt.Errorf("chord token %q references unknown instrument %q", atom, instName)
		}
		inner := strings.ReplaceAll(head[openBr+1:len(head)-1], ",", " ")
		pitchTokens := strings.Fields(inner)
		if len(pitchTokens) == 0 {
			return NoteEvent{}, "", fmt.Errorf("empty chord %q", atom)
		}
		var sweeps []PitchSweep
		for _, pt := range pitchTokens {
			sw, err := parsePitchOrSweep(pt)
			if err != nil {
				return NoteEvent{}, "", fmt.Errorf("in chord %q: %w", atom, err)
			}
			sw.StartFreq *= transposeMultiplier
			sw.EndFreq *= transposeMultiplier
			sweeps = append(sweeps, sw)
		}
		return NoteEvent{
			IsRest:      false,
			Inst:        inst,
			Pitches:     sweeps,
			DurationSec: durSec,
		}, durStr, nil
	}

	// 3. Check for Instrument Trigger with explicit pitch/sweep: 'inst(pitchOrSweep)'
	if openPar := strings.IndexByte(head, '('); openPar > 0 && strings.HasSuffix(head, ")") {
		instName := strings.TrimSpace(head[:openPar])
		inst, ok := s.Instruments[instName]
		if !ok {
			return NoteEvent{}, "", fmt.Errorf("token %q references unknown instrument %q", atom, instName)
		}
		inner := strings.TrimSpace(head[openPar+1 : len(head)-1])
		sw, err := parsePitchOrSweep(inner)
		if err != nil {
			return NoteEvent{}, "", fmt.Errorf("in instrument trigger %q: %w", atom, err)
		}
		sw.StartFreq *= transposeMultiplier
		sw.EndFreq *= transposeMultiplier
		return NoteEvent{
			IsRest:      false,
			Inst:        inst,
			Pitches:     []PitchSweep{sw},
			DurationSec: durSec,
		}, durStr, nil
	}

	// 4. Check for bare Instrument Trigger: 'kick:8', 'snare:16', 'hat:16'
	if inst, ok := s.Instruments[head]; ok {
		if defaultInst != "" && defaultInst != head && (s.ExplicitInstruments == nil || !s.ExplicitInstruments[head]) {
			if defInst, defOk := s.Instruments[defaultInst]; defOk && isDrumKitWave(defInst.WaveType) && isDrumKitWave(inst.WaveType) {
				if defInst.Muted {
					inst.Muted = true
					inst.Volume = 0
				} else if volScale := defInst.Volume / 0.19; volScale > 0 {
					inst.Volume *= volScale
				}
				inst.Pan = math.Max(-1.0, math.Min(1.0, inst.Pan+defInst.Pan))
			}
		}
		startHz := inst.DefaultStartFreq
		endHz := inst.DefaultEndFreq
		if startHz <= 0 {
			startHz = 440.0
			endHz = 440.0
		}
		return NoteEvent{
			IsRest:      false,
			Inst:        inst,
			Pitches:     []PitchSweep{{StartFreq: startHz * transposeMultiplier, EndFreq: endHz * transposeMultiplier}},
			DurationSec: durSec,
		}, durStr, nil
	}

	// 5. Otherwise, parse as a Pitch or Frequency Sweep using the track's default instrument
	sw, err := parsePitchOrSweep(head)
	if err != nil {
		return NoteEvent{}, "", fmt.Errorf("unrecognized note, pattern, or instrument %q: %w", atom, err)
	}
	if defaultInst == "" {
		return NoteEvent{}, "", fmt.Errorf("pitch token %q used on a track without a default instrument", atom)
	}
	inst, ok := s.Instruments[defaultInst]
	if !ok {
		return NoteEvent{}, "", fmt.Errorf("unknown default instrument %q", defaultInst)
	}
	sw.StartFreq *= transposeMultiplier
	sw.EndFreq *= transposeMultiplier

	return NoteEvent{
		IsRest:      false,
		Inst:        inst,
		Pitches:     []PitchSweep{sw},
		DurationSec: durSec,
	}, durStr, nil
}

// ============================================================================
// 3. DRIFT-FREE DSP SYNTHESIS & 4-BYTE ALIGNED PCM MIXING
// ============================================================================

// AlignPCMBytes enforces 4-byte stereo frame alignment (16-bit Left + 16-bit Right)
// required by Ebitengine's audio.Context to prevent runtime panics on odd byte counts.
func AlignPCMBytes(n int) int {
	return n &^ 3
}

// AlignPCMOffset enforces 4-byte stereo frame alignment on int64 stream seek/loop offsets.
func AlignPCMOffset(offset int64) int64 {
	return offset &^ 3
}

// SynthesizeScore renders all tracks of a parsed Score into a 4-byte aligned 16-bit 44.1kHz stereo PCM buffer.
// When score.SynthEngine is "apple", it dispatches to macOS CoreAudio / AudioToolbox sampled synthesis.
func SynthesizeScore(score *Score) ([]byte, error) {
	mixed, _, err := SynthesizeScoreWithStems(score)
	return mixed, err
}

// SynthesizeScoreWithStems renders all tracks of a parsed Score into both a mixed 16-bit 44.1kHz stereo PCM buffer
// and a per-track slice of 4-byte aligned stereo PCM stem buffers (aligned 1:1 with score.Tracks).
func SynthesizeScoreWithStems(score *Score) ([]byte, [][]byte, error) {
	if score == nil || len(score.Tracks) == 0 {
		return nil, nil, fmt.Errorf("synthesize score: score is nil or has no tracks")
	}
	if strings.EqualFold(score.SynthEngine, "apple") {
		return SynthesizeScoreAppleWithStems(score)
	}
	return SynthesizeScoreProceduralWithStems(score)
}

func applyScorePostFX(pcm []byte, score *Score) ([]byte, error) {
	if len(pcm) == 0 || score == nil {
		return pcm, nil
	}
	out := pcm
	if score.GlobalLPF > 0 {
		out = ApplyLowPassFilter(out, score.GlobalLPF)
	}
	if score.GlobalHPF > 0 {
		out = ApplyHighPassFilter(out, score.GlobalHPF)
	}
	if score.GlobalBitcrushBits > 0 {
		out = ApplyBitcrush(out, score.GlobalBitcrushBits, score.GlobalBitcrushDownsample)
	}
	if score.HasLoopSlice {
		sliced, err := SliceLoopPCM(out, score.LoopStartSec, score.LoopEndSec)
		if err != nil {
			return nil, err
		}
		out = sliced
	}
	return out[:len(out)&^3], nil
}

// SynthesizeScoreProcedural renders all tracks using the pure-Go YM2612 4-op FM, SN76489 PSG, and procedural DSP engine.
func SynthesizeScoreProcedural(score *Score) ([]byte, error) {
	mixed, _, err := SynthesizeScoreProceduralWithStems(score)
	return mixed, err
}

// SynthesizeScoreProceduralWithStems renders all tracks in parallel across CPU cores using the pure-Go
// YM2612 4-op FM, SN76489 PSG, and procedural DSP engine, returning both the master mix and per-track stems.
func SynthesizeScoreProceduralWithStems(score *Score) ([]byte, [][]byte, error) {
	if score == nil || len(score.Tracks) == 0 {
		return nil, nil, fmt.Errorf("synthesize score: score is nil or has no tracks")
	}

	trackPCMs := make([][]byte, len(score.Tracks))
	var wg sync.WaitGroup
	for trIdx, tr := range score.Tracks {
		wg.Add(1)
		go func(idx int, events []NoteEvent) {
			defer wg.Done()
			trackPCMs[idx] = synthesizeTrackEvents(events)
		}(trIdx, tr.Events)
	}
	wg.Wait()

	var nonEmpty [][]byte
	for _, pcm := range trackPCMs {
		if len(pcm) > 0 {
			nonEmpty = append(nonEmpty, pcm)
		}
	}
	if len(nonEmpty) == 0 {
		return nil, nil, fmt.Errorf("synthesize score: rendered tracks produced 0 PCM bytes")
	}

	mixed := MixTracksPCM(nonEmpty)
	var err error
	mixed, err = applyScorePostFX(mixed, score)
	if err != nil {
		return nil, nil, err
	}

	for i := range trackPCMs {
		if len(trackPCMs[i]) > 0 {
			stemOut, stemErr := applyScorePostFX(trackPCMs[i], score)
			if stemErr == nil {
				trackPCMs[i] = stemOut
			}
		}
	}

	return mixed, trackPCMs, nil
}

// synthesizeTrackEvents renders a sequence of NoteEvents using cumulative sample rounding
// so multi-bar tracks with different subdivisions never accumulate floating-point timing drift.
func synthesizeTrackEvents(events []NoteEvent) []byte {
	var totalSec float64
	for _, ev := range events {
		if ev.DurationSec > 0 {
			totalSec += ev.DurationSec
		}
	}
	totalSamples := int(math.Round(totalSec * SampleRate))
	if totalSamples <= 0 {
		return nil
	}

	buf := make([]byte, (totalSamples*BytesPerFrame)&^3)
	cursorSec := 0.0

	for eventIdx, ev := range events {
		if ev.DurationSec <= 0 {
			continue
		}
		startSample := int(math.Round(cursorSec * SampleRate))
		cursorSec += ev.DurationSec
		endSample := int(math.Round(cursorSec * SampleRate))
		if endSample > totalSamples {
			endSample = totalSamples
		}
		numSamples := endSample - startSample
		if numSamples <= 0 || ev.IsRest || len(ev.Pitches) == 0 {
			continue
		}

		sliceBytes := buf[startSample*BytesPerFrame : endSample*BytesPerFrame]
		seed := int64(eventIdx)*7919 + int64(startSample)
		renderNoteEventInto(sliceBytes, numSamples, ev, seed)
	}

	return buf[:len(buf)&^3]
}

func renderNoteEventInto(out []byte, numSamples int, ev NoteEvent, rngSeed int64) {
	inst := ev.Inst
	if inst.Muted {
		return
	}
	durSec := float64(numSamples) / SampleRate

	gateRatio := ev.GateRatio
	if gateRatio <= 0 || gateRatio > 1.0 {
		gateRatio = 1.0
	}
	activeSamples := numSamples
	if gateRatio < 1.0 {
		activeSamples = int(math.Round(float64(numSamples) * gateRatio))
		if activeSamples < 1 {
			activeSamples = 1
		}
	}
	activeDurSec := float64(activeSamples) / SampleRate

	attack := inst.Attack
	if ev.AttackScale > 0 {
		attack *= ev.AttackScale
	}

	panStart := inst.Pan
	panEnd := inst.Pan
	if ev.HasCustomPan {
		panStart = ev.PanStart
		panEnd = ev.PanEnd
	}
	panStart = math.Max(-1.0, math.Min(1.0, panStart))
	panEnd = math.Max(-1.0, math.Min(1.0, panEnd))
	staticPan := panStart == panEnd
	leftPan := math.Cos((panStart + 1.0) * math.Pi / 4.0)
	rightPan := math.Sin((panStart + 1.0) * math.Pi / 4.0)

	vol := inst.Volume
	if vol <= 0 {
		vol = 0.2
	}
	gainStart := 1.0
	gainMid := 1.0
	gainEnd := 1.0
	if ev.HasCustomGain {
		gainStart = ev.GainStart
		gainMid = ev.GainMid
		gainEnd = ev.GainEnd
	}

	numVoices := len(ev.Pitches)
	voiceScale := 1.0 / math.Sqrt(float64(numVoices))

	phases := make([]float64, numVoices)
	modPhases := make([]float64, numVoices)
	ymStates := make([]ym2612VoiceState, numVoices)
	ymPatch, isYMPatch := LookupYM2612PatchForInst(inst)
	ymDrumWave, isYMDrum := ResolveYM2612DrumWave(inst)
	var filterVal float64
	var ymDrumFilter float64
	rng := rand.New(rand.NewPCG(uint64(rngSeed), uint64(rngSeed)^0x9e3779b97f4a7c15))

	filterCoeff := inst.NoiseFilter
	if filterCoeff <= 0 || filterCoeff > 1.0 {
		filterCoeff = 1.0
	}
	blend := inst.NoiseBlend
	if blend < 0 {
		blend = 0
	} else if blend > 1.0 {
		blend = 1.0
	}

	for i := 0; i < activeSamples; i++ {
		t := float64(i) / SampleRate
		progress := t / durSec

		var voiceSum float64
		for vIdx, sw := range ev.Pitches {
			var currentFreq float64
			if sw.StartFreq == sw.EndFreq {
				currentFreq = sw.StartFreq
			} else if sw.StartFreq > 0 && sw.EndFreq > 0 {
				currentFreq = sw.StartFreq * math.Pow(sw.EndFreq/sw.StartFreq, progress)
			} else {
				currentFreq = sw.StartFreq + progress*(sw.EndFreq-sw.StartFreq)
			}

			if inst.VibratoFreq > 0 && inst.VibratoDepth > 0 {
				vibScale := 1.0
				switch inst.WaveType {
				case "violin", "cello", "strings", "voice", "flute", "oboe", "clarinet", "shakuhachi", "brass", "trumpet", "horn", "overdriven_guitar", "rhythm_guitar", "ym2612_guitar", "ym2612_rhythm_guitar", "ym2612_strings", "ym2612_choir", "ym2612_flute", "ym2612_brass":
					// Natural vibrato bloom over 120ms
					vibScale = 0.65 + 0.35*math.Min(1.0, t/0.12)
				}
				currentFreq += math.Sin(2.0*math.Pi*inst.VibratoFreq*t) * inst.VibratoDepth * vibScale
			}

			if isYMPatch {
				ymKeyOffSec := math.Max(0.005, activeDurSec-math.Min(inst.Release, activeDurSec*0.25))
				oscAmp := stepYM2612Voice(&ymStates[vIdx], ymPatch, currentFreq, t, ymKeyOffSec, inst.DutyCycle)
				voiceSum += oscAmp * voiceScale
				continue
			}
			if isYMDrum {
				oscAmp := stepYM2612Drum(ymDrumWave, t, sw.StartFreq, sw.EndFreq, activeDurSec, rng, &ymDrumFilter)
				voiceSum += oscAmp * voiceScale
				continue
			}

			dt := currentFreq / SampleRate
			phases[vIdx] += dt
			for phases[vIdx] >= 1.0 {
				phases[vIdx] -= 1.0
			}
			phase := phases[vIdx]
			theta := 2.0 * math.Pi * phase

			var modFreq float64
			if inst.ModRatio > 0 {
				modFreq = currentFreq * inst.ModRatio
			} else if inst.ModFreq > 0 {
				modFreq = inst.ModFreq
			} else if inst.WaveType == "fm" || inst.WaveType == "epiano" || inst.WaveType == "piano" {
				modFreq = currentFreq * 2.0
			} else if inst.WaveType == "bell" {
				modFreq = currentFreq * 3.5
			}
			if modFreq > 0 {
				modPhases[vIdx] += modFreq / SampleRate
				for modPhases[vIdx] >= 1.0 {
					modPhases[vIdx] -= 1.0
				}
			}

			var oscAmp float64
			switch inst.WaveType {
			case "fm":
				modIndex := inst.ModIndex
				if modIndex <= 0 {
					modIndex = 2.0
				}
				modSample := math.Sin(2.0 * math.Pi * modPhases[vIdx])
				oscAmp = math.Sin(theta + modIndex*modSample)
			case "violin":
				rolloff := 1.0 / (1.0 + currentFreq/850.0)
				oscAmp = (math.Sin(theta) +
					0.52*math.Sin(2.0*theta) +
					0.32*rolloff*math.Sin(3.0*theta) +
					0.18*rolloff*math.Sin(4.0*theta) +
					0.09*rolloff*math.Sin(5.0*theta) +
					0.04*rolloff*math.Sin(6.0*theta)) * 0.56
			case "cello":
				rolloff := 1.0 / (1.0 + currentFreq/650.0)
				oscAmp = (math.Sin(theta) +
					0.58*math.Sin(2.0*theta) +
					0.36*rolloff*math.Sin(3.0*theta) +
					0.19*rolloff*math.Sin(4.0*theta) +
					0.08*rolloff*math.Sin(5.0*theta)) * 0.54
			case "strings":
				rolloff := 1.0 / (1.0 + currentFreq/900.0)
				oscAmp = (math.Sin(theta) +
					0.44*math.Sin(2.0*theta) +
					0.24*rolloff*math.Sin(3.0*theta) +
					0.11*rolloff*math.Sin(4.0*theta)) * 0.62
			case "voice":
				rolloff := 1.0 / (1.0 + currentFreq/950.0)
				oscAmp = (math.Sin(theta) +
					0.36*math.Sin(2.0*theta) +
					0.15*rolloff*math.Sin(3.0*theta)) * 0.72
			case "flute", "shakuhachi":
				oscAmp = (math.Sin(theta) + 0.22*math.Sin(2.0*theta) + 0.07*math.Sin(3.0*theta)) * 0.80
			case "oboe":
				rolloff := 1.0 / (1.0 + currentFreq/1100.0)
				oscAmp = (0.55*math.Sin(theta) + 0.65*math.Sin(2.0*theta) + 0.42*rolloff*math.Sin(3.0*theta) + 0.20*rolloff*math.Sin(4.0*theta)) * 0.58
			case "clarinet":
				rolloff := 1.0 / (1.0 + currentFreq/1000.0)
				oscAmp = (math.Sin(theta) + 0.12*math.Sin(2.0*theta) + 0.55*rolloff*math.Sin(3.0*theta) + 0.25*rolloff*math.Sin(5.0*theta)) * 0.60
			case "brass", "trumpet", "horn":
				bloom := math.Min(1.0, t/0.06)
				rolloff := 1.0 / (1.0 + currentFreq/1200.0)
				oscAmp = (math.Sin(theta) +
					0.65*bloom*math.Sin(2.0*theta) +
					0.45*bloom*rolloff*math.Sin(3.0*theta) +
					0.28*bloom*rolloff*math.Sin(4.0*theta) +
					0.14*bloom*rolloff*math.Sin(5.0*theta)) * 0.50
			case "organ":
				oscAmp = (math.Sin(theta) + 0.55*math.Sin(2.0*theta) + 0.35*math.Sin(3.0*theta) + 0.25*math.Sin(4.0*theta) + 0.15*math.Sin(6.0*theta)) * 0.50
			case "piano":
				hammerDecay := math.Exp(-4.5 * t)
				oscAmp = (math.Sin(theta) +
					(0.25+0.45*hammerDecay)*math.Sin(2.0*theta) +
					0.30*hammerDecay*math.Sin(3.0*theta) +
					0.16*hammerDecay*math.Sin(4.0*theta) +
					0.08*hammerDecay*math.Sin(5.0*theta)) * 0.58
			case "harp", "guitar", "koto", "shamisen":
				pluckDecay := math.Exp(-5.5 * t)
				oscAmp = (math.Sin(theta) +
					pluckDecay*(0.48*math.Sin(2.0*theta)+0.25*math.Sin(3.0*theta)+0.12*math.Sin(4.0*theta))) * 0.68
			case "epiano":
				modIndex := inst.ModIndex
				if modIndex <= 0 {
					modIndex = 1.5
				}
				tineDecay := math.Exp(-3.5 * t)
				modSample := math.Sin(2.0 * math.Pi * modPhases[vIdx])
				oscAmp = math.Sin(theta + (0.22+0.78*tineDecay)*modIndex*modSample)
			case "bell":
				modIndex := inst.ModIndex
				if modIndex <= 0 {
					modIndex = 1.6
				}
				chimeDecay := math.Exp(-3.0 * t)
				modSample := math.Sin(2.0 * math.Pi * modPhases[vIdx])
				oscAmp = math.Sin(theta + (0.15+0.85*chimeDecay)*modIndex*modSample)
			case "sine":
				oscAmp = math.Sin(theta)
			case "square":
				duty := inst.DutyCycle
				if duty <= 0 || duty >= 1.0 {
					duty = 0.5
				}
				raw := -1.0
				if phase < duty {
					raw = 1.0
				}
				raw += polyBLEP(phase, dt)
				raw -= polyBLEP(math.Mod(phase+1.0-duty, 1.0), dt)
				dc := 2.0*duty - 1.0
				oscAmp = (raw - dc) * 0.80
			case "triangle":
				if phase < 0.5 {
					oscAmp = 4.0*phase - 1.0
				} else {
					oscAmp = 3.0 - 4.0*phase
				}
			case "sawtooth":
				oscAmp = (2.0*phase - 1.0) - polyBLEP(phase, dt)
			default:
				oscAmp = math.Sin(theta)
			}

			voiceSum += oscAmp * voiceScale
		}

		if blend > 0 {
			rawNoise := rng.Float64()*2.0 - 1.0
			filterVal += filterCoeff * (rawNoise - filterVal)
		}

		amp := (1.0-blend)*voiceSum + blend*filterVal
		env := getEnvelope(t, activeDurSec, attack, inst.Decay, inst.Sustain, inst.Release)
		eventGain := evalGainCurve(progress, gainStart, gainMid, gainEnd, ev.HasGainMid)
		finalAmp := amp * env * vol * eventGain

		if !staticPan {
			curPan := panStart + (panEnd-panStart)*progress
			leftPan = math.Cos((curPan + 1.0) * math.Pi / 4.0)
			rightPan = math.Sin((curPan + 1.0) * math.Pi / 4.0)
		}

		leftVal := int16(math.Max(-1.0, math.Min(1.0, finalAmp*leftPan)) * 32760)
		rightVal := int16(math.Max(-1.0, math.Min(1.0, finalAmp*rightPan)) * 32760)

		idx := i * BytesPerFrame
		out[idx] = byte(leftVal)
		out[idx+1] = byte(leftVal >> 8)
		out[idx+2] = byte(rightVal)
		out[idx+3] = byte(rightVal >> 8)
	}

	lpfAlpha := inst.LPF
	if ev.LPFOverride > 0 {
		lpfAlpha = ev.LPFOverride
	}
	if lpfAlpha > 0 {
		filtered := ApplyLowPassFilter(out, lpfAlpha)
		copy(out, filtered)
	}
	hpfAlpha := inst.HPF
	if ev.HPFOverride > 0 {
		hpfAlpha = ev.HPFOverride
	}
	if hpfAlpha > 0 {
		filtered := ApplyHighPassFilter(out, hpfAlpha)
		copy(out, filtered)
	}
	if inst.BitcrushBits > 0 {
		crushed := ApplyBitcrush(out, inst.BitcrushBits, inst.BitcrushDownsample)
		copy(out, crushed)
	}
}

// MixTracksPCM sums multiple stereo 16-bit PCM byte slices with a C1-continuous
// soft-knee master limiter above 85% full scale so transient peaks never hard-clip
// and never drag down the gain of the entire song.
func MixTracksPCM(tracks [][]byte) []byte {
	maxLen := 0
	for _, t := range tracks {
		aligned := len(t) &^ 3
		if aligned > maxLen {
			maxLen = aligned
		}
	}
	maxLen &= ^3
	if maxLen == 0 {
		return nil
	}

	const knee = 28000.0
	const headroom = 4767.0

	result := make([]byte, maxLen)
	for i := 0; i < maxLen; i += 2 {
		var sum int32
		for _, t := range tracks {
			alignedTrackLen := len(t) &^ 3
			if i+1 < alignedTrackLen {
				sample := int16(uint16(t[i]) | (uint16(t[i+1]) << 8))
				sum += int32(sample)
			}
		}
		absSum := float64(sum)
		sign := 1.0
		if absSum < 0 {
			absSum = -absSum
			sign = -1.0
		}
		outVal := absSum
		if absSum > knee {
			outVal = knee + headroom*math.Tanh((absSum-knee)/headroom)
		}
		val := int32(math.Round(sign * outVal))
		if val > 32767 {
			val = 32767
		} else if val < -32768 {
			val = -32768
		}
		result[i] = byte(val)
		result[i+1] = byte(val >> 8)
	}
	return result
}

// SliceLoopPCM extracts a 4-byte aligned stereo PCM loop region between startSec and endSec.
func SliceLoopPCM(pcm []byte, startSec, endSec float64) ([]byte, error) {
	alignedTotal := len(pcm) &^ 3
	if alignedTotal == 0 {
		return nil, fmt.Errorf("slice loop PCM: input buffer is empty or smaller than 4 bytes (%d bytes)", len(pcm))
	}
	if startSec < 0 || endSec <= startSec {
		return nil, fmt.Errorf("slice loop PCM: invalid time range [%.4fs, %.4fs]", startSec, endSec)
	}

	startByte := int(startSec*BytesPerSecond) &^ 3
	endByte := int(endSec*BytesPerSecond) &^ 3
	if endByte > alignedTotal {
		endByte = alignedTotal
	}
	sliceLen := (endByte - startByte) &^ 3
	if sliceLen <= 0 {
		return nil, fmt.Errorf("slice loop PCM: computed 4-byte aligned slice length is %d bytes for range [%.4fs, %.4fs]", sliceLen, startSec, endSec)
	}

	reader := bytes.NewReader(pcm[:alignedTotal])
	if _, err := reader.Seek(int64(startByte)&^3, io.SeekStart); err != nil {
		return nil, fmt.Errorf("slice loop PCM seek failed: %w", err)
	}
	out := make([]byte, sliceLen)
	if _, err := io.ReadFull(reader, out); err != nil {
		return nil, fmt.Errorf("slice loop PCM read failed: %w", err)
	}
	return out, nil
}

// ApplyLowPassFilter applies a single-pole IIR low-pass filter (alpha in (0.0, 1.0]) to a 16-bit stereo PCM buffer.
func ApplyLowPassFilter(pcm []byte, alpha float64) []byte {
	alignedLen := len(pcm) &^ 3
	if alignedLen == 0 {
		return nil
	}
	if alpha <= 0 {
		alpha = 0.01
	} else if alpha > 1.0 {
		alpha = 1.0
	}

	out := make([]byte, alignedLen)
	var prevL, prevR float64
	for i := 0; i < alignedLen; i += 4 {
		inL := float64(int16(uint16(pcm[i]) | (uint16(pcm[i+1]) << 8)))
		inR := float64(int16(uint16(pcm[i+2]) | (uint16(pcm[i+3]) << 8)))

		prevL += alpha * (inL - prevL)
		prevR += alpha * (inR - prevR)

		outL := int16(math.Max(-32768, math.Min(32767, prevL)))
		outR := int16(math.Max(-32768, math.Min(32767, prevR)))

		out[i] = byte(outL)
		out[i+1] = byte(outL >> 8)
		out[i+2] = byte(outR)
		out[i+3] = byte(outR >> 8)
	}
	return out
}

// ApplyHighPassFilter applies a single-pole IIR high-pass filter (alpha in (0.0, 1.0)) to a 16-bit stereo PCM buffer.
func ApplyHighPassFilter(pcm []byte, alpha float64) []byte {
	alignedLen := len(pcm) &^ 3
	if alignedLen == 0 {
		return nil
	}
	if alpha <= 0 {
		alpha = 0.01
	} else if alpha >= 1.0 {
		alpha = 0.999
	}

	out := make([]byte, alignedLen)
	var prevInL, prevInR, prevOutL, prevOutR float64
	for i := 0; i < alignedLen; i += 4 {
		inL := float64(int16(uint16(pcm[i]) | (uint16(pcm[i+1]) << 8)))
		inR := float64(int16(uint16(pcm[i+2]) | (uint16(pcm[i+3]) << 8)))

		prevOutL = alpha * (prevOutL + inL - prevInL)
		prevOutR = alpha * (prevOutR + inR - prevInR)
		prevInL = inL
		prevInR = inR

		outL := int16(math.Max(-32768, math.Min(32767, prevOutL)))
		outR := int16(math.Max(-32768, math.Min(32767, prevOutR)))

		out[i] = byte(outL)
		out[i+1] = byte(outL >> 8)
		out[i+2] = byte(outR)
		out[i+3] = byte(outR >> 8)
	}
	return out
}

// ApplyBitcrush reduces amplitude resolution to bitDepth (1..16) and holds samples for downsample frames (>=1).
func ApplyBitcrush(pcm []byte, bitDepth int, downsample int) []byte {
	alignedLen := len(pcm) &^ 3
	if alignedLen == 0 {
		return nil
	}
	if bitDepth < 1 {
		bitDepth = 1
	} else if bitDepth > 16 {
		bitDepth = 16
	}
	if downsample < 1 {
		downsample = 1
	}

	shift := uint(16 - bitDepth)
	out := make([]byte, alignedLen)
	var holdL, holdR int16
	frameIdx := 0

	for i := 0; i < alignedLen; i += 4 {
		if frameIdx%downsample == 0 {
			inL := int16(uint16(pcm[i]) | (uint16(pcm[i+1]) << 8))
			inR := int16(uint16(pcm[i+2]) | (uint16(pcm[i+3]) << 8))
			if shift > 0 {
				holdL = (inL >> shift) << shift
				holdR = (inR >> shift) << shift
			} else {
				holdL = inL
				holdR = inR
			}
		}
		out[i] = byte(holdL)
		out[i+1] = byte(holdL >> 8)
		out[i+2] = byte(holdR)
		out[i+3] = byte(holdR >> 8)
		frameIdx++
	}
	return out
}

func getEnvelope(t, duration, attack, decay, sustain, release float64) float64 {
	if t < 0 || t > duration || duration <= 0 {
		return 0.0
	}
	if attack+decay+release > duration {
		attack = math.Min(attack, duration*0.25)
		release = math.Min(release, (duration-attack)*0.30)
		decay = math.Max(0, duration-attack-release)
	}
	if t < attack {
		if attack > 0 {
			return t / attack
		}
		return 1.0
	}
	if t < attack+decay {
		if decay > 0 {
			progress := (t - attack) / decay
			return 1.0 - (1.0-sustain)*progress
		}
		return sustain
	}
	if t < duration-release {
		return sustain
	}
	timeInRelease := t - (duration - release)
	if release > 0 {
		progress := timeInRelease / release
		if progress > 1.0 {
			progress = 1.0
		}
		return sustain * (1.0 - progress)
	}
	return 0.0
}

// ============================================================================
// 4. SOUND SYSTEM DRIVER (BGM & RATE-LIMITED SFX PLAYBACK ENGINE)
// ============================================================================

// SoundSystem manages Ebitengine BGM playback and rate-limited polyphonic SFX triggers.
type SoundSystem struct {
	context     *audio.Context
	musicPlayer *audio.Player
	mu          sync.Mutex
	lastSFX     map[string]time.Time
}

// NewSoundSystem initializes the sound system driver.
func NewSoundSystem(ctx *audio.Context) *SoundSystem {
	return &SoundSystem{
		context: ctx,
		lastSFX: make(map[string]time.Time),
	}
}

// Play plays a 4-byte aligned PCM buffer once or in an infinite loop on the music channel.
func (s *SoundSystem) Play(pcm []byte, loop bool) error {
	if s.context == nil {
		return fmt.Errorf("sound system: audio.Context is nil")
	}
	alignedLen := len(pcm) &^ 3
	if alignedLen == 0 {
		return fmt.Errorf("sound system: PCM buffer is empty or smaller than 4-byte stereo frame (%d bytes)", len(pcm))
	}
	pcm = pcm[:alignedLen]
	s.Stop()

	if loop {
		loopLength := int64(alignedLen) &^ 3
		loopStream := audio.NewInfiniteLoop(bytes.NewReader(pcm), loopLength)
		player, err := s.context.NewPlayer(loopStream)
		if err != nil {
			return err
		}
		s.musicPlayer = player
		player.Play()
	} else {
		player := s.context.NewPlayerFromBytes(pcm)
		s.musicPlayer = player
		player.Play()
	}
	return nil
}

// PlaySFX plays a one-shot sound effect concurrently without interrupting BGM,
// enforcing an optional per-cue cooldown to prevent audio channel choking.
func (s *SoundSystem) PlaySFX(cueName string, pcm []byte, cooldown time.Duration) error {
	if s.context == nil {
		return fmt.Errorf("sound system: audio.Context is nil")
	}
	alignedLen := len(pcm) &^ 3
	if alignedLen == 0 {
		return fmt.Errorf("sound system: SFX PCM buffer %q is empty or smaller than 4-byte stereo frame (%d bytes)", cueName, len(pcm))
	}

	if cooldown > 0 && cueName != "" {
		s.mu.Lock()
		now := time.Now()
		if last, ok := s.lastSFX[cueName]; ok && now.Sub(last) < cooldown {
			s.mu.Unlock()
			return nil
		}
		s.lastSFX[cueName] = now
		s.mu.Unlock()
	}

	player := s.context.NewPlayerFromBytes(pcm[:alignedLen])
	player.Play()
	return nil
}

// PlayDSL compiles a DSL script and plays it (one-shot or loop).
func (s *SoundSystem) PlayDSL(dslText string, loop bool) error {
	pcm, err := CompileDSL(dslText)
	if err != nil {
		return err
	}
	return s.Play(pcm, loop)
}

// SeekBytes seeks the active player to a 4-byte aligned byte offset in the 44.1kHz stereo PCM stream.
func (s *SoundSystem) SeekBytes(offsetBytes int64) error {
	if s.musicPlayer == nil {
		return fmt.Errorf("sound system: no active player to seek")
	}
	alignedOffset := offsetBytes &^ 3
	if alignedOffset < 0 {
		return fmt.Errorf("sound system: negative seek offset (%d)", alignedOffset)
	}
	targetDuration := time.Duration(alignedOffset) * time.Second / BytesPerSecond
	return s.musicPlayer.Seek(targetDuration)
}

// Stop stops any currently playing music player.
func (s *SoundSystem) Stop() {
	if s.musicPlayer != nil && s.musicPlayer.IsPlaying() {
		s.musicPlayer.Pause()
	}
}

// ============================================================================
// 5. WAV FILE EXPORTER
// ============================================================================

// ExportWAV writes a 4-byte aligned 16-bit 44100Hz stereo PCM buffer to a .wav file.
func ExportWAV(filename string, pcm []byte) (retErr error) {
	alignedLen := len(pcm) &^ 3
	if alignedLen == 0 {
		return fmt.Errorf("export WAV: PCM buffer is empty or smaller than 4-byte stereo frame (%d bytes)", len(pcm))
	}
	pcm = pcm[:alignedLen]

	f, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer func() {
		if closeErr := f.Close(); closeErr != nil && retErr == nil {
			retErr = closeErr
		}
	}()

	const bitsPerSample = 16
	const byteRate = SampleRate * NumChannels * (bitsPerSample / 8)
	const blockAlign = NumChannels * (bitsPerSample / 8)

	dataSize := uint32(alignedLen)
	chunkSize := 36 + dataSize

	if _, err := f.WriteString("RIFF"); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, chunkSize); err != nil {
		return err
	}
	if _, err := f.WriteString("WAVE"); err != nil {
		return err
	}

	if _, err := f.WriteString("fmt "); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, uint32(16)); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, uint16(1)); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, uint16(NumChannels)); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, uint32(SampleRate)); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, uint32(byteRate)); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, uint16(blockAlign)); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, uint16(bitsPerSample)); err != nil {
		return err
	}

	if _, err := f.WriteString("data"); err != nil {
		return err
	}
	if err := binary.Write(f, binary.LittleEndian, dataSize); err != nil {
		return err
	}
	_, err = f.Write(pcm)
	return err
}

// ============================================================================
// 8. MUSIC THEORY, CONSONANCE & PRODUCTION QUALITY VALIDATOR
// ============================================================================

var midiNoteNames = [12]string{"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"}

func freqToNearestMIDI(freq float64) int {
	if freq <= 0 {
		return -1
	}
	return int(math.Round(69.0 + 12.0*math.Log2(freq/440.0)))
}

func midiToPitchName(midi int) string {
	if midi < 0 {
		return "none"
	}
	pc := ((midi % 12) + 12) % 12
	oct := (midi / 12) - 1
	return fmt.Sprintf("%s%d", midiNoteNames[pc], oct)
}

// ValidateProductionBGM enforces minimum production standards (e.g. >= 8 channels, >= 30s duration)
// in addition to full music-theory and harmonic consonance validation via ValidateScoreTheory.
func ValidateProductionBGM(score *Score, minChannels int, minDurationSec float64) error {
	if score == nil {
		return fmt.Errorf("validate BGM: score is nil")
	}
	if minChannels <= 0 {
		minChannels = 8
	}
	if minDurationSec <= 0 {
		minDurationSec = 30.0
	}
	if len(score.Tracks) < minChannels {
		return fmt.Errorf("validate BGM %q: track has %d channels, minimum required is %d channels", score.Title, len(score.Tracks), minChannels)
	}
	var totalSec float64
	if len(score.Tracks) > 0 {
		for _, ev := range score.Tracks[0].Events {
			totalSec += ev.DurationSec
		}
	}
	if totalSec+1e-4 < minDurationSec {
		return fmt.Errorf("validate BGM %q: duration is %.2fs, minimum required is %.2fs", score.Title, totalSec, minDurationSec)
	}
	return ValidateScoreTheory(score)
}

// ValidateScoreTheory audits a parsed Score for music-theory, voice-leading, and synthesis hygiene:
//  1. Zero sample-frame drift across all polyphonic tracks.
//  2. No wide pitch-sweep sirens (`->` > 2.5 semitones over >= 0.25s) on melodic tracks.
//  3. No continuous static noise (`noise=`) blended into sustained melodic notes (>= 0.30s).
//  4. Vertical harmonic consonance across simultaneous pitched channels (no sustained minor-2nd/flat-9th
//     collisions or simultaneous G# vs G-natural / F-natural cross-channel modal clashes).
func ValidateScoreTheory(score *Score) error {
	if score == nil || len(score.Tracks) == 0 {
		return fmt.Errorf("validate theory: score has no tracks")
	}

	var expectedBytes int
	var totalSec float64

	for idx, tr := range score.Tracks {
		var trSec float64
		for _, ev := range tr.Events {
			trSec += ev.DurationSec
			if ev.IsRest || len(ev.Pitches) == 0 || ev.Inst.WaveType == "noise" || IsPercussionInstrument(ev.Inst) {
				continue
			}

			for _, sw := range ev.Pitches {
				// 1. Check for melodic pitch-sweep sirens (exclude low-frequency drum pitch drops)
				if sw.StartFreq != sw.EndFreq && sw.StartFreq > 0 && sw.EndFreq > 0 {
					isDrumSweep := (sw.StartFreq <= 260.0 && sw.EndFreq < sw.StartFreq && sw.EndFreq <= 110.0) ||
						(ev.Inst.DefaultStartFreq > ev.Inst.DefaultEndFreq && ev.Inst.DefaultStartFreq <= 300.0)
					if !isDrumSweep {
						semi := math.Abs(12.0 * math.Log2(sw.EndFreq/sw.StartFreq))
						if semi > 2.5 && ev.DurationSec >= 0.25 {
							return fmt.Errorf(
								"music theory violation on track %q: wide pitch sweep (%.1f Hz -> %.1f Hz, %.1f semitones over %.2fs) creates microtonal siren dissonance; use discrete diatonic grace notes instead",
								tr.Name, sw.StartFreq, sw.EndFreq, semi, ev.DurationSec,
							)
						}
					}
				}

				// 2. Check for continuous noise blended into sustained melodic notes
				if sw.StartFreq == sw.EndFreq && ev.DurationSec >= 0.30 && ev.Inst.NoiseBlend > 0.005 {
					return fmt.Errorf(
						"synthesis hygiene violation on track %q: instrument %q blends continuous noise (%.2f) into sustained melodic notes (%.2fs), creating static hiss",
						tr.Name, ev.Inst.Name, ev.Inst.NoiseBlend, ev.DurationSec,
					)
				}
			}
		}

		trBytes := int(math.Round(trSec*SampleRate)) * BytesPerFrame &^ 3
		if idx == 0 {
			expectedBytes = trBytes
			totalSec = trSec
		} else if trBytes != expectedBytes {
			return fmt.Errorf("timing drift on track %q: got %d PCM bytes (%.2fs), want %d PCM bytes (%.2fs)",
				tr.Name, trBytes, trSec, expectedBytes, totalSec)
		}
	}

	// 3. Audit vertical harmonic consonance across pitched tracks on a beat-subdivision grid
	type activePitch struct {
		trackName string
		midi      int
		durSec    float64
	}

	stepSec := 0.25
	if score.BPM > 0 {
		stepSec = (60.0 / score.BPM) / 2.0 // 8th-note grid
	}

	for t := 0.05; t < totalSec-0.05; t += stepSec {
		var sounding []activePitch
		for _, tr := range score.Tracks {
			cursor := 0.0
			for _, ev := range tr.Events {
				next := cursor + ev.DurationSec
				if t >= cursor && t < next {
					if !ev.IsRest && ev.Inst.WaveType != "noise" && !IsPercussionInstrument(ev.Inst) {
						for _, sw := range ev.Pitches {
							// Only audit stationary pitched notes above sub-percussion range
							if sw.StartFreq == sw.EndFreq && sw.StartFreq >= 50.0 {
								m := freqToNearestMIDI(sw.StartFreq)
								if m >= 24 {
									sounding = append(sounding, activePitch{
										trackName: tr.Name,
										midi:      m,
										durSec:    ev.DurationSec,
									})
								}
							}
						}
					}
					break
				}
				cursor = next
			}
		}

		for i := 0; i < len(sounding); i++ {
			for j := i + 1; j < len(sounding); j++ {
				a := sounding[i]
				b := sounding[j]
				if a.trackName == b.trackName {
					continue
				}
				lower, upper := a, b
				if lower.midi > upper.midi {
					lower, upper = b, a
				}
				diff := upper.midi - lower.midi
				pcLower := ((lower.midi % 12) + 12) % 12
				pcUpper := ((upper.midi % 12) + 12) % 12

				// Sustained close minor-2nd clash (1 semitone apart)
				if diff == 1 && a.durSec >= 0.25 && b.durSec >= 0.25 {
					return fmt.Errorf(
						"harmonic dissonance at t=%.2fs: track %q (%s) and track %q (%s) clash by a close minor 2nd (1 semitone)",
						t, lower.trackName, midiToPitchName(lower.midi), upper.trackName, midiToPitchName(upper.midi),
					)
				}

				// Sustained flat-9th (minor 9th) clash (e.g. E3 against F4 or A3 against Bb4)
				if diff >= 13 && (diff%12) == 1 && a.durSec >= 0.30 && b.durSec >= 0.30 {
					return fmt.Errorf(
						"harmonic dissonance at t=%.2fs: track %q (%s) and track %q (%s) form a harsh minor-9th (b9) clash",
						t, lower.trackName, midiToPitchName(lower.midi), upper.trackName, midiToPitchName(upper.midi),
					)
				}

				// Cross-channel E7 (G#) vs Em/G (G natural) modal collision
				if (pcLower == 7 && pcUpper == 8) || (pcLower == 8 && pcUpper == 7) {
					return fmt.Errorf(
						"modal harmonic clash at t=%.2fs: track %q (%s) and track %q (%s) simultaneously sound G natural and G#",
						t, a.trackName, midiToPitchName(a.midi), b.trackName, midiToPitchName(b.midi),
					)
				}
			}
		}
	}

	return nil
}
