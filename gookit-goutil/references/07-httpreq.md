# netutil/httpreq: HTTP client

`github.com/gookit/goutil/netutil/httpreq` (not `goutil/httpreq`). Thin wrapper over `net/http`; all send functions return the raw `*http.Response` (close its body yourself) and `error`.

## Package-level functions

```go
import "github.com/gookit/goutil/netutil/httpreq"

resp, err := httpreq.Get(url)                                           // also Delete, Send(method, url, optFns...)
resp, err = httpreq.Get(url, httpreq.WithData(map[string]string{"a": "1"}))   // non-body methods (anything but POST/PUT/PATCH): data -> query string (?a=1)
resp, err = httpreq.Post(url, `{"name":"x"}`, httpreq.WithJSONType)     // data: string | []byte | io.Reader | map | struct...
resp, err = httpreq.PostJSON(url, map[string]string{"k": "v"})          // marshals data as JSON
resp, err = httpreq.Put(url, data)
```

Not present: `httpreq.Patch`, `NewRequest`, `NewJSONRequest`, `NewFormRequest`, `NewMultipartRequest`, `IsSuccess` (use `IsSuccessful(statusCode)`).

Options (`OptionFn = func(opt *Option)`): `httpreq.WithJSONType`, `httpreq.WithData(data)`, or a closure:

```go
httpreq.Get(url, func(o *httpreq.Option) {
	o.HeaderMap = map[string]string{"Authorization": "Bearer x"}
	o.Timeout = 3000 // ms
})
```
`Option` fields: `Timeout(ms) Method HeaderMap ContentType Logger Context Data Body`.

## Client

```go
cli := httpreq.New("http://api.example.com")            // base URL; also NewWithTimeout(ms), NewClient(ms), Std()
cli.DefaultHeader("X-App", "demo").SetTimeout(3000).OnBeforeSend(func(r *http.Request) {...})

resp, err := cli.Get("/users")
resp, err = cli.Post("/users", `{"name":"x"}`, httpreq.WithJSONType)
resp, err = cli.PostJSON("/users", map[string]string{"k": "v"})

// builder style: *Client.JSONBody/FormBody/StringBody/BytesBody return *Option which has Send/Get/Post/Put/Delete
resp, err = cli.JSONBody(payload).WithHeader("X-A", "1").Send("PUT", "/users/1")
```

Gotcha: `opt.Post(url, data)` takes its own `data` and replaces a body set earlier by `JSONBody(...)` (passing `nil` sends an empty body). When the body is already set on the option, call `Send(method, url)`.

## Response helper

```go
rx := httpreq.NewResp(resp)                 // *RespX;  WrapResp(cli.Get(...)) (*RespX, error);  MustRespX
rx.IsOk(); rx.IsSuccessful(); rx.IsFail()   // status checks
rx.BodyString()                             // body as string (buffered)
var out T; rx.BindJSON(&out); rx.BindJSONOnOk(&out)
rx.ContentType()
httpreq.ResponseToString(resp)              // debug dump of a raw response; RequestToString(req)
```

## Utils

`httpreq.IsOK/IsSuccessful/IsRedirect/IsClientError/IsServerError/IsNotFound(statusCode)`, `MakeQuery(data) url.Values`, `AppendQueryToURLString(url, values)`, `BuildBasicAuth(user, pwd)`, `HeaderToStringMap(h)`, `ParseAccept(h)`. Content-type constants: package `netutil/httpctype`; header names: `netutil/httpheader`; extra HTTP helpers: `netutil/httpex`.
For tests use `testutil.NewEchoServer()` or `net/http/httptest` (see 01-testing-assert.md).
