# Handlers Guide

Complete reference for all built-in handlers and their configuration.

## Handler Types

### ConsoleHandler

Output logs to console with optional color support.

```go
import "github.com/gookit/slog/handler"

// Handle all levels
h := handler.NewConsoleHandler(slog.AllLevels)

// Handle specific levels
h := handler.NewConsoleHandler([]slog.Level{
    slog.InfoLevel,
    slog.WarnLevel,
    slog.ErrorLevel,
})

slog.AddHandlers(h)
```

**Enable color:**

```go
h := handler.NewConsoleHandler(slog.AllLevels)
h.Formatter().(*slog.TextFormatter).EnableColor = true
```

### FileHandler

Write logs to a single file without buffering.

```go
// Basic usage
h, err := handler.NewFileHandler("/var/log/app.log")

// With options
h, err := handler.NewFileHandler(
    "/var/log/app.log",
    handler.WithLogLevels(slog.AllLevels),
    handler.WithUseJSON(true), // Use JSON format
)

slog.AddHandlers(h)
defer slog.MustClose()
```

### BuffFileHandler

Write logs with buffer for better performance.

```go
// 8KB buffer
h, err := handler.NewBuffFileHandler(
    "/var/log/app.log",
    1024*8,
    handler.WithLogLevels(slog.AllLevels),
)

slog.AddHandlers(h)
defer slog.MustClose() // Important: flush buffer
```

**Buffer modes:**

```go
// Byte buffer (default)
handler.WithBuffMode("bite")

// Line buffer (flush on complete line)
handler.WithBuffMode("line")
```

### RotateFileHandler

Automatically rotate log files by time and/or size.

```go
h, err := handler.NewRotateFileHandler(
    "/var/log/app.log",
    rotatefile.EveryHour, // Rotate time
    handler.WithMaxSize(20*1024*1024),  // 20MB
    handler.WithBackupNum(10),          // Keep 10 old files
    handler.WithBackupTime(168),        // Keep files for 7 days
    handler.WithCompress(true),         // Gzip old files
)

slog.AddHandlers(h)
defer slog.MustClose()
```

**Rotate times:**

```go
rotatefile.EveryDay      // Daily at midnight
rotatefile.EveryHour     // Every hour
rotatefile.Every30Min    // Every 30 minutes
rotatefile.Every15Min    // Every 15 minutes
rotatefile.EveryMinute   // Every minute
rotatefile.EverySecond   // Every second (for testing)
```

**Rotate by size only:**

```go
h, err := handler.NewSizeRotateFile(
    "/var/log/app.log",
    20*1024*1024, // 20MB
    handler.WithBackupNum(10),
)
```

**Rotate by time only:**

```go
h, err := handler.NewTimeRotateFile(
    "/var/log/app.log",
    rotatefile.EveryDay,
    handler.WithBackupNum(30), // Keep 30 days
)
```

**Rotated file names:**

```text
app.log                    # Current file
app.log.20260128_140000    # Rotated by time
app.log.140530_0001        # Rotated by size (1st)
app.log.140530_0002        # Rotated by size (2nd)
app.log.20260128_140000.gz # Compressed
```

### SimpleHandler

Simple output to io.Writer.

```go
import "os"

h := handler.NewSimpleHandler(os.Stdout, slog.InfoLevel)
slog.AddHandlers(h)
```

### EmailHandler

Send logs via email (for critical errors).

```go
from := handler.EmailOption{
    Address:  "alerts@example.com",
    Host:     "smtp.example.com",
    Port:     587,
    Username: "alerts@example.com",
    Password: "password",
}

to := []string{"admin@example.com", "dev@example.com"}

h := handler.NewEmailHandler(from, to)
h.SetLevels([]slog.Level{slog.ErrorLevel, slog.FatalLevel})

slog.AddHandlers(h)
```

### SysLogHandler

Send logs to system syslog.

```go
import "log/syslog"

h, err := handler.NewSysLogHandler(
    syslog.LOG_ERR|syslog.LOG_LOCAL0,
    "myapp",
)

slog.AddHandlers(h)
```

## Configuration

### Using Config

Build handler from configuration:

```go
cfg := handler.Config{
    Logfile:    "/var/log/app.log",
    LevelMode:  handler.LevelModeList,
    Levels:     slog.AllLevels,
    UseJSON:    false,
    BuffSize:   1024 * 8,
    RotateTime: rotatefile.EveryHour,
    MaxSize:    20 * 1024 * 1024,
    Compress:   true,
    BackupNum:  10,
    BackupTime: 168,
}

h := cfg.CreateHandler()
slog.AddHandlers(h)
```

**Config from YAML:**

```yaml
# config.yaml
log:
  logfile: /var/log/app.log
  level_mode: 1
  levels: [100, 200, 300, 400, 500]
  use_json: false
  buff_size: 8192
  rotate_time: 3600  # 1 hour in seconds
  max_size: 20971520 # 20MB
  compress: true
  backup_num: 10
  backup_time: 168   # 7 days in hours
```

### Using Builder

Fluent API to build handlers:

```go
h := handler.NewBuilder().
    WithLogfile("/var/log/app.log").
    WithLogLevels(slog.AllLevels).
    WithBuffSize(1024*8).
    WithRotateTime(rotatefile.EveryHour).
    WithMaxSize(20*1024*1024).
    WithCompress(true).
    WithBackupNum(10).
    WithBackupTime(168).
    Build()

slog.AddHandlers(h)
```

### Common Options

Available for most file-based handlers:

```go
// Log levels to handle
handler.WithLogLevels(slog.DangerLevels)

// Use JSON format
handler.WithUseJSON(true)

// Buffer size (0 to disable)
handler.WithBuffSize(1024*8)

// Buffer mode
handler.WithBuffMode("line")

// Rotate time
handler.WithRotateTime(rotatefile.EveryHour)

// Max file size
handler.WithMaxSize(20*1024*1024)

// Compress old files
handler.WithCompress(true)

// Number of backups to keep
handler.WithBackupNum(10)

// Time to keep backups (hours)
handler.WithBackupTime(168)

// Custom filename for rotated files
handler.WithRenameFunc(func(filepath string, rotateNum uint) string {
    return filepath + ".old"
})
```

## Level Groups

Predefined level groups for convenience:

```go
slog.AllLevels      // All 8 levels
slog.DangerLevels   // panic, fatal, error, warn
slog.NormalLevels   // info, notice, debug, trace
slog.InfoLevel      // Single level
```

**Custom level filter:**

```go
levels := []slog.Level{
    slog.ErrorLevel,
    slog.WarnLevel,
    slog.InfoLevel,
}

h := handler.NewConsoleHandler(levels)
```

## Multiple Handlers Example

Separate error and info logs:

```go
func setupLogging() {
    // Errors to error.log
    errorFile := handler.MustRotateFile(
        "/var/log/error.log",
        rotatefile.EveryDay,
        handler.WithLogLevels(slog.DangerLevels),
        handler.WithCompress(true),
    )

    // Info to info.log
    infoFile := handler.MustRotateFile(
        "/var/log/info.log",
        rotatefile.EveryDay,
        handler.WithLogLevels(slog.NormalLevels),
        handler.WithCompress(true),
    )

    // All to console (dev only)
    if os.Getenv("ENV") == "development" {
        console := handler.NewConsoleHandler(slog.AllLevels)
        slog.PushHandlers(errorFile, infoFile, console)
    } else {
        slog.PushHandlers(errorFile, infoFile)
    }
}

func main() {
    setupLogging()
    defer slog.MustClose()

    slog.Info("app started")
    slog.Error("something went wrong")
}
```

## Custom Handler

Create your own handler:

```go
import "io"

type MyHandler struct {
    handler.LevelsWithFormatter
    output io.Writer
}

func (h *MyHandler) Handle(r *slog.Record) error {
    bts, err := h.Formatter().Format(r)
    if err != nil {
        return err
    }

    _, err = h.output.Write(bts)
    return err
}

func (h *MyHandler) Flush() error {
    if f, ok := h.output.(interface{ Flush() error }); ok {
        return f.Flush()
    }
    return nil
}

func (h *MyHandler) Close() error {
    if c, ok := h.output.(io.Closer); ok {
        return c.Close()
    }
    return nil
}

// Usage
h := &MyHandler{
    LevelsWithFormatter: handler.LevelsWithFormatter{
        Levels:    slog.AllLevels,
        Formatter: slog.NewJSONFormatter(),
    },
    output: os.Stdout,
}

slog.AddHandlers(h)
```

## Handler Tips

1. **Always close**: Use `defer slog.MustClose()` with buffered/file handlers
2. **Buffer size**: 8-16KB works well for most cases
3. **Rotate settings**: Balance between file size and rotation frequency
4. **Compression**: Enable for production to save disk space
5. **Backup limits**: Set both `BackupNum` and `BackupTime` to prevent disk fill
6. **Level separation**: Use different handlers for different severity levels
