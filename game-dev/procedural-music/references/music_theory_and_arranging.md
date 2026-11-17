# Music theory, arranging, and 16-bit study archetypes

Practical arranging and harmonic voice-leading principles distilled from classic Mega Drive / Genesis soundtracks and enforced by `ValidateScoreTheory` in [`../scripts/sound.go`](../scripts/sound.go).

---

## 1. Scene playback baselines and structural archetypes

Match playback mode, duration, tempo, and macro-form to the gameplay role:

| Scene / Event Type | Playback Mode | Typical Duration | Typical BPM Range | Musical Structure |
| :--- | :--- | :--- | :--- | :--- |
| **Stage / Gameplay** | **Looped** (`audio.NewInfiniteLoop`) | `60s` to `180s+` | `100` to `160 BPM` | Multi-section arc (*Intro -> Theme A -> Theme B -> Climax -> Turnaround*) to prevent loop fatigue. |
| **Boss Battle** | **Looped** (`audio.NewInfiniteLoop`) | `45s` to `120s` | `135` to `180+ BPM` | Driving syncopation, harmonic minor or Phrygian tension, 4-op FM leads, octave `:16` bass. |
| **Title / Menu / Sanctuary** | **Looped** (`audio.NewInfiniteLoop`) | `30s` to `90s` | `70` to `125 BPM` | Memorable motif or pad/arpeggio texture setting world mood. |
| **Game Over** | **One-off** (`Play(pcm, false)`) | `4s` to `15s` | `60` to `90 BPM` | Non-looping minor cadence or quiet resolution keeping retry friction low. |
| **Stage Clear / Fanfare** | **One-off** (`Play(pcm, false)`) | `5s` to `15s` | `120` to `160 BPM` | Non-looping ascending brass/bell fanfare with clean final chord release. |

Never force every soundtrack into identical instruments or an `8-bar A + 8-bar B` loop. Five classic reference scores live in [`../scripts/`](../scripts/):

| Archetype and Study Score | Tempo & Feel | Core Palette | Macro-Form Architecture |
| :--- | :--- | :--- | :--- |
| **Urban Club Groove** (`bare_knuckle_intro.music`) | `100 BPM` (`moderato`), syncopated house/funk | **Zero guitars**: 3-voice FM synth-brass, `epiano1`, `psg_square` lead + `:8` delay, `slap_bass_1`, `string_ensemble_1`. | **Through-composed 41 bars**: `8-bar` dark intro -> `8-bar` pulsing buildup -> `8-bar` brass hook -> `8-bar` climax with high PSG counter-lead -> `9-bar` drumless fade outro. |
| **Sci-Fi Shmup** (`gaiares_level2.music`) | `148 BPM` (`allegro`), propulsive | Bright FM lead + echo, `vibraphone`, `epiano1`, brass, `:16` PSG arps, `electric_bass` + `slap_bass_1`. | **Asymmetric loop (73 bars)**: `2-bar` solo drum fill -> `33-bar` loop (`32` melodic + `1` solo drum-break bar) x 2 -> `5-bar` fade. |
| **East-Asian Action** (`shinobi2_stage2.music`) | `134 BPM` (`allegro`), galloping momentum | `shamisen` / `koto` / `orchestral_harp` ostinato, galloping toms, FM lead, brass, driving bass. | **Ostinato frame (98 bars)**: `4-bar` intro -> `44-bar` loop (`A` heroic -> `B` lift -> `C` breakdown -> `4-bar` shamisen bridge) x 2 -> `6-bar` fade. |
| **Neoclassical Action** (`elemental_master_stage1.music`) | `150 BPM` (`allegro`), dramatic rock/metal | Twin harmonizing FM guitars in 3rds/6ths, `epiano1`, strings, `:16` driving bass. | **Fanfare anthem (69 bars)**: `8-bar` ceremonial fanfare with tom rolls -> `28-bar` loop x 2 -> `5-bar` fade. |
| **Lyrical Stage Ballad** (`ground_zero.music`) | `96 BPM` (`andantino`), spacious | Solo lead + `:16` octave echo, `epiano1`, brass, strings, `C1..C2` bass. | **Evolving cycles (56 bars)**: `4-bar` intro -> Cycle 1 (`A+B`, sparse bass) -> Cycles 2 and 3 (`A+B`, `:16` bass + open-fifth arps) -> `4-bar` coda. |

---

## 2. Cross-bar continuity vs. re-attacked stabs

1. **Hold legato notes across barlines with `~`**: Write `C3:1~1` or `F5:8~ | :16` instead of `C3:1 | C3:1`, which creates an artificial attack transient on Beat 1.
2. **Keep rhythmic chord stabs crisp**: Write explicit `:8.` re-attacks (`*N` repeats) with `:16` release gaps (`R:16`) at turnarounds so stabs punch cleanly:
   ```text
   (A4:8 E5:8.*2 F5*3 R:16 D5:8.*2 G5*2 G5:8 |)*9
   ```

---

## 3. Rhythmic signatures and bass engines

- **Tresillo stabs (`3+3+3+3+2+2`)**: Grouping `:16` subdivisions in 3s (`:8.`) over straight `4/4` drums drives synth-brass hooks and plucked ostinatos (`E4:8. A4 B4 C5 B4:8 A4`).
- **Triplets (`:8t`, `:4t`) over a `:16` backing**: Combining `~` ties with `:8t` and `:4t` keeps floating leads locked via exact 64-bit rational arithmetic with zero sample drift.
- **Rotate bass patterns by section**:
  1. **Pulsing pre-drop buildup**: `(A2:8.*2 A2:4 A2:4.)*8`
  2. **Offbeat slap-bass**: `((G2:16 A2:8)*4 A2:8. G2:16)*15`
  3. **Driving `:16` rock octave bass**: `(C1 C2):16*4`
- **Half-bar call-and-response**: Pair held `:2` peaks on Beats 1 and 2 with `:8. :8. :8` answers on Beats 3 and 4 rather than splitting held halves into `:4 :4`.

---

## 4. Riff voicing, counter-melody, and harmony

1. **Split 3-voice chords across separate channels**: Put top, mid, and bottom chord voices on dedicated tracks and animate the bottom voice with `:16` octave drops (`A4:8 A3:16`, `B4:8 G3:16`).
2. **Add tracks instead of hijacking riff tracks**: Keep 3-voice hooks running on `ch01..ch04` when counter-melodies, `:8` echoes, bell doubles, and inner harmonies enter on `ch05..ch08`.
3. **Echo vs. double**: Use `:16` or `:8` delayed echoes only on sustained lyrical leads; use zero-delay stereo doubling (for example `-0.18` vs. `+0.24` pan) on fast syncopated chord stabs so echoes do not smear chord changes.
4. **Harmonic palettes**: Alternate Aeolian/Dorian vamps (`Am7 -> Fmaj7 | G`), modal mixture (`C` major with borrowed `Bb`, `Ab`, `Fm -> Gsus4 -> G`), and neoclassical Phrygian/harmonic minor cadences (`F -> Dm -> E7 -> Am`).
5. **Drum contrast**: Avoid nonstop beat cymbals. Drop drums completely (`(R:1 |)*7`) for atmospheric intros, enter via Beat 4 pickup rolls (`R:2. (snare*3 kick):16 |`), and vary every 4th/8th bar turnaround.

---

## 5. Voice-leading rules (`ValidateScoreTheory`)

`ValidateScoreTheory` inspects all simultaneously sounding pitched voices:

- **Allowed vertical intervals**: Unisons, octaves, 3rds, 4ths, 5ths, 6ths, major 2nds/9ths (`diff == 2` or `14`), tritones (`diff == 6`), minor 7ths (`diff == 10`), and major 7ths (`diff == 11`). Short passing/echo notes under `0.25s` are also permitted.
- **Forbidden vertical collisions**:
  1. Sustained close minor 2nd (`diff == 1`) when both notes last `>= 0.25s`.
  2. Sustained flat 9th (`diff >= 13` and `(upper - lower)%12 == 1`) when both last `>= 0.30s` (such as `B2` below `C5`).
  3. Simultaneous `G` natural and `G#`/`Ab` across channels at any duration.
- **Real voice-leading fixes**:
  - **Hold pad notes until melody resolves**: Keep low pads on `C3/E3` while melody sustains `C5` over a `B` barline, then slide cleanly.
  - **Isolate slow-tempo echo tails inside each measure**: At `<= 100 BPM`, `:8` notes exceed `0.25s`. Start echoes with a leading rest and release before the next bar (`R:8 <lead>:2 R:8 <pickup>:4 |`) so chromatic steps never bleed across barlines.
  - **Common-tone pedal drones**: Sustain only pitch classes shared by every chord in the progression (hold `C3`, not `[C3 G3]`, across `Cm -> Ab -> Fm -> G`). On flat-VI chords (`Ab` in `Cm`), stick to `Ab`, `C`, `Eb` and avoid `G` natural.
