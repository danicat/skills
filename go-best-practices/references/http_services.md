# Idiomatic HTTP Services in Go

Best practices for building robust, maintainable, and testable web services.

## Core Principles

1.  **Use a `run` function**: Keep `main.go` minimal and move setup logic to a `run` function that accepts a `context.Context`, `io.Writer` (for logs), and environment variables.
2.  **Graceful Shutdown**: Always handle `os.Interrupt` and `syscall.SIGTERM` to shut down the server gracefully.
3.  **Constructors for Handlers**: Use constructors to inject dependencies into your handlers.
4.  **Avoid Global State**: Pass dependencies (DB, logger) explicitly.
5.  **Small Interfaces**: Define interfaces on the consumer side.

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

	// 1. Setup dependencies
	// db, err := setupDB(getEnv("DB_URL"))

	// 2. Initialize handlers
	// srv := server.NewServer(db)

	httpServer := &http.Server{
		Addr:    net.JoinHostPort("0.0.0.0", "8080"),
		// Handler: srv,
	}

	// 3. Start server in a goroutine
	go func() {
		if err := httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			fmt.Fprintf(w, "server error: %s\n", err)
		}
	}()

	// 4. Wait for interrupt signal
	<-ctx.Done()

	// 5. Shutdown with timeout
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	return httpServer.Shutdown(shutdownCtx)
}
```

## Routing and Handlers

*   **Standard Library**: Use `http.ServeMux` (Go 1.22+ supports methods and wildcards).
*   **Decoupled Handlers**: Define your server as a struct that implements `http.Handler`.

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

Wrap `http.Handler` to add cross-cutting concerns (logging, auth, metrics).

```go
func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		log.Printf("%s %s %s", r.Method, r.URL.Path, time.Since(start))
	})
}
```
