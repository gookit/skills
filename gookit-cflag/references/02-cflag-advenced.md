# cflag 进阶用法


## 高级特性

### 枚举标志

限制标志值为特定选项：

```go
var logLevel string

// 创建枚举并指定允许的值
enumLevel := cflag.NewEnumString("debug", "info", "warn", "error")
c.Var(enumLevel, "level", "l", "Log level")

c.MustParse()
logLevel = enumLevel.String()
```

### 键值对标志

解析 key=value 键值对：

```go
// 创建键值对标志
kvFlag := cflag.NewKVString()
c.Var(kvFlag, "env", "e", "Environment variables")

// 用法: --env key1=value1 --env key2=value2
c.MustParse()

// 获取值
value := kvFlag.Get("key1")
allValues := kvFlag.Values()
```

### 自定义验证器

```go
// 带验证的整数
var port int
portVar := cflag.NewIntVar(cflag.LimitInt(1024, 65535))
c.Var(portVar, "port", "p", "Server port (1024-65535)")

c.MustParse()
port = portVar.Int()
```

### 必需参数

```go
// 定义必需参数
arg := cflag.NewArg("filename", "Input file", true)  // true = required
c.AddArg(arg)

c.MustParse()

// 获取参数值
filename := c.Arg(0)
```

## 验证

### 内置验证器

```go
// 整数范围验证
portVar := cflag.NewIntVar(cflag.LimitInt(1024, 65535))
c.Var(portVar, "port", "p", "Server port")

// 自定义函数验证
validator := func(val string) error {
    if len(val) < 3 {
        return errors.New("name must be at least 3 characters")
    }
    return nil
}
nameVar := cflag.NewStrVar(validator)
c.Var(nameVar, "name", "n", "User name")
```

### 自定义验证器类型

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

// 使用自定义验证器
emailVar := &EmailValidator{}
c.Var(emailVar, "email", "e", "Email address")
```

## 完整示例

### 高级 CLI 应用

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

    c.StrVar(&host, "host", "h", "localhost", "Server host")

    // 带验证的端口
    portVar := cflag.NewIntVar(cflag.LimitInt(1024, 65535))
    c.Var(portVar, "port", "p", "Server port (1024-65535)")

    // 枚举类型
    enumLevel := cflag.NewEnumString("debug", "info", "warn", "error")
    c.Var(enumLevel, "level", "l", "Log level")

    // 键值对
    envVars = cflag.NewKVString()
    c.Var(envVars, "env", "e", "Environment variables")

    if err := c.Parse(); err != nil {
        fmt.Println("Error:", err)
        c.PrintHelp()
        os.Exit(1)
    }

    port = portVar.Int()
    logLevel = enumLevel.String()

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

**用法：**
```bash
./server --port 8080 --level info --env DB_HOST=localhost --env DB_PORT=5432
./server -p 8080 -l info -e DB_HOST=localhost -e DB_PORT=5432
```

### 带必需参数的 CLI

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

    c.StrVar(&output, "output", "o", "output.txt", "Output file")

    formatEnum := cflag.NewEnumString("json", "xml", "yaml")
    c.Var(formatEnum, "format", "f", "Output format")

    c.BoolVar(&verbose, "verbose", "v", false, "Verbose output")

    // 必需参数
    inputArg := cflag.NewArg("input", "Input file", true)
    c.AddArg(inputArg)

    c.MustParse()

    inputFile := c.Arg(0)
    if inputFile == "" {
        fmt.Println("Error: input file is required")
        c.PrintHelp()
        os.Exit(1)
    }

    format = formatEnum.String()

    if !fsutil.FileExists(inputFile) {
        fmt.Printf("Error: file not found: %s\n", inputFile)
        os.Exit(1)
    }

    if verbose {
        fmt.Printf("Processing %s...\n", inputFile)
        fmt.Printf("Format: %s\n", format)
        fmt.Printf("Output: %s\n", output)
    }

    fmt.Println("Done!")
}
```

**用法：**
```bash
./fileproc input.txt --output result.json --format json --verbose
./fileproc input.txt -o result.json -f json -v
```

### 交互式 CLI

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

    if name == "" || email == "" {
        fmt.Println("Error: name and email are required")
        return
    }

    fmt.Printf("Creating account for %s (%s)...\n", name, email)
    fmt.Println("Account created successfully!")
}
```

**用法：**
```bash
# 交互模式
./register

# 自动模式
./register --name John --email john@example.com --auto
./register -n John -e john@example.com -a
```

## 工具函数

```go
// 检查标志名是否有效
if cflag.IsGoodName("my-flag") {
    // 有效
}

// 添加前缀
flagName := cflag.AddPrefix("help")  // "--help"

// 添加短选项和长选项
flagName := cflag.AddPrefixes("help", []string{"h"})  // "-h, --help"

// 拆分快捷字符串
shorts := cflag.SplitShortcut("vh")  // []string{"v", "h"}

// 启用调试模式
cflag.SetDebug(true)
cflag.DebugMsg("Parsing flag: %s", "name")
```
