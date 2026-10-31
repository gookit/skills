# CLI reference

Usage: `miglite [app flags] COMMAND [flags] [args]`. Verified with `miglite --help` / `COMMAND --help`.

## Flags

Accepted by every command (and at app level):

| Flag | Meaning |
|---|---|
| `-c, --config FILE` | config file; if the file does not exist it is silently ignored |
| `--db NAME` | override the database name in the final DSN (sqlite: the DB file path) |
| `--efile, --env-file FILE` | dotenv file; must exist when given |
| `-v, --verbose` | dump config, print SQL sections / skipped items |

App level only (put before the command): `--pfx, --env-prefix PREFIX` (same as `MIGLITE_ENV_PREFIX`),
`-V, --version`, `-h, --help`.

## Commands

### create (alias new)

`miglite create NAME...` - creates `<first-migrations-path>/YYYYMMDD-HHMMSS-NAME.sql` (dir auto-created,
timestamp = now). Several names create several files (they may share a timestamp, so distinct names).
Refuses empty names, names starting with `-`, and existing files. With several comma-separated migration
paths it asks interactively which to use. Needs config loaded (driver must resolve) but does not connect.
Generated content:

```sql
--
-- name: NAME
-- author: <os user>
-- created_at: 20260128-143022
--

-- Migrate:UP
-- Add your migration SQL here

-- Migrate:DOWN
-- Add your rollback SQL here (optional)
```

NAME is not validated beyond the above; use only `[A-Za-z0-9_-]` or the file will not be discovered.

### init

`miglite init [--drop]` - creates `z_schema_migrations` (`IF NOT EXISTS`; mssql: plain CREATE).
`--drop` drops the table first (loses all history).

### up (aliases migrate, run)

`miglite up [-y] [-n N] [-s]` - connects, ensures the record table exists, discovers files, then for each
file not yet applied/skipped: prompts (unless `-y`), runs the UP section in a transaction, records `up`.
`-n N` stops after N applied. Files already `up` or `skip` are skipped; a file with status `down`
(rolled back) is applied again. On error it aborts; with `-s` it continues but the command still
returns an error listing failed files. Unparseable file names or missing UP SQL abort the run.

### down (alias rollback)

`miglite down [-y] [-n N]` (N default 1, must be >= 1) - takes the N most recently applied records
(`status=up`, newest version first), runs each DOWN section, records `down`. A file with no DOWN is skipped
with a warning. A record whose file no longer exists is an error.

### status (alias st)

Table of every discovered file with `applied` / `rolled` / `skipped` / `pending` and time. If the record
table is missing: "please run `miglite init`". No `--json` option exists.

### skip (alias ignore)

`miglite skip FILE...` - marks files as `skip` (never run by `up`). Names are looked up in the migration
paths, `.sql` appended if missing. Files already `up` are left unchanged. No `--all`.

### exec (aliases execute, run-sql)

`miglite exec [-y] "SQL"` or `miglite exec [-y] ./file.sql` - prints the SQL, asks to confirm unless `-y`,
splits into statements (aware of quotes, `--`, `#`, `/* */`), runs them in one transaction; statements
that look like queries print result tables, others print rows affected. Does not touch the record table.

### show (aliases info, describe)

`miglite show -t` lists tables (record table hidden); `miglite show -s TABLE` prints columns.
Giving neither or both flags is an error (validated before connecting). No `--details`.

## Misc

- Prompts use a y/n confirm; use `-y` in CI.
- Prints "Loaded environment variables from ..." and "Loaded config file from ..." on start.
- Errors are returned to the app runner and exit non-zero.
