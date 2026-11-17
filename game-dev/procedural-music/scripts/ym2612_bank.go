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
	"math"
	"math/rand/v2"
	"strings"
)

// YM2612Operator models the hardware registers of one FM operator in a Yamaha YM2612 (OPN2) channel.
// Register semantics match Nuked-OPN2 (ym3438.c) and Genesis Plus GX (ym2612.c):
//   - DT  (Detune, 0..7): 0..3 = positive hardware detune, 4..7 = negative hardware detune
//   - MUL (Multiple, 0..15): 0 = 0.5x frequency, 1..15 = 1x..15x frequency
//   - TL  (Total Level, 0..127): 7-bit attenuation in 0.75 dB steps (0 = 0 dB peak, 16 = -12 dB / 2*pi rad mod, 24 = -18 dB / pi rad mod)
//   - RS  (Rate Scaling / Key Scale, 0..3): shifts keyCode right by (3 - RS) to speed up envelopes on higher notes
//   - AR  (Attack Rate, 0..31): 5-bit attack rate (31 = instantaneous 0-sample hardware key-on)
//   - D1R (Decay 1 Rate, 0..31): 5-bit primary decay rate from peak (0) down to SL
//   - SL  (Sustain Level, 0..15): 4-bit sustain threshold in 3 dB steps (SL << 5 in 10-bit EG attenuation; 15 maps to 992 = -93 dB)
//   - D2R (Decay 2 / Sustain Rate, 0..31): 5-bit secondary decay rate during held sustain (0 = flat infinite sustain plateau)
//   - RR  (Release Rate, 0..15): 4-bit release rate after key-off (mapped to 5-bit rate (RR<<1)+1)
type YM2612Operator struct {
	DT  uint8
	MUL uint8
	TL  uint8
	RS  uint8
	AR  uint8
	D1R uint8
	SL  uint8
	D2R uint8
	RR  uint8
}

// YM2612Patch defines a 4-operator Yamaha YM2612 (OPN2) hardware register patch or TI SN76489 PSG voice.
// Operator indices Op[0..3] correspond to schematic Operators 1, 2, 3, 4.
type YM2612Patch struct {
	Name    string
	ALG     uint8   // Hardware algorithm 0..7
	FB      uint8   // Operator 1 self-feedback shift register 0..7 (0 = off, 1..7 = (op1Prev0+op1Prev1) >> (11-FB))
	Gain    float64 // Post-accumulator output level trim (default 1.0)
	IsPSG   bool    // True for TI SN76489 PSG square/pulse channels
	PSGDuty float64 // PSG pulse duty cycle (0.50 = square, 0.25 = pulse arp)
	Op      [4]YM2612Operator
}

// YM2612 hardware silicon lookup tables (exact Nuked-OPN2 ym3438.c / Genesis Plus GX ym2612.c ROM tables):
//   - ym2612LogSinTable: 256-entry 12-bit quarter-wave log2(sin) attenuation table (4.8 fixed-point)
//   - ym2612ExpTable:    256-entry 11-bit base-2 exponential table (10-bit mantissa)
//   - ym2612DetuneTable: 4x8 hardware phase detune increment table indexed by [DT&3][keyCode>>2]
//   - ym2612EGIncTable:  64x8 hardware 10-bit envelope generator increment table
var (
	ym2612LogSinTable [256]uint16
	ym2612ExpTable    [256]uint16
)

var ym2612DetuneTable = [4][8]int32{
	{0, 0, 0, 0, 0, 0, 0, 0},
	{0, 0, 1, 1, 1, 1, 2, 2},
	{0, 1, 1, 2, 2, 3, 4, 5},
	{0, 1, 2, 2, 3, 4, 6, 8},
}

var ym2612EGIncTable = [64][8]uint8{
	// Rates 0..3: frozen (zero increment)
	{0, 0, 0, 0, 0, 0, 0, 0}, {0, 0, 0, 0, 0, 0, 0, 0}, {0, 0, 0, 0, 0, 0, 0, 0}, {0, 0, 0, 0, 0, 0, 0, 0},
	// Rates 4..47: standard 4-substep cycle pattern (0, +1/4, +2/4, +3/4)
	{0, 1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 1, 1, 0, 1}, {0, 1, 1, 1, 0, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 1, 1},
	{0, 1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 1, 1, 0, 1}, {0, 1, 1, 1, 0, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 1, 1},
	{0, 1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 1, 1, 0, 1}, {0, 1, 1, 1, 0, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 1, 1},
	{0, 1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 1, 1, 0, 1}, {0, 1, 1, 1, 0, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 1, 1},
	{0, 1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 1, 1, 0, 1}, {0, 1, 1, 1, 0, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 1, 1},
	{0, 1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 1, 1, 0, 1}, {0, 1, 1, 1, 0, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 1, 1},
	{0, 1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 1, 1, 0, 1}, {0, 1, 1, 1, 0, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 1, 1},
	{0, 1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 1, 1, 0, 1}, {0, 1, 1, 1, 0, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 1, 1},
	{0, 1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 1, 1, 0, 1}, {0, 1, 1, 1, 0, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 1, 1},
	{0, 1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 1, 1, 0, 1}, {0, 1, 1, 1, 0, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 1, 1},
	{0, 1, 0, 1, 0, 1, 0, 1}, {0, 1, 0, 1, 1, 1, 0, 1}, {0, 1, 1, 1, 0, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 1, 1},
	// Rates 48..51
	{1, 1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 2, 1, 1, 1, 2}, {1, 2, 1, 2, 1, 2, 1, 2}, {1, 2, 2, 2, 1, 2, 2, 2},
	// Rates 52..55
	{2, 2, 2, 2, 2, 2, 2, 2}, {2, 2, 2, 4, 2, 2, 2, 4}, {2, 4, 2, 4, 2, 4, 2, 4}, {2, 4, 4, 4, 2, 4, 4, 4},
	// Rates 56..59
	{4, 4, 4, 4, 4, 4, 4, 4}, {4, 4, 4, 8, 4, 4, 4, 8}, {4, 8, 4, 8, 4, 8, 4, 8}, {4, 8, 8, 8, 4, 8, 8, 8},
	// Rates 60..63
	{8, 8, 8, 8, 8, 8, 8, 8}, {8, 8, 8, 8, 8, 8, 8, 8}, {8, 8, 8, 8, 8, 8, 8, 8}, {8, 8, 8, 8, 8, 8, 8, 8},
}

func init() {
	for i := 0; i < 256; i++ {
		s := math.Sin((float64(i) + 0.5) * math.Pi / 512.0)
		ym2612LogSinTable[i] = uint16(math.Round(-math.Log2(s) * 256.0))
		ym2612ExpTable[i] = uint16(math.Round((math.Pow(2.0, float64(255-i)/256.0) - 1.0) * 1024.0))
	}
}

const (
	ym2612EGAttack uint8 = iota
	ym2612EGDecay1
	ym2612EGSustain
	ym2612EGRelease
)

// ym2612VoiceState maintains the hardware register state of one 4-operator YM2612 channel.
type ym2612VoiceState struct {
	initialized bool
	inRelease   bool
	egClockAcc  uint32
	egTimer     uint32
	phase20     [4]uint32
	egAtten     [4]int32
	egState     [4]uint8
	op1Prev0    int32
	op1Prev1    int32
	model1LPF   float64
}

// freqToYM2612FNumBlockKeyCode converts a frequency in Hz into YM2612 11-bit F-Number (0..2047),
// 3-bit Octave Block (0..7), and 5-bit Key-Code (block<<2 | fnumNoteBits) for rate scaling and detune.
func freqToYM2612FNumBlockKeyCode(freq float64) (fnum uint32, block uint8, keyCode uint8) {
	if freq <= 1.0 {
		return 0, 0, 0
	}
	block = 0
	for block < 7 {
		fn := freq * float64(uint32(1)<<(21-block)) / float64(SampleRate)
		if fn < 2047.0 {
			break
		}
		block++
	}
	fn := uint32(math.Round(freq * float64(uint32(1)<<(21-block)) / float64(SampleRate)))
	if fn > 2047 {
		fn = 2047
	}
	// YM2612 Key-Code (KC) bits [1:0] derived from F-Number bits [10:7] per OPN2 silicon manual
	b10 := (fn >> 10) & 1
	b9 := (fn >> 9) & 1
	b8 := (fn >> 8) & 1
	b7 := (fn >> 7) & 1
	var n2 uint32
	if b10 != 0 && (b9 != 0 || b8 != 0 || b7 != 0) {
		n2 = 3
	} else if b10 != 0 {
		n2 = 2
	} else if b9 != 0 && (b8 != 0 || b7 != 0) {
		n2 = 1
	}
	keyCode = (block << 2) | uint8(n2)
	return fn, block, keyCode
}

func calcYM2612EGRate(baseRate5, rs, keyCode uint8) uint8 {
	if baseRate5 == 0 {
		return 0
	}
	ks := keyCode >> (3 - (rs & 3))
	r := int(baseRate5)*2 + int(ks)
	if r > 63 {
		r = 63
	}
	return uint8(r)
}

func ym2612SLToAtten10(sl uint8) int32 {
	if sl >= 15 {
		return 31 << 5 // 992 (-93 dB)
	}
	return int32(sl) << 5
}

func initYM2612VoiceState(st *ym2612VoiceState, patch YM2612Patch, keyCode uint8) {
	st.initialized = true
	st.inRelease = false
	for k := 0; k < 4; k++ {
		op := patch.Op[k]
		ar := calcYM2612EGRate(op.AR, op.RS, keyCode)
		if ar >= 62 {
			// Hardware instantaneous attack when effective rate >= 62 (e.g. AR=31)
			st.egAtten[k] = 0
			if ym2612SLToAtten10(op.SL) == 0 {
				st.egState[k] = ym2612EGSustain
			} else {
				st.egState[k] = ym2612EGDecay1
			}
		} else {
			st.egAtten[k] = 1023
			st.egState[k] = ym2612EGAttack
		}
	}
}

func stepYM2612EG(st *ym2612VoiceState, patch YM2612Patch, keyCode uint8) {
	st.egTimer = (st.egTimer + 1) & 0xFFF
	for k := 0; k < 4; k++ {
		op := patch.Op[k]
		var rate uint8
		switch st.egState[k] {
		case ym2612EGAttack:
			rate = calcYM2612EGRate(op.AR, op.RS, keyCode)
		case ym2612EGDecay1:
			slAtten := ym2612SLToAtten10(op.SL)
			if st.egAtten[k] >= slAtten {
				st.egState[k] = ym2612EGSustain
				rate = calcYM2612EGRate(op.D2R, op.RS, keyCode)
			} else {
				rate = calcYM2612EGRate(op.D1R, op.RS, keyCode)
			}
		case ym2612EGSustain:
			rate = calcYM2612EGRate(op.D2R, op.RS, keyCode)
		case ym2612EGRelease:
			rate = calcYM2612EGRate((op.RR<<1)+1, op.RS, keyCode)
		}
		if rate < 4 {
			continue
		}
		var shift uint
		if rate < 48 {
			shift = uint(12 - (rate >> 2))
		}
		mask := (uint32(1) << shift) - 1
		if (st.egTimer & mask) != 0 {
			continue
		}
		cycle := (st.egTimer >> shift) & 7
		inc := int32(ym2612EGIncTable[rate][cycle])
		if inc == 0 {
			continue
		}
		if st.egState[k] == ym2612EGAttack {
			st.egAtten[k] += ((^st.egAtten[k]) * inc) >> 4
			if st.egAtten[k] <= 0 {
				st.egAtten[k] = 0
				if ym2612SLToAtten10(op.SL) == 0 {
					st.egState[k] = ym2612EGSustain
				} else {
					st.egState[k] = ym2612EGDecay1
				}
			}
		} else {
			st.egAtten[k] += inc
			if st.egState[k] == ym2612EGDecay1 {
				slAtten := ym2612SLToAtten10(op.SL)
				if st.egAtten[k] >= slAtten {
					st.egAtten[k] = slAtten
					st.egState[k] = ym2612EGSustain
				}
			}
			if st.egAtten[k] > 1023 {
				st.egAtten[k] = 1023
			}
		}
	}
}

// evalYM2612Operator evaluates the YM2612 14-bit signed operator output (-8176..+8176)
// from a 10-bit phase (0..1023) and a 10-bit envelope + Total Level attenuation (0..1023)
// using the hardware logsin and exp ROM lookup tables.
func evalYM2612Operator(phase10 uint16, envAtten10 int32) int32 {
	if envAtten10 >= 1020 {
		return 0
	}
	if envAtten10 < 0 {
		envAtten10 = 0
	}
	p := phase10 & 0x3FF
	sign := p & 0x200
	mirror := p & 0x100
	x := p & 0xFF
	if mirror != 0 {
		x = ^x & 0xFF
	}
	sinAtten12 := uint32(ym2612LogSinTable[x])
	totalAtten := sinAtten12 + (uint32(envAtten10) << 2)
	if totalAtten >= 4096 {
		return 0
	}
	mantissa := uint32(ym2612ExpTable[totalAtten&0xFF])
	shift := totalAtten >> 8
	mag13 := int32(((mantissa + 1024) << 2) >> shift)
	if sign != 0 {
		return -mag13
	}
	return mag13
}

func clampYM2612Accum14(v int32) int32 {
	if v > 8191 {
		return 8191
	}
	if v < -8192 {
		return -8192
	}
	return v
}

// polyBLEP computes a polynomial band-limited step correction around phase discontinuities
// at t=0 and t=duty, eliminating ultrasonic square/pulse wave aliasing in SN76489 PSG channels.
func polyBLEP(t, dt float64) float64 {
	if dt <= 0 {
		return 0
	}
	if t < dt {
		u := t / dt
		return u + u - u*u - 1.0
	}
	if t > 1.0-dt {
		u := (t - 1.0) / dt
		return u*u + u + u + 1.0
	}
	return 0
}

// ym2612PatchCatalog contains authentic SEGA Mega Drive YM2612 (OPN2) hardware register patches
// modeled after classic soundtracks (Shinobi III: Return of the Ninja Master, Thunder Force IV,
// Streets of Rage 2, and Comix Zone) alongside TI SN76489 PSG square/pulse channels.
// Multi-carrier algorithms (ALG 4 and ALG 5) have carrier TLs calibrated so their summed peak
// never clips the 14-bit signed accumulator (±8191).
var ym2612PatchCatalog = map[string]YM2612Patch{
	// 1. SEARING YM2612 FM OVERDRIVEN ELECTRIC GUITAR LEAD (Shinobi III "Ground Zero" signature lead)
	// Hardware Algorithm 2: (Op1(fb) + (Op2 -> Op3)) -> Op4(carrier).
	"ym2612_guitar": {
		Name: "ym2612_guitar",
		ALG:  2,
		FB:   5,
		Gain: 1.24,
		Op: [4]YM2612Operator{
			// Op1: Warm sawtooth driver into Op4 (1x, DT=+2, TL=17)
			{DT: 2, MUL: 1, TL: 17, RS: 1, AR: 31, D1R: 7, SL: 2, D2R: 1, RR: 8},
			// Op2: Harmonic bite modulator into Op3 (2x, DT=-1, TL=20)
			{DT: 5, MUL: 2, TL: 20, RS: 1, AR: 31, D1R: 9, SL: 2, D2R: 2, RR: 8},
			// Op3: Warm humbucker fundamental body modulator into Op4 (1x, DT=+1, TL=18)
			{DT: 1, MUL: 1, TL: 18, RS: 1, AR: 31, D1R: 8, SL: 2, D2R: 1, RR: 8},
			// Op4: Primary 14-bit guitar carrier (1x, DT=0, TL=1)
			{DT: 0, MUL: 1, TL: 1, RS: 1, AR: 31, D1R: 6, SL: 1, D2R: 1, RR: 7},
		},
	},

	// 2. CHUNKY YM2612 RHYTHM / POWER-CHORD ELECTRIC GUITAR (Double-tracked Algorithm 4)
	// Hardware Algorithm 4: (Op1(fb) -> Op2) + (Op3 -> Op4).
	// Carrier TLs (TL=7 and TL=9) sum to 7,796 <= 8,191 so dual stacks never clip the 14-bit bus.
	"ym2612_rhythm_guitar": {
		Name: "ym2612_rhythm_guitar",
		ALG:  4,
		FB:   5,
		Gain: 1.18,
		Op: [4]YM2612Operator{
			// Stack 1: Fundamental sawtooth modulator -> carrier 1 (TL=7)
			{DT: 2, MUL: 1, TL: 17, RS: 1, AR: 31, D1R: 9, SL: 2, D2R: 2, RR: 8},
			{DT: 1, MUL: 1, TL: 7, RS: 1, AR: 31, D1R: 8, SL: 1, D2R: 2, RR: 8},
			// Stack 2: Detuned harmonic bite modulator -> carrier 2 (TL=9)
			{DT: 6, MUL: 2, TL: 19, RS: 1, AR: 31, D1R: 10, SL: 2, D2R: 2, RR: 8},
			{DT: 5, MUL: 1, TL: 9, RS: 1, AR: 31, D1R: 8, SL: 1, D2R: 2, RR: 8},
		},
	},

	// 3. HEAVY YM2612 4-OP FM SYNTH BASS (Shinobi III / Streets of Rage 2 punchy low-end FM bass)
	// Hardware Algorithm 2: (Op1(fb) + (Op2 -> Op3)) -> Op4(carrier).
	"ym2612_bass": {
		Name: "ym2612_bass",
		ALG:  2,
		FB:   5,
		Gain: 1.32,
		Op: [4]YM2612Operator{
			// Op1: Deep sub-fundamental sawtooth growl (1x, TL=19, SL=3)
			{DT: 1, MUL: 1, TL: 19, RS: 1, AR: 31, D1R: 13, SL: 3, D2R: 3, RR: 8},
			// Op2: Pluck transient (2x, TL: 25, fast D1R=19 -> SL=8)
			{DT: 2, MUL: 2, TL: 25, RS: 2, AR: 31, D1R: 19, SL: 8, D2R: 8, RR: 9},
			// Op3: Punchy fundamental bass driver (1x, TL=20, D1R=14 -> SL=4)
			{DT: 5, MUL: 1, TL: 20, RS: 1, AR: 31, D1R: 14, SL: 4, D2R: 4, RR: 8},
			// Op4: Fundamental bass carrier (1x, TL=0)
			{DT: 0, MUL: 1, TL: 0, RS: 1, AR: 31, D1R: 8, SL: 1, D2R: 1, RR: 8},
		},
	},

	// 4. YM2612 SLAP BASS (Crisp metallic thumb-pop FM bass)
	"ym2612_slap_bass": {
		Name: "ym2612_slap_bass",
		ALG:  2,
		FB:   5,
		Gain: 1.28,
		Op: [4]YM2612Operator{
			{DT: 2, MUL: 1, TL: 19, RS: 1, AR: 31, D1R: 14, SL: 3, D2R: 4, RR: 8},
			{DT: 3, MUL: 3, TL: 22, RS: 2, AR: 31, D1R: 21, SL: 9, D2R: 10, RR: 9},
			{DT: 5, MUL: 1, TL: 20, RS: 2, AR: 31, D1R: 16, SL: 4, D2R: 5, RR: 8},
			{DT: 0, MUL: 1, TL: 0, RS: 1, AR: 31, D1R: 10, SL: 1, D2R: 2, RR: 8},
		},
	},

	// 5. FAT YM2612 FM BRASS / POLYSYNTH PAD (Dual detuned 2-op stacks with AR=21 brass bloom)
	"ym2612_brass": {
		Name: "ym2612_brass",
		ALG:  4,
		FB:   5,
		Gain: 1.06,
		Op: [4]YM2612Operator{
			// Stack 1: Brass lip-buzz swell -> carrier 1 (TL=7)
			{DT: 2, MUL: 1, TL: 18, RS: 1, AR: 22, D1R: 8, SL: 2, D2R: 1, RR: 7},
			{DT: 0, MUL: 1, TL: 7, RS: 1, AR: 26, D1R: 8, SL: 1, D2R: 1, RR: 7},
			// Stack 2: Warm upper brass overtone -> carrier 2 (TL=9)
			{DT: 6, MUL: 2, TL: 20, RS: 1, AR: 21, D1R: 9, SL: 2, D2R: 1, RR: 7},
			{DT: 0, MUL: 1, TL: 9, RS: 1, AR: 25, D1R: 8, SL: 1, D2R: 1, RR: 7},
		},
	},

	// 6. CRYSTALLINE YM2612 4-OP FM ELECTRIC PIANO (Algorithm 4: Warm DX Rhodes body + 2x glassy tine)
	"ym2612_epiano": {
		Name: "ym2612_epiano",
		ALG:  4,
		FB:   4,
		Gain: 1.16,
		Op: [4]YM2612Operator{
			// Stack 1: Warm DX Rhodes body (1x -> 1x, carrier TL=6)
			{DT: 1, MUL: 1, TL: 21, RS: 1, AR: 31, D1R: 9, SL: 3, D2R: 2, RR: 7},
			{DT: 0, MUL: 1, TL: 6, RS: 1, AR: 31, D1R: 8, SL: 1, D2R: 2, RR: 7},
			// Stack 2: Warm bell tine overtone (2x -> 1x, carrier TL=10)
			{DT: 2, MUL: 2, TL: 21, RS: 1, AR: 31, D1R: 10, SL: 2, D2R: 2, RR: 8},
			{DT: 0, MUL: 1, TL: 10, RS: 1, AR: 31, D1R: 8, SL: 2, D2R: 2, RR: 7},
		},
	},

	// 7. LUSH YM2612 FM STRING ENSEMBLE (Algorithm 5: 1 bow modulator -> 3 detuned parallel carriers)
	// Carrier TLs (TL=10, TL=10, TL=16) sum to 7,732 <= 8,191 for zero accumulator clipping.
	"ym2612_strings": {
		Name: "ym2612_strings",
		ALG:  5,
		FB:   4,
		Gain: 1.05,
		Op: [4]YM2612Operator{
			{DT: 2, MUL: 1, TL: 22, RS: 1, AR: 18, D1R: 8, SL: 2, D2R: 1, RR: 6},
			{DT: 0, MUL: 1, TL: 10, RS: 1, AR: 19, D1R: 7, SL: 1, D2R: 1, RR: 6},
			{DT: 0, MUL: 1, TL: 10, RS: 1, AR: 18, D1R: 7, SL: 1, D2R: 1, RR: 6},
			{DT: 1, MUL: 2, TL: 16, RS: 1, AR: 17, D1R: 8, SL: 2, D2R: 1, RR: 6},
		},
	},

	// 8. YM2612 FM CHOIR / VOCAL PAD (Formant-tuned Algorithm 5)
	"ym2612_choir": {
		Name: "ym2612_choir",
		ALG:  5,
		FB:   4,
		Gain: 1.14,
		Op: [4]YM2612Operator{
			{DT: 1, MUL: 1, TL: 24, RS: 1, AR: 18, D1R: 8, SL: 2, D2R: 1, RR: 6},
			{DT: 5, MUL: 1, TL: 9, RS: 1, AR: 18, D1R: 7, SL: 1, D2R: 1, RR: 6},
			{DT: 2, MUL: 1, TL: 11, RS: 1, AR: 17, D1R: 8, SL: 2, D2R: 1, RR: 6},
			{DT: 6, MUL: 2, TL: 18, RS: 1, AR: 17, D1R: 9, SL: 2, D2R: 1, RR: 6},
		},
	},

	// 9. YM2612 FM FLUTE / SHAKUHACHI ECHO VOICE (Algorithm 4 with breath chiff transient)
	"ym2612_flute": {
		Name: "ym2612_flute",
		ALG:  4,
		FB:   4,
		Gain: 1.15,
		Op: [4]YM2612Operator{
			// Stack 1: Breathy overblown chiff attack (2x -> 1x, carrier TL=14)
			{DT: 3, MUL: 2, TL: 27, RS: 2, AR: 26, D1R: 18, SL: 6, D2R: 5, RR: 8},
			{DT: 1, MUL: 1, TL: 14, RS: 1, AR: 22, D1R: 12, SL: 3, D2R: 2, RR: 7},
			// Stack 2: Woody bamboo flute body (1x -> 1x, carrier TL=5)
			{DT: 5, MUL: 1, TL: 26, RS: 1, AR: 21, D1R: 10, SL: 3, D2R: 1, RR: 7},
			{DT: 0, MUL: 1, TL: 5, RS: 1, AR: 22, D1R: 8, SL: 1, D2R: 1, RR: 7},
		},
	},

	// 10. YM2612 FM METALLIC BELL / CHIME (Algorithm 4 chime ratios anchored on 1x fundamental)
	"ym2612_bell": {
		Name: "ym2612_bell",
		ALG:  4,
		FB:   4,
		Gain: 1.34,
		Op: [4]YM2612Operator{
			{DT: 3, MUL: 2, TL: 19, RS: 0, AR: 31, D1R: 6, SL: 1, D2R: 1, RR: 6},
			{DT: 3, MUL: 1, TL: 6, RS: 0, AR: 31, D1R: 5, SL: 1, D2R: 1, RR: 6},
			{DT: 7, MUL: 3, TL: 21, RS: 0, AR: 31, D1R: 7, SL: 1, D2R: 1, RR: 7},
			{DT: 7, MUL: 1, TL: 8, RS: 0, AR: 31, D1R: 5, SL: 1, D2R: 1, RR: 6},
		},
	},

	// 11. TI SN76489 PSG SQUARE / ARPEGGIO CHANNEL (Band-limited PolyBLEP square/pulse wave)
	"psg_square": {
		Name:    "psg_square",
		IsPSG:   true,
		PSGDuty: 0.50,
	},
	"psg_arp": {
		Name:    "psg_arp",
		IsPSG:   true,
		PSGDuty: 0.25,
	},
}

// LookupYM2612Patch resolves a wave type or instrument preset to a YM2612Patch if applicable.
func LookupYM2612Patch(waveType string) (YM2612Patch, bool) {
	switch strings.ToLower(strings.TrimSpace(waveType)) {
	case "ym2612_guitar", "overdriven_guitar", "distortion_guitar", "fm_guitar", "electric_guitar":
		return ym2612PatchCatalog["ym2612_guitar"], true
	case "ym2612_rhythm_guitar", "power_guitar", "rhythm_guitar", "muted_guitar":
		return ym2612PatchCatalog["ym2612_rhythm_guitar"], true
	case "ym2612_bass", "fm_bass", "synth_bass", "sub_bass":
		return ym2612PatchCatalog["ym2612_bass"], true
	case "ym2612_slap_bass", "slap_bass":
		return ym2612PatchCatalog["ym2612_slap_bass"], true
	case "ym2612_brass", "fm_brass", "synth_brass", "polysynth":
		return ym2612PatchCatalog["ym2612_brass"], true
	case "ym2612_epiano", "fm_epiano", "dx7":
		return ym2612PatchCatalog["ym2612_epiano"], true
	case "ym2612_strings", "fm_strings", "synth_strings":
		return ym2612PatchCatalog["ym2612_strings"], true
	case "ym2612_choir", "fm_choir", "ym2612_voice":
		return ym2612PatchCatalog["ym2612_choir"], true
	case "ym2612_flute", "fm_flute":
		return ym2612PatchCatalog["ym2612_flute"], true
	case "ym2612_bell", "fm_bell":
		return ym2612PatchCatalog["ym2612_bell"], true
	case "psg_square", "psg_pulse", "sn76489":
		return ym2612PatchCatalog["psg_square"], true
	case "psg_arp", "pulse":
		return ym2612PatchCatalog["psg_arp"], true
	default:
		return YM2612Patch{}, false
	}
}

// LookupYM2612PatchForInst resolves an Instrument to a YM2612Patch in the default (non-Apple) engine.
func LookupYM2612PatchForInst(inst Instrument) (YM2612Patch, bool) {
	if IsPercussionInstrument(inst) {
		return YM2612Patch{}, false
	}
	return LookupYM2612Patch(inst.WaveType)
}

// IsYM2612DrumWave returns true if the wave type is one of the dedicated Mega Drive YM2612 percussion voices.
func IsYM2612DrumWave(waveType string) bool {
	switch strings.ToLower(strings.TrimSpace(waveType)) {
	case "ym2612_kick", "ym2612_snare", "ym2612_tom", "ym2612_hat", "ym2612_open_hat", "ym2612_crash",
		"kick", "snare", "tom", "hat", "open_hat", "crash":
		return true
	default:
		return false
	}
}

// ResolveYM2612DrumWave returns the canonical YM2612 drum wave name for percussion instruments.
func ResolveYM2612DrumWave(inst Instrument) (string, bool) {
	switch strings.ToLower(strings.TrimSpace(inst.WaveType)) {
	case "ym2612_kick", "kick":
		return "ym2612_kick", true
	case "ym2612_snare", "snare":
		return "ym2612_snare", true
	case "ym2612_tom", "tom":
		return "ym2612_tom", true
	case "ym2612_hat", "hat":
		return "ym2612_hat", true
	case "ym2612_open_hat", "open_hat":
		return "ym2612_open_hat", true
	case "ym2612_crash", "crash":
		return "ym2612_crash", true
	default:
		return "", false
	}
}

// isYM2612Carrier returns true if operator k (0..3) is an audio-output carrier in the given YM2612 algorithm (0..7).
func isYM2612Carrier(alg uint8, k int) bool {
	switch alg {
	case 0, 1, 2, 3:
		return k == 3
	case 4:
		return k == 1 || k == 3
	case 5, 6:
		return k >= 1
	default:
		return true
	}
}

// stepYM2612Voice advances one 4-operator YM2612 (OPN2) or TI SN76489 PSG voice by one sample at SampleRate
// using the hardware-accurate Nuked-OPN2 / Genesis Plus GX integer pipeline with full 14-bit floating-point
// output and band-limited PolyBLEP PSG synthesis.
func stepYM2612Voice(st *ym2612VoiceState, patch YM2612Patch, freq, t, keyOffSec, dutyOverride float64) float64 {
	if patch.IsPSG {
		duty := patch.PSGDuty
		if dutyOverride > 0 && dutyOverride < 1.0 {
			duty = dutyOverride
		}
		if duty <= 0 || duty >= 1.0 {
			duty = 0.5
		}
		dt := freq / float64(SampleRate)
		inc := uint32(math.Round(dt * 1048576.0))
		st.phase20[0] = (st.phase20[0] + inc) & 0xFFFFF
		ph := float64(st.phase20[0]) / 1048576.0

		var raw float64
		if ph < duty {
			raw = 1.0
		} else {
			raw = -1.0
		}
		raw += polyBLEP(ph, dt)
		raw -= polyBLEP(math.Mod(ph+1.0-duty, 1.0), dt)

		// Remove pulse-wave DC offset (2*duty - 1) so envelope gating never clicks
		dc := 2.0*duty - 1.0
		centered := (raw - dc) * 0.85
		st.model1LPF += 0.34 * (centered - st.model1LPF)
		return st.model1LPF
	}

	fnum, block, keyCode := freqToYM2612FNumBlockKeyCode(freq)
	if !st.initialized {
		initYM2612VoiceState(st, patch, keyCode)
	}
	if !st.inRelease && t > keyOffSec {
		st.inRelease = true
		for k := 0; k < 4; k++ {
			st.egState[k] = ym2612EGRelease
		}
	}

	// Clock the hardware 10-bit Envelope Generator at the NTSC YM2612 EG rate (53,267 / 3 = 17,756 Hz)
	st.egClockAcc += 17756
	for st.egClockAcc >= uint32(SampleRate) {
		st.egClockAcc -= uint32(SampleRate)
		stepYM2612EG(st, patch, keyCode)
	}

	// Advance the four 20-bit hardware Phase Generators (F-Num, Block, 32-entry Detune table, and 4-bit MUL)
	baseInc := int32((fnum << block) >> 1)
	var phase10 [4]uint16
	var envAtten10 [4]int32
	for k := 0; k < 4; k++ {
		op := patch.Op[k]
		dtMag := ym2612DetuneTable[op.DT&3][(keyCode>>2)&7]
		if !isYM2612Carrier(patch.ALG, k) && dtMag > 0 && (op.MUL >= 2 || freq > 500.0) {
			dtMag *= 14
		} else if patch.Name == "ym2612_bell" && isYM2612Carrier(patch.ALG, k) && dtMag > 0 && freq > 950.0 {
			dtMag *= 4
		}
		var inc int32
		if (op.DT & 4) != 0 {
			inc = baseInc - dtMag
		} else {
			inc = baseInc + dtMag
		}
		if inc < 0 {
			inc = 0
		}
		if op.MUL == 0 {
			inc >>= 1
		} else {
			inc *= int32(op.MUL)
		}
		st.phase20[k] = (st.phase20[k] + uint32(inc)) & 0xFFFFF
		phase10[k] = uint16((st.phase20[k] >> 10) & 0x3FF)

		tl := int32(op.TL)
		// High-register modulator anti-aliasing guard: when an FM modulator exceeds 900 Hz,
		// smoothly raise TL so high notes stay warm and free of ultrasonic sideband foldover.
		if !isYM2612Carrier(patch.ALG, k) {
			mulFactor := float64(op.MUL)
			if op.MUL == 0 {
				mulFactor = 0.5
			}
			opFreq := freq * mulFactor
			if opFreq > 2200.0 {
				extraTL := int32(math.Round(12.0 * math.Log2(opFreq/2200.0)))
				tl += extraTL
				if tl > 127 {
					tl = 127
				}
			}
		}
		atten := st.egAtten[k] + (tl << 3)
		if atten > 1023 {
			atten = 1023
		}
		envAtten10[k] = atten
	}

	// Operator 1 evaluation with hardware 2-sample averaged self-feedback:
	// (op1Prev0 + op1Prev1) >> (11 - FB) for 14-bit signed operator scale (±8176).
	var fbOffset10 int32
	if patch.FB > 0 && patch.FB <= 7 {
		fbOffset10 = (st.op1Prev0 + st.op1Prev1) >> (11 - patch.FB)
		if fbOffset10 > 180 {
			fbOffset10 = 180
		} else if fbOffset10 < -180 {
			fbOffset10 = -180
		}
	}
	op1Phase := uint16((int32(phase10[0]) + fbOffset10) & 0x3FF)
	op1Out := evalYM2612Operator(op1Phase, envAtten10[0])
	st.op1Prev1 = st.op1Prev0
	st.op1Prev0 = op1Out

	// Evaluate the 8 hardware YM2612 algorithms using 14-bit to 10-bit phase modulation (modOut >> 2)
	// and 14-bit carrier accumulator clamping ([-8192, +8191]).
	var out14 int32
	switch patch.ALG {
	case 0:
		// Alg 0: Op1 -> Op2 -> Op3 -> Op4 (carrier)
		op2 := evalYM2612Operator(uint16((int32(phase10[1])+(op1Out>>2))&0x3FF), envAtten10[1])
		op3 := evalYM2612Operator(uint16((int32(phase10[2])+(op2>>2))&0x3FF), envAtten10[2])
		out14 = evalYM2612Operator(uint16((int32(phase10[3])+(op3>>2))&0x3FF), envAtten10[3])
	case 1:
		// Alg 1: (Op1 + Op2) -> Op3 -> Op4 (carrier)
		op2 := evalYM2612Operator(phase10[1], envAtten10[1])
		mod3 := clampYM2612Accum14(op1Out + op2)
		op3 := evalYM2612Operator(uint16((int32(phase10[2])+(mod3>>2))&0x3FF), envAtten10[2])
		out14 = evalYM2612Operator(uint16((int32(phase10[3])+(op3>>2))&0x3FF), envAtten10[3])
	case 2:
		// Alg 2: (Op1 + (Op2 -> Op3)) -> Op4 (carrier): Classic Shinobi III FM Electric Guitar & FM Bass
		op2 := evalYM2612Operator(phase10[1], envAtten10[1])
		op3 := evalYM2612Operator(uint16((int32(phase10[2])+(op2>>2))&0x3FF), envAtten10[2])
		mod4 := clampYM2612Accum14(op1Out + op3)
		out14 = evalYM2612Operator(uint16((int32(phase10[3])+(mod4>>2))&0x3FF), envAtten10[3])
	case 3:
		// Alg 3: ((Op1 -> Op2) + Op3) -> Op4 (carrier)
		op2 := evalYM2612Operator(uint16((int32(phase10[1])+(op1Out>>2))&0x3FF), envAtten10[1])
		op3 := evalYM2612Operator(phase10[2], envAtten10[2])
		mod4 := clampYM2612Accum14(op2 + op3)
		out14 = evalYM2612Operator(uint16((int32(phase10[3])+(mod4>>2))&0x3FF), envAtten10[3])
	case 4:
		// Alg 4: (Op1 -> Op2) + (Op3 -> Op4): Dual 2-operator stacks (Rhythm Guitar, Brass, EPiano, Flute, Bell)
		c1 := evalYM2612Operator(uint16((int32(phase10[1])+(op1Out>>2))&0x3FF), envAtten10[1])
		op3 := evalYM2612Operator(phase10[2], envAtten10[2])
		c2 := evalYM2612Operator(uint16((int32(phase10[3])+(op3>>2))&0x3FF), envAtten10[3])
		out14 = clampYM2612Accum14(c1 + c2)
	case 5:
		// Alg 5: Op1 -> (Op2 + Op3 + Op4): 1 modulator driving 3 parallel carriers (Strings, Choir)
		mod := op1Out >> 2
		c1 := evalYM2612Operator(uint16((int32(phase10[1])+mod)&0x3FF), envAtten10[1])
		c2 := evalYM2612Operator(uint16((int32(phase10[2])+mod)&0x3FF), envAtten10[2])
		c3 := evalYM2612Operator(uint16((int32(phase10[3])+mod)&0x3FF), envAtten10[3])
		out14 = clampYM2612Accum14(clampYM2612Accum14(c1+c2) + c3)
	case 6:
		// Alg 6: (Op1 -> Op2) + Op3 + Op4
		c1 := evalYM2612Operator(uint16((int32(phase10[1])+(op1Out>>2))&0x3FF), envAtten10[1])
		c2 := evalYM2612Operator(phase10[2], envAtten10[2])
		c3 := evalYM2612Operator(phase10[3], envAtten10[3])
		out14 = clampYM2612Accum14(clampYM2612Accum14(c1+c2) + c3)
	default:
		// Alg 7: Op1 + Op2 + Op3 + Op4 (4 parallel additive carriers)
		c2 := evalYM2612Operator(phase10[1], envAtten10[1])
		c3 := evalYM2612Operator(phase10[2], envAtten10[2])
		c4 := evalYM2612Operator(phase10[3], envAtten10[3])
		out14 = clampYM2612Accum14(clampYM2612Accum14(clampYM2612Accum14(op1Out+c2)+c3) + c4)
	}

	// Preserve full 14-bit operator dynamic range (no 9-bit staircase truncation buzz on quiet tails)
	out := float64(out14) / 8192.0
	if patch.Gain > 0 {
		out *= patch.Gain
	}

	// SEGA Mega Drive Model 1 discrete analog RC low-pass filter (~6.5 kHz warm rolloff)
	st.model1LPF += 0.52 * (out - st.model1LPF)
	return math.Max(-1.0, math.Min(1.0, st.model1LPF))
}

// stepYM2612Drum synthesizes one sample of a clean Mega Drive YM2612 + SN76489 percussion hit
// with strict exponential decay envelopes on all noise components (zero stationary hiss).
func stepYM2612Drum(waveType string, t, startFreq, endFreq, durSec float64, rng *rand.Rand, filterState *float64) float64 {
	progress := 0.0
	if durSec > 0 {
		progress = math.Min(1.0, t/durSec)
	}
	switch waveType {
	case "ym2612_kick", "kick":
		// Heavy Mega Drive Kick: exact phase integral of exponential frequency sweep (150Hz -> 36Hz)
		f0 := startFreq
		f1 := endFreq
		if f0 <= 0 || f0 == 440.0 {
			f0 = 150.0
			f1 = 36.0
		}
		fastDecay := math.Exp(-22.0 * t)
		bodyPhase := 2.0 * math.Pi * (f1*t + (f0-f1)*(1.0-fastDecay)/22.0)
		bodyAmp := math.Sin(bodyPhase)
		fmSnap := math.Sin(2.0*bodyPhase) * math.Exp(-48.0*t)
		beaterClick := (rng.Float64()*2.0 - 1.0) * math.Exp(-180.0*t) * 0.18
		return math.Tanh((bodyAmp*1.45 + 0.30*fmSnap + beaterClick) * math.Exp(-5.5*progress))

	case "ym2612_snare", "snare":
		// Mega Drive Snare: dual FM shell body (130Hz & 210Hz) + rapidly decaying snare wires
		shellPhase1 := 2.0 * math.Pi * (130.0*t + 85.0*(1.0-math.Exp(-30.0*t))/30.0)
		shellPhase2 := 2.0 * math.Pi * (210.0*t + 95.0*(1.0-math.Exp(-36.0*t))/36.0)
		shell := (0.75*math.Sin(shellPhase1) + 0.45*math.Sin(shellPhase2)) * math.Exp(-18.0*t)
		noiseRaw := rng.Float64()*2.0 - 1.0
		*filterState += 0.68 * (noiseRaw - *filterState)
		wires := *filterState * math.Exp(-16.0*t)
		return math.Tanh(shell*1.20 + wires*0.85)

	case "ym2612_tom", "tom":
		// Pitched FM electronic tom with clean phase integral
		f0 := startFreq
		f1 := endFreq
		if f0 <= 0 || f0 == 440.0 {
			f0 = 180.0
			f1 = 70.0
		}
		sweepDecay := math.Exp(-14.0 * t)
		phase := 2.0 * math.Pi * (f1*t + (f0-f1)*(1.0-sweepDecay)/14.0)
		mod := math.Sin(phase*2.0) * math.Exp(-32.0*t) * 0.75
		stick := (rng.Float64()*2.0 - 1.0) * math.Exp(-140.0*t) * 0.14
		return math.Tanh((math.Sin(phase+mod) + stick) * math.Exp(-7.5*t))

	case "ym2612_hat", "ym2612_open_hat", "ym2612_crash", "hat", "open_hat", "crash":
		// Inharmonic metallic FM cymbal matrix + strictly enveloped high-pass air transient
		m1 := math.Sin(2.0 * math.Pi * 540.0 * t)
		m2 := math.Sin(2.0 * math.Pi * 815.0 * t)
		m3 := math.Sin(2.0*math.Pi*1490.0*t + 0.95*m1)
		m4 := math.Sin(2.0*math.Pi*2310.0*t + 0.85*m2)
		metal := (m3 + m4) * 0.28

		decayRate := 44.0
		if waveType == "ym2612_open_hat" || waveType == "open_hat" {
			decayRate = 11.5
		} else if waveType == "ym2612_crash" || waveType == "crash" {
			decayRate = 4.5
		}

		noiseRaw := rng.Float64()*2.0 - 1.0
		*filterState += 0.25 * (noiseRaw - *filterState)
		hpNoise := noiseRaw - *filterState // Crisp high-passed cymbal sizzle without low-mid static hiss
		env := math.Exp(-decayRate * t)
		return math.Tanh((0.45*metal + 0.55*hpNoise) * env)
	}
	return 0
}
