# Testing: x/assert, testutil, fakeobj

## Which assert package?

| Path | Status |
|---|---|
| `github.com/gookit/goutil/x/assert` | **Canonical, newest, superset.** Use this. |
| `github.com/gookit/goutil/testutil/assert` | Deprecated compat shim that forwards to `x/assert` (doc: "Deprecated: use github.com/gookit/goutil/x/assert"). Do not use in new code. |
| `github.com/gookit/assert` (separate repo, v0.2.0) | Standalone module with **no goutil dependency**, code originally copied from goutil `testutil/assert`. Has `Require/Must` too, but lacks `Zero/NotZero/EqInt/EqFloat/InDelta/ContainsElemsAny/ErrHasMsg/New/DisableColor/HideFullPath/SetFailFast`; adds `StrEq`, `MockEnvValue/MockOsEnv/MockOsEnvByText`, `NewBuffer/NewSafeBuffer`. Choose it only when a project must not import goutil. |

Rule of thumb: inside any project that already uses (or may use) goutil, import `x/assert`.

## Basics

```go
import (
	"testing"
	"github.com/gookit/goutil/x/assert"
)

func TestUser(t *testing.T) {
	u, err := LoadUser(1)
	assert.Require(t, assert.NoErr(t, err)) // stop this test if it fails
	assert.NotNil(t, u)
	assert.Eq(t, "tom", u.Name)             // (t, want, give)
	assert.Contains(t, u.Tags, "admin", "user %d must be admin", u.ID) // optional message: fmt + args
}
```

- Every assertion: `func X(t TestingT, ..., fmtAndArgs ...any) bool`. `TestingT` needs `Helper()`, `Name() string`, `Error(...any)`, so `*testing.T`, `*testing.B`, `testing.TB` all work.
- On failure: logs `Test Name / Error Pos / Error Msg / User Msg` via `t.Error` and returns `false`; the test **keeps running**.
- Optional last args: `fmtAndArgs` = a message, or a format string + args.

## Stop the test on failure (verified)

```go
func Require(t TestingT, condition bool, fmtAndArgs ...any)   // calls FailNow when condition is false
func Must(t TestingT, condition bool, fmtAndArgs ...any)      // alias of Require
func FailNow(t TestingT, failMsg string, fmtAndArgs ...any) bool // log + t.FailNow() unconditionally
func SetFailFast(enable bool)                                 // global: every failed assertion calls FailNow
```

Pattern (this is the supported form of "wrap with Require"):

```go
assert.Require(t, assert.Eq(t, 1, got))   // inner Eq logs the real diff; Require then calls t.FailNow()
assert.Require(t, assert.NoErr(t, err), "setup failed")
```

Semantics checked with a fake `TestingT`: a failing inner assertion produces 2 `Error` entries (the diff, then `Required`) and one `FailNow`; a passing one produces none. `FailNow` needs `t` to implement `FailNow()` (true for `*testing.T`); otherwise it only logs. `Require` ends the goroutine of the current test/sub-test via `runtime.Goexit` (via `t.FailNow`), so call it from the test goroutine, not from spawned goroutines.

Global switches (affect all tests in the process; not goroutine-safe to flip in parallel tests): `assert.SetFailFast(true)`, `assert.DisableColor()`, `assert.HideFullPath()`, vars `ShowFullPath`, `EnableColor`, `FailFast`.

## Group cases with `t.Run`

```go
func TestAdd(t *testing.T) {
	tests := []struct {
		name       string
		a, b, want int
	}{
		{"zero", 0, 0, 0},
		{"pos", 1, 2, 3},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) { // shadow t: assertions bind to the sub-test
			assert.Eq(t, tt.want, Add(tt.a, tt.b))
		})
	}
}
```

A `Require` inside `t.Run` stops only that sub-test; siblings continue. Using the outer `t` inside the closure attributes failures to the parent: always use the inner `t`.

## Function list (all verified in `go doc ./x/assert`)

Bool / nil / empty:
`True False Nil NotNil Empty NotEmpty Zero NotZero`

Equality / compare (`Eq(t, want, give)`):
- `Eq Equal` (aliases), `Neq NotEq NotEqual` (aliases): value + type equality; **`Eq(uint(1), int(1))` and `Eq(int64(1), 1)` fail**; float `want` compares with delta 0.009
- `EqInt(t, want, give)` converts both to int64 first; `InDelta/EqFloat(t, want, give, delta float64)`
- `Lt Lte Gt Gte (t, give, bound any)` on int/uint/float
- `Same NotSame` (pointer identity), `IsType(t, wantTypeValue, give)`, `IsKind(t, reflect.Kind, give)`

Containers / strings (`Contains(t, src, elem)`: string=substring, map=key, slice/array=element):
`Contains NotContains ContainsKey NotContainsKey ContainsKeys NotContainsKeys (mp, keys any) ContainsElems[T] ContainsElemsAny Len(t, give, wantLen) LenGt StrContains StrNotContains StrContainsAll(t, s, subs []string) StrCount(t, s, sub, n)`

Errors:
`NoErr/NoError, Err/Error, ErrIs(t, err, target), ErrMsg(t, err, exactMsg), ErrSubMsg/ErrMsgContains/ErrHasMsg(t, err, subMsg)`

Panics (`fn` is `func()`):
`Panics NotPanics PanicsMsg(t, fn, wantVal) PanicsErrMsg(t, fn, errMsg)`

Files: `FileExists FileNotExists DirExists DirNotExists`

Control: `Fail(t, msg)` (log, continue), `FailNow(t, msg)`, `Require`, `Must`.

Chained style: `as := assert.New(t); as.Eq(1, 1).True(true).Contains("abc", "a"); as.IsOk()/IsFail()` (same names as the functions, minus `t`, returning `*Assertions`).

`assert.Buffer()` returns a `*byteutil.Buffer` helper.

There is no `StrEq`, `ElementsMatch`, `JSONEq`, `Equalf` or `NoErrorf` in `x/assert`; do not use testify names that are not in the list above. `ErrMsg` is an exact message match; `ErrIs` uses `errors.Is`; `Nil/NotNil` treat typed-nil pointers/maps/slices as nil.

## testutil (non-assert helpers)

```go
import "github.com/gookit/goutil/testutil"

testutil.MockEnvValue("APP_ENV", "dev", func(nv string) { /* env set, restored after */ })
testutil.MockOsEnv(map[string]string{"A": "1"}, func() { /* replaces whole env */ }) // alias MockCleanOsEnv
testutil.MockOsEnvByText("A=1\nB=2", func() {})

testutil.RewriteStdout()
fmt.Println("hi")
out := testutil.RestoreStdout()          // "hi\n"   (also RewriteStderr/RestoreStderr)

rr := testutil.MockRequest(handler, "POST", "/p", &testutil.MD{BodyString: "x", Headers: testutil.M{"X-A": "1"}})
rr.Body.String()                         // *httptest.ResponseRecorder

srv := testutil.NewEchoServer(); defer srv.Close() // httptest.Server echoing requests; srv.URL
testutil.SetTimeLocalUTC(); defer testutil.RestoreTimeLocal()
```

Also: `NewBuffer`, `NewSafeBuffer`, `NewTestWriter`, `DiscardStdout`, `NewHTTPRequest`, `SetOsEnvs/RevertOSEnv/ClearOSEnv`.
`t.TempDir()` from the stdlib is preferred over custom temp helpers (there is no `testutil.MkTestDir`).

## x/fakeobj

Fakes for fs interfaces and IO: `fakeobj.NewDirEntry(path, isDir...)`, `NewFile/NewFileInfo`, `NewWriter()/NewBuffer()` (writer with `String()`), `NewReader()/NewStrReader(s)`, `NewClock(value)`.
