---
name: gookit-finder
description: Powerful file and directory finder with advanced filtering and matching capabilities
author: inhere
platform: github
source: https://github.com/gookit/goutil/tree/master/x/finder
tags: [file-finder, file-search, directory-scanning, filtering, matching, filesystem]
version: 1.0.0
generated: 2026-02-09T00:00:00Z
---

# Finder Skill

Finder provides a powerful and flexible file/directory lookup functionality with advanced filtering, excluding, matching, and ignoring capabilities. It supports concurrent scanning and comes with many built-in matchers for common use cases.

## Quick Start

```go
package main

import (
    "github.com/gookit/goutil/dump"
    "github.com/gookit/goutil/x/finder"
)

func main() {
    ff := finder.NewFinder()
    ff.AddScan("/tmp", "/usr/local", "/usr/local/share")
    ff.ExcludeDir("abc", "def").ExcludeFile("*.log", "*.tmp")
    // add built-in matchers
    ff.Exclude(finder.MatchSuffix("_test.go"), finder.MatchExt(".md"))

    ss := ff.FindPaths()
    dump.P(ss)
}
```

## Overview

Finder is a Go package that provides simple yet powerful file and directory lookup capabilities. It's designed to be flexible and efficient, supporting various filtering options and concurrent scanning for better performance.

## Features

- **Multiple Path Scanning**: Support scanning multiple directories simultaneously
- **Concurrent Scanning**: Built-in concurrency support for faster scanning
- **Flexible Filtering**: Comprehensive filtering options for files and directories
- **Built-in Matchers**: Rich set of built-in matchers for common patterns
- **Custom Matchers**: Support for custom matcher functions
- **Cross-platform**: Works on all major operating systems
- **Memory Efficient**: Stream-based processing with optional caching
- **Rich API**: Multiple ways to consume results (channels, slices, callbacks)

## Installation

```bash
go get github.com/gookit/goutil/x/finder
```

## Usage

### Basic Usage

```go
import "github.com/gookit/goutil/x/finder"

// Create finder instance
f := finder.NewFinder("/path/to/search")

// Simple file finding
paths := f.FindPaths()
fmt.Println("Found files:", paths)
```

### Advanced Filtering

```go
f := finder.NewFinder("/project/path").
    IncludeExt(".go", ".md").
    ExcludeDir("vendor", "node_modules").
    ExcludeName("*_test.go")

// Get results
for el := range f.Find() {
    fmt.Println("Found:", el.Path())
}
```

### Using Built-in Matchers

```go
f := finder.NewFinder("/search/path").
    Add(finder.MatchExt(".go")).
    Add(finder.MatchSize(">1KB")).
    Add(finder.MatchModTime(">1d"))

results := f.FindPaths()
```

### Custom Matchers

```go
customMatcher := finder.MatcherFunc(func(el finder.Elem) bool {
    return strings.HasPrefix(el.Name(), "config")
})

f := finder.NewFinder("/path").Add(customMatcher)
```

## API Reference

### Core Types

#### Finder
Main finder struct that handles the scanning and filtering logic.

```go
type Finder struct {
    // contains filtered or unexported fields
}
```

#### Elem
Represents a found file or directory element.

```go
type Elem interface {
    Path() string      // Full path
    Name() string      // Base name
    IsDir() bool       // Check if directory
    Info() (os.FileInfo, error)  // File info
}
```

### Main Methods

#### Constructor Functions
```go
// NewFinder creates finder with directory paths
func NewFinder(dirPaths ...string) *Finder

// NewWithConfig creates finder with custom config
func NewWithConfig(c *Config) *Finder

// NewEmpty creates empty finder instance
func NewEmpty() *Finder
```

#### Result Methods
```go
// Find returns channel for streaming results
func (f *Finder) Find() <-chan Elem

// FindPaths returns slice of found paths
func (f *Finder) FindPaths() []string

// FindNames returns slice of found names
func (f *Finder) FindNames() []string
```

#### Iteration Methods
```go
// Each processes each found element
func (f *Finder) Each(fn func(el Elem))

// EachPath processes each file path
func (f *Finder) EachPath(fn func(filePath string))

// EachFile processes each file as *os.File
func (f *Finder) EachFile(fn func(file *os.File))
```

#### Configuration Methods
```go
// AddScan adds directories to scan
func (f *Finder) AddScan(dirs ...string) *Finder

// IncludeExt includes files with extensions
func (f *Finder) IncludeExt(exts ...string) *Finder

// ExcludeDir excludes directories
func (f *Finder) ExcludeDir(names ...string) *Finder

// SetMaxDepth sets maximum scan depth
func (f *Finder) SetMaxDepth(depth int) *Finder
```

### Built-in Matchers

#### File Content Matchers
- `MatchExt(exts ...string)` - Match file extensions
- `MatchName(names ...string)` - Match file/directory names
- `MatchPrefix(prefixes ...string)` - Match name prefixes
- `MatchSuffix(suffixes ...string)` - Match name suffixes
- `GlobMatch(patterns ...string)` - Match using glob patterns
- `RegexMatch(pattern string)` - Match using regex

#### File Property Matchers
- `FileSize(min, max uint64)` - Match by file size range
- `HumanSize(expr string)` - Match by human-readable size (>1KB, <5MB)
- `MatchModTime(start, end time.Time)` - Match by modification time
- `HumanModTime(expr string)` - Match by human-readable time (>1d, <1w)

#### Directory Matchers
- `MatchDotDir()` - Match dot directories (.git, .svn)
- `MatchDotFile()` - Match dot files (.gitignore, .env)
- `StartWithDot()` - Match items starting with dot

#### Utility Matchers
- `NameLike(patterns ...string)` - Match names using LIKE patterns
- `MatchPath(subPaths []string)` - Match by path substrings

## Configuration

### Config Structure

```go
type Config struct {
    ScanDirs       []string    // Directories to scan
    FindFlags      FindFlag    // What to find (files/dirs/both)
    MaxDepth       int         // Maximum directory depth
    Concurrency    int         // Number of concurrent workers
    UseAbsPath     bool        // Return absolute paths
    CacheResult    bool        // Cache results
    ExcludeDotDir  bool        // Exclude dot directories
    ExcludeDotFile bool        // Exclude dot files
    
    // Matcher collections
    Matchers       []Matcher   // Generic matchers
    ExMatchers     []Matcher   // Generic exclude matchers
    DirMatchers    []Matcher   // Directory matchers
    DirExMatchers  []Matcher   // Directory exclude matchers
    FileMatchers   []Matcher   // File matchers
    FileExMatchers []Matcher   // File exclude matchers
}
```

### Configuration Options

#### Scan Control
- `MaxDepth`: Limit directory traversal depth (0 = unlimited)
- `Concurrency`: Number of concurrent scanning goroutines
- `UseAbsPath`: Return absolute paths instead of relative

#### Filter Control
- `ExcludeDotDir`: Automatically exclude common dot directories
- `ExcludeDotFile`: Automatically exclude common dot files
- `CacheResult`: Cache results for repeated access

#### Result Type
- `FlagFile`: Find only files (default)
- `FlagDir`: Find only directories
- `FlagBoth`: Find both files and directories

## Development

### Adding Custom Matchers

```go
// Simple function matcher
func CustomExtensionMatcher(ext string) finder.MatcherFunc {
    return func(el finder.Elem) bool {
        return filepath.Ext(el.Path()) == ext
    }
}

// Struct-based matcher
type SizeThresholdMatcher struct {
    minSize int64
}

func (stm SizeThresholdMatcher) Apply(el finder.Elem) bool {
    if el.IsDir() {
        return false
    }
    info, err := el.Info()
    if err != nil {
        return false
    }
    return info.Size() >= stm.minSize
}
```

### Performance Tips

1. **Use appropriate concurrency**: Set `Concurrency` based on your system
2. **Limit scan depth**: Use `MaxDepth` to avoid deep directory trees
3. **Filter early**: Apply exclude filters to reduce processing
4. **Use channels**: For large result sets, use the channel-based API
5. **Enable caching**: For repeated queries on same data

### Error Handling

```go
f := finder.NewFinder("/path")
paths := f.FindPaths()

if f.Err() != nil {
    log.Printf("Finder error: %v", f.Err())
}

fmt.Printf("Found %d items\n", f.Num())
```

## Troubleshooting

### Common Issues

**Q: Finder returns no results**
A: Check if paths exist and you have read permissions. Enable debug mode to see what's happening.

**Q: Performance is slow on large directories**
A: Increase concurrency, limit max depth, or add more specific filters.

**Q: Getting permission denied errors**
A: Run with appropriate permissions or exclude problematic directories.

**Q: Memory usage is high**
A: Use channel-based iteration instead of collecting all results, or disable caching.

### Debug Mode

```go
f := finder.NewFinder("/path")
f.WithDebug(true)  // Enable debug output
paths := f.FindPaths()
```

## Resources

- [Source Repository](https://github.com/gookit/goutil/tree/master/x/finder)
- [GoDoc Documentation](https://pkg.go.dev/github.com/gookit/goutil/x/finder)
- [Examples Directory](https://github.com/gookit/goutil/tree/master/x/finder/_examples)

### Related Packages

- [goutil/fsutil](https://github.com/gookit/goutil/tree/master/fsutil) - File system utilities
- [goutil/strutil](https://github.com/gookit/goutil/tree/master/strutil) - String utilities
- [goutil/errorx](https://github.com/gookit/goutil/tree/master/errorx) - Enhanced error handling

### Similar Tools

- `find` command (Unix/Linux)
- `fd` - Simple, fast and user-friendly alternative to find
- `ripgrep` - Recursively searches directories for a regex pattern