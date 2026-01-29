# 高级功能

## 结构体映射

```go
type User struct {
    Name string
    Age  int
}

user := &User{}
ini.MapStruct(ini.DefSection(), user)
```

映射所有数据到嵌套 struct：

```go
ini.MapStruct("", ptr)
```

## 变量引用

INI 配置中支持 `%(varName)s` 变量引用：

```ini
[portal]
url = http://%(host)s:%(port)s/api
host = localhost
port = 8080
```

```go
cfg := ini.New()
cfg.WithOptions(ini.ParseVar)

fmt.Println(cfg.MustString("portal.url"))
// 输出: http://localhost:8080/api
```

## 环境变量

支持 `${ENV}` 和 `${ENV|default}` 格式：

```go
shell := ini.String("shell")     // 自动读取 $SHELL
noEnv := ini.String("noEnv")     // 使用默认值
```

## 选项配置

```go
// 默认实例设置选项
ini.WithOptions(ini.ParseEnv, ini.ParseVar)

// 新实例设置选项
cfg := ini.New()
cfg.WithOptions(ini.ParseEnv, ini.ParseVar, func(opts *Options) {
    opts.SectionSep = ":"        // 键路径分隔符
    opts.DefSection = "default"  // 默认 section 名
    opts.IgnoreCase = true       // 忽略大小写
})
```

### 可用选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `Readonly` | 只读模式 | false |
| `ParseEnv` | 解析环境变量 | true |
| `ParseVar` | 解析变量引用 | false |
| `IgnoreCase` | 忽略键名大小写 | false |
| `DefSection` | 默认 section 名 | `__default` |
| `SectionSep` | 键路径分隔符 | `.` |

## Dotenv 支持

```go
import "github.com/gookit/ini/v2/dotenv"

// 加载 .env 文件
dotenv.Load("./", ".env")
// dotenv.LoadExists("./", ".env")  // 忽略不存在的文件

// 读取环境变量
val := dotenv.Get("KEY")
intVal := dotenv.Int("LOG_LEVEL")
valWithDefault := dotenv.Get("KEY", "default")
```

### Dotenv 文件示例

```bash
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret
```

## 注释支持

- 单行注释: `;` 或 `#`
- 多行注释: `/* ... */`
- 多行值: `"""..."""` 或 `'''...'''`
