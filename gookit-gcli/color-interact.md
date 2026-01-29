# 颜色与交互

## 颜色输出

```go
import "github.com/gookit/color"

// 简单使用
color.Cyan.Printf("Hello %s\n", "world")

// 内置风格
color.Info.Tips("message")
color.Warn.Println("warning")
color.Error.Println("error")

// 自定义颜色
color.New(color.FgWhite, color.BgBlack).Println("custom")
color.Style{color.FgCyan, color.OpBold}.Println("style")

// 颜色标签
color.Print("<suc>success</><comment>comment</>")
color.Print("<fg=yellow;bg=black;op=underscore;>text</>")
```

## 用户交互

### 读取输入

```go
import "github.com/gookit/gcli/v3/interact"

name, _ := interact.ReadLine("Your name? ")
pwd := interact.ReadPassword("Password? ")
```

### 确认选择

```go
if interact.Confirm("Ensure continue?") {
    // 用户确认
}
```

### 单选列表

```go
ans := interact.SelectOne(
    "Select a city:",
    []string{"beijing", "shanghai", "guangzhou"},
    "",
)
```

### 多选列表

```go
ans := interact.MultiSelect(
    "Select cities:",
    []string{"beijing", "shanghai", "guangzhou"},
    nil,
)
```

## 进度显示

```go
import "github.com/gookit/gcli/v3/progress"

// 进度条
p := progress.Bar(maxSteps)
p.Start()
for i := 0; i < maxSteps; i++ {
    p.Advance()
}
p.Finish()

// 文本进度
p := progress.Txt("Processing...")
p.Start()
p.Advance()
p.Finish()

// 加载动画
progress.Loading().Start()
time.Sleep(2 * time.Second)
```
