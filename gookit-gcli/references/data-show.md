# 数据展示 (show 包)

import 路径: `github.com/gookit/gcli/v3/show`

## 快捷函数

```go
import "github.com/gookit/gcli/v3/show"

// 键值列表
show.AList("User Info", map[string]any{
    "Name": "Tom",
    "Age":  30,
    "Role": "admin",
})

// 多组键值列表 (map of maps)
show.MList(map[string]any{
    "Server": map[string]any{"Host": "localhost", "Port": 8080},
    "DB":     map[string]any{"Host": "db:5432", "Name": "app"},
})

// JSON 格式化输出
show.JSON(myStruct)
show.JSON(myStruct, "", "  ") // 自定义缩进

// 标题横幅
show.Banner("Welcome to MyApp")

// 标题行
show.ATitle("Section Title")
```

## 表格 (show/table)

import 路径: `github.com/gookit/gcli/v3/show/table`

### 手动构建

```go
import "github.com/gookit/gcli/v3/show/table"

table.New("Users").
    SetHeads("Name", "Age", "City").
    AddRow("Tom", 25, "Beijing").
    AddRow("Jerry", 30, "Shanghai").
    Format() // 直接打印到终端
```

### struct slice 自动映射

字段名自动作为表头，无需手动 `SetHeads`：

```go
type User struct {
    Name string
    Age  int
    Job  string
}

table.New("Team").
    SetRows([]User{
        {"Tom", 25, "Engineer"},
        {"Jerry", 30, "Designer"},
    }).
    Format()
```

### `[][]any` 行数据

```go
table.New("Report").
    SetHeads("ID", "Status", "Msg").
    SetRows([][]any{
        {1, "OK", "success"},
        {2, "ERR", "timeout"},
    }).
    Format()
```

### 样式

| 常量 | 效果 |
|------|------|
| `table.StyleMySql` | MySQL 风格边框 |
| `table.StyleSimple` | 简洁无外框 |
| `table.StyleMarkdown` | Markdown 表格格式 |
| `table.StyleBold` | 加粗边框 |
| `table.StyleRounded` | 圆角边框 |
| `table.StyleDouble` | 双线边框 |
| `table.StyleMinimal` | 极简风格 |
| `table.StyleBoldBorder` | 加粗外框 |

```go
table.New("Styled").
    SetHeads("ID", "Name").
    AddRow(1, "Alice").
    WithStyle(table.StyleRounded).
    Format()
```

### 获取字符串而非打印

```go
output := table.New("Data").
    SetHeads("K", "V").
    AddRow("foo", "bar").
    Render() // 返回 string

fmt.Fprint(w, output)
```

## 列表 (show/lists)

```go
import "github.com/gookit/gcli/v3/show/lists"

// 单个列表
l := lists.NewList("Config", map[string]any{"key": "val"})
l.Format()

// 通过 show 包快捷调用
show.NewList("Config", map[string]any{"key": "val"}).Format()
```
