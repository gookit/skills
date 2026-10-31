# 高级功能

## 补全脚本

两种方式，默认生成**动态（瘦）**脚本：脚本回调 `bin --in-completion ...` 取候选，命令/选项变化后无需重新生成。

```bash
myapp --gen-completion bash > ~/.myapp-completion.sh   # bash|zsh|pwsh
myapp --gen-completion help                            # 配置说明
```

或注册内置命令：

```go
import "github.com/gookit/gcli/v3/builtin"

app.Add(builtin.GenAutoComplete())
// myapp genac -s zsh -o out.zsh [-b bin-name] [-S 静态嵌入式脚本]
```

代码中：`app.GenCompletionScript("bash")`（动态）、`app.GenStaticCompletionScript("zsh")`。
选项可用 `gflag.WithChoices("a","b")` 提供取值候选。

## 命令文档生成

```go
app.Add(builtin.GenDoc())                  // myapp gendoc -f md|man -o ./docs

import "github.com/gookit/gcli/v3/docgen"
docgen.MarkdownTree(app, "./docs")         // 每命令一个 .md + index.md
docgen.ManTree(app, "./docs")
```

## 独立命令（单命令即应用）

```go
cmd := gcli.NewCommand("demo", "demo command", func(c *gcli.Command) {
    c.StrOpt(&opt, "opt", "o", "", "option")
    c.AddArg("file", "input file")
})
cmd.Func = func(c *gcli.Command, args []string) error { return nil }

if err := cmd.Run(nil); err != nil { // nil => os.Args[1:]；或 cmd.MustRun(nil)（出错打印）
    os.Exit(1)
}
```

独立运行时同样自带 `-h/--help`、`-V/--version`；`gcli.GOpts().SetDisable()` 可关闭自动绑定的全局选项（仅保留 help）。

## 日志级别与严格模式

- 级别：`VerbQuiet VerbError(默认) VerbWarn VerbInfo VerbDebug VerbCrazy`；环境变量 `GCLI_VERBOSE=debug` 或 `gcli.SetVerbose(gcli.VerbDebug)`。没有 `--verbose` 命令行选项。
- `gcli.SetStrictMode(true)`：规范化长选项形态（`--a`→`-a`、`---name`→`--name`）。
- `gcli.SetEnhanceShort(level)`：全局 POSIX 短选项增强，见 [flags-args.md](flags-args.md)。

## 错误处理

`Func` 返回 error 即由 gcli 渲染 `ERROR: ...` 并设码（见 [commands.md](commands.md#退出码)）。
需要在出错时做额外处理（日志、清理）可监听 `gcli.EvtCmdRunError`（命令级）或 `gevent.OnAppRunError`（应用级）钩子。

## 内置命令（builtin）

`builtin.GenAutoComplete()`、`builtin.GenDoc()` 为函数（可传 `func(c *gcli.Command)` 调整）；`builtin.GenCmdCode`、`builtin.GenEmojiMap` 为变量，用于开发期代码生成。
