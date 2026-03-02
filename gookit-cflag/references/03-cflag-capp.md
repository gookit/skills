# cflag 多命令 CLI 应用

使用 `cflag/capp` 方便快速的创建多命令 CLI 应用.

应用结构参考：

```txt
your-app/
├── cmd/your-app/main.go
├── internal/
│   ├── cli/
│   │   ├── cli.go
│   │   ├── getip_cmd.go
│   │   └── ... more commands
```

### 应用入口

```go cmd/your-app/main.go
package main

import (
    "your-app/internal/cli"
)

var (
    Version   = "develop"
    CommitID  = "unknown"
    BuildDate = ""
)

func main() {
    cli.Run(Version, BuildDate, CommitID)
}
```

### CLI 注册

```go your-app/internal/cli/cli.go
package cli

import (
    "your-app/internal/config"

    "github.com/gookit/goutil/cflag/capp"
	"github.com/gookit/goutil/strutil"
    "github.com/gookit/goutil/x/ccolor"
)

func Run(version, buildDate, commitID string) {
    if buildDate == "" {
        buildDate = time.Now().Format("2006-01-02 15:04:05")
    }

    app := capp.NewApp()
    app.Name = "your-app"
    app.Desc = fmt.Sprintf("remote init a edge linux device\n build: %s, hash: %s", buildDate, strutil.Substr(commitID, 0, 8))
    app.Version = version

	// 每个命令运行都会执行此方法
    app.BeforeRun = beforeRun

	configApp(app)
    addCommands(app)
    app.Run()
}

var (
	configPath string
	logLevel   string
)

func configApp(app *capp.App) {
	app.StringVar(&configPath, "config", "config.yaml", "配置文件路径")
	app.StringVar(&logLevel, "log-level", "info", "日志级别 (debug, info, warn, error)")
}

func addCommands(app *capp.App) {
    app.Add(newGetIPCmd(), newInitCmd(), newAddDhcpCmd())
}

func beforeRun(c *capp.Cmd, args []string) bool {
	// eg: 公共的初始化逻辑
	if err := bootstrap(); err != nil {
		ccolor.Errorf("初始化失败: %s\n", err)
		return false
	}
	return true
}

func bootstrap() error {
    if err := config.Init(configPath); err != nil {
        return err
    }
    return nil
}
```

### 定义命令

```go your-app/internal/cli/getip_cmd.go
package cli

type GetIPOptions struct {
    Hostname    string
    RouterURL   string
    SesskeyFile string
}

func newGetIPCmd() *capp.Cmd {
    opts := &GetIPOptions{}
    c := capp.NewCmd("get-ip", "discover new device IP from router", func(c *capp.Cmd) error {
        return runGetIP(opts)
    })

    c.StringVar(&opts.Hostname, "hostname", "", "device hostname filter")
    c.StringVar(&opts.RouterURL, "router-url", "http://172.20.0.1", "router management addr")
    c.StringVar(&opts.SesskeyFile, "sesskey-file", ".ikuai.sesskey", "login sesskey file path")

    return c
}

func runGetIP(opts *GetIPOptions) error {
    // 处理逻辑
}
```

## 最佳实践

### 1. 提供短选项和长选项

```go
// 推荐：同时提供短选项和长选项
c.StrVar(&name, "name", "n", "", "User name")

// 可接受：不常用标志只提供长选项
c.BoolVar(&debug, "debug", "", false, "Debug mode")
```

### 2. 使用合理的默认值

```go
// 推荐：提供有用的默认值
c.IntVar(&port, "port", "p", 8080, "Server port")
c.StrVar(&config, "config", "c", "config.yml", "Config file")
```

### 3. 添加清晰的描述

```go
// 推荐：清晰简洁
c.StrVar(&host, "host", "h", "localhost", "Server host address")

// 避免：过于模糊
c.StrVar(&host, "host", "h", "localhost", "Host")
```

### 4. 验证输入

```go
// 使用验证器设置约束
portVar := cflag.NewIntVar(cflag.LimitInt(1024, 65535))
c.Var(portVar, "port", "p", "Server port (1024-65535)")

// 使用枚举限制选项
level := cflag.NewEnumString("debug", "info", "warn", "error")
c.Var(level, "level", "l", "Log level")
```

### 5. 优雅处理错误

```go
if err := c.Parse(); err != nil {
    fmt.Fprintf(os.Stderr, "Error: %v\n", err)
    c.PrintHelp()
    os.Exit(1)
}
```
