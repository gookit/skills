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

## 参数取值（绑定后如何读取）

`AddArg` 只是**声明**；解析后用 `c.Arg("name")` 取到 `*gflag.CliArg`（内嵌 `structs.Value`），再按类型取值：

```go
c.Arg("key").String()    // 单值字符串
c.Arg("id").Int()        // 整数
c.Arg("cmd").Strings()   // 数组参数(Arrayed) -> []string；亦可 .Array()
c.Arg("x").HasValue()    // 是否绑定了值
```

> 选项(Opt)的值直接写入 `Config` 里 `XxxOpt(&v, ...)` 绑定的变量 `v`，无需再取。

## 参数与选项的解析顺序（重要·常见坑）

gcli 的 flag 解析（gflag，仿标准库 `flag`）**遇到第一个非选项 token 就停止解析选项**，因此选项必须在位置参数之前：

```bash
mycmd --host-path X --force myproj     # ✅ 选项在前，--host-path 正常绑定
mycmd myproj --host-path X             # ❌ 解析停在 myproj，--host-path 不绑定(落入剩余参数被忽略)
```

若要支持"位置参数在前"的写法，需在入口自行把前置位置参数重排到选项之后再 `app.Run(args)`——gcli 本身**不做**交错(interspersed)解析。

## `--` 分隔符与透传参数（passthrough）

gcli **原生处理 `--`**：遇到 `--` 即终止选项解析，其后所有 token 原样进入参数区（即使以 `-`/`--` 开头也不当选项）。**不要在入口自己切 `--`**。

捕获 `--` 之后的原始命令：声明一个**末尾的可选数组参数**来承接，用 `c.Arg(...).Strings()` 读取：

```go
Config: func(c *gcli.Command) {
    c.StrOpt(&agent, "agent", "a", "", "agent")
    // 承接 `-- <argv...>`，如 `run -a exec -- go test -run X`
    c.AddArg("cmd", "raw command after --", false, true) // 可选 + 数组
},
Func: func(c *gcli.Command, _ []string) error {
    argv := c.Arg("cmd").Strings() // ["go","test","-run","X"]
    _ = argv
    return nil
},
```

> **坑**：叶子命令若**未声明任何参数**(`!c.HasArguments()`)，给它传位置参数时会打印一行
> `ERROR: <cmd> - subcommand 'X' is not found`（随后仍 fallthrough 执行 Func）。
> 声明一个（数组）参数来承接，即可**同时消除该提示并拿到值**——优于读 Func 的剩余参数。

## Func 第二个参数 `args`

```go
Func: func(c *gcli.Command, args []string) error { ... }
```

> `args` 是**选项与命名参数都消费完后剩余的 token**，一般为空。特殊场景（未用 `AddArg` 声明时）可用它读 `--` 之后的透传值；但优先用 `AddArg` + `c.Arg(...)`（见上，且能消除上面的伪提示）。
