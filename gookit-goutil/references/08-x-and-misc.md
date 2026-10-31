# x/* packages, syncs, netutil, comdef

Extras live under `github.com/gookit/goutil/x/<name>`. List: `go doc -short github.com/gookit/goutil/x/<name>`. Only signatures confirmed by `go doc` are listed.

| Package | Purpose and key API |
|---|---|
| `x/assert` | test assertions, see [01](01-testing-assert.md) |
| `x/fakeobj` | fakes for tests: `NewDirEntry`, `NewFileInfo/NewFile`, `NewWriter/NewBuffer`, `NewReader/NewStrReader`, `NewClock` |
| `x/finder` | file/dir finder (`finder.NewFinder().AddScan(dir).ExcludeDir(..).Exclude(finder.MatchSuffix("_test.go")).FindPaths()`); full guide in skill `gookit-finder` |
| `x/ccolor` | colored output, see [04](04-fs-sys-env-cli.md) |
| `x/termenv` | `IsTerminal()`, `IsSupportColor/256/TrueColor()`, `GetTermSize()`, `NoColor()`, `DisableColor()`, `ReadPassword(q...)`, `CurrentShell(onlyName)` |
| `x/fmtutil` | `DataSize(uint64)` / `HumanSize` (bytes -> text), `ParseByte(str)`, `FormatDuration`, `PrettyJSON(v)`, `HowLongAgo(sec)` |
| `x/goinfo` | `GoVersion()`, `FuncName(fn)`, `GetCallerInfo(skip)`, `GetCallersInfo(skip, max)`, `OsGoInfo()`, `ParseGoVersion(line)` |
| `x/basefn` | generic helpers re-exported by the root: `Must[T](v, err)`, `MustOK`, `PanicIf`, `PanicErr`, `OrValue`, `OrReturn`, `CallOn`, `FirstOr` |
| `x/ptr` | pointers: `ptr.Of(v)` (generic), `ptr.String/Int/Bool` |
| `x/obox` | tiny named-dependency container: `obox.Set(name, val, opts...)`, `Get[T](name)`, `MustGet[T]`, `Has`, `Delete`, `Reset`; options `Lazy(factory)`, `Transient()` |
| `x/clipboard` | `clipboard.WriteString(s)`, `ReadString()`, `Available()` (uses the OS clipboard tools) |
| `x/stdio` | IO helpers: `NewIOReader(in)`, `NewScanner(in)`, `ReadString(r)`, `SafeClose(c)`, `WriteString(s)`, `Writeln(s)` |
| `x/clog` | leveled colored logger: `clog.Info/Warn/Error/Debug/Success/Trace`, `Infof`, `SetOutput(w)`, `SetTemplate(tpl)` |
| `x/encodes` | `B64Encode/B64Decode`, `B32Encode/B32Decode`; sub-packages `x/encodes/hashutil`, `x/encodes/secutil` |

Relocation note: the old README lists `encodes`, `finder`, `fmtutil`, `goinfo`, `clipboard`, `fakeobj`, `assert` as top-level names; the import paths are all under `x/` now.

## syncs

```go
import "github.com/gookit/goutil/syncs"

eg := syncs.NewErrGroup(4)            // limit concurrency; NewCtxErrGroup(ctx, limit...)
eg.Go(func() error { return nil }); eg.Add(fn1, fn2); err := eg.Wait()
err = syncs.Go(fn)                     // runs fn in a goroutine, waits; panic -> returned error
syncs.WaitCloseSignals(onClose)        // block until SIGINT/SIGTERM
sm := syncs.NewSafeMap[string, int]()  // generic concurrent map
```

(`goutil.SafeGo(fn, errHandler)` / `goutil.SafeRun(fn)` in the root package cover simple recover cases.)

## netutil

`netutil.IPv4()`, `InternalIPv4()`, `GetLocalIPs()`, `AllLocalIPv4()`, `FreePort()`, `FirstMacAddr()`, `HostIP()`; subpackages `httpreq`, `httpctype`, `httpheader`, `httpex`.

## strutil subpackages / sysutil subpackages

- `strutil/textutil`: text replace helpers; `strutil/textscan`: text scanner for INI/Properties-like formats.
- `sysutil/cmdr` (`cmdr.NewCmd`, batch tasks), `sysutil/process`, `sysutil/checkenv`; `cliutil/cmdline`.

## comdef

Constraint types for generics: `ScalarType`, `Integer`, `Int`, `Uint`, `Float`, `Number`, `NumberOrString`, `SimpleType`, `SortedType`, `Compared`; function types `MatchFunc[T]`, `StringMatchFunc`, `StringHandleFunc`; `Align` (`comdef.Left`...), `Serializer/Codec` interfaces.
