# config Documentation

Complete documentation for gookit/config configuration management library.

## Documentation Structure

### 📘 [Loading Configuration](LOADING.md)
Load configuration from various sources:
- Files (single, multiple, directory)
- Environment variables
- CLI flags
- Remote URLs
- Go structs/maps
- Loading strategies and patterns

**Read this when**: Setting up configuration loading

---

### 📚 [Using Configuration](USAGE.md)
Access and manipulate configuration data:
- Getting values (all types)
- Binding to structs
- Setting values
- Type conversions
- Practical patterns

**Read this when**: Working with configuration in your code

---

### 🔧 [Advanced Features](ADVANCED.md)
Advanced options and patterns:
- Configuration options
- Events and hooks
- File watching and auto-reload
- Dumping configuration
- Multiple instances
- Custom drivers
- Testing

**Read this when**: Need advanced features or customization

---

## Quick Navigation

**First Time Users:**
1. [Main SKILL.md](../SKILL.md) - Overview and quick start
2. [LOADING.md](LOADING.md) - Load your first config
3. [USAGE.md](USAGE.md) - Access config values

**Common Tasks:**
- Load YAML file → [LOADING.md#load-from-files](LOADING.md)
- Get config value → [USAGE.md#getting-values](USAGE.md)
- Bind to struct → [USAGE.md#bind-to-struct](USAGE.md)
- Load from ENV → [LOADING.md#load-from-env](LOADING.md)
- Parse CLI flags → [LOADING.md#load-from-cli-flags](LOADING.md)
- Watch file changes → [ADVANCED.md#watch-file-changes](ADVANCED.md)
- Multiple configs → [ADVANCED.md#multiple-config-instances](ADVANCED.md)

**By Format:**
- JSON → [LOADING.md#json](LOADING.md)
- YAML → [LOADING.md#yaml](LOADING.md)
- TOML → [LOADING.md#toml](LOADING.md)
- INI → [LOADING.md#ini](LOADING.md)
- ENV → [LOADING.md#load-from-env](LOADING.md)

## Document Stats

| Document | Focus |
|----------|-------|
| SKILL.md | Overview, installation, quick start |
| LOADING.md | Loading from all sources |
| USAGE.md | Reading, binding, setting values |
| ADVANCED.md | Options, events, watching, instances |

Designed for quick reference - each document focuses on one aspect without duplication.
