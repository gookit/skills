# miglite Documentation

Complete documentation for the miglite database migration tool.

## Documentation Structure

The documentation is organized into focused guides, each covering a specific topic:

### 📘 [Configuration Guide](CONFIGURATION.md)
**319 lines** - Complete configuration reference

Topics covered:
- Configuration priority and loading order
- YAML file format with examples
- Environment variables
- Database URL formats for all supported databases
- Connection pool settings and tuning
- Multi-environment setup strategies
- Docker and container configuration

**Start here if:** You need to configure miglite for your specific environment or database.

---

### 🔧 [CLI Command Reference](CLI_REFERENCE.md)
**533 lines** - Comprehensive CLI documentation

Topics covered:
- Complete reference for all commands (init, create, up, down, status, show, skip)
- Command options and flags
- Usage examples for every command
- Common workflows and patterns
- Exit codes
- Tips and tricks

**Start here if:** You're using miglite from the command line and need command syntax.

---

### 📝 [Migration Files Guide](MIGRATION_FILES.md)
**544 lines** - Everything about migration files

Topics covered:
- File naming conventions and rules
- File structure (UP/DOWN sections)
- 5 detailed migration examples
- Database-specific syntax (MySQL, PostgreSQL, SQLite, MSSQL)
- Directory organization patterns
- Best practices for writing migrations

**Start here if:** You're creating migration files and need guidance on structure and syntax.

---

### 📚 [Library Usage Guide](LIBRARY_USAGE.md)
**614 lines** - Using miglite as a Go library

Topics covered:
- Installation and setup
- 4 basic usage examples
- Advanced usage patterns
- Framework integration (Gin, Echo)
- Testing integration
- Building custom migration tools
- Docker integration
- Best practices for library usage

**Start here if:** You're integrating miglite into your Go application code.

---

### 🔍 [API Reference](API_REFERENCE.md)
**654 lines** - Complete API documentation

Topics covered:
- Migrator type and all methods
- Configuration types (Config, Database, Migrations)
- Command options (UpOption, DownOption, etc.)
- Helper types and functions
- Error handling
- Thread safety considerations

**Start here if:** You need detailed API documentation for Go development.

---

### ✅ [Best Practices](BEST_PRACTICES.md)
**551 lines** - Recommended practices

Topics covered (10 key practices):
1. Always write DOWN migrations
2. Test migrations locally first
3. Use descriptive names
4. Keep migrations atomic
5. Handle data migrations carefully
6. Use transactions wisely
7. Version control migrations
8. Production deployment workflow
9. Environment management
10. CI/CD integration

**Start here if:** You want to learn recommended patterns and avoid common pitfalls.

---

### 🔧 [Troubleshooting](TROUBLESHOOTING.md)
**706 lines** - Common issues and solutions

Topics covered:
- Configuration issues
- Database connection problems
- Migration file issues
- Transaction errors
- SQLite-specific issues
- Environment variable problems
- Performance issues
- Debugging tips

**Start here if:** You're experiencing issues and need solutions.

---

## Quick Navigation

### By Role

**Database Administrator:**
1. [Configuration Guide](CONFIGURATION.md) - Setup and configuration
2. [CLI Reference](CLI_REFERENCE.md) - Command usage
3. [Troubleshooting](TROUBLESHOOTING.md) - Problem solving

**Application Developer:**
1. [Library Usage](LIBRARY_USAGE.md) - Integration
2. [API Reference](API_REFERENCE.md) - Code reference
3. [Migration Files](MIGRATION_FILES.md) - Writing migrations

**DevOps Engineer:**
1. [Best Practices](BEST_PRACTICES.md) - Deployment patterns
2. [Configuration](CONFIGURATION.md) - Multi-environment setup
3. [Troubleshooting](TROUBLESHOOTING.md) - Production issues

### By Task

**Setting up miglite:**
- [Configuration Guide](CONFIGURATION.md) - All configuration methods
- [CLI Reference](CLI_REFERENCE.md#init) - Initialize command

**Creating migrations:**
- [Migration Files Guide](MIGRATION_FILES.md) - File structure and examples
- [CLI Reference](CLI_REFERENCE.md#create) - Create command
- [Best Practices](BEST_PRACTICES.md) - Migration best practices

**Running migrations:**
- [CLI Reference](CLI_REFERENCE.md#up) - Apply migrations
- [Library Usage](LIBRARY_USAGE.md) - Programmatic usage
- [Best Practices](BEST_PRACTICES.md#8-production-deployment) - Production workflow

**Integrating with application:**
- [Library Usage Guide](LIBRARY_USAGE.md) - Complete integration guide
- [API Reference](API_REFERENCE.md) - Detailed API docs

**Troubleshooting:**
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Comprehensive solutions

## Documentation Statistics

| Document | Lines | Focus |
|----------|-------|-------|
| CONFIGURATION.md | 319 | Configuration reference |
| CLI_REFERENCE.md | 533 | Command-line usage |
| MIGRATION_FILES.md | 544 | Migration file guide |
| BEST_PRACTICES.md | 551 | Recommended patterns |
| LIBRARY_USAGE.md | 614 | Go library integration |
| API_REFERENCE.md | 654 | API documentation |
| TROUBLESHOOTING.md | 706 | Problem solving |
| **Total** | **3,921** | **Complete coverage** |

## Contributing

Found an issue or have a suggestion? Please:
1. Check if it's already covered
2. Open an issue at https://github.com/gookit/miglite/issues
3. Include which document needs updating

## Main Documentation

Return to [main SKILL.md](../SKILL.md) for overview and quick start.
