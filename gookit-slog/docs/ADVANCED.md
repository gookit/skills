# Advanced Usage

Advanced features: custom formatters, processors, rotatefile package, and integration patterns.

## Custom Formatters

### Text Formatter

Customize text output with templates:

```go
f := slog.NewTextFormatter()

// Built-in templates
f.SetTemplate(slog.DefaultTemplate)
// [{{datetime}}] [{{channel}}] [{{level}}] [{{caller}}] {{message}} {{data}} {{extra}}\n

f.SetTemplate(slog.NamedTemplate)
// {{datetime}} channel={{channel}} level={{level}} [file={{caller}}] message={{message}} data={{data}}\n

// Custom template
f.SetTemplate("[{{level}}] {{message}}\n")

slog.SetFormatter(f)
```

**Template variables:**

- `{{datetime}}` - Timestamp
- `{{channel}}` - Logger name/channel
- `{{level}}` - Log level
- `{{caller}}` - File:line
- `{{message}}` - Log message
- `{{data}}` - Structured data fields
- `{{extra}}` - Extra fields from processors

**Template options:**

```go
f := slog.NewTextFormatter()
f.TimeFormat = "2006-01-02 15:04:05"  // Custom time format
f.EnableColor = true                  // Console colors
f.FullDisplay = true                  // Show all fields
```

### JSON Formatter

Customize JSON output:

```go
f := slog.NewJSONFormatter()

// Pretty print
f.PrettyPrint = true

// Custom time format
f.TimeFormat = time.RFC3339

// Filter fields
f.Fields = []string{"level", "message", "datetime"}

// Rename fields
f.Aliases = slog.StringMap{
    "level":    "severity",
    "message":  "msg",
    "datetime": "timestamp",
}

slog.SetFormatter(f)
```

**Output:**

```json
{
  "severity": "INFO",
  "msg": "user logged in",
  "timestamp": "2020-07-16T13:23:33Z"
}
```

### Custom Formatter

Implement `Formatter` interface:

```go
type MyFormatter struct {}

func (f *MyFormatter) Format(r *slog.Record) ([]byte, error) {
    // Custom formatting logic
    output := fmt.Sprintf("[%s] %s: %s\n",
        r.Level.String(),
        r.Time.Format("15:04:05"),
        r.Message,
    )
    return []byte(output), nil
}

// Usage
slog.SetFormatter(&MyFormatter{})
```

**Using FormatterFunc:**

```go
slog.SetFormatter(slog.FormatterFunc(func(r *slog.Record) ([]byte, error) {
    return []byte(r.Message + "\n"), nil
}))
```

## Processors

### Built-in Processors

**Add hostname:**

```go
slog.AddProcessor(slog.AddHostname())
// Adds: "hostname":"MyServer"
```

**Custom processor:**

```go
slog.AddProcessor(slog.ProcessorFunc(func(r *slog.Record) {
    r.Extra["app"] = "myapp"
    r.Extra["version"] = "1.0.0"
    r.Extra["pid"] = os.Getpid()
}))
```

### Request Context Processor

Add request ID, user info to logs:

```go
type RequestProcessor struct {
    RequestID string
    UserID    int
}

func (p *RequestProcessor) Process(r *slog.Record) {
    r.Extra["request_id"] = p.RequestID
    r.Extra["user_id"] = p.UserID
}

// In HTTP handler
func handleRequest(w http.ResponseWriter, r *http.Request) {
    requestID := r.Header.Get("X-Request-ID")
    userID := getUserID(r)

    logger := slog.New()
    logger.AddProcessor(&RequestProcessor{
        RequestID: requestID,
        UserID:    userID,
    })

    logger.Info("processing request")
}
```

### Context-based Processor

Extract values from context:

```go
type ContextProcessor struct {
    ctx context.Context
}

func (p *ContextProcessor) Process(r *slog.Record) {
    if reqID, ok := p.ctx.Value("request_id").(string); ok {
        r.Extra["request_id"] = reqID
    }
    if userID, ok := p.ctx.Value("user_id").(int); ok {
        r.Extra["user_id"] = userID
    }
}

// Usage
ctx := context.WithValue(context.Background(), "request_id", "abc123")
logger := slog.New()
logger.AddProcessor(&ContextProcessor{ctx: ctx})
```

## rotatefile Package

Standalone file rotation utility.

### Basic Usage

```go
import "github.com/gookit/slog/rotatefile"

writer, err := rotatefile.NewConfig("app.log").Create()
if err != nil {
    panic(err)
}
defer writer.Close()

writer.Write([]byte("log message\n"))
```

### Configuration

```go
cfg := rotatefile.Config{
    Filepath:   "app.log",
    MaxSize:    20 * 1024 * 1024,  // 20MB
    RotateTime: rotatefile.EveryHour,
    BackupNum:  10,
    BackupTime: 168,  // 7 days in hours
    Compress:   true,
}

writer, err := cfg.Create()
```

### With Other Loggers

**Standard log package:**

```go
import (
    "log"
    "github.com/gookit/slog/rotatefile"
)

writer, _ := rotatefile.NewConfig("app.log").Create()
log.SetOutput(writer)
log.Println("message")
```

**Zap:**

```go
import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
    "github.com/gookit/slog/rotatefile"
)

writer, _ := rotatefile.NewConfig("app.log").Create()

core := zapcore.NewCore(
    zapcore.NewJSONEncoder(zap.NewProductionEncoderConfig()),
    zapcore.AddSync(writer),
    zapcore.InfoLevel,
)

logger := zap.New(core)
logger.Info("message")
```

**Logrus:**

```go
import (
    "github.com/sirupsen/logrus"
    "github.com/gookit/slog/rotatefile"
)

writer, _ := rotatefile.NewConfig("app.log").Create()
logrus.SetOutput(writer)
logrus.Info("message")
```

### File Cleanup

Clean old log files independently:

```go
import "github.com/gookit/slog/rotatefile"

cleaner := rotatefile.FilesClear{
    Dir:        "/var/log",
    Pattern:    "app.log.*",
    BackupNum:  10,
    BackupTime: 168,  // 7 days
    Compress:   true,
}

removed, err := cleaner.Clean()
fmt.Printf("Removed %d files\n", removed)
```

**Scheduled cleanup:**

```go
import "time"

go func() {
    ticker := time.NewTicker(24 * time.Hour)
    defer ticker.Stop()

    for range ticker.C {
        cleaner.Clean()
    }
}()
```

## Integration Patterns

### Web Framework Integration

**Gin:**

```go
import (
    "github.com/gin-gonic/gin"
    "github.com/gookit/slog"
)

func LoggerMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        c.Next()

        duration := time.Since(start)
        status := c.Writer.Status()

        logger := slog.WithFields(slog.M{
            "method":   c.Request.Method,
            "path":     c.Request.URL.Path,
            "status":   status,
            "duration": duration.Milliseconds(),
            "ip":       c.ClientIP(),
        })

        if status >= 500 {
            logger.Error("server error")
        } else if status >= 400 {
            logger.Warn("client error")
        } else {
            logger.Info("request completed")
        }
    }
}

func main() {
    r := gin.New()
    r.Use(LoggerMiddleware())
    r.Run()
}
```

**Echo:**

```go
import (
    "github.com/labstack/echo/v4"
    "github.com/gookit/slog"
)

func LoggerMiddleware() echo.MiddlewareFunc {
    return func(next echo.HandlerFunc) echo.HandlerFunc {
        return func(c echo.Context) error {
            start := time.Now()

            err := next(c)

            slog.WithFields(slog.M{
                "method":   c.Request().Method,
                "path":     c.Request().URL.Path,
                "status":   c.Response().Status,
                "duration": time.Since(start).Milliseconds(),
            }).Info("request")

            return err
        }
    }
}
```

### GORM Integration

Use slog as GORM logger:

```go
import (
    "gorm.io/gorm"
    "gorm.io/gorm/logger"
    "github.com/gookit/slog"
)

type GormLogger struct {
    logger *slog.Logger
}

func (l *GormLogger) LogMode(level logger.LogLevel) logger.Interface {
    return l
}

func (l *GormLogger) Info(ctx context.Context, msg string, data ...interface{}) {
    l.logger.Infof(msg, data...)
}

func (l *GormLogger) Warn(ctx context.Context, msg string, data ...interface{}) {
    l.logger.Warnf(msg, data...)
}

func (l *GormLogger) Error(ctx context.Context, msg string, data ...interface{}) {
    l.logger.Errorf(msg, data...)
}

func (l *GormLogger) Trace(ctx context.Context, begin time.Time, fc func() (string, int64), err error) {
    elapsed := time.Since(begin)
    sql, rows := fc()

    fields := slog.M{
        "elapsed": elapsed.Milliseconds(),
        "rows":    rows,
        "sql":     sql,
    }

    if err != nil {
        l.logger.WithFields(fields).Error(err.Error())
    } else {
        l.logger.WithFields(fields).Debug("query executed")
    }
}

// Usage
db, _ := gorm.Open(sqlite.Open("test.db"), &gorm.Config{
    Logger: &GormLogger{logger: slog.New()},
})
```

### Graceful Shutdown

Ensure logs are flushed before exit:

```go
import (
    "os"
    "os/signal"
    "syscall"
)

func main() {
    setupLogging()

    // Setup signal handling
    sigChan := make(chan os.Signal, 1)
    signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

    go func() {
        <-sigChan
        slog.Info("shutting down...")
        slog.MustClose()  // Flush and close handlers
        os.Exit(0)
    }()

    // Application code
    runApp()
}
```

## Buffer Writers

### BufIOWriter

Enhanced bufio.Writer with Sync and Close:

```go
import "github.com/gookit/slog/bufwrite"

writer := bufwrite.NewBufIOWriter(file, 8*1024)
writer.Write([]byte("data"))
writer.Flush()
writer.Close()
```

### LineWriter

Flush buffer on complete lines:

```go
writer := bufwrite.NewLineWriter(file, 8*1024)
writer.Write([]byte("line1\nline2\npartial"))
writer.Flush() // Ensures partial lines stay in buffer
```

## Testing

Mock logger for unit tests:

```go
import (
    "bytes"
    "testing"
)

func TestMyFunction(t *testing.T) {
    // Capture logs
    buf := new(bytes.Buffer)
    h := handler.NewSimpleHandler(buf, slog.AllLevels)

    logger := slog.NewWithHandlers(h)

    // Test code
    myFunction(logger)

    // Check logs
    logs := buf.String()
    if !strings.Contains(logs, "expected message") {
        t.Error("expected log message not found")
    }
}
```
