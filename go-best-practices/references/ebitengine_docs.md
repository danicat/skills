# Ebitengine Best Practices

Best practices for building 2D games with [Ebitengine](https://ebitengine.org/).

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

## Standard Project Structure

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

## Performance Tips

1.  **Batch Drawing**: Draw multiple items using the same image/texture in succession to minimize draw calls.
2.  **Avoid Real-time Allocation**: Pre-allocate objects in `init()` or `NewGame()` to avoid GC pauses during `Update` or `Draw`.
3.  **Use `Image.SubImage`**: Efficiently use spritesheets.
4.  **Offscreen Images**: Use offscreen images for complex compositions that don't change every frame.

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
