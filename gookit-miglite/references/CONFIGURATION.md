# Configuration Guide

Comprehensive configuration guide for miglite database migration tool.

## Configuration Priority

miglite loads configuration in this order (later sources override earlier ones):

1. Default values
2. Configuration file (`miglite.yaml`)
3. `.env` files (`.env`, `.env.dev`, `.env.local`)
4. Environment variables
5. Command-line flags

## Configuration File Format

### Full miglite.yaml Example

```yaml
# Verbose output (optional)
verbose: false

database:
  # Database driver name (required)
  driver: mysql  # Options: mysql, postgres, sqlite, mssql

  # Connection string (required)
  dsn: user:password@tcp(localhost:3306)/dbname?charset=utf8mb4&parseTime=True&loc=Local

  # Optional: SQL driver name (if different from driver)
  sql_driver: mysql

  # Connection pool settings (optional)
  max_idle_conns: 10
  max_open_conns: 100
  conn_max_idle_time: 300  # seconds
  conn_max_lifetime: 3600  # seconds

migrations:
  # Migration files directory (default: ./migrations)
  path: ./migrations

  # Recursive search (default: true)
  recursive: true

  # Custom table name (optional)
  table: schema_migrations
```

### Minimal Configuration

```yaml
database:
  driver: sqlite
  dsn: ./app.db
```

### Database-Specific Examples

#### MySQL Configuration

```yaml
database:
  driver: mysql
  dsn: user:password@tcp(localhost:3306)/dbname?charset=utf8mb4&parseTime=True&loc=Local
  max_open_conns: 100
  max_idle_conns: 10

migrations:
  path: ./migrations
```

#### PostgreSQL Configuration

```yaml
database:
  driver: postgres
  host: localhost
  port: 5432
  user: postgres
  password: secret
  dbname: myapp
  ssl_mode: disable

migrations:
  path: ./db/migrations
```

#### SQLite Configuration

```yaml
database:
  driver: sqlite
  dsn: ./data/app.db

migrations:
  path: ./migrations
  recursive: true
```

## Environment Variables

### Core Variables

- `DATABASE_URL` - Full database connection URL (format: `driver://dsn`)
- `DATABASE_DRIVER` - Database driver name
- `DATABASE_DSN` - Database connection string
- `DATABASE_SQL_DRIVER` - SQL driver name (if different from driver)
- `MIGRATIONS_PATH` - Path to migration files (supports multiple paths with `,`)

### Database URL Format Examples

```bash
# SQLite
DATABASE_URL="sqlite://./app.db"
DATABASE_URL="sqlite://path/to/database.db"

# MySQL (must include tcp protocol)
DATABASE_URL="mysql://user:password@tcp(127.0.0.1:3306)/dbname?charset=utf8mb4&parseTime=True&loc=Local"

# PostgreSQL
DATABASE_URL="postgres://host=localhost port=5432 user=username password=password dbname=dbname sslmode=disable"

# MSSQL
DATABASE_URL="mssql://server=localhost;user id=sa;password=yourStrong(!)Password;database=testdb;port=1433;"
```

### Advanced Migration Paths

```bash
# Multiple paths
MIGRATIONS_PATH="./migrations,./db/migrations"

# Environment variable substitution
MIGRATIONS_PATH="./migrations/${MODULE_NAME}"

# Driver-specific paths
MIGRATIONS_PATH="./migrations/{driver}"
```

## .env File Support

miglite automatically loads `.env` files in this order:

1. `.env.local` (highest priority)
2. `.env.dev`
3. `.env`

### .env File Examples

**Basic .env:**

```ini
DATABASE_URL=mysql://root:password@tcp(127.0.0.1:3306)/myapp?charset=utf8mb4&parseTime=True&loc=Local
MIGRATIONS_PATH=./database/migrations
```

**Development .env.dev:**

```ini
DATABASE_URL=sqlite://./dev.db
MIGRATIONS_PATH=./migrations
DATABASE_DRIVER=sqlite
```

**Production .env:**

```ini
DATABASE_URL=mysql://prod_user:${DB_PASSWORD}@tcp(db.example.com:3306)/production?charset=utf8mb4
MIGRATIONS_PATH=./migrations/core,./migrations/prod
```

## Connection Pool Configuration

### Pool Settings

```yaml
database:
  # Maximum number of open connections
  max_open_conns: 100

  # Maximum number of idle connections
  max_idle_conns: 10

  # Maximum time (seconds) a connection can be idle
  conn_max_idle_time: 300

  # Maximum time (seconds) a connection can be reused
  conn_max_lifetime: 3600
```

### Recommended Settings by Database Size

**Small Applications (< 1000 users):**
```yaml
max_open_conns: 25
max_idle_conns: 5
conn_max_idle_time: 300
conn_max_lifetime: 3600
```

**Medium Applications (1000-10000 users):**
```yaml
max_open_conns: 100
max_idle_conns: 10
conn_max_idle_time: 600
conn_max_lifetime: 7200
```

**Large Applications (> 10000 users):**
```yaml
max_open_conns: 200
max_idle_conns: 20
conn_max_idle_time: 900
conn_max_lifetime: 14400
```

## Multi-Environment Setup

### Using Different Config Files

```bash
# Development
miglite --config ./config/dev.yaml up

# Staging
miglite --config ./config/staging.yaml up

# Production
miglite --config ./config/prod.yaml up
```

### Config File Examples

**config/dev.yaml:**
```yaml
verbose: true
database:
  driver: sqlite
  dsn: ./dev.db
migrations:
  path: ./migrations/core,./migrations/dev
```

**config/prod.yaml:**
```yaml
verbose: false
database:
  driver: mysql
  dsn: ${DATABASE_DSN}
  max_open_conns: 100
migrations:
  path: ./migrations/core,./migrations/prod
```

## Docker Configuration

### Using Environment Variables

```dockerfile
FROM golang:1.21-alpine

WORKDIR /app
COPY . .

RUN go install github.com/gookit/miglite/cmd/miglite@latest

ENV DATABASE_URL="postgres://user:pass@db:5432/myapp"
ENV MIGRATIONS_PATH="/app/migrations"

CMD ["miglite", "up", "--yes"]
```

### Docker Compose Example

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

  migrate:
    build: .
    depends_on:
      - db
    environment:
      DATABASE_URL: "postgres://host=db port=5432 user=myapp password=secret dbname=myapp_dev sslmode=disable"
      MIGRATIONS_PATH: "./migrations"
    command: ["miglite", "up", "--yes"]
```

## Configuration Validation

### Common Issues

1. **Missing driver**: Ensure `database.driver` is set
2. **Invalid DSN format**: Check connection string syntax
3. **Path not found**: Verify `migrations.path` exists
4. **Permission errors**: Ensure database user has required permissions

### Testing Configuration

```bash
# Test database connection
miglite status

# Verbose output for debugging
miglite --verbose status

# Dry run to check what would be executed
miglite up --dry-run
```
