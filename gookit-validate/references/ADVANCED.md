# 高级用法

## 自定义验证器

### 全局验证器

```go
func init() {
    validate.AddValidator("myCheck", func(val any) bool {
        // 验证逻辑
        return true
    })

    // 批量添加
    validate.AddValidators(validate.M{
        "check1": func(val any) bool { return true },
        "check2": func(val any) bool { return true },
    })
}
```

### 临时验证器

```go
v := validate.Struct(&UserForm{})
v.AddValidator("myCheck", func(val any) bool {
    return true
})
v.StringRule("field", "myCheck")
```

### 自定义 required 验证

验证器名必须以 `required` 开头：

```go
type Data struct {
    Age int `validate:"required_custom" message:"年龄必填"`
}

v := validate.New(&Data{Age: 0})
v.AddValidator("required_custom", func(val any) bool {
    // 自定义空值判断
    return false // 返回 false 表示验证失败
})
```

## 自定义过滤器

### 全局过滤器

```go
func init() {
    validate.AddFilter("myToInt", func(val any) int {
        // 过滤逻辑
        return 1
    })

    // 支持返回 error
    validate.AddFilters(validate.M{
        "filter1": func(val any) (int, error) { return 1, nil },
    })
}
```

### 临时过滤器

```go
v := validate.New(data)
v.AddFilter("myFilter", func(val any) int {
    return 1
})
v.FilterRule("field", "myFilter")
```

## 全局配置

```go
validate.Config(func(opt *validate.GlobalOption) {
    opt.StopOnError = false     // 不在第一个错误时停止
    opt.SkipOnEmpty = false     // 不跳过空值
    opt.UpdateSource = true     // 更新源数据
    opt.ValidatePrivateFields = true // 验证私有字段
})
```

## 字段标签

| 标签 | 说明 | 默认值 |
|------|------|--------|
| `validate` | 验证规则 | `validate` |
| `filter` | 过滤规则 | `filter` |
| `json` | 字段映射名 | `json` |
| `label` | 字段显示名 | `label` |
| `message` | 错误消息 | `message` |

## 在 Gin 中使用

```go
import (
    "github.com/gin-gonic/gin/binding"
    "github.com/gookit/validate"
)

type customValidator struct{}

func (c *customValidator) ValidateStruct(ptr any) error {
    v := validate.Struct(ptr)
    if v.Validate() {
        return nil
    }
    return v.Errors
}

func (c *customValidator) Engine() any { return nil }

func main() {
    binding.Validator = &customValidator{}
    // ... Gin 代码
}
```

## 数据过滤

验证前转换/清理数据：

```go
v := validate.Map(data)
v.FilterRule("age", "int")      // 转换为 int
v.FilterRule("name", "trim")    // 去除首尾空格
v.FilterRule("email", "lower")  // 转为小写
v.StringRule("age", "required|min:1|max:99")
```

## 内置过滤器

| 过滤器 | 说明 |
|--------|------|
| `int` / `toInt` | 转为 int |
| `uint` | 转为 uint |
| `int64` | 转为 int64 |
| `float` | 转为 float |
| `bool` / `toBool` | 转为 bool |
| `trim` | 去除首尾空格 |
| `lower` / `upper` | 大小写转换 |
| `camel` / `snake` | 命名风格转换 |
| `str2ints` | 字符串转 []int |
| `str2arr` | 字符串转 []string |
| `str2time` | 字符串转 time.Time |
| `escapeHtml` | HTML 转义 |
