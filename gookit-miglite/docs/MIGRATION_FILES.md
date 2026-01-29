# Migration Files Guide

Complete guide for creating and managing migration files in miglite.

## File Naming Convention

Migration files must follow this strict naming pattern:

```
YYYYMMDD-HHMMSS-{migration-name}.sql
```

**Format Breakdown:**
- `YYYYMMDD` - Date (year, month, day)
- `HHMMSS` - Time (hour, minute, second)
- `{migration-name}` - Descriptive name (lowercase, hyphens)

**Valid Examples:**
- `20260128-143022-create-users-table.sql`
- `20260129-091530-add-email-index.sql`
- `20260130-165445-create-posts-table.sql`

**Invalid Examples:**
- `create-users.sql` (missing timestamp)
- `20260128-create-users.sql` (incomplete timestamp)
- `20260128_143022_create_users.sql` (wrong separators)

**Automatic Generation:**

The `miglite create` command automatically generates correctly named files:

```bash
miglite create create-users-table
# Creates: 20260128-143022-create-users-table.sql
```

## File Structure

Each migration file contains two sections:

```sql
-- Migrate:UP
-- SQL statements to apply changes

-- Migrate:DOWN
-- SQL statements to revert changes (optional)
```

### Section Markers

**-- Migrate:UP** (Required)
- Marks the beginning of forward migration
- All SQL after this marker is executed during `miglite up`
- Must be present in every migration file

**-- Migrate:DOWN** (Optional but Recommended)
- Marks the beginning of rollback migration
- All SQL after this marker is executed during `miglite down`
- Should reverse changes made in UP section

### Important Notes

- Section markers are **case-sensitive**
- All SQL between UP and DOWN is executed as UP migration
- All SQL after DOWN is executed as rollback
- Comments are allowed and encouraged
- Multi-statement support depends on database driver

## Migration Examples

### Example 1: Create Table

```sql
-- Migrate:UP
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Migrate:DOWN
DROP TABLE users;
```

### Example 2: Add Column

```sql
-- Migrate:UP
ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;
ALTER TABLE users ADD INDEX idx_phone (phone);

-- Migrate:DOWN
ALTER TABLE users DROP INDEX idx_phone;
ALTER TABLE users DROP COLUMN phone;
```

### Example 3: Create Index

```sql
-- Migrate:UP
CREATE INDEX idx_created_at ON posts(created_at);
CREATE INDEX idx_author_id ON posts(author_id);

-- Migrate:DOWN
DROP INDEX idx_created_at ON posts;
DROP INDEX idx_author_id ON posts;
```

### Example 4: Data Migration

```sql
-- Migrate:UP
-- Add new status column
ALTER TABLE orders ADD COLUMN status VARCHAR(20) DEFAULT 'pending';

-- Migrate existing data
UPDATE orders SET status = 'completed' WHERE completed = 1;
UPDATE orders SET status = 'cancelled' WHERE cancelled = 1;

-- Remove old columns
ALTER TABLE orders DROP COLUMN completed;
ALTER TABLE orders DROP COLUMN cancelled;

-- Migrate:DOWN
-- Restore old structure
ALTER TABLE orders ADD COLUMN completed TINYINT(1) DEFAULT 0;
ALTER TABLE orders ADD COLUMN cancelled TINYINT(1) DEFAULT 0;

-- Migrate data back
UPDATE orders SET completed = 1 WHERE status = 'completed';
UPDATE orders SET cancelled = 1 WHERE status = 'cancelled';

-- Remove new column
ALTER TABLE orders DROP COLUMN status;
```

### Example 5: Complex Schema Change

```sql
-- Migrate:UP
-- Create new table with improved structure
CREATE TABLE posts_new (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
    published_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_author (author_id),
    INDEX idx_status (status),
    INDEX idx_published_at (published_at),
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Migrate existing data
INSERT INTO posts_new (id, title, slug, content, author_id, created_at, updated_at)
SELECT id, title, title AS slug, content, author_id, created_at, updated_at
FROM posts;

-- Drop old table and rename
DROP TABLE posts;
RENAME TABLE posts_new TO posts;

-- Migrate:DOWN
-- Reverse the process
CREATE TABLE posts_old (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    author_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO posts_old (id, title, content, author_id, created_at, updated_at)
SELECT id, title, content, author_id, created_at, updated_at
FROM posts;

DROP TABLE posts;
RENAME TABLE posts_old TO posts;
```

## Database-Specific Syntax

### MySQL

```sql
-- Migrate:UP
CREATE TABLE products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add fulltext index (MySQL specific)
ALTER TABLE products ADD FULLTEXT INDEX ft_name (name);

-- Migrate:DOWN
DROP TABLE products;
```

### PostgreSQL

```sql
-- Migrate:UP
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_name ON products(name);

-- PostgreSQL specific: Create extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Migrate:DOWN
DROP EXTENSION IF EXISTS "uuid-ossp";
DROP INDEX IF EXISTS idx_products_name;
DROP TABLE IF EXISTS products;
```

### SQLite

```sql
-- Migrate:UP
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_name ON products(name);

-- Migrate:DOWN
DROP INDEX IF EXISTS idx_products_name;
DROP TABLE IF EXISTS products;
```

### MSSQL

```sql
-- Migrate:UP
CREATE TABLE products (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE()
);

CREATE INDEX idx_products_name ON products(name);

-- Migrate:DOWN
DROP INDEX idx_products_name ON products;
DROP TABLE products;
```

## Directory Organization

miglite supports flexible directory structures:

### Simple Structure

```
migrations/
├── 20260101-100000-init-database.sql
├── 20260102-110000-create-users.sql
└── 20260103-120000-create-posts.sql
```

### Module-Based Structure

```
migrations/
├── users/
│   ├── 20260101-100000-create-users-table.sql
│   └── 20260102-110000-add-user-roles.sql
├── posts/
│   ├── 20260103-100000-create-posts-table.sql
│   └── 20260104-110000-add-post-tags.sql
└── _backup/  # Ignored (starts with _)
    └── old-migration.sql
```

### Environment-Specific

```
migrations/
├── core/
│   └── 20260101-100000-init-schema.sql
├── dev/
│   └── 20260102-100000-seed-dev-data.sql
└── prod/
    └── 20260103-100000-seed-prod-data.sql
```

**Configuration:**
```yaml
migrations:
  path: ./migrations/core,./migrations/${ENV}
```

### Feature-Based

```
migrations/
├── auth/
│   ├── 20260101-100000-create-users.sql
│   ├── 20260102-110000-create-sessions.sql
│   └── 20260103-120000-create-permissions.sql
├── blog/
│   ├── 20260104-100000-create-posts.sql
│   └── 20260105-110000-create-comments.sql
└── ecommerce/
    ├── 20260106-100000-create-products.sql
    └── 20260107-110000-create-orders.sql
```

## Best Practices for Migration Files

### 1. Always Include DOWN Migration

Even if you think you won't need to roll back, include it:

```sql
-- Migrate:UP
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Migrate:DOWN
ALTER TABLE users DROP COLUMN phone;
```

### 2. Use Descriptive Names

Good migration names describe what they do:

✅ Good:
- `create-users-table`
- `add-email-index-to-users`
- `migrate-user-status-to-enum`

❌ Bad:
- `migration1`
- `update`
- `fix`

### 3. Keep Migrations Atomic

Each migration should do one logical thing:

✅ Good - Separate migrations:
- `20260101-100000-create-users-table.sql`
- `20260102-110000-add-email-index.sql`

❌ Bad - Everything in one:
- `20260101-100000-setup-entire-database.sql`

### 4. Test Both UP and DOWN

Always test both directions:

```bash
# Test UP
miglite up

# Verify
miglite status

# Test DOWN
miglite down

# Verify rollback
miglite status

# Reapply
miglite up
```

### 5. Handle Data Carefully

When migrating data, consider:

- **Backup first**: Always backup before data migrations
- **Handle NULLs**: Account for NULL values
- **Large datasets**: Consider batch processing
- **Reversibility**: Ensure DOWN can restore data

```sql
-- Migrate:UP
-- Add column with default
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';

-- Update existing rows (handle NULLs)
UPDATE users
SET status = CASE
    WHEN deleted_at IS NULL THEN 'active'
    ELSE 'inactive'
END;

-- Migrate:DOWN
ALTER TABLE users DROP COLUMN status;
```

### 6. Use Comments

Document complex logic:

```sql
-- Migrate:UP

-- Create temporary table for data transformation
CREATE TEMPORARY TABLE temp_users AS
SELECT * FROM users WHERE active = 1;

-- Transform and insert data
INSERT INTO new_users (id, email, status)
SELECT id, email, 'active'
FROM temp_users;

-- Cleanup
DROP TEMPORARY TABLE temp_users;

-- Migrate:DOWN
-- Reverse transformation logic here
```

### 7. Avoid Mixing DDL and DML

Some databases have issues with mixing DDL (schema changes) and DML (data changes):

✅ Good - Separate migrations:
```sql
-- 20260101-100000-add-status-column.sql
ALTER TABLE users ADD COLUMN status VARCHAR(20);

-- 20260101-100100-populate-status-column.sql
UPDATE users SET status = 'active' WHERE active = 1;
```

❌ Risky - Mixed in one:
```sql
ALTER TABLE users ADD COLUMN status VARCHAR(20);
UPDATE users SET status = 'active';  -- May fail in some databases
```

### 8. Handle Foreign Keys Carefully

Drop foreign keys before dropping tables:

```sql
-- Migrate:UP
CREATE TABLE posts (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Migrate:DOWN
-- Drop FK first, then table
ALTER TABLE posts DROP FOREIGN KEY fk_user;
DROP TABLE posts;
```

### 9. Use IF EXISTS/IF NOT EXISTS

Make migrations idempotent where possible:

```sql
-- Migrate:UP
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY
);

-- Migrate:DOWN
DROP TABLE IF EXISTS users;
```

### 10. Version Control

Always commit migration files to version control:

```bash
git add migrations/
git commit -m "Add user phone column migration"
git push
```

## Troubleshooting Migration Files

### Syntax Errors

Check SQL syntax for your specific database:

```bash
# Dry run to catch syntax errors
miglite up --dry-run
```

### File Not Found

Ensure correct path and naming:

```bash
# Check MIGRATIONS_PATH
echo $MIGRATIONS_PATH

# Verify file naming
ls -la migrations/

# Check for hidden characters
cat -A migrations/file.sql
```

### Transaction Issues

Some operations can't run in transactions:

```sql
-- Some databases don't support DDL in transactions
-- Check database-specific documentation
```

### Encoding Issues

Use UTF-8 encoding:

```bash
# Check file encoding
file -i migrations/file.sql

# Convert if needed
iconv -f ISO-8859-1 -t UTF-8 old.sql > new.sql
```
