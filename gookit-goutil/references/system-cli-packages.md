# GoUtil - System & CLI Packages Reference

Complete reference for GoUtil's system utilities and command-line interface packages.

## Table of Contents

- [cliutil - CLI Utilities](#cliutil---cli-utilities)
- [sysutil - System Utilities](#sysutil---system-utilities)
- [envutil - Environment Utilities](#envutil---environment-utilities)
- [fsutil - Filesystem Utilities](#fsutil---filesystem-utilities)
- [jsonutil - JSON Utilities](#jsonutil---json-utilities)

---

## cliutil - CLI Utilities

**Import**: `github.com/gookit/goutil/cliutil`

Command-line utilities for input/output, colored printing, and command execution.

### User Input

```go
import "github.com/gookit/goutil/cliutil"

// Read line of text
name, err := cliutil.ReadInput("Enter your name: ")
// User types: John Doe
// name = "John Doe"

// Read single line
line, err := cliutil.ReadLine("Enter text: ")

// Read first character
char, err := cliutil.ReadFirst("Continue? (y/n): ")
// char = "y" or "n"

// Read first byte
b, err := cliutil.ReadFirstByte("Press key: ")

// Read first rune
r, err := cliutil.ReadFirstRune("Enter character: ")
```

### Password Input

```go
// Read password (no echo)
password := cliutil.ReadPassword("Enter password: ")
// User types but characters are hidden
```

### Confirmation Prompts

```go
// Yes/No confirmation
confirmed := cliutil.Confirm("Continue?")
// Accepts: y, yes, Y, YES -> true
// Accepts: n, no, N, NO -> false

// With default value
confirmed := cliutil.Confirm("Continue?", true)  // Default is Yes

// Read as bool
result := cliutil.ReadAsBool("Enable feature?", false)

// Check if input is yes
if cliutil.InputIsYes("y") {
    // Yes was entered
}

if cliutil.ByteIsYes('y') {
    // Yes byte
}
```

### Command Execution

```go
// Execute command
output, err := cliutil.ExecCmd("ls", []string{"-la"})
fmt.Println(output)

// Execute with working directory
output, err := cliutil.ExecCmd("git", []string{"status"}, "/path/to/repo")

// Execute command line string
output, err := cliutil.ExecLine("git status", "/path/to/repo")

// Quick exec (combines both)
output, err := cliutil.QuickExec("ls -la")

// Shell execution
output, err := cliutil.ShellExec("echo $HOME")
```

### Command Line Parsing

```go
// Parse command line string to arguments
args := cliutil.ParseLine(`./app top sub --msg "has multi words"`)
// Result: []string{"./app", "top", "sub", "--msg", "has multi words"}

// Build command line from parts
line := cliutil.BuildLine("./myapp", []string{
    "-a", "val0",
    "-m", "this is message",
    "arg0",
})
// Result: "./myapp -a val0 -m \"this is message\" arg0"

// Shell quote string
quoted := cliutil.ShellQuote("hello world")  // "'hello world'"
```

### System Information

```go
// Get current working directory
workdir := cliutil.Workdir()

// Get binary directory
binDir := cliutil.BinDir()

// Get binary file path
binFile := cliutil.BinFile()

// Get binary name
binName := cliutil.BinName()

// Get terminal size
width, height := cliutil.GetTermSize()

// Get current shell
shell := cliutil.CurrentShell(false)  // Full path
shell := cliutil.CurrentShell(true)   // Name only

// Check if shell exists
if cliutil.HasShellEnv("bash") {
    // bash is available
}
```

### Output Formatting

```go
// Split command output into lines
output, _ := cliutil.ExecCmd("ls", []string{})
lines := cliutil.OutputLines(output)
for _, line := range lines {
    fmt.Println(line)
}

// Build option help name
helpName := cliutil.BuildOptionHelpName([]string{"help", "h"})
// Result: "-h, --help"
```

### Complete CLI Example

```go
package main

import (
    "fmt"
    "os"
    "github.com/gookit/goutil/cliutil"
)

func main() {
    fmt.Println("=== User Registration ===")

    // Get username
    username, err := cliutil.ReadInput("Username: ")
    if err != nil {
        fmt.Println("Error:", err)
        os.Exit(1)
    }

    // Get email
    email, err := cliutil.ReadInput("Email: ")
    if err != nil {
        fmt.Println("Error:", err)
        os.Exit(1)
    }

    // Get password
    password := cliutil.ReadPassword("Password: ")
    if len(password) < 8 {
        fmt.Println("Password too short")
        os.Exit(1)
    }

    // Confirm
    if !cliutil.Confirm("Create account?", true) {
        fmt.Println("Cancelled")
        os.Exit(0)
    }

    // Create account (example)
    fmt.Printf("Creating account for %s (%s)...\n", username, email)

    // Execute system command
    output, err := cliutil.ExecCmd("whoami", []string{})
    if err == nil {
        fmt.Printf("Current user: %s\n", output)
    }

    fmt.Println("Registration complete!")
}
```

---

## sysutil - System Utilities

**Import**: `github.com/gookit/goutil/sysutil`

System information and process management utilities.

### System Information

```go
import "github.com/gookit/goutil/sysutil"

// Get hostname
hostname := sysutil.Hostname()

// Get username
username := sysutil.Username()

// Get current user
user := sysutil.CurrentUser()

// Get home directory
home := sysutil.HomeDir()
home := sysutil.UserHomeDir()

// Get working directory
workdir := sysutil.Workdir()
```

### Process Operations

```go
// Check if process exists
exists := sysutil.ProcessExists(1234)

// Get current process ID
pid := sysutil.CurrentPID()

// Get parent process ID
ppid := sysutil.ParentPID()

// Find executable
path, err := sysutil.FindExecutable("git")
```

### Command Execution

```go
// Execute command
cmd := sysutil.NewCmd("ls", "-la")
output, err := cmd.Run()

// Execute with context
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
output, err := cmd.RunWithContext(ctx)
```

### Complete System Example

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/sysutil"
)

func main() {
    fmt.Println("=== System Information ===")
    fmt.Printf("Hostname: %s\n", sysutil.Hostname())
    fmt.Printf("Username: %s\n", sysutil.Username())
    fmt.Printf("Home: %s\n", sysutil.HomeDir())
    fmt.Printf("Workdir: %s\n", sysutil.Workdir())
    fmt.Printf("PID: %d\n", sysutil.CurrentPID())

    // Check if git is installed
    gitPath, err := sysutil.FindExecutable("git")
    if err == nil {
        fmt.Printf("Git found at: %s\n", gitPath)
    } else {
        fmt.Println("Git not found")
    }
}
```

---

## envutil - Environment Utilities

**Import**: `github.com/gookit/goutil/envutil`

Environment variable management and runtime information.

### Environment Variables

```go
import "github.com/gookit/goutil/envutil"

// Get environment variable
value := envutil.Get("HOME")
value := envutil.Getenv("PATH")

// Get with default
value := envutil.Get("API_KEY", "default-key")

// Set environment variable
envutil.Set("MY_VAR", "value")
envutil.Setenv("MY_VAR", "value")

// Set multiple
envutil.SetEnvs(map[string]string{
    "VAR1": "value1",
    "VAR2": "value2",
})

// Unset
envutil.Unset("MY_VAR")
```

### Environment Parsing

```go
// Parse environment variable
value := envutil.ParseEnvValue("${HOME}/config")
// Result: "/Users/username/config"

// Parse with variables
text := "Server: ${HOST}:${PORT}"
result := envutil.ParseEnvValue(text)
// Result: "Server: localhost:8080" (if HOST and PORT are set)
```

### Platform Detection

```go
// Check operating system
if envutil.IsWin() {
    fmt.Println("Running on Windows")
}

if envutil.IsMac() {
    fmt.Println("Running on macOS")
}

if envutil.IsLinux() {
    fmt.Println("Running on Linux")
}

if envutil.IsMSys() {
    fmt.Println("Running on MSys/Git Bash")
}

// Check if running in Docker
if envutil.IsDocker() {
    fmt.Println("Running in Docker container")
}

// Check if running in terminal
if envutil.IsTerminal() {
    fmt.Println("Running in terminal")
}
```

### Runtime Information

```go
// Check Go version
version := envutil.GoVersion()

// Check if specific Go version
if envutil.HasGoVersion("1.19") {
    // Go 1.19 or higher
}
```

### Complete Environment Example

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/envutil"
)

func main() {
    // Platform info
    fmt.Println("=== Platform ===")
    switch {
    case envutil.IsWin():
        fmt.Println("Windows")
    case envutil.IsMac():
        fmt.Println("macOS")
    case envutil.IsLinux():
        fmt.Println("Linux")
    }

    // Environment variables
    fmt.Println("\n=== Environment ===")
    fmt.Printf("HOME: %s\n", envutil.Get("HOME"))
    fmt.Printf("PATH: %s\n", envutil.Get("PATH"))

    // Set temporary config
    envutil.Set("APP_MODE", "development")
    mode := envutil.Get("APP_MODE", "production")
    fmt.Printf("Mode: %s\n", mode)

    // Parse environment
    configPath := envutil.ParseEnvValue("${HOME}/.myapp/config.yml")
    fmt.Printf("Config: %s\n", configPath)
}
```

---

## fsutil - Filesystem Utilities

**Import**: `github.com/gookit/goutil/fsutil`

File and directory operations with convenient helper functions.

### File Checking

```go
import "github.com/gookit/goutil/fsutil"

// Check if file exists
if fsutil.FileExists("test.txt") {
    // File exists
}

// Check if is file
if fsutil.IsFile("test.txt") {
    // Is a file
}

// Check if is directory
if fsutil.IsDir("mydir") {
    // Is a directory
}

// Check if path exists (file or directory)
if fsutil.PathExists("path/to/something") {
    // Exists
}

// Check if absolute path
if fsutil.IsAbsPath("/absolute/path") {
    // Is absolute
}

// Check if empty directory
if fsutil.IsEmptyDir("mydir") {
    // Directory is empty
}
```

### Directory Operations

```go
// Create directory
err := fsutil.Mkdir("mydir", 0755)

// Create directories recursively
err := fsutil.MkDirs("path/to/nested/dir", 0755)

// Create parent directories
err := fsutil.MkParentDir("path/to/file.txt")

// List directory
files, err := fsutil.ReadDir("mydir")

// Remove directory
err := fsutil.Remove("mydir")

// Remove directory recursively
err := fsutil.RemoveAll("mydir")
```

### File Reading

```go
// Read entire file
data, err := fsutil.ReadFile("test.txt")
content := string(data)

// Read file to string
content, err := fsutil.ReadString("test.txt")

// Read text lines
lines, err := fsutil.ReadLines("test.txt")
for _, line := range lines {
    fmt.Println(line)
}

// Read file or default
content := fsutil.MustReadFile("test.txt")
content := fsutil.GetContents("test.txt")
```

### File Writing

```go
// Write bytes to file
data := []byte("Hello, World!")
err := fsutil.WriteFile("test.txt", data, 0644)

// Write string
err := fsutil.WriteString("test.txt", "Hello, World!", 0644)

// Append to file
err := fsutil.AppendFile("test.txt", data, 0644)

// Append string
err := fsutil.AppendString("test.txt", "More content\n", 0644)

// Put contents (write or create)
err := fsutil.PutContents("test.txt", []byte("content"))
```

### File Operations

```go
// Copy file
err := fsutil.CopyFile("source.txt", "dest.txt")

// Copy with mode preservation
err := fsutil.CopyFile("source.txt", "dest.txt", fsutil.WithMode())

// Move file
err := fsutil.MoveFile("old.txt", "new.txt")

// Rename
err := fsutil.Rename("old.txt", "new.txt")

// Delete file
err := fsutil.DeleteFile("test.txt")
err := fsutil.Remove("test.txt")

// Create empty file
file, err := fsutil.CreateFile("test.txt", 0644, 0755)
```

### File Information

```go
// Get file size
size, err := fsutil.FileSize("test.txt")

// Get file mode
mode, err := fsutil.FileMode("test.txt")

// Get modification time
mtime, err := fsutil.ModTime("test.txt")

// Get file name without extension
name := fsutil.NameWithoutExt("test.txt")  // "test"

// Get file extension
ext := fsutil.Ext("test.txt")  // ".txt"

// Get directory name
dir := fsutil.Dir("path/to/file.txt")  // "path/to"

// Get base name
base := fsutil.Base("path/to/file.txt")  // "file.txt"
```

### Path Operations

```go
// Join paths
path := fsutil.JoinPath("path", "to", "file.txt")
// Result: "path/to/file.txt"

// Clean path
clean := fsutil.CleanPath("path//to/../file.txt")
// Result: "path/file.txt"

// Absolute path
abs, err := fsutil.Abs("relative/path")

// Real path (resolve symlinks)
real, err := fsutil.Realpath("symlink")
```

### Glob and Search

```go
// Find files by pattern
files, err := fsutil.Glob("*.txt")
files, err := fsutil.Glob("**/*.go")

// Search files
files, err := fsutil.Search("mydir", "*.txt", false)  // non-recursive
files, err := fsutil.Search("mydir", "*.txt", true)   // recursive
```

### Complete Filesystem Example

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/fsutil"
)

func main() {
    // Create directory structure
    err := fsutil.MkDirs("data/logs", 0755)
    if err != nil {
        panic(err)
    }

    // Write configuration file
    config := `
server:
  host: localhost
  port: 8080
`
    err = fsutil.WriteString("data/config.yml", config, 0644)
    if err != nil {
        panic(err)
    }

    // Write log file
    logMsg := "Application started\n"
    err = fsutil.WriteString("data/logs/app.log", logMsg, 0644)
    if err != nil {
        panic(err)
    }

    // Append to log
    fsutil.AppendString("data/logs/app.log", "Processing request\n", 0644)

    // Check files
    if fsutil.IsFile("data/config.yml") {
        fmt.Println("Config file exists")

        // Read it
        content, _ := fsutil.ReadString("data/config.yml")
        fmt.Println("Config:")
        fmt.Println(content)
    }

    // List log files
    logs, _ := fsutil.Glob("data/logs/*.log")
    fmt.Println("Log files:", logs)

    // Get file info
    size, _ := fsutil.FileSize("data/config.yml")
    fmt.Printf("Config size: %d bytes\n", size)

    // Cleanup (optional)
    // fsutil.RemoveAll("data")
}
```

---

## jsonutil - JSON Utilities

**Import**: `github.com/gookit/goutil/jsonutil`

JSON encoding, decoding, and manipulation utilities.

### JSON Encoding

```go
import "github.com/gookit/goutil/jsonutil"

// Encode to JSON string
data := map[string]any{"name": "John", "age": 30}
jsonStr, err := jsonutil.Encode(data)
// Result: {"name":"John","age":30}

// Encode with indentation
jsonStr, err := jsonutil.EncodePretty(data)
// Result: (formatted JSON with indentation)

// Must encode (panics on error)
jsonStr := jsonutil.MustString(data)
```

### JSON Decoding

```go
// Decode JSON string
jsonStr := `{"name":"John","age":30}`
var result map[string]any
err := jsonutil.Decode([]byte(jsonStr), &result)

// Decode from string
err := jsonutil.DecodeString(jsonStr, &result)

// Decode to specific type
type User struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}
var user User
err := jsonutil.DecodeString(jsonStr, &user)
```

### JSON File Operations

```go
// Read JSON from file
var config map[string]any
err := jsonutil.ReadFile("config.json", &config)

// Write JSON to file
data := map[string]any{"key": "value"}
err := jsonutil.WriteFile("config.json", data)

// Write pretty JSON
err := jsonutil.WritePretty("config.json", data)
```

### JSON Utilities

```go
// Check if valid JSON
if jsonutil.IsJSON(`{"key":"value"}`) {
    // Valid JSON
}

// Strip comments from JSON
jsonWithComments := `{
    // This is a comment
    "key": "value"
}`
clean := jsonutil.StripComments(jsonWithComments)
```

### Complete JSON Example

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/jsonutil"
    "github.com/gookit/goutil/fsutil"
)

type Config struct {
    Server   ServerConfig   `json:"server"`
    Database DatabaseConfig `json:"database"`
}

type ServerConfig struct {
    Host string `json:"host"`
    Port int    `json:"port"`
}

type DatabaseConfig struct {
    Driver string `json:"driver"`
    DSN    string `json:"dsn"`
}

func main() {
    // Create config
    config := Config{
        Server: ServerConfig{
            Host: "localhost",
            Port: 8080,
        },
        Database: DatabaseConfig{
            Driver: "postgres",
            DSN:    "user:pass@localhost/db",
        },
    }

    // Save to file
    err := jsonutil.WritePretty("config.json", config)
    if err != nil {
        panic(err)
    }

    fmt.Println("Config saved")

    // Read from file
    var loaded Config
    err = jsonutil.ReadFile("config.json", &loaded)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Loaded config: %+v\n", loaded)

    // Convert to JSON string
    jsonStr := jsonutil.MustString(loaded)
    fmt.Println("JSON:", jsonStr)

    // Cleanup
    fsutil.Remove("config.json")
}
```

---

## Import Quick Reference

```go
import (
    "github.com/gookit/goutil/cliutil"   // CLI utilities
    "github.com/gookit/goutil/sysutil"   // System utilities
    "github.com/gookit/goutil/envutil"   // Environment utilities
    "github.com/gookit/goutil/fsutil"    // Filesystem utilities
    "github.com/gookit/goutil/jsonutil"  // JSON utilities
)
```

---

**Related Documentation:**
- [Main Skill Documentation](SKILL.md)
- [Basic Packages](basic-packages.md)
- [Debug & Test Packages](debug-test-packages.md)
