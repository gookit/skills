# 选项与参数

选项（`--long` / `-s`）与位置参数（`AddArg`）都在命令的 `Config` 里声明。`c` 内嵌 `gflag.Flags`（字段名 `c.Flags`）。

## 选项绑定

```go
Config: func(c *gcli.Command) {
    var verbose bool; var port int; var host string; var wait time.Duration
    c.BoolOpt(&verbose, "verbose", "v", false, "verbose output")
    c.IntOpt(&port, "port", "p", 8080, "port")
    c.StrOpt(&host, "host", "H", "localhost", "the `HOST` name") // 反引号词作为帮助里的值名
    c.DurationOpt(&wait, "wait", "w", time.Second, "wait time")
    c.Float64Opt(&rate, "rate", "", 1.0, "rate")
}
```

方法族：`BoolOpt IntOpt Int64Opt UintOpt Uint64Opt Float64Opt DurationOpt StrOpt(=StringOpt) VarOpt`；返回指针的 `Bool/Int/Str/...(name, shorts, def, desc) *T`；
`Xxx2(&v, "name,shorts", desc, setFns...)`（如 `StrOpt2`）；元数据版 `StrVar(&v, &gcli.CliOpt{Name:..., Required: true})`。

- **短名不能与长名相同**（如 `("x","x")`），否则 panic；重名也 panic。
- 默认值支持环境变量写法：`"${DB_USER}"`。
- `shorts` 可写多个，逗号分隔。
- 配置函数（`gflag.CliOptFn`）：`gflag.WithRequired() WithShorts WithDefault WithValidator WithChoices WithCategory WithQuestion WithCollector WithHandler`。

```go
c.StrOpt2(&token, "token,t", "api token",
    gflag.WithRequired(),
    gflag.WithValidator(func(v string) error { /* ... */ return nil }))
```

### 泛型绑定

```go
var name string; var tags []string
gflag.Opt(&c.Flags, &name, "name", "n", "tom", "the user name")
gflag.Opt(&c.Flags, &tags, "tag", "t", nil, "repeatable") // 切片/map 可重复；其默认值为零值
```

支持 `bool int int64 uint uint64 float64 string time.Duration []string []int []bool map[string]string` 及 `flag.Value`。
注意传的是 `&c.Flags`（不是 `c.Flags()`，命令上没有该方法；App 上才有 `app.Flags()`）。

### 自定义/多值类型（`VarOpt`）

| 类型 | 输入 | 取值 |
|---|---|---|
| `gcli.Strings` | `--tag a --tag b` | `.Strings()` |
| `gcli.Ints` | `--n 1 --n 2` | `[]int(v)` |
| `gcli.Booleans` | `--f true --f false` | `.Bools()` |
| `gcli.EnumString` | `--env prod`（越界报错） | `.String()`，先 `SetEnum([]string{"dev","prod"})` |
| `gflag.KVString` | `--set k=v --set a=b` | `.Data()`（SMap） |
| `gflag.IntsString` | `--ids 1 --ids 2`（可重复，**不是**逗号分隔） | `.Ints()` |
| `gflag.ConfString` | `--conf 'k0=v0;k1=v1'` | `.Data()` |

任何实现 `flag.Value` 的类型都可用 `c.VarOpt(&v, "name", "n", "desc")`。

## 结构体绑定

```go
type opts struct {
    Force bool     `flag:"name=force;shorts=f;desc=overwrite"`
    Name  string   `flag:"name=name,n;required=true;desc=user name"` // name 里可带短名
    Port  int      `flag:"name=port;shorts=p;desc=port;default=80"`
    Tags  []string `flag:"name=tag;shorts=t;desc=repeatable"`
    Opt   *string  `flag:"name=opt;desc=pointer field"`   // 指针字段须预先赋非 nil
}
o := &opts{Opt: new(string)}
c.MustFromStruct(o)             // 失败 panic；c.FromStruct(o) 返回 error
```

三种规则（第二个参数）：

| 规则 | 标签 |
|---|---|
| `gcli.TagRuleNamed`（默认） | `flag:"name=n;shorts=s;required=true;desc=...;default=v"` |
| `gcli.TagRuleSimple` | `flag:"desc;required;default;shorts"` 或 `flag:"name;desc;required;default;shorts"` |
| `gcli.TagRuleField` | 字段名转 snake/kebab 作选项名：`` `flag:"u" desc:"..." required:"true" default:"18" enum:"a,b,c"` `` |

支持字段：`bool int uint float string []string []int []bool time.Duration map[string]string` 及 `flag.Value`；匿名嵌套结构体自动展开；`enum:"a,b"` 校验取值（Field 规则）。已验证。

## 位置参数

```go
c.AddArg("src", "source", true)            // 必填
c.AddArg("dst", "target")                  // 可选
c.AddArg("rest", "more", false, true)      // 数组，吞掉其后全部，只能放最后
```

`AddArg(name, desc string, requiredAndArrayed ...bool) *gflag.CliArg`。违规（必填在可选后、数组后再加、重名）会 panic。
可链式配置：`.WithDefault(v) .WithValidator(func(any)(any,error)) .WithAfterFn(...)`。

读取：

```go
c.Arg("src").String()      // 也有 .Int() .Int64() .Float64() .Bool()
c.Arg("rest").Strings()    // 数组参数；亦可 .Array()
c.Arg("dst").HasValue()
c.Args()                   // 全部声明的参数
```

`c.Arg("未声明")` 会 panic。缺少必填参数：`must set value for the argument: dst(position#1)`，退出码 2。

### 未声明/多余的位置参数

| 情形 | 结果 |
|---|---|
| 叶子命令一个 `AddArg` 都没有，却传了位置参数 | 报 `<cmd> - subcommand 'x' is not found`，退出码 2，Func 不执行（`--` 之后的也一样） |
| 声明了 N 个非数组参数，传了更多 | 多出部分进入 `Func` 的 `args`，不报错 |
| 声明了数组参数 | 其位置之后全部进入该数组，`args` 为空 |

要接收「任意个位置参数」，声明一个可选数组参数即可。

## 解析顺序与 `--`

- 默认**自动重排**，选项可在参数前后任意位置：`copy a b -f` ≡ `copy -f a b`。关闭（回到标准库式、遇非选项即停）：`c.WithConfigFn(gflag.WithReorderArgs(false))`。
- 子命令边界处重排会停止，只重排最终被执行命令的参数。
- 未声明的选项（即使参数里想当字面量用）会报 `option provided but not defined: --run`。要把 `-x/--y` 这类原样交给下游，需用 `--`。
- `--` **紧跟选项之后**：被消费，其后全部原样进入参数区：

```go
Config: func(c *gcli.Command) {
    c.StrOpt(&agent, "agent", "a", "", "agent")
    c.AddArg("cmd", "raw argv after --", false, true)
},
Func: func(c *gcli.Command, _ []string) error {
    argv := c.Arg("cmd").Strings() // run -a exec -- go test -run X  => [go test -run X]
    return nil
},
```

- 若 `--` 前已有位置参数（`r A -- B -x`），`--` 本身会作为字面量出现在数组参数里（`["--","B","-x"]`），需自行过滤。

## 短选项增强

默认关闭。`-ab` 拆分仅当组合内全是 bool 短选项：

```go
c.ParserCfg().EnhanceShort = gcli.EnhanceShortMerge  // -aux => -a -u -x
c.ParserCfg().EnhanceShort = gcli.EnhanceShortAttach // 另支持 -Ostdout => -O stdout
gcli.SetEnhanceShort(gcli.EnhanceShortMerge)          // 全局，命令自身设置优先
```

## 共享（继承）选项

```go
var gitDir string
top := &gcli.Command{Name: "git", Desc: "git tools"}
top.SharedOpts().StrOpt(&gitDir, "git-dir", "", ".git", "git dir") // 父及全部子孙共用同一变量
top.Add(&gcli.Command{Name: "status", Func: func(c *gcli.Command, _ []string) error {
    _ = gitDir; return nil
}})
// myapp git status --git-dir /x
```

帮助中归入 `Inherited Options` 分组。

## 其它

- 必填选项：`WithRequired()` / 结构体 `required=true`；`c.Required("name")`。
- 选项为空时交互收集：`gflag.WithQuestion("Token: ")`（需要终端输入）。
- 严格模式：`gcli.SetStrictMode(true)`，规范化 `--a`→`-a`、`---name`→`--name`；`--` 之后与取值型选项的值保持原样。
