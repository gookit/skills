# fsutil, sysutil, envutil, cliutil, ccolor

## fsutil: files and paths

```go
import "github.com/gookit/goutil/fsutil"

// check
fsutil.IsFile(p); IsDir(p); PathExists(p) (FileExists/DirExist are aliases); IsAbsPath(p); IsEmptyDir(p); IsSymlink(p); IsImageFile(p)
// read  (NOTE: ReadFile / ReadString / MustReadFile PANIC when the file is missing)
fsutil.ReadOrErr(p) ([]byte, error)      // safe; arg may also be an io.Reader
fsutil.ReadFile(p) []byte                // panics on error
fsutil.ReadString(p) string              // panics on error
fsutil.ReadExistFile(p) []byte           // empty when file does not exist
// write  (data: string | []byte | io.Reader; dirs auto-created)
fsutil.SaveFile(p, "text")               // error; options: fsutil.WithFlag(f), fsutil.WithPerm(m)
fsutil.PutContents(p, "more", fsutil.FsCWAFlags)  // (n int, err); default flag truncates, FsCWAFlags appends
fsutil.WriteFile(p, data, 0644, flags...)
fsutil.UpdateContents(p, func(bs []byte) []byte { return bs })   // read-modify-write
fsutil.MustSave(p, data); fsutil.Must2(fsutil.PutContents(p, "x"))
// dirs / copy / remove
fsutil.MkdirQuick(dir) // 0755      fsutil.MkParentDir(file)    fsutil.MkDirs(perm, d1, d2)    fsutil.EnsureDir(dir)
fsutil.CopyFile(src, dst); fsutil.Remove(p); fsutil.RmIfExist(p); fsutil.QuietRemove(p); fsutil.MustRemove(p)
// names
fsutil.Name("a/b.txt")      // "b.txt"      NameNoExt -> "b"      Suffix/FileExt -> ".txt"      Extname -> "txt"
fsutil.Dir(p); JoinPaths(a, b...); UnixPath(p); Expand("~/x"); Realpath(p); HomeDir()
// search / walk
fsutil.Glob("dir/*.go"); FirstExists(p1, p2...); SearchNameUp(startDir, ".git") // dir that contains the name
fsutil.FindInDir(dir, func(fp string, ent fs.DirEntry) error {...}, fsutil.OnlyFindFile, fsutil.ExcludeSuffix(".log"))
fsutil.WalkDir(dir, fn); DetectMime(p); Unzip(archive, dst)
```

Not present: `ReadLines`, `AppendFile`, `MoveFile`, `Rename`, `FileSize`, `ModTime`, `RemoveAll` (use `SafeRemoveAll`), `Search`, `WithMode`. For rich lookups use `x/finder` (skill `gookit-finder`).

## sysutil: system and exec

```go
import "github.com/gookit/goutil/sysutil"

out, err := sysutil.ExecCmd("ls", []string{"-al"}, workDir...)  // combined output
out, err = sysutil.QuickExec("git status", workDir...)           // splits a simple command line
out, err = sysutil.ShellExec("echo $((1+1))", "sh")              // run via shell (default shell when omitted)
sysutil.HasExecutable("git"); FindExecutable("git"); Executable("git")
sysutil.IsWin(); IsLinux(); IsMac(); IsWSL(); IsMSys(); IsTerminal(fd); StdIsTerminal()
sysutil.HomeDir(); Workdir(); BinDir(); BinName(); Hostname(); CurrentShell(true)
sysutil.UserConfigDir("app"); UserCacheDir("app"); ExpandPath("~/x")
sysutil.ProcessExists(pid); Kill(pid, syscall.SIGTERM); OpenURL(url); OpenBrowser(url)
sysutil.Getenv(name, def...); Environ()
sysutil.NewCmd("git", "status")   // *cmdr.Cmd builder (subpackage sysutil/cmdr; also sysutil/process, checkenv)
```

Not present: `CurrentPID`, `ParentPID`, `Username` (use `os.Getpid`, `os.Getppid`, `sysutil.CurrentUser().Username`).

## envutil: environment

```go
envutil.Getenv("NAME", "default"); GetInt("PORT", 8080); GetBool("DEBUG"); MustGet("NAME"); HasEnv("NAME")
envutil.GetOne([]string{"A", "B"}, "def")      // first set name wins
envutil.SetEnvs("K1", "v1", "K2", "v2"); UnsetEnvs("K1"); SetEnvMap(map)
envutil.VarParse("${HOME}/bin")                // expand ${VAR} / $VAR (alias ParseValue, VarReplace)
envutil.DotenvLoad(func(c *envutil.Dotenv) { c.Files = []string{".env", ".env.local"}; c.BaseDir = dir; c.IgnoreNotExist = true })
envutil.LoadEnvFiles(baseDir, ".env")          // also LoadText / LoadString
envutil.IsWin(); IsLinux(); IsMac(); IsMSys(); IsSupportColor(); IsGithubActions()
```

By default an OS env value wins over the dotenv value (`Dotenv.DotenvFirst=false`). Not present: `envutil.Get/Set/Unset/Setenv/GoVersion/IsDocker`.

## cliutil: CLI output and input

```go
cliutil.Infoln("..."); Successln(); Warnln(); Errorln(); Infof("x %d\n", 1); Redln(); Greenp()  // colored print
cliutil.Confirm("Continue?", true) bool        // prompt, default yes
cliutil.ReadInput("Name: ") (string, error); ReadLine; ReadInt; ReadPassword("pwd: ")
cliutil.ShowTable([]string{"id", "name"}, [][]any{{1, "tom"}})   // prints; FormatTable(...) returns string
cliutil.NewTableBuilder(style).Format(cols, rows)
cliutil.ParseLine(`git commit -m "x y"`)       // -> []string (shell-like split); BuildLine(bin, args)
cliutil.ExecLine("echo hi"); ExecCmd; ShellExec; QuickExec
cliutil.GetTermSize() (w, h)
```

Subpackage `cliutil/cmdline` has `NewParser(line)` / `NewBuilder(bin, args...)` for command line parse/build.

## x/ccolor: colored output (ANSI)

```go
import "github.com/gookit/goutil/x/ccolor"

ccolor.Println("<green>ok</> <red>bad</>")        // tag syntax: <tag>text</>
ccolor.Print("<info>hi</>\n"); ccolor.Infoln("x"); Successln; Warnln; Errorln
ccolor.Red.Sprint("x"); ccolor.Green.Sprintf("%d", 1)  // Color constants (Fg*/Bg*/Op*)
ccolor.Sprintf("<red>%s</>", s); ccolor.ClearTag("<red>x</>") // "x"; ClearCode strips raw ANSI
ccolor.Disable(); ForceEnableColor(); IsSupportColor()
```

`ccolor` is a trimmed copy of `gookit/color`; for the full library use `github.com/gookit/color`. Terminal capability detection lives in `x/termenv`.
