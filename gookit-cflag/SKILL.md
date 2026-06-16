---
name: gookit-cflag
description: Enhanced flag parsing library for building command-line applications. Wraps and extends Go's standard flag package.
author: inhere
platform: github
source: https://github.com/gookit/goutil
tags: [go, golang, utilities, cli, cliapp, console, cflag, capp]
version: 1.0.0
generated: 2026-02-07T00:00:00Z
---

**Import**: `github.com/gookit/goutil/cflag`

Enhanced flag parsing library for building command-line applications. Wraps and extends Go's standard `flag` package.

## Overview

Gookit cflag 是一个增强型的命令行参数解析库，对 Go 标准库 `flag`进行了封装和扩展。

### 主要特性

- 支持短选项和长选项 (-h, --help)
- 多种标志类型支持 (string, int, bool, float, slice)
- 自定义验证器
- 枚举类型标志
- 键值对标志
- 自动帮助信息生成
- 支持必需参数
- 多命令应用支持

### 安装

```bash
go get github.com/gookit/goutil/cflag
```

## Quick Start

### 基础用法

学习如何创建 CFlags 实例、定义标志和解析参数：

→ 查看 [references/01-cflag-basic.md](references/01-cflag-basic.md)

```go
import "github.com/gookit/goutil/cflag"

c := cflag.New()
c.StrVar(&name, "name", "", "Your name;;n")
c.IntVar(&age, "age", 0, "Your age;;a")
c.Parse()
```

flag 描述格式为： `desc;required;short`

其中：

- desc: 描述文本
- required: true/false 可省略
- short: 短选项,多个逗号隔开 可省略

### 高级用法

学习枚举标志、键值对、自定义验证器等高级功能：

→ 查看 [references/02-cflag-advenced.md](references/02-cflag-advenced.md)

### 多命令应用

使用 `cflag/capp` 创建多命令 CLI 应用：

→ 查看 [references/03-cflag-capp.md](references/03-cflag-capp.md)

```go
// 使用 capp 创建多命令应用
app := capp.NewApp()
app.Add(newGetIPCmd(), newInitCmd())
app.Run()
```

## Documentation Structure

| 文档 | 说明 |
|------|------|
| [references/01-cflag-basic.md](references/01-cflag-basic.md) | 基础用法：创建实例、定义标志、解析参数、标志类型 |
| [references/02-cflag-advenced.md](references/02-cflag-advenced.md) | 高级用法：枚举标志、键值对、验证器、最佳实践 |
| [references/03-cflag-capp.md](references/03-cflag-capp.md) | 多命令应用：使用 `cflag/capp` 创建多命令 CLI 应用 |
