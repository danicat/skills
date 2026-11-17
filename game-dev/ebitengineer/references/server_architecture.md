# WebAssembly Server Architecture & Google Cloud Run Reference

This reference covers hosting WebAssembly (WASM) Ebitengine builds on **Google Cloud Run** and providing server-side REST API endpoints for global state tracking (such as high scores and leaderboards).

> **Official GCP Reference Implementation**: See [devrel-demos/gemini-cli-match3-golang/Dockerfile](https://github.com/GoogleCloudPlatform/devrel-demos/blob/main/codelabs/gemini-cli/gemini-cli-match3-golang/Dockerfile) for the authoritative Dockerfile build pipeline.

---

## 1. Google Cloud Run Hosting Architecture

Google Cloud Run is the primary target for hosting Ebitengine WASM applications because:
- **Automatic Scaling to Zero**: Zero cost when idle; scales instantly on incoming traffic spikes.
- **Managed HTTPS & Custom Domains**: Automatic TLS termination and global edge distribution.
- **Unified Single-Binary / Container**: The Go server embeds static WASM assets (`//go:embed public/*`) and serves both the game UI and backend REST APIs from one container image.

---

## 2. Server Implementation (`cmd/server/main.go`)

Cloud Run injects a `PORT` environment variable (default `8080`). The Go server binds to `:$PORT` and serves embedded public web assets alongside fail-fast REST API endpoints:

```go
package main

import (
	"cmp"
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"log"
	"net/http"
	"os"
	"slices"
	"sync"
	"time"
)

const maxScores = 100

//go:embed public/*
var publicFS embed.FS

type ScoreEntry struct {
	PlayerName string    `json:"player_name"`
	Score      int       `json:"score"`
	Timestamp  time.Time `json:"timestamp"`
}

type HighScoreStore struct {
	mu     sync.RWMutex
	scores []ScoreEntry
}

func main() {
	store := &HighScoreStore{
		scores: make([]ScoreEntry, 0, 64),
	}

	// Sub-filesystem for embedded public WASM web assets
	staticFS, err := fs.Sub(publicFS, "public")
	if err != nil {
		log.Fatalf("server: initialize static filesystem: %v", err)
	}

	http.Handle("/", http.FileServer(http.FS(staticFS)))

	// Leaderboard REST API Endpoints
	http.HandleFunc("/api/v1/scores", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch r.Method {
		case http.MethodGet:
			store.mu.RLock()
			payload, err := json.Marshal(store.scores)
			store.mu.RUnlock()
			if err != nil {
				http.Error(w, fmt.Sprintf("server: marshal scores: %v", err), http.StatusInternalServerError)
				return
			}
			if _, err := w.Write(payload); err != nil {
				log.Printf("server: write scores response: %v", err)
			}

		case http.MethodPost:
			r.Body = http.MaxBytesReader(w, r.Body, 4096)
			var entry ScoreEntry
			if err := json.NewDecoder(r.Body).Decode(&entry); err != nil {
				http.Error(w, fmt.Sprintf("server: invalid score JSON: %v", err), http.StatusBadRequest)
				return
			}
			if entry.PlayerName == "" || entry.Score < 0 {
				http.Error(w, "server: player_name required and score must be >= 0", http.StatusBadRequest)
				return
			}
			entry.Timestamp = time.Now().UTC()

			store.mu.Lock()
			store.scores = append(store.scores, entry)
			slices.SortFunc(store.scores, func(a, b ScoreEntry) int {
				return cmp.Compare(b.Score, a.Score)
			})
			if len(store.scores) > maxScores {
				store.scores = store.scores[:maxScores]
			}
			store.mu.Unlock()

			w.WriteHeader(http.StatusCreated)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	srv := &http.Server{
		Addr:              ":" + port,
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       10 * time.Second,
		WriteTimeout:      10 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	log.Printf("Server starting on port %s...", port)
	if err := srv.ListenAndServe(); err != nil {
		log.Fatalf("server: ListenAndServe failed: %v", err)
	}
}
```

---

## 3. Reference Cloud Run Dockerfile (`Dockerfile`)

Based directly on the GCP [gemini-cli-match3-golang Dockerfile](https://github.com/GoogleCloudPlatform/devrel-demos/blob/main/codelabs/gemini-cli/gemini-cli-match3-golang/Dockerfile), the container build compiles the WebAssembly payload, bundles the web assets into `public/`, compiles the server binary, and runs in a minimal container:

```dockerfile
# Build stage 1: Compile the Go server and WASM
FROM golang:1.27-alpine AS builder

WORKDIR /app

# Install dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# 1. Build WASM binary into public directory
RUN GOOS=js GOARCH=wasm go build -o public/game.wasm ./cmd/game

# 2. Bundle static web assets and Go WASM glue into public directory
# Note: Go 1.24+ moved wasm_exec.js to lib/wasm/; fallback to misc/wasm/ for older toolchains
RUN mkdir -p public/assets && \
    cp index.html public/ && \
    if [ -f "$(go env GOROOT)/lib/wasm/wasm_exec.js" ]; then \
        cp "$(go env GOROOT)/lib/wasm/wasm_exec.js" public/wasm_exec.js; \
    else \
        cp "$(go env GOROOT)/misc/wasm/wasm_exec.js" public/wasm_exec.js; \
    fi && \
    cp -r assets/* public/assets/

# 3. Build HTTP Server binary
RUN CGO_ENABLED=0 GOOS=linux go build -o /server ./cmd/server

# Stage 2: Final minimal runtime container for Cloud Run
FROM gcr.io/distroless/static-debian12

COPY --from=builder /server /server

EXPOSE 8080
ENTRYPOINT ["/server"]
```

### OS Location Variations for `wasm_exec.js`

When copying `wasm_exec.js` locally outside Docker, query `$(go env GOROOT)` to resolve the active path automatically (Go `1.24+` uses `lib/wasm/wasm_exec.js`; Go `1.23` and earlier use `misc/wasm/wasm_exec.js`):
- **Go Toolchain Query (Cross-Platform)**: `$(go env GOROOT)/lib/wasm/wasm_exec.js` (or `misc/wasm/wasm_exec.js`)
- **Linux / Docker Container**: `/usr/local/go/lib/wasm/wasm_exec.js`
- **macOS (Homebrew Apple Silicon)**: `/opt/homebrew/opt/go/libexec/lib/wasm/wasm_exec.js`
- **macOS (Homebrew Intel)**: `/usr/local/opt/go/libexec/lib/wasm/wasm_exec.js`
- **Windows**: `%GOROOT%\lib\wasm\wasm_exec.js`

---

## 4. Google Cloud Run Deployment

Deploy directly from source to Google Cloud Run (Cloud Build builds the container and pushes to Artifact Registry automatically):

```bash
gcloud run deploy ebiten-wasm-game \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```
