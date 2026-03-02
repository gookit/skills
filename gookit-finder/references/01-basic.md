# Finder Basics

This document covers the fundamental concepts and basic usage of the Finder package.

## Core Concepts

### What is Finder?

Finder is a Go package that provides powerful file and directory searching capabilities with flexible filtering options. Unlike simple file walking, Finder offers:

- **Advanced Filtering**: Multiple ways to include/exclude files and directories
- **Concurrent Processing**: Built-in support for parallel scanning
- **Rich Matchers**: Pre-built matchers for common patterns
- **Stream Processing**: Channel-based results for memory efficiency

### Key Components

#### Finder Instance
The main struct that manages the scanning process:

```go
type Finder struct {
    // Configuration and state management
    // Handles concurrent scanning
    // Manages filters and matchers
}
```

#### Elements (Elem)
Represents found files or directories:

```go
type Elem interface {
    Path() string           // Full file path
    Name() string           // File/directory name
    IsDir() bool            // Directory check
    Info() (os.FileInfo, error) // File metadata
}
```

#### Matchers
Functions that determine whether an element should be included:

```go
type Matcher interface {
    Apply(elem Elem) bool
}

type MatcherFunc func(elem Elem) bool
```

## Basic Usage Patterns

### 1. Simple File Finding

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/x/finder"
)

func main() {
    // Find all files in a directory
    f := finder.NewFinder("/path/to/search")
    paths := f.FindPaths()
    
    fmt.Printf("Found %d files:\n", len(paths))
    for _, path := range paths {
        fmt.Println(path)
    }
}
```

### 2. Directory Finding

```go
// Find only directories
f := finder.NewFinder("/path/to/search").
    WithFlag(finder.FlagDir)

dirs := f.FindPaths()
```

### 3. Combined File and Directory Search

```go
// Find both files and directories
f := finder.NewFinder("/path/to/search").
    WithFlag(finder.FlagBoth)

allItems := f.FindPaths()
```

## Essential Configuration

### Setting Scan Paths

```go
// Single path
f := finder.NewFinder("/single/path")

// Multiple paths
f := finder.NewFinder("/path1", "/path2", "/path3")

// Or add paths incrementally
f := finder.NewEmpty()
f.AddScan("/path1").AddScan("/path2")
```

### Controlling Depth

```go
// Unlimited depth (default)
f := finder.NewFinder("/path")

// Limit to 3 levels deep
f := finder.NewFinder("/path").SetMaxDepth(3)

// Only top level
f := finder.NewFinder("/path").SetMaxDepth(1)
```

### Concurrency Settings

```go
// Single threaded (default)
f := finder.NewFinder("/path")

// Use 4 concurrent workers
f := finder.NewFinder("/path").SetConcurrency(4)

// Use all available CPU cores
import "runtime"
f := finder.NewFinder("/path").SetConcurrency(runtime.NumCPU())
```

## Basic Filtering

### Extension-based Filtering

```go
// Include only Go files
f := finder.NewFinder("/project").
    IncludeExt(".go")

// Include multiple extensions
f := finder.NewFinder("/project").
    IncludeExt(".go", ".md", ".txt")

// Exclude test files
f := finder.NewFinder("/project").
    ExcludeExt("_test.go")
```

### Name-based Filtering

```go
// Include specific filenames
f := finder.NewFinder("/config").
    IncludeName("config.json", "settings.yaml")

// Exclude temporary files
f := finder.NewFinder("/work").
    ExcludeName("*.tmp", "*.bak")
```

### Directory Filtering

```go
// Exclude vendor directories
f := finder.NewFinder("/project").
    ExcludeDir("vendor", "node_modules", ".git")

// Include only specific directories
f := finder.NewFinder("/src").
    IncludeDir("models", "controllers", "views")
```

## Result Processing

### Channel-based Processing (Recommended)

```go
f := finder.NewFinder("/large/directory")

// Process results as they're found
for elem := range f.Find() {
    fmt.Printf("Found: %s (dir: %t)\n", elem.Path(), elem.IsDir())
    
    // Access file info if needed
    if info, err := elem.Info(); err == nil {
        fmt.Printf("  Size: %d bytes\n", info.Size())
    }
}
```

### Slice-based Processing

```go
f := finder.NewFinder("/directory")

// Get all paths at once
paths := f.FindPaths()
fmt.Printf("Total found: %d\n", len(paths))

// Get all names
names := f.FindNames()
```

### Callback-based Processing

```go
f := finder.NewFinder("/directory")

// Process each element with callback
f.Each(func(el finder.Elem) {
    fmt.Println("Processing:", el.Path())
})

// Process only paths
f.EachPath(func(path string) {
    fmt.Println("Path:", path)
})
```

## Error Handling

```go
f := finder.NewFinder("/possibly/missing/path")
paths := f.FindPaths()

// Check for errors
if err := f.Err(); err != nil {
    fmt.Printf("Error during search: %v\n", err)
    return
}

// Check result count
fmt.Printf("Found %d items successfully\n", f.Num())
```

## Practical Examples

### Example 1: Find Large Log Files

```go
func findLargeLogs(rootPath string) []string {
    f := finder.NewFinder(rootPath).
        IncludeExt(".log").
        Add(finder.HumanSize(">10MB"))
    
    return f.FindPaths()
}
```

### Example 2: Clean Up Temporary Files

```go
func cleanupTempFiles(tempDir string) {
    f := finder.NewFinder(tempDir).
        IncludeName("*.tmp", "*.temp", "*.bak").
        SetMaxDepth(2)  // Don't go too deep
    
    var removed []string
    f.EachPath(func(path string) {
        if err := os.Remove(path); err == nil {
            removed = append(removed, path)
        }
    })
    
    fmt.Printf("Removed %d temporary files\n", len(removed))
}
```

### Example 3: Find Recent Configuration Files

```go
func findRecentConfigs(configDir string) {
    f := finder.NewFinder(configDir).
        IncludeExt(".yaml", ".yml", ".json", ".toml").
        Add(finder.HumanModTime("<7d"))  // Modified within last 7 days
    
    f.Each(func(el finder.Elem) {
        info, _ := el.Info()
        fmt.Printf("%s - %v\n", el.Path(), info.ModTime())
    })
}
```

## Performance Considerations

### When to Use Each Approach

1. **Channel-based (`Find()`)**: Best for large directories, memory efficiency
2. **Slice-based (`FindPaths()`)**: Good for small to medium results, convenience
3. **Callback-based (`Each()`)**: Best when processing results immediately

### Memory Usage Patterns

```go
// Memory efficient - processes as found
for elem := range f.Find() {
    processElement(elem)
}

// Higher memory usage - collects all first
paths := f.FindPaths()
for _, path := range paths {
    processPath(path)
}
```

## Next Steps

After mastering these basics, explore:
- Advanced matcher combinations
- Custom matcher creation
- Performance optimization techniques
- Integration with other tools