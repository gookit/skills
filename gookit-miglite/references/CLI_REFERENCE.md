# CLI Command Reference

Complete reference for miglite command-line interface.

## Global Options

Available for all commands:

```bash
--config FILE, -c FILE    Config file path (default: ./miglite.yaml)
--verbose, -v             Verbose output
--help, -h                Show help
```

## Commands

### help - Show Help

Display help information for miglite or specific commands.

```bash
# Show general help
miglite --help
miglite -h

# Show help for specific command
miglite up --help
miglite down -h
```

### version - Show Version

Display miglite version information.

```bash
miglite --version
miglite -v
```

Output example:
```
miglite version 0.1.0
Go version: go1.21.0
Build time: 2026-01-28
Git commit: abc1234
```

### init - Initialize Migration System

Creates the migration tracking table in your database.

**Usage:**
```bash
miglite init [OPTIONS]
```

**Options:**
- `--config FILE, -c FILE` - Custom config file path

**Examples:**
```bash
# Initialize with default config
miglite init

# Initialize with custom config
miglite init --config ./config/miglite.yaml

# Initialize with verbose output
miglite --verbose init
```

**What it does:**
- Creates `schema_migrations` table (or custom table name from config)
- Table structure:
  - `version` - Migration version (timestamp)
  - `name` - Migration name
  - `applied_at` - Timestamp when applied

### create - Create Migration File

Generate new migration files with timestamp-based naming.

**Usage:**
```bash
miglite create MIGRATION_NAME [OPTIONS]
```

**Arguments:**
- `MIGRATION_NAME` - Descriptive name for the migration

**Options:**
- `--config FILE, -c FILE` - Custom config file path

**Examples:**
```bash
# Create basic migration
miglite create create-users-table

# Create with descriptive name
miglite create add-email-index-to-users

# Create with custom config
miglite create add-posts-table --config ./config/db.yaml
```

**Created File:**
```
./migrations/YYYYMMDD-HHMMSS-MIGRATION_NAME.sql
```

Example: `./migrations/20260128-143022-create-users-table.sql`

**File Template:**
```sql
-- Migrate:UP
-- Add migration SQL here

-- Migrate:DOWN
-- Add rollback SQL here (optional)
```

### up - Apply Migrations

Execute pending migrations to update database schema.

**Usage:**
```bash
miglite up [OPTIONS]
```

**Options:**
- `--yes, -y` - Skip confirmation prompt
- `--dry-run` - Show SQL without executing
- `--number N, -n N` - Apply only N migrations (0 = all)
- `--config FILE, -c FILE` - Custom config file path

**Examples:**
```bash
# Apply all pending migrations (with confirmation)
miglite up

# Apply without confirmation
miglite up --yes
miglite up -y

# Dry run (show SQL without executing)
miglite up --dry-run

# Apply specific number of migrations
miglite up --number 3
miglite up -n 3

# Combine options
miglite up --number 5 --yes

# Using custom config
miglite up --config ./config/miglite.yaml
```

**Behavior:**
- Lists all pending migrations
- Shows confirmation prompt (unless `--yes`)
- Executes migrations in chronological order
- Each migration runs in a transaction
- Stops on first error
- Records successful migrations

**Output Example:**
```
Pending migrations:
  20260128-143022-create-users-table
  20260129-091530-add-email-index
  20260130-165445-create-posts-table

Apply 3 migration(s)? [y/N]: y

Applying: 20260128-143022-create-users-table... ✓
Applying: 20260129-091530-add-email-index... ✓
Applying: 20260130-165445-create-posts-table... ✓

Successfully applied 3 migration(s)
```

### down - Rollback Migrations

Revert applied migrations to undo schema changes.

**Usage:**
```bash
miglite down [OPTIONS]
```

**Options:**
- `--yes, -y` - Skip confirmation prompt
- `--dry-run` - Show SQL without executing
- `--number N, -n N` - Rollback N migrations (default: 1)
- `--config FILE, -c FILE` - Custom config file path

**Examples:**
```bash
# Rollback last migration (with confirmation)
miglite down

# Rollback without confirmation
miglite down --yes
miglite down -y

# Rollback multiple migrations
miglite down --number 3
miglite down -n 3

# Dry run
miglite down --dry-run

# Combine options
miglite down --number 2 --yes
```

**Behavior:**
- Lists migrations to be rolled back
- Shows confirmation prompt (unless `--yes`)
- Executes DOWN sections in reverse chronological order
- Each rollback runs in a transaction
- Stops on first error
- Removes migration records

**Output Example:**
```
Migrations to rollback:
  20260130-165445-create-posts-table
  20260129-091530-add-email-index

Rollback 2 migration(s)? [y/N]: y

Rolling back: 20260130-165445-create-posts-table... ✓
Rolling back: 20260129-091530-add-email-index... ✓

Successfully rolled back 2 migration(s)
```

### status - Show Migration Status

View current migration state with visual indicators.

**Usage:**
```bash
miglite status [OPTIONS]
```

**Options:**
- `--compact` - Compact output format
- `--json` - JSON output format
- `--config FILE, -c FILE` - Custom config file path

**Examples:**
```bash
# Show status (default format)
miglite status

# Compact output
miglite status --compact

# JSON output
miglite status --json

# With custom config
miglite status --config ./config/miglite.yaml
```

**Default Output:**
```
Migration Status:
  Applied: 5
  Pending: 2

Status  Version               Name                        Applied At
------  -------------------   --------------------------  --------------------
✓ UP    20260115-100000       create-users-table          2026-01-15 10:05:23
✓ UP    20260116-110000       add-email-index             2026-01-16 11:02:45
✓ UP    20260117-120000       create-posts-table          2026-01-17 12:15:30
✓ UP    20260118-130000       add-foreign-keys            2026-01-18 13:20:15
✓ UP    20260119-140000       create-comments-table       2026-01-19 14:10:22
  --    20260120-150000       add-user-roles              Not applied
  --    20260121-160000       create-sessions-table       Not applied
```

**Compact Output:**
```
Applied: 5, Pending: 2
20260115-100000 ✓ | 20260116-110000 ✓ | 20260117-120000 ✓ | 20260118-130000 ✓ | 20260119-140000 ✓
20260120-150000 - | 20260121-160000 -
```

**JSON Output:**
```json
{
  "applied": 5,
  "pending": 2,
  "migrations": [
    {
      "version": "20260115-100000",
      "name": "create-users-table",
      "status": "applied",
      "applied_at": "2026-01-15T10:05:23Z"
    },
    {
      "version": "20260120-150000",
      "name": "add-user-roles",
      "status": "pending",
      "applied_at": null
    }
  ]
}
```

### show - Show Database Tables

List all tables in the database.

**Usage:**
```bash
miglite show [OPTIONS]
```

**Options:**
- `--details` - Show detailed table information
- `--config FILE, -c FILE` - Custom config file path

**Examples:**
```bash
# Show all tables
miglite show

# Show with details
miglite show --details

# With custom config
miglite show --config ./config/miglite.yaml
```

**Output Example:**
```
Database Tables:
  schema_migrations
  users
  posts
  comments
  sessions

Total: 5 tables
```

**Detailed Output:**
```
Database Tables:

Table: users
  Columns: id, username, email, password_hash, created_at, updated_at
  Indexes: PRIMARY, idx_email, idx_username

Table: posts
  Columns: id, title, content, author_id, created_at
  Indexes: PRIMARY, idx_author

Total: 2 tables
```

### skip - Skip Migrations

Mark migrations as applied without executing them. Useful for existing databases or when manually applying migrations.

**Usage:**
```bash
miglite skip VERSION [VERSION...] [OPTIONS]
miglite skip --all [OPTIONS]
```

**Arguments:**
- `VERSION` - Migration version(s) to skip (timestamp format)

**Options:**
- `--all` - Skip all pending migrations
- `--config FILE, -c FILE` - Custom config file path

**Examples:**
```bash
# Skip a specific migration
miglite skip 20260120-150000

# Skip multiple migrations
miglite skip 20260120-150000 20260121-160000

# Skip all pending migrations
miglite skip --all

# With custom config
miglite skip --all --config ./config/miglite.yaml
```

**Output Example:**
```
Marking migrations as applied:
  20260120-150000-add-user-roles
  20260121-160000-create-sessions-table

Skipped 2 migration(s)
```

**Use Cases:**
1. Existing database with schema already in place
2. Manually applied migrations outside miglite
3. Testing or development scenarios
4. Migrating from another migration tool

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Configuration error
- `3` - Database connection error
- `4` - Migration execution error

### exec - Direct Execute SQL

Execute raw SQL queries directly.

- Alias names: `run-sql`, `execute`

**Usage:**

```bash
miglite exec <SQL|sql-file>
```

## Common Workflows

### Initial Setup

```bash
# 1. Initialize migration system
miglite init

# 2. Check status
miglite status

# 3. Create first migration
miglite create init-schema

# 4. Edit migration file and apply
miglite up
```

### Development Workflow

```bash
# 1. Create new migration
miglite create add-new-feature

# 2. Edit the migration file
# 3. Test migration
miglite up --dry-run

# 4. Apply migration
miglite up --yes

# 5. Check status
miglite status
```

### Rollback Workflow

```bash
# 1. Check current status
miglite status

# 2. Dry run rollback
miglite down --dry-run

# 3. Rollback last migration
miglite down --yes

# 4. Verify rollback
miglite status
```

### Production Deployment

```bash
# 1. Check status
miglite status

# 2. Dry run
miglite up --dry-run

# 3. Apply migrations
miglite up --yes

# 4. Verify
miglite status
```

## Tips and Tricks

### Using with Shell Scripts

```bash
#!/bin/bash

# Exit on error
set -e

# Check migration status
echo "Checking migration status..."
miglite status

# Apply migrations
echo "Applying migrations..."
miglite up --yes

# Verify
echo "Verifying migrations..."
miglite status

echo "Migration complete!"
```

### Conditional Execution

```bash
# Only apply if there are pending migrations
if miglite status | grep -q "Pending: 0"; then
    echo "No pending migrations"
else
    echo "Applying migrations..."
    miglite up --yes
fi
```

### Backup Before Migration

```bash
# Create backup before applying migrations
mysqldump -u user -p dbname > backup_$(date +%Y%m%d_%H%M%S).sql
miglite up --yes
```
