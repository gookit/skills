# Library Usage Guide

Comprehensive guide for using miglite as a Go library in your applications.

## Installation

```bash
go get github.com/gookit/miglite
```

**Important**: Add your database driver dependency:

```bash
# MySQL
go get github.com/go-sql-driver/mysql

# PostgreSQL
go get github.com/lib/pq
go get github.com/jackc/pgx/v5  # Alternative

# SQLite (CGO-free recommended)
go get modernc.org/sqlite
go get github.com/glebarez/go-sqlite  # Alternative
go get github.com/ncruces/go-sqlite3  # Alternative

# SQLite (requires CGO)
go get github.com/mattn/go-sqlite3

# MSSQL
go get github.com/microsoft/go-mssqldb
```

## Basic Usage Examples

### Example 1: Simple Migration Runner

```go
package main

import (
    "log"

    "github.com/gookit/miglite"
    "github.com/gookit/miglite/pkg/command"
    "github.com/gookit/miglite/pkg/config"

    _ "github.com/go-sql-driver/mysql"
)

func main() {
    // Create migrator with auto-loaded config
    mig, err := miglite.NewAuto(func(cfg *config.Config) {
        // Optional: modify config
        cfg.Verbose = true
    })
    if err != nil {
        log.Fatal(err)
    }

    // Initialize migration table
    if err := mig.Init(command.InitOption{}); err != nil {
        log.Fatal(err)
    }

    // Run up migrations
    if err := mig.Up(command.UpOption{
        Yes: true, // Don't ask for confirmation
    }); err != nil {
        log.Fatal(err)
    }

    log.Println("Migrations applied successfully!")
}
```

### Example 2: Custom Configuration

```go
package main

import (
    "log"

    "github.com/gookit/miglite"
    "github.com/gookit/miglite/pkg/command"
    "github.com/gookit/miglite/pkg/config"

    _ "modernc.org/sqlite"
)

func main() {
    // Load config from custom file
    mig, err := miglite.New("./config/db.yaml", func(cfg *config.Config) {
        // Override settings
        cfg.Database.DSN = "./app.db"
        cfg.Migrations.Path = "./db/migrations"
    })
    if err != nil {
        log.Fatal(err)
    }

    // Run migrations
    if err := mig.Up(command.UpOption{Yes: true}); err != nil {
        log.Fatal(err)
    }
}
```

### Example 3: Using Existing Database Connection

```go
package main

import (
    "database/sql"
    "log"

    "github.com/gookit/miglite"
    "github.com/gookit/miglite/pkg/command"
    "github.com/gookit/miglite/pkg/config"

    _ "github.com/lib/pq"
)

func main() {
    // Open database connection
    db, err := sql.Open("postgres",
        "host=localhost port=5432 user=postgres password=secret dbname=myapp sslmode=disable")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // Create config
    cfg := &config.Config{
        Database: config.Database{
            Driver: "postgres",
        },
        Migrations: config.Migrations{
            Path:      "./migrations",
            Recursive: true,
        },
    }

    // Create migrator with existing connection
    mig := miglite.NewWithConfig(cfg)
    mig.SetSqlDB(db)

    // Run migrations
    if err := mig.Up(command.UpOption{Yes: true}); err != nil {
        log.Fatal(err)
    }
}
```

### Example 4: Programmatic Migration Management

```go
package main

import (
    "log"

    "github.com/gookit/miglite"
    "github.com/gookit/miglite/pkg/command"

    _ "github.com/go-sql-driver/mysql"
)

func main() {
    mig, err := miglite.NewAuto()
    if err != nil {
        log.Fatal(err)
    }

    // Initialize
    if err := mig.Init(command.InitOption{}); err != nil {
        log.Fatal("Init failed:", err)
    }

    // Check status
    if err := mig.Status(command.StatusOption{}); err != nil {
        log.Fatal("Status check failed:", err)
    }

    // Apply migrations
    if err := mig.Up(command.UpOption{
        Number: 5, // Apply only 5 migrations
        Yes:    true,
    }); err != nil {
        log.Fatal("Up failed:", err)
    }

    // Rollback if needed
    needRollback := false
    if needRollback {
        if err := mig.Down(command.DownOption{
            Number: 1, // Rollback last migration
            Yes:    true,
        }); err != nil {
            log.Fatal("Down failed:", err)
        }
    }

    // Show database tables
    if err := mig.Show(command.ShowOption{}); err != nil {
        log.Fatal("Show failed:", err)
    }
}
```

## Advanced Usage

### Error Handling

```go
package main

import (
    "errors"
    "log"

    "github.com/gookit/miglite"
    "github.com/gookit/miglite/pkg/command"
)

func main() {
    mig, err := miglite.NewAuto()
    if err != nil {
        log.Fatalf("Failed to create migrator: %v", err)
    }

    // Apply migrations with error handling
    if err := mig.Up(command.UpOption{Yes: true}); err != nil {
        // Check error type
        var migErr *command.MigrationError
        if errors.As(err, &migErr) {
            log.Printf("Migration %s failed: %v", migErr.Version, migErr.Err)
        } else {
            log.Printf("Migration failed: %v", err)
        }
        return
    }

    log.Println("Success!")
}
```

### Using with Different Environments

```go
package main

import (
    "log"
    "os"

    "github.com/gookit/miglite"
    "github.com/gookit/miglite/pkg/command"
)

func main() {
    env := os.Getenv("APP_ENV")
    if env == "" {
        env = "development"
    }

    // Load environment-specific config
    configFile := "./config/" + env + ".yaml"

    mig, err := miglite.New(configFile)
    if err != nil {
        log.Fatal(err)
    }

    if err := mig.Up(command.UpOption{Yes: true}); err != nil {
        log.Fatal(err)
    }
}
```

### Integration with Web Frameworks

#### Gin Framework

```go
package main

import (
    "log"

    "github.com/gin-gonic/gin"
    "github.com/gookit/miglite"
    "github.com/gookit/miglite/pkg/command"

    _ "github.com/go-sql-driver/mysql"
)

func main() {
    // Run migrations before starting server
    if err := runMigrations(); err != nil {
        log.Fatal(err)
    }

    // Start web server
    r := gin.Default()
    r.GET("/ping", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "pong"})
    })
    r.Run(":8080")
}

func runMigrations() error {
    mig, err := miglite.NewAuto()
    if err != nil {
        return err
    }

    return mig.Up(command.UpOption{Yes: true})
}
```

#### Echo Framework

```go
package main

import (
    "log"

    "github.com/labstack/echo/v4"
    "github.com/gookit/miglite"
    "github.com/gookit/miglite/pkg/command"

    _ "github.com/lib/pq"
)

func main() {
    // Run migrations
    if err := runMigrations(); err != nil {
        log.Fatal(err)
    }

    // Setup Echo
    e := echo.New()
    e.GET("/health", func(c echo.Context) error {
        return c.String(200, "OK")
    })
    e.Logger.Fatal(e.Start(":8080"))
}

func runMigrations() error {
    mig, err := miglite.NewAuto()
    if err != nil {
        return err
    }

    return mig.Up(command.UpOption{Yes: true})
}
```

### Testing Integration

```go
package myapp

import (
    "database/sql"
    "testing"

    "github.com/gookit/miglite"
    "github.com/gookit/miglite/pkg/command"
    "github.com/gookit/miglite/pkg/config"

    _ "modernc.org/sqlite"
)

func setupTestDB(t *testing.T) *sql.DB {
    // Create in-memory database
    db, err := sql.Open("sqlite", ":memory:")
    if err != nil {
        t.Fatal(err)
    }

    // Run migrations
    cfg := &config.Config{
        Database: config.Database{
            Driver: "sqlite",
        },
        Migrations: config.Migrations{
            Path: "./migrations",
        },
    }

    mig := miglite.NewWithConfig(cfg)
    mig.SetSqlDB(db)

    if err := mig.Init(command.InitOption{}); err != nil {
        t.Fatal(err)
    }

    if err := mig.Up(command.UpOption{Yes: true}); err != nil {
        t.Fatal(err)
    }

    return db
}

func TestUserRepository(t *testing.T) {
    db := setupTestDB(t)
    defer db.Close()

    // Run your tests
    // ...
}
```

## Building Custom Migration Tool

Create your own CLI tool with only the drivers you need:

```go
package main

import (
    "github.com/gookit/miglite/pkg/command"

    // Import only the drivers you need
    _ "github.com/go-sql-driver/mysql"
    _ "github.com/lib/pq"
)

var (
    Version   = "1.0.0"
    BuildTime = "2026-01-28"
    GitCommit = "abc1234"
)

func main() {
    // Optional: Set build info
    command.SetBuildInfo(Version, "go1.21", BuildTime, GitCommit)

    // Create CLI app
    app := command.NewApp(
        "mymigrate",                   // App name
        Version,                        // Version
        "Custom database migration tool", // Description
    )

    // Run the application
    app.Run()
}
```

### Build Script

**Makefile:**

```makefile
VERSION := 1.0.0
BUILD_TIME := $(shell date -u '+%Y-%m-%d_%H:%M:%S')
GIT_COMMIT := $(shell git rev-parse --short HEAD)
LDFLAGS := -X main.Version=$(VERSION) \
           -X main.BuildTime=$(BUILD_TIME) \
           -X main.GitCommit=$(GIT_COMMIT)

build:
	go build -ldflags "$(LDFLAGS)" -o mymigrate ./cmd/mymigrate

install:
	go install -ldflags "$(LDFLAGS)" ./cmd/mymigrate

release:
	GOOS=linux GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o mymigrate-linux-amd64 ./cmd/mymigrate
	GOOS=darwin GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o mymigrate-darwin-amd64 ./cmd/mymigrate
	GOOS=windows GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o mymigrate-windows-amd64.exe ./cmd/mymigrate
```

**Build Commands:**

```bash
# Development build
make build

# Install locally
make install

# Cross-platform release
make release
```

## Docker Integration

### Dockerfile

```dockerfile
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o miglite ./cmd/miglite

FROM alpine:latest
RUN apk --no-cache add ca-certificates

WORKDIR /app
COPY --from=builder /app/miglite /usr/local/bin/
COPY migrations /app/migrations

ENV DATABASE_URL=""
ENV MIGRATIONS_PATH="/app/migrations"

CMD ["miglite", "up", "--yes"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  migrate:
    build: .
    depends_on:
      - db
    environment:
      DATABASE_URL: "postgres://host=db port=5432 user=myapp password=secret dbname=myapp_dev sslmode=disable"
      MIGRATIONS_PATH: "/app/migrations"
    command: ["miglite", "up", "--yes"]

volumes:
  postgres_data:
```

## Best Practices

### 1. Always Handle Errors

```go
if err := mig.Up(command.UpOption{Yes: true}); err != nil {
    log.Fatalf("Migration failed: %v", err)
}
```

### 2. Use Configuration Functions

```go
mig, err := miglite.NewAuto(func(cfg *config.Config) {
    cfg.Verbose = true
    cfg.Database.MaxOpenConns = 100
    cfg.Migrations.Path = "./custom/migrations"
})
```

### 3. Separate Migration Logic

```go
func runMigrations() error {
    mig, err := miglite.NewAuto()
    if err != nil {
        return err
    }
    return mig.Up(command.UpOption{Yes: true})
}

func main() {
    if err := runMigrations(); err != nil {
        log.Fatal(err)
    }
    // Continue with application startup
}
```

### 4. Use Environment-Specific Configs

```go
func getConfigFile() string {
    env := os.Getenv("APP_ENV")
    switch env {
    case "production":
        return "./config/prod.yaml"
    case "staging":
        return "./config/staging.yaml"
    default:
        return "./config/dev.yaml"
    }
}
```

### 5. Implement Health Checks

```go
func checkMigrations() error {
    mig, err := miglite.NewAuto()
    if err != nil {
        return err
    }
    return mig.Status(command.StatusOption{})
}
```
