# Best Practices

Recommended practices for using miglite effectively and safely.

## 1. Always Write DOWN Migrations

Always include rollback logic to enable safe rollbacks.

**Why:**
- Enables quick rollback if issues arise
- Makes testing easier
- Documents how to undo changes
- Required for safe production deployments

**Example:**

```sql
-- Migrate:UP
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
ALTER TABLE users ADD INDEX idx_phone (phone);

-- Migrate:DOWN
ALTER TABLE users DROP INDEX idx_phone;
ALTER TABLE users DROP COLUMN phone;
```

**Even for "irreversible" changes:**

```sql
-- Migrate:UP
ALTER TABLE users DROP COLUMN legacy_field;

-- Migrate:DOWN
-- Note: Data will be lost, but structure can be restored
ALTER TABLE users ADD COLUMN legacy_field VARCHAR(255);
```

## 2. Test Migrations Locally First

Always test both UP and DOWN migrations before deploying.

**Testing Workflow:**

```bash
# 1. Create migration
miglite create add-user-status

# 2. Edit migration file

# 3. Test UP migration
miglite up --dry-run  # Check SQL first
miglite up            # Apply

# 4. Verify database state
miglite status
# Check actual database tables/data

# 5. Test DOWN migration
miglite down --dry-run  # Check rollback SQL
miglite down            # Rollback

# 6. Verify rollback
miglite status
# Check database restored correctly

# 7. Reapply for final test
miglite up
```

**Testing Checklist:**
- [ ] SQL syntax is correct
- [ ] Migration applies successfully
- [ ] Database schema matches expectations
- [ ] Application still works with new schema
- [ ] Rollback works correctly
- [ ] Database restored after rollback
- [ ] No data loss during rollback (if applicable)

## 3. Use Descriptive Names

Migration names should clearly describe what they do.

**Good Names:**
```
create-users-table
add-email-index-to-users
migrate-user-status-to-enum
add-foreign-key-posts-to-users
remove-deprecated-columns-from-orders
```

**Bad Names:**
```
migration1
update
fix
changes
new-stuff
temp
```

**Naming Convention:**
- Use verb-noun format
- Be specific about what changes
- Include table names
- Use hyphens for word separation
- Keep under 50 characters

## 4. Keep Migrations Small

Each migration should do one logical thing.

**Why:**
- Easier to understand and review
- Easier to rollback specific changes
- Reduces risk of conflicts
- Simplifies debugging

**Good (Atomic Migrations):**
```
20260101-100000-create-users-table.sql
20260102-110000-add-email-index-to-users.sql
20260103-120000-add-phone-column-to-users.sql
20260104-130000-add-status-enum-to-users.sql
```

**Bad (Too Large):**
```
20260101-100000-setup-entire-user-system.sql
```

**Exception:**
Related changes that must happen together can be in one migration:
```sql
-- Adding a foreign key requires both column and constraint
ALTER TABLE posts ADD COLUMN author_id BIGINT;
ALTER TABLE posts ADD FOREIGN KEY (author_id) REFERENCES users(id);
```

## 5. Handle Data Migrations Carefully

Data migrations need extra care to prevent data loss.

**Always Backup First:**

```bash
# PostgreSQL
pg_dump dbname > backup_$(date +%Y%m%d_%H%M%S).sql

# MySQL
mysqldump -u user -p dbname > backup_$(date +%Y%m%d_%H%M%S).sql

# SQLite
cp app.db app.db.backup_$(date +%Y%m%d_%H%M%S)
```

**Handle NULL Values:**

```sql
-- Migrate:UP
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';

-- Update existing rows (handle NULLs)
UPDATE users
SET status = CASE
    WHEN deleted_at IS NOT NULL THEN 'deleted'
    WHEN banned_at IS NOT NULL THEN 'banned'
    ELSE 'active'
END
WHERE status IS NULL;

-- Make non-nullable after data migration
ALTER TABLE users MODIFY COLUMN status VARCHAR(20) NOT NULL;

-- Migrate:DOWN
ALTER TABLE users DROP COLUMN status;
```

**Large Dataset Considerations:**

For large tables, consider:
- Batch processing
- Adding column with default first
- Updating in batches
- Adding NOT NULL constraint after

```sql
-- For large tables, split into multiple migrations:

-- Migration 1: Add column with default
ALTER TABLE large_table ADD COLUMN new_field VARCHAR(20) DEFAULT 'default_value';

-- Migration 2: Update data in batches (do this manually or in application)
-- UPDATE large_table SET new_field = ... WHERE id BETWEEN 1 AND 10000;
-- UPDATE large_table SET new_field = ... WHERE id BETWEEN 10001 AND 20000;
-- ...

-- Migration 3: Add constraints
ALTER TABLE large_table MODIFY COLUMN new_field VARCHAR(20) NOT NULL;
```

## 6. Use Transactions Wisely

Understand transaction behavior for your database.

**Transaction Support:**
- PostgreSQL: DDL is transactional ✅
- SQLite: DDL is transactional ✅
- MySQL: Most DDL causes implicit commit ⚠️
- MSSQL: DDL is transactional ✅

**miglite automatically:**
- Wraps each migration in a transaction
- Rolls back on error
- Prevents partial migrations

**Be Aware:**
```sql
-- MySQL: Each of these may commit separately
ALTER TABLE users ADD COLUMN col1 VARCHAR(20);  -- Commits
ALTER TABLE users ADD COLUMN col2 VARCHAR(20);  -- Commits
-- If second fails, first is already committed
```

**Solution for MySQL:**
Split risky operations into separate migrations:

```sql
-- 20260101-100000-add-col1.sql
ALTER TABLE users ADD COLUMN col1 VARCHAR(20);

-- 20260101-100100-add-col2.sql
ALTER TABLE users ADD COLUMN col2 VARCHAR(20);
```

## 7. Version Control

Always commit migration files to version control.

**Git Workflow:**

```bash
# Create migration
miglite create add-user-roles

# Edit migration file

# Test locally
miglite up
miglite down
miglite up

# Commit to git
git add migrations/20260128-143022-add-user-roles.sql
git commit -m "Add user roles migration"
git push
```

**Best Practices:**
- Never modify committed migrations
- Never delete committed migrations
- Create new migration to fix issues
- Include migrations in code reviews
- Tag releases with migration versions

**Fixing Bad Migrations:**

Don't:
```bash
# Don't modify already deployed migration
vim migrations/20260101-100000-bad-migration.sql
git commit -am "Fix migration"
```

Do:
```bash
# Create new migration to fix
miglite create fix-previous-migration
# Edit the new migration
git add migrations/20260102-110000-fix-previous-migration.sql
git commit -m "Fix issues from previous migration"
```

## 8. Production Deployment

Follow a safe deployment workflow for production.

**Production Workflow:**

```bash
# 1. Backup database
pg_dump production_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Check current status
miglite status

# 3. Review pending migrations
ls -la migrations/ | grep -v "Applied"

# 4. Dry run
miglite up --dry-run

# 5. Review dry run output carefully

# 6. Apply migrations
miglite up

# 7. Verify
miglite status
# Check application functionality
# Check database state

# 8. Monitor for errors
# Check application logs
# Check database logs
# Check application metrics

# 9. If issues, rollback
miglite down --number N
# Or restore from backup
```

**Pre-Deployment Checklist:**
- [ ] Migrations tested in staging
- [ ] Database backed up
- [ ] Rollback plan prepared
- [ ] Team notified
- [ ] Monitoring ready
- [ ] Downtime communicated (if needed)

**Rollback Plan:**
```bash
# Option 1: Rollback migrations
miglite down --number 3

# Option 2: Restore backup
# Stop application
# Restore database from backup
# Restart application
```

## 9. Environment Management

Use different configurations for different environments.

**Directory Structure:**

```
config/
├── dev.yaml       # Development
├── staging.yaml   # Staging
├── prod.yaml      # Production
└── test.yaml      # Testing

migrations/
├── core/          # Shared migrations
├── dev/           # Dev-only migrations
├── staging/       # Staging-only
└── prod/          # Prod-only
```

**Configuration Examples:**

```yaml
# config/dev.yaml
verbose: true
database:
  driver: sqlite
  dsn: ./dev.db
migrations:
  path: ./migrations/core,./migrations/dev

# config/prod.yaml
verbose: false
database:
  driver: mysql
  dsn: ${DATABASE_DSN}
  max_open_conns: 100
migrations:
  path: ./migrations/core,./migrations/prod
```

**Usage:**

```bash
# Development
miglite --config ./config/dev.yaml up

# Production
miglite --config ./config/prod.yaml up
```

## 10. CI/CD Integration

Automate migrations in your deployment pipeline.

**GitLab CI Example:**

```yaml
# .gitlab-ci.yml
stages:
  - test
  - deploy

test-migrations:
  stage: test
  script:
    - miglite --config ./config/test.yaml init
    - miglite --config ./config/test.yaml up
    - miglite --config ./config/test.yaml down --number 999
  only:
    - merge_requests

deploy-migrations:
  stage: deploy
  script:
    - miglite --config ./config/prod.yaml status
    - miglite --config ./config/prod.yaml up --yes
  only:
    - main
  when: manual
```

**GitHub Actions Example:**

```yaml
# .github/workflows/migrations.yml
name: Migrations

on:
  pull_request:
    paths:
      - 'migrations/**'
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'

      - name: Install miglite
        run: go install github.com/gookit/miglite/cmd/miglite@latest

      - name: Test migrations
        run: |
          miglite init
          miglite up
          miglite down --all

  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    needs: test
    steps:
      - uses: actions/checkout@v3

      - name: Run migrations
        run: |
          miglite status
          miglite up --yes
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

**Best Practices for CI/CD:**
- Test migrations in CI
- Require manual approval for production
- Always check status before applying
- Log migration output
- Send notifications on failure
- Set appropriate timeouts

## Additional Tips

### Use Meaningful Timestamps

While timestamps are auto-generated, create migrations in logical order:

```bash
# Don't create all migrations at once
miglite create create-users
miglite create create-posts
miglite create create-comments

# Create and test one at a time
miglite create create-users
# Test, commit
miglite create create-posts
# Test, commit
miglite create create-comments
# Test, commit
```

### Document Complex Migrations

Add comments explaining complex logic:

```sql
-- Migrate:UP

-- This migration consolidates user_profiles into users table
-- Background: Separate tables were causing performance issues
-- See: JIRA-1234 for details

-- Step 1: Add new columns to users
ALTER TABLE users
ADD COLUMN bio TEXT,
ADD COLUMN avatar_url VARCHAR(255);

-- Step 2: Migrate data from user_profiles
UPDATE users u
INNER JOIN user_profiles p ON u.id = p.user_id
SET u.bio = p.bio, u.avatar_url = p.avatar_url;

-- Step 3: Drop old table
DROP TABLE user_profiles;

-- Migrate:DOWN
-- Note: Data loss is possible if user_profiles had additional data
CREATE TABLE user_profiles (
    user_id BIGINT PRIMARY KEY,
    bio TEXT,
    avatar_url VARCHAR(255)
);
```

### Monitor Migration Performance

Track migration execution time:

```bash
time miglite up
```

For slow migrations, consider:
- Breaking into smaller migrations
- Adding indexes after data migration
- Using batch updates
- Running during low-traffic periods

### Keep Migration History

Never delete old migrations, even if they seem obsolete:
- They provide history
- New developers need them
- Fresh database setups use them
