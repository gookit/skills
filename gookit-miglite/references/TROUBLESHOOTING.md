# Troubleshooting Guide

Common issues and solutions when using miglite.

## Configuration Issues

### "database driver is required"

**Problem:** No database driver specified in configuration.

**Symptoms:**
```
Error: database driver is required
```

**Solution:**

Set driver via environment variable:
```bash
export DATABASE_URL="mysql://user:pass@tcp(localhost:3306)/dbname"
```

Or in config file:
```yaml
database:
  driver: mysql
  dsn: user:pass@tcp(localhost:3306)/dbname
```

**Verification:**
```bash
miglite status
```

---

### "could not import driver package"

**Problem:** Database driver not imported when using as library.

**Symptoms:**
```
sql: unknown driver "mysql" (forgotten import?)
```

**Solution:**

Add driver import to your Go code:
```go
import (
    "github.com/gookit/miglite"

    // Add driver import with blank identifier
    _ "github.com/go-sql-driver/mysql"
)
```

Install the driver:
```bash
go get github.com/go-sql-driver/mysql
```

**Common Drivers:**
- MySQL: `_ "github.com/go-sql-driver/mysql"`
- PostgreSQL: `_ "github.com/lib/pq"`
- SQLite: `_ "modernc.org/sqlite"`

---

### "migration table doesn't exist"

**Problem:** Migration tracking table hasn't been created.

**Symptoms:**
```
Error: table schema_migrations doesn't exist
```

**Solution:**

Initialize the migration system:
```bash
miglite init
```

**Verification:**
```bash
miglite status
```

---

### Config file not found

**Problem:** miglite can't find configuration file.

**Symptoms:**
```
Config file not found: ./miglite.yaml
```

**Solution:**

1. Create config file:
```bash
cat > miglite.yaml <<EOF
database:
  driver: sqlite
  dsn: ./app.db
migrations:
  path: ./migrations
EOF
```

2. Or specify custom location:
```bash
miglite --config ./config/db.yaml up
```

3. Or use environment variables:
```bash
export DATABASE_URL="sqlite://./app.db"
miglite up
```

## Database Connection Issues

### MySQL "multiStatements" error

**Problem:** DSN doesn't include `multiStatements=true` parameter.

**Symptoms:**
```
Error: Error 1064: You have an error in your SQL syntax
```

**Solution:**

miglite automatically adds `multiStatements=true`. If you still see this error, check your DSN format:

```bash
# Correct format (miglite adds multiStatements automatically)
DATABASE_URL="mysql://user:pass@tcp(127.0.0.1:3306)/dbname?charset=utf8mb4&parseTime=True"

# Or manually:
DATABASE_URL="mysql://user:pass@tcp(127.0.0.1:3306)/dbname?multiStatements=true"
```

---

### Connection refused

**Problem:** Can't connect to database server.

**Symptoms:**
```
Error: dial tcp 127.0.0.1:3306: connect: connection refused
```

**Solution:**

1. Check if database server is running:
```bash
# MySQL
systemctl status mysql

# PostgreSQL
systemctl status postgresql

# Or check process
ps aux | grep mysql
ps aux | grep postgres
```

2. Check database host and port:
```bash
# Test connection
telnet localhost 3306  # MySQL
telnet localhost 5432  # PostgreSQL
```

3. Verify DSN configuration:
```yaml
database:
  driver: mysql
  host: localhost  # Try 127.0.0.1 or actual IP
  port: 3306
  user: root
  password: secret
  dbname: myapp
```

---

### Permission denied

**Problem:** Database user lacks required permissions.

**Symptoms:**
```
Error: Access denied for user 'myapp'@'localhost'
```

**Solution:**

Grant necessary permissions:

**MySQL:**
```sql
-- Grant all privileges on database
GRANT ALL PRIVILEGES ON dbname.* TO 'user'@'localhost';
FLUSH PRIVILEGES;

-- Or create new user with permissions
CREATE USER 'migrator'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON myapp.* TO 'migrator'@'localhost';
FLUSH PRIVILEGES;
```

**PostgreSQL:**
```sql
-- Grant all privileges on database
GRANT ALL PRIVILEGES ON DATABASE dbname TO username;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO username;
GRANT ALL ON ALL TABLES IN SCHEMA public TO username;
```

**Verify Permissions:**
```bash
# MySQL
mysql -u myapp -p -e "SHOW GRANTS;"

# PostgreSQL
psql -U myapp -c "\du"
```

---

### Connection pool exhausted

**Problem:** Too many connections or connection leak.

**Symptoms:**
```
Error: too many connections
Error: pq: sorry, too many clients already
```

**Solution:**

Configure connection pool:
```yaml
database:
  max_open_conns: 25
  max_idle_conns: 5
  conn_max_lifetime: 300
  conn_max_idle_time: 300
```

**Check current connections:**

```sql
-- MySQL
SHOW PROCESSLIST;

-- PostgreSQL
SELECT * FROM pg_stat_activity;
```

**Recommended Settings:**
- Small apps: `max_open_conns: 25`
- Medium apps: `max_open_conns: 100`
- Large apps: `max_open_conns: 200`

## Migration File Issues

### Migration file not found

**Problem:** Migration files not in correct directory or wrong naming.

**Symptoms:**
```
No migration files found in ./migrations
Error: migration file not found
```

**Solution:**

1. Check MIGRATIONS_PATH:
```bash
echo $MIGRATIONS_PATH
# Or in config:
grep "path:" miglite.yaml
```

2. Verify file naming format:
```bash
ls -la migrations/
# Should be: YYYYMMDD-HHMMSS-name.sql
```

3. Check file permissions:
```bash
ls -la migrations/
chmod 644 migrations/*.sql
```

4. Ensure not in ignored directory:
```bash
# Files in directories starting with _ are ignored
mv migrations/_backup/file.sql migrations/file.sql
```

**Create Migration Correctly:**
```bash
miglite create migration-name
# Creates: YYYYMMDD-HHMMSS-migration-name.sql
```

---

### SQL syntax error

**Problem:** Invalid SQL in migration file.

**Symptoms:**
```
Error: You have an error in your SQL syntax near '...'
```

**Solution:**

1. Check SQL syntax for your database:
```bash
# Dry run to see SQL without executing
miglite up --dry-run
```

2. Test SQL manually:
```bash
# MySQL
mysql -u user -p dbname < migrations/file.sql

# PostgreSQL
psql -U user dbname < migrations/file.sql
```

3. Common mistakes:
```sql
-- Missing semicolon
CREATE TABLE users (id INT)  -- ❌
CREATE TABLE users (id INT); -- ✅

-- Wrong quotes
CREATE TABLE "users" (id INT); -- ❌ MySQL
CREATE TABLE `users` (id INT); -- ✅ MySQL
CREATE TABLE "users" (id INT); -- ✅ PostgreSQL

-- Database-specific syntax
-- MySQL:
id INT AUTO_INCREMENT
-- PostgreSQL:
id SERIAL
```

---

### Version conflicts

**Problem:** Multiple migration files with same timestamp.

**Symptoms:**
```
Error: duplicate migration version: 20260128-143022
```

**Solution:**

Each migration must have unique timestamp:

```bash
# Use miglite create to ensure unique timestamps
miglite create migration-name

# Or manually rename
mv 20260128-143022-duplicate.sql 20260128-143023-duplicate.sql
```

**Prevent:**
- Don't copy migration files
- Don't manually create timestamps
- Use `miglite create` command

## Transaction Issues

### Implicit commits (MySQL)

**Problem:** DDL statements cause implicit commits in MySQL.

**Symptoms:**
```
Migration partially applied
Can't rollback DDL changes
```

**Explanation:**

Most MySQL DDL statements (CREATE, ALTER, DROP, etc.) cause implicit commits and can't be rolled back.

**Solution:**

1. Split risky operations into separate migrations:
```bash
# Instead of one large migration:
miglite create add-columns           # Part 1
miglite create add-indexes          # Part 2
miglite create add-foreign-keys     # Part 3
```

2. Test thoroughly before applying:
```bash
miglite up --dry-run
```

3. Backup before major changes:
```bash
mysqldump dbname > backup.sql
miglite up
```

---

### Deadlocks

**Problem:** Migration causes database deadlock.

**Symptoms:**
```
Error: Deadlock found when trying to get lock
```

**Solution:**

1. Ensure no other processes are accessing the database:
```bash
# Stop application before migration
systemctl stop myapp
miglite up
systemctl start myapp
```

2. Check for long-running transactions:
```sql
-- MySQL
SHOW FULL PROCESSLIST;
KILL <process_id>;

-- PostgreSQL
SELECT * FROM pg_stat_activity WHERE state = 'active';
SELECT pg_terminate_backend(<pid>);
```

3. Run migrations during maintenance window

## SQLite Specific Issues

### CGO errors

**Problem:** Using `mattn/go-sqlite3` which requires CGO.

**Symptoms:**
```
# github.com/mattn/go-sqlite3
exec: "gcc": executable file not found in %PATH%
```

**Solution:**

Use a CGO-free driver:

```bash
# Option 1: modernc.org/sqlite (recommended)
go get modernc.org/sqlite

# Option 2: glebarez/go-sqlite
go get github.com/glebarez/go-sqlite

# Option 3: ncruces/go-sqlite3
go get github.com/ncruces/go-sqlite3
```

Update import:
```go
// Replace
// _ "github.com/mattn/go-sqlite3"

// With
_ "modernc.org/sqlite"
```

---

### Database locked

**Problem:** SQLite database file is locked.

**Symptoms:**
```
Error: database is locked
```

**Solution:**

1. Close all connections to database:
```bash
# Check for processes
lsof app.db
fuser app.db

# Kill process if needed
kill <pid>
```

2. Check for concurrent access:
- Only one writer at a time
- Readers must wait for writer
- Use WAL mode for better concurrency:

```sql
PRAGMA journal_mode=WAL;
```

3. Increase timeout:
```go
db, _ := sql.Open("sqlite", "file:app.db?_timeout=5000")
```

## Environment Variable Issues

### Environment variables not loaded

**Problem:** `.env` file not being read.

**Symptoms:**
```
DATABASE_URL not set
Migration path not found
```

**Solution:**

1. Ensure `.env` file exists in working directory:
```bash
ls -la .env*
```

2. miglite loads files in order:
   - `.env.local` (highest priority)
   - `.env.dev`
   - `.env`

3. Check file format:
```ini
# .env file format
DATABASE_URL=mysql://user:pass@tcp(localhost:3306)/dbname
MIGRATIONS_PATH=./migrations

# No quotes needed
# No spaces around =
# One variable per line
```

4. Verify environment variables:
```bash
env | grep DATABASE
echo $DATABASE_URL
```

5. Test loading:
```bash
# Load .env manually
set -a
source .env
set +a

miglite status
```

## Performance Issues

### Slow migrations

**Problem:** Migrations taking too long.

**Symptoms:**
```
Migration timeout
Very slow execution
```

**Solution:**

1. Check migration SQL:
```bash
miglite up --dry-run
# Review SQL for inefficient operations
```

2. Add indexes after data migration:
```sql
-- Migration 1: Add column and data
ALTER TABLE large_table ADD COLUMN status VARCHAR(20);
UPDATE large_table SET status = 'active';

-- Migration 2: Add index (separate migration)
CREATE INDEX idx_status ON large_table(status);
```

3. Use batch updates for large datasets:
```sql
-- Instead of:
UPDATE large_table SET status = 'active';

-- Use batches:
UPDATE large_table SET status = 'active' WHERE id <= 10000;
UPDATE large_table SET status = 'active' WHERE id > 10000 AND id <= 20000;
-- etc.
```

4. Run during low-traffic periods

5. Monitor execution time:
```bash
time miglite up
```

## Debugging Tips

### Enable verbose output

```bash
miglite --verbose up
```

### Check migration status

```bash
miglite status
```

### Dry run before applying

```bash
miglite up --dry-run
miglite down --dry-run
```

### Verify database state

```bash
miglite show
miglite show --details
```

### Check logs

Enable logging in config:
```yaml
verbose: true
```

Or set log function programmatically:
```go
cfg.LogFunc = func(msg string) {
    log.Println("[MIGLITE]", msg)
}
```

### Test migrations in isolation

```bash
# Create test database
createdb test_migrations

# Test migrations
DATABASE_URL="postgres://localhost/test_migrations" miglite up

# Drop test database
dropdb test_migrations
```

## Getting Help

If you're still stuck:

1. Check [official documentation](https://github.com/gookit/miglite)
2. Search [existing issues](https://github.com/gookit/miglite/issues)
3. Enable verbose mode for more details
4. Create a [new issue](https://github.com/gookit/miglite/issues/new) with:
   - miglite version
   - Database type and version
   - Configuration file
   - Error message
   - Steps to reproduce
