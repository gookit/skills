# cflag 基础用法

## 创建 CFlags 实例

```go
import "github.com/gookit/goutil/cflag"

// 创建新的 cflag 实例
c := cflag.New()

// 创建时指定应用信息
c := cflag.NewWith("myapp", "1.0.0", "My application description")

// 使用函数式选项创建
c := cflag.New(
    cflag.WithDesc("My application"),
    cflag.WithVersion("1.0.0"),
)
```

## 定义标志

```go
var (
    name    string
    age     int
    verbose bool
)

c := cflag.New()

// String 标志，带短选项
c.StrVar(&name, "name", "", "Your name;;n")

// Int 标志
c.IntVar(&age, "age", 0, "Your age;;a")

// Bool 标志
c.BoolVar(&verbose, "verbose", false, "Verbose output;;v")

// 解析命令行参数
c.Parse()
```

## 解析参数

```go
// 解析 os.Args
err := c.Parse()
if err != nil {
    fmt.Println("Error:", err)
    os.Exit(1)
}

// 必须解析（遇到错误会 panic）
c.MustParse()

// 解析自定义参数
err = c.ParseArgs([]string{"--name", "John", "--age", "30"})
```

## 标志类型

### String 标志

```go
var name string
c.StrVar(&name, "name", "n", "", "User name")

// 带默认值
var config string
c.StrVar(&config, "config", "c", "config.yml", "Config file")
```

### Integer 标志

```go
var port int
c.IntVar(&port, "port", 8080, "Server port;;p")

var count int64
c.Int64Var(&count, "count", "", 0, "Item count")

var size uint
c.UintVar(&size, "size", 0, "Buffer size;;s")
```

### Boolean 标志

```go
var verbose bool
c.BoolVar(&verbose, "verbose", "v", false, "Verbose output")

var debug bool
c.BoolVar(&debug, "debug", "d", false, "Debug mode")
```

### Float 标志

```go
var threshold float64
c.Float64Var(&threshold, "threshold", 0.5, "Threshold value;;t")
```

### Slice 标志

```go
var tags []string
c.StrSliceVar(&tags, "tags", nil, "Tags list;;t")
// 用法: --tags=tag1,tag2,tag3

var ports []int
c.IntSliceVar(&ports, "ports", nil, "Port list")
// 用法: --ports=8080,8081,8082
```

## 绑定参数

支持按位置绑定剩余参数：

```go
// 格式
c.AddArg("name", "description", [required:bool], [is_array:bool])

// eg
c.AddArg("file", "file name")
```

获取值：

```go
fileName := c.Arg("file").String()
```

## 简单示例

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

    c := cflag.NewWith(
        "userinfo",
        "1.0.0",
        "Display user information",
    )

    c.StrVar(&name, "name", "n", "", "User name (required)")
    c.IntVar(&age, "age", "a", 0, "User age")
    c.BoolVar(&verbose, "verbose", "v", false, "Verbose output")

    c.MustParse()

    if name == "" {
        fmt.Println("Error: name is required")
        c.PrintHelp()
        os.Exit(1)
    }

    fmt.Printf("Name: %s\n", name)
    if age > 0 {
        fmt.Printf("Age: %d\n", age)
    }

    if verbose {
        fmt.Println("Verbose mode enabled")
    }
}
```

**用法：**
```bash
./userinfo --name John --age 30 --verbose
./userinfo -n John -a 30 -v
```
