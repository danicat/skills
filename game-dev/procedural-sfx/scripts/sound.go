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
	"errors"
	"fmt"
	"io"
	"math"
	"math/rand/v2"
	"os"
	"sort"
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
	Preset             string  // Built-in archetype preset name (e.g. "arcade_laser")
	WaveType           string  // "sine", "square", "triangle", "sawtooth", "noise", "psg_noise", "fm"
	Volume             float64 // 0.0 to 1.0
	Muted              bool    // True when explicitly set to vol=0.0
	Pan                float64 // -1.0 (left) to +1.0 (right)
	DutyStart          float64 // Pulse width at start (0.01 to 0.99)
	DutyEnd            float64 // Pulse width at end (0.01 to 0.99)
	DutyCycle          float64 // Fallback single duty cycle
	Attack             float64 // ADSR Attack in seconds
	Decay              float64 // ADSR Decay in seconds
	Sustain            float64 // ADSR Sustain amplitude (0.0 to 1.0)
	Release            float64 // ADSR Release in seconds
	VibratoFreq        float64 // Vibrato LFO rate in Hz
	VibratoDepth       float64 // Vibrato LFO depth in Hz
	ModRatio           float64 // FM modulator frequency multiplier relative to carrier
	ModFreq            float64 // Fixed FM modulator frequency in Hz (if ModRatio == 0)
	ModIndexStart      float64 // FM modulation index at start
	ModIndexEnd        float64 // FM modulation index at end
	ModIndex           float64 // Fallback FM modulation index
	NoiseFilter        float64 // Single-pole LPF coefficient for noise (0.0 to 1.0]
	NoiseBlend         float64 // Blend between oscillator (0.0) and filtered noise (1.0)
	NoiseType          string  // "white" or "psg" (periodic LFSR)
	DefaultStartFreq   float64 // Default starting frequency in Hz (for drum/SFX triggers)
	DefaultEndFreq     float64 // Default ending frequency in Hz (for frequency sweeps)
	PitchCurve         string  // "exp" (default), "lin", "hyper"
	LPFStart           float64 // Low-pass filter cutoff in Hz (or alpha) at start
	LPFEnd             float64 // Low-pass filter cutoff in Hz (or alpha) at end
	LPF                float64 // Optional per-instrument low-pass filter alpha or Hz
	HPFStart           float64 // High-pass filter cutoff in Hz (or alpha) at start
	HPFEnd             float64 // High-pass filter cutoff in Hz (or alpha) at end
	HPF                float64 // Optional per-instrument high-pass filter alpha or Hz
	ResonanceQ         float64 // SVF filter Q factor (0.5 to 12.0, default 0.707)
	BitcrushBits       int     // Optional per-instrument bit depth (1..16)
	BitcrushDownsample int     // Optional per-instrument downsample factor (>=1)
}

// Built-in curated SFX archetype presets for games
var sfxPresets = map[string]Instrument{
	"arcade_laser": {
		Preset: "arcade_laser", WaveType: "square", Volume: 0.32,
		DutyStart: 0.50, DutyEnd: 0.15, DutyCycle: 0.50,
		Attack: 0.002, Decay: 0.05, Sustain: 0.10, Release: 0.04,
		DefaultStartFreq: 950.0, DefaultEndFreq: 110.0, PitchCurve: "exp",
	},
	"plasma_gun": {
		Preset: "plasma_gun", WaveType: "sawtooth", Volume: 0.30,
		Attack: 0.003, Decay: 0.07, Sustain: 0.12, Release: 0.05,
		DefaultStartFreq: 1200.0, DefaultEndFreq: 180.0, PitchCurve: "exp",
		LPFStart: 3500.0, LPFEnd: 400.0, ResonanceQ: 2.2,
	},
	"explosion_arcade": {
		Preset: "explosion_arcade", WaveType: "psg_noise", Volume: 0.38,
		Attack: 0.004, Decay: 0.25, Sustain: 0.18, Release: 0.35,
		DefaultStartFreq: 180.0, DefaultEndFreq: 25.0, PitchCurve: "exp",
		LPFStart: 1200.0, LPFEnd: 150.0, ResonanceQ: 1.8,
		NoiseFilter: 0.35, NoiseBlend: 1.0,
	},
	"explosion_deep": {
		Preset: "explosion_deep", WaveType: "sine", Volume: 0.42,
		Attack: 0.004, Decay: 0.22, Sustain: 0.20, Release: 0.45,
		DefaultStartFreq: 120.0, DefaultEndFreq: 24.0, PitchCurve: "exp",
		NoiseFilter: 0.15, NoiseBlend: 0.45,
	},
	"jump_arcade": {
		Preset: "jump_arcade", WaveType: "square", Volume: 0.26,
		DutyStart: 0.50, DutyEnd: 0.50, DutyCycle: 0.50,
		Attack: 0.003, Decay: 0.04, Sustain: 0.55, Release: 0.05,
		DefaultStartFreq: 160.0, DefaultEndFreq: 620.0, PitchCurve: "exp",
	},
	"jump_spring": {
		Preset: "jump_spring", WaveType: "triangle", Volume: 0.28,
		Attack: 0.004, Decay: 0.06, Sustain: 0.45, Release: 0.06,
		DefaultStartFreq: 120.0, DefaultEndFreq: 480.0, PitchCurve: "exp",
		VibratoFreq: 18.0, VibratoDepth: 25.0,
	},
	"coin_pickup": {
		Preset: "coin_pickup", WaveType: "square", Volume: 0.22,
		DutyStart: 0.50, DutyEnd: 0.50, DutyCycle: 0.50,
		Attack: 0.002, Decay: 0.025, Sustain: 0.35, Release: 0.035,
		DefaultStartFreq: 987.77, DefaultEndFreq: 1318.51,
	},
	"gem_shimmer": {
		Preset: "gem_shimmer", WaveType: "fm", Volume: 0.20,
		ModRatio: 2.76, ModIndexStart: 2.2, ModIndexEnd: 0.2, ModIndex: 2.2,
		Attack: 0.001, Decay: 0.06, Sustain: 0.15, Release: 0.12,
		DefaultStartFreq: 1567.98, DefaultEndFreq: 1567.98,
	},
	"sword_clash": {
		Preset: "sword_clash", WaveType: "fm", Volume: 0.32,
		ModFreq: 620.0, ModIndexStart: 5.5, ModIndexEnd: 0.5, ModIndex: 5.5,
		Attack: 0.001, Decay: 0.04, Sustain: 0.08, Release: 0.10,
		DefaultStartFreq: 520.0, DefaultEndFreq: 210.0, PitchCurve: "exp",
		NoiseBlend: 0.25, NoiseFilter: 0.60,
	},
	"shield_deflect": {
		Preset: "shield_deflect", WaveType: "fm", Volume: 0.30,
		ModRatio: 3.1415, ModIndexStart: 4.0, ModIndexEnd: 0.2, ModIndex: 4.0,
		Attack: 0.001, Decay: 0.035, Sustain: 0.06, Release: 0.15,
		DefaultStartFreq: 880.0, DefaultEndFreq: 440.0, PitchCurve: "exp",
	},
	"hit_punch": {
		Preset: "hit_punch", WaveType: "triangle", Volume: 0.35,
		Attack: 0.002, Decay: 0.035, Sustain: 0.10, Release: 0.04,
		DefaultStartFreq: 180.0, DefaultEndFreq: 45.0, PitchCurve: "hyper",
		NoiseBlend: 0.30, NoiseFilter: 0.45,
	},
	"hit_damage": {
		Preset: "hit_damage", WaveType: "sawtooth", Volume: 0.32,
		Attack: 0.003, Decay: 0.05, Sustain: 0.15, Release: 0.06,
		DefaultStartFreq: 220.0, DefaultEndFreq: 65.0, PitchCurve: "exp",
		NoiseBlend: 0.38, NoiseFilter: 0.30,
	},
	"powerup_fanfare": {
		Preset: "powerup_fanfare", WaveType: "square", Volume: 0.24,
		DutyStart: 0.35, DutyEnd: 0.35, DutyCycle: 0.35,
		Attack: 0.004, Decay: 0.035, Sustain: 0.65, Release: 0.06,
		DefaultStartFreq: 523.25, DefaultEndFreq: 1046.50,
	},
	"ui_select": {
		Preset: "ui_select", WaveType: "sine", Volume: 0.18,
		Attack: 0.001, Decay: 0.012, Sustain: 0.0, Release: 0.008,
		DefaultStartFreq: 880.0, DefaultEndFreq: 1100.0, PitchCurve: "lin",
	},
	"ui_confirm": {
		Preset: "ui_confirm", WaveType: "square", Volume: 0.20,
		DutyStart: 0.50, DutyEnd: 0.50, DutyCycle: 0.50,
		Attack: 0.002, Decay: 0.025, Sustain: 0.25, Release: 0.03,
		DefaultStartFreq: 659.25, DefaultEndFreq: 1318.51,
	},
	"ui_error": {
		Preset: "ui_error", WaveType: "sawtooth", Volume: 0.24,
		Attack: 0.004, Decay: 0.045, Sustain: 0.40, Release: 0.05,
		DefaultStartFreq: 150.0, DefaultEndFreq: 110.0, PitchCurve: "lin",
	},
	"footstep_stone": {
		Preset: "footstep_stone", WaveType: "noise", Volume: 0.28,
		Attack: 0.002, Decay: 0.03, Sustain: 0.0, Release: 0.015,
		NoiseFilter: 0.25, NoiseBlend: 1.0,
	},
	"engine_thruster": {
		Preset: "engine_thruster", WaveType: "psg_noise", Volume: 0.30,
		Attack: 0.03, Decay: 0.08, Sustain: 0.80, Release: 0.10,
		DefaultStartFreq: 110.0, DefaultEndFreq: 110.0,
		NoiseFilter: 0.35, NoiseBlend: 1.0,
	},
}

// GetSFXPreset returns a copy of a built-in archetype preset patch.
func GetSFXPreset(name string) (Instrument, bool) {
	lower := strings.ToLower(strings.TrimSpace(name))
	p, ok := sfxPresets[lower]
	if !ok {
		return Instrument{}, false
	}
	return p, true
}

// ListSFXPresets returns sorted names of all built-in SFX archetype presets.
func ListSFXPresets() []string {
	names := make([]string, 0, len(sfxPresets))
	for k := range sfxPresets {
		names = append(names, k)
	}
	sort.Strings(names)
	return names
}

// PitchSweep represents a stationary note (StartFreq == EndFreq) or a continuous pitch glide.
type PitchSweep struct {
	StartFreq float64
	EndFreq   float64
}

// NoteEvent represents a single resolved musical note, chord, sweep, or rest on a timeline.
type NoteEvent struct {
	IsRest      bool
	Inst        Instrument
	Pitches     []PitchSweep
	DurationSec float64
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
	TimeSigNum               int
	TimeSigDen               int
	Instruments              map[string]Instrument
	Patterns                 map[string][]dslNode
	Tracks                   []Track
	GlobalLPF                float64
	GlobalHPF                float64
	GlobalBitcrushBits       int
	GlobalBitcrushDownsample int
	HasLoopSlice             bool
	LoopStartSec             float64
	LoopEndSec               float64
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
	tokRepeat
	tokTranspose
)

type dslToken struct {
	kind   dslTokenKind
	text   string
	number int
}

type dslNode struct {
	isGroup   bool
	atom      string
	children  []dslNode
	repeat    int
	transpose int
}

// LoadDSLFile reads and parses a `.music` or `.sfx` DSL file from disk.
func LoadDSLFile(filepath string) (*Score, error) {
	data, err := os.ReadFile(filepath)
	if err != nil {
		return nil, fmt.Errorf("load DSL file %q: %w", filepath, err)
	}
	return ParseDSL(string(data))
}

// CompileDSL parses a DSL script, validates score structures, and synthesizes it into a 4-byte aligned 16-bit 44.1kHz stereo PCM buffer.
func CompileDSL(dslText string) ([]byte, error) {
	score, err := ParseDSL(dslText)
	if err != nil {
		return nil, err
	}
	if err := ValidateScore(score); err != nil {
		return nil, err
	}
	return SynthesizeScore(score)
}

// ParseDSL parses a procedural music or SFX DSL script into a validated Score AST.
func ParseDSL(dslText string) (*Score, error) {
	score := &Score{
		Title:       "Untitled",
		Type:        "song",
		BPM:         120.0,
		TimeSigNum:  4,
		TimeSigDen:  4,
		Instruments: make(map[string]Instrument),
		Patterns:    make(map[string][]dslNode),
	}

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
		if strings.HasPrefix(lowerWord, "seq:") {
			remainder = strings.TrimSpace(firstWord[3:] + " " + remainder)
			lowerWord = "seq"
		}

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
			if prev.keyword == "pattern" || prev.keyword == "track" || prev.keyword == "seq" {
				prev.rest += " " + trimmed
			} else {
				return nil, fmt.Errorf("line %d: unknown directive %q (or unexpected continuation after %q)", lineNum, firstWord, prev.keyword)
			}
		}
	}

	var stepEvents []NoteEvent

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

		case "bpm":
			bpm, err := strconv.ParseFloat(st.rest, 64)
			if err != nil || bpm <= 0 || bpm > 1000 {
				return nil, fmt.Errorf("line %d: invalid bpm %q (must be a number between 1 and 1000)", st.lineNum, st.rest)
			}
			score.BPM = bpm

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
			if _, exists := score.Instruments[instName]; exists {
				return nil, fmt.Errorf("line %d: duplicate instrument definition %q", st.lineNum, instName)
			}
			inst, _, err := parseInstrumentOrStepAttrs(instName, attrText, score.BPM, false)
			if err != nil {
				return nil, fmt.Errorf("line %d (inst %s): %w", st.lineNum, instName, err)
			}
			score.Instruments[instName] = inst

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
			if _, isInst := score.Instruments[patName]; isInst {
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
			events, err := score.expandNodesToEvents(nodes, defaultInst, 0, make(map[string]bool))
			if err != nil {
				return nil, fmt.Errorf("line %d (track %s): %w", st.lineNum, trackName, err)
			}
			score.appendTrackEvents(trackName, defaultInst, events)

		case "seq":
			colonIdx := strings.IndexByte(st.rest, ':')
			var defaultInst, bodyText string
			if colonIdx >= 0 {
				header := strings.TrimSpace(st.rest[:colonIdx])
				bodyText = strings.TrimSpace(st.rest[colonIdx+1:])
				if header != "" {
					defaultInst = header
					if _, ok := score.Instruments[defaultInst]; !ok {
						return nil, fmt.Errorf("line %d: seq references unknown instrument %q", st.lineNum, defaultInst)
					}
				}
			} else {
				bodyText = strings.TrimSpace(st.rest)
			}
			if bodyText == "" {
				return nil, fmt.Errorf("line %d: 'seq' has an empty body", st.lineNum)
			}
			nodes, err := parsePatternNodes(bodyText)
			if err != nil {
				return nil, fmt.Errorf("line %d (seq): %w", st.lineNum, err)
			}
			events, err := score.expandNodesToEvents(nodes, defaultInst, 0, make(map[string]bool))
			if err != nil {
				return nil, fmt.Errorf("line %d (seq): %w", st.lineNum, err)
			}
			score.appendTrackEvents("seq", defaultInst, events)

		case "step":
			inst, durSec, err := parseInstrumentOrStepAttrs("_step", st.rest, score.BPM, true)
			if err != nil {
				return nil, fmt.Errorf("line %d (step): %w", st.lineNum, err)
			}
			startFreq := inst.DefaultStartFreq
			endFreq := inst.DefaultEndFreq
			if startFreq <= 0 && inst.WaveType != "noise" {
				return nil, fmt.Errorf("line %d (step): non-noise step requires 'freq=<pitchOrHz>' or 'freq=<start>-><end>'", st.lineNum)
			}
			if startFreq <= 0 {
				startFreq = 440.0
				endFreq = 440.0
			}
			stepEvents = append(stepEvents, NoteEvent{
				IsRest:      false,
				Inst:        inst,
				Pitches:     []PitchSweep{{StartFreq: startFreq, EndFreq: endFreq}},
				DurationSec: durSec,
			})
		}
	}

	if len(stepEvents) > 0 {
		score.appendTrackEvents("_steps", "", stepEvents)
	}

	if len(score.Tracks) == 0 {
		return nil, fmt.Errorf("parse DSL: score %q contains no tracks, sequences, or steps", score.Title)
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
	case "title", "type", "bpm", "time", "filter", "bitcrush", "loop", "inst", "patch", "pattern", "track", "seq", "step":
		return true
	default:
		return false
	}
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

func parseInstrumentOrStepAttrs(name, attrText string, bpm float64, isStep bool) (Instrument, float64, error) {
	inst := Instrument{
		Name:        name,
		Volume:      0.2,
		Pan:         0.0,
		DutyStart:   0.5,
		DutyEnd:     0.5,
		DutyCycle:   0.5,
		Attack:      0.005,
		Decay:       0.04,
		Sustain:     0.7,
		Release:     0.03,
		NoiseFilter: 1.0,
		PitchCurve:  "exp",
		ResonanceQ:  0.7071,
	}
	var durSec float64
	hasWave := false
	hasDur := false
	hasVol := false
	explicitVol := 0.0
	hasExplicitNoiseBlend := false

	fields := strings.Fields(attrText)
	if len(fields) == 0 {
		return inst, 0, fmt.Errorf("missing attributes")
	}

	// First pass: scan for preset=<name> or template=<name>
	for _, field := range fields {
		eq := strings.IndexByte(field, '=')
		if eq <= 0 || eq == len(field)-1 {
			continue
		}
		key := strings.ToLower(field[:eq])
		val := field[eq+1:]
		if key == "preset" || key == "template" || key == "archetype" {
			p, ok := GetSFXPreset(val)
			if !ok {
				return inst, 0, fmt.Errorf("unknown preset %q (available: %s)", val, strings.Join(ListSFXPresets(), ", "))
			}
			origName := inst.Name
			inst = p
			inst.Name = origName
			hasWave = true
			break
		}
	}

	for _, field := range fields {
		eq := strings.IndexByte(field, '=')
		if eq <= 0 || eq == len(field)-1 {
			return inst, 0, fmt.Errorf("malformed attribute %q (expected key=value)", field)
		}
		key := strings.ToLower(field[:eq])
		val := field[eq+1:]

		switch key {
		case "preset", "template", "archetype":
			// Already processed in first pass
			continue

		case "wave", "wave_type":
			if p, ok := GetSFXPreset(val); ok {
				origName := inst.Name
				inst = p
				inst.Name = origName
				if hasVol {
					inst.Volume = explicitVol
					inst.Muted = explicitVol == 0.0
				}
				hasWave = true
			} else {
				w, err := normalizeWaveType(val)
				if err != nil {
					return inst, 0, err
				}
				inst.WaveType = w
				hasWave = true
			}

		case "vol", "volume":
			v, err := strconv.ParseFloat(val, 64)
			if err != nil || v < 0.0 || v > 1.0 {
				return inst, 0, fmt.Errorf("invalid volume %q (must be 0.0 to 1.0)", val)
			}
			hasVol = true
			explicitVol = v
			inst.Volume = v
			inst.Muted = v == 0.0

		case "pan":
			p, err := strconv.ParseFloat(val, 64)
			if err != nil || p < -1.0 || p > 1.0 {
				return inst, 0, fmt.Errorf("invalid pan %q (must be -1.0 to +1.0)", val)
			}
			inst.Pan = p

		case "duty", "duty_cycle":
			if arrowIdx := strings.Index(val, "->"); arrowIdx > 0 {
				d1, err1 := strconv.ParseFloat(val[:arrowIdx], 64)
				d2, err2 := strconv.ParseFloat(val[arrowIdx+2:], 64)
				if err1 != nil || err2 != nil || d1 <= 0.0 || d1 >= 1.0 || d2 <= 0.0 || d2 >= 1.0 {
					return inst, 0, fmt.Errorf("invalid duty sweep %q (must be in (0.0, 1.0))", val)
				}
				inst.DutyStart = d1
				inst.DutyEnd = d2
				inst.DutyCycle = d1
			} else {
				d, err := strconv.ParseFloat(val, 64)
				if err != nil || d <= 0.0 || d >= 1.0 {
					return inst, 0, fmt.Errorf("invalid duty cycle %q (must be in (0.0, 1.0))", val)
				}
				inst.DutyStart = d
				inst.DutyEnd = d
				inst.DutyCycle = d
			}

		case "adsr", "env":
			parts := strings.Split(val, ",")
			if len(parts) != 4 {
				return inst, 0, fmt.Errorf("invalid adsr %q (expected attack,decay,sustain,release)", val)
			}
			a, err1 := parseSecondsOrDuration(parts[0], bpm)
			d, err2 := parseSecondsOrDuration(parts[1], bpm)
			s, err3 := strconv.ParseFloat(parts[2], 64)
			r, err4 := parseSecondsOrDuration(parts[3], bpm)
			if err1 != nil || err2 != nil || err3 != nil || err4 != nil || a < 0 || d < 0 || s < 0 || s > 1.0 || r < 0 {
				return inst, 0, fmt.Errorf("invalid adsr values %q", val)
			}
			inst.Attack = a
			inst.Decay = d
			inst.Sustain = s
			inst.Release = r

		case "attack":
			a, err := parseSecondsOrDuration(val, bpm)
			if err != nil || a < 0 {
				return inst, 0, fmt.Errorf("invalid attack %q", val)
			}
			inst.Attack = a

		case "decay":
			d, err := parseSecondsOrDuration(val, bpm)
			if err != nil || d < 0 {
				return inst, 0, fmt.Errorf("invalid decay %q", val)
			}
			inst.Decay = d

		case "sustain":
			s, err := strconv.ParseFloat(val, 64)
			if err != nil || s < 0 || s > 1.0 {
				return inst, 0, fmt.Errorf("invalid sustain %q (must be 0.0 to 1.0)", val)
			}
			inst.Sustain = s

		case "release":
			r, err := parseSecondsOrDuration(val, bpm)
			if err != nil || r < 0 {
				return inst, 0, fmt.Errorf("invalid release %q", val)
			}
			inst.Release = r

		case "curve", "pitch_curve":
			c := strings.ToLower(val)
			if c != "exp" && c != "lin" && c != "hyper" {
				return inst, 0, fmt.Errorf("invalid pitch curve %q (expected 'exp', 'lin', or 'hyper')", val)
			}
			inst.PitchCurve = c

		case "vib", "vibrato":
			parts := strings.Split(val, ",")
			if len(parts) != 2 {
				return inst, 0, fmt.Errorf("invalid vibrato %q (expected rateHz,depthHz)", val)
			}
			vf, err1 := parseHzNumber(parts[0])
			vd, err2 := parseHzNumber(parts[1])
			if err1 != nil || err2 != nil || vf < 0 || vd < 0 {
				return inst, 0, fmt.Errorf("invalid vibrato parameters %q", val)
			}
			inst.VibratoFreq = vf
			inst.VibratoDepth = vd

		case "freq", "sweep", "pitch":
			sweep, err := parsePitchOrSweep(val)
			if err != nil {
				return inst, 0, fmt.Errorf("invalid freq/sweep %q: %w", val, err)
			}
			inst.DefaultStartFreq = sweep.StartFreq
			inst.DefaultEndFreq = sweep.EndFreq

		case "dur", "duration":
			d, err := ParseDuration(val, bpm)
			if err != nil || d <= 0 {
				return inst, 0, fmt.Errorf("invalid duration %q: %w", val, err)
			}
			durSec = d
			hasDur = true

		case "fm":
			parts := strings.Split(val, ",")
			if len(parts) != 2 {
				return inst, 0, fmt.Errorf("invalid fm %q (expected ratioOrHz,modIndex)", val)
			}
			modIdxStr := parts[1]
			if arrowIdx := strings.Index(modIdxStr, "->"); arrowIdx > 0 {
				m1, err1 := strconv.ParseFloat(modIdxStr[:arrowIdx], 64)
				m2, err2 := strconv.ParseFloat(modIdxStr[arrowIdx+2:], 64)
				if err1 != nil || err2 != nil || m1 < 0 || m2 < 0 {
					return inst, 0, fmt.Errorf("invalid fm mod_index sweep in %q", val)
				}
				inst.ModIndexStart = m1
				inst.ModIndexEnd = m2
				inst.ModIndex = m1
			} else {
				mi, err2 := strconv.ParseFloat(modIdxStr, 64)
				if err2 != nil || mi < 0 {
					return inst, 0, fmt.Errorf("invalid fm mod_index in %q", val)
				}
				inst.ModIndexStart = mi
				inst.ModIndexEnd = mi
				inst.ModIndex = mi
			}
			if strings.HasSuffix(strings.ToLower(parts[0]), "hz") {
				mf, err1 := parseHzNumber(parts[0])
				if err1 != nil || mf <= 0 {
					return inst, 0, fmt.Errorf("invalid fm mod_freq in %q", val)
				}
				inst.ModFreq = mf
			} else {
				mr, err1 := strconv.ParseFloat(parts[0], 64)
				if err1 != nil || mr <= 0 {
					return inst, 0, fmt.Errorf("invalid fm mod_ratio in %q", val)
				}
				inst.ModRatio = mr
			}

		case "mod_ratio":
			mr, err := strconv.ParseFloat(val, 64)
			if err != nil || mr <= 0 {
				return inst, 0, fmt.Errorf("invalid mod_ratio %q", val)
			}
			inst.ModRatio = mr

		case "mod_freq":
			mf, err := parseHzNumber(val)
			if err != nil || mf <= 0 {
				return inst, 0, fmt.Errorf("invalid mod_freq %q", val)
			}
			inst.ModFreq = mf

		case "mod_index":
			if arrowIdx := strings.Index(val, "->"); arrowIdx > 0 {
				m1, err1 := strconv.ParseFloat(val[:arrowIdx], 64)
				m2, err2 := strconv.ParseFloat(val[arrowIdx+2:], 64)
				if err1 != nil || err2 != nil || m1 < 0 || m2 < 0 {
					return inst, 0, fmt.Errorf("invalid mod_index sweep %q", val)
				}
				inst.ModIndexStart = m1
				inst.ModIndexEnd = m2
				inst.ModIndex = m1
			} else {
				mi, err := strconv.ParseFloat(val, 64)
				if err != nil || mi < 0 {
					return inst, 0, fmt.Errorf("invalid mod_index %q", val)
				}
				inst.ModIndexStart = mi
				inst.ModIndexEnd = mi
				inst.ModIndex = mi
			}

		case "noise":
			parts := strings.Split(val, ",")
			if len(parts) != 2 {
				return inst, 0, fmt.Errorf("invalid noise %q (expected filterCoeff,blend)", val)
			}
			nf, err1 := strconv.ParseFloat(parts[0], 64)
			nb, err2 := strconv.ParseFloat(parts[1], 64)
			if err1 != nil || err2 != nil || nf <= 0 || nf > 1.0 || nb < 0 || nb > 1.0 {
				return inst, 0, fmt.Errorf("invalid noise parameters %q (filter in (0,1], blend in [0,1])", val)
			}
			inst.NoiseFilter = nf
			inst.NoiseBlend = nb
			hasExplicitNoiseBlend = true

		case "noise_filter":
			nf, err := strconv.ParseFloat(val, 64)
			if err != nil || nf <= 0 || nf > 1.0 {
				return inst, 0, fmt.Errorf("invalid noise_filter %q (must be in (0.0, 1.0])", val)
			}
			inst.NoiseFilter = nf

		case "noise_blend":
			nb, err := strconv.ParseFloat(val, 64)
			if err != nil || nb < 0 || nb > 1.0 {
				return inst, 0, fmt.Errorf("invalid noise_blend %q (must be in [0.0, 1.0])", val)
			}
			inst.NoiseBlend = nb
			hasExplicitNoiseBlend = true

		case "q", "res", "resonance":
			q, err := strconv.ParseFloat(val, 64)
			if err != nil || q < 0.1 || q > 20.0 {
				return inst, 0, fmt.Errorf("invalid filter resonance q %q (expected 0.1 to 20.0)", val)
			}
			inst.ResonanceQ = q

		case "lpf":
			if arrowIdx := strings.Index(val, "->"); arrowIdx > 0 {
				f1, err1 := parseFilterFreqOrAlpha(val[:arrowIdx])
				f2, err2 := parseFilterFreqOrAlpha(val[arrowIdx+2:])
				if err1 != nil || err2 != nil {
					return inst, 0, fmt.Errorf("invalid lpf sweep %q", val)
				}
				inst.LPFStart = f1
				inst.LPFEnd = f2
				inst.LPF = f1
			} else {
				f, err := parseFilterFreqOrAlpha(val)
				if err != nil {
					return inst, 0, fmt.Errorf("invalid lpf %q: %w", val, err)
				}
				inst.LPFStart = f
				inst.LPFEnd = f
				inst.LPF = f
			}

		case "hpf":
			if arrowIdx := strings.Index(val, "->"); arrowIdx > 0 {
				f1, err1 := parseFilterFreqOrAlpha(val[:arrowIdx])
				f2, err2 := parseFilterFreqOrAlpha(val[arrowIdx+2:])
				if err1 != nil || err2 != nil {
					return inst, 0, fmt.Errorf("invalid hpf sweep %q", val)
				}
				inst.HPFStart = f1
				inst.HPFEnd = f2
				inst.HPF = f1
			} else {
				f, err := parseFilterFreqOrAlpha(val)
				if err != nil {
					return inst, 0, fmt.Errorf("invalid hpf %q: %w", val, err)
				}
				inst.HPFStart = f
				inst.HPFEnd = f
				inst.HPF = f
			}

		case "bitcrush":
			parts := strings.Split(val, ",")
			if len(parts) != 2 {
				return inst, 0, fmt.Errorf("invalid bitcrush %q (expected bits,downsample)", val)
			}
			bits, err1 := strconv.Atoi(parts[0])
			down, err2 := strconv.Atoi(parts[1])
			if err1 != nil || err2 != nil || bits < 1 || bits > 16 || down < 1 {
				return inst, 0, fmt.Errorf("invalid bitcrush %q (bits 1..16, downsample >= 1)", val)
			}
			inst.BitcrushBits = bits
			inst.BitcrushDownsample = down

		default:
			return inst, 0, fmt.Errorf("unknown attribute %q", key)
		}
	}

	if !hasWave {
		return inst, 0, fmt.Errorf("missing required 'wave=<type>' or 'preset=<name>' attribute")
	}
	if (inst.WaveType == "noise" || inst.WaveType == "psg_noise" || inst.WaveType == "periodic_noise") && !hasExplicitNoiseBlend {
		inst.NoiseBlend = 1.0
	}
	if isStep && !hasDur {
		return inst, 0, fmt.Errorf("missing required 'dur=<duration>' attribute on step")
	}
	return inst, durSec, nil
}

func normalizeWaveType(w string) (string, error) {
	switch strings.ToLower(strings.TrimSpace(w)) {
	case "sine", "sin":
		return "sine", nil
	case "square", "sq", "pulse":
		return "square", nil
	case "triangle", "tri":
		return "triangle", nil
	case "sawtooth", "saw":
		return "sawtooth", nil
	case "noise", "white_noise":
		return "noise", nil
	case "psg_noise", "periodic_noise", "psg":
		return "psg_noise", nil
	case "fm":
		return "fm", nil
	default:
		return "", fmt.Errorf("unsupported wave type %q (valid: sine, square, pulse, triangle, sawtooth, noise, psg_noise, fm, or preset name)", w)
	}
}

func parseFilterFreqOrAlpha(s string) (float64, error) {
	trimmed := strings.TrimSpace(s)
	lower := strings.ToLower(trimmed)
	if strings.HasSuffix(lower, "hz") {
		return parseHzNumber(trimmed)
	}
	val, err := strconv.ParseFloat(trimmed, 64)
	if err != nil || val <= 0 {
		return 0, fmt.Errorf("invalid filter frequency or alpha %q", s)
	}
	return val, nil
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

// ParseDuration converts a DSL duration token (e.g. "4", "8", "16.", "8t", "1/4", "2b", "150ms", "0.5s")
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
			startNum := i
			if i < n && (input[i] == '+' || input[i] == '-') {
				i++
			}
			for i < n && input[i] >= '0' && input[i] <= '9' {
				i++
			}
			semi, err := strconv.Atoi(input[startNum:i])
			if err != nil || semi < -48 || semi > 48 {
				return nil, fmt.Errorf("invalid semitone transpose '@%s' (expected e.g. @+12 or @-7)", input[startNum:i])
			}
			tokens = append(tokens, dslToken{kind: tokTranspose, number: semi})
			continue
		}

		// Scan an atom token (which may contain [...] chord brackets or inst(...) pitch args)
		start := i
		for i < n {
			ch := input[i]
			if ch == ' ' || ch == '\t' || ch == '\r' || ch == '\n' || ch == '|' || ch == ')' || ch == '*' || ch == '@' {
				break
			}
			if ch == '(' {
				//Attached '(' is an instrument argument list like kick(150Hz->40Hz):8
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
	nodes, err := parseNodeList(tokens, &pos, false)
	if err != nil {
		return nil, err
	}
	if len(nodes) == 0 {
		return nil, fmt.Errorf("pattern or track contains no musical events")
	}
	return nodes, nil
}

func parseNodeList(tokens []dslToken, pos *int, insideGroup bool) ([]dslNode, error) {
	var nodes []dslNode
	for *pos < len(tokens) {
		tok := tokens[*pos]
		switch tok.kind {
		case tokPipe:
			*pos++
		case tokRParen:
			if !insideGroup {
				return nil, fmt.Errorf("unmatched ')' in pattern")
			}
			*pos++
			return nodes, nil
		case tokLParen:
			*pos++
			children, err := parseNodeList(tokens, pos, true)
			if err != nil {
				return nil, err
			}
			if len(children) == 0 {
				return nil, fmt.Errorf("empty group '()' is not allowed")
			}
			node := dslNode{isGroup: true, children: children, repeat: 1}
			for *pos < len(tokens) && (tokens[*pos].kind == tokRepeat || tokens[*pos].kind == tokTranspose) {
				if tokens[*pos].kind == tokRepeat {
					node.repeat *= tokens[*pos].number
				} else {
					node.transpose += tokens[*pos].number
				}
				*pos++
			}
			nodes = append(nodes, node)
		case tokAtom:
			*pos++
			node := dslNode{isGroup: false, atom: tok.text, repeat: 1}
			for *pos < len(tokens) && (tokens[*pos].kind == tokRepeat || tokens[*pos].kind == tokTranspose) {
				if tokens[*pos].kind == tokRepeat {
					node.repeat *= tokens[*pos].number
				} else {
					node.transpose += tokens[*pos].number
				}
				*pos++
			}
			nodes = append(nodes, node)
		case tokRepeat:
			return nil, fmt.Errorf("unexpected '*%d' without a preceding note, pattern, or group", tok.number)
		case tokTranspose:
			return nil, fmt.Errorf("unexpected '@%d' without a preceding note, pattern, or group", tok.number)
		}
	}
	if insideGroup {
		return nil, fmt.Errorf("unclosed '(' in pattern")
	}
	return nodes, nil
}

func (s *Score) expandNodesToEvents(nodes []dslNode, defaultInst string, transposeSemi int, activePatterns map[string]bool) ([]NoteEvent, error) {
	if len(activePatterns) > maxPatternDepth {
		return nil, fmt.Errorf("maximum pattern nesting depth (%d) exceeded", maxPatternDepth)
	}
	var out []NoteEvent
	defaultStepDur := "4" // Default to quarter note if duration suffix is omitted

	for _, node := range nodes {
		totalTranspose := transposeSemi + node.transpose
		if node.isGroup {
			subEvents, err := s.expandNodesToEvents(node.children, defaultInst, totalTranspose, activePatterns)
			if err != nil {
				return nil, err
			}
			for r := 0; r < node.repeat; r++ {
				out = append(out, subEvents...)
			}
			continue
		}

		// Check if node.atom is a pattern reference
		if patNodes, isPat := s.Patterns[node.atom]; isPat {
			if activePatterns[node.atom] {
				return nil, fmt.Errorf("cyclic pattern reference detected involving %q", node.atom)
			}
			activePatterns[node.atom] = true
			patEvents, err := s.expandNodesToEvents(patNodes, defaultInst, totalTranspose, activePatterns)
			delete(activePatterns, node.atom)
			if err != nil {
				return nil, fmt.Errorf("in pattern %q: %w", node.atom, err)
			}
			for r := 0; r < node.repeat; r++ {
				out = append(out, patEvents...)
			}
			continue
		}

		// Otherwise parse atom as an event (Rest, Chord, Instrument Trigger, or Pitch/Sweep)
		ev, usedDurStr, err := s.parseSingleAtomEvent(node.atom, defaultInst, defaultStepDur, totalTranspose)
		if err != nil {
			return nil, err
		}
		if usedDurStr != "" {
			defaultStepDur = usedDurStr
		}
		for r := 0; r < node.repeat; r++ {
			out = append(out, ev)
		}
	}
	return out, nil
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

	// 4. Check for bare Instrument Trigger: 'kick:8', 'snare:16', 'hat:16', or track default trigger ':80ms'
	instName := head
	if instName == "" {
		instName = defaultInst
	}
	if inst, ok := s.Instruments[instName]; ok {
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

// polyBLEP computes a polynomial band-limited step correction around phase discontinuities
// at t=0 and t=duty, eliminating ultrasonic square/pulse and sawtooth aliasing in digital SFX synthesis.
func polyBLEP(t, dt float64) float64 {
	if dt <= 0 {
		return 0
	}
	if t < dt {
		u := t / dt
		return u + u - u*u - 1.0
	} else if t > 1.0-dt {
		u := (t - 1.0) / dt
		return u*u + u + u + 1.0
	}
	return 0.0
}

// LFSRNoise produces authentic chiptune pseudo-random periodic or white noise using
// a 16-bit Linear Feedback Shift Register (Galois configuration), replicating classic PSG sound chips.
type LFSRNoise struct {
	lfsr  uint32
	phase float64
	val   float64
}

// NewLFSRNoise instantiates a new 16-bit Galois LFSR noise generator.
func NewLFSRNoise(seed uint32) *LFSRNoise {
	if seed == 0 {
		seed = 0x89abcdef
	}
	bit := (seed ^ (seed >> 1)) & 1
	seed = (seed >> 1) | (bit << 15)
	val := float64(bit)*2.0 - 1.0
	return &LFSRNoise{lfsr: seed, val: val}
}

// Next advances the shift register at the specified clock frequency in Hz.
func (n *LFSRNoise) Next(freq float64) float64 {
	if freq <= 0 || freq >= SampleRate {
		bit := (n.lfsr ^ (n.lfsr >> 1)) & 1
		n.lfsr = (n.lfsr >> 1) | (bit << 15)
		n.val = float64(bit)*2.0 - 1.0
		return n.val
	}
	n.phase += freq / SampleRate
	for n.phase >= 1.0 {
		n.phase -= 1.0
		bit := (n.lfsr ^ (n.lfsr >> 1)) & 1
		n.lfsr = (n.lfsr >> 1) | (bit << 15)
		n.val = float64(bit)*2.0 - 1.0
	}
	return n.val
}

// SVFilter is a Chamberlin State Variable Filter supporting dynamic cutoff frequency
// and resonance Q sweeps without numerical instability or blow-up.
type SVFilter struct {
	s1, s2 float64
}

// Process filters a single sample through the SVF in low-pass ("lp"), high-pass ("hp"), or band-pass ("bp") mode.
func (f *SVFilter) Process(in, cutoffHz, q float64, mode string) float64 {
	if cutoffHz < 10.0 {
		cutoffHz = 10.0
	} else if cutoffHz > SampleRate*0.48 {
		cutoffHz = SampleRate * 0.48
	}
	if q < 0.1 {
		q = 0.707
	} else if q > 20.0 {
		q = 20.0
	}

	fCoeff := 2.0 * math.Sin(math.Pi*cutoffHz/SampleRate)
	qDamp := 1.0 / q

	hp := in - f.s1*qDamp - f.s2
	bp := hp*fCoeff + f.s1
	lp := bp*fCoeff + f.s2

	f.s1 = bp
	f.s2 = lp

	if math.IsNaN(f.s1) || math.IsInf(f.s1, 0) {
		f.s1 = 0
	}
	if math.IsNaN(f.s2) || math.IsInf(f.s2, 0) {
		f.s2 = 0
	}

	switch mode {
	case "hp", "hpf":
		return hp
	case "bp", "bpf":
		return bp
	case "lp", "lpf":
		fallthrough
	default:
		return lp
	}
}

// SoftClip applies smooth C^1 compression above threshold 0.75,
// preventing digital harshness or overflow while retaining full dynamic range.
func SoftClip(x float64) float64 {
	const threshold = 0.75
	if x > threshold {
		delta := x - threshold
		return threshold + (1.0-threshold)*math.Tanh(delta/(1.0-threshold))
	} else if x < -threshold {
		delta := -x - threshold
		return -(threshold + (1.0-threshold)*math.Tanh(delta/(1.0-threshold)))
	}
	return x
}

// applyAntiClickRamp applies a smooth 44-frame (~1ms at 44.1kHz) micro-fade
// at the start and end of the PCM buffer, ensuring sample 0 and the final sample
// are smoothly anchored near zero, eliminating speaker pops when sound effects trigger in Ebitengine.
func applyAntiClickRamp(pcm []byte) {
	alignedLen := len(pcm) &^ 3
	numFrames := alignedLen / BytesPerFrame
	const rampFrames = 44
	if numFrames < rampFrames*2 {
		return
	}

	for i := 0; i < rampFrames; i++ {
		rampIn := float64(i) / float64(rampFrames)
		idxIn := i * BytesPerFrame
		leftIn := int16(uint16(pcm[idxIn]) | (uint16(pcm[idxIn+1]) << 8))
		rightIn := int16(uint16(pcm[idxIn+2]) | (uint16(pcm[idxIn+3]) << 8))
		leftIn = int16(float64(leftIn) * rampIn)
		rightIn = int16(float64(rightIn) * rampIn)
		pcm[idxIn] = byte(leftIn)
		pcm[idxIn+1] = byte(leftIn >> 8)
		pcm[idxIn+2] = byte(rightIn)
		pcm[idxIn+3] = byte(rightIn >> 8)

		outFrameIdx := numFrames - 1 - i
		rampOut := float64(i) / float64(rampFrames)
		idxOut := outFrameIdx * BytesPerFrame
		leftOut := int16(uint16(pcm[idxOut]) | (uint16(pcm[idxOut+1]) << 8))
		rightOut := int16(uint16(pcm[idxOut+2]) | (uint16(pcm[idxOut+3]) << 8))
		leftOut = int16(float64(leftOut) * rampOut)
		rightOut = int16(float64(rightOut) * rampOut)
		pcm[idxOut] = byte(leftOut)
		pcm[idxOut+1] = byte(leftOut >> 8)
		pcm[idxOut+2] = byte(rightOut)
		pcm[idxOut+3] = byte(rightOut >> 8)
	}
}

// SynthesizeScore renders all tracks of a parsed Score into a 4-byte aligned 16-bit 44.1kHz stereo PCM buffer.
func SynthesizeScore(score *Score) ([]byte, error) {
	if score == nil || len(score.Tracks) == 0 {
		return nil, fmt.Errorf("synthesize score: score is nil or has no tracks")
	}

	var trackPCMs [][]byte
	for _, tr := range score.Tracks {
		pcm := synthesizeTrackEvents(tr.Events)
		if len(pcm) > 0 {
			trackPCMs = append(trackPCMs, pcm)
		}
	}
	if len(trackPCMs) == 0 {
		return nil, fmt.Errorf("synthesize score: rendered tracks produced 0 PCM bytes")
	}

	mixed := MixTracksPCM(trackPCMs)

	if score.GlobalLPF > 0 {
		mixed = ApplyLowPassFilter(mixed, score.GlobalLPF)
	}
	if score.GlobalHPF > 0 {
		mixed = ApplyHighPassFilter(mixed, score.GlobalHPF)
	}
	if score.GlobalBitcrushBits > 0 {
		mixed = ApplyBitcrush(mixed, score.GlobalBitcrushBits, score.GlobalBitcrushDownsample)
	}
	if score.HasLoopSlice {
		sliced, err := SliceLoopPCM(mixed, score.LoopStartSec, score.LoopEndSec)
		if err != nil {
			return nil, err
		}
		mixed = sliced
	}

	applyAntiClickRamp(mixed)

	return mixed[:len(mixed)&^3], nil
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
		renderNoteEventInto(sliceBytes, numSamples, ev, int64(eventIdx)*7919+int64(startSample))
	}

	return buf[:len(buf)&^3]
}

func renderNoteEventInto(out []byte, numSamples int, ev NoteEvent, rngSeed int64) {
	inst := ev.Inst
	if inst.Muted {
		return
	}
	durSec := float64(numSamples) / SampleRate

	pan := inst.Pan
	if pan < -1.0 {
		pan = -1.0
	} else if pan > 1.0 {
		pan = 1.0
	}
	leftPan := math.Cos((pan + 1.0) * math.Pi / 4.0)
	rightPan := math.Sin((pan + 1.0) * math.Pi / 4.0)

	vol := inst.Volume
	if vol <= 0 {
		vol = 0.2
	}
	numVoices := len(ev.Pitches)
	voiceScale := 1.0 / math.Sqrt(float64(numVoices))

	phases := make([]float64, numVoices)
	modPhases := make([]float64, numVoices)
	var filterVal float64
	rng := rand.New(rand.NewPCG(uint64(rngSeed), uint64(rngSeed)^0x9e3779b97f4a7c15))
	lfsr := NewLFSRNoise(uint32(rngSeed ^ 0x9e3779b9))

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

	dutyStart := inst.DutyStart
	dutyEnd := inst.DutyEnd
	if dutyStart <= 0 || dutyStart >= 1.0 {
		dutyStart = inst.DutyCycle
		if dutyStart <= 0 || dutyStart >= 1.0 {
			dutyStart = 0.5
		}
	}
	if dutyEnd <= 0 || dutyEnd >= 1.0 {
		dutyEnd = dutyStart
	}

	modStart := inst.ModIndexStart
	modEnd := inst.ModIndexEnd
	if modStart <= 0 {
		modStart = inst.ModIndex
		if modStart <= 0 {
			modStart = 2.0
		}
	}
	if modEnd <= 0 {
		modEnd = modStart
	}

	lpfStart := inst.LPFStart
	lpfEnd := inst.LPFEnd
	if lpfStart <= 0 && inst.LPF > 1.0 {
		lpfStart = inst.LPF
	}
	if lpfEnd <= 0 {
		lpfEnd = lpfStart
	}
	hasLPFSVF := lpfStart > 0 && lpfEnd > 0
	var svfLPF SVFilter

	hpfStart := inst.HPFStart
	hpfEnd := inst.HPFEnd
	if hpfStart <= 0 && inst.HPF > 1.0 {
		hpfStart = inst.HPF
	}
	if hpfEnd <= 0 {
		hpfEnd = hpfStart
	}
	hasHPFSVF := hpfStart > 0 && hpfEnd > 0
	var svfHPF SVFilter

	q := inst.ResonanceQ
	if q < 0.1 {
		q = 0.707
	}

	for i := 0; i < numSamples; i++ {
		t := float64(i) / SampleRate
		progress := t / durSec

		currentDuty := dutyStart + progress*(dutyEnd-dutyStart)
		currentModIndex := modStart + progress*(modEnd-modStart)

		var voiceSum float64
		for vIdx, sw := range ev.Pitches {
			var currentFreq float64
			switch inst.PitchCurve {
			case "lin", "linear":
				currentFreq = sw.StartFreq + progress*(sw.EndFreq-sw.StartFreq)
			case "hyper", "hyperbolic":
				if sw.StartFreq > 0 && sw.EndFreq > 0 {
					currentFreq = sw.StartFreq / (1.0 + progress*(sw.StartFreq/sw.EndFreq-1.0))
				} else {
					currentFreq = sw.StartFreq + progress*(sw.EndFreq-sw.StartFreq)
				}
			case "exp", "exponential":
				fallthrough
			default:
				if sw.StartFreq == sw.EndFreq {
					currentFreq = sw.StartFreq
				} else if sw.StartFreq > 0 && sw.EndFreq > 0 {
					currentFreq = sw.StartFreq * math.Pow(sw.EndFreq/sw.StartFreq, progress)
				} else {
					currentFreq = sw.StartFreq + progress*(sw.EndFreq-sw.StartFreq)
				}
			}

			if inst.VibratoFreq > 0 && inst.VibratoDepth > 0 {
				currentFreq += math.Sin(2.0*math.Pi*inst.VibratoFreq*t) * inst.VibratoDepth
			}

			dt := currentFreq / SampleRate
			phases[vIdx] += dt
			for phases[vIdx] >= 1.0 {
				phases[vIdx] -= 1.0
			}
			phase := phases[vIdx]

			var modFreq float64
			if inst.ModRatio > 0 {
				modFreq = currentFreq * inst.ModRatio
			} else if inst.ModFreq > 0 {
				modFreq = inst.ModFreq
			} else if inst.WaveType == "fm" {
				modFreq = currentFreq * 2.0
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
				modSample := math.Sin(2.0 * math.Pi * modPhases[vIdx])
				oscAmp = math.Sin(2.0*math.Pi*phase + currentModIndex*modSample)
			case "sine":
				oscAmp = math.Sin(2.0 * math.Pi * phase)
			case "square":
				raw := -1.0
				if phase < currentDuty {
					raw = 1.0
				}
				raw += polyBLEP(phase, dt)
				raw -= polyBLEP(math.Mod(phase+1.0-currentDuty, 1.0), dt)
				dc := 2.0*currentDuty - 1.0
				oscAmp = (raw - dc) * 0.85
			case "triangle":
				if phase < 0.5 {
					oscAmp = 4.0*phase - 1.0
				} else {
					oscAmp = 3.0 - 4.0*phase
				}
			case "sawtooth":
				oscAmp = (2.0*phase - 1.0) - polyBLEP(phase, dt)
			case "psg_noise":
				oscAmp = lfsr.Next(currentFreq)
			default:
				oscAmp = math.Sin(2.0 * math.Pi * phase)
			}

			voiceSum += oscAmp * voiceScale
		}

		var rawNoise float64
		if inst.NoiseType == "psg" {
			rawNoise = lfsr.Next(1000.0)
		} else {
			rawNoise = rng.Float64()*2.0 - 1.0
		}
		filterVal += filterCoeff * (rawNoise - filterVal)

		amp := (1.0-blend)*voiceSum + blend*filterVal

		if hasLPFSVF {
			curLPF := lpfStart
			if lpfStart != lpfEnd && lpfStart > 0 && lpfEnd > 0 {
				curLPF = lpfStart * math.Pow(lpfEnd/lpfStart, progress)
			}
			amp = svfLPF.Process(amp, curLPF, q, "lp")
		}
		if hasHPFSVF {
			curHPF := hpfStart
			if hpfStart != hpfEnd && hpfStart > 0 && hpfEnd > 0 {
				curHPF = hpfStart * math.Pow(hpfEnd/hpfStart, progress)
			}
			amp = svfHPF.Process(amp, curHPF, q, "hp")
		}

		env := getEnvelope(t, durSec, inst.Attack, inst.Decay, inst.Sustain, inst.Release)
		finalAmp := SoftClip(amp * env * vol)

		leftVal := int16(math.Max(-1.0, math.Min(1.0, finalAmp*leftPan)) * 32760)
		rightVal := int16(math.Max(-1.0, math.Min(1.0, finalAmp*rightPan)) * 32760)

		idx := i * BytesPerFrame
		out[idx] = byte(leftVal)
		out[idx+1] = byte(leftVal >> 8)
		out[idx+2] = byte(rightVal)
		out[idx+3] = byte(rightVal >> 8)
	}

	if !hasLPFSVF && inst.LPF > 0 && inst.LPF <= 1.0 {
		filtered := ApplyLowPassFilter(out, inst.LPF)
		copy(out, filtered)
	}
	if !hasHPFSVF && inst.HPF > 0 && inst.HPF < 1.0 {
		filtered := ApplyHighPassFilter(out, inst.HPF)
		copy(out, filtered)
	}
	if inst.BitcrushBits > 0 {
		crushed := ApplyBitcrush(out, inst.BitcrushBits, inst.BitcrushDownsample)
		copy(out, crushed)
	}
}

// MixTracksPCM sums multiple stereo 16-bit PCM byte slices with smooth C^1 soft-clipping and 4-byte alignment.
func MixTracksPCM(tracks [][]byte) []byte {
	maxLen := 0
	for _, t := range tracks {
		aligned := len(t) &^ 3
		if aligned > maxLen {
			maxLen = aligned
		}
	}
	maxLen &= ^3
	result := make([]byte, maxLen)

	for i := 0; i < maxLen; i += 2 {
		var sum float64
		for _, t := range tracks {
			alignedTrackLen := len(t) &^ 3
			if i+1 < alignedTrackLen {
				sample := int16(uint16(t[i]) | (uint16(t[i+1]) << 8))
				sum += float64(sample) / 32767.0
			}
		}
		clipped := SoftClip(sum)
		outVal := int16(clipped * 32760.0)
		result[i] = byte(outVal)
		result[i+1] = byte(outVal >> 8)
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
	if t < 0 || t > duration {
		return 0.0
	}
	if attack+decay+release > duration {
		rampUp := duration * 0.1
		if t < rampUp {
			return t / rampUp
		}
		return 1.0 - (t-rampUp)/(duration-rampUp)
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
// 6. PRODUCTION SFX AUDIT & VALIDATION ENGINE
// ============================================================================

// SFXValidationReport contains acoustic and DSP diagnostics for a synthesized sound effect.
type SFXValidationReport struct {
	TotalFrames      int
	DurationSec      float64
	PeakLeft         float64 // 0.0 to 1.0 linear amplitude
	PeakRight        float64 // 0.0 to 1.0 linear amplitude
	PeakDBFS         float64 // dB relative to full scale (0 dBFS = max)
	RMSLeft          float64
	RMSRight         float64
	RMSDBFS          float64
	DCOffsetLeft     float64
	DCOffsetRight    float64
	StartSampleLeft  int16
	StartSampleRight int16
	EndSampleLeft    int16
	EndSampleRight   int16
	Passed           bool
	Issues           []string
}

// ValidateProductionSFX audits a synthesized PCM buffer against production game audio standards:
// 1. Strict 4-byte frame alignment and non-empty length.
// 2. Playback duration between 5ms and 15.0s.
// 3. Amplitude headroom: true peak between -36 dBFS (not silent) and -0.01 dBFS (no digital clipping).
// 4. DC offset under 0.02 (2% full scale) preventing sub-bass speaker excursion and gate clicks.
// 5. Anti-click boundary zero-crossings: initial and final frames smoothly anchored near zero.
func ValidateProductionSFX(pcm []byte) (*SFXValidationReport, error) {
	rep := &SFXValidationReport{Passed: true}
	if len(pcm) == 0 {
		rep.Passed = false
		rep.Issues = append(rep.Issues, "PCM buffer is empty (0 bytes)")
		return rep, errors.New(strings.Join(rep.Issues, "; "))
	}
	if len(pcm)%4 != 0 {
		rep.Passed = false
		rep.Issues = append(rep.Issues, fmt.Sprintf("PCM buffer is not 4-byte frame aligned (%d bytes)", len(pcm)))
	}

	alignedLen := len(pcm) &^ 3
	numFrames := alignedLen / BytesPerFrame
	rep.TotalFrames = numFrames
	rep.DurationSec = float64(numFrames) / SampleRate

	if rep.DurationSec < 0.005 {
		rep.Passed = false
		rep.Issues = append(rep.Issues, fmt.Sprintf("duration %.3fs is under 5ms minimum", rep.DurationSec))
	} else if rep.DurationSec > 15.0 {
		rep.Passed = false
		rep.Issues = append(rep.Issues, fmt.Sprintf("duration %.2fs exceeds 15.0s maximum SFX limit", rep.DurationSec))
	}

	if numFrames > 0 {
		rep.StartSampleLeft = int16(uint16(pcm[0]) | (uint16(pcm[1]) << 8))
		rep.StartSampleRight = int16(uint16(pcm[2]) | (uint16(pcm[3]) << 8))
		lastIdx := (numFrames - 1) * BytesPerFrame
		rep.EndSampleLeft = int16(uint16(pcm[lastIdx]) | (uint16(pcm[lastIdx+1]) << 8))
		rep.EndSampleRight = int16(uint16(pcm[lastIdx+2]) | (uint16(pcm[lastIdx+3]) << 8))
	}

	var sumL, sumR float64
	var sumSqL, sumSqR float64
	var maxAbsL, maxAbsR float64

	for i := 0; i < alignedLen; i += 4 {
		sL := float64(int16(uint16(pcm[i]) | (uint16(pcm[i+1]) << 8))) / 32768.0
		sR := float64(int16(uint16(pcm[i+2]) | (uint16(pcm[i+3]) << 8))) / 32768.0

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
	}

	rep.PeakLeft = maxAbsL
	rep.PeakRight = maxAbsR
	peakMax := math.Max(maxAbsL, maxAbsR)
	if peakMax > 0 {
		rep.PeakDBFS = 20.0 * math.Log10(peakMax)
	} else {
		rep.PeakDBFS = -120.0
	}

	if numFrames > 0 {
		rep.DCOffsetLeft = sumL / float64(numFrames)
		rep.DCOffsetRight = sumR / float64(numFrames)
		rep.RMSLeft = math.Sqrt(sumSqL / float64(numFrames))
		rep.RMSRight = math.Sqrt(sumSqR / float64(numFrames))
		rmsMax := math.Max(rep.RMSLeft, rep.RMSRight)
		if rmsMax > 0 {
			rep.RMSDBFS = 20.0 * math.Log10(rmsMax)
		} else {
			rep.RMSDBFS = -120.0
		}
	}

	if peakMax < 0.015 {
		rep.Passed = false
		rep.Issues = append(rep.Issues, fmt.Sprintf("signal is effectively silent (peak: %.4f, %.1f dBFS)", peakMax, rep.PeakDBFS))
	}
	if peakMax > 0.9995 {
		rep.Passed = false
		rep.Issues = append(rep.Issues, fmt.Sprintf("signal exhibits digital clipping (peak: %.4f, >= 0 dBFS)", peakMax))
	}
	if math.Abs(rep.DCOffsetLeft) > 0.02 || math.Abs(rep.DCOffsetRight) > 0.02 {
		rep.Passed = false
		rep.Issues = append(rep.Issues, fmt.Sprintf("excessive DC offset (L: %+.4f, R: %+.4f, threshold: ±0.02)", rep.DCOffsetLeft, rep.DCOffsetRight))
	}
	if math.Abs(float64(rep.StartSampleLeft)) > 300 || math.Abs(float64(rep.StartSampleRight)) > 300 {
		rep.Passed = false
		rep.Issues = append(rep.Issues, fmt.Sprintf("boundary start frame not zeroed (L: %d, R: %d, anti-click violated)", rep.StartSampleLeft, rep.StartSampleRight))
	}
	if math.Abs(float64(rep.EndSampleLeft)) > 300 || math.Abs(float64(rep.EndSampleRight)) > 300 {
		rep.Passed = false
		rep.Issues = append(rep.Issues, fmt.Sprintf("boundary end frame not zeroed (L: %d, R: %d, anti-click violated)", rep.EndSampleLeft, rep.EndSampleRight))
	}

	if !rep.Passed {
		return rep, fmt.Errorf("production SFX validation failed: %s", strings.Join(rep.Issues, "; "))
	}
	return rep, nil
}

// ValidateScore audits a parsed Score for structural integrity and numerical sanity.
func ValidateScore(score *Score) error {
	if score == nil {
		return fmt.Errorf("validate score: score is nil")
	}
	if len(score.Tracks) == 0 {
		return fmt.Errorf("validate score: score %q has no tracks", score.Title)
	}
	for trIdx, tr := range score.Tracks {
		if len(tr.Events) == 0 {
			return fmt.Errorf("validate score: track %d %q has 0 note events", trIdx, tr.Name)
		}
		var trackSec float64
		for evIdx, ev := range tr.Events {
			if math.IsNaN(ev.DurationSec) || math.IsInf(ev.DurationSec, 0) || ev.DurationSec < 0 {
				return fmt.Errorf("validate score: track %d event %d has invalid duration %.4f", trIdx, evIdx, ev.DurationSec)
			}
			trackSec += ev.DurationSec
			for pIdx, p := range ev.Pitches {
				if math.IsNaN(p.StartFreq) || math.IsNaN(p.EndFreq) || p.StartFreq <= 0 || p.EndFreq <= 0 {
					return fmt.Errorf("validate score: track %d event %d pitch %d has invalid frequencies (%.1f -> %.1f)", trIdx, evIdx, pIdx, p.StartFreq, p.EndFreq)
				}
			}
		}
		if trackSec <= 0 {
			return fmt.Errorf("validate score: track %d %q has total duration 0s", trIdx, tr.Name)
		}
	}
	return nil
}
