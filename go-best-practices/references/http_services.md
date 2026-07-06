# Idiomatic HTTP Services in Go

Guidelines for building maintainable and testable HTTP services.

## Core Design Rules

*   Keep `main.go` minimal and delegate the setup to a `run` function. This function should accept a `context.Context`, an `io.Writer` for logging, and a function to retrieve environment variables.
*   Handle `os.Interrupt` and `syscall.SIGTERM` to perform a graceful server shutdown.
*   Inject handler dependencies explicitly using constructors rather than relying on global state.
*   Define interfaces on the client or consumer side rather than the implementation side.

## Structure Example

```go
package main

import (
	"context"
	"fmt"
	"io"
	"net"
	"net/http"
	"os"
	"os/signal"
	"time"
)

func main() {
	ctx := context.Background()
	if err := run(ctx, os.Stdout, os.Getenv); err != nil {
		fmt.Fprintf(os.Stderr, "%s\n", err)
		os.Exit(1)
	}
}

func run(ctx context.Context, w io.Writer, getEnv func(string) string) error {
	ctx, cancel := signal.NotifyContext(ctx, os.Interrupt)
	defer cancel()

	// Setup dependencies here (e.g., database connections)

	httpServer := &http.Server{
		Addr: net.JoinHostPort("0.0.0.0", "8080"),
	}

	go func() {
		if err := httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			fmt.Fprintf(w, "server error: %s\n", err)
		}
	}()

	<-ctx.Done()

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	return httpServer.Shutdown(shutdownCtx)
}
```

## Routing and Handlers

*   Use standard library routing via `http.ServeMux` (Go 1.22+ supports HTTP methods and wildcards).
*   Structure the server as a custom struct implementing `http.Handler` to keep route definitions and handlers cohesive.

```go
type Server struct {
	db     *DB
	router *http.ServeMux
}

func NewServer(db *DB) *Server {
	s := &Server{
		db:     db,
		router: http.NewServeMux(),
	}
	s.routes()
	return s
}

func (s *Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	s.router.ServeHTTP(w, r)
}
```

## Middleware

Extend or wrap handler behavior using middleware functions.

```go
func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		log.Printf("%s %s %s", r.Method, r.URL.Path, time.Since(start))
	})
}
```

