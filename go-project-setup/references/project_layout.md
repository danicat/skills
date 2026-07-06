Source: https://go.dev/doc/modules/layout

# Organizing a Go Module

This guide details recommended patterns for structuring Go projects by type.

---

### Basic Package

A basic package keeps all source files in the project's root folder, consisting of a single module and a single package whose name matches the last path component of the module.

Project structure:

```
project-root-directory/
  go.mod
  modname.go
  modname_test.go
```

*(Note: File and package names here are examples.)*

If hosted at `github.com/someuser/modname`, the `go.mod` file declares:

```
module github.com/someuser/modname
```

`modname.go` declares the package:

```
package modname

// Code goes here
```

Users import this package with:

```go
import "github.com/someuser/modname"
```

A package can be split into multiple files in the same folder:

```
project-root-directory/
  go.mod
  modname.go
  modname_test.go
  auth.go
  auth_test.go
  hash.go
  hash_test.go
```

All files in this folder use `package modname`.

---

### Basic Command

Command-line tools are structured according to size: simple tools can reside in a single Go file declaring a main function, while larger programs split code across multiple files declaring package main:

```
project-root-directory/
  go.mod
  auth.go
  auth_test.go
  client.go
  main.go
```

The `main` function is usually in `main.go`, but any file name works.

If hosted at `github.com/someuser/modname`, the `go.mod` file declares:

```
module github.com/someuser/modname
```

Install it using:

```bash
go install github.com/someuser/modname@latest
```

---

### Supporting Packages

Larger tools or packages can put code into helper packages. Keep them in an `internal/` folder so other projects cannot import them. This lets you change code without breaking other users.

Structure:

```
project-root-directory/
  internal/
    auth/
      auth.go
      auth_test.go
    hash/
      hash.go
      hash_test.go
  go.mod
  modname.go
  modname_test.go
```

`modname.go` imports the internal package:

```go
import "github.com/someuser/modname/internal/auth"
```

For commands, the layout is the same but the root files use `package main`.

---

### Multiple Packages

A module can have many public packages. Place each in its own folder:

```
project-root-directory/
  go.mod
  modname.go
  modname_test.go
  auth/
    auth.go
    auth_test.go
    token/
      token.go
      token_test.go
  hash/
    hash.go
  internal/
    trace/
      trace.go
```

If the module is named `github.com/someuser/modname`, users import them like this:

```go
import "github.com/someuser/modname"
import "github.com/someuser/modname/auth"
import "github.com/someuser/modname/auth/token"
import "github.com/someuser/modname/hash"
```

The package in `internal/trace` cannot be imported outside this module. Keep packages internal unless they must be public.

---

### Multiple Commands

Multiple apps in the same repository use separate folders:

```
project-root-directory/
  go.mod
  internal/
    ... shared internal packages
  prog1/
    main.go
  prog2/
    main.go
```

Each app folder uses `package main`. The `internal/` folder holds shared code.

Install these programs with:

```bash
go install github.com/someuser/modname/prog1@latest
go install github.com/someuser/modname/prog2@latest
```

If a project has both packages and commands, put commands in a `cmd/` folder.

---

### Packages and Commands in One Repository

For projects with both importable packages and commands, use this structure:

```
project-root-directory/
  go.mod
  modname.go
  modname_test.go
  auth/
    auth.go
    auth_test.go
  internal/
    ... internal packages
  cmd/
    prog1/
      main.go
    prog2/
      main.go
```

Users import the packages:

```go
import "github.com/someuser/modname"
import "github.com/someuser/modname/auth"
```

And install the commands:

```bash
go install github.com/someuser/modname/cmd/prog1@latest
go install github.com/someuser/modname/cmd/prog2@latest
```

---

### Server Projects

Servers rarely expose packages for other projects. Keep Go code in `internal/` and put entry points in `cmd/`:

```
project-root-directory/
  go.mod
  internal/
    auth/
      ...
    metrics/
      ...
    model/
      ...
  cmd/
    api-server/
      main.go
    metrics-analyzer/
      main.go
```

If internal packages become useful elsewhere, split them into separate modules.