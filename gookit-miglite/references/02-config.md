# Configuration

## Load order (internal/config.Load)

1. Dotenv: with `--env-file F` only `F` (must exist); otherwise the first existing of `.env.local`,
   `.env.dev`, `.env` in the working dir (only one file is loaded; missing is fine). Variables already
   set in the real environment are NOT overridden by dotenv.
2. `MIGLITE_ENV_PREFIX` is read (unprefixed) unless `--env-prefix` was given.
3. YAML: `-c FILE`, or else the first existing of `./miglite.yaml`, `./miglite.local.yaml` (NOT merged).
   `${VAR}` / `${VAR | default}` / `${VAR | ?error msg}` placeholders are expanded in the whole file.
4. Env overrides: `DATABASE_DSN`, `DATABASE_DRIVER` (also sets sql_driver), `DATABASE_SQL_DRIVER`,
   then `DATABASE_URL` (wins over DSN; sets driver + DSN).
5. Validation: driver required; driver name normalised; DSN built from parts if empty.
6. `MIGRATIONS_PATH` overrides `migrations.path`; default `./migrations`; `{driver}` replaced with the
   normalised driver; `${ENV}` expanded.
7. `--db NAME` rewrites the DB name inside the DSN (mysql/postgres/mssql) or replaces it (sqlite).

All env names get `MIGLITE_ENV_PREFIX` prepended when it is set (e.g. `MY_DATABASE_URL`).

## YAML

```yaml
verbose: false
database:
  driver: mysql          # mysql | postgres | sqlite | mssql
  sql_driver: ""         # database/sql registered name; default = driver exactly as written
  dsn: ""                # wins; else built from the fields below
  host: localhost
  port: 3306             # defaults: mysql 3306, postgres 5432, mssql 1433
  user: root             # required to build a DSN (not for sqlite)
  password: ""
  dbname: app
  ssl_mode: disable      # postgres only
  max_idle_conns: 10     # parsed but not applied by the current code
  max_open_conns: 100
  conn_max_idle_time: 0
  conn_max_lifetime: 3600
migrations:
  path: ./migrations     # comma-separated; {driver}, ${ENV}
  recursive: true        # default true when loaded from file/env
  table: ""              # parsed, currently unused (record table is z_schema_migrations)
```

Pool settings and `migrations.table` exist in the struct but nothing reads them (verified by search).
The record table name can only be changed in code: `miglite.SetSchemaTableName("x")` (global).

## Driver names

`driver` is normalised for provider lookup: `mysql|my|mariadb|mysql2` -> mysql;
`postgres|pg|pgx|pgsql|postgresql` -> postgres; `sqlite|sqlite3` -> sqlite; `mssql|ms|sqlserver` -> mssql.
Other names are used as-is and fail with "unsupported OR un-registered database driver" unless you
add a provider (see 04-library.md).

`sql_driver` is the string passed to `sql.Open`. If empty it is the raw `driver` value, so `driver: pg`
without `sql_driver` calls `sql.Open("pg")` and fails unless a driver is registered under that name.
The prebuilt CLI registers: `mysql`, `postgres` (lib/pq), `sqlite` (modernc). It has no mssql, pgx or
`sqlite3`; build your own CLI (04-library.md) for those.

## DSN formats

| DB | DSN |
|---|---|
| sqlite | file path, e.g. `./app.db` |
| mysql | `user:pass@tcp(host:3306)/db?charset=utf8mb4&parseTime=True&loc=Local` (`tcp(...)` required; `multiStatements=true` is appended if missing) |
| postgres | key/value: `host=localhost port=5432 user=u password=p dbname=d sslmode=disable` (lib/pq also accepts a full `postgres://` URL here) |
| mssql | `server=h;user id=u;password=p;database=d;port=1433;` |

## DATABASE_URL

Format `driver://DSN`: split at the first `://`; everything after is passed through unchanged.

```bash
DATABASE_URL="sqlite://./app.db"
DATABASE_URL="mysql://user:pw@tcp(127.0.0.1:3306)/app?parseTime=True"
DATABASE_URL="postgres://host=localhost port=5432 user=u password=p dbname=d sslmode=disable"
# real postgres URL: use the split form instead
DATABASE_DRIVER=postgres
DATABASE_DSN="postgres://u:p@localhost:5432/d?sslmode=disable"
```

`DATABASE_URL` does not set `sql_driver`; the URL scheme becomes the driver name (and, if
`sql_driver` is empty, the `sql.Open` name too).

## Multiple databases

Use prefixes: `MIGLITE_ENV_PREFIX=ORDERS_ miglite up` reads `ORDERS_DATABASE_URL`,
`ORDERS_MIGRATIONS_PATH`; `--db other_db` retargets just the database name.
