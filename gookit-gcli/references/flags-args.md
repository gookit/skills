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

## 内置自定义类型

gcli 内置了多种实现 `flag.Value` 的类型，直接与 `VarOpt` 配合使用，无需额外引入。

| 类型                | 说明                         | 输入示例                       |
|-------------------|------------------------------|------------------------------|
| `gcli.Strings`    | 可重复的字符串列表             | `--tag=a --tag=b`            |
| `gcli.Ints`       | 可重复的整数列表               | `--id=1 --id=2`              |
| `gcli.IntsString` | 逗号分隔的整数列表（单次传入）  | `--ids=1,2,3`                |
| `gcli.Booleans`   | 可重复的布尔列表               | `--flag=true --flag=false`   |
| `gcli.EnumString` | 枚举字符串（限定允许值）        | `--env=prod`                 |
| `gcli.KVString`   | 可重复的键值对                 | `--set=k1=v1 --set=k2=v2`   |
| `gcli.ConfString` | INI 格式配置字符串             | `--conf=k1=v1;k2=v2`        |

```go
cmd.Config = func(c *gcli.Command) {
    // 多值字符串列表: --tag=a --tag=b
    var tags gcli.Strings
    c.VarOpt(&tags, "tag", "t", "add build tags")

    // 枚举限定: --env=dev|test|prod
    var env gcli.EnumString
    env.SetEnum([]string{"dev", "test", "prod"})
    c.VarOpt(&env, "env", "e", "target environment")

    // 键值对: --set=key=value (可重复)
    var opts gcli.KVString
    c.VarOpt(&opts, "set", "s", "set key=value options")
}

// 读取值
fmt.Println(tags.Strings()) // []string{"a", "b"}
fmt.Println(env.String())   // "prod"
fmt.Println(opts.Data())    // maputil.SMap{"key": "value"} (即 map[string]string)
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
