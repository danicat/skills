# Ebitengine Best Practices

Guidelines for building 2D games using the [Ebitengine](https://ebitengine.org/) game library.

## Game Interface

Every Ebitengine game must implement the `ebiten.Game` interface:

```go
type Game interface {
    // Update proceeds the game state.
    // Update is called every tick (default: 1/60s).
    Update() error

    // Draw draws the game screen.
    // Draw is called every frame (typically 60Hz).
    Draw(screen *ebiten.Image)

    // Layout takes the outside size (e.g., window size) and returns the (logical) screen size.
    Layout(outsideWidth, outsideHeight int) (screenWidth, screenHeight int)
}
```

## Recommended File Structure

```text
game/
├── assets/         (Images, sounds, fonts)
├── internal/       (Game logic, sub-systems)
│   ├── entity/     (Game objects)
│   ├── input/      (Input handling)
│   └── scene/      (Game states)
├── go.mod
└── main.go         (Window setup and ebiten.RunGame)
```

## Performance Guidelines

*   Draw multiple items using the same sprite sheet or texture in sequence to reduce GPU draw calls.
*   Pre-allocate critical objects in `init()` or `NewGame()` to prevent garbage collection pauses during gameplay.
*   Use `Image.SubImage` to load sprite coordinates from sheets efficiently.
*   Utilize offscreen textures or images for complex compositions that remain static between frames.

## Example `main.go`

```go
package main

import (
	"log"

	"github.com/hajimehoshi/ebiten/v2"
)

type Game struct{}

func (g *Game) Update() error {
	return nil
}

func (g *Game) Draw(screen *ebiten.Image) {}

func (g *Game) Layout(outsideWidth, outsideHeight int) (int, int) {
	return 640, 480
}

func main() {
	ebiten.SetWindowSize(640, 480)
	ebiten.SetWindowTitle("Hello, World!")
	if err := ebiten.RunGame(&Game{}); err != nil {
		log.Fatal(err)
	}
}
```

