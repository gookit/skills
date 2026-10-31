---
name: gookit-miglite
description: Use when working with gookit/miglite, a lite Go SQL schema migration tool - the `miglite` CLI (create/init/up/down/status/skip/exec/show), miglite.yaml / .env / DATABASE_URL config, `YYYYMMDD-HHMMSS-name.sql` migration files with `-- Migrate:UP` / `-- Migrate:DOWN` sections, or embedding it via the `github.com/gookit/miglite` Go library (Migrator, embed.FS, custom DB driver). Covers mysql, postgres, sqlite, mssql.
author: inhere
platform: github
source: https://github.com/gookit/miglite
tags: [go, database, migration, sql, mysql, postgres, sqlite, mssql, cli]
version: 2.0.0
---

# miglite - lite SQL migration tool for Go

Plain-SQL migrations on top of `database/sql`. Every migration runs in one transaction; applied
state is kept in the table `z_schema_migrations` (`version`, `applied_at`, `status`). The core
library bundles no DB driver; the `miglite` CLI bundles mysql, postgres (lib/pq) and sqlite (modernc).

Verified against miglite source at commit c812d77.

## Install

```bash
go install github.com/gookit/miglite/cmd/miglite@latest   # CLI (cmd/miglite is its own Go module)
go get github.com/gookit/miglite                           # library; add your own driver import
```

## Quick start

```bash
export DATABASE_URL="sqlite://./app.db"   # driver://DSN  (or put it in .env / miglite.yaml)
miglite create add-users      # -> ./migrations/20260128-143022-add-users.sql (template, edit it)
miglite init                  # create z_schema_migrations (`up` also creates it if missing)
miglite up -y                 # apply pending, no prompt
miglite status                # applied / pending / rolled / skipped
miglite down -y               # roll back the latest one
```

Migration file:

```sql
-- Migrate:UP
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);

-- Migrate:DOWN
DROP TABLE users;
```

## Rules that matter

- **File name**: `YYYYMMDD-HHMMSS-{name}.sql` (HHMMSS = hour, minute, second). The loader regex is
  `^(\d{8})-(\d{6})([\w-]+)\.sql$`, so `{name}` may only use `[A-Za-z0-9_-]` (no dots/spaces).
  Any `.sql` file in the migration dir that does not match makes discovery fail for the whole run,
  except files/dirs starting with `_`, which are ignored. Order = prefix, then full file name.
- **Markers** (exact, case-sensitive, trimmed line prefix): `-- Migrate:UP`, `-- Migrate:DOWN`.
  UP is required and must contain SQL. DOWN is optional: `down` on a file without it is skipped
  with a warning (record stays `up`).
- Inside the sections, lines starting with `-- ` (dash dash space) are dropped; blank lines too.
- UP/DOWN each execute as ONE `Exec` in a transaction (no statement splitting; MySQL gets
  `multiStatements=true` appended automatically). DDL auto-commits on MySQL, so a failed
  MySQL migration may be partially applied.
- Do not edit an applied migration; add a new one.
- `exec` is different: it splits statements, runs queries/DDL in one transaction, prints SELECT rows.

## CLI at a glance

Global flags (before or after the command): `-c/--config`, `--db`, `--env-file|--efile`, `-v/--verbose`;
app-level only (before the command): `--env-prefix|--pfx`, `-V/--version`.

| Command (aliases) | Flags / args |
|---|---|
| `create` (new) | `name...` (required, several allowed); writes into the FIRST migration path |
| `init` | `--drop` drop the record table first |
| `up` (migrate, run) | `-y/--yes`, `-n/--number N`, `-s/--skip-err` (continue, still exits non-zero) |
| `down` (rollback) | `-y/--yes`, `-n/--number N` (default 1) |
| `status` (st) | - |
| `skip` (ignore) | `file...` (required; `.sql` optional) mark as skipped without running |
| `exec` (execute, run-sql) | `sql-or-file` (required; a value ending in `.sql`, < 128 chars, is read as a file), `-y` |
| `show` (info, describe) | exactly one of `-t/--tables` or `-s/--schema TABLE` |

Details: [references/01-cli.md](references/01-cli.md).

## Configuration at a glance

Sources, later wins: `miglite.yaml` then `miglite.local.yaml` (first existing one only unless `-c`)
< env `DATABASE_DSN`/`DATABASE_DRIVER` < env `DATABASE_URL` < `--db` (DB name override).
`.env.local`, `.env.dev`, `.env` - only the first existing one is loaded, and real env vars win.

```yaml
database:
  driver: postgres        # mysql|postgres|sqlite|mssql (aliases: pg, pgx, sqlite3, mariadb, sqlserver...)
  sql_driver: pgx         # optional: name registered with database/sql, default = driver as written
  dsn: ${PG_DSN}          # or host/port/user/password/dbname/ssl_mode instead of dsn
migrations:
  path: ./migrations/{driver}   # comma-separated list, ${ENV} and {driver} expanded
  recursive: true
```

Env vars: `DATABASE_URL`, `DATABASE_DSN`, `DATABASE_DRIVER`, `DATABASE_SQL_DRIVER`,
`MIGRATIONS_PATH`, `MIGLITE_ENV_PREFIX`. Gotchas: `DATABASE_URL` is only split at the first `://`
(the rest is the raw DSN, e.g. postgres needs `postgres://host=... dbname=...` key/value form, or use
`DATABASE_DRIVER` + `DATABASE_DSN` for a real URL); MySQL DSN needs `tcp(...)`. See
[references/02-config.md](references/02-config.md).

## Library at a glance

```go
import (
    "github.com/gookit/miglite"
    "github.com/gookit/miglite/pkg/command"
    _ "modernc.org/sqlite"            // YOU register the driver
)

mig, err := miglite.NewAuto(func(c *miglite.Config) { c.Migrations.Path = "migrations" })
err = mig.Up(command.UpOption{})      // never prompts; Yes is CLI-only
err = mig.Down(command.DownOption{Number: 1})   // Number must be >= 1
```

Also `New(cfgFile, fns...)`, `NewWithConfig(cfg)`, `NewWithConfigAndFS(cfg, fsys)`, `SetSqlDB(*sql.DB)`
(caller keeps ownership), `SetFS(embed.FS)`, `Config.Output`. Details and pitfalls:
[references/04-library.md](references/04-library.md).

## References

- [01-cli.md](references/01-cli.md) - commands, flags, behaviours, output, exit on errors
- [02-config.md](references/02-config.md) - config file, env vars, DSN formats, driver selection
- [03-migration-files.md](references/03-migration-files.md) - naming, sections, discovery, examples
- [04-library.md](references/04-library.md) - Migrator API, embed.FS, custom CLI, custom drivers/providers
- [05-troubleshooting.md](references/05-troubleshooting.md) - common errors and fixes
