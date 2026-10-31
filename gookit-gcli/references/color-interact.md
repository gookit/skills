# 颜色、交互、进度

这些能力不在 gcli 内：颜色来自 `github.com/gookit/color`，交互/进度/展示来自 `github.com/gookit/cliui`。
gcli 已依赖它们，业务模块直接 import 后 `go mod tidy` 即可。**`gcli/v3/interact`、`gcli/v3/progress`、`gcli/v3/show` 已不存在。**

## 颜色输出

```go
import "github.com/gookit/color"

color.Cyan.Printf("Hello %s\n", "world")
color.Info.Tips("message")        // INFO: message
color.Warn.Println("warning")
color.Error.Println("error")
color.Print("<suc>ok</> <comment>c</> <fg=yellow;bg=black;op=underscore;>text</>\n")
color.New(color.FgWhite, color.BgBlack).Println("custom")
```

`gcli.Print/Println/Printf` 是 `color.Print*` 的别名，同样解析 `<info>..</>` 标签。命令/应用的 `Desc`、`Examples` 也支持标签。
非 TTY 时颜色自动关闭；`color.Disable()` 手动关闭。

## 交互（cliui/interact）

```go
import "github.com/gookit/cliui/interact"

name, err := interact.ReadLine("Your name? ")        // (string, error)
pwd := interact.ReadPassword("Password? ")           // string
ok := interact.Confirm("Continue?")                  // bool；Confirm("..", true) 设默认值
city := interact.SelectOne("City:", []string{"beijing", "shanghai"}, "") // 单选，返回值
cities := interact.MultiSelect("Cities:", []string{"beijing", "shanghai"}, nil) // []string
```

- 带 `E` 后缀的变体返回 `error`：`ConfirmE SelectOneE MultiSelectE AskE`；`interact.Ask(q, def, validatorFn)` 带校验重问。
- `options` 可为 `[]string` 或 `map[string]string` 等；`defOpt` 为默认选项。
- 新版 UI 组件：`interact.NewUIInput(...).Run(ctx, interact.NewUIReadlineBackend())`，另有 `NewUISelect/NewUIConfirm/NewUIMultiSelect`。
- 选项值缺失时自动提问：`gflag.WithQuestion("Token: ")`。
- 测试：`cliui.CustomIO(in, out)` 注入输入输出，`defer cliui.ResetIO()`。

## 进度（cliui/progress）

```go
import "github.com/gookit/cliui/progress"

p := progress.Bar(100)       // 参数是步数(int64，可省略)；Txt/Counter/Full/DynamicText 同理
p.Start()
for i := 0; i < 100; i++ { p.Advance() }
p.Finish()

t := progress.Txt(3)         // 文本进度，如 33.3%(1/3)
t.Start(); t.Advance(); t.Finish()

sp := progress.LoadingSpinner(progress.RandomCharsTheme(), 100*time.Millisecond)
sp.Start()
// ... 工作 ...
sp.Stop("Done")
```

`progress.Txt("Processing...")` 这类传字符串的写法是错的（参数是步数）。其它：`RoundTrip`、`Spinner(speed)`、`NewMulti()`（多进度）、`NewByteTracker(p)`（字节速率）。
`gcli.GOpts().NoProgress`（环境变量 `NO_PROGRESS`）可全局关闭进度显示。
