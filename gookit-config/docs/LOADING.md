# Loading Configuration

Complete guide for loading configuration from various sources.

## Load from Files

### Single File

```go
import (
    "github.com/gookit/config/v2"
    "github.com/gookit/config/v2/yaml"
)

config.AddDriver(yaml.Driver)
err := config.LoadFiles("config.yaml")
```

### Multiple Files

Files are automatically merged by key:

```go
// All at once
config.LoadFiles("base.yaml", "prod.yaml", "local.yaml")

// Or separately (same result)
config.LoadFiles("base.yaml")
config.LoadFiles("prod.yaml")  // Overrides base
config.LoadFiles("local.yaml") // Overrides prod
```

**Merge behavior:**

```yaml
# base.yaml
app:
  name: myapp
  debug: true
  timeout: 30

# prod.yaml
app:
  debug: false
  timeout: 60
  workers: 4

# Result after merging
app:
  name: myapp       # from base
  debug: false      # overridden by prod
  timeout: 60       # overridden by prod
  workers: 4        # from prod
```

### Load if Exists

Skip error if file doesn't exist:

```go
// Won't error if file missing
config.LoadExists("config.local.yaml")
config.LoadExists("config.yaml", "config.local.yaml")
```

### Load by Format

Specify format explicitly:

```go
// Load YAML files
config.LoadFilesByFormat("yaml", "app.yml", "db.yml")

// Load JSON files
config.LoadFilesByFormat("json", "config.json", "override.json")
```

### Load from Directory

Load all files from a directory:

```go
// Load all .yaml files from config/
// File names become top-level keys
config.LoadFromDir("./config", "yaml")

// Directory structure:
// config/
//   app.yaml    -> config.Get("app")
//   db.yaml     -> config.Get("db")
//   cache.yaml  -> config.Get("cache")
```

## Load from ENV

### Map ENV to Config Keys

```go
// OS ENV: APP_NAME=myapp DB_HOST=localhost DB_PORT=5432

config.LoadOSEnvs(map[string]string{
    "APP_NAME": "app.name",
    "DB_HOST":  "database.host",
    "DB_PORT":  "database.port",
})

config.String("app.name")      // "myapp"
config.String("database.host") // "localhost"
config.Int("database.port")    // 5432
```

### Nested Keys

Map ENV to nested structure:

```go
// APP_DEBUG=true SERVER_HOST=0.0.0.0 SERVER_PORT=8080

config.LoadOSEnvs(map[string]string{
    "APP_DEBUG":    "app.debug",
    "SERVER_HOST":  "server.host",
    "SERVER_PORT":  "server.port",
})

// Access nested values
config.Bool("app.debug")      // true
config.String("server.host")  // "0.0.0.0"
config.Int("server.port")     // 8080
```

### ENV with Defaults

Use `ParseEnv` option to parse ENV vars in config values:

```go
config.WithOptions(config.ParseEnv)

// config.yaml
database:
  host: ${DB_HOST|localhost}
  port: ${DB_PORT|5432}
  name: ${DB_NAME}

// If DB_HOST not set, uses "localhost"
// If DB_PORT not set, uses "5432"
// DB_NAME required (no default)
```

## Load from CLI Flags

### Basic Flags

```go
// Define flags
config.LoadFlags([]string{
    "env",        // string flag
    "debug:bool", // bool flag
    "port:int",   // int flag
})

// Run: myapp --env prod --debug --port 9090

config.String("env")  // "prod"
config.Bool("debug")  // true
config.Int("port")    // 9090
```

### Flags with Descriptions

```go
config.LoadFlags([]string{
    "env:set the environment (dev/prod)",
    "debug:bool:enable debug mode",
    "port:int:server port",
    "workers:int:number of workers",
})
```

### Nested Keys from Flags

```go
config.LoadFlags([]string{
    "db.host",
    "db.port:int",
    "cache.ttl:int",
})

// Run: myapp --db.host localhost --db.port 5432 --cache.ttl 3600

config.String("db.host")   // "localhost"
config.Int("db.port")      // 5432
config.Int("cache.ttl")    // 3600
```

### Flag Types

```go
// String (default)
"name"          // --name value
"name:desc"     // --name value

// Bool
"debug:bool"    // --debug (no value needed)
"verbose:bool:enable verbose output"

// Int
"port:int"      // --port 8080
"workers:int:number of workers"
```

## Load from Remote URL

Load config from HTTP/HTTPS:

```go
// JSON from URL
err := config.LoadRemote("json", "https://example.com/config.json")

// YAML from URL
err := config.LoadRemote("yaml", "https://example.com/config.yaml")

// With authentication
client := &http.Client{
    Transport: &customTransport{token: "secret"},
}
config.WithOptions(config.WithHTTPClient(client))
err := config.LoadRemote("json", "https://api.example.com/config")
```

## Load from Strings

```go
// JSON string
jsonStr := `{"app": {"name": "myapp", "debug": true}}`
config.LoadStrings("json", jsonStr)

// YAML string
yamlStr := `
app:
  name: myapp
  debug: true
`
config.LoadStrings("yaml", yamlStr)

// Multiple strings (auto-merged)
config.LoadStrings("json", baseJSON, overrideJSON)
```

## Load from Go Data

### From Struct

```go
type AppConfig struct {
    App struct {
        Name  string
        Debug bool
    }
    Server struct {
        Port int
    }
}

cfg := AppConfig{}
cfg.App.Name = "myapp"
cfg.App.Debug = true
cfg.Server.Port = 8080

config.LoadData(cfg)

config.String("app.name")  // "myapp"
config.Int("server.port")  // 8080
```

### From Map

```go
data := map[string]any{
    "app": map[string]any{
        "name":  "myapp",
        "debug": true,
    },
    "server": map[string]any{
        "port": 8080,
    },
}

config.LoadData(data)
```

### Multiple Data Sources

```go
base := map[string]any{"timeout": 30}
override := map[string]any{"timeout": 60}

config.LoadData(base, override)
config.Int("timeout") // 60 (overridden)
```

## Loading Strategies

### Environment-Specific Loading

```go
env := os.Getenv("APP_ENV")
if env == "" {
    env = "development"
}

// Load base config
config.LoadFiles("config.yaml")

// Load environment-specific overrides
config.LoadExists("config." + env + ".yaml")

// Load local overrides (not in git)
config.LoadExists("config.local.yaml")
```

### Layered Configuration

```go
// 1. Load defaults
config.LoadFiles("config.default.yaml")

// 2. Load environment config
config.LoadFiles("config." + env + ".yaml")

// 3. Load from ENV vars
config.LoadOSEnvs(envMap)

// 4. Load from flags (highest priority)
config.LoadFlags(flagDefs)

// Priority: flags > ENV > env file > default file
```

### Conditional Loading

```go
// Load based on environment
if isDevelopment() {
    config.LoadFiles("config.dev.yaml")
} else {
    config.LoadFiles("config.prod.yaml")
}

// Load optional configs
if config.Bool("feature.advanced") {
    config.LoadExists("advanced.yaml")
}
```

## Format-Specific Loading

### JSON

```go
import "github.com/gookit/config/v2/json"

// JSON is default, no need to add driver
config.LoadFiles("config.json")

// JSON5 (with comments, trailing commas)
import "github.com/gookit/config/v2/json5"
config.AddDriver(json5.Driver)
config.LoadFiles("config.json5")
```

### YAML

```go
import "github.com/gookit/config/v2/yaml"

config.AddDriver(yaml.Driver)
config.LoadFiles("config.yaml", "config.yml")
```

### TOML

```go
import "github.com/gookit/config/v2/toml"

config.AddDriver(toml.Driver)
config.LoadFiles("config.toml")
```

### INI

```go
import "github.com/gookit/config/v2/ini"

config.AddDriver(ini.Driver)
config.LoadFiles("config.ini")
```

### Properties

```go
import "github.com/gookit/config/v2/properties"

config.AddDriver(properties.Driver)
config.LoadFiles("application.properties")
```

### HCL

```go
// HCL requires custom driver
import (
    "github.com/hashicorp/hcl"
    "github.com/gookit/config/v2"
)

// Implement custom driver
type HclDriver struct{}

func (d *HclDriver) Name() string { return "hcl" }
func (d *HclDriver) GetDecoder() config.Decoder {
    return config.DecoderFunc(hcl.Unmarshal)
}
func (d *HclDriver) GetEncoder() config.Encoder {
    return nil // if don't need encode
}

config.AddDriver(&HclDriver{})
config.LoadFiles("config.hcl")
```

## Loading Best Practices

1. **Load order matters**: Later loads override earlier ones
2. **Use `LoadExists`** for optional files
3. **Enable `ParseEnv`** to support ENV vars in config values
4. **Separate concerns**: base + environment + local
5. **Validate after loading**: Check required keys exist
6. **Handle errors**: Don't ignore loading errors in production

```go
// Good pattern
config.WithOptions(config.ParseEnv)
config.AddDriver(yaml.Driver)

if err := config.LoadFiles("config.yaml"); err != nil {
    log.Fatal(err)
}

config.LoadExists("config.local.yaml")

if err := config.LoadOSEnvs(envMap); err != nil {
    log.Fatal(err)
}

// Validate
if !config.Exists("app.name") {
    log.Fatal("app.name is required")
}
```
