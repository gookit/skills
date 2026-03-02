# 高级功能

## 生成命令补全脚本

```go
import "github.com/gookit/gcli/v3/builtin"

app.Add(builtin.GenAutoComplete())
```

构建并运行：

```bash
go build ./_examples/cliapp.go && ./cliapp genac
```

生成 `auto-completion.bash` 或 `auto-completion.zsh` 文件。

## 独立命令应用

将单个命令作为独立应用运行：

```go
import "github.com/gookit/color/colorp"

cmd := gcli.NewCommand("demo", "demo command")
cmd.Config = func(c *gcli.Command) {
    c.StrOpt(&opt, "opt", "o", "", "option message")
}
cmd.Func = func(c *gcli.Command, args []string) error {
    gcli.Println("demo command")
    return nil
}

if err := cmd.Run(nil); err != nil {
    colorp.Errorln(err)
}
```

## 错误处理

```go
func exampleExecute(c *gcli.Command, args []string) error {
    if someError {
        return c.NewErrf("something went wrong: %s", err)
    }
    return nil
}
```

错误会自动渲染为带颜色的提示信息。

## 全局选项

| 选项 | 说明 |
|------|------|
| `--verbose, -v` | 显示详细日志 |
| `--version, -V` | 显示版本 |
| `--help, -h` | 显示帮助 |
