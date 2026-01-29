# GoUtil - cflag Package Reference

**Import**: `github.com/gookit/goutil/cflag`

Enhanced flag parsing library for building command-line applications. Wraps and extends Go's standard `flag` package.

## Table of Contents

- [Overview](#overview)
- [Basic Usage](#basic-usage)
- [Flag Types](#flag-types)
- [Advanced Features](#advanced-features)
- [Create Mulit Command App](#create-cli-application)
- [Validation](#validation)
- [Complete Examples](#complete-examples)

---

## Overview

### Features

- Extends standard `flag.FlagSet`
- Support for short and long flags (-h, --help)
- Custom validators
- Enum flags
- Key-value pair flags
- Automatic help generation
- Support for required arguments
- Subcommand support

### Installation

```bash
go get github.com/gookit/goutil/cflag
```

---

## Basic Usage

### Creating CFlags

```go
import "github.com/gookit/goutil/cflag"

// Create new cflag instance
c := cflag.New()

// Create with options
c := cflag.NewWith("myapp", "1.0.0", "My application description")

// Create with functional options
c := cflag.New(
    cflag.WithDesc("My application"),
    cflag.WithVersion("1.0.0"),
)
```

### Defining Flags

```go
var (
    name    string
    age     int
    verbose bool
)

c := cflag.New()

// String flag with short option
c.StrVar(&name, "name", "n", "", "Your name")

// Int flag
c.IntVar(&age, "age", "a", 0, "Your age")

// Bool flag
c.BoolVar(&verbose, "verbose", "v", false, "Verbose output")

// Parse command line
c.Parse()
```

### Parsing

```go
// Parse os.Args
err := c.Parse()
if err != nil {
    fmt.Println("Error:", err)
    os.Exit(1)
}

// Must parse (panics on error)
c.MustParse()

// Parse custom args
err = c.ParseArgs([]string{"--name", "John", "--age", "30"})
```

---

## Flag Types

### String Flags

```go
var name string
c.StrVar(&name, "name", "n", "", "User name")

// With default value
var config string
c.StrVar(&config, "config", "c", "config.yml", "Config file")
```

### Integer Flags

```go
var port int
c.IntVar(&port, "port", "p", 8080, "Server port")

var count int64
c.Int64Var(&count, "count", "", 0, "Item count")

var size uint
c.UintVar(&size, "size", "s", 0, "Buffer size")
```

### Boolean Flags

```go
var verbose bool
c.BoolVar(&verbose, "verbose", "v", false, "Verbose output")

var debug bool
c.BoolVar(&debug, "debug", "d", false, "Debug mode")
```

### Float Flags

```go
var threshold float64
c.Float64Var(&threshold, "threshold", "t", 0.5, "Threshold value")
```

### Slice Flags

```go
var tags []string
c.StrSliceVar(&tags, "tags", "t", nil, "Tags list")
// Usage: --tags=tag1,tag2,tag3

var ports []int
c.IntSliceVar(&ports, "ports", "", nil, "Port list")
// Usage: --ports=8080,8081,8082
```

---

## Advanced Features

### Enum Flags

Restrict flag value to specific options:

```go
var logLevel string

// Create enum with allowed values
enumLevel := cflag.NewEnumString("debug", "info", "warn", "error")
c.Var(enumLevel, "level", "l", "Log level")

// Parse
c.MustParse()
logLevel = enumLevel.String()
```

### Key-Value Flags

Parse key=value pairs:

```go
// Create key-value flag
kvFlag := cflag.NewKVString()
c.Var(kvFlag, "env", "e", "Environment variables")

// Usage: --env key1=value1 --env key2=value2
c.MustParse()

// Access values
value := kvFlag.Get("key1")
allValues := kvFlag.Values()
```

### Custom Validators

```go
// Integer with validation
var port int
portVar := cflag.NewIntVar(cflag.LimitInt(1024, 65535))
c.Var(portVar, "port", "p", "Server port (1024-65535)")

c.MustParse()
port = portVar.Int()
```

### Required Arguments

```go
// Define required argument
arg := cflag.NewArg("filename", "Input file", true)  // true = required
c.AddArg(arg)

c.MustParse()

// Get argument value
filename := c.Arg(0)
if filename == "" {
    fmt.Println("Error: filename is required")
    os.Exit(1)
}
```

---

## Validation

### Built-in Validators

```go
// Integer range validation
portVar := cflag.NewIntVar(cflag.LimitInt(1024, 65535))
c.Var(portVar, "port", "p", "Server port")

// String validation with custom function
validator := func(val string) error {
    if len(val) < 3 {
        return errors.New("name must be at least 3 characters")
    }
    return nil
}
nameVar := cflag.NewStrVar(validator)
c.Var(nameVar, "name", "n", "User name")
```

### Custom Validators

```go
type EmailValidator struct {
    value string
}

func (e *EmailValidator) String() string {
    return e.value
}

func (e *EmailValidator) Set(val string) error {
    if !strings.Contains(val, "@") {
        return errors.New("invalid email format")
    }
    e.value = val
    return nil
}

// Use custom validator
emailVar := &EmailValidator{}
c.Var(emailVar, "email", "e", "Email address")
```

---

## Complete Examples

### Simple CLI Tool

```go
package main

import (
    "fmt"
    "os"
    "github.com/gookit/goutil/cflag"
)

func main() {
    var (
        name    string
        age     int
        verbose bool
    )

    // Create and configure
    c := cflag.NewWith(
        "userinfo",
        "1.0.0",
        "Display user information",
    )

    // Define flags
    c.StrVar(&name, "name", "n", "", "User name (required)")
    c.IntVar(&age, "age", "a", 0, "User age")
    c.BoolVar(&verbose, "verbose", "v", false, "Verbose output")

    // Parse
    c.MustParse()

    // Validate
    if name == "" {
        fmt.Println("Error: name is required")
        c.PrintHelp()
        os.Exit(1)
    }

    // Execute
    fmt.Printf("Name: %s\n", name)
    if age > 0 {
        fmt.Printf("Age: %d\n", age)
    }

    if verbose {
        fmt.Println("Verbose mode enabled")
    }
}
```

**Usage:**
```bash
./userinfo --name John --age 30 --verbose
./userinfo -n John -a 30 -v
```

### Advanced CLI with Validation

```go
package main

import (
    "fmt"
    "os"
    "github.com/gookit/goutil/cflag"
)

func main() {
    var (
        host     string
        port     int
        logLevel string
        envVars  *cflag.KVString
    )

    c := cflag.NewWith("server", "1.0.0", "HTTP server")

    // Host
    c.StrVar(&host, "host", "h", "localhost", "Server host")

    // Port with validation
    portVar := cflag.NewIntVar(cflag.LimitInt(1024, 65535))
    c.Var(portVar, "port", "p", "Server port (1024-65535)")

    // Log level enum
    enumLevel := cflag.NewEnumString("debug", "info", "warn", "error")
    c.Var(enumLevel, "level", "l", "Log level")

    // Environment variables (key=value)
    envVars = cflag.NewKVString()
    c.Var(envVars, "env", "e", "Environment variables")

    // Parse
    if err := c.Parse(); err != nil {
        fmt.Println("Error:", err)
        c.PrintHelp()
        os.Exit(1)
    }

    // Get values
    port = portVar.Int()
    logLevel = enumLevel.String()

    // Display config
    fmt.Printf("Server starting...\n")
    fmt.Printf("  Host: %s\n", host)
    fmt.Printf("  Port: %d\n", port)
    fmt.Printf("  Log Level: %s\n", logLevel)

    if len(envVars.Values()) > 0 {
        fmt.Println("  Environment:")
        for k, v := range envVars.Values() {
            fmt.Printf("    %s=%s\n", k, v)
        }
    }
}
```

**Usage:**
```bash
./server --port 8080 --level info --env DB_HOST=localhost --env DB_PORT=5432
./server -p 8080 -l info -e DB_HOST=localhost -e DB_PORT=5432
```

### File Processor with Arguments

```go
package main

import (
    "fmt"
    "os"
    "github.com/gookit/goutil/cflag"
    "github.com/gookit/goutil/fsutil"
)

func main() {
    var (
        output  string
        format  string
        verbose bool
    )

    c := cflag.NewWith("fileproc", "1.0.0", "File processor")

    // Flags
    c.StrVar(&output, "output", "o", "output.txt", "Output file")

    formatEnum := cflag.NewEnumString("json", "xml", "yaml")
    c.Var(formatEnum, "format", "f", "Output format")

    c.BoolVar(&verbose, "verbose", "v", false, "Verbose output")

    // Required argument
    inputArg := cflag.NewArg("input", "Input file", true)
    c.AddArg(inputArg)

    // Parse
    c.MustParse()

    // Get arguments
    inputFile := c.Arg(0)
    if inputFile == "" {
        fmt.Println("Error: input file is required")
        c.PrintHelp()
        os.Exit(1)
    }

    format = formatEnum.String()

    // Validate input file
    if !fsutil.FileExists(inputFile) {
        fmt.Printf("Error: file not found: %s\n", inputFile)
        os.Exit(1)
    }

    // Process
    if verbose {
        fmt.Printf("Processing %s...\n", inputFile)
        fmt.Printf("Format: %s\n", format)
        fmt.Printf("Output: %s\n", output)
    }

    // ... processing logic ...

    fmt.Println("Done!")
}
```

**Usage:**
```bash
./fileproc input.txt --output result.json --format json --verbose
./fileproc input.txt -o result.json -f json -v
```

### Interactive CLI

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/cflag"
    "github.com/gookit/goutil/cliutil"
)

func main() {
    var (
        name  string
        email string
        auto  bool
    )

    c := cflag.New(cflag.WithDesc("User registration"))

    c.StrVar(&name, "name", "n", "", "User name")
    c.StrVar(&email, "email", "e", "", "Email address")
    c.BoolVar(&auto, "auto", "a", false, "Auto mode (no prompts)")

    c.MustParse()

    // Interactive mode if not auto
    if !auto {
        if name == "" {
            name, _ = cliutil.ReadInput("Enter your name: ")
        }

        if email == "" {
            email, _ = cliutil.ReadInput("Enter your email: ")
        }

        if !cliutil.Confirm("Create account?", true) {
            fmt.Println("Cancelled")
            return
        }
    }

    // Validate
    if name == "" || email == "" {
        fmt.Println("Error: name and email are required")
        return
    }

    // Create account
    fmt.Printf("Creating account for %s (%s)...\n", name, email)
    fmt.Println("Account created successfully!")
}
```

**Usage:**
```bash
# Interactive mode
./register

# Auto mode with flags
./register --name John --email john@example.com --auto
./register -n John -e john@example.com -a
```

---

## Create cli application

Use `cflag/capp` to quickly build a multi-command application.

eg: CLI app entry `cmd/your-cliapp/main.go`:

```go cmd/your-cliapp/main.go
package main

import (
	"your-cliapp/internal/cli"
)

// Version information (set by ldflags)
var (
	Version   = "develop" // eg: v1.0.0
	CommitID  = "unknown" // eg: 12345678
	BuildDate = ""        // eg: 2023-01-01T00:00:00Z
)

func main() {
	cli.Run(Version, BuildDate, CommitID)
}
```

register multi commands:

```go your-cliapp/internal/cli/cli.go
package cli

import (
	"your-cliapp/internal/config"

	"github.com/gookit/goutil/cflag/capp"
	"github.com/gookit/goutil/x/ccolor"
)

var (
	configPath string
	logLevel   string
)

func Run(version, buildDate, buildHash string) {
	if buildDate == "" {
		buildDate = time.Now().Format("2006-01-02 15:04:05")
	}
	if len(buildHash) > 8 {
		buildHash = buildHash[:8]
	}

	app := capp.NewApp()
	app.Name = "your-cliapp"
	app.Desc = fmt.Sprintf("remote init a edge linux device\n build: %s, hash: %s", buildDate, buildHash)
	app.Version = version

    // 全局参数
	app.StringVar(&configPath, "config", "config.yaml", "配置文件路径;;c")
	app.StringVar(&logLevel, "log-level", "info", "日志级别 (debug, info, warn, error)")

	app.BeforeRun = func(c *capp.Cmd, args []string) bool {
		if err := bootstrap(); err != nil {
			ccolor.Errorf("初始化失败: %s\n", err)
			return false
		}
		return true
	}

	// 添加命令
	addCommands(app)

	// 运行应用
	app.Run()
}

func addCommands(app *capp.App) {
	app.Add(newGetIPCmd(), newInitCmd(), newAddDhcpCmd())
}

func bootstrap() error {
	// load .env file

	// 初始化配置
	if err := config.Init(configPath); err != nil {
		return err
	}

	// init logger
	// return logger.Init(&config.Cfg().Logging)
	return nil
}
```


one command example:

```go your-cliapp/internal/cli/getip_cmd.go
package cli

type GetIPOptions struct {
	Hostname string
	RouterURL string
	SesskeyFile string
}

func newGetIPCmd() *capp.Cmd {
	opts := &GetIPOptions{}
	c := capp.NewCmd("get-ip", "discover new device IP from router", func(c *capp.Cmd) error {
		return runGetIP(opts)
	})

	c.StringVar(&opts.Hostname, "hostname", "", "device hostnamt filter")
	c.StringVar(&opts.RouterURL, "router-url", "http://172.20.0.1", "router management addr")
	c.StringVar(&opts.SesskeyFile, "sesskey-file", ".ikuai.sesskey", "login sesskey file path")

	return c
}

func runGetIP(opts *GetIPOptions) error {
    // handle logic
}
```

## Best Practices

### 1. Provide Short and Long Options

```go
// Good: both short and long options
c.StrVar(&name, "name", "n", "", "User name")

// Acceptable: long only for less common flags
c.BoolVar(&debug, "debug", "", false, "Debug mode")
```

### 2. Use Sensible Defaults

```go
// Good: provide useful defaults
c.IntVar(&port, "port", "p", 8080, "Server port")
c.StrVar(&config, "config", "c", "config.yml", "Config file")
```

### 3. Add Clear Descriptions

```go
// Good: clear and concise
c.StrVar(&host, "host", "h", "localhost", "Server host address")

// Avoid: too vague
c.StrVar(&host, "host", "h", "localhost", "Host")
```

### 4. Validate Input

```go
// Use validators for constraints
portVar := cflag.NewIntVar(cflag.LimitInt(1024, 65535))
c.Var(portVar, "port", "p", "Server port (1024-65535)")

// Use enums for specific choices
level := cflag.NewEnumString("debug", "info", "warn", "error")
c.Var(level, "level", "l", "Log level")
```

### 5. Handle Errors Gracefully

```go
if err := c.Parse(); err != nil {
    fmt.Fprintf(os.Stderr, "Error: %v\n", err)
    c.PrintHelp()
    os.Exit(1)
}
```

---

## Utilities

### Helper Functions

```go
// Check if flag name is valid
if cflag.IsGoodName("my-flag") {
    // Valid flag name
}

// Add prefix to flag
flagName := cflag.AddPrefix("help")  // "--help"

// Add both short and long
flagName := cflag.AddPrefixes("help", []string{"h"})  // "-h, --help"

// Split shortcut string
shorts := cflag.SplitShortcut("vh")  // []string{"v", "h"}
```

### Debug Mode

```go
// Enable debug output
cflag.SetDebug(true)

// Debug messages will be printed
cflag.DebugMsg("Parsing flag: %s", "name")
```

---

**Related Documentation:**
- [Main Skill Documentation](SKILL.md)
- [CLI Utilities](system-cli-packages.md#cliutil---cli-utilities)
- [timex Reference](timex-reference.md)
