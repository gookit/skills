# 使用指南

## 安装

```go
go get github.com/gookit/validate
```

## 验证 Struct

### 标签配置

```go
type UserForm struct {
    Name     string    `validate:"required|minLen:7" message:"名称必填" label:"用户名"`
    Email    string    `validate:"email" message:"邮箱格式错误"`
    Age      int       `validate:"required|int|min:1|max:99"`
    Password string    `validate:"required|minLen:6"`
    Code     string    `validate:"customValidator"` // 自定义验证
    Safe     int       `validate:"-"` // 跳过验证
}
```

### 自定义验证方法

```go
func (f UserForm) CustomValidator(val string) bool {
    return len(val) == 4
}
```

### 场景验证

```go
func (f UserForm) ConfigValidation(v *validate.Validation) {
    v.WithScenes(validate.SValues{
        "add":    []string{"Name", "Email", "Password"},
        "update": []string{"Name"},
    })
}

// 使用场景验证
v := validate.Struct(&UserForm{})
v.Validate("add") // 验证指定场景
```

### 自定义错误消息

```go
func (f UserForm) Messages() map[string]string {
    return validate.MS{
        "required":   "字段必填",
        "email":      "邮箱格式不正确",
        "Name.minLen": "名称至少7个字符",
    }
}

// 字段翻译
func (f UserForm) Translates() map[string]string {
    return validate.MS{
        "Name":  "用户名",
        "Email": "邮箱地址",
    }
}
```

## 验证 Map

```go
m := map[string]any{
    "name":  "inhere",
    "age":   100,
    "email": "test@example.com",
}

v := validate.Map(m)
v.StringRule("name", "required|minLen:7")
v.StringRule("age", "required|int|min:1|max:99")
v.StringRule("email", "required|email")

// 支持 slice 内元素验证
v.StringRule("tags.*", "required|string|minLen:1")

if v.Validate() {
    safeData := v.SafeData()
}
```

## 验证 HTTP Request

```go
import (
    "net/http"
    "github.com/gookit/validate"
)

func handler(w http.ResponseWriter, r *http.Request) {
    data, err := validate.FromRequest(r)
    if err != nil {
        panic(err)
    }

    v := data.Create()
    v.FilterRule("age", "int") // 转换为 int
    v.StringRule("name", "required|minLen:7")

    if v.Validate() {
        userForm := &UserForm{}
        v.BindSafeData(userForm)
    }
}
```

## 错误处理

```go
if v.Validate() {
    return nil
}

// 获取所有错误
es := v.Errors

// 判断是否有错误
es.Empty()

// 获取单个错误
es.One()       // 随机一条错误消息
es.OneError()  // 随机一个错误
es.Field("Name") // 指定字段的错误

// JSON 格式
// StopOnError=true (默认): 只返回第一个错误
// StopOnError=false: 返回所有错误
```

## 快速方法

```go
// 创建 Validation
validate.New(data)
validate.Struct(ptr)
validate.Map(m)
validate.Request(r)

// 从不同数据源创建 DataFace
validate.FromMap(m)
validate.FromStruct(s)
validate.FromJSON(jsonStr)
validate.FromURLValues(url.Values)
validate.FromRequest(r)
```
