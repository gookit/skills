# Using Configuration

Complete guide for reading, binding, and manipulating configuration data.

## Getting Values

### Basic Types

```go
// String
name := config.String("app.name")
name := config.String("app.name", "default") // with default

// Int
port := config.Int("server.port")
port := config.Int("server.port", 8080)

// Bool
debug := config.Bool("app.debug")
debug := config.Bool("app.debug", false)

// Float
timeout := config.Float("timeout")
timeout := config.Float("timeout", 30.0)

// Uint
workers := config.Uint("workers")
```

### Collections

```go
// String array
tags := config.Strings("tags")
// ["api", "web", "admin"]

// Int array
ports := config.Ints("ports")
// [8080, 8081, 8082]

// String map
settings := config.StringMap("settings")
// map[string]string{"key1": "val1", "key2": "val2"}

// Int map
limits := config.IntMap("limits")
// map[string]int{"cpu": 80, "memory": 90}

// Raw value (interface{})
data := config.Get("features")
```

### Key Path Access

Access nested values with dot notation:

```go
// config.yaml
database:
  master:
    host: db1.example.com
    port: 5432
  slaves:
    - host: db2.example.com
      port: 5432
    - host: db3.example.com
      port: 5432

// Access nested map
config.String("database.master.host")      // "db1.example.com"
config.Int("database.master.port")         // 5432

// Access array elements
config.String("database.slaves.0.host")    // "db2.example.com"
config.Int("database.slaves.1.port")       // 5432
```

### Check Existence

```go
if config.Exists("optional.feature") {
    feature := config.String("optional.feature")
    // use feature
}

// Check nested key
if config.Exists("db.master.host") {
    // key exists
}
```

### Get with Type Assertion

```go
value := config.Get("complex.data")

if m, ok := value.(map[string]any); ok {
    // handle map
}

if arr, ok := value.([]any); ok {
    // handle array
}
```

## Bind to Struct

### Basic Binding

```go
type Config struct {
    App struct {
        Name  string `mapstructure:"name"`
        Debug bool   `mapstructure:"debug"`
    } `mapstructure:"app"`

    Server struct {
        Host string `mapstructure:"host"`
        Port int    `mapstructure:"port"`
    } `mapstructure:"server"`
}

var cfg Config
err := config.Decode(&cfg)

fmt.Println(cfg.App.Name)    // "myapp"
fmt.Println(cfg.Server.Port) // 8080
```

### Bind Specific Key

```go
type ServerConfig struct {
    Host    string `mapstructure:"host"`
    Port    int    `mapstructure:"port"`
    Timeout int    `mapstructure:"timeout"`
}

var server ServerConfig
err := config.BindStruct("server", &server)

fmt.Println(server.Host) // "0.0.0.0"
fmt.Println(server.Port) // 8080
```

### Bind Only if Key Exists

```go
// Only bind if key exists, won't error if missing
var optional OptionalConfig
err := config.MapOnExists("optional", &optional)
```

### Custom Tag Names

```go
// Change tag name from "mapstructure" to "config"
config.WithOptions(func(opt *config.Options) {
    opt.DecoderConfig.TagName = "config"
})

type Config struct {
    Name string `config:"name"`
    Port int    `config:"port"`
}
```

### Default Values

#### From Struct Tags

```go
config.WithOptions(config.ParseDefault)

type ServerConfig struct {
    Host    string `default:"0.0.0.0"`
    Port    int    `default:"8080"`
    Timeout int    `default:"30"`
    SSL     bool   `default:"false"`
}

// Even if config file doesn't have these keys,
// struct will use default values
var server ServerConfig
config.BindStruct("server", &server)

// If config has no "server.host", server.Host = "0.0.0.0"
```

#### From ENV

```go
type DBConfig struct {
    Host string `default:"${DB_HOST|localhost}"`
    Port int    `default:"${DB_PORT|5432}"`
    User string `default:"${DB_USER}"`
}

config.WithOptions(config.ParseDefault, config.ParseEnv)

var db DBConfig
config.BindStruct("database", &db)

// Reads from ENV, falls back to defaults
```

### Nested Structs

```go
type AppConfig struct {
    App struct {
        Name  string `mapstructure:"name"`
        Debug bool   `mapstructure:"debug"`
    } `mapstructure:"app"`

    Database struct {
        Master struct {
            Host string `mapstructure:"host"`
            Port int    `mapstructure:"port"`
        } `mapstructure:"master"`

        Slaves []struct {
            Host string `mapstructure:"host"`
            Port int    `mapstructure:"port"`
        } `mapstructure:"slaves"`
    } `mapstructure:"database"`
}

var cfg AppConfig
config.Decode(&cfg)

fmt.Println(cfg.Database.Master.Host)
fmt.Println(cfg.Database.Slaves[0].Host)
```

### Time Duration

```go
config.WithOptions(config.ParseTime)

type Config struct {
    Timeout  time.Duration `mapstructure:"timeout"`
    Interval time.Duration `mapstructure:"interval"`
}

// config.yaml
timeout: 30s
interval: 5m

var cfg Config
config.Decode(&cfg)

fmt.Println(cfg.Timeout)  // 30s
fmt.Println(cfg.Interval) // 5m0s
```

## Setting Values

### Set Single Value

```go
// Set string
config.Set("app.name", "newname")

// Set int
config.Set("server.port", 9090)

// Set bool
config.Set("app.debug", false)

// Set nested value
config.Set("db.master.host", "newhost.com")
```

### Set Map Data

```go
config.SetData(map[string]any{
    "app": map[string]any{
        "name":  "myapp",
        "debug": true,
    },
    "server": map[string]any{
        "port": 8080,
    },
})
```

### Merge Data

```go
// Existing config
existing := map[string]any{
    "app": map[string]any{
        "name":  "myapp",
        "debug": false,
    },
}
config.LoadData(existing)

// Merge new data
newData := map[string]any{
    "app": map[string]any{
        "debug":   true,    // overrides
        "version": "1.0.0", // adds
    },
}
config.LoadData(newData)

// Result: name="myapp", debug=true, version="1.0.0"
```

## Working with Data

### Get All Data

```go
data := config.Data()
// Returns: map[string]any

// Iterate
for key, value := range data {
    fmt.Printf("%s: %v\n", key, value)
}
```

### Get Sub-Data

```go
// Get entire section as map
dbData := config.StringMap("database")
// map[string]string{"host": "localhost", "port": "5432"}

// Get as generic map
serverData := config.Get("server").(map[string]any)
```

### Clear Data

```go
// Clear all data
config.ClearData()

// Or use SetData with empty map
config.SetData(map[string]any{})
```

## Type Conversions

### Automatic Conversion

```go
// String to Int
config.Set("port", "8080")         // stored as string
port := config.Int("port")          // converted to int: 8080

// String to Bool
config.Set("debug", "true")
debug := config.Bool("debug")       // converted to bool: true

// String to Float
config.Set("timeout", "30.5")
timeout := config.Float("timeout")  // converted to float: 30.5
```

### Array Conversions

```go
// String array from comma-separated
config.Set("tags", "api,web,admin")
tags := config.Strings("tags") // []string{"api", "web", "admin"}

// Int array from comma-separated
config.Set("ports", "8080,8081,8082")
ports := config.Ints("ports") // []int{8080, 8081, 8082}
```

## Practical Patterns

### Application Config

```go
type AppConfig struct {
    Name    string `mapstructure:"name" default:"myapp"`
    Env     string `mapstructure:"env" default:"dev"`
    Debug   bool   `mapstructure:"debug" default:"false"`
    Version string `mapstructure:"version" default:"1.0.0"`
}

type DBConfig struct {
    Host     string `mapstructure:"host" default:"localhost"`
    Port     int    `mapstructure:"port" default:"5432"`
    Username string `mapstructure:"username" default:"${DB_USER}"`
    Password string `mapstructure:"password" default:"${DB_PASS}"`
    Database string `mapstructure:"database" default:"myapp"`
}

type Config struct {
    App      AppConfig `mapstructure:"app"`
    Database DBConfig  `mapstructure:"database"`
}

func LoadConfig() (*Config, error) {
    config.WithOptions(config.ParseDefault, config.ParseEnv)
    config.AddDriver(yaml.Driver)

    if err := config.LoadFiles("config.yaml"); err != nil {
        return nil, err
    }

    config.LoadExists("config.local.yaml")

    var cfg Config
    if err := config.Decode(&cfg); err != nil {
        return nil, err
    }

    return &cfg, nil
}
```

### Feature Flags

```go
// config.yaml
features:
  new_ui: true
  beta_api: false
  analytics: true

// Check features
if config.Bool("features.new_ui") {
    // enable new UI
}

if config.Bool("features.beta_api") {
    // enable beta API
}
```

### Environment Detection

```go
env := config.String("app.env", "development")

func IsDevelopment() bool {
    return env == "development"
}

func IsProduction() bool {
    return env == "production"
}

func IsTest() bool {
    return env == "test"
}

// Usage
if IsDevelopment() {
    config.Set("app.debug", true)
}
```

### Dynamic Config Updates

```go
// Update config at runtime
func UpdateConfig(key string, value any) error {
    if config.Readonly {
        return errors.New("config is readonly")
    }

    return config.Set(key, value)
}

// Use in handler
func handleUpdateConfig(w http.ResponseWriter, r *http.Request) {
    key := r.FormValue("key")
    value := r.FormValue("value")

    if err := UpdateConfig(key, value); err != nil {
        http.Error(w, err.Error(), 500)
        return
    }

    w.Write([]byte("Config updated"))
}
```

### Config Validation

```go
func ValidateConfig() error {
    // Check required fields
    required := []string{
        "app.name",
        "database.host",
        "database.username",
    }

    for _, key := range required {
        if !config.Exists(key) {
            return fmt.Errorf("required config key missing: %s", key)
        }
    }

    // Validate values
    if config.Int("server.port") < 1024 {
        return errors.New("server.port must be >= 1024")
    }

    if config.Int("server.port") > 65535 {
        return errors.New("server.port must be <= 65535")
    }

    return nil
}

// Use after loading
config.LoadFiles("config.yaml")
if err := ValidateConfig(); err != nil {
    log.Fatal(err)
}
```

### Readonly Config

```go
// Load config
config.WithOptions(config.ParseEnv)
config.LoadFiles("config.yaml")

// Make readonly after loading
config.WithOptions(config.Readonly)

// This will fail
err := config.Set("app.name", "newname")
// Error: config is readonly
```
