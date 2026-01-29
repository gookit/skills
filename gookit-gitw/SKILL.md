---
name: gookit-gitw
source: https://github.com/gookit/gitw
description: Git 命令包装器、仓库信息查询、Changelog 生成工具。用于执行 git 命令、查询仓库信息（分支/标签/远程）、生成变更日志。支持链式调用、gitmoji emoji 转换、GitHub Actions 集成。使用场景：(1) 需要在代码中执行 git 命令，(2) 查询仓库状态和分支信息，(3) 生成版本变更日志，(4) 解析 gitmoji 提交信息
tags: ["git", "golang", "gitw", "changelog", "gitmoji", "cli"]
---

# gookit-gitw

Git 命令包装器、仓库信息查询、Changelog 生成工具。

## 安装

```bash
go get github.com/gookit/gitw
```

## 核心功能

### GitWrap - Git 命令包装器

链式调用执行 git 命令：

```go
import "github.com/gookit/gitw"

// 标准命令
gitw.Log("-2").OutputLines()
gitw.Branch("-a").SafeOutput()
gitw.Tag("-l").Output()

// 自定义命令
gitw.New("log", "-2").SafeOutput()
gitw.Cmd("status", "-s").Output()

// 链式配置
gw := gitw.New("log", "-1").
    WithWorkDir("/path/to/repo").
    WithArgf("--pretty=format:'%s'", "%H")
output := gw.SafeOutput()
```

**执行方法：**

| 方法 | 说明 |
|------|------|
| `Output()` | 返回 (string, error) |
| `SafeOutput()` | 忽略错误，返回空字符串 |
| `OutputLines()` | 按行分割返回 []string |
| `Run()` | 执行命令，返回 error |
| `Success()` | 返回 bool |
| `MustRun()` | 失败 panic |

### Repo - 仓库信息查询

```go
repo := gitw.NewRepo("/path/to/repo")
```

**仓库信息：**

```go
repo.Info()           // RepoInfo{Name, Branch, Version, URL, Remotes}
repo.StatusInfo()     // StatusInfo{分支状态、跟踪分支}
repo.CurBranchInfo()  // 当前分支信息
repo.CurBranchName()  // 当前分支名
repo.LastCommitID()   // 最后提交 ID
repo.LastAbbrevID()   // 7位提交 ID
```

**分支操作：**

```go
repo.BranchInfos()           // 所有分支信息
repo.BranchInfo("feature/x") // 指定分支信息
repo.HasBranch("dev")        // 检查分支是否存在
repo.HasLocalBranch("dev")   // 检查本地分支
repo.HasRemoteBranch("dev", "origin") // 检查远程分支
repo.BranchDelete("name", "origin")   // 删除分支
```

**标签操作：**

```go
repo.Tags()                    // 所有标签
repo.LargestTag()              // 最大版本标签
repo.TagSecondMax()            // 第二大标签
repo.TagsSortedByRefName()     // 按标签名排序
repo.TagsSortedByCreatorDate() // 按创建时间排序
```

**远程操作：**

```go
repo.RemoteNames()           // 远程名称列表
repo.RemoteInfo("origin")    // 远程信息
repo.DefaultRemoteInfo()     // 默认远程信息
repo.UpstreamPath()          // 上游分支路径 "origin/main"
repo.UpstreamRemote()        // 上游远程名
repo.UpstreamBranch()        // 上游分支名
```

**快速执行：**

```go
repo.QuickRun("fetch", "--all")
repo.Git().Log("-1").Output()
```

### Gitmoji - Emoji 支持

```go
import "github.com/gookit/gitw/gmoji"

em := gmoji.MustEmojis("en") // 或 "zh-CN"

// 查找 emoji
em.Search([]string{"bug"}, 5)
em.FindOne("feat", "new")

// 转换为 emoji
em.CodeToEmoji(":bug:")      // 🐛
em.NameToEmoji("bug")        // 🐛
em.RenderCodes(":art: fix")  // 🎨 fix
```

### 辅助函数

```go
// 输出处理
gitw.FirstLine(output)       // 首行
gitw.OutputLines(output)     // 按行分割

// 错误处理
gitw.MustString(s, err)      // panic 或返回字符串
gitw.MustStrings(ss, err)    // panic 或返回 []string

// 仓库检查
gitw.IsGitDir("/path")       // 是否 git 仓库
gitw.HasDotGitDir("/path")   // 是否包含 .git 目录

// 配置
gitw.Config("user.name")     // 获取配置
gitw.Editor()                // 获取编辑器
```

## GitWrap 支持的命令

```go
Add, Annotate, Apply, Bisect, Blame, Branch, Checkout, CherryPick, Clean
Clone, Commit, Config, Describe, Diff, Fetch, Grep, Init, Log, Merge, Mv
Pull, Push, Rebase, Reflog, Remote, Reset, Restore, Revert, RevList, RevParse
Rm, ShortLog, Show, Stash, Status, Switch, Tag, Var, Worktree
```

## 进阶配置

```go
// 调试模式
gitw.SetDebug(true)

// 全局参数
gitw.GlobalFlags = []string{"-c", "core.autocrlf=false"}

// 预设命令
gitw.PrintCmdline()  // 打印命令
gitw.WithDryRun(true) // 模拟执行
```

## 相关文档

- [Changelog 生成](changelog.md)
