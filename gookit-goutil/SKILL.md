---
name: gookit-goutil
description: Guide for github.com/gookit/goutil (v0.8.x), a Go utility library covering slices, strings, maps, structs, reflection, JSON, errors, files, system/env, CLI, time, HTTP client and Go test assertions. Use when writing or reviewing Go code that imports gookit/goutil, when writing Go tests with github.com/gookit/goutil/x/assert (assert.Eq, assert.Require, assert.NoErr), or when choosing between goutil/x/assert, testutil/assert and github.com/gookit/assert.
---

# gookit/goutil

Go utility library (module `github.com/gookit/goutil`, go.mod `go 1.19`, generics-based). Install: `go get github.com/gookit/goutil`.
Docs: <https://pkg.go.dev/github.com/gookit/goutil>. This skill was checked against HEAD `8d1f873` (v0.8.6).

**Before using a function, confirm it exists**: `go doc github.com/gookit/goutil/strutil | rg Camel` (or `go doc -short <pkg>`). Do not guess names from other languages' utility libs; many plausible names do NOT exist (e.g. `strutil.IsEmail`, `strutil.Snake`, `mathutil.Sum/Avg`, `fsutil.ReadLines`, `timex.Today`).

## Package map (verified import paths)

| Import path | What | Reference |
|---|---|---|
| `goutil` (root) | `IsEmpty/IsEqual/Contains`, `String/Int/ToInt`, `Must`, `PanicIf`, `SafeRun`, `OrValue` | [02](references/02-data-basics.md) |
| `arrutil` `strutil` `maputil` `mathutil` `byteutil` | slice / string / map / number / bytes helpers | [02](references/02-data-basics.md) |
| `reflects` `structs` `jsonutil` `errorx` `dump` | reflection, struct tags/defaults/map, JSON, stacked errors, pretty debug print | [03](references/03-reflect-struct-json-error-dump.md) |
| `fsutil` `sysutil` `envutil` `cliutil` `cflag` | files, exec/system, env + dotenv, CLI IO/table, flag parser | [04](references/04-fs-sys-env-cli.md), [05](references/05-cflag.md) |
| `timex` | enhanced `time.Time` + PHP-style date templates | [06](references/06-timex.md) |
| `netutil/httpreq` | HTTP client and helpers | [07](references/07-httpreq.md) |
| **`x/assert`** | **Go test assertions** | [01](references/01-testing-assert.md) |
| `testutil` | env/stdout mocks, HTTP mock, echo server | [01](references/01-testing-assert.md) |
| `x/ccolor` `x/finder` `x/fakeobj` `x/fmtutil` `x/goinfo` `x/ptr` `x/clipboard` `x/obox` `x/clog` `x/stdio` `x/termenv` `x/basefn` `x/encodes`, `syncs`, `netutil`, `comdef` | extras | [08](references/08-x-and-misc.md) |

Layout note: newer extras live under `x/` (`github.com/gookit/goutil/x/<name>`). Old root paths such as `goutil/assert`, `goutil/fakeobj`, `goutil/ccolor`, `goutil/testutil/assert` do not exist or are deprecated shims; always use the `x/` path. File finder has its own skill: `gookit-finder`.

## Testing: use `x/assert`

```go
import "github.com/gookit/goutil/x/assert"   // NOT testutil/assert (deprecated shim)

func TestFoo(t *testing.T) {
	got, err := Foo()
	assert.Require(t, assert.NoErr(t, err)) // stop THIS test now if err != nil
	assert.Eq(t, "want", got.Name)          // argument order: (t, want, give)
}
```

Key rules (details and full function list in [01](references/01-testing-assert.md)):
- Assertions return `bool` and, on failure, call `t.Error` and **continue** (unless `assert.SetFailFast(true)`).
- Stop the current test: `assert.Require(t, assert.Xxx(t, ...))` (alias `assert.Must`). Verified to exist; `Require(t, condition bool, fmtAndArgs ...any)` calls `t.FailNow()` when `condition` is false. The inner assertion already logged the real failure, so you will see a second "Required" entry.
- Group cases with `t.Run(name, func(t *testing.T) {...})` and use the **inner** `t` in assertions.
- `assert.Eq` compares by value+type (`Eq(uint(1), int(1))` fails; use `EqInt`); floats compare with delta 0.009.
- Import-path answer: use `github.com/gookit/goutil/x/assert`. `github.com/gookit/assert` is a separate zero-dependency module copied from goutil; use it only in projects that must not depend on goutil.

## Common recipes

```go
arrutil.Unique([]int{1, 2, 1})                          // [1 2]
strutil.CamelCase("user_name")                          // "userName"
maputil.GetByPath("a.b[1]", mp)                         // (val, ok)
structs.InitDefaults(&cfg)                              // from `default:"..."` tags
fsutil.SaveFile(path, "text")                           // auto-creates dirs
sysutil.QuickExec("git status")                         // (combined output, err)
errorx.Wrap(err, "load config")                         // keeps chain, errors.Is works
dump.P(v)                                               // pretty debug print with caller position
```

## Gotchas found while verifying

- `strutil.ReplaceVars` uses `{name}` (single braces).
- `mathutil.DataSize(1024)` -> `"1.00K"` (no `B`).
- `jsonutil.EncodeString` returns **indented** JSON (use `jsonutil.Encode` for compact bytes).
- `errorx.WithStack(err)` copies only the message: `errors.Is(wrapped, err)` is false. Use `errorx.Wrap/WithPrev` to keep the chain; messages join with `"; "`.
- `structs.ToMap` / `SetValues` / `BindData` key by the `json` tag by default (`structs.WithMapTagName` to change); `structs.Wrap(v).Get/Set` take the Go **field name**.
- `fsutil.ReadFile/ReadString/MustReadFile` **panic** on a missing file (`ReadExistFile` returns empty for a missing file); use `fsutil.ReadOrErr(path)` for an `error`.
- `CFlags.RemainArgs()` excludes args already bound with `AddArg`.

## References

- [01-testing-assert.md](references/01-testing-assert.md): x/assert API, Require/Must, t.Run grouping, testutil, fakeobj
- [02-data-basics.md](references/02-data-basics.md): root, arrutil, strutil, maputil, mathutil, byteutil
- [03-reflect-struct-json-error-dump.md](references/03-reflect-struct-json-error-dump.md): reflects, structs, jsonutil, errorx, dump
- [04-fs-sys-env-cli.md](references/04-fs-sys-env-cli.md): fsutil, sysutil, envutil, cliutil, ccolor
- [05-cflag.md](references/05-cflag.md): cflag and cflag/capp
- [06-timex.md](references/06-timex.md): timex
- [07-httpreq.md](references/07-httpreq.md): netutil/httpreq
- [08-x-and-misc.md](references/08-x-and-misc.md): x/* packages, syncs, netutil, comdef
