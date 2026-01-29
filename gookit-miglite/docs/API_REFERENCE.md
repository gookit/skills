# API Reference

Complete API reference for miglite Go library.

## Core Types

### Migrator

Main migration manager that orchestrates database migrations.

```go
type Migrator struct {
    // internal fields
}
```

#### Constructor Functions

**NewAuto**

Creates a new Migrator with auto-loaded configuration from default file (`./miglite.yaml`).

```go
func NewAuto(fns ...ConfigFn) (*Migrator, error)
```

**Parameters:**
- `fns` - Optional configuration functions to modify loaded config

**Returns:**
- `*Migrator` - Migrator instance
- `error` - Error if configuration fails

**Example:**
```go
mig, err := miglite.NewAuto(func(cfg *config.Config) {
    cfg.Verbose = true
    cfg.Database.MaxOpenConns = 50
})
```

---

**New**

Creates a new Migrator with configuration from specified file.

```go
func New(configFile string, fns ...ConfigFn) (*Migrator, error)
```

**Parameters:**
- `configFile` - Path to configuration file (skips if doesn't exist)
- `fns` - Optional configuration functions

**Returns:**
- `*Migrator` - Migrator instance
- `error` - Error if configuration fails

**Example:**
```go
mig, err := miglite.New("./config/db.yaml", func(cfg *config.Config) {
    cfg.Migrations.Path = "./custom/migrations"
})
```

---

**NewWithConfig**

Creates a new Migrator with pre-configured Config object.

```go
func NewWithConfig(cfg *Config) *Migrator
```

**Parameters:**
- `cfg` - Pre-configured Config object

**Returns:**
- `*Migrator` - Migrator instance

**Example:**
```go
cfg := &config.Config{
    Database: config.Database{
        Driver: "sqlite",
        DSN:    "./app.db",
    },
    Migrations: config.Migrations{
        Path: "./migrations",
    },
}
mig := miglite.NewWithConfig(cfg)
```

#### Methods

**SetSqlDB**

Sets custom database connection to use with migrator.

```go
func (m *Migrator) SetSqlDB(db *sql.DB)
```

**Parameters:**
- `db` - sql.DB database connection

**Example:**
```go
db, _ := sql.Open("postgres", "postgres://...")
mig.SetSqlDB(db)
```

---

**Init**

Initializes migration tracking table in the database.

```go
func (m *Migrator) Init(opt command.InitOption) error
```

**Parameters:**
- `opt` - Initialization options

**Returns:**
- `error` - Error if initialization fails

**Example:**
```go
err := mig.Init(command.InitOption{})
```

---

**Up**

Applies pending migrations to update database schema.

```go
func (m *Migrator) Up(opt command.UpOption) error
```

**Parameters:**
- `opt` - Up operation options

**Returns:**
- `error` - Error if migration fails

**Example:**
```go
err := mig.Up(command.UpOption{
    Yes:    true,
    Number: 5,
})
```

---

**Down**

Rolls back applied migrations to revert schema changes.

```go
func (m *Migrator) Down(opt command.DownOption) error
```

**Parameters:**
- `opt` - Down operation options

**Returns:**
- `error` - Error if rollback fails

**Example:**
```go
err := mig.Down(command.DownOption{
    Yes:    true,
    Number: 2,
})
```

---

**Skip**

Marks migrations as applied without executing them.

```go
func (m *Migrator) Skip(opt command.SkipOption) error
```

**Parameters:**
- `opt` - Skip operation options

**Returns:**
- `error` - Error if skip fails

**Example:**
```go
err := mig.Skip(command.SkipOption{
    Versions: []string{"20260120-150000"},
})
```

---

**Status**

Shows current migration status.

```go
func (m *Migrator) Status(opt command.StatusOption) error
```

**Parameters:**
- `opt` - Status display options

**Returns:**
- `error` - Error if status check fails

**Example:**
```go
err := mig.Status(command.StatusOption{
    JSON: true,
})
```

---

**Show**

Displays database tables.

```go
func (m *Migrator) Show(opt command.ShowOption) error
```

**Parameters:**
- `opt` - Show display options

**Returns:**
- `error` - Error if show fails

**Example:**
```go
err := mig.Show(command.ShowOption{
    Details: true,
})
```

## Configuration Types

### Config

Main configuration structure.

```go
type Config struct {
    Verbose    bool
    Database   Database
    Migrations Migrations
    ConfigFile string
    LogFunc    func(msg string)
}
```

**Fields:**
- `Verbose` - Enable verbose output
- `Database` - Database configuration
- `Migrations` - Migrations configuration
- `ConfigFile` - Path to config file (internal use)
- `LogFunc` - Custom log function handler (internal use)

**Load Function:**

```go
func Load(configFile string) (*Config, error)
```

Loads configuration from file and environment variables.

**Example:**
```go
cfg, err := config.Load("./miglite.yaml")
```

---

### Database

Database connection configuration.

```go
type Database struct {
    Driver    string
    SqlDriver string
    DSN       string

    // Alternative split configuration
    Host     string
    Port     int
    User     string
    Password string
    DBName   string
    SSLMode  string

    // Connection pool settings
    MaxIdleConns    int
    MaxOpenConns    int
    ConnMaxIdleTime int
    ConnMaxLifetime int
}
```

**Fields:**
- `Driver` - Database driver name (mysql, postgres, sqlite, mssql)
- `SqlDriver` - SQL driver name if different from driver
- `DSN` - Connection string
- `Host` - Database host (alternative to DSN)
- `Port` - Database port (alternative to DSN)
- `User` - Database user (alternative to DSN)
- `Password` - Database password (alternative to DSN)
- `DBName` - Database name (alternative to DSN)
- `SSLMode` - SSL mode for PostgreSQL
- `MaxIdleConns` - Maximum idle connections in pool
- `MaxOpenConns` - Maximum open connections in pool
- `ConnMaxIdleTime` - Max time (seconds) connection can be idle
- `ConnMaxLifetime` - Max time (seconds) connection can be reused

**Example:**
```go
db := config.Database{
    Driver: "mysql",
    DSN:    "user:pass@tcp(localhost:3306)/dbname",
    MaxOpenConns: 100,
    MaxIdleConns: 10,
}
```

---

### Migrations

Migrations directory configuration.

```go
type Migrations struct {
    Path      string
    Table     string
    Recursive bool
}
```

**Fields:**
- `Path` - Migration files directory path (supports multiple paths)
- `Table` - Custom migration tracking table name
- `Recursive` - Enable recursive directory search (default: true)

**Methods:**

```go
func (m *Migrations) GetPaths() []string
```

Returns array of migration paths (split by comma).

**Example:**
```go
mig := config.Migrations{
    Path:      "./migrations/core,./migrations/prod",
    Recursive: true,
}
paths := mig.GetPaths() // ["./migrations/core", "./migrations/prod"]
```

## Command Options

### InitOption

Options for initialization operation.

```go
type InitOption struct {
    // Currently no options
}
```

**Example:**
```go
opt := command.InitOption{}
err := mig.Init(opt)
```

---

### UpOption

Options for up migration operation.

```go
type UpOption struct {
    Yes    bool
    DryRun bool
    Number int
}
```

**Fields:**
- `Yes` - Skip confirmation prompt
- `DryRun` - Show SQL without executing
- `Number` - Number of migrations to apply (0 = all)

**Example:**
```go
opt := command.UpOption{
    Yes:    true,
    Number: 5,
    DryRun: false,
}
err := mig.Up(opt)
```

---

### DownOption

Options for down migration operation.

```go
type DownOption struct {
    Yes    bool
    DryRun bool
    Number int
}
```

**Fields:**
- `Yes` - Skip confirmation prompt
- `DryRun` - Show SQL without executing
- `Number` - Number of migrations to rollback (default: 1)

**Example:**
```go
opt := command.DownOption{
    Yes:    true,
    Number: 2,
}
err := mig.Down(opt)
```

---

### SkipOption

Options for skip operation.

```go
type SkipOption struct {
    Versions []string
    All      bool
}
```

**Fields:**
- `Versions` - Specific migration versions to skip
- `All` - Skip all pending migrations

**Example:**
```go
opt := command.SkipOption{
    Versions: []string{"20260120-150000", "20260121-160000"},
}
err := mig.Skip(opt)
```

---

### StatusOption

Options for status display.

```go
type StatusOption struct {
    Compact bool
    JSON    bool
}
```

**Fields:**
- `Compact` - Use compact output format
- `JSON` - Output in JSON format

**Example:**
```go
opt := command.StatusOption{
    JSON: true,
}
err := mig.Status(opt)
```

---

### ShowOption

Options for show command.

```go
type ShowOption struct {
    Details bool
}
```

**Fields:**
- `Details` - Show detailed table information

**Example:**
```go
opt := command.ShowOption{
    Details: true,
}
err := mig.Show(opt)
```

## Helper Types

### ConfigFn

Function type for modifying configuration.

```go
type ConfigFn func(c *config.Config)
```

**Example:**
```go
fn := func(cfg *config.Config) {
    cfg.Verbose = true
    cfg.Database.MaxOpenConns = 50
    cfg.Migrations.Path = "./custom/migrations"
}

mig, err := miglite.NewAuto(fn)
```

## CLI Application

### Creating Custom CLI

```go
package command

func NewApp(name, version, description string) *cliapp.App
```

Creates a new CLI application with all miglite commands.

**Parameters:**
- `name` - Application name
- `version` - Application version
- `description` - Application description

**Returns:**
- `*cliapp.App` - CLI application instance

**Example:**
```go
app := command.NewApp(
    "mymigrate",
    "1.0.0",
    "Custom database migration tool",
)
app.Run()
```

---

### SetBuildInfo

```go
func SetBuildInfo(version, goVersion, buildTime, gitCommit string)
```

Sets build information for CLI application.

**Parameters:**
- `version` - Application version
- `goVersion` - Go version used for build
- `buildTime` - Build timestamp
- `gitCommit` - Git commit hash

**Example:**
```go
command.SetBuildInfo("1.0.0", "go1.21", "2026-01-28", "abc1234")
```

## Error Handling

### Common Errors

**Configuration Errors:**
- Invalid database driver
- Missing DSN
- Invalid migration path

**Connection Errors:**
- Database connection failed
- Permission denied
- Driver not found

**Migration Errors:**
- SQL syntax error
- Migration file not found
- Transaction error

**Example Error Handling:**
```go
mig, err := miglite.NewAuto()
if err != nil {
    switch {
    case strings.Contains(err.Error(), "driver"):
        log.Fatal("Database driver error:", err)
    case strings.Contains(err.Error(), "DSN"):
        log.Fatal("Database connection error:", err)
    default:
        log.Fatal("Configuration error:", err)
    }
}

if err := mig.Up(command.UpOption{Yes: true}); err != nil {
    log.Fatal("Migration failed:", err)
}
```

## Thread Safety

The Migrator is **not** thread-safe. Do not use the same Migrator instance across multiple goroutines.

For concurrent usage:
```go
// Create separate instances
mig1, _ := miglite.NewAuto()
mig2, _ := miglite.NewAuto()

go func() {
    mig1.Up(command.UpOption{Yes: true})
}()

go func() {
    mig2.Status(command.StatusOption{})
}()
```
