# Changelog 生成

从 git log 生成变更日志。

## 安装 CLI 工具

```bash
go install github.com/gookit/gitw/cmd/chlog@latest
```

## CLI 使用

```bash
chlog prev last          # 从 prev 到 last
chlog v1.0.2 v1.0.3      # 指定版本
chlog -c config.yml last head  # 使用配置文件
chlog -h                 # 查看帮助
```

### 配置文件示例

```yaml
# .github/changelog.yml
title: "## Change Log"
log_format: "%s"
no_merges: true
group_prefix: "### "
group_suffix: "\n"
names:
  - feat
  - fix
  - perf
  - refactor
```

## 代码使用

```go
import (
    "github.com/gookit/gitw/chlog"
)

cl := chlog.New()
cl.WithConfig(func(c *chlog.Config) {
    c.Title = "## Change Log"
    c.LogFormat = "%s"
})

// 获取日志并生成
cl.FetchGitLog("v0.1.0", "HEAD", "--no-merges")
goutil.PanicIfErr(cl.Generate())

// 输出结果
fmt.Println(cl.Changelog())
```

## 配置选项

| 字段 | 说明 |
|------|------|
| `Title` | 标题 |
| `LogFormat` | git log format |
| `NoMerges` | 排除合并提交 |
| `RmRepeat` | 去除重复提交 |
| `GroupPrefix` | 分组前缀 |
| `GroupSuffix` | 分组后缀 |
| `Names` | 分组名称列表 |

## 过滤规则

```go
// 自定义过滤器
type ItemFilter interface {
    Handle(item *LogItem) bool
}

// 内置过滤器
WithExcludeScope("test")        // 排除范围
WithScopeFilter("feat", "fix")  // 只包含
```

## GitHub Actions 示例

```yaml
steps:
  - name: Checkout
    uses: actions/checkout@v3
    with:
      fetch-depth: 0

  - name: Generate changelog
    run: |
      curl -L https://github.com/gookit/gitw/releases/latest/download/chlog-linux-amd64 -o /usr/local/bin/chlog
      chmod a+x /usr/local/bin/chlog
      chlog -c .github/changelog.yml -o CHANGELOG.md prev last
```

## 输出格式

```markdown
## Change Log

### Features
- 🎨 add new component
- ✨ implement user auth

### Bug Fixes
- 🐛 fix memory leak
- 🔧 update config

### Performance
- ⚡ improve loading speed
```
