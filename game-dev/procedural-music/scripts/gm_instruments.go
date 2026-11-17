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
	"strconv"
	"strings"
)

var gmProgramByName = map[string]int{
	// Piano (0..7)
	"piano":                0,
	"acoustic_grand_piano": 0,
	"grand_piano":          0,
	"bright_piano":         1,
	"electric_grand":       2,
	"honky_tonk":           3,
	"epiano":               4,
	"epiano1":              4,
	"rhodes":               4,
	"electric_piano_1":     4,
	"epiano2":              5,
	"dx7":                  5,
	"chorused_piano":       5,
	"electric_piano_2":     5,
	"harpsichord":          6,
	"clavinet":             7,

	// Chromatic Percussion (8..15)
	"celesta":       8,
	"glockenspiel":  9,
	"music_box":     10,
	"vibraphone":    11,
	"marimba":       12,
	"xylophone":     13,
	"tubular_bells": 14,
	"bell":          14,
	"chime":         14,
	"dulcimer":      15,

	// Organ (16..23)
	"organ":            16,
	"drawbar_organ":    16,
	"hammond":          16,
	"percussive_organ": 17,
	"rock_organ":       18,
	"church_organ":     19,
	"pipe_organ":       19,
	"reed_organ":       20,
	"accordion":        21,
	"harmonica":        22,
	"bandoneon":        23,

	// Guitar (24..31)
	"guitar":            24,
	"acoustic_guitar":   24,
	"nylon_guitar":      24,
	"steel_guitar":      25,
	"jazz_guitar":       26,
	"clean_guitar":      27,
	"muted_guitar":      28,
	"overdriven_guitar": 29,
	"distortion_guitar": 30,
	"guitar_harmonics":  31,

	// Bass (32..39)
	"acoustic_bass": 32,
	"upright_bass":  32,
	"finger_bass":   33,
	"electric_bass": 33,
	"pick_bass":     34,
	"fretless_bass": 35,
	"slap_bass":     36,
	"slap_bass_1":   36,
	"slap_bass_2":   37,
	"synth_bass":    38,
	"synth_bass_1":  38,
	"fm_bass":       38,
	"synth_bass_2":  39,
	"sub_bass":      39,

	// Strings & Orchestra (40..47)
	"violin":            40,
	"viola":             41,
	"cello":             42,
	"contrabass":        43,
	"double_bass":       43,
	"tremolo_strings":   44,
	"pizzicato_strings": 45,
	"pizzicato":         45,
	"orchestral_harp":   46,
	"harp":              46,
	"pluck":             46,
	"timpani":           47,

	// Ensemble & Choir (48..55)
	"strings":           48,
	"ensemble":          48,
	"string_ensemble_1": 48,
	"slow_strings":      49,
	"string_ensemble_2": 49,
	"synth_strings":     50,
	"synth_strings_1":   50,
	"synth_strings_2":   51,
	"choir":             52,
	"choir_aahs":        52,
	"voice":             52,
	"vocal":             52,
	"voice_oohs":        53,
	"synth_voice":       54,
	"orchestra_hit":     55,

	// Brass (56..63)
	"trumpet":       56,
	"trombone":      57,
	"tuba":          58,
	"muted_trumpet": 59,
	"french_horn":   60,
	"horn":          60,
	"brass":         61,
	"brass_section": 61,
	"synth_brass":   62,
	"synth_brass_1": 62,
	"synth_brass_2": 63,

	// Reed & Pipe (64..79)
	"soprano_sax":  64,
	"alto_sax":     65,
	"tenor_sax":    66,
	"baritone_sax": 67,
	"oboe":         68,
	"english_horn": 69,
	"bassoon":      70,
	"clarinet":     71,
	"piccolo":      72,
	"flute":        73,
	"woodwind":     73,
	"recorder":     74,
	"pan_flute":    75,
	"blown_bottle": 76,
	"shakuhachi":   77,
	"whistle":      78,
	"ocarina":      79,

	// Synth Lead (80..87)
	"lead_square":    80,
	"square":         80,
	"pulse":          80,
	"lead_sawtooth":  81,
	"sawtooth":       81,
	"lead_calliope":  82,
	"lead_chiff":     83,
	"lead_charang":   84,
	"lead_voice":     85,
	"lead_fifths":    86,
	"lead_bass_lead": 87,
	"fm_lead":        87,
	"fm":             87,

	// Synth Pad (88..95)
	"pad_new_age":   88,
	"new_age_pad":   88,
	"pad_warm":      89,
	"warm_pad":      89,
	"pad_polysynth": 90,
	"polysynth":     90,
	"pad_choir":     91,
	"pad_bowed":     92,
	"pad_metallic":  93,
	"pad_halo":      94,
	"pad_sweep":     95,

	// Synth Effects (96..103)
	"fx_rain":       96,
	"fx_soundtrack": 97,
	"fx_crystal":    98,
	"fx_atmosphere": 99,
	"fx_brightness": 100,
	"fx_goblins":    101,
	"fx_echoes":     102,
	"fx_sci_fi":     103,

	// Ethnic & Percussive (104..119)
	"sitar":          104,
	"banjo":          105,
	"shamisen":       106,
	"koto":           107,
	"kalimba":        108,
	"bagpipe":        109,
	"fiddle":         110,
	"shanai":         111,
	"tinkle_bell":    112,
	"agogo":          113,
	"steel_drums":    114,
	"woodblock":      115,
	"taiko_drum":     116,
	"taiko":          116,
	"melodic_tom":    117,
	"synth_drum":     118,
	"reverse_cymbal": 119,
}

var gmDrumNoteByName = map[string]int{
	"kick":           36,
	"bass_drum":      36,
	"bd":             36,
	"acoustic_kick":  35,
	"side_stick":     37,
	"rimshot":        37,
	"rim":            37,
	"snare":          38,
	"sd":             38,
	"electric_snare": 40,
	"clap":           39,
	"hand_clap":      39,
	"low_floor_tom":  41,
	"closed_hi_hat":  42,
	"hat":            42,
	"hihat":          42,
	"ch":             42,
	"high_floor_tom": 43,
	"pedal_hi_hat":   44,
	"low_tom":        45,
	"tom_low":        45,
	"open_hi_hat":    46,
	"open_hat":       46,
	"ohat":           46,
	"oh":             46,
	"low_mid_tom":    47,
	"mid_tom":        47,
	"tom_mid":        47,
	"hi_mid_tom":     48,
	"crash":          49,
	"crash_cymbal":   49,
	"cymbal":         49,
	"high_tom":       50,
	"tom_hi":         50,
	"ride":           51,
	"ride_cymbal":    51,
	"chinese_cymbal": 52,
	"ride_bell":      53,
	"tambourine":     54,
	"splash":         55,
	"cowbell":        56,
	"crash_2":        57,
	"shaker":         70,
	"maracas":        70,
}

// ParseGMProgram parses a General MIDI program number (0..127) or instrument name.
func ParseGMProgram(spec string) (int, error) {
	cleaned := strings.ToLower(strings.TrimSpace(spec))
	cleaned = strings.ReplaceAll(cleaned, "-", "_")
	if n, err := strconv.Atoi(cleaned); err == nil {
		if n < 0 || n > 127 {
			return 0, fmt.Errorf("invalid General MIDI program %d (must be 0..127)", n)
		}
		return n, nil
	}
	if prog, ok := gmProgramByName[cleaned]; ok {
		return prog, nil
	}
	return 0, fmt.Errorf("unknown General MIDI program %q (expected 0..127 or name like piano, epiano, violin, cello, strings, choir, flute, oboe, clarinet, shakuhachi, trumpet, horn, brass, harp, koto, shamisen, synth_bass_1, fm_lead)", spec)
}

// ParseGMDrumNote parses a General MIDI Channel 10 percussion note (27..87) or drum name.
func ParseGMDrumNote(spec string) (int, error) {
	cleaned := strings.ToLower(strings.TrimSpace(spec))
	cleaned = strings.ReplaceAll(cleaned, "-", "_")
	if n, err := strconv.Atoi(cleaned); err == nil {
		if n < 27 || n > 87 {
			return 0, fmt.Errorf("invalid General MIDI drum note %d (must be 27..87)", n)
		}
		return n, nil
	}
	if note, ok := gmDrumNoteByName[cleaned]; ok {
		return note, nil
	}
	return 0, fmt.Errorf("unknown General MIDI drum note %q (expected 27..87 or name like kick, snare, hat, open_hat, crash, ride, clap, tom_hi, tom_mid, tom_low)", spec)
}

func inferWaveTypeFromGMProgram(prog int) string {
	switch {
	case prog >= 0 && prog <= 3:
		return "piano"
	case prog == 7:
		return "psg_square"
	case prog >= 4 && prog <= 6:
		return "ym2612_epiano"
	case prog >= 8 && prog <= 15:
		return "ym2612_bell"
	case prog >= 16 && prog <= 23:
		return "organ"
	case prog == 24 || prog == 25 || prog == 26:
		return "guitar"
	case prog == 27 || prog == 28 || prog == 30:
		return "ym2612_rhythm_guitar"
	case prog == 29 || prog == 31:
		return "ym2612_guitar"
	case prog == 36 || prog == 37:
		return "ym2612_slap_bass"
	case prog >= 32 && prog <= 39:
		return "ym2612_bass"
	case prog == 40 || prog == 41 || prog == 110:
		return "violin"
	case prog == 42 || prog == 43:
		return "cello"
	case prog == 45 || prog == 46:
		return "psg_arp"
	case prog >= 48 && prog <= 51:
		return "ym2612_strings"
	case prog >= 52 && prog <= 54:
		return "ym2612_choir"
	case prog >= 56 && prog <= 63:
		return "ym2612_brass"
	case prog >= 68 && prog <= 70:
		return "oboe"
	case prog == 71:
		return "clarinet"
	case prog >= 72 && prog <= 79:
		return "ym2612_flute"
	case prog == 80:
		return "psg_square"
	case prog == 81:
		return "sawtooth"
	case prog >= 82 && prog <= 87:
		return "fm"
	case prog == 106:
		return "shamisen"
	case prog == 107:
		return "koto"
	default:
		return "ym2612_strings"
	}
}

func inferDrumWaveFromGMDrumNote(note int) string {
	switch note {
	case 35, 36:
		return "kick"
	case 37, 38, 39, 40:
		return "snare"
	case 41, 43, 45, 47, 48, 50:
		return "tom"
	case 42, 44:
		return "ym2612_hat"
	case 46:
		return "ym2612_open_hat"
	case 49, 51, 52, 55, 57:
		return "crash"
	default:
		return "snare"
	}
}

// IsPercussionInstrument returns true if the instrument should be routed to General MIDI Channel 10 (index 9).
func IsPercussionInstrument(inst Instrument) bool {
	if inst.GMDrumNote > 0 {
		return true
	}
	if inst.HasGMProgram {
		return false
	}
	if inst.WaveType == "noise" || IsYM2612DrumWave(inst.WaveType) {
		return true
	}
	lowerName := strings.ToLower(inst.Name)
	for _, kw := range []string{"kick", "snare", "hat", "cymbal", "crash", "ride", "clap", "tom", "rim", "cowbell", "shaker", "tamb"} {
		if strings.Contains(lowerName, kw) {
			return true
		}
	}
	if inst.DefaultStartFreq > inst.DefaultEndFreq && inst.DefaultStartFreq > 0 && inst.DefaultStartFreq <= 320.0 && inst.DefaultEndFreq <= 120.0 {
		return true
	}
	return false
}

// ResolveGMDrumNote returns the General MIDI Channel 10 percussion note number (35..81) for a drum instrument.
func ResolveGMDrumNote(inst Instrument) int {
	if inst.GMDrumNote > 0 {
		return inst.GMDrumNote
	}
	lowerName := strings.ToLower(inst.Name)
	switch {
	case strings.Contains(lowerName, "open") && strings.Contains(lowerName, "hat"), lowerName == "ohat", lowerName == "oh":
		return 46 // Open Hi-Hat
	case strings.Contains(lowerName, "pedal") && strings.Contains(lowerName, "hat"):
		return 44 // Pedal Hi-Hat
	case strings.Contains(lowerName, "hat"), lowerName == "ch":
		return 42 // Closed Hi-Hat
	case strings.Contains(lowerName, "crash"), strings.Contains(lowerName, "cymbal"):
		return 49 // Crash Cymbal 1
	case strings.Contains(lowerName, "ride"):
		return 51 // Ride Cymbal 1
	case strings.Contains(lowerName, "clap"):
		return 39 // Hand Clap
	case strings.Contains(lowerName, "rim"), strings.Contains(lowerName, "stick"):
		return 37 // Side Stick
	case strings.Contains(lowerName, "snare"), lowerName == "sd":
		return 38 // Acoustic Snare
	case strings.Contains(lowerName, "tom_hi"), strings.Contains(lowerName, "high_tom"):
		return 50 // High Tom
	case strings.Contains(lowerName, "tom_mid"), strings.Contains(lowerName, "mid_tom"):
		return 47 // Low-Mid Tom
	case strings.Contains(lowerName, "tom_low"), strings.Contains(lowerName, "low_tom"), strings.Contains(lowerName, "tom"):
		return 45 // Low Tom
	case strings.Contains(lowerName, "kick"), strings.Contains(lowerName, "bd"):
		return 36 // Bass Drum 1
	}
	if inst.WaveType == "noise" {
		if inst.NoiseFilter >= 0.80 {
			return 42 // Closed Hi-Hat
		}
		if inst.Attack >= 0.01 || inst.Decay >= 0.30 {
			return 49 // Crash Cymbal 1
		}
		return 38 // Acoustic Snare
	}
	if inst.DefaultStartFreq >= 160.0 {
		return 47 // Mid Tom
	}
	return 36 // Bass Drum 1
}

// ResolveGMProgram returns the General MIDI program number (0..127) for a melodic/harmonic instrument.
func ResolveGMProgram(inst Instrument) int {
	if inst.HasGMProgram {
		return inst.GMProgram
	}

	// 1. Explicit acoustic/orchestral WaveType takes priority over instrument variable naming
	switch inst.WaveType {
	case "piano":
		return 0 // Acoustic Grand Piano
	case "epiano":
		return 4 // Electric Piano 1
	case "bell":
		return 14 // Tubular Bells
	case "organ":
		return 16 // Drawbar Organ
	case "guitar":
		return 24 // Acoustic Guitar (nylon)
	case "violin":
		return 40 // Violin
	case "cello":
		return 42 // Cello
	case "harp":
		return 46 // Orchestral Harp
	case "strings":
		return 48 // String Ensemble 1
	case "voice":
		return 52 // Choir Aahs
	case "trumpet":
		return 56 // Trumpet
	case "horn":
		return 60 // French Horn
	case "brass":
		return 61 // Brass Section
	case "oboe":
		return 68 // Oboe
	case "clarinet":
		return 71 // Clarinet
	case "flute":
		return 73 // Flute
	case "shakuhachi":
		return 77 // Shakuhachi
	case "koto":
		return 107 // Koto
	case "shamisen":
		return 106 // Shamisen
	case "ym2612_guitar", "overdriven_guitar":
		return 29 // Overdriven Guitar
	case "ym2612_rhythm_guitar", "rhythm_guitar":
		return 30 // Distortion Guitar
	case "ym2612_bass", "synth_bass":
		return 33 // Electric Bass (finger)
	case "sub_bass":
		return 32 // Acoustic / Upright Bass
	case "ym2612_slap_bass", "slap_bass":
		return 36 // Slap Bass 1
	case "ym2612_brass":
		return 61 // Brass Section
	case "ym2612_epiano":
		return 4 // Electric Piano 1 (Rhodes)
	case "ym2612_strings":
		return 48 // String Ensemble 1
	case "ym2612_choir":
		return 52 // Choir Aahs
	case "ym2612_flute":
		return 73 // Flute
	case "ym2612_bell":
		return 11 // Vibraphone
	case "psg_arp", "pulse":
		return 46 // Orchestral Harp
	case "psg_square":
		return 7 // Clavinet
	}

	// 2. For generic synth waveforms (fm, sawtooth, square, triangle, sine), inspect name cues
	lowerName := strings.ToLower(inst.Name)
	switch {
	case strings.Contains(lowerName, "sub") && strings.Contains(lowerName, "bass"):
		return 39 // Synth Bass 2
	case strings.Contains(lowerName, "slap") && strings.Contains(lowerName, "bass"):
		return 36 // Slap Bass 1
	case strings.Contains(lowerName, "bass"):
		if inst.WaveType == "triangle" || inst.WaveType == "sine" {
			return 33 // Electric Bass (finger)
		}
		return 38 // Synth Bass 1
	case strings.Contains(lowerName, "pizz"):
		return 45 // Pizzicato Strings
	case strings.Contains(lowerName, "cello"):
		return 42 // Cello
	case strings.Contains(lowerName, "viola"):
		return 41 // Viola
	case strings.Contains(lowerName, "violin"), strings.Contains(lowerName, "fiddle"):
		return 40 // Violin
	case strings.Contains(lowerName, "harp"):
		return 46 // Orchestral Harp
	case strings.Contains(lowerName, "koto"):
		return 107 // Koto
	case strings.Contains(lowerName, "shamisen"):
		return 106 // Shamisen
	case strings.Contains(lowerName, "shakuhachi"):
		return 77 // Shakuhachi
	case strings.Contains(lowerName, "choir"), strings.Contains(lowerName, "voice"), strings.Contains(lowerName, "vocal"):
		return 52 // Choir Aahs
	case strings.Contains(lowerName, "epiano"), strings.Contains(lowerName, "rhodes"):
		return 4 // Electric Piano 1
	case strings.Contains(lowerName, "piano"):
		return 0 // Acoustic Grand Piano
	case strings.Contains(lowerName, "organ"):
		return 16 // Drawbar Organ
	case strings.Contains(lowerName, "trumpet"):
		return 56 // Trumpet
	case strings.Contains(lowerName, "horn"):
		return 60 // French Horn
	case strings.Contains(lowerName, "brass"):
		return 61 // Brass Section
	case strings.Contains(lowerName, "oboe"):
		return 68 // Oboe
	case strings.Contains(lowerName, "clarinet"):
		return 71 // Clarinet
	case strings.Contains(lowerName, "flute"):
		return 73 // Flute
	case strings.Contains(lowerName, "bell"), strings.Contains(lowerName, "chime"):
		return 14 // Tubular Bells
	}

	switch inst.WaveType {
	case "fm":
		if strings.Contains(lowerName, "arp") {
			return 5 // Electric Piano 2 (DX7)
		}
		if strings.Contains(lowerName, "pad") {
			return 89 // Pad 2 (warm)
		}
		return 87 // Lead 8 (bass + lead)
	case "sawtooth":
		if strings.Contains(lowerName, "pad") || strings.Contains(lowerName, "str") {
			return 48 // String Ensemble 1
		}
		return 81 // Lead 2 (sawtooth)
	case "square":
		return 80 // Lead 1 (square)
	case "triangle":
		if strings.Contains(lowerName, "arp") {
			return 46 // Orchestral Harp
		}
		return 73 // Flute
	case "sine":
		if strings.Contains(lowerName, "pad") {
			return 89 // Pad 2 (warm)
		}
		return 75 // Pan Flute
	default:
		return 0
	}
}
