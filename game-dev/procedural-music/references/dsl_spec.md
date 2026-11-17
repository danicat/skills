# Music composition DSL specification

Complete syntax reference for `.music` scores compiled by [`../scripts/sound.go`](../scripts/sound.go).

A `.music` score has four sections: **headers**, **instruments (`inst`)**, **reusable patterns (`pattern`)**, and **multi-channel tracks (`track`)**.

---

## 1. Header directives and tempo markings

```text
title "Bare Knuckle / Streets of Rage - Intro"
type song
tempo moderato 100
time 4/4
```

- `#` (at line start or after whitespace) and `//` start comments.
- `synth <default|apple>` selects the pure-Go YM2612/PSG engine (`default`) or macOS CoreAudio real instruments (`apple`).
- `tempo <marking> [<bpm>]` or `bpm <number|marking>` sets tempo from a number, a classical Italian marking, or both:

| Tempo Marking | Default BPM | Typical Scene Fit |
| :--- | :--- | :--- |
| `larghissimo` / `grave` / `largo` / `lento` / `larghetto` | `24` / `42` / `50` / `56` / `63` | Solemn, mysterious, or atmospheric intros |
| `adagio` / `adagietto` | `70` / `76` | Slow, reflective themes and quiet sanctuaries |
| `andante` / `andantino` | `88` / `96` | Lyrical stage themes and epilogue ballads |
| `moderato` / `allegretto` | `112` / `120` | Mid-tempo urban grooves and exploration themes |
| `allegro` | `138` | Upbeat action stages (`126` to `150 BPM`) |
| `vivace` / `vivacissimo` | `160` / `172` | High-energy boss battles and fast combat |
| `presto` / `prestissimo` | `184` / `204` | Fast escape sequences and final boss phases |

---

## 2. Instrument patches (`inst`) and defaults

Every `wave=` archetype pre-populates tuned studio defaults for `vol`, `adsr`, `vib`, `lpf`, `duty`, and a matching General MIDI (`gm=` / `gm_drum=`) patch for `-apple`:

```text
inst fm_brass_lead wave=ym2612_brass      pan=-0.18
inst fm_brass_echo wave=ym2612_brass      gm=synth_brass_1 vol=0.13 pan=0.24 lpf=0.44
inst psg_lead      wave=psg_square        vol=0.15 pan=-0.10
inst fm_bass       wave=ym2612_slap_bass
inst sub_bass      wave=sub_bass          gm=electric_bass
inst drums         wave=kick              vol=0.28 pan=0.00
```

> **1:1 `inst`-to-`track` channel rule**: Give each declared `inst` its own dedicated `track` channel so isolated stem rendering (`SynthesizeScoreWithStems`) produces one clean stereo stem per instrument with matching `vol` and `pan`. A standard **8-piece drum kit** (`kick`, `snare`, `tom_hi`, `tom_mid`, `tom_low`, `hat`, `open_hat`, `crash`) is pre-seeded for pattern events (`kick:8`, `snare:8`, `hat:8`). Declare a single primary percussion instrument (`inst drums wave=kick vol=0.28 pan=0.00`) for your drum track: adjusting its `vol` (including `vol=0` to mute) or `pan` scales and pans all pre-seeded drum hits proportionally.

| Waveform (`wave=`) | Default `gm=` Upgrade (`-apple`) | Studio Defaults and Roles |
| :--- | :--- | :--- |
| `ym2612_brass` | `brass_section` (`synth_brass_1`, `synth_brass_2`) | `vol=0.12 pan=0.20 adsr=0.025,0.16,0.86,0.14 vib=4.8,0.06 lpf=0.36`. 4-op FM synth-brass for chord stabs and fanfares. |
| `ym2612_epiano`, `ym2612_bell` | `epiano1`, `vibraphone` (`tubular_bells`) | `epiano`: `vol=0.13 lpf=0.38`; `bell`: `vol=0.060 lpf=0.64`. Electric piano and crystal chime for inner voices and melody doubling. |
| `ym2612_guitar`, `ym2612_rhythm_guitar` | `overdriven_guitar`, `distortion_guitar` | `guitar`: `vol=0.16 vib=5.5,3.50 lpf=0.46`; `rhythm_guitar`: `vol=0.10 lpf=0.42`. Parallel 3rds/6ths leads and power chords. |
| `ym2612_bass`, `ym2612_slap_bass`, `sub_bass` | `electric_bass`, `slap_bass_1`, `synth_bass_1` | `bass`: `vol=0.25 lpf=0.055`; `slap_bass`: `vol=0.22 lpf=0.065`; `sub_bass`: `vol=0.24 lpf=0.036`. Anchors `C1` to `C2` (`32 Hz` to `130 Hz`). |
| `ym2612_strings`, `ym2612_choir`, `ym2612_flute` | `string_ensemble_1`, `choir_aahs`, `flute` | `strings`/`choir`: `vol=0.10 lpf=0.32`; `flute`: `vol=0.12 vib=5.5,2.20 lpf=0.42`. Sustained pads, vocal textures, and counter-lines. |
| `psg_square`, `psg_arp` | `lead_square`, `orchestral_harp` (`clavinet`) | `psg_square`: `vol=0.050 duty=0.50 lpf=0.42`; `psg_arp`: `vol=0.072 duty=0.25 lpf=0.44`. SN76489 chip leads, echoes, and `:16` arps. |
| `koto`, `shamisen`, `harp`, `guitar` | `koto`, `shamisen`, `orchestral_harp`, `nylon_guitar` | Plucked string voices (`vol=0.11` to `0.13`) for fast ostinatos and acoustic intros. |
| `violin`, `cello`, `piano`, `organ`, `oboe`, `clarinet`, `shakuhachi` | Matching GM program names | Orchestral strings, keyboard, and solo woodwind models with tuned envelopes and filter curves. |
| `kick`, `snare`, `tom`, `hat`, `open_hat`, `crash` | `gm_drum=kick`, `snare`, `tom_hi`, `tom_mid`, `tom_low`, `hat`, `open_hat`, `crash` | Exponential-decay Mega Drive drum kit in default mode; acoustic GM drum kit in `-apple` mode. |

### Instrument attributes

| Attribute | Values / Format | Description |
| :--- | :--- | :--- |
| `gm` / `program` | `0..127` or GM name | `gs_instruments.dls` patch for `-apple` (inferred from `wave=` if omitted). |
| `gm_drum` / `drum_note` | `27..87` or drum name | General MIDI Channel 10 drum note. |
| `vol` | `0.0` .. `1.0` | Voice gain (`0.0` mutes the track; keep mids/highs around `0.05..0.18` and bass `0.20..0.25`). |
| `pan` | `-1.0` .. `+1.0` | Constant-power stereo pan (`-1.0` left, `0.0` center, `+1.0` right). |
| `adsr` | `A,D,S,R` | Envelope override: Attack (`sec`), Decay (`sec`), Sustain (`0..1`), Release (`sec`). |
| `vib` | `rateHz,depthHz` | LFO vibrato rate and depth in Hz (`vib=5.5,2.20`). |
| `freq` / `sweep` | `<pitchOrHz>` or `<start>-><end>` | Drum pitch sweep override (`freq=158Hz->38Hz`). |
| `lpf` / `hpf` | `(0.0, 1.0]` | Single-pole low-pass or high-pass filter alpha override. |

---

## 3. Notes, tied durations (`~`), repeats, groups, and barlines

Events inside `pattern` and `track` follow `<target>[:<duration>][*<repeat>][@<modifier>...]`:

- **Pitches, rests, and chords**:
  - Scientific pitch `C0`..`B8` with `#` (or `s`) sharp and `b` flat: `E5:2`, `Bb4:8.`, `A1:16`.
  - Rests use `R`, `_`, or `.` (`R:1`, `R:16`). Chords use brackets (`[A3 C4 E4]:1`, `[G3 B3 D4]:2`).
- **Standard, dotted, and triplet subdivisions**:
  - Standard: `:1` (4 beats), `:2` (2 beats), `:4` (1 beat), `:8` (0.5 beat), `:16` (0.25 beat), `:32` (0.125 beat).
  - Dotted (`1.5x`): `:1.` (6 beats), `:2.` (3 beats), `:4.` (1.5 beats), `:8.` (0.75 beats).
  - Triplets (`2/3x`): `:2t` (`4/3` beats), `:4t` (`2/3` beat), `:8t` (`1/3` beat), `:16t` (`1/6` beat).
- **Tied durations (`~`) and cross-barline ties (`~ |`)**:
  - Chain any durations with `~`: `C3:1~1` (2 bars), `A4:1~1~1` (3 bars), `D5:1~1~4t`, `A5:1~2.~16t`.
  - Use a trailing `~` before `|` (`F5:8~ | F5:16` or shorthand `F5:8~ | :16`) to sustain across barlines without re-triggering the envelope while keeping measure lengths exact.
  - Exact rational fractions `<num>/<den>` also parse via 64-bit GCD arithmetic.
- **Sticky running durations**:
  - State `:dur` once when adjacent tokens share duration (`A4:8t C5 E5`). Running duration persists across tokens and `(...)` groups until the next `:dur`.
- **Repeats (`*N`) and group durations (`(...):dur`)**:
  - Repeat notes (`C5:8.*5`) or folded phrases (`(A5:2 F5:4 C5 | D5:2. G5:4 |)*2`).
  - Attach `:dur` to a group (`(C3 G3 C4 G4):16*2 |`) without mutating outer running duration. In `4/4` time, an 8-note `:16` group is `2.0` beats (`*2` fills `4.0` beats); an 8-note `:8` group fills `4.0` beats.
- **Track block rule and measure verification (`|`)**:
  - `track` blocks must reference declared `pattern` identifiers (`track ch01 lead: lead_intro lead_secA`), never raw notes. Declare patterns first (`pattern <name> = ...`).
  - Every `|` barline is checked against `time` signature (`4/4` = `4` beats). Any drop or extra subdivision fails fast with track/pattern name and beat offset.

---

## 4. Per-channel dynamics, articulations, and phrase modifiers

| Category | Modifiers | Behavior |
| :--- | :--- | :--- |
| **Static levels** | `@ppp`, `@pp`, `@p`, `@mp`, `@mf`, `@f`, `@ff`, `@fff` | Scales note or group gain (`0.20x` to `1.55x`). |
| **Volume ramps** | `@crescendo`, `@diminuendo`, `@fade_in`, `@fade_out`, `@swell`, `@vol=1.000->0.005` | Sample-accurate gain ramp (and MIDI `CC 11` Expression in `-apple`). |
| **Articulations** | `@staccato` (`0.40`), `@spiccato` (`0.28`), `@pizzicato` (`0.35`), `@portato` (`0.70`), `@legato` (`1.0`), `@tenuto`, `@marcato` | Scales note gate ratio and attack transient without shifting beat grid. |
| **Phrase modifiers** | `@+12` / `@-12` (or `@+N` / `@-N`), `@pan=-0.6->0.6`, `@lpf=0.35` | Transposes patterns/groups in semitones, sweeps stereo pan, or overrides filter cutoff. |
