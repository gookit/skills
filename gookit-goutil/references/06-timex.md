# timex: enhanced time

`github.com/gookit/goutil/timex`: `*timex.Time` wraps `time.Time` (embedded, so `Unix()`, `In()`, `Before()` etc. still work) and adds helpers plus PHP-like date templates.

## Create

```go
tx := timex.Now()                       // also New(t), FromTime(t), Wrap(t), FromUnix(sec), Local(), LocalByName("Asia/Shanghai")
tx, err := timex.FromString("2022-04-20 19:40:34")                 // auto layout; parsed in LOCAL time zone
tx, err = timex.FromString("2022-04-20", "2006-01-02")             // explicit layout
tx, err = timex.FromDate("2022-04-20 19:40:34", "Y-m-d H:I:S")     // template instead of layout
```

## Methods (each returns a new `*Time`)

```go
tx.Yesterday(); tx.Tomorrow(); tx.DayAgo(2); tx.DayAfter(2)
tx.DayStart(); tx.DayEnd(); tx.HourStart(); tx.HourEnd()          // 00:00:00 / 23:59:59 ...
tx.AddDay(1); AddHour(1); AddMinutes(15); AddSeconds(30); AddDur(d); AddString("1h30m"); SubDay/SubHour/SubMinutes/SubSeconds
tx.Datetime()                    // "2006-01-02 15:04:05" (optional layout arg)
tx.DateFormat("Y-m-d"); tx.TplFormat(tpl); tx.Format(goLayout)
tx.IsBefore(u); IsAfter(u); IsBeforeUnix(ts); IsAfterUnix(ts); Diff(u); DiffSec(u); Timestamp(); T() time.Time
tx.HowLongAgo(before)
```

## Functions on `time.Time` / values

```go
timex.Datetime(t); Date(t, "Y-m-d"); DateFormat(t, tpl); FormatByTpl(t, tpl); FormatUnix(sec); FormatDuration(d)
timex.DayStart(t); DayEnd(t); HourStart(t); AddDay(t, n); NowAddDay(1); NowUnix(); TodayStart(); TodayEnd(); NowHourStart()
timex.ToTime(s, layouts...) (time.Time, error)            // alias strutil.ToTime (local zone)
timex.ToDuration("1h30m"); ParseDuration(s); IsDuration(s)
timex.FromNow(t)  // "2 hours ago"      timex.Elapsed(start, end) // "1.50mins"      HowLongAgo(sec)
timex.InRange(t, start, end)
start, end, err := timex.ParseRange("-1h~0", nil)          // relative range; keywords: today yesterday tomorrow now
timex.SetLocalByName("Asia/Shanghai")
```

## Date template characters

`timex.ToLayout("Y-m-d H:I:S")` -> `"2006-01-02 15:04:05"`. Note **`I` = minutes, `S` = seconds** (not PHP's `i`/`s`, which mean unpadded).

| Char | Meaning | Char | Meaning |
|---|---|---|---|
| `Y` / `y` | 2006 / 06 | `H` | 24h hour `15` |
| `m` / `n` | 01 / 1 | `h` / `g` | 12h hour `03` / `3` |
| `d` / `j` | 02 / 2 | `I` / `i` | minute `04` / `4` |
| `M` / `F` | Jan / January | `S` / `s` | second `05` / `5` |
| `D` / `l` | Mon / Monday | `a` / `A` | pm / PM |
| `v` / `u` | ms `000` / µs `000000` | `c` / `r` | RFC3339 / RFC1123Z |

Constants: `timex.DefaultTemplate = "Y-m-d H:I:S"`, `TemplateWithMs3`, `TemplateWithMs6`, `DatetimeLayout`.
Not present: `timex.Today()`, `Tomorrow()`, `Yesterday()` as package functions (they are `*Time` methods), `timex.Parse`, `FromDateTime`.
