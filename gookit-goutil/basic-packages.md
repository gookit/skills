# GoUtil - Basic Packages Reference

Complete reference for GoUtil's basic data manipulation packages.

## Table of Contents

- [arrutil - Array/Slice Utilities](#arrutil---arrayslice-utilities)
- [strutil - String Utilities](#strutil---string-utilities)
- [maputil - Map Utilities](#maputil---map-utilities)
- [mathutil - Math Utilities](#mathutil---math-utilities)
- [byteutil - Byte Utilities](#byteutil---byte-utilities)
- [reflects - Reflection Utilities](#reflects---reflection-utilities)
- [structs - Struct Utilities](#structs---struct-utilities)

---

## arrutil - Array/Slice Utilities

**Import**: `github.com/gookit/goutil/arrutil`

Array and slice manipulation including check, convert, format, and collection operations.

### Type Checking

```go
// Check if slice contains value
arrutil.IntsHas([]int{1, 2, 3}, 2)           // true
arrutil.Int64sHas([]int64{1, 2, 3}, 2)       // true
arrutil.StringsHas([]string{"a", "b"}, "a")  // true

// Generic contains check
arrutil.Contains([]int{1, 2, 3}, 2)          // true
arrutil.NotContains([]int{1, 2, 3}, 5)       // true

// Check if all values exist
arrutil.ContainsAll([]int{1, 2, 3, 4}, []int{2, 3})  // true
arrutil.IsSubList([]int{2, 3}, []int{1, 2, 3, 4})    // true
```

### Type Conversion

```go
// Convert to int64 slice
ints, err := arrutil.ToInt64s([]string{"1", "2", "3"})
// Result: []int64{1, 2, 3}

// Must convert (panics on error)
ints := arrutil.MustToInt64s([]string{"1", "2", "3"})

// Convert to string slice
strs, err := arrutil.ToStrings([]int{1, 2, 3})
// Result: []string{"1", "2", "3"}

strs := arrutil.MustToStrings([]int{1, 2, 3})

// Convert to string
str := arrutil.ToString([]int{1, 2, 3})  // "1,2,3"

// Join with separator
str := arrutil.JoinSlice(",", []int{1, 2, 3})  // "1,2,3"
str := arrutil.JoinStrings(", ", "a", "b", "c") // "a, b, c"
```

### Array Operations

```go
// Remove duplicates
unique := arrutil.Unique([]int{1, 2, 2, 3, 3, 3})
// Result: []int{1, 2, 3}

// Reverse slice in place
slice := []int{1, 2, 3}
arrutil.Reverse(slice)  // slice is now []int{3, 2, 1}

// Remove specific value
result := arrutil.Remove([]int{1, 2, 3, 2}, 2)
// Result: []int{1, 3}

// Get first element or default
first := arrutil.FirstOr([]int{1, 2, 3}, 0)    // 1
first := arrutil.FirstOr([]int{}, 0)           // 0

// Find index
idx := arrutil.IndexOf(2, []int{1, 2, 3})      // 1
idx := arrutil.IndexOf(5, []int{1, 2, 3})      // -1
```

### Functional Operations

```go
// Filter: keep elements matching condition
filtered := arrutil.Filter([]int{1, 2, 3, 4, 5}, func(v int) bool {
    return v > 2
})
// Result: []int{3, 4, 5}

// Map: transform each element
squared := arrutil.Map([]int{1, 2, 3}, func(v int) int {
    return v * v
})
// Result: []int{1, 4, 9}

// Column: extract field from structs
type User struct { Name string; Age int }
users := []User{{"Alice", 25}, {"Bob", 30}}
names := arrutil.Column(users, func(u User) (string, bool) {
    return u.Name, true
})
// Result: []string{"Alice", "Bob"}

// Convert to map
users := []User{{"Alice", 25}, {"Bob", 30}}
ageMap := arrutil.ToMap(users, func(u User) (string, int) {
    return u.Name, u.Age
})
// Result: map[string]int{"Alice": 25, "Bob": 30}
```

### Set Operations

```go
first := []int{1, 2, 3, 4}
second := []int{3, 4, 5, 6}

// Difference: elements in first but not in second
diff := arrutil.Diff(first, second, arrutil.ValueEqualsComparer[int])
// Result: []int{1, 2}

// Intersection: common elements
inter := arrutil.Intersects(first, second, arrutil.ValueEqualsComparer[int])
// Result: []int{3, 4}

// Union: all unique elements
union := arrutil.Union(first, second, arrutil.ValueEqualsComparer[int])
// Result: []int{1, 2, 3, 4, 5, 6}
```

### Complete Example

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/arrutil"
)

func main() {
    // Original data
    numbers := []int{5, 2, 8, 2, 9, 1, 5, 8}

    // Remove duplicates
    unique := arrutil.Unique(numbers)
    fmt.Println("Unique:", unique)  // [5 2 8 9 1]

    // Filter even numbers
    evens := arrutil.Filter(unique, func(n int) bool {
        return n%2 == 0
    })
    fmt.Println("Evens:", evens)  // [2 8]

    // Square the numbers
    squared := arrutil.Map(evens, func(n int) int {
        return n * n
    })
    fmt.Println("Squared:", squared)  // [4 64]

    // Convert to strings
    strs := arrutil.MustToStrings(squared)
    fmt.Println("Strings:", strs)  // ["4" "64"]
}
```

---

## strutil - String Utilities

**Import**: `github.com/gookit/goutil/strutil`

Comprehensive string manipulation including case conversion, checking, formatting, and encoding.

### Case Conversion

```go
// Upper/Lower case
strutil.Upper("hello")           // "HELLO"
strutil.Lower("HELLO")           // "hello"
strutil.UpperFirst("hello")      // "Hello"
strutil.LowerFirst("Hello")      // "hello"

// Snake case
strutil.Snake("HelloWorld")      // "hello_world"
strutil.Snake("helloWorld", "-") // "hello-world"

// Camel case
strutil.Camel("hello_world")     // "helloWorld"
strutil.UpperCamelCase("hello_world")  // "HelloWorld"
```

### String Checking

```go
// Type checking
strutil.IsNumeric("123")         // true
strutil.IsNumeric("12.34")       // true
strutil.IsAlpha("abc")           // true
strutil.IsAlphaNum("abc123")     // true

// Empty/blank checking
strutil.IsEmpty("")              // true
strutil.IsBlank("  \t\n  ")      // true

// Format validation
strutil.IsEmail("user@example.com")      // true
strutil.IsURL("https://example.com")     // true
```

### String Operations

```go
// Substring
strutil.Substr("hello", 0, 2)    // "he"
strutil.Substr("hello", 1, 3)    // "ell"

// Repeat
strutil.Repeat("a", 3)           // "aaa"

// Replace multiple
strutil.Replaces("hello world", map[string]string{
    "hello": "hi",
    "world": "there",
})  // "hi there"

// Split
parts := strutil.Split("a,b,c", ",")  // []string{"a", "b", "c"}

// Trim
strutil.Trim("  hello  ")        // "hello"
strutil.TrimLeft("  hello")      // "hello"
strutil.TrimRight("hello  ")     // "hello"
```

### String Search

```go
// Contains
strutil.Contains("hello world", "world")     // true
strutil.ContainsAll("hello world", []string{"hello", "world"})  // true
strutil.ContainsAny("hello", []string{"hi", "hello"})          // true

// Has prefix/suffix
strutil.HasPrefix("hello", "he")  // true
strutil.HasSuffix("hello", "lo")  // true

// Has one of prefixes/suffixes
strutil.HasOneSuffix("test.go", []string{".go", ".md"})  // true
```

### Random and Hash

```go
// Generate random string
random := strutil.Random(10)         // Random 10-char string
random := strutil.RandomChars(10)    // Random from custom charset

// Generate hash
md5 := strutil.Md5("hello")          // MD5 hash
```

### Complete Example

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/strutil"
)

func main() {
    // Sanitize user input
    input := "  Hello_World  "

    // Clean and transform
    cleaned := strutil.Trim(input)
    snake := strutil.Snake(cleaned)
    lower := strutil.Lower(snake)

    fmt.Println(lower)  // "hello_world"

    // Validation
    email := "user@example.com"
    if strutil.IsEmail(email) {
        fmt.Println("Valid email")
    }

    // Replace sensitive data
    text := "My password is secret123"
    safe := strutil.Replaces(text, map[string]string{
        "secret123": "****",
    })
    fmt.Println(safe)  // "My password is ****"
}
```

---

## maputil - Map Utilities

**Import**: `github.com/gookit/goutil/maputil`

Map data manipulation including nested access, merging, and conversion.

### Nested Value Access

```go
data := map[string]any{
    "user": map[string]any{
        "name": "John",
        "profile": map[string]any{
            "age": 30,
            "city": "NYC",
        },
    },
}

// Get nested value by path
name := maputil.GetByPath(data, "user.name")
// Result: "John"

age := maputil.GetByPath(data, "user.profile.age")
// Result: 30

// Get with default value
country := maputil.GetByPath(data, "user.profile.country", "USA")
// Result: "USA"

// Set nested value
maputil.SetByPath(&data, "user.profile.country", "USA")
```

### Map Operations

```go
// Merge maps
map1 := map[string]string{"a": "1", "b": "2"}
map2 := map[string]string{"b": "3", "c": "4"}
merged := maputil.Merge(map1, map2)
// Result: map[string]string{"a": "1", "b": "3", "c": "4"}

// Extract keys
keys := maputil.Keys(map[string]int{"a": 1, "b": 2})
// Result: []string{"a", "b"}

// Extract values
values := maputil.Values(map[string]int{"a": 1, "b": 2})
// Result: []any{1, 2}
```

### Type Conversion

```go
// Convert to string map
data := map[string]any{"a": 1, "b": "hello"}
smap := maputil.ToSMap(data)
// Result: map[string]string{"a": "1", "b": "hello"}

// Combine slices to map
keys := []string{"a", "b", "c"}
values := []int{1, 2, 3}
m := maputil.CombineToMap(keys, values)
// Result: map[string]int{"a": 1, "b": 2, "c": 3}
```

### Complete Example

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/maputil"
)

func main() {
    config := map[string]any{
        "database": map[string]any{
            "host": "localhost",
            "port": 5432,
            "credentials": map[string]any{
                "user": "admin",
                "pass": "secret",
            },
        },
    }

    // Access nested config
    host := maputil.GetByPath(config, "database.host")
    fmt.Println("Host:", host)  // "localhost"

    // Get with default
    timeout := maputil.GetByPath(config, "database.timeout", 30)
    fmt.Println("Timeout:", timeout)  // 30

    // Merge with overrides
    overrides := map[string]any{
        "database": map[string]any{
            "port": 3306,
        },
    }
    merged := maputil.Merge(config, overrides, true)
    port := maputil.GetByPath(merged, "database.port")
    fmt.Println("New port:", port)  // 3306
}
```

---

## mathutil - Math Utilities

**Import**: `github.com/gookit/goutil/mathutil`

Math operations including calculations, comparisons, and random number generation.

### Basic Operations

```go
// Max/Min
mathutil.Max(1, 5, 3)            // 5
mathutil.Min(1, 5, 3)            // 1
mathutil.MaxInt(1, 5, 3)         // 5

// Sum and Average
mathutil.Sum(1, 2, 3, 4)         // 10
mathutil.Avg(2, 4, 6)            // 4

// Absolute value
mathutil.Abs(-5)                 // 5
```

### Range Operations

```go
// Check if in range
mathutil.InRange(5, 1, 10)       // true
mathutil.InRange(15, 1, 10)      // false

// Check if out of range
mathutil.OutRange(15, 1, 10)     // true
```

### Random Numbers

```go
// Random integer in range
num := mathutil.RandomInt(1, 100)     // Random 1-100
num := mathutil.RandInt(1, 100)       // Same as above

// Random with seed
mathutil.RandomIntWithSeed(1, 100, 42)
```

### Conversions

```go
// Safe int conversion
num, err := mathutil.ToInt("123")     // 123, nil
num, err := mathutil.ToInt("abc")     // 0, error

// Must convert (panics on error)
num := mathutil.MustInt("123")        // 123

// Float conversion
f, err := mathutil.ToFloat("12.34")   // 12.34, nil
```

### Complete Example

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/mathutil"
)

func main() {
    // Calculate statistics
    scores := []int{85, 90, 78, 92, 88}

    sum := 0
    for _, s := range scores {
        sum = mathutil.Sum(sum, s)
    }

    max := mathutil.Max(scores...)
    min := mathutil.Min(scores...)
    avg := sum / len(scores)

    fmt.Printf("Max: %d, Min: %d, Avg: %d\n", max, min, avg)

    // Generate random test data
    for i := 0; i < 5; i++ {
        score := mathutil.RandomInt(0, 100)
        if mathutil.InRange(score, 60, 100) {
            fmt.Printf("Score %d: Pass\n", score)
        } else {
            fmt.Printf("Score %d: Fail\n", score)
        }
    }
}
```

---

## byteutil - Byte Utilities

**Import**: `github.com/gookit/goutil/byteutil`

Byte manipulation utilities including conversion, checking, and encoding.

### Conversions

```go
// String to bytes
bs := byteutil.ToBytes("hello")       // []byte("hello")
bs := byteutil.SafeBytes(123)         // []byte("123")

// Bytes to string
str := byteutil.String([]byte("hello"))     // "hello"
str := byteutil.ToString([]byte("hello"))   // "hello"

// Safe conversion with error
str, err := byteutil.StrOrErr([]byte("hello"), nil)
```

### Byte Checking

```go
// Check byte type
byteutil.IsNumChar('5')         // true
byteutil.IsAlphaChar('a')       // true
```

### Byte Operations

```go
// MD5 hash
hash := byteutil.Md5("hello")        // MD5 bytes
hash := byteutil.Md5Sum("hello")     // MD5 bytes

// Random bytes
random, err := byteutil.Random(16)   // 16 random bytes

// Get first line
line := byteutil.FirstLine([]byte("line1\nline2"))  // []byte("line1")

// Cut at separator
before, after, found := byteutil.Cut([]byte("key=value"), '=')
// before: []byte("key"), after: []byte("value"), found: true
```

---

## reflects - Reflection Utilities

**Import**: `github.com/gookit/goutil/reflects`

Extended reflection utilities for Go.

### Type Information

```go
import "github.com/gookit/goutil/reflects"

// Get base type name
typeName := reflects.TypeName([]int{})        // "slice"
typeName := reflects.TypeName(map[string]int{})  // "map"

// Check types
reflects.IsEmpty(nil)                // true
reflects.IsEmpty([]int{})            // true
reflects.IsNil(nil)                  // true
```

### Value Operations

```go
// Set value
var i int
reflects.SetValue(&i, 42)

// Get value with reflection
val := reflects.Value(someVar)
```

---

## structs - Struct Utilities

**Import**: `github.com/gookit/goutil/structs`

Struct manipulation utilities including tag parsing and data initialization.

### Tag Parsing

```go
type User struct {
    Name  string `json:"name" validate:"required"`
    Email string `json:"email" validate:"email"`
    Age   int    `json:"age" validate:"min=0,max=120"`
}

// Parse struct tags
tags := structs.ParseTags(User{}, "json")
// Get tag information
```

### Struct Operations

```go
// Initialize struct with data
user := &User{}
data := map[string]any{
    "name": "John",
    "email": "john@example.com",
    "age": 30,
}
structs.InitValues(user, data)
```

---

## Import Quick Reference

```go
import (
    "github.com/gookit/goutil/arrutil"   // Array/slice utilities
    "github.com/gookit/goutil/strutil"   // String utilities
    "github.com/gookit/goutil/maputil"   // Map utilities
    "github.com/gookit/goutil/mathutil"  // Math utilities
    "github.com/gookit/goutil/byteutil"  // Byte utilities
    "github.com/gookit/goutil/reflects"  // Reflection utilities
    "github.com/gookit/goutil/structs"   // Struct utilities
)
```

---

**Related Documentation:**
- [Main Skill Documentation](SKILL.md)
- [Debug & Test Packages](debug-test-packages.md)
- [System & CLI Packages](system-cli-packages.md)
