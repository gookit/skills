# 选项与参数绑定

## 选项绑定方法

```go
// 布尔选项
cmd.BoolOpt(&b, "name", "shorts", false, "description")

// 数值选项
cmd.IntOpt(&id, "id", "", 2, "the id option")
cmd.StrOpt(&str, "name", "shorts", "default", "description")
cmd.Float64Opt(&f, "name", "shorts", 1.0, "description")

// 自定义类型 (需实现 flag.Value 接口)
cmd.VarOpt(&custom, "name", "shorts", "description")
```

## 结构体标签绑定

```go
type userOpts struct {
    Int  int    `flag:"name=int0;shorts=i;required=true;desc=int option message"`
    Bol  bool   `flag:"name=bol;shorts=b;desc=bool option message"`
    Str1 string `flag:"name=str1;shorts=o;required=true;desc=str1 message"`
    Str2 *string `flag:"name=str2;required=true;desc=str2 message"`
}

cmd.Config = func(c *gcli.Command) {
    c.MustFromStruct(&userOpts{
        Str2: &astr,
    })
}
```

### 标签格式

```
flag:"name=NAME;shorts=S;required=BOOL;desc=DESCRIPTION"
```

## 参数绑定

```go
// 必需参数
cmd.AddArg("arg0", "description", true)

// 可选参数
cmd.AddArg("arg1", "description", false)

// 数组参数
cmd.AddArg("arrArg", "description", false, true)
```

## 规则

- 必需参数必须在可选参数之前
- 数组参数只能在最后定义
- 支持 POSIX 风格短选项组合 (`-ab`)
