# reflects, structs, jsonutil, errorx, dump

## reflects

Extended reflection helpers (`github.com/gookit/goutil/reflects`).

```go
reflects.IsEqual(a, b)                    // deep value equality incl. numeric-kind handling
reflects.IsNil(rv); IsEmpty(rv); IsEmptyReal(rv); IsFunc(v); CanBeNil(typ); IsValidPtr(rv)
reflects.Indirect(rv); Elem(rv); TypeReal(typ); TypeElem(typ)  // strip ptr/interface
reflects.Len(rv)                          // -1 when kind has no length
reflects.ToString(rv) (string, error)     // String(rv) ignores error
reflects.ConvToType(val, typ) (reflect.Value, error); ConvToKind(val, kind)
reflects.SetValue(rv, val) error          // set with conversion; SetUnexportedValue(rv, v)
reflects.Call(fn, args, opt) / SafeCall(fn, args)
reflects.ValueOf(v) Value                 // wrapper with Int()/Uint()/Elem()/Indirect()/BKind()
reflects.TypeOf(v) Type                   // wrapper over reflect.Type
reflects.NewFunc(fn) *FuncX               // reflect-based func caller
```

## structs

Tag parsing, defaults, struct <-> map. Default tag name for `ToMap`, `SetValues`, `BindData` is **`json`**; `Wrapper` Get/Set use the Go field name.

```go
type Conf struct {
	Name string        `json:"name" default:"tom"`
	Wait time.Duration `default:"10s"`
	Env  string        `default:"${APP_ENV}"`
	Tags []string      `default:"a,b"`
}
c := &Conf{}
structs.InitDefaults(c)                       // alias: structs.Init; only string/bool/intX/uintX/floatX/array/slice
structs.InitDefaults(c, func(o *structs.InitOptions) { o.ParseEnv = true; o.ParseTime = true }) // ${ENV}, duration/time

mp := structs.ToMap(c)                        // keys from json tag: {"name": "tom", ...}
structs.ToMap(c, structs.WithMapTagName("yaml"))  // another tag; no tag -> field name
structs.TryToMap(c) / MustToMap / ToSMap / ToString
structs.ToMap(c, structs.WithIgnoreEmpty)     // skip empty values (MapOptFunc taking *MapOptions)

structs.SetValues(c, map[string]any{"name": "bob"})   // keyed by json tag; BindData is the same family
structs.BindData(c, data, structs.WithParseDefault)

tags, _ := structs.ParseTags(c, []string{"json"})     // map[field]SMap{"json": "name"}

w := structs.Wrap(c)                          // Wrapper: by Go FIELD name (verified)
w.Set("Name", "z"); w.Get("Name"); w.Lookup("Name")

d := structs.NewData(); d.Set("a", 1); d.Get("a"); d.IntVal("a")  // simple (optionally locked) data bag
```

Also `structs.Aliases`, `structs.SMap`, `structs.OrderedData`, `structs.TagParser`.

## jsonutil

```go
jsonutil.Encode(v) ([]byte, error)           // compact (json.Marshal)
jsonutil.EncodePretty(v); Pretty(v) (string, error); MustPretty(v)  // indented 4 spaces
jsonutil.EncodeString(v) (string, error)     // NOTE: indented, despite the name
jsonutil.MustString(v)
jsonutil.Decode(bts, &ptr); DecodeString(str, &ptr); DecodeFile(path, &ptr); DecodeReader(r, &ptr)
jsonutil.ReadFile(path, &ptr); WriteFile(path, data); WritePretty(path, data)
jsonutil.IsJSON(s); IsObject(s); IsArray(s); IsJSONFast(s)
jsonutil.StripComments(src)                  // remove // and /* */ comments (string literals kept)
jsonutil.Mapping(src, dst)                   // map/struct -> struct via json tags
```

## errorx

Errors with call stacks and wrapping. `%+v` prints the stack; `Error()` is the message chain joined with `"; "`.

```go
errorx.New("msg")                 // with stack      errorx.Newf / Errorf / Ef(...) variants
errorx.Raw("msg"); Rawf(...)      // plain errors.New (no stack)
errorx.Wrap(err, "ctx")           // keep chain, NO stack      Wrapf(err, tpl, args...)
errorx.WithPrev(err, "ctx")       // keep chain + stack (alias With); WithPrevf / Withf
errorx.WithStack(err)             // stack only; copies the message and DROPS the original chain
errorx.Is(err, target); Has(err, target); As(err, &t); Cause(err); Unwrap(err)
errorx.ToErrorX(err) (*ErrorX, bool); ex.StackString(); ex.Location()
errorx.IsTrue(cond, "must be true %d", 1) error   // nil when cond is true; IsFalse, IsIn, NotIn
errorx.Config(errorx.SkipDepth(2), errorx.TraceDepth(10))  // global stack options
```

Example: `e := errorx.Wrap(base, "ctx")` gives `"ctx; base"` and `errors.Is(e, base) == true`; `errors.Is(errorx.WithStack(base), base) == false`.
Also: `errorx.ErrorR` / `Fail(code, msg)` / `Suc(msg)` for result-style errors with a code; `errorx.Errors` / `ErrorM` multi-error collections.
`errorx.New` returns plain `error`; use `errorx.ToErrorX(err)` to get the `*ErrorX`. `errorx.WrapR` does not exist.

## dump

Pretty debug printer: shows type, length and the caller position (`PRINT AT pkg.Func(file:line)`).

```go
import "github.com/gookit/goutil/dump"

dump.P(v1, v2)                // like fmt.Println, colored, with caller position  (`dump.Print` is identical; `V`/`Println` are variants on the same std dumper)
dump.NoLoc(v)                 // no caller position   (Clear: same)
s := dump.Format(v)           // returns string instead of printing
dump.Fprint(w, v)             // to a writer
dump.Config(dump.WithoutPosition(), dump.WithoutColor(), dump.SkipNilField(), dump.SkipPrivate(), dump.BytesAsString())
dump.Reset()                  // restore std dumper defaults
d := dump.NewWithOptions(dump.WithoutOutput(w)); d.Print(v)
```

Options available: `WithoutColor WithoutPosition WithoutType WithoutLen WithCallerSkip SkipNilField SkipPrivate BytesAsString WithoutOutput(writer)`.
