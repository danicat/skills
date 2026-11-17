# WebAssembly Audio Late-Sync, 44.1 kHz Stereo PCM & Fail-Fast Save Persistence Reference

This module covers 4-byte aligned 44.1 kHz 16-bit stereo PCM audio playback across `procedural-sfx`, `procedural-music`, and `lyria`, WebAssembly browser autoplay unlock synchronization, and build-tagged fail-fast save storage across Desktop (`!js`) and WebAssembly (`js && wasm`).

---

## 1. Unified 44.1 kHz Stereo PCM Audio & WebAssembly Autoplay Unlock

Ebitengine's `audio.Context` operates on **16-bit signed little-endian stereo PCM at 44,100 Hz (4 bytes per sample frame: 2 bytes Left + 2 bytes Right)**. Share a single `*audio.Context` across all `procedural-sfx` (`.sfx`), `procedural-music` (`.music`), and `lyria` audio buffers.

Modern browsers block WebAudio playback until the user performs an explicit interaction gesture (key press, mouse click, or touch). Meanwhile, the game's `Update()` loop and visual clocks continue running from `0:00`.

When the user finally interacts at elapsed time $T_{\text{elapsed}}$, starting BGM at `0:00` desynchronizes music from intro choreography or beat-synced visuals. Instead, compute the exact byte offset in Ebitengine's 4-byte stereo frame format and `Seek()` into the loop:

$$
\text{ByteOffset} = \left(\left\lfloor T_{\text{elapsed}} \times \text{SampleRate} \right\rfloor \times 4\right) \pmod{\text{LoopLengthBytes}}
$$

> **CRITICAL INVARIANT**: Ebitengine audio streams require all buffer lengths and seek offsets to be an exact multiple of `4` (`length &^ 3`). Passing an unaligned length or seeking to an unaligned byte offset causes a runtime panic or corrupts stereo channels.

```go
package audio

import (
	"fmt"
	"io"
	"time"

	"github.com/hajimehoshi/ebiten/v2"
	ebitaudio "github.com/hajimehoshi/ebiten/v2/audio"
	"github.com/hajimehoshi/ebiten/v2/inpututil"
)

const (
	SampleRate     = 44100
	BytesPerSample = 4 // 16-bit stereo: 2 bytes * 2 channels
)

type SyncedBGMPlayer struct {
	ctx           *ebitaudio.Context
	loopStream    *ebitaudio.InfiniteLoop
	player        *ebitaudio.Player
	loopLengthBytes int64
	elapsed       time.Duration
	unlocked      bool
}

func NewSyncedBGMPlayer(ctx *ebitaudio.Context, pcmStream io.ReadSeeker, loopLengthBytes int64) (*SyncedBGMPlayer, error) {
	if ctx == nil {
		return nil, fmt.Errorf("audio: nil audio.Context")
	}
	alignedLen := loopLengthBytes &^ 3
	if alignedLen <= 0 {
		return nil, fmt.Errorf("audio: loopLengthBytes (%d) must be >= 4 bytes", loopLengthBytes)
	}

	loop := ebitaudio.NewInfiniteLoop(pcmStream, alignedLen)
	p, err := ctx.NewPlayer(loop)
	if err != nil {
		return nil, fmt.Errorf("audio: create BGM player: %w", err)
	}

	return &SyncedBGMPlayer{
		ctx:             ctx,
		loopStream:      loop,
		player:          p,
		loopLengthBytes: alignedLen,
	}, nil
}

// AlignPCMByteOffset converts a duration into a 4-byte aligned stereo PCM byte offset
// wrapped cleanly within loopLengthBytes.
func AlignPCMByteOffset(elapsed time.Duration, sampleRate int, loopLengthBytes int64) (int64, error) {
	if sampleRate <= 0 {
		return 0, fmt.Errorf("audio: invalid sampleRate %d", sampleRate)
	}
	if loopLengthBytes <= 0 || loopLengthBytes%BytesPerSample != 0 {
		return 0, fmt.Errorf("audio: invalid loopLengthBytes %d (must be multiple of 4)", loopLengthBytes)
	}

	totalSamples := int64(elapsed.Seconds() * float64(sampleRate))
	rawByteOffset := totalSamples * BytesPerSample
	wrappedOffset := rawByteOffset % loopLengthBytes
	if wrappedOffset < 0 {
		wrappedOffset = 0
	}
	// Enforce strict 4-byte frame boundary alignment (&^ 3)
	alignedOffset := wrappedOffset &^ 3
	return alignedOffset, nil
}

// Update advances the internal clock and unlocks/seeks audio on first user gesture.
func (bgm *SyncedBGMPlayer) Update(dt time.Duration) error {
	bgm.elapsed += dt

	if bgm.unlocked {
		return nil
	}

	if hasUserGesture() {
		offsetBytes, err := AlignPCMByteOffset(bgm.elapsed, bgm.ctx.SampleRate(), bgm.loopLengthBytes)
		if err != nil {
			return fmt.Errorf("audio: compute late-sync offset: %w", err)
		}
		if _, err := bgm.loopStream.Seek(offsetBytes, io.SeekStart); err != nil {
			return fmt.Errorf("audio: seek BGM stream to %d bytes: %w", offsetBytes, err)
		}
		bgm.player.Play()
		bgm.unlocked = true
	}
	return nil
}

func hasUserGesture() bool {
	if len(inpututil.AppendJustPressedKeys(nil)) > 0 {
		return true
	}
	if inpututil.IsMouseButtonJustPressed(ebiten.MouseButtonLeft) ||
		inpututil.IsMouseButtonJustPressed(ebiten.MouseButtonRight) {
		return true
	}
	if len(inpututil.AppendJustPressedTouchIDs(nil)) > 0 {
		return true
	}
	return false
}
```

### 1.1 Zero-Latency SFX Bank with Cooldown Throttling (`procedural-sfx`)
Pre-compile `.sfx` scripts into 4-byte aligned `[]byte` buffers during boot and throttle rapid triggers in `Update()`:

```go
type SFXBank struct {
	ctx        *ebitaudio.Context
	cues       map[string][]byte
	lastPlayed map[string]time.Time
}

func NewSFXBank(ctx *ebitaudio.Context) (*SFXBank, error) {
	if ctx == nil {
		return nil, fmt.Errorf("audio: nil audio.Context for SFXBank")
	}
	return &SFXBank{
		ctx:        ctx,
		cues:       make(map[string][]byte, 16),
		lastPlayed: make(map[string]time.Time, 16),
	}, nil
}

func (b *SFXBank) RegisterCue(name string, pcm []byte) error {
	alignedLen := len(pcm) &^ 3
	if name == "" || alignedLen == 0 {
		return fmt.Errorf("audio: invalid SFX cue %q (aligned length=%d)", name, alignedLen)
	}
	b.cues[name] = pcm[:alignedLen]
	return nil
}

func (b *SFXBank) PlaySFX(name string, cooldown time.Duration) error {
	pcm, ok := b.cues[name]
	if !ok {
		return fmt.Errorf("audio: unknown SFX cue %q", name)
	}
	now := time.Now()
	if last, exists := b.lastPlayed[name]; exists && now.Sub(last) < cooldown {
		return nil
	}
	b.lastPlayed[name] = now
	p := b.ctx.NewPlayerFromBytes(pcm)
	p.Play()
	return nil
}
```

---

## 2. Build-Tagged Fail-Fast Save Storage (Desktop vs. WASM)

Use Go build tags (`//go:build !js` and `//go:build js && wasm`) to provide a unified, fail-fast `SaveStorage` interface without silent fallbacks or ignored errors.

### 2.1 Shared Save Contract (`internal/save/storage.go`)

```go
package save

import (
	"encoding/json"
	"fmt"
)

type GameSaveData struct {
	Version   int    `json:"version"`
	HighScore int    `json:"high_score"`
	Unlocked  []int  `json:"unlocked"`
}

type Storage interface {
	Save(slot string, data GameSaveData) error
	Load(slot string) (GameSaveData, error)
}

func MarshalSave(data GameSaveData) ([]byte, error) {
	if data.Version <= 0 {
		return nil, fmt.Errorf("save: invalid schema version %d (must be >= 1)", data.Version)
	}
	raw, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return nil, fmt.Errorf("save: marshal GameSaveData: %w", err)
	}
	return raw, nil
}

func UnmarshalSave(raw []byte) (GameSaveData, error) {
	var data GameSaveData
	if err := json.Unmarshal(raw, &data); err != nil {
		return GameSaveData{}, fmt.Errorf("save: unmarshal GameSaveData: %w", err)
	}
	if data.Version <= 0 {
		return GameSaveData{}, fmt.Errorf("save: corrupt or missing schema version %d", data.Version)
	}
	return data, nil
}
```

### 2.2 Desktop Native Atomic File Persistence (`internal/save/storage_desktop.go`)

```go
//go:build !js

package save

import (
	"fmt"
	"os"
	"path/filepath"
)

type DesktopStorage struct {
	baseDir string
}

func NewStorage(appID string) (Storage, error) {
	if appID == "" {
		return nil, fmt.Errorf("save: appID must not be empty")
	}
	cfgDir, err := os.UserConfigDir()
	if err != nil {
		return nil, fmt.Errorf("save: resolve os.UserConfigDir: %w", err)
	}
	dir := filepath.Join(cfgDir, appID)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return nil, fmt.Errorf("save: create save directory %q: %w", dir, err)
	}
	return &DesktopStorage{baseDir: dir}, nil
}

func (ds *DesktopStorage) Save(slot string, data GameSaveData) error {
	if slot == "" {
		return fmt.Errorf("save: slot name must not be empty")
	}
	raw, err := MarshalSave(data)
	if err != nil {
		return err
	}
	targetPath := filepath.Join(ds.baseDir, slot+".json")
	tmpPath := targetPath + ".tmp"
	if err := os.WriteFile(tmpPath, raw, 0o600); err != nil {
		return fmt.Errorf("save: write temp save file %q: %w", tmpPath, err)
	}
	if err := os.Rename(tmpPath, targetPath); err != nil {
		return fmt.Errorf("save: atomic rename %q -> %q: %w", tmpPath, targetPath, err)
	}
	return nil
}

func (ds *DesktopStorage) Load(slot string) (GameSaveData, error) {
	if slot == "" {
		return GameSaveData{}, fmt.Errorf("save: slot name must not be empty")
	}
	targetPath := filepath.Join(ds.baseDir, slot+".json")
	raw, err := os.ReadFile(targetPath)
	if err != nil {
		return GameSaveData{}, fmt.Errorf("save: read save file %q: %w", targetPath, err)
	}
	return UnmarshalSave(raw)
}
```

### 2.3 WebAssembly `localStorage` Persistence (`internal/save/storage_wasm.go`)

```go
//go:build js && wasm

package save

import (
	"fmt"
	"syscall/js"
)

type WASMStorage struct {
	appID        string
	localStorage js.Value
}

func NewStorage(appID string) (Storage, error) {
	if appID == "" {
		return nil, fmt.Errorf("save: appID must not be empty")
	}
	win := js.Global().Get("window")
	if win.IsUndefined() || win.IsNull() {
		return nil, fmt.Errorf("save: browser window object is unavailable in WASM environment")
	}
	ls := win.Get("localStorage")
	if ls.IsUndefined() || ls.IsNull() {
		return nil, fmt.Errorf("save: window.localStorage is unavailable or disabled")
	}
	return &WASMStorage{appID: appID, localStorage: ls}, nil
}

func (ws *WASMStorage) key(slot string) string {
	return ws.appID + ":" + slot
}

func (ws *WASMStorage) Save(slot string, data GameSaveData) error {
	if slot == "" {
		return fmt.Errorf("save: slot name must not be empty")
	}
	raw, err := MarshalSave(data)
	if err != nil {
		return err
	}
	ws.localStorage.Call("setItem", ws.key(slot), string(raw))
	return nil
}

func (ws *WASMStorage) Load(slot string) (GameSaveData, error) {
	if slot == "" {
		return GameSaveData{}, fmt.Errorf("save: slot name must not be empty")
	}
	val := ws.localStorage.Call("getItem", ws.key(slot))
	if val.IsNull() || val.IsUndefined() {
		return GameSaveData{}, fmt.Errorf("save: slot %q not found in localStorage", ws.key(slot))
	}
	return UnmarshalSave([]byte(val.String()))
}
```
