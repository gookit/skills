# Practical Examples

Real-world usage examples for common scenarios.

## Web Application Logging

### Complete Setup

```go
package main

import (
    "github.com/gookit/slog"
    "github.com/gookit/slog/handler"
    "github.com/gookit/slog/rotatefile"
)

func setupLogging() {
    // Error logs: separate file, rotate daily
    errorLog := handler.MustRotateFile(
        "/var/log/myapp/error.log",
        rotatefile.EveryDay,
        handler.WithLogLevels(slog.DangerLevels),
        handler.WithMaxSize(50*1024*1024), // 50MB
        handler.WithBackupNum(30),         // 30 days
        handler.WithCompress(true),
    )

    // Info logs: separate file, rotate every hour
    infoLog := handler.MustRotateFile(
        "/var/log/myapp/info.log",
        rotatefile.EveryHour,
        handler.WithLogLevels(slog.NormalLevels),
        handler.WithMaxSize(100*1024*1024),
        handler.WithBackupNum(72),  // 3 days of hourly logs
        handler.WithCompress(true),
    )

    // Console output in development
    if isDevelopment() {
        console := handler.NewConsoleHandler(slog.AllLevels)
        console.Formatter().(*slog.TextFormatter).EnableColor = true
        slog.PushHandlers(errorLog, infoLog, console)
    } else {
        slog.PushHandlers(errorLog, infoLog)
    }

    // Add processors
    slog.AddProcessor(slog.AddHostname())
    slog.AddProcessor(slog.ProcessorFunc(func(r *slog.Record) {
        r.Extra["app"] = "myapp"
        r.Extra["version"] = Version
    }))
}

func main() {
    setupLogging()
    defer slog.MustClose()

    slog.Info("application started")
    // ... application code
}
```

### HTTP Request Logging

```go
type HTTPLogger struct {
    logger *slog.Logger
}

func NewHTTPLogger() *HTTPLogger {
    return &HTTPLogger{
        logger: slog.New(),
    }
}

func (l *HTTPLogger) LogRequest(r *http.Request, status int, duration time.Duration) {
    fields := slog.M{
        "method":     r.Method,
        "path":       r.URL.Path,
        "query":      r.URL.RawQuery,
        "status":     status,
        "duration":   duration.Milliseconds(),
        "ip":         r.RemoteAddr,
        "user_agent": r.UserAgent(),
        "referer":    r.Referer(),
    }

    logger := l.logger.WithFields(fields)

    switch {
    case status >= 500:
        logger.Error("server error")
    case status >= 400:
        logger.Warn("client error")
    case status >= 300:
        logger.Info("redirect")
    default:
        logger.Info("success")
    }
}

// Usage in middleware
func LoggingMiddleware(next http.Handler) http.Handler {
    httpLogger := NewHTTPLogger()

    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()

        // Wrap response writer to capture status
        wrapped := &responseWriter{ResponseWriter: w, status: 200}

        next.ServeHTTP(wrapped, r)

        httpLogger.LogRequest(r, wrapped.status, time.Since(start))
    })
}

type responseWriter struct {
    http.ResponseWriter
    status int
}

func (w *responseWriter) WriteHeader(status int) {
    w.status = status
    w.ResponseWriter.WriteHeader(status)
}
```

## Microservice Logging

### Service Logger

```go
package service

import "github.com/gookit/slog"

type UserService struct {
    logger *slog.Logger
}

func NewUserService() *UserService {
    return &UserService{
        logger: slog.NewWithName("user-service"),
    }
}

func (s *UserService) CreateUser(user *User) error {
    logger := s.logger.WithFields(slog.M{
        "user_id": user.ID,
        "email":   user.Email,
    })

    logger.Info("creating user")

    if err := s.validateUser(user); err != nil {
        logger.WithData(slog.M{"error": err.Error()}).
            Warn("user validation failed")
        return err
    }

    if err := s.saveUser(user); err != nil {
        logger.WithData(slog.M{"error": err.Error()}).
            Error("failed to save user")
        return err
    }

    logger.Info("user created successfully")
    return nil
}
```

### Distributed Tracing

```go
import (
    "context"
    "github.com/gookit/slog"
)

type TraceLogger struct {
    logger  *slog.Logger
    traceID string
    spanID  string
}

func NewTraceLogger(ctx context.Context) *TraceLogger {
    traceID := getTraceID(ctx)
    spanID := getSpanID(ctx)

    logger := slog.New()
    logger.AddProcessor(slog.ProcessorFunc(func(r *slog.Record) {
        r.Extra["trace_id"] = traceID
        r.Extra["span_id"] = spanID
    }))

    return &TraceLogger{
        logger:  logger,
        traceID: traceID,
        spanID:  spanID,
    }
}

func (l *TraceLogger) Info(msg string, fields ...slog.M) {
    if len(fields) > 0 {
        l.logger.WithFields(fields[0]).Info(msg)
    } else {
        l.logger.Info(msg)
    }
}

// Usage in service
func ProcessOrder(ctx context.Context, orderID string) error {
    logger := NewTraceLogger(ctx)

    logger.Info("processing order", slog.M{"order_id": orderID})

    // ... business logic

    logger.Info("order processed successfully")
    return nil
}
```

## Background Jobs

### Job Logger

```go
type JobLogger struct {
    jobID  string
    logger *slog.Logger
}

func NewJobLogger(jobID, jobType string) *JobLogger {
    logger := slog.New()
    logger.AddProcessor(slog.ProcessorFunc(func(r *slog.Record) {
        r.Extra["job_id"] = jobID
        r.Extra["job_type"] = jobType
        r.Extra["worker"] = getWorkerID()
    }))

    return &JobLogger{
        jobID:  jobID,
        logger: logger,
    }
}

func (j *JobLogger) LogStart() {
    j.logger.Info("job started")
}

func (j *JobLogger) LogProgress(progress int, total int) {
    j.logger.WithData(slog.M{
        "progress": progress,
        "total":    total,
        "percent":  float64(progress) / float64(total) * 100,
    }).Info("job progress")
}

func (j *JobLogger) LogComplete(duration time.Duration) {
    j.logger.WithData(slog.M{
        "duration": duration.Milliseconds(),
    }).Info("job completed")
}

func (j *JobLogger) LogError(err error) {
    j.logger.WithData(slog.M{
        "error": err.Error(),
    }).Error("job failed")
}

// Usage
func ProcessImportJob(jobID string, file string) {
    logger := NewJobLogger(jobID, "import")

    logger.LogStart()

    items, err := loadFile(file)
    if err != nil {
        logger.LogError(err)
        return
    }

    start := time.Now()
    for i, item := range items {
        processItem(item)
        if i%100 == 0 {
            logger.LogProgress(i, len(items))
        }
    }

    logger.LogComplete(time.Since(start))
}
```

## Database Operations

### Query Logging

```go
type QueryLogger struct {
    logger *slog.Logger
}

func NewQueryLogger() *QueryLogger {
    return &QueryLogger{
        logger: slog.NewWithName("database"),
    }
}

func (q *QueryLogger) LogQuery(query string, args []interface{}, duration time.Duration, err error) {
    fields := slog.M{
        "query":    query,
        "args":     args,
        "duration": duration.Milliseconds(),
    }

    if err != nil {
        q.logger.WithFields(fields).WithData(slog.M{
            "error": err.Error(),
        }).Error("query failed")
    } else if duration > 100*time.Millisecond {
        q.logger.WithFields(fields).Warn("slow query")
    } else {
        q.logger.WithFields(fields).Debug("query executed")
    }
}

// Usage with database wrapper
type DB struct {
    *sql.DB
    logger *QueryLogger
}

func (db *DB) Query(query string, args ...interface{}) (*sql.Rows, error) {
    start := time.Now()
    rows, err := db.DB.Query(query, args...)
    duration := time.Since(start)

    db.logger.LogQuery(query, args, duration, err)

    return rows, err
}
```

## Error Tracking

### Error Logger with Stack Trace

```go
import (
    "fmt"
    "runtime/debug"
)

type ErrorLogger struct {
    logger *slog.Logger
}

func NewErrorLogger() *ErrorLogger {
    return &ErrorLogger{
        logger: slog.New(),
    }
}

func (e *ErrorLogger) LogError(err error, context map[string]interface{}) {
    fields := slog.M{
        "error":      err.Error(),
        "stacktrace": string(debug.Stack()),
    }

    for k, v := range context {
        fields[k] = v
    }

    e.logger.WithFields(fields).Error("error occurred")
}

func (e *ErrorLogger) LogPanic(recovered interface{}) {
    e.logger.WithFields(slog.M{
        "panic":      fmt.Sprintf("%v", recovered),
        "stacktrace": string(debug.Stack()),
    }).Fatal("panic recovered")
}

// Usage with panic recovery
func HandleRequest(w http.ResponseWriter, r *http.Request) {
    errorLogger := NewErrorLogger()

    defer func() {
        if r := recover(); r != nil {
            errorLogger.LogPanic(r)
            http.Error(w, "Internal Server Error", 500)
        }
    }()

    // Request handling
    if err := processRequest(r); err != nil {
        errorLogger.LogError(err, map[string]interface{}{
            "path":   r.URL.Path,
            "method": r.Method,
        })
        http.Error(w, "Error", 500)
        return
    }

    w.Write([]byte("OK"))
}
```

## Structured Logging Patterns

### Context-Rich Logging

```go
type AppLogger struct {
    logger *slog.Logger
    ctx    map[string]interface{}
}

func NewAppLogger() *AppLogger {
    return &AppLogger{
        logger: slog.New(),
        ctx:    make(map[string]interface{}),
    }
}

func (a *AppLogger) WithContext(key string, value interface{}) *AppLogger {
    newCtx := make(map[string]interface{})
    for k, v := range a.ctx {
        newCtx[k] = v
    }
    newCtx[key] = value

    return &AppLogger{
        logger: a.logger,
        ctx:    newCtx,
    }
}

func (a *AppLogger) Info(msg string, fields ...map[string]interface{}) {
    merged := make(slog.M)
    for k, v := range a.ctx {
        merged[k] = v
    }
    if len(fields) > 0 {
        for k, v := range fields[0] {
            merged[k] = v
        }
    }

    a.logger.WithFields(merged).Info(msg)
}

// Usage
logger := NewAppLogger().
    WithContext("env", "production").
    WithContext("region", "us-east-1")

logger.Info("service started")

requestLogger := logger.WithContext("request_id", "abc123")
requestLogger.Info("processing request", map[string]interface{}{
    "user_id": 456,
})
```

## Performance Monitoring

### Timing Logger

```go
type Timer struct {
    logger *slog.Logger
    start  time.Time
    fields slog.M
}

func StartTimer(operation string) *Timer {
    return &Timer{
        logger: slog.New(),
        start:  time.Now(),
        fields: slog.M{"operation": operation},
    }
}

func (t *Timer) AddField(key string, value interface{}) *Timer {
    t.fields[key] = value
    return t
}

func (t *Timer) End() {
    duration := time.Since(t.start)
    t.fields["duration"] = duration.Milliseconds()

    logger := t.logger.WithFields(t.fields)

    if duration > time.Second {
        logger.Warn("operation took too long")
    } else {
        logger.Info("operation completed")
    }
}

// Usage
func ProcessData(data []byte) {
    timer := StartTimer("process_data").
        AddField("size", len(data))
    defer timer.End()

    // Processing logic
    time.Sleep(100 * time.Millisecond)
}
```

## Configuration from YAML

```go
import (
    "gopkg.in/yaml.v2"
    "io/ioutil"
)

type LogConfig struct {
    Level   string         `yaml:"level"`
    Handlers []HandlerConfig `yaml:"handlers"`
}

type HandlerConfig struct {
    Type       string `yaml:"type"`
    File       string `yaml:"file"`
    MaxSize    int    `yaml:"max_size"`
    RotateTime string `yaml:"rotate_time"`
    Compress   bool   `yaml:"compress"`
    BackupNum  int    `yaml:"backup_num"`
}

func LoadConfig(filename string) (*LogConfig, error) {
    data, err := ioutil.ReadFile(filename)
    if err != nil {
        return nil, err
    }

    var config LogConfig
    if err := yaml.Unmarshal(data, &config); err != nil {
        return nil, err
    }

    return &config, nil
}

func SetupFromConfig(configFile string) error {
    config, err := LoadConfig(configFile)
    if err != nil {
        return err
    }

    // Set log level
    level := slog.LevelByName(config.Level)
    slog.SetLogLevel(level)

    // Setup handlers
    for _, hc := range config.Handlers {
        var h slog.Handler
        var err error

        switch hc.Type {
        case "rotate_file":
            rotateTime := parseRotateTime(hc.RotateTime)
            h, err = handler.NewRotateFileHandler(
                hc.File,
                rotateTime,
                handler.WithMaxSize(uint64(hc.MaxSize)),
                handler.WithCompress(hc.Compress),
                handler.WithBackupNum(uint(hc.BackupNum)),
            )
        case "file":
            h, err = handler.NewFileHandler(hc.File)
        case "console":
            h = handler.NewConsoleHandler(slog.AllLevels)
        }

        if err != nil {
            return err
        }

        slog.AddHandlers(h)
    }

    return nil
}

// logging.yaml
/*
level: info
handlers:
  - type: rotate_file
    file: /var/log/app/app.log
    max_size: 20971520
    rotate_time: 1h
    compress: true
    backup_num: 10
  - type: console
*/
```
