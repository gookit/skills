# 命令管理

## 创建应用

```go
app := gcli.NewApp()
app.Version = "1.0.3"
app.Desc = "my cli application"
// app.SetVerbose(gcli.VerbDebug)
app.Run(nil) // 传 nil 等价 os.Args[1:]
```

### 添加全局选项

```go
// app 上也有 Command 相同的选项绑定方法
app.Flags().BoolOpt(...)
app.Flags().StrOpt(...)
```

### 监听App事件

```go
app.On(gcli.EvtGOptionsParsed, func(ctx *gcli.HookCtx) (stop bool) {
	// eg. bootstrap config load
	return
})
```

### 退出码

`app.Run(args)` **返回进程退出码**（成功为 0）。需要把命令失败传播为非 0 退出码时：

```go
os.Exit(app.Run(nil))
```

> gcli 仅从实现了 `errorx.ErrorCoder` 的错误推导非 0 退出码（如 `errorx.Failf(code, ...)`）；普通 `error` 仅打印、退出码仍为成功值。命令需要非 0 退出时返回带 code 的错误。

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

运行: `app parent child`（多级子命令需带上父命令路径，不能只写 `app child`）

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
