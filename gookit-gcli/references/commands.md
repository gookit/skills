# 命令管理

## 创建应用

```go
app := gcli.NewApp()
app.Version = "1.0.3"
app.Desc = "my cli application"
// app.SetVerbose(gcli.VerbDebug)
app.Run(nil)
```

## 添加命令

### 直接定义

```go
app.Add(&gcli.Command{
    Name:    "demo",
    Desc:    "this is a description",
    Aliases: []string{"dm"},
    Func: func(cmd *gcli.Command, args []string) error {
        gcli.Println("hello, in the demo command")
        return nil
    },
})
```

### 独立命令变量

```go
var MyCmd = &gcli.Command{
    Name:    "demo",
    Desc:    "demo command",
    Aliases: []string{"dm"},
    Func: func(cmd *gcli.Command, args []string) error {
        gcli.Println("hello")
        return nil
    },
    Subs: []*gcli.Command{},
}

app.Add(MyCmd)
```

## 子命令

```go
app.Add(&gcli.Command{
    Name: "parent",
    Desc: "parent command",
    Subs: []*gcli.Command{
        {
            Name:    "child",
            Desc:    "child command",
            Aliases: []string{"c"},
            Func: func(c *gcli.Command, args []string) error {
                gcli.Println("child command executed")
                return nil
            },
        },
    },
})
```

运行: `app child`

## 命令字段

| 字段 | 说明 |
|------|------|
| `Name` | 命令名称 |
| `Desc` | 命令描述 |
| `Aliases` | 命令别名列表 |
| `Func` | 命令执行函数 |
| `Config` | 命令配置函数（初始化时调用） |
| `Subs` | 子命令列表 |

## 帮助信息

```bash
./cliapp           # 显示所有命令
./cliapp -h        # 显示帮助
./cliapp --help    # 显示帮助
./cliapp cmd -h    # 显示指定命令帮助
```

## 错误提示

输入错误命令时，自动提示相似命令和别名。
