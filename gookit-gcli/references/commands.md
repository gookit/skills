# 应用与命令

## App

```go
app := gcli.NewApp()            // 等价 gcli.New()
app.Name = "myapp"
app.Version = "1.0.0"           // 默认 "0.1.0-dev"
app.Desc = "my cli app"
app.SetLogo("ASCII logo", "info")
os.Exit(app.Run(nil))           // nil => os.Args[1:]
```

- `app.Run(args)` 返回退出码；`ExitOnEnd` 默认 false（不会自己退出）。`gcli.NewApp(gcli.NotExitOnEnd())` 与默认等价，可显式写出意图。
- 其它入口：`app.QuickRun()`（用 os.Args）、`app.RunArgs("cmd", "-a")`、`app.RunLine("cmd -a val")`。
- `app.Func`：无命令名时执行（为空则显示帮助）。`app.SetDefaultCommand("name")`：无命令名时默认跑某命令。
- 应用级选项（写在命令名之前）：`app.Flags().StrOpt(&cfg, "config", "c", "", "config file")`，如 `myapp -c x.yml cmd`。
- 全局选项只有 `-h/--help`、`-V/--version`、`--gen-completion`。

## 退出码

| 情形 | 码 |
|---|---|
| 成功 | 0 |
| `Func` 返回普通 `error`、解析/校验错误、未知命令、panic | 2 |
| 返回实现 `errorx.ErrorCoder` 的错误 | 其 `Code()` |

```go
import "github.com/gookit/goutil/errorx"

return errorx.Failf(7, "deploy failed: %s", reason) // 退出码 7
```

`c.NewErrf(...)` 只是 `fmt.Errorf` 的包装，不改变退出码。

## 定义命令

```go
app.Add(&gcli.Command{
    Name:     "demo",
    Desc:     "desc with <info>color</> and {$cmd}", // 支持颜色标签与帮助变量
    Aliases:  []string{"dm"},
    Category: "tools",    // 帮助中分组
    Hidden:   false,
    Examples: "{$binName} {$cmd} --id 12 file",
    Config:   func(c *gcli.Command) { /* 绑定选项/参数 */ },
    Func:     func(c *gcli.Command, args []string) error { return nil },
})

// 或
cmd := gcli.NewCommand("demo", "desc", func(c *gcli.Command) { /* Config */ })
cmd.Func = func(c *gcli.Command, args []string) error { return nil }
app.Add(cmd)         // 一次可 app.Add(a, b, c)；也可 cmd.AttachTo(app)
```

`Func` 的 `args` 是选项与命名参数消费后**剩余**的位置参数（声明了数组参数时通常为空）。
`Config` 在加入 app 时执行一次；选项值写入 `Config` 里绑定的变量，命令间不要共用包级变量。

帮助变量：`{$cmd} {$fullCmd} {$binName} {$binWithCmd} {$binWithPath} {$binDir} {$workDir}`。

## 子命令

```go
parent := &gcli.Command{Name: "git", Desc: "git tools"}
parent.Add(gcli.NewCommand("status", "show status", func(c *gcli.Command) {
    c.Func = func(c *gcli.Command, _ []string) error { return nil }
}))
app.Add(parent)
```

- 运行 `app git status`；需带完整父路径。无 `Func` 的父命令会显示子命令帮助。
- 子命令找不到：父命令**没有声明参数**时报 `git - subcommand 'x' is not found`（退出码 2）；声明了参数的命令则把它当作参数。
- `c.Path()` 如 `git status`；`c.ID()` 如 `git:status`；`c.Parent()`、`c.Root()`、`c.App()`。
- 在命令里调用其它命令：`c.App().Exec("git status", []string{"-a"})`（返回 error，不走退出码）。

## 中间件

```go
app.Use(func(c *gcli.Command, args []string) error { return nil })     // 所有命令，先执行
cmd.Use(authCheck)                                                       // 单命令，后于 app 级
```

按注册顺序执行，任一返回 error 即中止，主 `Func` 不再执行。panic 会被恢复并转成 error（码 2）。

## 钩子事件

```go
app.On(gcli.EvtAppOptsParsed, func(ctx *gcli.HookCtx) (stop bool) {
    // 例如加载配置；返回 true 则停止后续运行
    return false
})
cmd.On(gcli.EvtCmdRunBefore, hookFn)
```

常用：`EvtAppInitBefore / EvtAppInit / EvtAppOptsParsed / EvtAppPrepareAfter / EvtAppExit / EvtCmdNotFound / EvtCmdSubNotFound / EvtCmdOptParsed / EvtCmdRunBefore / EvtCmdRunAfter / EvtCmdRunError`（常量也在 `gcli/v3/gevent` 包，名为 `On*`）。

## Handler 接口

```go
type hello struct{ name string }

func (h *hello) Creator() *gcli.Command { return &gcli.Command{Name: "hello", Desc: "say hello"} }
func (h *hello) Config(c *gcli.Command) { c.StrOpt(&h.name, "name", "n", "world", "who") }
func (h *hello) Execute(c *gcli.Command, args []string) error { return nil }

app.AddHandler(&hello{})
```

## 帮助与分类

- `myapp`（无参）、`myapp -h`、`myapp help [cmd]`、`myapp cmd -h` 显示帮助；输入错误命令时提示相似命令。
- 命令 `Category` 与选项 `gflag.WithCategory("x")` 用于帮助分组。
