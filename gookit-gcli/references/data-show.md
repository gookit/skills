# 数据展示（cliui/show）

import：`github.com/gookit/cliui/show`（**不是** `gcli/v3/show`）。

## 快捷函数

```go
import "github.com/gookit/cliui/show"

show.AList("User Info", map[string]any{"Name": "Tom", "Age": 30}) // 键值列表
show.MList(map[string]any{                                        // 多组列表
    "Server": map[string]any{"Host": "localhost"},
    "DB":     map[string]any{"Name": "app"},
})
show.JSON(v)                    // 美化 JSON；show.JSON(v, "", "  ") 自定义前缀/缩进
show.Banner("Welcome")          // 边框横幅
show.ATitle("Section")          // 标题行
```

`show.NewList(title, data)` / `show.NewLists(listMap)` / `show.NewBanner(...)` 返回对象，可调用 `.Format()` 输出。

## 表格 `show/table`

```go
import "github.com/gookit/cliui/show/table"

table.New("Users").
    SetHeads("Name", "Age").
    AddRow("Tom", 25).
    AddRow("Jerry", 30).
    Format() // 直接打印；Render() 返回 string

// struct slice：字段名即表头
type User struct { Name string; Age int }
table.New("Team").SetRows([]User{{"Tom", 25}}).Format()

// [][]any
table.New("R").SetHeads("ID", "Msg").SetRows([][]any{{1, "ok"}}).Format()
```

样式：`WithStyle(table.StyleRounded)`；可选 `StyleMySql StyleSimple StyleMarkdown StyleBold StyleRounded StyleDouble StyleMinimal StyleBoldBorder`。
其它选项：`table.New(title, table.WithStyle(...), table.WithShowRowNumber(true), table.WithoutBorder(), table.WithCSVOutput(true))`。

## 列表 `show/lists`

```go
import "github.com/gookit/cliui/show/lists"

lists.NewList("Config", map[string]any{"key": "val"}).Format()
```

## 其它子包

`show/alert`（提示消息）、`show/title`、`show/banner`、`show/emoji`、`show/symbols`。输出重定向用 `cliui.SetOutput(w)` / `cliui.CustomIO(in, out)`。
