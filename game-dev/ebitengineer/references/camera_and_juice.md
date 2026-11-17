# 2D Camera Systems, Viewport Transforms & Game Feel ("Juice") Reference

This module covers genre-agnostic 2D camera math using `ebiten.GeoM`, frame-rate independent exponential damping (lerp), Squirrel Eiserloh's trauma-based screen shake, hitstop (freeze frames), spring-driven squash-and-stretch deformation, sprite pivot transformation order, non-linear easing functions, and zero-allocation particle pools.

---

## 1. 2D Camera Architecture with `ebiten.GeoM`

A 2D camera decouples **World Space** (where entities live across top-down maps, tactics grids, shmup stages, isometric boards, or platformer levels) from **Virtual Screen Space** (e.g. `640x360` or `320x180`).

### 1.1 Exact Transformation Order
To render world entities through a camera with position $(X, Y)$, zoom $Z$, rotation $\theta$, and viewport dimensions $(W, H)$:
1. **Translate world to camera focus**: `Translate(-cam.X, -cam.Y)`
2. **Scale for zoom**: `Scale(cam.Zoom, cam.Zoom)`
3. **Rotate for camera roll/tilt**: `Rotate(cam.Rotation)`
4. **Translate to screen center + shake offset**: `Translate(W/2 + shakeX, H/2 + shakeY)`

```go
package camera

import (
	"fmt"
	"math"

	"github.com/hajimehoshi/ebiten/v2"
)

type Camera struct {
	X, Y               float64 // Current world center position
	TargetX, TargetY   float64 // Desired world target position
	ViewportW          float64 // Virtual screen width
	ViewportH          float64 // Virtual screen height
	Zoom               float64 // 1.0 = 100%
	Rotation           float64 // Radians
	FollowSharpness    float64 // Exponential damping rate (e.g., 10.0)
	ShakeOffsetX       float64
	ShakeOffsetY       float64
	ShakeAngle         float64

	// Optional world boundary clamping
	HasBounds                  bool
	MinX, MinY, MaxX, MaxY     float64
}

func NewCamera(viewportW, viewportH float64) (*Camera, error) {
	if viewportW <= 0 || viewportH <= 0 {
		return nil, fmt.Errorf("camera: invalid viewport dimensions (%.1f x %.1f): must be > 0", viewportW, viewportH)
	}
	return &Camera{
		ViewportW:       viewportW,
		ViewportH:       viewportH,
		Zoom:            1.0,
		FollowSharpness: 12.0,
	}, nil
}

// ViewMatrix returns the World -> Screen transformation matrix.
func (c *Camera) ViewMatrix() ebiten.GeoM {
	var m ebiten.GeoM
	m.Translate(-c.X, -c.Y)
	m.Scale(c.Zoom, c.Zoom)
	m.Rotate(c.Rotation + c.ShakeAngle)
	m.Translate(c.ViewportW*0.5+c.ShakeOffsetX, c.ViewportH*0.5+c.ShakeOffsetY)
	return m
}

// ScreenToWorld converts virtual screen coordinates (e.g., mouse/touch) into world coordinates.
func (c *Camera) ScreenToWorld(screenX, screenY float64) (float64, float64, error) {
	view := c.ViewMatrix()
	if !view.IsInvertible() {
		return 0, 0, fmt.Errorf("camera: view matrix is non-invertible (zoom=%.4f)", c.Zoom)
	}
	view.Invert()
	wx, wy := view.Apply(screenX, screenY)
	return wx, wy, nil
}
```

---

## 2. Frame-Rate Independent Exponential Lerp

Never use `c.X += (c.TargetX - c.X) * 0.1` directly without delta time $dt$, as camera speed will change between 60Hz, 120Hz, and variable WASM frame timings. Use continuous exponential decay:

$$
x(t + \Delta t) = \text{target} + (x(t) - \text{target}) \cdot e^{-\lambda \Delta t}
$$

```go
// ExpDecay performs frame-rate independent exponential interpolation.
// sharpness typically ranges from 4.0 (cinematic float) to 25.0 (snappy lock).
func ExpDecay(current, target, sharpness, dt float64) float64 {
	return target + (current-target)*math.Exp(-sharpness*dt)
}

func (c *Camera) UpdateFollow(dt float64) {
	c.X = ExpDecay(c.X, c.TargetX, c.FollowSharpness, dt)
	c.Y = ExpDecay(c.Y, c.TargetY, c.FollowSharpness, dt)

	if c.HasBounds && c.Zoom > 0 {
		halfW := (c.ViewportW * 0.5) / c.Zoom
		halfH := (c.ViewportH * 0.5) / c.Zoom
		c.X = math.Max(c.MinX+halfW, math.Min(c.MaxX-halfW, c.X))
		c.Y = math.Max(c.MinY+halfH, math.Min(c.MaxY-halfH, c.Y))
	}
}
```

---

## 3. Trauma-Based Screen Shake

Instead of adding raw random pixel offsets, accumulate normalized **Trauma** $\in [0, 1]$ and compute **Shake** $= \text{Trauma}^2$ (or $\text{Trauma}^3$). Quadratic/cubic scaling makes small hits feel subtle while heavy explosions feel dramatic, with smooth decay back to rest:

```go
type TraumaShaker struct {
	Trauma       float64 // Normalized [0.0, 1.0]
	DecayRate    float64 // Trauma lost per second (e.g., 1.5)
	MaxOffsetPx  float64 // Maximum translational offset in virtual pixels (e.g., 12.0)
	MaxAngleRad  float64 // Maximum rotational roll in radians (e.g., 0.05)
	Time         float64 // Elapsed time for deterministic wave sampling
}

func NewTraumaShaker(decayRate, maxOffsetPx, maxAngleRad float64) (*TraumaShaker, error) {
	if decayRate <= 0 {
		return nil, fmt.Errorf("camera: trauma decayRate must be > 0, got %f", decayRate)
	}
	return &TraumaShaker{
		DecayRate:   decayRate,
		MaxOffsetPx: maxOffsetPx,
		MaxAngleRad: maxAngleRad,
	}, nil
}

// AddTrauma injects impact energy (e.g., 0.2 for light hit, 0.6 for explosion).
func (ts *TraumaShaker) AddTrauma(amount float64) {
	if amount <= 0 {
		return
	}
	ts.Trauma = math.Min(1.0, ts.Trauma+amount)
}

// Update decays trauma and applies non-linear shake offsets to the camera.
func (ts *TraumaShaker) Update(dt float64, cam *Camera) {
	if ts.Trauma <= 0 {
		cam.ShakeOffsetX = 0
		cam.ShakeOffsetY = 0
		cam.ShakeAngle = 0
		return
	}

	ts.Time += dt
	shake := ts.Trauma * ts.Trauma // Quadratic intensity curve

	// Pseudo-perlin multi-frequency trigonometric noise (zero allocations)
	nx := math.Sin(ts.Time*37.0)*0.6 + math.Cos(ts.Time*73.0)*0.4
	ny := math.Cos(ts.Time*41.0)*0.6 + math.Sin(ts.Time*89.0)*0.4
	nr := math.Sin(ts.Time*53.0)*0.7 + math.Cos(ts.Time*97.0)*0.3

	cam.ShakeOffsetX = ts.MaxOffsetPx * shake * nx
	cam.ShakeOffsetY = ts.MaxOffsetPx * shake * ny
	cam.ShakeAngle = ts.MaxAngleRad * shake * nr

	ts.Trauma = math.Max(0.0, ts.Trauma-ts.DecayRate*dt)
}
```

---

## 4. Hitstop (Freeze Frames) & Time Dilation

Hitstop briefly pauses gameplay simulation (such as `30ms to 90ms`) on critical impacts, parries, puzzle line clears, or boss kills while keeping camera shake and HUD effects active:

```go
type TimeController struct {
	HitstopRemaining float64 // Seconds remaining in freeze-frame
	TimeScale        float64 // 1.0 = normal speed, 0.25 = slow-mo
}

func NewTimeController() *TimeController {
	return &TimeController{TimeScale: 1.0}
}

// TriggerHitstop freezes world simulation for durationSeconds.
func (tc *TimeController) TriggerHitstop(durationSeconds float64) {
	if durationSeconds > tc.HitstopRemaining {
		tc.HitstopRemaining = durationSeconds
	}
}

// Step computes the effective world delta time.
// Camera shake and UI animations should still receive rawDt.
func (tc *TimeController) Step(rawDt float64) (worldDt float64, frozen bool) {
	if tc.HitstopRemaining > 0 {
		tc.HitstopRemaining -= rawDt
		if tc.HitstopRemaining < 0 {
			tc.HitstopRemaining = 0
		}
		return 0, true
	}
	return rawDt * tc.TimeScale, false
}
```

---

## 5. Spring-Driven Squash & Stretch

Apply damped harmonic oscillator springs to sprite scale $(S_x, S_y)$ while conserving 2D area ($S_x \cdot S_y \approx 1$) so entities deform organically when firing, landing, selecting tiles, or taking hits:

```go
type ScaleSpring struct {
	ScaleX, ScaleY float64
	VelX, VelY     float64
	Stiffness      float64 // e.g., 320.0
	Damping        float64 // e.g., 18.0
}

func NewScaleSpring(stiffness, damping float64) (*ScaleSpring, error) {
	if stiffness <= 0 || damping <= 0 {
		return nil, fmt.Errorf("camera: spring stiffness (%f) and damping (%f) must be > 0", stiffness, damping)
	}
	return &ScaleSpring{
		ScaleX:    1.0,
		ScaleY:    1.0,
		Stiffness: stiffness,
		Damping:   damping,
	}, nil
}

// Impulse deforms the sprite while preserving volume (e.g., sx=1.35, sy=1/1.35).
func (s *ScaleSpring) Impulse(scaleX float64) {
	if scaleX <= 0.1 {
		scaleX = 0.1
	}
	s.ScaleX = scaleX
	s.ScaleY = 1.0 / scaleX
}

func (s *ScaleSpring) Update(dt float64) {
	// Hooke's Law + velocity damping toward rest scale (1.0, 1.0)
	forceX := (1.0 - s.ScaleX) * s.Stiffness
	forceY := (1.0 - s.ScaleY) * s.Stiffness

	s.VelX = (s.VelX + forceX*dt) * math.Exp(-s.Damping*dt)
	s.VelY = (s.VelY + forceY*dt) * math.Exp(-s.Damping*dt)

	s.ScaleX += s.VelX * dt
	s.ScaleY += s.VelY * dt
}
```

---

## 6. Sprite Pivot Transformation Order (`Transform2D`)

2D affine matrix multiplication in `ebiten.GeoM` is non-commutative. Whenever scaling or rotating a sprite around a local pivot point `(OriginX, OriginY)` and placing it at world coordinates `(X, Y)`, apply operations in strict order:

1. `m.Translate(-OriginX, -OriginY)`: Shift the local pivot to `(0, 0)`.
2. `m.Scale(ScaleX, ScaleY)`: Scale around the pivot.
3. `m.Rotate(Rotation)`: Rotate in radians around the pivot.
4. `m.Translate(OriginX+X, OriginY+Y)`: Translate to the final world position.

```go
type Transform2D struct {
	X, Y     float64 // World position
	ScaleX   float64 // Horizontal scale
	ScaleY   float64 // Vertical scale
	Rotation float64 // Angle in radians
	OriginX  float64 // Pivot offset X
	OriginY  float64 // Pivot offset Y
}

func (t Transform2D) GetGeoM() ebiten.GeoM {
	var m ebiten.GeoM
	m.Translate(-t.OriginX, -t.OriginY)
	m.Scale(t.ScaleX, t.ScaleY)
	m.Rotate(t.Rotation)
	m.Translate(t.OriginX+t.X, t.OriginY+t.Y)
	return m
}
```

---

## 7. Non-Linear Easing Functions

Normalized easing curves (`t` in `[0.0, 1.0]`) drive camera transitions, UI pop-ins, hit-flash fades, and tweened sprite animations cleanly:

```go
func EaseLinear(t float64) float64 { return t }

func EaseInQuad(t float64) float64 { return t * t }

func EaseOutQuad(t float64) float64 { return t * (2.0 - t) }

func EaseInOutCubic(t float64) float64 {
	if t < 0.5 {
		return 4.0 * t * t * t
	}
	return 1.0 - math.Pow(-2.0*t+2.0, 3.0)/2.0
}

func EaseElasticOut(t float64) float64 {
	if t <= 0 {
		return 0
	}
	if t >= 1 {
		return 1
	}
	p := 0.3
	return math.Pow(2.0, -10.0*t)*math.Sin((t-p/4.0)*(2.0*math.Pi)/p) + 1.0
}
```

---

## 8. Zero-Allocation Particle System Pool

Pre-allocate a fixed `[]Particle` pool, reusable glow texture (with premultiplied RGBA), and persistent `ebiten.DrawImageOptions` struct during initialization so spawning, updating, and rendering particles with additive blending (`ebiten.BlendLighter`) causes zero heap allocations in `Draw()`:

```go
package vfx

import (
	"fmt"
	"image"
	"image/color"
	"math"
	"math/rand/v2"

	"github.com/hajimehoshi/ebiten/v2"
)

// PremultiplyRGBA converts straight RGB + Alpha into valid premultiplied color.RGBA (R, G, B <= A).
func PremultiplyRGBA(r, g, b, a uint8) color.RGBA {
	alpha := uint16(a)
	return color.RGBA{
		R: uint8((uint16(r)*alpha + 127) / 255),
		G: uint8((uint16(g)*alpha + 127) / 255),
		B: uint8((uint16(b)*alpha + 127) / 255),
		A: a,
	}
}

func LerpColor(c1, c2 color.RGBA, t float64) color.RGBA {
	if t <= 0 {
		return c1
	}
	if t >= 1 {
		return c2
	}
	r := uint8(float64(c1.R) + t*(float64(c2.R)-float64(c1.R)))
	g := uint8(float64(c1.G) + t*(float64(c2.G)-float64(c1.G)))
	b := uint8(float64(c1.B) + t*(float64(c2.B)-float64(c1.B)))
	a := uint8(float64(c1.A) + t*(float64(c2.A)-float64(c1.A)))
	if r > a {
		r = a
	}
	if g > a {
		g = a
	}
	if b > a {
		b = a
	}
	return color.RGBA{R: r, G: g, B: b, A: a}
}

type Particle struct {
	X, Y       float64
	VX, VY     float64
	AX, AY     float64
	Life       float64
	Age        float64
	StartSize  float64
	EndSize    float64
	StartColor color.RGBA
	EndColor   color.RGBA
	Additive   bool
	Active     bool
}

type ParticleSystem struct {
	pool    []Particle
	texture *ebiten.Image
	drawOp  ebiten.DrawImageOptions
}

func NewParticleSystem(maxParticles int) (*ParticleSystem, error) {
	if maxParticles <= 0 {
		return nil, fmt.Errorf("vfx: maxParticles must be > 0, got %d", maxParticles)
	}
	img := image.NewRGBA(image.Rect(0, 0, 16, 16))
	for y := 0; y < 16; y++ {
		for x := 0; x < 16; x++ {
			d := math.Hypot(float64(x)+0.5-8.0, float64(y)+0.5-8.0) - 8.0
			if d < 0 {
				alpha := uint8(math.Min(255.0, math.Max(0.0, (-d/8.0)*255.0)))
				img.SetRGBA(x, y, PremultiplyRGBA(255, 255, 255, alpha))
			}
		}
	}
	return &ParticleSystem{
		pool:    make([]Particle, maxParticles),
		texture: ebiten.NewImageFromImage(img),
	}, nil
}

func (ps *ParticleSystem) EmitExplosion(x, y float64, count int) {
	spawned := 0
	for i := range ps.pool {
		if !ps.pool[i].Active {
			p := &ps.pool[i]
			p.Active = true
			p.X = x
			p.Y = y
			angle := rand.Float64() * 2.0 * math.Pi
			speed := 50.0 + rand.Float64()*150.0
			p.VX = math.Cos(angle) * speed
			p.VY = math.Sin(angle) * speed
			p.AX = 0
			p.AY = 40.0
			p.Life = 0.4 + rand.Float64()*0.4
			p.Age = 0
			p.StartSize = 1.2 + rand.Float64()*0.8
			p.EndSize = 0.1
			p.StartColor = PremultiplyRGBA(255, 200, 50, 255)
			p.EndColor = PremultiplyRGBA(200, 30, 10, 0)
			p.Additive = true

			spawned++
			if spawned >= count {
				break
			}
		}
	}
}

func (ps *ParticleSystem) Update(dt float64) {
	for i := range ps.pool {
		p := &ps.pool[i]
		if !p.Active {
			continue
		}
		p.Age += dt
		if p.Age >= p.Life {
			p.Active = false
			continue
		}
		p.VX += p.AX * dt
		p.VY += p.AY * dt
		p.X += p.VX * dt
		p.Y += p.VY * dt
	}
}

func (ps *ParticleSystem) Draw(screen *ebiten.Image) {
	for i := range ps.pool {
		p := &ps.pool[i]
		if !p.Active {
			continue
		}
		progress := p.Age / p.Life
		size := p.StartSize + progress*(p.EndSize-p.StartSize)
		curColor := LerpColor(p.StartColor, p.EndColor, progress)

		ps.drawOp.GeoM.Reset()
		ps.drawOp.GeoM.Translate(-8, -8)
		ps.drawOp.GeoM.Scale(size, size)
		ps.drawOp.GeoM.Translate(p.X, p.Y)

		ps.drawOp.ColorScale.Reset()
		ps.drawOp.ColorScale.ScaleWithColor(curColor)

		if p.Additive {
			ps.drawOp.Blend = ebiten.BlendLighter
		} else {
			ps.drawOp.Blend = ebiten.BlendSourceOver
		}

		screen.DrawImage(ps.texture, &ps.drawOp)
	}
}
```
