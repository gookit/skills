# 基本使用

## 加载配置

```go
// 加载文件，不存在则报错
err := ini.LoadFiles("config.ini")

// 加载文件，不存在则忽略
err := ini.LoadExists("config.ini", "other.ini")

// 从字符串加载
err := ini.LoadStrings(`
[section]
key = value
`)
```

## 读取数据

```go
// 基本类型
name := ini.String("name")
age := ini.Int("age")
enabled := ini.Bool("debug")

// 键路径写法
val := ini.String("sec1.key")

// Section 数据
secData := ini.StringMap("sec1")
// map[string]string{"key":"val0", "some":"value"}

// 默认值
val := ini.String("not-exist", "default")
```

## 设置数据

```go
// 设置值
ini.Set("name", "new name")
ini.Set("sec1.key", "new value")

// 读取设置后的值
name := ini.String("name")
```

## 完整示例

```go
ini.LoadExists("testdata/test.ini")

fmt.Println(ini.String("name"))       // inhere
fmt.Println(ini.Int("age"))           // 50
fmt.Println(ini.Bool("debug"))        // true
fmt.Println(ini.String("sec1.key"))   // val0
```

### INI 文件示例

```ini
# comments
name = inhere
age = 50
debug = true

[sec1]
key = val0
some = value
```
