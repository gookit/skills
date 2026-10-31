# Go library

Module `github.com/gookit/miglite` (go 1.20). Depends on goutil and goccy/go-yaml but on no DB driver:
import yours (`_ "github.com/go-sql-driver/mysql"`, `_ "github.com/lib/pq"`, `_ "modernc.org/sqlite"`,
pgx, mattn/go-sqlite3, go-mssqldb ...).

## Constructors (package miglite)

```go
func NewAuto(fns ...ConfigFn) (*Migrator, error)               // load .env + miglite.yaml + env, then apply fns
func New(configFile string, fns ...ConfigFn) (*Migrator, error)
func NewWithConfig(cfg *Config) *Migrator                       // no loading at all
func NewWithConfigAndFS(cfg *Config, fsys fs.FS) *Migrator
type ConfigFn func(c *Config)
```

`Config`, `Database`, `Migrations` are aliases of the internal types; fields as in 02-config.md
(`Config.Verbose`, `.Database.{Driver,SqlDriver,DSN,...}`, `.Migrations.{Path,Recursive}`, `.LogFunc`, `.Output`).

With `NewWithConfig` you build everything yourself: set `Database.Driver` (normalised name, e.g.
`"postgres"`), `SqlDriver` (name registered with database/sql), `DSN`, `Migrations.Path`, and
`Migrations.Recursive: true` if you want subdirectories (zero value = not recursive).

## Methods

```go
func (m *Migrator) Init(command.InitOption{Drop bool}) error
func (m *Migrator) Up(command.UpOption{Yes, SkipErr bool; Number int; StartTime string}) error
func (m *Migrator) Down(command.DownOption{Number int; Yes bool}) error   // Number >= 1 required
func (m *Migrator) Skip(command.SkipOption{FileNames []string}) error
func (m *Migrator) Status(command.StatusOption{}) error                   // prints a table
func (m *Migrator) Show(command.ShowOption{Tables bool; Schema string}) error  // prints
func (m *Migrator) Exec(command.ExecOption{SQLOrFile string; Yes bool}) error
func (m *Migrator) SetSqlDB(db *sql.DB) *Migrator   // inject your connection; never closed by miglite
func (m *Migrator) SetFS(fsys fs.FS) *Migrator      // embedded migrations; nil = local disk
```

Behaviour:

- Library calls never prompt; `Yes` is CLI-only.
- Methods print the same progress output as the CLI. Redirect/silence via `Config.Output` (e.g.
  `io.Discard`); output is process-global, so concurrent Migrators with different writers are serialised.
- Without `SetSqlDB`, each call opens a connection from the config and closes it at the end.
  With it, `Config.Database.Driver` still selects the SQL provider, so set Driver.
- `Up` with `SkipErr` continues past failures but still returns an error naming them.
- Results are printed, not returned; there is no public programmatic status list.

## Embedded migrations

```go
//go:embed migrations/*.sql
var migFS embed.FS

mig, _ := miglite.NewAuto(func(c *miglite.Config) { c.Migrations.Path = "migrations" }) // path inside the FS
mig.SetFS(migFS).SetSqlDB(db)
err := mig.Up(command.UpOption{})
```

With an FS, `Path` is an io/fs logical path (forward slashes, relative to the FS root; use `fs.Sub` to
re-root), `_` entries are still skipped, and `create` still writes to local disk.

## Build your own CLI

```go
import ("github.com/gookit/miglite"; "github.com/gookit/miglite/pkg/command"; _ "github.com/lib/pq")

func main() {
    // miglite.BindFS(migFS)   // optional: CLI handlers read migrations from an embed.FS
    app := command.NewApp("mytool", "1.0.0", "my migration tool")
    app.Run()
}
```

Hooks/globals: `command.OnConfigLoaded` (modify/validate config), `command.SetBuildInfo(...)`,
`command.SetCfg`, `command.SetDB`, `miglite.SetEnvPrefix(p)`, `miglite.SetSchemaTableName(name)`.
`command.Handle*` functions run each subcommand with CLI semantics (prompts included).

## Custom drivers / databases

- Other `sql.Open` name for a known DB: set `Database.SqlDriver` (or `sql_driver` / `DATABASE_SQL_DRIVER`),
  e.g. `Driver: "postgres", SqlDriver: "pgx"`.
- Unknown DB family: `miglite.AddSqlProvider("name", provider)` where provider implements
  `SqlProvider` (CreateSchema, DropSchema, ShowTables, QueryTableSchema, QueryAll, QueryOne, QueryStatus,
  QueryExists, InsertMigration `(version,status)`, UpdateMigration `(status,version)`,
  GetAppliedSortedByVersion `(status,limit)`); embed `database.ReSqlProvider` is not importable (internal),
  so implement every method.
  Built-ins: mysql, postgres, sqlite, mssql.
