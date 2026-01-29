# GoUtil - httpreq Package Reference

**Import**: `github.com/gookit/goutil/netutil/httpreq`

Easier-to-use HTTP client that wraps Go's `http.Client` with convenient methods and utilities.

## Table of Contents

- [Overview](#overview)
- [Basic Requests](#basic-requests)
- [Request Building](#request-building)
- [Response Handling](#response-handling)
- [Advanced Features](#advanced-features)
- [Complete Examples](#complete-examples)

---

## Overview

### Features

- Simple API for common HTTP methods
- Automatic JSON encoding/decoding
- Request and response middleware
- Timeout configuration
- Custom headers support
- Form data handling
- File upload support
- Response helpers

### Installation

```bash
go get github.com/gookit/goutil/netutil/httpreq
```

---

## Basic Requests

### GET Requests

```go
import "github.com/gookit/goutil/netutil/httpreq"

// Simple GET request
resp, err := httpreq.Get("https://api.example.com/users")
if err != nil {
    // Handle error
}
defer resp.Body.Close()

// Read response body
body, err := io.ReadAll(resp.Body)
```

### POST Requests

```go
// POST with JSON data
data := map[string]any{
    "name":  "John Doe",
    "email": "john@example.com",
}

resp, err := httpreq.Post("https://api.example.com/users", data)
if err != nil {
    // Handle error
}
defer resp.Body.Close()
```

### Other HTTP Methods

```go
// PUT request
resp, err := httpreq.Put("https://api.example.com/users/123", updateData)

// DELETE request
resp, err := httpreq.Delete("https://api.example.com/users/123")

// PATCH request
resp, err := httpreq.Patch("https://api.example.com/users/123", patchData)
```

---

## Request Building

### Create Client

```go
// Create new client with options
client := httpreq.New()

// Set timeout
client.SetTimeout(30 * time.Second)

// Set base URL
client.SetBaseURL("https://api.example.com")

// Set default headers
client.SetHeader("Authorization", "Bearer token123")
client.SetHeader("User-Agent", "MyApp/1.0")
```

### Build Request

```go
// Create request
req := httpreq.NewRequest("GET", "/users")

// Add query parameters
req.AddQuery("page", "1")
req.AddQuery("limit", "10")

// Set headers
req.SetHeader("Accept", "application/json")
req.SetHeader("Authorization", "Bearer token")

// Execute request
resp, err := client.Do(req)
```

### Request with JSON Body

```go
// Create request with JSON
req := httpreq.NewJSONRequest("POST", "/users", map[string]any{
    "name": "John",
    "age":  30,
})

resp, err := client.Do(req)
```

### Request with Form Data

```go
// Create form request
req := httpreq.NewFormRequest("POST", "/login")

// Add form fields
req.AddFormField("username", "john")
req.AddFormField("password", "secret")

resp, err := client.Do(req)
```

---

## Response Handling

### Read Response Body

```go
resp, err := httpreq.Get("https://api.example.com/data")
if err != nil {
    return err
}
defer resp.Body.Close()

// Read as bytes
body, err := io.ReadAll(resp.Body)

// Read as string
bodyStr := string(body)
```

### Parse JSON Response

```go
type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

resp, err := httpreq.Get("https://api.example.com/users/1")
if err != nil {
    return err
}
defer resp.Body.Close()

// Parse JSON
var user User
if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
    return err
}
```

### Check Status Code

```go
resp, err := httpreq.Get(url)
if err != nil {
    return err
}
defer resp.Body.Close()

// Check status
if resp.StatusCode != http.StatusOK {
    return fmt.Errorf("unexpected status: %d", resp.StatusCode)
}

// Or use status helpers
if !httpreq.IsSuccess(resp) {
    return errors.New("request failed")
}
```

---

## Advanced Features

### Custom Headers

```go
// Set headers on request
req := httpreq.NewRequest("GET", "/api/data")
req.SetHeader("Authorization", "Bearer token123")
req.SetHeader("Accept", "application/json")
req.SetHeader("X-Custom-Header", "value")

// Set multiple headers
headers := map[string]string{
    "Authorization": "Bearer token123",
    "Accept":        "application/json",
}
req.SetHeaders(headers)
```

### Query Parameters

```go
req := httpreq.NewRequest("GET", "/api/search")

// Add query params
req.AddQuery("q", "golang")
req.AddQuery("page", "1")
req.AddQuery("limit", "20")

// Result: /api/search?q=golang&page=1&limit=20

// Add multiple at once
params := map[string]string{
    "category": "tech",
    "sort":     "recent",
}
req.AddQueryParams(params)
```

### Request Timeout

```go
// Set timeout on client
client := httpreq.New()
client.SetTimeout(10 * time.Second)

// Or per request with context
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

req := httpreq.NewRequestWithContext(ctx, "GET", url)
resp, err := client.Do(req)
```

### File Upload

```go
// Upload file
file, err := os.Open("document.pdf")
if err != nil {
    return err
}
defer file.Close()

req := httpreq.NewMultipartRequest("POST", "/upload")
req.AddFile("document", "document.pdf", file)
req.AddFormField("description", "My document")

resp, err := client.Do(req)
```

### Follow Redirects

```go
// Disable redirect following
client := httpreq.New()
client.SetCheckRedirect(func(req *http.Request, via []*http.Request) error {
    return http.ErrUseLastResponse
})

// Or limit redirects
client.SetMaxRedirects(5)
```

---

## Complete Examples

### REST API Client

```go
package main

import (
    "fmt"
    "encoding/json"
    "github.com/gookit/goutil/netutil/httpreq"
)

type APIClient struct {
    client  *httpreq.Client
    baseURL string
    apiKey  string
}

func NewAPIClient(baseURL, apiKey string) *APIClient {
    client := httpreq.New()
    client.SetTimeout(30 * time.Second)
    client.SetHeader("Authorization", "Bearer "+apiKey)
    client.SetHeader("Content-Type", "application/json")

    return &APIClient{
        client:  client,
        baseURL: baseURL,
        apiKey:  apiKey,
    }
}

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

func (c *APIClient) GetUser(id int) (*User, error) {
    url := fmt.Sprintf("%s/users/%d", c.baseURL, id)
    resp, err := c.client.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    if resp.StatusCode != 200 {
        return nil, fmt.Errorf("API error: %d", resp.StatusCode)
    }

    var user User
    if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
        return nil, err
    }

    return &user, nil
}

func (c *APIClient) CreateUser(name, email string) (*User, error) {
    url := fmt.Sprintf("%s/users", c.baseURL)
    data := map[string]string{
        "name":  name,
        "email": email,
    }

    resp, err := c.client.Post(url, data)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    if resp.StatusCode != 201 {
        return nil, fmt.Errorf("create failed: %d", resp.StatusCode)
    }

    var user User
    if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
        return nil, err
    }

    return &user, nil
}

func main() {
    client := NewAPIClient("https://api.example.com", "your-api-key")

    // Get user
    user, err := client.GetUser(1)
    if err != nil {
        panic(err)
    }
    fmt.Printf("User: %+v\n", user)

    // Create user
    newUser, err := client.CreateUser("Jane Doe", "jane@example.com")
    if err != nil {
        panic(err)
    }
    fmt.Printf("Created: %+v\n", newUser)
}
```

### Download File

```go
package main

import (
    "fmt"
    "io"
    "os"
    "github.com/gookit/goutil/netutil/httpreq"
    "github.com/gookit/goutil/fsutil"
)

func downloadFile(url, destPath string) error {
    // Create HTTP request
    resp, err := httpreq.Get(url)
    if err != nil {
        return fmt.Errorf("request failed: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != 200 {
        return fmt.Errorf("bad status: %d", resp.StatusCode)
    }

    // Create destination file
    out, err := os.Create(destPath)
    if err != nil {
        return fmt.Errorf("create file failed: %w", err)
    }
    defer out.Close()

    // Copy data
    _, err = io.Copy(out, resp.Body)
    if err != nil {
        return fmt.Errorf("download failed: %w", err)
    }

    return nil
}

func main() {
    url := "https://example.com/file.pdf"
    destPath := "downloaded.pdf"

    fmt.Printf("Downloading %s...\n", url)
    if err := downloadFile(url, destPath); err != nil {
        panic(err)
    }

    size, _ := fsutil.FileSize(destPath)
    fmt.Printf("Downloaded %d bytes to %s\n", size, destPath)
}
```

### Upload with Progress

```go
package main

import (
    "fmt"
    "os"
    "io"
    "github.com/gookit/goutil/netutil/httpreq"
)

type ProgressReader struct {
    reader     io.Reader
    total      int64
    uploaded   int64
    onProgress func(uploaded, total int64)
}

func (pr *ProgressReader) Read(p []byte) (int, error) {
    n, err := pr.reader.Read(p)
    pr.uploaded += int64(n)

    if pr.onProgress != nil {
        pr.onProgress(pr.uploaded, pr.total)
    }

    return n, err
}

func uploadWithProgress(url, filePath string) error {
    file, err := os.Open(filePath)
    if err != nil {
        return err
    }
    defer file.Close()

    stat, _ := file.Stat()
    totalSize := stat.Size()

    // Wrap file with progress reader
    progressReader := &ProgressReader{
        reader: file,
        total:  totalSize,
        onProgress: func(uploaded, total int64) {
            percent := float64(uploaded) / float64(total) * 100
            fmt.Printf("\rUploading: %.2f%% (%d/%d bytes)", percent, uploaded, total)
        },
    }

    // Create multipart request
    req := httpreq.NewMultipartRequest("POST", url)
    req.AddFile("file", filePath, progressReader)

    client := httpreq.New()
    resp, err := client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    fmt.Println("\nUpload complete!")
    return nil
}

func main() {
    url := "https://api.example.com/upload"
    filePath := "large-file.zip"

    if err := uploadWithProgress(url, filePath); err != nil {
        panic(err)
    }
}
```

### Retry Logic

```go
package main

import (
    "fmt"
    "time"
    "github.com/gookit/goutil/netutil/httpreq"
)

func requestWithRetry(url string, maxRetries int) (*http.Response, error) {
    var resp *http.Response
    var err error

    for i := 0; i < maxRetries; i++ {
        resp, err = httpreq.Get(url)
        if err == nil && resp.StatusCode == 200 {
            return resp, nil
        }

        if resp != nil {
            resp.Body.Close()
        }

        // Wait before retry (exponential backoff)
        waitTime := time.Duration(i+1) * time.Second
        fmt.Printf("Retry %d/%d after %v...\n", i+1, maxRetries, waitTime)
        time.Sleep(waitTime)
    }

    return nil, fmt.Errorf("max retries exceeded: %w", err)
}

func main() {
    url := "https://api.example.com/unstable-endpoint"
    resp, err := requestWithRetry(url, 3)
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()

    fmt.Println("Request successful!")
}
```

### Concurrent Requests

```go
package main

import (
    "fmt"
    "sync"
    "github.com/gookit/goutil/netutil/httpreq"
)

type Result struct {
    URL    string
    Status int
    Error  error
}

func fetchAll(urls []string) []Result {
    results := make([]Result, len(urls))
    var wg sync.WaitGroup

    for i, url := range urls {
        wg.Add(1)
        go func(index int, targetURL string) {
            defer wg.Done()

            resp, err := httpreq.Get(targetURL)
            if err != nil {
                results[index] = Result{
                    URL:   targetURL,
                    Error: err,
                }
                return
            }
            defer resp.Body.Close()

            results[index] = Result{
                URL:    targetURL,
                Status: resp.StatusCode,
            }
        }(i, url)
    }

    wg.Wait()
    return results
}

func main() {
    urls := []string{
        "https://api.example.com/endpoint1",
        "https://api.example.com/endpoint2",
        "https://api.example.com/endpoint3",
    }

    fmt.Println("Fetching URLs concurrently...")
    results := fetchAll(urls)

    for _, result := range results {
        if result.Error != nil {
            fmt.Printf("✗ %s - Error: %v\n", result.URL, result.Error)
        } else {
            fmt.Printf("✓ %s - Status: %d\n", result.URL, result.Status)
        }
    }
}
```

---

## Best Practices

### 1. Always Close Response Body

```go
// Good
resp, err := httpreq.Get(url)
if err != nil {
    return err
}
defer resp.Body.Close()

// Bad - memory leak
resp, err := httpreq.Get(url)
// Missing defer resp.Body.Close()
```

### 2. Check Status Codes

```go
// Good
resp, err := httpreq.Post(url, data)
if err != nil {
    return err
}
defer resp.Body.Close()

if resp.StatusCode != http.StatusCreated {
    return fmt.Errorf("unexpected status: %d", resp.StatusCode)
}
```

### 3. Use Context for Timeouts

```go
// Good
ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
defer cancel()

req := httpreq.NewRequestWithContext(ctx, "GET", url)
resp, err := client.Do(req)
```

### 4. Reuse HTTP Clients

```go
// Good - reuse client
var client = httpreq.New()

func makeRequest(url string) error {
    resp, err := client.Get(url)
    // ...
}

// Avoid - creating new client each time
func makeRequest(url string) error {
    client := httpreq.New()  // Wasteful
    resp, err := client.Get(url)
    // ...
}
```

### 5. Handle Errors Properly

```go
// Good
resp, err := httpreq.Get(url)
if err != nil {
    return fmt.Errorf("request failed: %w", err)
}
defer resp.Body.Close()

if resp.StatusCode >= 400 {
    body, _ := io.ReadAll(resp.Body)
    return fmt.Errorf("HTTP %d: %s", resp.StatusCode, string(body))
}
```

---

## Utilities

### Status Code Helpers

```go
// Check if successful (2xx)
if httpreq.IsSuccess(resp) {
    // Success
}

// Check if redirect (3xx)
if httpreq.IsRedirect(resp) {
    // Redirect
}

// Check if client error (4xx)
if httpreq.IsClientError(resp) {
    // Client error
}

// Check if server error (5xx)
if httpreq.IsServerError(resp) {
    // Server error
}
```

---

**Related Documentation:**
- [Main Skill Documentation](SKILL.md)
- [System & CLI Packages](system-cli-packages.md)
- [timex Reference](timex-reference.md)
