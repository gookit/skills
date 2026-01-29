---
name: gookit-validate
source: https://github.com/gookit/validate
description: Go 数据验证和过滤库。支持 Map、Struct、HTTP Request 验证，内置 70+ 验证器、数据过滤转换、自定义验证器、i18n 错误消息。框架无关，可用于 Gin、Echo、Chi 等。使用场景：(1) 验证 Struct 或 Map 数据，(2) HTTP 请求参数验证，(3) 表单数据校验，(4) 自定义验证规则
tags: ["golang", "validate", "validation", "filter", "gookit"]
---

# gookit-validate

Gookit/validate 是一个通用的 Go 数据验证和过滤库。

## 核心特性

- **多数据源验证**：支持 Map、Struct、HTTP Request (Form/JSON/url.Values/UploadedFile)
- **内置 70+ 验证器**：覆盖常见验证场景
- **数据过滤/转换**：验证前预处理数据
- **自定义验证器**：支持全局和临时验证器
- **场景验证**：不同场景验证不同字段
- **i18n 错误消息**：内置 en、zh-CN、zh-TW 支持
- **框架无关**：可在 Gin、Echo、Chi 等框架中使用

## 快速开始

```go
import "github.com/gookit/validate"

type UserForm struct {
    Name  string `validate:"required|minLen:7" label:"用户名"`
    Email string `validate:"email" message:"邮箱格式错误"`
    Age   int    `validate:"required|int|min:1|max:99"`
}

// 验证 Struct
v := validate.Struct(&UserForm{Name: "inhere"})
if v.Validate() {
    // 验证通过
} else {
    fmt.Println(v.Errors) // 获取错误信息
}

// 快速验证值
ok := validate.Val("test@example.com", "required|email")
```

## 主要功能

- [USAGE.md](USAGE.md) - 基础使用指南
- [VALIDATORS.md](VALIDATORS.md) - 内置验证器参考
- [ADVANCED.md](ADVANCED.md) - 高级用法（自定义验证器、过滤器、场景等）

## 与 go-playground/validator 对比

- 更轻量，API 更简洁
- 支持 Map 数据直接验证
- 内置数据过滤功能
- 场景验证更灵活
