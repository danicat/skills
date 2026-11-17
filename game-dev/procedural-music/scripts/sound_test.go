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
	"math"
	"os"
	"testing"
)

// ExampleCompileDSL_stageBGM demonstrates composing a 16-bar, 6-channel 16-bit Genesis-style stage theme in the Music DSL.
func ExampleCompileDSL_stageBGM() {
	pcm, err := CompileDSL(DemoStageBGMDSL)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Synthesized Stage BGM (%d bytes PCM, 4-byte aligned=%v)\n", len(pcm), len(pcm)%4 == 0)

	// Output:
	// Synthesized Stage BGM (5210584 bytes PCM, 4-byte aligned=true)
}

// ExampleCompileDSL_bossBGM demonstrates composing an intense 170 BPM 16-bar diminished boss battle theme with 2-operator FM synthesis.
func ExampleCompileDSL_bossBGM() {
	const bossDSL = `
title "Diminished Boss Theme"
type song
bpm 170
time 4/4

# 6-Channel Aggressive Boss Palette
inst fm_lead wave=fm       vol=0.13 pan=-0.20 adsr=0.005,0.04,0.70,0.04 fm=2.0,3.2 vib=8.0,10.0
inst counter wave=sawtooth vol=0.08 pan=0.20  adsr=0.005,0.04,0.60,0.04
inst pad     wave=sawtooth vol=0.06 pan=0.00  adsr=0.050,0.10,0.80,0.10 lpf=0.30
inst bass    wave=sawtooth vol=0.15 pan=0.00  adsr=0.005,0.08,0.60,0.04
inst arp     wave=triangle vol=0.07 pan=-0.30 adsr=0.005,0.03,0.40,0.01
inst kick    wave=sine     vol=0.15 pan=0.00  adsr=0.002,0.05,0.10,0.02 freq=150Hz->35Hz noise=0.15,0.30
inst snare   wave=noise    vol=0.09 pan=0.20  adsr=0.002,0.06,0.10,0.02 noise_filter=0.55

# 1-Bar Motif Cells Transposed Across Diminished Progression (Adim -> Gdim -> Fdim -> Edim)
pattern lead_cell    = A5:8 D#5:8 D#5:8 A5:8 D#5:8 D#5:8 A5:8 C6:8
pattern counter_cell = C5:8 F#4:8 A4:8 C5:8 F#4:8 A4:8 C5:8 D#5:8
pattern arp_cell     = (A4:16 C5:16 D#5:16 F#5:16)*4
pattern bass_cell    = (A1:8 A2:8)*4

pattern lead_phrase    = lead_cell | lead_cell@-2 | lead_cell@-4 | lead_cell@-5
pattern counter_phrase = counter_cell | counter_cell@-2 | counter_cell@-4 | counter_cell@-5
pattern pad_phrase     = [A2 C3 D#3]:1 | [G2 A#2 C#3]:1 | [F2 G#2 B2]:1 | [E2 G2 A#2]:1
pattern bass_phrase    = bass_cell | bass_cell@-2 | bass_cell@-4 | bass_cell@-5
pattern arp_phrase     = arp_cell | arp_cell@-2 | arp_cell@-4 | arp_cell@-5
pattern drums_phrase   = (kick:8 snare:8)*16

# 16-Bar Boss Arrangement
track ch1_lead    fm_lead: lead_phrase * 2 | lead_phrase@+12 * 2
track ch2_counter counter: counter_phrase * 4
track ch3_pad     pad:     pad_phrase * 4
track ch4_bass    bass:    bass_phrase * 4
track ch5_arp     arp:     arp_phrase * 4
track ch6_drums:           drums_phrase * 4
`
	pcm, err := CompileDSL(bossDSL)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Synthesized Boss BGM (%d bytes PCM, 4-byte aligned=%v)\n", len(pcm), len(pcm)%4 == 0)

	// Output:
	// Synthesized Boss BGM (3984564 bytes PCM, 4-byte aligned=true)
}

// ExampleExportWAV demonstrates compiling a Music DSL score and exporting it to a 16-bit 44.1kHz stereo WAV file.
func ExampleExportWAV() {
	const fanfareDSL = `
title "Stage Clear Fanfare"
type song
bpm 150
time 4/4

inst brass wave=fm     vol=0.14 pan=-0.15 adsr=0.01,0.06,0.75,0.08 fm=1.0,2.2 vib=5.0,3.5
inst harm  wave=square vol=0.10 pan=0.20  adsr=0.01,0.06,0.70,0.08 duty=0.25
inst bass  wave=square vol=0.14 pan=0.00  adsr=0.01,0.05,0.60,0.05 duty=0.50

track lead brass: C5:8 E5:8 G5:8 C6:4 G5:8 C6:2
track pad  harm:  [C4 E4 G4]:2. [E4 G4 C5]:2
track low  bass:  C2:4 G2:4 C3:8 G2:8 C2:2
`
	pcm, err := CompileDSL(fanfareDSL)
	if err != nil {
		panic(err)
	}
	f, err := os.CreateTemp("", "fanfare_test_*.wav")
	if err != nil {
		panic(err)
	}
	tmpFile := f.Name()
	if err := f.Close(); err != nil {
		panic(err)
	}
	defer func() {
		if err := os.Remove(tmpFile); err != nil {
			panic(err)
		}
	}()
	if err := ExportWAV(tmpFile, pcm); err != nil {
		panic(err)
	}
	fmt.Printf("Exported WAV successfully (%d bytes)\n", len(pcm))

	// Output:
	// Exported WAV successfully (352800 bytes)
}

func TestMusicDSLParserAndDriftFreeTiming(t *testing.T) {
	score, err := ParseDSL(DemoStageBGMDSL)
	if err != nil {
		t.Fatalf("ParseDSL(DemoStageBGMDSL) failed: %v", err)
	}
	if len(score.Tracks) != 6 {
		t.Fatalf("expected 6 tracks, got %d", len(score.Tracks))
	}

	// Verify all 6 tracks (which use :1, :8, :16, and :32 subdivisions across 16 bars)
	// render to the exact same byte length with zero cumulative floating-point drift.
	var expectedLen int
	for idx, tr := range score.Tracks {
		trackPCM := synthesizeTrackEvents(tr.Events)
		if len(trackPCM) == 0 || len(trackPCM)%4 != 0 {
			t.Fatalf("track %q produced unaligned or empty PCM (%d bytes)", tr.Name, len(trackPCM))
		}
		if idx == 0 {
			expectedLen = len(trackPCM)
		} else if len(trackPCM) != expectedLen {
			t.Fatalf("drift detected on track %q: got %d bytes, want %d bytes", tr.Name, len(trackPCM), expectedLen)
		}
	}

	// Also verify battle_theme.music has 12 tracks, zero drift across 32 bars (48.00s = 8,467,200 bytes),
	// and passes full music-theory and harmonic consonance validation.
	battleScore, err := LoadDSLFile("battle_theme.music")
	if err != nil {
		t.Fatalf("LoadDSLFile(battle_theme.music) failed: %v", err)
	}
	if err := ValidateProductionBGM(battleScore, 8, 30.0); err != nil {
		t.Fatalf("ValidateProductionBGM(battle_theme.music) failed: %v", err)
	}
	if len(battleScore.Tracks) != 12 {
		t.Fatalf("battle_theme.music: expected 12 tracks, got %d", len(battleScore.Tracks))
	}
	const wantBattleBytes = 48 * BytesPerSecond // 8,467,200 bytes
	for _, tr := range battleScore.Tracks {
		trackPCM := synthesizeTrackEvents(tr.Events)
		if len(trackPCM) != wantBattleBytes {
			t.Fatalf("battle_theme.music track %q: got %d bytes, want %d bytes (zero drift)", tr.Name, len(trackPCM), wantBattleBytes)
		}
	}

	// Verify credits_theme.music has 13 tracks (1:1 with its 13 instruments), zero drift across 36 bars (90.00s = 15,876,000 bytes),
	// and passes full music-theory and harmonic consonance validation.
	creditsScore, err := LoadDSLFile("credits_theme.music")
	if err != nil {
		t.Fatalf("LoadDSLFile(credits_theme.music) failed: %v", err)
	}
	if err := ValidateProductionBGM(creditsScore, 13, 90.0); err != nil {
		t.Fatalf("ValidateProductionBGM(credits_theme.music) failed: %v", err)
	}
	if len(creditsScore.Tracks) != 13 {
		t.Fatalf("credits_theme.music: expected 13 tracks, got %d", len(creditsScore.Tracks))
	}
	const wantCreditsBytes = 90 * BytesPerSecond // 15,876,000 bytes
	for _, tr := range creditsScore.Tracks {
		trackPCM := synthesizeTrackEvents(tr.Events)
		if len(trackPCM) != wantCreditsBytes {
			t.Fatalf("credits_theme.music track %q: got %d bytes, want %d bytes (zero drift)", tr.Name, len(trackPCM), wantCreditsBytes)
		}
	}

	// Verify pitch and duration math
	a4, err := PitchToFreq("A4")
	if err != nil || math.Abs(a4-440.0) > 1e-6 {
		t.Fatalf("PitchToFreq(A4) = %v, %v; want 440.0", a4, err)
	}
	c4, err := PitchToFreq("C4")
	if err != nil || math.Abs(c4-261.625565) > 1e-3 {
		t.Fatalf("PitchToFreq(C4) = %v, %v; want ~261.63", c4, err)
	}
	dottedQuarter, err := ParseDuration("4.", 120)
	if err != nil || math.Abs(dottedQuarter-0.75) > 1e-6 {
		t.Fatalf("ParseDuration(4., 120) = %v, %v; want 0.75s", dottedQuarter, err)
	}
	tripletEighth, err := ParseDuration("8t", 120)
	if err != nil || math.Abs(tripletEighth-(0.25*2.0/3.0)) > 1e-6 {
		t.Fatalf("ParseDuration(8t, 120) = %v, %v; want 0.1667s", tripletEighth, err)
	}
}

func TestPCMAlignmentAndDSPPostProcessing(t *testing.T) {
	if got := AlignPCMBytes(103); got != 100 {
		t.Fatalf("AlignPCMBytes(103) = %d, want 100", got)
	}
	if got := AlignPCMOffset(107); got != 104 {
		t.Fatalf("AlignPCMOffset(107) = %d, want 104", got)
	}

	unalignedA := []byte{1, 2, 3, 4, 5, 6, 7}
	unalignedB := []byte{10, 0, 20, 0, 30}
	mixed := MixTracksPCM([][]byte{unalignedA, unalignedB})
	if len(mixed)%4 != 0 || len(mixed) != 4 {
		t.Fatalf("MixTracksPCM length = %d, want 4-byte aligned length 4", len(mixed))
	}

	const filterLoopDSL = `
title "Filtered Loop Test"
type song
bpm 120
filter lpf 0.35
filter hpf 0.85
bitcrush 8 2
loop 0.05s 0.20s

inst synth wave=sawtooth vol=0.5 adsr=0.01,0.04,0.8,0.05 lpf=0.4 hpf=0.9 bitcrush=12,2
track main synth: A4:4
`
	pcm, err := CompileDSL(filterLoopDSL)
	if err != nil {
		t.Fatalf("CompileDSL(filterLoopDSL) failed: %v", err)
	}
	if len(pcm) == 0 || len(pcm)%4 != 0 {
		t.Fatalf("CompileDSL returned unaligned or empty slice (%d bytes)", len(pcm))
	}
}

func TestDSLFailFastErrors(t *testing.T) {
	invalidScripts := []struct {
		name string
		dsl  string
	}{
		{"empty", ""},
		{"unknown directive", "foo bar"},
		{"invalid wave", "inst lead wave=banjo\ntrack t lead: A4:4"},
		{"missing wave", "inst lead vol=0.5\ntrack t lead: A4:4"},
		{"unknown instrument on track", "track t unknown_inst: A4:4"},
		{"invalid pitch", "inst lead wave=sine\ntrack t lead: H9:4"},
		{"cyclic pattern", "inst lead wave=sine\npattern a = b\npattern b = a\ntrack t lead: a"},
		{"unclosed group", "inst lead wave=sine\ntrack t lead: (A4:8 C5:8"},
		{"unclosed chord", "inst lead wave=sine\ntrack t lead: [A3 C4 E4:2"},
	}

	for _, tc := range invalidScripts {
		t.Run(tc.name, func(t *testing.T) {
			if _, err := CompileDSL(tc.dsl); err == nil {
				t.Fatalf("expected CompileDSL to fail fast on %q, but it succeeded", tc.name)
			}
		})
	}

	// Verify ValidateScoreTheory catches pitch-sweep sirens, continuous melodic noise, and minor-2nd/b9 clashes
	theoryViolations := []struct {
		name string
		dsl  string
	}{
		{
			"melodic_pitch_siren",
			"bpm 100\ninst v wave=violin vol=0.1\ntrack t v: A4->F5:2",
		},
		{
			"melodic_continuous_noise",
			"bpm 100\ninst v wave=violin vol=0.1 noise=0.05,0.4\ntrack t v: A4:2",
		},
		{
			"minor_second_clash",
			"bpm 100\ninst v wave=violin vol=0.1\ntrack t1 v: B4:2\ntrack t2 v: C5:2",
		},
		{
			"flat_ninth_clash",
			"bpm 100\ninst v wave=strings vol=0.1\ntrack t1 v: E3:2\ntrack t2 v: F4:2",
		},
	}

	for _, tc := range theoryViolations {
		t.Run(tc.name, func(t *testing.T) {
			score, err := ParseDSL(tc.dsl)
			if err != nil {
				t.Fatalf("ParseDSL(%q) unexpected error: %v", tc.name, err)
			}
			if err := ValidateScoreTheory(score); err == nil {
				t.Fatalf("expected ValidateScoreTheory to reject %q, but it passed", tc.name)
			}
		})
	}
}

func TestTempoMarkingsDynamicsArticulationsAndStrudelOps(t *testing.T) {
	// 1. Classical Tempo Markings
	tempoCases := []struct {
		spec    string
		wantBPM float64
	}{
		{"allegro", 138},
		{"andantino", 96},
		{"vivace", 160},
		{"adagio", 70},
		{"andantino 96", 96},
		{"allegro 144", 144},
		{"128 allegro", 128},
	}
	for _, tc := range tempoCases {
		got, _, err := ParseTempoSpec(tc.spec)
		if err != nil || math.Abs(got-tc.wantBPM) > 1e-6 {
			t.Fatalf("ParseTempoSpec(%q) = %v, %v; want %v", tc.spec, got, err, tc.wantBPM)
		}
	}

	// 2. Staccato vs Legato articulation preserves exact sample length while detaching the tail
	const staccatoDSL = `
tempo allegro 120
time 4/4
inst v wave=violin vol=0.4 adsr=0.01,0.05,0.8,0.04
track stacc_tr v: (A4:4@staccato)*4
track leg_tr   v: (A4:4@legato)*4
`
	staccScore, err := ParseDSL(staccatoDSL)
	if err != nil {
		t.Fatalf("ParseDSL(staccatoDSL) failed: %v", err)
	}
	staccPCM := synthesizeTrackEvents(staccScore.Tracks[0].Events)
	legPCM := synthesizeTrackEvents(staccScore.Tracks[1].Events)
	if len(staccPCM) != len(legPCM) {
		t.Fatalf("staccato track length (%d) != legato track length (%d)", len(staccPCM), len(legPCM))
	}
	// Verify the second half of the first staccato beat is detached silence (zero bytes)
	oneBeatBytes := len(staccPCM) / 4
	tailStart := AlignPCMBytes(int(float64(oneBeatBytes) * 0.65))
	tailEnd := AlignPCMBytes(int(float64(oneBeatBytes) * 0.95))
	nonZeroStaccTail := 0
	nonZeroLegTail := 0
	for i := tailStart; i < tailEnd; i++ {
		if staccPCM[i] != 0 {
			nonZeroStaccTail++
		}
		if legPCM[i] != 0 {
			nonZeroLegTail++
		}
	}
	if nonZeroStaccTail != 0 {
		t.Fatalf("expected detached silence in staccato tail [%d:%d], found %d non-zero bytes", tailStart, tailEnd, nonZeroStaccTail)
	}
	if nonZeroLegTail == 0 {
		t.Fatalf("expected sustained signal in legato tail [%d:%d], found all zeros", tailStart, tailEnd)
	}

	// 3. Per-channel/segment volume envelopes (@crescendo, @fade_in, @fade_out, @swell, @mp->ff)
	//    plus Strudel-inspired operations (@slow, @fast, @pan sweep, @lpf, Euclidean rhythms, < > alternation)
	const expressiveDSL = `
title "Expressive & Strudel Operations Test"
type song
tempo allegro
time 4/4

inst violin wave=violin  vol=0.12 pan=0.0  adsr=0.02,0.08,0.85,0.08
inst harp   wave=harp    vol=0.10 pan=-0.3 adsr=0.005,0.06,0.30,0.04
inst pad    wave=strings vol=0.10 pan=0.0  adsr=0.05,0.10,0.85,0.10
inst kick   wave=sine    vol=0.14 pan=0.0  adsr=0.002,0.05,0.10,0.02 freq=130Hz->36Hz

pattern motif      = A4:8 C5:8 E5:8 <G5:8 A5:8>
pattern arp_cell   = (A3:8 E4:8 A4:8 C5:8)@fast=2
pattern slow_pad   = ([A2 E3 A3 C4]:2 [G2 D3 G3 B3]:2)@slow=2
pattern euclid_drm = kick(3,8):2 (kick:2)@euclid=5,8

track ch1_violin violin: (motif * 2)@crescendo@legato | (motif * 2)@diminuendo@staccato
track ch2_harp   harp:   (arp_cell * 4)@fade_in@pan=-0.6->0.6 | (arp_cell * 4)@fade_out@pizzicato
track ch3_pad    pad:    slow_pad@swell@lpf=0.35
track ch4_drums:         euclid_drm@mp->f | euclid_drm@fade_out
`
	expScore, err := ParseDSL(expressiveDSL)
	if err != nil {
		t.Fatalf("ParseDSL(expressiveDSL) failed: %v", err)
	}
	if math.Abs(expScore.BPM-138.0) > 1e-6 {
		t.Fatalf("expected tempo allegro = 138 BPM, got %v", expScore.BPM)
	}
	// Verify <G5:8 A5:8> alternated on cycle 0 vs cycle 1 in ch1_violin
	ch1Events := expScore.Tracks[0].Events
	if len(ch1Events) != 16 {
		t.Fatalf("expected 16 events on ch1_violin, got %d", len(ch1Events))
	}
	g5Freq, _ := PitchToFreq("G5")
	a5Freq, _ := PitchToFreq("A5")
	if math.Abs(ch1Events[3].Pitches[0].StartFreq-g5Freq) > 1e-3 || math.Abs(ch1Events[7].Pitches[0].StartFreq-a5Freq) > 1e-3 {
		t.Fatalf("cycle alternation <G5:8 A5:8> failed: got %.2fHz and %.2fHz, want %.2fHz and %.2fHz",
			ch1Events[3].Pitches[0].StartFreq, ch1Events[7].Pitches[0].StartFreq, g5Freq, a5Freq)
	}
	// Verify @crescendo ramped GainStart -> GainEnd across the 8-note segment
	if !(ch1Events[0].GainStart < ch1Events[7].GainEnd) {
		t.Fatalf("expected crescendo gain ramp across ch1_violin segment: start=%v, end=%v",
			ch1Events[0].GainStart, ch1Events[7].GainEnd)
	}
	// Verify all 4 tracks compile to the exact same byte length
	var refLen int
	for idx, tr := range expScore.Tracks {
		pcm := synthesizeTrackEvents(tr.Events)
		if idx == 0 {
			refLen = len(pcm)
		} else if len(pcm) != refLen {
			t.Fatalf("track %q length %d != refLen %d", tr.Name, len(pcm), refLen)
		}
	}
}

func TestGroundZero56BarScore(t *testing.T) {
	score, err := LoadDSLFile("ground_zero.music")
	if err != nil {
		t.Fatalf("LoadDSLFile(ground_zero.music) failed: %v", err)
	}
	if err := ValidateProductionBGM(score, 11, 140.0); err != nil {
		t.Fatalf("ValidateProductionBGM(ground_zero.music) failed: %v", err)
	}
	pcm, err := SynthesizeScore(score)
	if err != nil {
		t.Fatalf("SynthesizeScore(ground_zero.music) failed: %v", err)
	}
	expectedBytes := 140 * BytesPerSecond
	if len(pcm) != expectedBytes {
		t.Fatalf("expected 140.00s PCM (%d bytes), got %d bytes", expectedBytes, len(pcm))
	}
}

func TestAppleHighFidelitySynthesis(t *testing.T) {
	const appleDSL = `
title "Apple CoreAudio High-Fidelity Test"
type song
synth apple
tempo andantino 96
time 4/4

inst lead  gm=violin            vol=0.14 pan=-0.15
inst ep    gm=epiano1           vol=0.10 pan=0.20
inst pad   gm=string_ensemble_1 vol=0.08 pan=0.00
inst bass  gm=synth_bass_1      vol=0.12 pan=0.00
inst kick  drum_note=kick       vol=0.14
inst snare drum_note=snare      vol=0.10
inst hat   drum_note=hat        vol=0.06

track ch1_lead lead: (G4:2 C5:8. G4:8. E5:8)@swell
track ch2_ep   ep:   [C3 E3 G3 C4]:2 [C3 E3 G3 C4]:2
track ch3_pad  pad:  ([C3 G3 C4 E4]:1)@fade_in
track ch4_bass bass: C2:8. C2:16 R:8 C2:8 R:8 C2:8 G1:8 C2:8
track ch5_drm:       kick:4 snare:4 kick:8 kick:8 snare:4
track ch6_hat:       (hat:8)*8
`
	score, err := ParseDSL(appleDSL)
	if err != nil {
		t.Fatalf("ParseDSL(appleDSL) failed: %v", err)
	}
	if score.SynthEngine != "apple" {
		t.Fatalf("expected SynthEngine='apple', got %q", score.SynthEngine)
	}
	pcm, err := SynthesizeScore(score)
	if err != nil {
		t.Fatalf("SynthesizeScore(appleDSL) failed: %v", err)
	}
	if len(pcm) == 0 || len(pcm)%BytesPerFrame != 0 {
		t.Fatalf("invalid PCM length %d", len(pcm))
	}
	nonZero := 0
	for _, b := range pcm {
		if b != 0 {
			nonZero++
		}
	}
	if nonZero == 0 {
		t.Fatal("Apple synthesis produced all-zero PCM output")
	}
}

func TestYM2612SynthesisAndDrumDecayHygiene(t *testing.T) {
	// 1. Verify native 4-op YM2612 + SN76489 PSG synthesis (electric guitar lead, rhythm guitar, FM bass, DAC drums)
	const ym2612DSL = `
title "SEGA Mega Drive YM2612 Electric Guitar & FM Bass Test"
type song
tempo andantino 96
time 4/4

inst gtr_lead wave=ym2612_guitar        gm=overdriven_guitar vol=0.16 pan=-0.12 adsr=0.004,0.12,0.88,0.08 vib=5.5,0.20
inst gtr_rhy  wave=ym2612_rhythm_guitar gm=distortion_guitar vol=0.10 pan=0.38  adsr=0.005,0.12,0.82,0.09
inst fm_brass wave=ym2612_brass         gm=brass_section     vol=0.09 pan=0.20  adsr=0.035,0.18,0.84,0.16
inst fm_ep    wave=ym2612_epiano        gm=epiano1           vol=0.10 pan=-0.25 adsr=0.003,0.22,0.55,0.10
inst psg      wave=psg_arp              gm=orchestral_harp   vol=0.07 pan=-0.45 adsr=0.002,0.08,0.38,0.04
inst fm_bass  wave=ym2612_bass          gm=electric_bass     vol=0.16 pan=0.00  adsr=0.002,0.09,0.74,0.04
inst kick     wave=ym2612_kick          gm_drum=kick         vol=0.18 pan=0.00  adsr=0.001,0.09,0.25,0.04 freq=165Hz->38Hz
inst snare    wave=ym2612_snare         gm_drum=snare        vol=0.14 pan=0.08  adsr=0.001,0.08,0.12,0.04

track ch1_lead  gtr_lead: E5:4 E5:4 C5:8. G4:8. E5:8
track ch2_rhy   gtr_rhy:  E4:4 E4:4 C4:8. G3:8. E4:8
track ch3_brass fm_brass: [C3 G3 C4 E4]:1
track ch4_ep    fm_ep:    [C3 E3 G3 C4]:2 [C3 E3 G3 C4]:2
track ch5_psg   psg:      (C3:16 G3:16 C4:16 G4:16)*4
track ch6_bass  fm_bass:  (C2:16 C3:16)*8
track ch7_drm:            kick:4 snare:4 kick:8 kick:8 snare:4
`
	score, err := ParseDSL(ym2612DSL)
	if err != nil {
		t.Fatalf("ParseDSL(ym2612DSL) failed: %v", err)
	}
	if err := ValidateScoreTheory(score); err != nil {
		t.Fatalf("ValidateScoreTheory(ym2612DSL) failed: %v", err)
	}

	// Render with default (non-Apple) YM2612 engine
	pcmDefault, err := SynthesizeScore(score)
	if err != nil {
		t.Fatalf("SynthesizeScore(ym2612DSL) failed: %v", err)
	}
	if len(pcmDefault) == 0 || len(pcmDefault)%BytesPerFrame != 0 {
		t.Fatalf("invalid default YM2612 PCM length %d", len(pcmDefault))
	}

	// Render with Apple CoreAudio real instruments (-apple)
	scoreApple := *score
	scoreApple.SynthEngine = "apple"
	pcmApple, err := SynthesizeScore(&scoreApple)
	if err != nil {
		t.Fatalf("SynthesizeScoreApple(ym2612DSL) failed: %v", err)
	}
	if len(pcmApple) != len(pcmDefault) {
		t.Fatalf("Apple PCM length %d != Default PCM length %d", len(pcmApple), len(pcmDefault))
	}

	// Verify Non-Apple and Apple produce distinct timbral waveforms (not spectrally cloned)
	var dot, sumDefSq, sumAppSq float64
	numFrames := len(pcmDefault) / BytesPerFrame
	for i := 0; i < numFrames; i++ {
		idx := i * BytesPerFrame
		dl := float64(int16(uint16(pcmDefault[idx])|(uint16(pcmDefault[idx+1])<<8))) / 32768.0
		al := float64(int16(uint16(pcmApple[idx])|(uint16(pcmApple[idx+1])<<8))) / 32768.0
		dot += dl * al
		sumDefSq += dl * dl
		sumAppSq += al * al
	}
	corr := math.Abs(dot / math.Sqrt(sumDefSq*sumAppSq))
	if corr > 0.50 {
		t.Fatalf("expected Non-Apple and Apple waveforms to have distinct timbres (|r| <= 0.50), got |r| = %.4f", corr)
	}

	// 2. Verify percussion decay hygiene: hat, open_hat, and snare must decay cleanly with zero stationary noise tail
	drumWaves := []string{"ym2612_hat", "ym2612_open_hat", "ym2612_snare"}
	for _, dw := range drumWaves {
		ev := NoteEvent{
			Inst: Instrument{
				Name:     dw,
				WaveType: dw,
				Volume:   0.5,
				Attack:   0.001,
				Decay:    0.08,
				Sustain:  0.50,
				Release:  0.04,
			},
			Pitches:     []PitchSweep{{StartFreq: 440, EndFreq: 440}},
			DurationSec: 0.40,
		}
		numSamp := int(0.40 * SampleRate)
		buf := make([]byte, numSamp*BytesPerFrame)
		renderNoteEventInto(buf, numSamp, ev, 42)

		// Compare attack RMS [0..30ms] vs late tail RMS [250..350ms]
		aEnd := int(0.03 * SampleRate)
		tStart := int(0.25 * SampleRate)
		tEnd := int(0.35 * SampleRate)
		var sumAttackSq, sumTailSq float64
		for i := 0; i < aEnd; i++ {
			s := float64(int16(uint16(buf[i*4])|(uint16(buf[i*4+1])<<8))) / 32768.0
			sumAttackSq += s * s
		}
		for i := tStart; i < tEnd; i++ {
			s := float64(int16(uint16(buf[i*4])|(uint16(buf[i*4+1])<<8))) / 32768.0
			sumTailSq += s * s
		}
		rmsAttack := math.Sqrt(sumAttackSq / float64(aEnd))
		rmsTail := math.Sqrt(sumTailSq / float64(tEnd-tStart))
		if rmsTail > rmsAttack*0.12 {
			t.Fatalf("drum %s has stationary noise tail: attackRMS=%.4f, tailRMS=%.4f (want < 12%% of attack)", dw, rmsAttack, rmsTail)
		}
	}

	// 3. Verify every hardware YM2612 patch is both harmonically rich (authentic OPN2 FM sidebands)
	// and strictly periodic (zero chaotic feedback noise across bass, mid, and high registers).
	testNotes := []struct {
		patchKey string
		freq     float64
	}{
		{"ym2612_guitar", 329.63},        // E4 lead guitar
		{"ym2612_guitar", 659.25},        // E5 high screaming guitar
		{"ym2612_rhythm_guitar", 164.81}, // E3 power-chord rhythm guitar
		{"ym2612_bass", 82.41},           // E2 FM synth bass
		{"ym2612_slap_bass", 98.00},      // G2 slap bass
		{"ym2612_brass", 261.63},         // C4 polysynth brass
		{"ym2612_epiano", 440.00},        // A4 DX electric piano
		{"ym2612_strings", 329.63},       // E4 string ensemble
		{"ym2612_choir", 261.63},         // C4 FM choir
		{"ym2612_flute", 523.25},         // C5 shakuhachi flute
		{"ym2612_bell", 587.33},          // D5 metallic chime
	}

	for _, tc := range testNotes {
		patch, ok := LookupYM2612Patch(tc.patchKey)
		if !ok {
			t.Fatalf("LookupYM2612Patch(%q) not found", tc.patchKey)
		}
		var st ym2612VoiceState
		const dur = 0.60
		n := int(dur * float64(SampleRate))
		samples := make([]float64, n)
		for i := 0; i < n; i++ {
			tm := float64(i) / float64(SampleRate)
			samples[i] = stepYM2612Voice(&st, patch, tc.freq, tm, dur, 0)
		}
		// Measure steady-state sustain window [0.20s .. 0.45s]
		s0 := int(0.20 * float64(SampleRate))
		s1 := int(0.45 * float64(SampleRate))
		var sumSq float64
		for i := s0; i < s1; i++ {
			sumSq += samples[i] * samples[i]
		}
		rms := math.Sqrt(sumSq / float64(s1-s0))
		if rms < 0.08 {
			t.Fatalf("patch %s @ %.1fHz has too low sustain RMS %.4f", tc.patchKey, tc.freq, rms)
		}
		// Autocorrelation at fundamental period lag = round(SampleRate / freq)
		lag := int(math.Round(float64(SampleRate) / tc.freq))
		var bestCorr float64
		for dl := -2; dl <= 2; dl++ {
			l := lag + dl
			var num, d0, d1 float64
			for i := s0; i < s1-l; i++ {
				a := samples[i]
				b := samples[i+l]
				num += a * b
				d0 += a * a
				d1 += b * b
			}
			if d0 > 0 && d1 > 0 {
				c := num / math.Sqrt(d0*d1)
				if c > bestCorr {
					bestCorr = c
				}
			}
		}
		if bestCorr < 0.94 {
			t.Fatalf("patch %s @ %.1fHz failed periodicity check (autocorrelation r=%.4f < 0.94; possible FM feedback noise)", tc.patchKey, tc.freq, bestCorr)
		}
	}
}

func TestFourClassicalMegaDriveReproductions(t *testing.T) {
	songs := []struct {
		file      string
		minDurSec float64
		wantTrks  int
	}{
		{"gaiares_level2.music", 130.0, 11},
		{"bare_knuckle_intro.music", 98.0, 11},
		{"shinobi2_stage2.music", 156.0, 11},
		{"elemental_master_stage1.music", 131.0, 11},
	}

	for _, tc := range songs {
		t.Run(tc.file, func(t *testing.T) {
			score, err := LoadDSLFile(tc.file)
			if err != nil {
				t.Fatalf("LoadDSLFile(%s) failed: %v", tc.file, err)
			}
			if err := ValidateProductionBGM(score, tc.wantTrks, tc.minDurSec); err != nil {
				t.Fatalf("ValidateProductionBGM(%s) failed: %v", tc.file, err)
			}
			if len(score.Tracks) != tc.wantTrks {
				t.Fatalf("%s: got %d tracks, want %d", tc.file, len(score.Tracks), tc.wantTrks)
			}
		})
	}
}

func TestSimplifiedDSLTiesGroupsBarlinesAndArchetypes(t *testing.T) {
	// 1. Exact 64-bit rational GCD-reduced ~ tied durations must match fractional equivalents with 0 ULP diff
	tieCases := []struct {
		tied string
		frac string
		bpm  float64
	}{
		{"1~1", "32/16", 100},
		{"2.~8.", "15/16", 96},
		{"4.~16", "7/16", 134},
		{"1~1~4t", "104/48", 100},
		{"1~2.~16t", "86/48", 100},
		{"8~8t", "10/48", 100},
	}
	for _, tc := range tieCases {
		dTied, err := ParseDuration(tc.tied, tc.bpm)
		if err != nil {
			t.Fatalf("ParseDuration(%q, %v) failed: %v", tc.tied, tc.bpm, err)
		}
		dFrac, err := ParseDuration(tc.frac, tc.bpm)
		if err != nil {
			t.Fatalf("ParseDuration(%q, %v) failed: %v", tc.frac, tc.bpm, err)
		}
		if dTied != dFrac {
			t.Fatalf("ParseDuration(%q) = %.17g != ParseDuration(%q) = %.17g at BPM %v", tc.tied, dTied, tc.frac, dFrac, tc.bpm)
		}
	}

	// 2. Cross-barline ties (F5:8~ | F5:16 and shorthand F5:8~ | :16), group-scoped (:dur),
	//    sticky running durations, archetype defaults, and pre-seeded 8-piece drum kit
	const simplifiedDSL = `
title "Simplified DSL Features Test"
type sfx
tempo moderato 100
time 4/4

inst brass wave=ym2612_brass pan=-0.18
inst bass  wave=ym2612_slap_bass

pattern hook = A4:8 E5:8.*2 F5*2 F5:8~ | :16 R:16 D5:8.*2 G5*2 G5:8 |
pattern fill = R:2. (snare*3 kick):16 |

track ch1 brass: hook
track ch2 bass:  (A1 G1 A1 E2):16*4 | A1:8. A1:8. A1:4 A1:4. |
track ch3:       kick:8. kick:16 snare:8 kick:4 kick:8 snare:4 | fill
`
	score, err := ParseDSL(simplifiedDSL)
	if err != nil {
		t.Fatalf("ParseDSL(simplifiedDSL) failed: %v", err)
	}
	// Verify archetype defaults populated brass and bass
	brassInst := score.Instruments["brass"]
	if brassInst.LPF != 0.36 || brassInst.VibratoFreq != 4.8 || ResolveGMProgram(brassInst) != 61 {
		t.Fatalf("unexpected ym2612_brass archetype defaults: %+v (GM=%d)", brassInst, ResolveGMProgram(brassInst))
	}
	// Verify cross-barline tie F5:8~ | :16 merged into a single F5:8. (0.45s at 100 BPM) event
	ch1Evs := score.Tracks[0].Events
	if len(ch1Evs) != 12 {
		t.Fatalf("expected 12 events in ch1 hook (with merged cross-bar F5), got %d", len(ch1Evs))
	}
	wantDottedEighth, _ := ParseDuration("8.", 100)
	if math.Abs(ch1Evs[5].DurationSec-wantDottedEighth) > 1e-9 {
		t.Fatalf("expected cross-bar tied F5 duration %.6fs (8.), got %.6fs", wantDottedEighth, ch1Evs[5].DurationSec)
	}

	// 3. Fail-fast on cross-barline pitch mismatch and mid-bar '|' misalignment
	const badTiePitchDSL = `
tempo 120
time 4/4
inst lead wave=ym2612_brass
track ch1 lead: C4:2. F5:8~ | G5:16 R:16 G4:2. |
`
	if _, err := ParseDSL(badTiePitchDSL); err == nil {
		t.Fatal("expected error for cross-barline tie pitch mismatch (F5:8~ | G5:16), got nil")
	}

	const misalignedBarlineDSL = `
tempo 120
time 4/4
inst lead wave=ym2612_brass
track ch1 lead: C4:2. E4:8. | G4:16 C5:1
`
	if _, err := ParseDSL(misalignedBarlineDSL); err == nil {
		t.Fatal("expected error for misaligned '|' barline at 3.75 beats (15/16) in 4/4, got nil")
	}
}

func TestMutedMelodicAndDrumTracks(t *testing.T) {
	const mutedMusicDSL = `
title "Muted Tracks Test"
type song
tempo 120
time 4/4

inst lead  wave=ym2612_brass vol=0
inst drums wave=kick         vol=0

pattern p_lead  = C5:4 E5:4 G5:4 C6:4 |
pattern p_drums = kick:4 snare:4 hat:4 crash:4 |

track ch01 lead:  p_lead
track ch02 drums: p_drums
`
	pcm, err := CompileDSL(mutedMusicDSL)
	if err != nil {
		t.Fatalf("CompileDSL(mutedMusicDSL) failed: %v", err)
	}
	if len(pcm) == 0 || len(pcm)%4 != 0 {
		t.Fatalf("expected non-empty 4-byte aligned PCM, got %d bytes", len(pcm))
	}
	for i, b := range pcm {
		if b != 0 {
			t.Fatalf("expected silence for vol=0 tracks at byte %d, got %d", i, b)
		}
	}
}





