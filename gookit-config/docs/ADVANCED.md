# Advanced Features

Advanced options, events, file watching, dumping, and multiple instances.

## Configuration Options

### Available Options

```go
type Options struct {
    // Parse ENV vars in values: ${VAR|default}
    ParseEnv bool

    // Parse time.Duration strings: 30s, 5m, 1h
    ParseTime bool

    // Make config readonly
    Readonly bool

    // Enable data cache for better performance
    EnableCache bool

    // Enable key path parsing: "app.name"
    ParseKey bool

    // Key path delimiter (default: '.')
    Delimiter byte

    // Default format for DumpTo
    DumpFormat string

    // Default format for reading
    ReadFormat string

    // Decoder config for struct binding
    DecoderConfig *mapstructure.DecoderConfig

    // Hook function for events
    HookFunc HookFunc

    // Parse default tag in struct binding
    ParseDefault bool
}
```

### Setting Options

```go
// Single option
config.WithOptions(config.ParseEnv)

// Multiple options
config.WithOptions(config.ParseEnv, config.ParseDefault)

// Function-based
config.WithOptions(func(opt *config.Options) {
    opt.ParseEnv = true
    opt.ParseDefault = true
    opt.Readonly = false
})

// Pre-defined option functions
config.WithOptions(
    config.ParseEnv,
    config.ParseDefault,
    config.ParseTime,
    config.EnableCache,
    config.Readonly,
)
```

### Custom Tag Names

```go
// Change struct tag from "mapstructure" to "config"
config.WithOptions(func(opt *config.Options) {
    opt.DecoderConfig.TagName = "config"
})

type Config struct {
    Name string `config:"name"`
    Port int    `config:"port"`
}
```

### Custom Delimiter

```go
// Change key delimiter from '.' to ':'
config.WithOptions(func(opt *config.Options) {
    opt.Delimiter = ':'
})

// Now use:
config.String("app:name")
config.Int("server:port")
```

## Events and Hooks

### Available Events

- `load.data` - Data loaded from source
- `set.value` - Single value set
- `set.data` - Bulk data set
- `clean.data` - Data cleared
- `reload.data` - Config reloaded

### Add Hook Function

```go
hookFn := func(event string, c *config.Config) {
    fmt.Printf("Event: %s\n", event)

    switch event {
    case config.OnLoadData:
        fmt.Println("Config loaded")
    case config.OnSetValue:
        fmt.Println("Value changed")
    case config.OnReloadData:
        fmt.Println("Config reloaded")
    }
}

// Set hook
config.WithOptions(config.WithHookFunc(hookFn))
```

### Example: Log Changes

```go
logger := log.New(os.Stdout, "CONFIG: ", log.LstdFlags)

config.WithOptions(config.WithHookFunc(func(event string, c *config.Config) {
    logger.Printf("Event %s triggered\n", event)

    if event == config.OnSetValue {
        logger.Println("Config value changed, consider restart")
    }
}))
```

### Example: Auto-Save on Change

```go
config.WithOptions(config.WithHookFunc(func(event string, c *config.Config) {
    if event == config.OnSetValue || event == config.OnSetData {
        // Save to file
        buf := new(bytes.Buffer)
        c.DumpTo(buf, config.YAML)
        ioutil.WriteFile("config.yaml", buf.Bytes(), 0644)
    }
}))
```

## Watch File Changes

Monitor config files and reload on changes:

```go
import "github.com/fsnotify/fsnotify"

func WatchConfig(configFile string) error {
    watcher, err := fsnotify.NewWatcher()
    if err != nil {
        return err
    }

    config.WithOptions(config.WithHookFunc(func(event string, c *config.Config) {
        if event == config.OnReloadData {
            fmt.Println("Config reloaded from file change")
            // Rebind to structs if needed
            var cfg MyConfig
            c.Decode(&cfg)
            applyNewConfig(cfg)
        }
    }))

    go func() {
        for {
            select {
            case event := <-watcher.Events:
                if event.Op&fsnotify.Write == fsnotify.Write {
                    fmt.Println("Config file modified, reloading...")
                    config.ReloadFiles()
                }

            case err := <-watcher.Errors:
                log.Println("Watcher error:", err)
            }
        }
    }()

    return watcher.Add(configFile)
}

// Usage
config.LoadFiles("config.yaml")
WatchConfig("config.yaml")
```

### Complete Watch Example

```go
type AppConfig struct {
    Debug   bool
    LogLevel string
}

var currentConfig AppConfig

func setupWatch() {
    config.LoadFiles("config.yaml")
    config.Decode(&currentConfig)

    // Setup reload hook
    config.WithOptions(config.WithHookFunc(func(event string, c *config.Config) {
        if event == config.OnReloadData {
            var newConfig AppConfig
            c.Decode(&newConfig)

            // Apply changes
            if newConfig.Debug != currentConfig.Debug {
                log.Println("Debug mode changed:", newConfig.Debug)
                applyDebugMode(newConfig.Debug)
            }

            if newConfig.LogLevel != currentConfig.LogLevel {
                log.Println("Log level changed:", newConfig.LogLevel)
                applyLogLevel(newConfig.LogLevel)
            }

            currentConfig = newConfig
        }
    }))

    // Watch file
    WatchConfig("config.yaml")
}
```

## Dump Configuration

### Export to Writer

```go
import "bytes"

buf := new(bytes.Buffer)

// Dump as JSON
_, err := config.DumpTo(buf, config.JSON)

// Dump as YAML
_, err := config.DumpTo(buf, config.YAML)

// Dump as TOML
_, err := config.DumpTo(buf, config.TOML)
```

### Export to File

```go
// JSON file
buf := new(bytes.Buffer)
config.DumpTo(buf, config.JSON)
ioutil.WriteFile("config.json", buf.Bytes(), 0644)

// YAML file
buf := new(bytes.Buffer)
config.DumpTo(buf, config.YAML)
ioutil.WriteFile("config.yaml", buf.Bytes(), 0644)

// Pretty JSON
config.JSONMarshalIndent = "    "
buf := new(bytes.Buffer)
config.DumpTo(buf, config.JSON)
ioutil.WriteFile("config.pretty.json", buf.Bytes(), 0644)
```

### Dump to HTTP Response

```go
func configHandler(w http.ResponseWriter, r *http.Request) {
    format := r.URL.Query().Get("format")
    if format == "" {
        format = config.JSON
    }

    w.Header().Set("Content-Type", "application/"+format)
    config.DumpTo(w, format)
}

// GET /config?format=yaml
// GET /config?format=json
```

## Multiple Config Instances

### Create Custom Instances

```go
// Create with default options
appConfig := config.New("app-config")
dbConfig := config.New("db-config")

// Create empty (no default drivers)
myConfig := config.NewEmpty("my-config")

// Create with options
readonlyConfig := config.NewWithOptions(
    "readonly",
    config.Readonly,
    config.ParseEnv,
)
```

### Use Multiple Instances

```go
// Separate configs for different purposes
appConfig := config.New("app")
appConfig.AddDriver(yaml.Driver)
appConfig.LoadFiles("app.yaml")

dbConfig := config.New("database")
dbConfig.AddDriver(yaml.Driver)
dbConfig.LoadFiles("database.yaml")

cacheConfig := config.New("cache")
cacheConfig.LoadFiles("cache.json")

// Use independently
appName := appConfig.String("name")
dbHost := dbConfig.String("host")
cacheTTL := cacheConfig.Int("ttl")
```

### Instance Management

```go
type ConfigManager struct {
    configs map[string]*config.Config
}

func NewConfigManager() *ConfigManager {
    return &ConfigManager{
        configs: make(map[string]*config.Config),
    }
}

func (m *ConfigManager) Load(name, file string) error {
    cfg := config.New(name)
    cfg.AddDriver(yaml.Driver)

    if err := cfg.LoadFiles(file); err != nil {
        return err
    }

    m.configs[name] = cfg
    return nil
}

func (m *ConfigManager) Get(name string) *config.Config {
    return m.configs[name]
}

// Usage
manager := NewConfigManager()
manager.Load("app", "app.yaml")
manager.Load("db", "database.yaml")

appCfg := manager.Get("app")
dbCfg := manager.Get("db")
```

## Custom Drivers

Create driver for custom format:

```go
import "encoding/xml"

// XML driver
type XmlDriver struct{}

func (d *XmlDriver) Name() string {
    return "xml"
}

func (d *XmlDriver) GetDecoder() config.Decoder {
    return config.DecoderFunc(xml.Unmarshal)
}

func (d *XmlDriver) GetEncoder() config.Encoder {
    return config.EncoderFunc(xml.Marshal)
}

// Register and use
config.AddDriver(&XmlDriver{})
config.LoadFiles("config.xml")
```

## Advanced Patterns

### Configuration Builder

```go
type ConfigBuilder struct {
    cfg *config.Config
}

func NewConfigBuilder() *ConfigBuilder {
    return &ConfigBuilder{
        cfg: config.New("builder"),
    }
}

func (b *ConfigBuilder) WithYAML() *ConfigBuilder {
    b.cfg.AddDriver(yaml.Driver)
    return b
}

func (b *ConfigBuilder) WithOptions(opts ...func(*config.Options)) *ConfigBuilder {
    b.cfg.WithOptions(opts...)
    return b
}

func (b *ConfigBuilder) LoadFiles(files ...string) *ConfigBuilder {
    b.cfg.LoadFiles(files...)
    return b
}

func (b *ConfigBuilder) Build() *config.Config {
    return b.cfg
}

// Usage
cfg := NewConfigBuilder().
    WithYAML().
    WithOptions(config.ParseEnv).
    LoadFiles("config.yaml", "local.yaml").
    Build()
```

### Config Inheritance

```go
// Base config
base := config.New("base")
base.LoadFiles("base.yaml")

// Child inherits from base
child := config.New("child")
child.LoadData(base.Data()) // Copy base data
child.LoadFiles("child.yaml") // Override with child

// Use child config
value := child.String("key")
```

### Cached Config Access

```go
config.WithOptions(config.EnableCache)

// First access: reads and caches
val1 := config.String("expensive.key")

// Second access: returns cached value
val2 := config.String("expensive.key") // faster

// Clear cache
config.ClearData()
```

### Thread-Safe Access

```go
import "sync"

type SafeConfig struct {
    cfg *config.Config
    mu  sync.RWMutex
}

func (sc *SafeConfig) Get(key string) any {
    sc.mu.RLock()
    defer sc.mu.RUnlock()
    return sc.cfg.Get(key)
}

func (sc *SafeConfig) Set(key string, val any) error {
    sc.mu.Lock()
    defer sc.mu.Unlock()
    return sc.cfg.Set(key, val)
}
```

## Testing with Config

### Mock Config for Tests

```go
func TestWithMockConfig(t *testing.T) {
    // Create test config
    testConfig := config.NewEmpty("test")
    testConfig.LoadData(map[string]any{
        "app": map[string]any{
            "name":  "testapp",
            "debug": true,
        },
    })

    // Use in test
    name := testConfig.String("app.name")
    assert.Equal(t, "testapp", name)
}
```

### Test Helpers

```go
func NewTestConfig(data map[string]any) *config.Config {
    cfg := config.NewEmpty("test")
    cfg.LoadData(data)
    return cfg
}

func TestApp(t *testing.T) {
    cfg := NewTestConfig(map[string]any{
        "db": map[string]any{
            "host": "localhost",
            "port": 5432,
        },
    })

    // Test with config
    app := NewApp(cfg)
    // ...
}
```

## Performance Tips

1. **Enable cache** for frequently accessed keys
2. **Use Decode** once instead of multiple Get calls
3. **Avoid deep key paths** in hot code
4. **Readonly mode** prevents accidental modifications
5. **Load once** at startup, not per request
