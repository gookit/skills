# Data basics: goutil (root), arrutil, strutil, maputil, mathutil, byteutil

All examples below compile and pass against v0.8.6. List the full API with `go doc -short github.com/gookit/goutil/<pkg>`.

## goutil (root)

```go
import "github.com/gookit/goutil"

goutil.IsEmpty(nil); goutil.IsEqual([]string{"a"}, []string{"a"}); goutil.IsNil(v)
goutil.Contains([]string{"a", "b"}, "a")   // string substring / map key / slice element
goutil.String(23)  // "23"      goutil.Int("-2") // -2   (quiet: bad input -> zero value)
n, err := goutil.ToInt("12")               // also ToInt64/ToUint/ToUint64/ToBool/ToString
goutil.Must(strconv.Atoi("3"))             // generic: returns v, panics on err
goutil.PanicIf(cond, "fmt %d", 1); goutil.PanicIfErr(err); goutil.MustOK(err)
goutil.OrValue(cond, a, b); goutil.OrReturn(cond, fnA, fnB)
err := goutil.SafeRun(func() { panic("x") })  // recover panic -> error
goutil.SafeGo(fn, errHandler); goutil.Go(func() error {...})
goutil.NewErrGroup(limit...)  // alias of syncs.ErrGroup
```

These generic helpers mostly forward to `x/basefn`, `internal/checkfn`, `reflects`.

## arrutil: slices

Type helpers: `arrutil.Strings`, `arrutil.Ints[T]`, `SortedList[T]`.

```go
arrutil.In(2, []int{1, 2}); arrutil.NotIn(3, list)       // comdef.ScalarType
arrutil.StringsHas(ss, "a"); arrutil.IntsHas(ints, 1); arrutil.Contains(anySlice, v) // reflect-based
arrutil.IndexOf(2, []int{1, 2})                          // 1 (-1 if absent)
arrutil.Unique([]int{1, 2, 1})                           // [1 2]; StringsUnique for strings
arrutil.Chunk([]int{1, 2, 3}, 2)                         // [[1 2] [3]]
arrutil.Map1(list, func(i int) int { return i * 2 })     // map every elem
arrutil.Map(list, func(i int) (string, bool) {...})      // map + keep only ok==true
arrutil.Filter(list, func(i int) bool { return i > 1 }) // variadic MatchFunc
arrutil.Remove([]int{1, 2}, 2)                           // [1]
arrutil.Find(list, pred) (v, err)                        // ErrElementNotFound when missing
arrutil.ToMap(list, func(s string) (string, int) {...}); arrutil.CombineToMap(keys, vals)
cmp := arrutil.ValueEqualsComparer[int]
arrutil.Diff(a, b, cmp); arrutil.Intersects(a, b, cmp); arrutil.Union(a, b, cmp) // set ops need a Comparer
arrutil.ToStrings(anySlice) ([]string, error); arrutil.MustToStrings(v); arrutil.ToInt64s(v)
arrutil.StringsToInts(ss) ([]int, error); arrutil.StringsMap(ss, strings.ToUpper); arrutil.TrimStrings(ss)
arrutil.JoinSlice(",", 1, 2)   // "1,2"        arrutil.FirstNonEmptyString("", "x")
arrutil.Reverse(list)          // in place      arrutil.RandomOne(list)
```

## strutil: strings

```go
// checks
strutil.IsBlank(" "); IsEmpty(""); IsNumeric("12.5"); IsInt("12"); IsAlphabet(c byte)
strutil.HasOneSub(s, subs); ContainsOne(s, subs); ContainsAll(s, subs); IContains(s, sub) // case-insens.
strutil.HasPrefix/HasSuffix; HasOnePrefix(s, prefixes)
// case / naming
strutil.CamelCase("user_name")  // "userName"  (alias Camel)
strutil.SnakeCase("userName")   // "user_name"
strutil.UpperFirst/LowerFirst/Upper/Lower  // Title = strings.ToTitle (all caps, not "Title Case"), UpperWord upper-cases first letter of each word
// split / cut / join
strutil.Split("a,b", ","); SplitTrimmed(" a , b ", ","); SplitValid("a,,b", ",")  // drop empties
strutil.Strings("a,b") / Ints("1,2")     // split by "," (optional sep), convert
k, v := strutil.SplitKV("a=b", "=")      // also Cut -> (before, after, found); TrimCut
strutil.AfterFirst/BeforeFirst/AfterLast/BeforeLast(s, sep)
strutil.Join(",", "a", "b"); JoinAny(",", 1, 2)
// trim / pad / cut-off
strutil.Trim(s, cutset...); TrimLeft/TrimRight(s, cutset...)   // cutset is variadic strings
strutil.PadLeft("1", "0", 3) // "001"   PadRight("1", " ", 3)   Repeat("ab", 2)
strutil.Truncate("abcdefg", 5, "...") // "ab..."  (width incl. tail)   Substr(s, pos, length)
strutil.WordWrap(s, 80); TextWrap/WidthWrap; TextWidth(s); Utf8Width
// replace / template
strutil.ReplaceVars("hi {name}", map[string]string{"name": "tom"}) // single braces
strutil.Replaces(s, map[string]string{"_": "-"})
// convert (safe/quiet/or-default family)
strutil.ToString(v) (string, error); QuietString(v); SafeString(v)
strutil.SafeInt("12"); IntOr("x", 5); ToInt(s) (int, error); Int64Or; ToBool; ToTime(s, layouts...)
strutil.ToByteSize("1KB") (uint64, error); ToDuration("1m"); Bool("yes")
strutil.OrElse("", "def"); BlankOr(" ", "def")
// match / compare
strutil.GlobMatch("*.go", "a.go"); QuickMatch("a*", "abc"); PathMatch
strutil.VersionCompare("1.2.3", "1.2.0", ">")
// hash / random / ids
strutil.Md5(any) // 32-hex     ShortMd5     RandomChars(n)/RandomCharsV2/V3     UUIDv4() (string, error)
strutil.B64Encode/B64Decode; URLEncode/URLDecode; EscapeHTML; Indent(s, prefix)
```

Types: `strutil.Buffer` (= `byteutil.Buffer`), `strutil.Builder`, `strutil.Value`/`StrVal` (string type with `Int()`, `Bool()`, `Split()`, `OrElse()`), `strutil.Runes`.
Not present: `IsEmail`, `IsURL` (only `IsHttpURL` var), `Snake`, `Random`, `ContainsAny`; `Camel` is only an alias of `CamelCase` (lower camel).

## maputil: maps

```go
mp := map[string]any{"top": map[string]any{"arr": []any{1, 2}, "k": "v"}}
v, ok := maputil.GetByPath("top.arr[1]", mp)   // dot path + [idx] (also "top.arr.1"); (path, map) order
maputil.QuietGet(mp, "top.k"); maputil.DeepGet(mp, "top.k")
maputil.SetByPath(&mp, "top.new", 1)           // pointer to map, returns error
maputil.MakeByPath("a.b", 1)                   // {"a":{"b":1}}
maputil.Flatten(nested)                        // {"a.b": 1}
maputil.Keys(m) []string (any map)   maputil.TypedKeys(m) / TypedValues(m)   maputil.Values(m)
maputil.HasKey(m, k); HasAllKeys(m, k1, k2) (ok, missingKey); HasOneKey
maputil.SimpleMerge(src, dst); Merge1level(...); MergeStringMap(src, dst, ignoreCase)
maputil.ToStringMap(m) / ToAnyMap(any) / TryAnyMap / SliceToSMap("k", "v") / SliceToMap
maputil.Clone(m); Copy(dst, src); DeleteFunc(m, fn); HTTPQueryString(map)
```

Types: `maputil.Data` (=`Map`, `map[string]any` with `Get/Int/Str/Bool/Strings/Sub/GetByPath/SetByPath...`), `maputil.StrMap`/`SMap`/`SM` (`map[string]string` with `Int/Bool/Strings...`), `maputil.Aliases`, `L2StrMap`.
Not present: `maputil.Merge`, `ToSMap`.

## mathutil: numbers

```go
mathutil.Max(3, 5); Min(3, 5); Abs(-3)          // generics
mathutil.InRange(3, 1, 5); OutRange(9, 1, 5); Compare(3, 2, ">")   // ops: = != < <= > >= (word forms like "gt" also work)
mathutil.ToInt("12") (int, error); SafeInt("12"); QuietInt(v); IntOr("x", 7); MustInt(v)
mathutil.ToInt64/ToUint/ToFloat...; Int64Or; FloatOr
mathutil.Percent(1, 2)        // 50    mathutil.RandInt(1, 3)  // inclusive
mathutil.DataSize(1024)       // "1.00K"   (also FormatBytes, HowLongAgo(sec))
mathutil.InDelta(want, give, delta); StrInt("12"); Div/Mul -> float64
```

Not present: `Sum`, `Avg`. `Max/Min` take exactly two args.

## byteutil

```go
byteutil.SafeBytes("abc"); byteutil.String(b)/ToString(b) // string(b)
byteutil.Md5(v) []byte; byteutil.Random(n) ([]byte, error); byteutil.Cut(b, sepByte) (before, after, found); byteutil.FirstLine(b)
buf := byteutil.NewBuffer(); buf.WriteString("x"); buf.String()  // bytes.Buffer + Printf/Println/WriteAny/ResetGet
```

Also `ChanPool`, `StdEncoder` (hex/b64 encoders: `byteutil.HexEncoder`).

## comdef

Type constraints used across the API: `comdef.ScalarType`, `Integer`, `Number`, `Float`, `Compared`, `SortedType`, `NumberOrString`; plus `comdef.MatchFunc[T]`, `StringMatchFunc`, `Align`.
