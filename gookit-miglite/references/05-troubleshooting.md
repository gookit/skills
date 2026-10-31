# Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `database driver is required` | no `database.driver`, `DATABASE_DRIVER` or `DATABASE_URL`; `create` needs it too |
| `database DSN is required` | no dsn and (non-sqlite) no `user` to build one |
| `invalid DATABASE_URL ... Should 'driver://DSN'` | missing `://` |
| `sql: unknown driver "pg"` | `sql.Open` name = raw driver string; set `sql_driver`/`DATABASE_SQL_DRIVER` to a registered name (CLI has only mysql, postgres, sqlite) or import the driver in your own build |
| `unsupported OR un-registered database driver: x` | no SQL provider for driver family `x`; use mysql/postgres/sqlite/mssql names or `AddSqlProvider` |
| postgres `invalid connection string` with `postgres://user:pw@host/db` in `DATABASE_URL` | the `postgres://` prefix is stripped; use key/value DSN or `DATABASE_DRIVER`+`DATABASE_DSN` |
| mysql DSN error | needs `user:pass@tcp(host:port)/db`; `multiStatements=true` is appended automatically |
| `invalid filename format: ..., expected YYYYMMDD-NNNNNN-{name}.sql` | a `.sql` file in the migration dir does not match `^\d{8}-\d{6}[\w-]+\.sql$`; rename, or prefix `_` to ignore it |
| `does not contain valid SQL in '-- Migrate:UP' section` | missing/misspelled marker (exact `-- Migrate:UP`), or section holds only `-- ` comments |
| `Skipping empty DOWN migration!` | file has no DOWN SQL; add one |
| `migration file not found for version` on `down` | an applied file was deleted/renamed |
| `migration table does not exist. please run miglite init` | run `miglite init` (only `status` and `down` require it; `up` auto-creates) |
| `up` says "No migrations found" | wrong `migrations.path`/`MIGRATIONS_PATH`, relative to the working dir; check `-v` output |
| migration not picked up from subdir | `recursive: false`, or dir/file starts with `_` |
| `--db` has no effect | the DSN has no recognizable DB-name part; check driver and DSN format |
| env var seems ignored | real env beats `.env`; only one of `.env.local`/`.env.dev`/`.env` loads; prefix applies to every name |
| `miglite show` prints an error | pass exactly one of `-t` or `-s TABLE` |
| pool settings ignored | `max_*`/`conn_*` are parsed but not applied by current code |

Debug: `miglite -v up` dumps the loaded config and SQL; `miglite exec -y "SELECT 1"` tests the connection.
