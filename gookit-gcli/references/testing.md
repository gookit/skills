# 测试 CLI

没有专用测试助手；用真实分发 `app.Run([]string{...})`（返回退出码）即可覆盖：命令查找、别名、选项重排、参数绑定、校验、中间件、退出码。

## 原则

- 命令用**构造函数**创建，选项结构体放在构造函数里（不要包级变量）；每个测试新建 App 与命令。
  同一实例重复 `Run` 会残留上一次的参数/选项值。
- `Run` 不会 `os.Exit`（`ExitOnEnd` 默认 false），可直接断言返回码。
- 断言解析结果：让 `Func` 把结果写入测试持有的变量或 `io.Writer`，而不是依赖打印。

## 示例

```go
func newGreetCmd(out *[]string) *gcli.Command {
    var name string
    return &gcli.Command{
        Name: "greet",
        Config: func(c *gcli.Command) {
            c.StrOpt(&name, "name", "n", "world", "who")
            c.AddArg("times", "repeat times")
        },
        Func: func(c *gcli.Command, args []string) error {
            *out = append(*out, fmt.Sprintf("%s x%s", name, c.Arg("times").String()))
            return nil
        },
    }
}

func TestGreet(t *testing.T) {
    var out []string
    app := gcli.NewApp()
    app.Add(newGreetCmd(&out))

    code := app.Run([]string{"greet", "3", "-n", "bob"}) // 参数在前也能解析
    assert.Eq(t, 0, code)
    assert.Eq(t, []string{"bob x3"}, out)
}
```

## 捕获输出

`gcli.Print*`、`color.*`、错误提示都经 `gookit/color` 输出：

```go
buf := new(bytes.Buffer)
color.SetOutput(buf); defer color.ResetOutput()
color.Disable();      defer color.ResetOptions() // 去掉颜色码

code := app.Run([]string{"fail"})
// code == 2, buf 含 "ERROR: boom"
```

帮助输出同理（`app.Run([]string{"-h"})` 返回 0，输出在 buf）。

## 断言错误路径

| 输入 | 退出码 |
|---|---|
| `Func` 返回普通 error | 2 |
| `Func` 返回 `errorx.Failf(7, ...)` | 7 |
| 缺必填参数/选项、未知选项、枚举越界 | 2 |
| 未知命令 | 2 |
| 无 AddArg 的叶子命令收到位置参数 | 2 |

## 单命令与交互

- 单命令（独立运行）：`err := cmd.Run([]string{"-o", "1", "file"})`，返回 `error` 而不是码。
- 交互输入（cliui）：`cliui.CustomIO(strings.NewReader("y\nbob\n"), out)`，结束 `defer cliui.ResetIO()`，
  之后 `interact.Confirm/ReadLine` 读取该输入、写入 `out`。
- 进程级全局配置（`gcli.SetVerbose`、`gcli.GOpts()`）测试后用 `gcli.ResetGOpts()` / `gcli.ResetVerbose()` 还原。
- 终端级端到端（真实 TTY 提示符）可参考 gcli 仓库的 `e2e_pty_test.go`（基于 `gookit/gopty`）。
