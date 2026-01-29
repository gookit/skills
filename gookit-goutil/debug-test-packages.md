# GoUtil - Debug & Test Packages Reference

Complete reference for GoUtil's debugging and testing utilities.

## Table of Contents

- [dump - Pretty Printer](#dump---pretty-printer)
- [errorx - Enhanced Errors](#errorx---enhanced-errors)
- [assert - Test Assertions](#assert---test-assertions)
- [testutil - Test Utilities](#testutil---test-utilities)
- [fakeobj - Fake Objects](#fakeobj---fake-objects)

---

## dump - Pretty Printer

**Import**: `github.com/gookit/goutil/dump`

Advanced value printing for debugging with auto-formatting, colors, and call location display.

### Basic Usage

```go
import "github.com/gookit/goutil/dump"

// Print any value
dump.P(variable)

// Print multiple values
dump.P(var1, var2, var3)

// Print with custom format
dump.Print(variable)
```

### Features

**Auto-formatted Output:**
- Slices and maps wrap each element
- Nested structures are indented
- Large data is paginated

**Call Location:**
Shows where dump.P() was called from:
```
PRINT AT path/to/file.go:42
```

**Colored Output:**
Automatically uses colors in terminal for better readability.

### Complete Example

```go
package main

import "github.com/gookit/goutil/dump"

type User struct {
    ID      int
    Name    string
    Email   string
    Active  bool
    Tags    []string
    Meta    map[string]string
}

func main() {
    user := User{
        ID:     1,
        Name:   "John Doe",
        Email:  "john@example.com",
        Active: true,
        Tags:   []string{"admin", "verified"},
        Meta: map[string]string{
            "location": "NYC",
            "timezone": "EST",
        },
    }

    // Pretty print the struct
    dump.P(user)

    // Output will show:
    // - Colored, formatted structure
    // - Call location
    // - Nested data properly indented
}
```

### Configuration

```go
// Enable/disable colors
dump.Config.ShowColor = true

// Enable/disable location
dump.Config.ShowCaller = true

// Set output depth
dump.Config.MaxDepth = 5
```

### Advanced Usage

```go
// Print slice with formatting
data := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
dump.P(data)

// Print nested map
config := map[string]any{
    "database": map[string]any{
        "host": "localhost",
        "port": 5432,
        "pool": map[string]int{
            "min": 5,
            "max": 20,
        },
    },
}
dump.P(config)

// Compare two values
dump.P("Before:", oldValue, "After:", newValue)
```

---

## errorx - Enhanced Errors

**Import**: `github.com/gookit/goutil/errorx`

Enhanced error implementation with stacktrace and error wrapping capabilities.

### Creating Errors

```go
import "github.com/gookit/goutil/errorx"

// Create simple error
err := errorx.New("something went wrong")

// Create error with format
err := errorx.Newf("failed to process item %d", itemID)

// Create with stacktrace
err := errorx.NewR("operation failed")  // R = with stack Recording
```

### Wrapping Errors

```go
// Wrap existing error
originalErr := errors.New("file not found")
err := errorx.Wrap(originalErr, "failed to read config")

// Wrap with format
err := errorx.Wrapf(originalErr, "failed to read config from %s", path)

// Wrap with stacktrace
err := errorx.WrapR(originalErr, "operation failed")
```

### Error Information

```go
// Check if has error
if errorx.Has(err) {
    // Handle error
}

// Get wrapped errors
cause := errorx.Cause(err)
previous := errorx.Previous(err)

// Get stacktrace
if ex, ok := err.(*errorx.ErrorX); ok {
    stack := ex.StackTrace()
}
```

### Complete Example

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/errorx"
)

func readFile(path string) error {
    // Simulate file operation error
    err := someFileOperation(path)
    if err != nil {
        return errorx.Wrapf(err, "failed to read file: %s", path)
    }
    return nil
}

func loadConfig(path string) error {
    err := readFile(path)
    if err != nil {
        return errorx.Wrap(err, "config loading failed")
    }
    return nil
}

func main() {
    err := loadConfig("/etc/myapp/config.yml")
    if err != nil {
        fmt.Println("Error:", err)

        // Print error chain
        if ex, ok := err.(*errorx.ErrorX); ok {
            fmt.Println("\nError chain:")
            fmt.Println(ex.Format())
        }
    }
}
```

---

## assert - Test Assertions

**Import**: `github.com/gookit/goutil/testutil/assert`

Provides common assertion functions for testing.

### Equality Assertions

```go
import (
    "testing"
    "github.com/gookit/goutil/testutil/assert"
)

func TestEquality(t *testing.T) {
    // Equal
    assert.Eq(t, 1, 1)
    assert.Equal(t, "hello", "hello")

    // Not equal
    assert.Neq(t, 1, 2)
    assert.NotEqual(t, "a", "b")

    // Same (pointer equality)
    a := &User{Name: "John"}
    b := a
    assert.Same(t, a, b)
}
```

### Boolean Assertions

```go
func TestBoolean(t *testing.T) {
    // True/False
    assert.True(t, true)
    assert.False(t, false)

    // OK (non-nil)
    assert.OK(t, &User{})

    // Nil
    assert.Nil(t, nil)
    assert.NotNil(t, &User{})
}
```

### Collection Assertions

```go
func TestCollections(t *testing.T) {
    slice := []int{1, 2, 3, 4, 5}

    // Contains
    assert.Contains(t, slice, 3)
    assert.NotContains(t, slice, 10)

    // Length
    assert.Len(t, slice, 5)
    assert.NotEmpty(t, slice)
    assert.Empty(t, []int{})

    // Map contains key
    m := map[string]int{"a": 1, "b": 2}
    assert.ContainsKey(t, m, "a")
    assert.NotContainsKey(t, m, "c")
}
```

### Comparison Assertions

```go
func TestComparison(t *testing.T) {
    // Greater/Less
    assert.Gt(t, 5, 3)       // Greater than
    assert.Lt(t, 3, 5)       // Less than
    assert.Gte(t, 5, 5)      // Greater than or equal
    assert.Lte(t, 3, 5)      // Less than or equal

    // In range
    assert.InRange(t, 5, 1, 10)
}
```

### Error Assertions

```go
func TestErrors(t *testing.T) {
    err := doSomething()

    // Error occurred
    assert.Err(t, err)
    assert.ErrMsg(t, err, "expected message")

    // No error
    assert.NoErr(t, nil)
}
```

### String Assertions

```go
func TestStrings(t *testing.T) {
    str := "Hello, World!"

    // Contains substring
    assert.StrContains(t, str, "World")
    assert.NotContains(t, str, "Goodbye")

    // Has prefix/suffix
    assert.HasPrefix(t, str, "Hello")
    assert.HasSuffix(t, str, "World!")

    // Match pattern
    assert.MatchRegex(t, str, `\w+,\s\w+!`)
}
```

### Complete Testing Example

```go
package calculator

import (
    "testing"
    "github.com/gookit/goutil/testutil/assert"
)

func Add(a, b int) int {
    return a + b
}

func Divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

func TestAdd(t *testing.T) {
    // Test cases
    tests := []struct {
        a, b, expected int
    }{
        {1, 2, 3},
        {0, 0, 0},
        {-1, 1, 0},
        {10, 20, 30},
    }

    for _, tt := range tests {
        result := Add(tt.a, tt.b)
        assert.Eq(t, tt.expected, result)
    }
}

func TestDivide(t *testing.T) {
    // Normal case
    result, err := Divide(10, 2)
    assert.NoErr(t, err)
    assert.Eq(t, 5, result)

    // Division by zero
    _, err = Divide(10, 0)
    assert.Err(t, err)
    assert.ErrMsg(t, err, "division by zero")
}

func TestCollection(t *testing.T) {
    numbers := []int{1, 2, 3, 4, 5}

    assert.Len(t, numbers, 5)
    assert.Contains(t, numbers, 3)
    assert.NotContains(t, numbers, 10)

    // Check all values
    for _, n := range numbers {
        assert.InRange(t, n, 1, 5)
    }
}
```

---

## testutil - Test Utilities

**Import**: `github.com/gookit/goutil/testutil`

Test helper utilities for mocking, HTTP testing, and environment manipulation.

### Mock Environment

```go
import "github.com/gookit/goutil/testutil"

func TestWithEnv(t *testing.T) {
    // Set temporary env var
    testutil.MockEnvValue("API_KEY", "test-key-123", func() {
        // API_KEY is set to "test-key-123" here
        key := os.Getenv("API_KEY")
        assert.Eq(t, "test-key-123", key)
    })

    // API_KEY is restored after callback
}

func TestClearEnv(t *testing.T) {
    // Clear specific env var
    restore := testutil.MockOsEnvByText("API_KEY=")
    defer restore()

    // API_KEY is empty
}
```

### HTTP Testing

```go
import (
    "net/http"
    "github.com/gookit/goutil/testutil"
)

func TestHTTPHandler(t *testing.T) {
    // Create test request
    req := testutil.NewHttpRequest("GET", "/api/users", nil)

    // Create response recorder
    w := testutil.NewTestResponseWriter()

    // Call handler
    handler(w, req)

    // Check response
    assert.Eq(t, 200, w.Code)
    assert.Contains(t, w.Body.String(), "users")
}

// POST request with JSON
func TestPostHandler(t *testing.T) {
    body := `{"name": "John", "email": "john@example.com"}`
    req := testutil.NewHttpRequest("POST", "/api/users", body)
    req.Header.Set("Content-Type", "application/json")

    w := testutil.NewTestResponseWriter()
    handler(w, req)

    assert.Eq(t, 201, w.Code)
}
```

### Temporary Directories

```go
func TestFileOperations(t *testing.T) {
    // Create temporary test directory
    tmpDir := testutil.MkTestDir(t, "mytest")
    defer os.RemoveAll(tmpDir)

    // Use tmpDir for file operations
    filePath := filepath.Join(tmpDir, "test.txt")
    err := os.WriteFile(filePath, []byte("test"), 0644)
    assert.NoErr(t, err)
}
```

---

## fakeobj - Fake Objects

**Import**: `github.com/gookit/goutil/x/fakeobj`

Provides fake objects for testing file system operations.

### Fake File

```go
import "github.com/gookit/goutil/x/fakeobj"

func TestFileReader(t *testing.T) {
    // Create fake file with content
    content := []byte("test file content")
    fakeFile := fakeobj.NewFile("test.txt", content)

    // Use like real file
    data := make([]byte, len(content))
    n, err := fakeFile.Read(data)

    assert.NoErr(t, err)
    assert.Eq(t, len(content), n)
    assert.Eq(t, content, data)
}
```

### Fake FileInfo

```go
func TestFileInfo(t *testing.T) {
    // Create fake file info
    info := fakeobj.NewFileInfo("test.txt", 1024, false)

    assert.Eq(t, "test.txt", info.Name())
    assert.Eq(t, int64(1024), info.Size())
    assert.False(t, info.IsDir())
}
```

### Fake DirEntry

```go
func TestDirEntry(t *testing.T) {
    // Create fake directory entry
    entry := fakeobj.NewDirEntry("subdir", true)

    assert.Eq(t, "subdir", entry.Name())
    assert.True(t, entry.IsDir())
}
```

### Complete Example

```go
package mypackage

import (
    "io"
    "testing"
    "github.com/gookit/goutil/testutil/assert"
    "github.com/gookit/goutil/x/fakeobj"
)

// Function to test
func ProcessFile(f io.Reader) (string, error) {
    data, err := io.ReadAll(f)
    if err != nil {
        return "", err
    }
    return string(data), nil
}

func TestProcessFile(t *testing.T) {
    // Create fake file
    content := []byte("test content")
    fakeFile := fakeobj.NewFile("test.txt", content)

    // Test the function
    result, err := ProcessFile(fakeFile)

    assert.NoErr(t, err)
    assert.Eq(t, "test content", result)
}

// Test with empty file
func TestProcessFileEmpty(t *testing.T) {
    fakeFile := fakeobj.NewFile("empty.txt", []byte{})

    result, err := ProcessFile(fakeFile)

    assert.NoErr(t, err)
    assert.Empty(t, result)
}
```

---

## Import Quick Reference

```go
import (
    "github.com/gookit/goutil/dump"              // Pretty printer
    "github.com/gookit/goutil/errorx"            // Enhanced errors
    "github.com/gookit/goutil/testutil/assert"   // Test assertions
    "github.com/gookit/goutil/testutil"          // Test utilities
    "github.com/gookit/goutil/x/fakeobj"         // Fake objects
)
```

---

## Testing Best Practices

### 1. Use Table-Driven Tests

```go
func TestCalculate(t *testing.T) {
    tests := []struct {
        name     string
        input    int
        expected int
    }{
        {"zero", 0, 0},
        {"positive", 5, 25},
        {"negative", -3, 9},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Calculate(tt.input)
            assert.Eq(t, tt.expected, result)
        })
    }
}
```

### 2. Mock External Dependencies

```go
func TestAPICall(t *testing.T) {
    // Mock environment
    testutil.MockEnvValue("API_URL", "http://test", func() {
        // Test code here
    })
}
```

### 3. Use Subtests

```go
func TestFeature(t *testing.T) {
    t.Run("case1", func(t *testing.T) {
        // Test case 1
    })

    t.Run("case2", func(t *testing.T) {
        // Test case 2
    })
}
```

---

**Related Documentation:**
- [Main Skill Documentation](SKILL.md)
- [Basic Packages](basic-packages.md)
- [System & CLI Packages](system-cli-packages.md)
