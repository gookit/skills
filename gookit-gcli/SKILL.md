---
name: gookit-gcli
description: 使用 gookit/gcli v3（模块 github.com/gookit/gcli/v3）编写或修改 Go 命令行应用：创建 App、命令/子命令、用 AddArg 声明位置参数并按名读取、把选项绑定到每个命令自己的结构体、退出码、中间件、补全脚本，以及通过 app.Run([]string{...}) 做真实分发的测试。遇到 gcli 的 --选项位置/`--` 透传/"subcommand is not found" 报错、或需要颜色/交互/进度/表格（已拆到 gookit/cliui）时使用。
---

# Gookit GCli (v3)

模块：`github.com/gookit/gcli/v3`（Go 1.23+）。根包 `gcli` 管 App/Command；选项与参数解析在 `gcli/v3/gflag`。
**交互、进度、表格/列表已不在 gcli 内**，在独立模块 `github.com/gookit/cliui`（见文末）。

```bash
go get github.com/gookit/gcli/v3
```

## 最小可运行示例

选项绑定到「命令构造函数里」的结构体，不要用包级可变变量；位置参数必须用 `AddArg` 声明。

```go
package main

import (
    "fmt"
    "os"

    "github.com/gookit/gcli/v3"
)

type copyOpts struct {
    Force bool     `flag:"name=force;shorts=f;desc=overwrite existing"`
    Mode  string   `flag:"name=mode;shorts=m;desc=copy mode;default=fast"`
    Tags  []string `flag:"name=tag;shorts=t;desc=repeatable tag"`
}

func newCopyCmd() *gcli.Command {
    opts := &copyOpts{} // 每次构造一份，命令间/测试间互不污染
    return &gcli.Command{
        Name:    "copy",
        Desc:    "copy files",
        Aliases: []string{"cp"},
        Config: func(c *gcli.Command) { // 命令初始化时调用一次
            c.MustFromStruct(opts)
            c.AddArg("src", "source path", true)         // 必填
            c.AddArg("dst", "target path", true)         // 必填
            c.AddArg("more", "more targets", false, true) // 可选 + 数组(只能放最后)
        },
        Func: func(c *gcli.Command, args []string) error {
            fmt.Println(c.Arg("src").String(), c.Arg("dst").String(), c.Arg("more").Strings(), opts.Force)
            return nil // 返回 error => 打印 ERROR 并使退出码非 0
        },
    }
}

func main() {
    app := gcli.NewApp()
    app.Name, app.Version, app.Desc = "myapp", "1.0.0", "my cli app"
    app.Add(newCopyCmd())
    os.Exit(app.Run(nil)) // nil = os.Args[1:]；Run 只返回退出码，不会自己 os.Exit
}
```

运行：`myapp copy a.txt b.txt c1 c2 -f --tag x -t y`（已验证：选项写在参数前后均可）。

## 关键行为（均已对照源码/实测）

| 主题 | 行为 |
|---|---|
| 退出码 | `app.Run` 返回码：成功 0；普通 `error`、解析错误、未知命令、panic（被捕获）均为 **2**；返回 `errorx.Failf(7, ...)`（实现 `errorx.ErrorCoder`）则用其 code。`ExitOnEnd` 默认 false，**main 必须 `os.Exit(app.Run(nil))`**，否则进程恒为 0 |
| 选项位置 | 默认**自动重排**：`cmd arg --opt v` 等价 `cmd --opt v arg`；`gflag.WithReorderArgs(false)` 可关（回到遇首个非选项即停） |
| 未声明的位置参数 | 叶子命令**没有任何 `AddArg`** 时，只要出现位置参数（含 `--` 之后的）就报 `<cmd> - subcommand 'X' is not found` 且退出码 2，**不会**执行 Func。要接收任意位置参数必须声明（可用一个数组参数） |
| 多余参数 | 已声明参数之外多出的位置参数不报错，进入 `Func` 的 `args`（非数组参数时）；数组参数会吞掉其后全部 |
| 读取参数 | `c.Arg("name")` 返回 `*gflag.CliArg`：`.String() .Int() .Bool() .Strings() .HasValue()`；**名字未声明会 panic** |
| `AddArg` 约束 | 必填不能在可选之后；只能有一个数组参数且在最后；重名/违规直接 panic（启动期暴露） |
| `--` | 紧跟选项之后写 `--` 时被消费，其后原样进入参数；若 `--` 前已有位置参数，`--` 会作为字面量进数组参数，需自行过滤 |
| 必填/校验失败 | 缺必填参数/选项、枚举越界、未定义选项（`option provided but not defined`）均退出码 2 |
| 全局选项 | 仅 `-h/--help`、`-V/--version`、`--gen-completion`；**没有** `--verbose`，日志级别用环境变量 `GCLI_VERBOSE=debug` 或 `gcli.SetVerbose(gcli.VerbDebug)` |
| 状态残留 | 同一个 App/Command 实例重复 `Run`，参数/选项值会残留上次的值；测试每例新建实例 |

## 子命令

```go
app.Add(&gcli.Command{
    Name: "db", Desc: "db tools",
    Subs: []*gcli.Command{{
        Name: "migrate", Desc: "run migrations", Aliases: []string{"mg"},
        Config: func(c *gcli.Command) { c.AddArg("target", "target version") },
        Func: func(c *gcli.Command, _ []string) error { return nil },
    }},
})
// 运行 myapp db migrate v2；也可 top.Add(sub) / gcli.NewCommand(name, desc, cfgFn)
```

父命令无 `Func` 时显示帮助；命令初始化（加入 app）之后再改 `Subs` 字段无效，请用 `c.Add(sub)`。详见 [references/commands.md](references/commands.md)。

## 选项绑定速览

- 代码绑定：`c.BoolOpt/IntOpt/StrOpt/Float64Opt/DurationOpt/VarOpt(&v, "name", "shorts", default, "desc")`；短名不能与长名相同（panic）。
- 泛型：`gflag.Opt(&c.Flags, &v, "name", "n", def, "desc")`（注意传 `&c.Flags`）。
- 结构体：`c.MustFromStruct(ptr[, gcli.TagRuleSimple|gcli.TagRuleField])`；指针字段须预先赋非 nil 值。
- 可重复/枚举：`gcli.Strings`、`gcli.Ints`、`gcli.EnumString`，以及 `gflag.KVString/IntsString/ConfString`。
- 共享选项：`parent.SharedOpts().StrOpt(...)` 供父及所有子孙命令使用。

详见 [references/flags-args.md](references/flags-args.md)。

## 测试：走真实分发

没有专门的测试助手；用 `app.Run([]string{...})` 拿退出码，输出用 `color.SetOutput` 捕获：

```go
func TestCopy(t *testing.T) {
    buf := new(bytes.Buffer)
    color.SetOutput(buf); defer color.ResetOutput()
    color.Disable();      defer color.ResetOptions()

    app := gcli.NewApp()          // 每个用例新建 app 与命令
    app.Add(newCopyCmd())
    code := app.Run([]string{"copy", "a", "b", "-f"})
    if code != 0 { t.Fatalf("code=%d out=%s", code, buf) }
}
```

要断言解析结果，让 `Func` 写入测试持有的变量/Writer。单命令：`cmd.Run(args)` 返回 `error`。详见 [references/testing.md](references/testing.md)。

## 颜色 / 交互 / 进度 / 展示（gookit/cliui）

| 需求 | import |
|---|---|
| 颜色标签 `gcli.Println("<info>x</>")`、`color.Info.Tips` | `github.com/gookit/color` |
| `interact.Confirm/ReadLine/SelectOne/MultiSelect/ReadPassword` | `github.com/gookit/cliui/interact` |
| `progress.Bar/Txt/LoadingSpinner` | `github.com/gookit/cliui/progress` |
| `show.AList/MList/JSON/Banner`、`table.New(...)`、`lists` | `github.com/gookit/cliui/show[/table|/lists]` |

`gcli/v3/interact|progress|show` 子包**已不存在**。详见 [references/color-interact.md](references/color-interact.md)、[references/data-show.md](references/data-show.md)。

## 参考文档

- [references/commands.md](references/commands.md) — App/命令/子命令/别名/中间件/钩子/默认命令/Handler
- [references/flags-args.md](references/flags-args.md) — 选项、结构体标签、参数、重排、`--`、共享选项
- [references/testing.md](references/testing.md) — 真实分发测试与输出捕获
- [references/color-interact.md](references/color-interact.md) — 颜色、交互、进度（cliui）
- [references/data-show.md](references/data-show.md) — 列表、JSON、表格（cliui）
- [references/advanced.md](references/advanced.md) — 补全脚本、文档生成、独立命令、严格模式

链接：[GoDoc](https://pkg.go.dev/github.com/gookit/gcli/v3) · [GitHub](https://github.com/gookit/gcli) · [cliui](https://github.com/gookit/cliui)
