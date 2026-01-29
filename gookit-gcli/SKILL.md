---
name: gookit-gcli
description: Go 命令行应用和工具库。支持命令管理、选项/参数绑定、颜色输出、交互输入、进度显示等功能。用于快速构建专业的 CLI 应用程序。
author: auto-generated
source: https://github.com/gookit/gcli
tags: [go, cli, command-line, terminal, interactive, progress, color]
version: 1.0.0
generated: 2026-01-28
---

# Gookit GCli Skill

Golang 编写的简单易用的命令行应用和工具库。

## Quick Start

```bash
go get github.com/gookit/gcli/v3
```

```go
package main

import (
    "github.com/gookit/gcli/v3"
)

func main() {
    app := gcli.NewApp()
    app.Version = "1.0.3"
    app.Desc = "my cli application"

    app.Add(&gcli.Command{
        Name:    "demo",
        Desc:    "demo command",
        Aliases: []string{"dm"},
        Func: func(cmd *gcli.Command, args []string) error {
            gcli.Println("hello, in the demo command")
            return nil
        },
    })

    app.Run(nil)
}
```

## 核心功能

### 命令管理

- **多命令支持** - 添加多个命令及其别名
- **多级子命令** - 支持嵌套命令结构
- **自动帮助生成** - 命令执行错误时提示相似命令

详细用法见 [references/commands.md](references/commands.md)

### 选项与参数

- **选项绑定** - 支持 `--long` 长选项和 `-s` 短选项
- **结构体绑定** - 通过标签绑定选项和参数
- **验证器** - 自定义参数验证
- **POSIX 风格** - 支持短选项组合 (`-ab`)

详细用法见 [references/flags-args.md](references/flags-args.md)

### 颜色与交互

- **颜色输出** - 丰富的终端颜色渲染，Windows 兼容
- **用户交互** - 输入读取、确认选择、多选列表
- **进度显示** - 进度条、加载动画、文字动态更新

详细用法见 [references/color-interact.md](references/color-interact.md)

### 高级功能

- **自动补全** - 生成 bash/zsh 补全脚本
- **独立命令** - 单命令作为独立应用运行
- **错误处理** - 自动渲染错误提示

详细用法见 [references/advanced.md](references/advanced.md)

## 常用场景

| 场景        | 参考文档                                              |
|-----------|---------------------------------------------------|
| 创建 CLI 应用 | [references/commands.md](references/commands.md)             |
| 绑定选项和参数   | [references/flags-args.md](references/flags-args.md)         |
| 添加颜色输出和用户交互输入   | [references/color-interact.md](references/color-interact.md) |
| 生成命令补全    | [references/advanced.md](references/advanced.md)                        |

## 相关链接

- [Godoc](https://pkg.go.dev/github.com/gookit/gcli/v3)
- [GitHub](https://github.com/gookit/gcli)
- [gookit/color](https://github.com/gookit/color) - 颜色库
