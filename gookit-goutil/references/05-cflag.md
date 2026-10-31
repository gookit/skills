# cflag: enhanced flag parser (and cflag/capp)

`github.com/gookit/goutil/cflag` wraps `flag.FlagSet`: required options, short aliases, named positional args, validators, options allowed before or after args, pretty help. Multi-command apps: `github.com/gookit/goutil/cflag/capp`.

## Single command

```go
import "github.com/gookit/goutil/cflag"

var name string; var age int
c := cflag.NewWith("demo", "0.1.0", "a demo command") // or cflag.New(func(c *cflag.CFlags){ c.Desc = "..." })
c.StringVar(&name, "name", "", "user name;true;n")    // usage string: "desc;required;shorts"
c.IntVar(&age, "age", 0, "age;;a,ag")                 // not required; -a / -ag shortcuts
c.AddArg("path", "input path", true)                  // named positional arg (name, desc, required, [default, arrayed])
c.AddArg("extras", "more", false, nil, true)          // arrayed arg must be last

c.Func = func(c *cflag.CFlags) error {                // run body
	fmt.Println(name, age, c.Arg("path").String(), c.RemainArgs())
	return nil
}
c.MustParse(nil)  // nil = os.Args[1:]; Parse(args) returns error; MustRun(args) = parse + Func; QuickRun()
```

Facts verified in tests:
- Usage-string format: `desc` / `desc;required` / `desc;required;shorts` / `desc{[required;shorts]}` (the braces form keeps `;` in the description). `required` accepts `true,on,yes`.
- Missing required option: `Parse` returns `flag option 'name' is required`.
- `RemainArgs()` returns only args **not bound** by `AddArg`.
- Options may come before or after positional args (`demo p1 --name tom`), `--` stops option parsing.
- Other: `c.AddShortcuts(name, shorts...)`, `c.AddValidator(name, func(v any) error)`, `cflag.LimitInt(min, max)`, `cflag.NewEnumString(...)`, repeatable types `cflag.Ints/Strings/Booleans`, `cflag.KVString`, `c.ShowHelp()`.
- `cflag.Debug` / `cflag.SetDebug(true)` or env `CFLAG_DEBUG=1` prints parse debug.

## Multi-command app (capp)

```go
import "github.com/gookit/goutil/cflag/capp"

app := capp.NewApp()                      // or capp.NewWith(name, version, desc)
app.Name, app.Desc, app.Version = "myapp", "my cli", "1.0.0"
app.StringVar(&workdir, "workdir", "", "global option;;w")  // global options: only BEFORE the command name

cmd := capp.NewCmd("demo", "demo command")
cmd.IntVar(&age, "age", 0, "age;;a")
cmd.AddArg("arg1", "first arg", true, nil)
cmd.Func = func(c *capp.Cmd) error { fmt.Println(c.Arg("arg1").String()); return nil }
app.Add(cmd)
app.Run()                                 // os.Args;  app.RunWithArgs([]string{"demo", "v0", "--name", "tom"})
```

Two-level groups: `group := capp.NewCmd("session", "..."); list := capp.NewCmd("list", "...", fn); list.Aliases = []string{"ls"}` (set aliases **before** `Add`); `group.Add(list); app.Add(group)`. Group options go before the sub-command name; a group cannot declare positional args. `cmd.OnAdd = func(c *capp.Cmd){...}` can declare flags lazily; `capp.WithAliases(...)` is a `CmdOptionFn`.
