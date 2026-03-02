# Advanced Finder Techniques

This document covers advanced usage patterns, performance optimization, and sophisticated filtering techniques for the Finder package.

## Advanced Matcher Combinations

### Complex Filter Logic

```go
// Find Go source files that are NOT tests and larger than 1KB
f := finder.NewFinder("/project").
    IncludeExt(".go").
    ExcludeName("*_test.go").
    Add(finder.HumanSize(">1KB"))

// Find configuration files modified recently
f = finder.NewFinder("/app").
    IncludeExt(".yaml", ".yml", ".json").
    Add(finder.HumanModTime("<30d")).
    ExcludeDir("vendor", "node_modules")
```

### Multi-Criteria Matching

```go
// Files that match ANY of these criteria
f := finder.NewFinder("/search").
    Add(
        finder.MatchExt(".go"),
        finder.MatchName("Dockerfile"),
        finder.GlobMatch("Makefile*"),
    )

// Files that match ALL of these criteria
multiMatcher := &finder.MultiMatcher{
    Matchers: []finder.Matcher{
        finder.MatchExt(".log"),
        finder.HumanSize(">1MB"),
        finder.HumanModTime(">7d"),
    },
}
f = finder.NewFinder("/logs").Add(multiMatcher)
```

### Negative Matching

```go
// Find files that DON'T match certain patterns
f := finder.NewFinder("/project").
    // Exclude by extension
    ExcludeExt(".tmp", ".log", ".cache").
    // Exclude by name pattern
    ExcludeName("*.backup", "*.old").
    // Exclude by directory
    ExcludeDir(".git", "node_modules", "vendor")
```

## Custom Matcher Implementation

### Function-based Custom Matchers

```go
// Matcher for files containing specific content
func ContainsTextMatcher(text string) finder.MatcherFunc {
    return func(el finder.Elem) bool {
        if el.IsDir() {
            return false
        }
        
        content, err := os.ReadFile(el.Path())
        if err != nil {
            return false
        }
        
        return strings.Contains(string(content), text)
    }
}

// Usage
f := finder.NewFinder("/docs").
    Add(ContainsTextMatcher("TODO"))
```

### Struct-based Custom Matchers

```go
// Advanced file analyzer matcher
type FileInfoMatcher struct {
    MinLines    int
    HasShebang  bool
    Extensions  []string
}

func (fim FileInfoMatcher) Apply(el finder.Elem) bool {
    if el.IsDir() {
        return false
    }
    
    // Check extension
    if len(fim.Extensions) > 0 {
        ext := filepath.Ext(el.Path())
        found := false
        for _, allowedExt := range fim.Extensions {
            if ext == allowedExt {
                found = true
                break
            }
        }
        if !found {
            return false
        }
    }
    
    // Check content if needed
    if fim.MinLines > 0 || fim.HasShebang {
        content, err := os.ReadFile(el.Path())
        if err != nil {
            return false
        }
        
        lines := strings.Count(string(content), "\n") + 1
        
        // Check minimum lines
        if fim.MinLines > 0 && lines < fim.MinLines {
            return false
        }
        
        // Check shebang
        if fim.HasShebang {
            firstLine := strings.SplitN(string(content), "\n", 2)[0]
            if !strings.HasPrefix(firstLine, "#!") {
                return false
            }
        }
    }
    
    return true
}

// Usage
scriptMatcher := FileInfoMatcher{
    MinLines:   10,
    HasShebang: true,
    Extensions: []string{".sh", ".py", ".pl"},
}

f := finder.NewFinder("/scripts").Add(scriptMatcher)
```

## Performance Optimization

### Concurrency Tuning

```go
import (
    "runtime"
    "github.com/gookit/goutil/x/finder"
)

func optimizedFinder(paths []string) *finder.Finder {
    // Calculate optimal concurrency based on system
    cpuCount := runtime.NumCPU()
    concurrency := cpuCount
    
    // For IO-heavy operations, you might want more goroutines
    if len(paths) > 1000 {
        concurrency = cpuCount * 2
    }
    
    return finder.NewFinder(paths...).
        SetConcurrency(concurrency).
        SetMaxDepth(5)  // Prevent infinite recursion
}
```

### Memory-Efficient Processing

```go
// Process large directories without memory buildup
func processLargeDirectory(rootPath string) {
    f := finder.NewFinder(rootPath).
        SetConcurrency(4).
        WithCache(false)  // Disable caching for memory efficiency
    
    // Process immediately, don't collect all results
    processed := 0
    for elem := range f.Find() {
        processElement(elem)
        processed++
        
        // Optional: periodic reporting
        if processed%1000 == 0 {
            fmt.Printf("Processed %d files...\n", processed)
        }
    }
    
    fmt.Printf("Total processed: %d\n", processed)
}
```

### Selective Scanning Strategy

```go
// Smart scanning with progressive filtering
func smartProjectScanner(projectRoot string) []string {
    var results []string
    
    // Phase 1: Quick exclusion of obvious directories
    phase1 := finder.NewFinder(projectRoot).
        ExcludeDir(".git", "node_modules", "vendor", ".idea", ".vscode").
        SetMaxDepth(1)
    
    // Get candidate directories
    candidateDirs := phase1.FindPaths()
    
    // Phase 2: Detailed scanning of candidates
    for _, dir := range candidateDirs {
        if isRelevantDirectory(dir) {
            detailed := finder.NewFinder(dir).
                IncludeExt(".go", ".md", ".yaml").
                ExcludeName("*_test.go", "*.tmp").
                SetMaxDepth(3)
            
            results = append(results, detailed.FindPaths()...)
        }
    }
    
    return results
}

func isRelevantDirectory(dir string) bool {
    // Custom logic to determine if directory is worth scanning
    // Could check for presence of go.mod, package.json, etc.
    return true
}
```

## Advanced Configuration Patterns

### Dynamic Configuration

```go
type ScanProfile struct {
    Name        string
    Extensions  []string
    ExcludeDirs []string
    MaxDepth    int
    Concurrency int
}

func (sp ScanProfile) ApplyTo(f *finder.Finder) *finder.Finder {
    f = f.SetMaxDepth(sp.MaxDepth).
        SetConcurrency(sp.Concurrency)
    
    if len(sp.Extensions) > 0 {
        f = f.IncludeExt(sp.Extensions...)
    }
    
    if len(sp.ExcludeDirs) > 0 {
        f = f.ExcludeDir(sp.ExcludeDirs...)
    }
    
    return f
}

// Predefined profiles
var (
    GoProjectProfile = ScanProfile{
        Name:        "Go Project",
        Extensions:  []string{".go", ".mod", ".sum"},
        ExcludeDirs: []string{"vendor", ".git"},
        MaxDepth:    10,
        Concurrency: 4,
    }
    
    WebProjectProfile = ScanProfile{
        Name:        "Web Project",
        Extensions:  []string{".js", ".ts", ".jsx", ".tsx", ".html", ".css"},
        ExcludeDirs: []string{"node_modules", "dist", "build", ".git"},
        MaxDepth:    5,
        Concurrency: 2,
    }
)

// Usage
func scanWithProfile(root string, profile ScanProfile) []string {
    f := profile.ApplyTo(finder.NewFinder(root))
    return f.FindPaths()
}
```

### Rule-based Configuration Loading

```go
func loadFinderRules(rulesFile string) (*finder.Config, error) {
    // Parse rules from YAML/JSON file
    // Format example:
    // include:
    //   exts: [.go, .md, .yaml]
    //   names: [go.mod, README.md]
    // exclude:
    //   dirs: [vendor, .git, node_modules]
    //   names: [*_test.go, *.tmp]
    
    config := finder.NewEmptyConfig()
    
    // Load and apply rules
    // This would parse your config file and apply the rules
    
    return config, nil
}
```

## Integration Patterns

### With Other Tools

```go
// Integration with file hashing
func findDuplicateFiles(rootPath string) map[string][]string {
    hashToFiles := make(map[string][]string)
    
    f := finder.NewFinder(rootPath).
        ExcludeDir(".git", "node_modules").
        IncludeExt(".go", ".md", ".txt")
    
    f.EachFile(func(file *os.File) {
        hash := calculateFileHash(file)
        hashToFiles[hash] = append(hashToFiles[hash], file.Name())
        file.Close()
    })
    
    // Filter to only duplicates
    duplicates := make(map[string][]string)
    for hash, files := range hashToFiles {
        if len(files) > 1 {
            duplicates[hash] = files
        }
    }
    
    return duplicates
}

func calculateFileHash(file *os.File) string {
    // Implementation of file hashing
    hasher := sha256.New()
    // ... hash calculation
    return hex.EncodeToString(hasher.Sum(nil))
}
```

### Pipeline Processing

```go
type FileProcessor interface {
    Process(el finder.Elem) error
    Close() error
}

type ProcessingPipeline struct {
    processors []FileProcessor
}

func (pp *ProcessingPipeline) Process(f *finder.Finder) error {
    for elem := range f.Find() {
        for _, processor := range pp.processors {
            if err := processor.Process(elem); err != nil {
                return err
            }
        }
    }
    
    // Close all processors
    for _, processor := range pp.processors {
        if err := processor.Close(); err != nil {
            return err
        }
    }
    
    return nil
}

// Example processors
type CounterProcessor struct {
    count int
}

func (cp *CounterProcessor) Process(el finder.Elem) error {
    cp.count++
    return nil
}

func (cp *CounterProcessor) Close() error {
    fmt.Printf("Processed %d files\n", cp.count)
    return nil
}
```

## Advanced Error Handling

```go
type DetailedErrorHandler struct {
    errors []error
    stats  map[string]int
}

func (eh *DetailedErrorHandler) HandleError(err error, context string) {
    eh.errors = append(eh.errors, fmt.Errorf("%s: %w", context, err))
    eh.stats[context]++
}

func (eh *DetailedErrorHandler) Summary() string {
    if len(eh.errors) == 0 {
        return "No errors occurred"
    }
    
    var summary strings.Builder
    summary.WriteString(fmt.Sprintf("Total errors: %d\n", len(eh.errors)))
    
    for context, count := range eh.stats {
        summary.WriteString(fmt.Sprintf("  %s: %d errors\n", context, count))
    }
    
    return summary.String()
}

// Usage with finder
func robustFinding(rootPath string) ([]string, error) {
    errorHandler := &DetailedErrorHandler{
        stats: make(map[string]int),
    }
    
    f := finder.NewFinder(rootPath)
    
    var results []string
    f.EachElem(func(el finder.Elem) {
        // Your processing logic here
        results = append(results, el.Path())
    })
    
    if err := f.Err(); err != nil {
        errorHandler.HandleError(err, "finder operation")
    }
    
    fmt.Println(errorHandler.Summary())
    return results, nil
}
```

## Testing and Benchmarking

### Comprehensive Test Suite

```go
func TestAdvancedFinderScenarios(t *testing.T) {
    // Setup test directory structure
    tempDir := setupTestDirectories(t)
    defer os.RemoveAll(tempDir)
    
    tests := []struct {
        name     string
        setup    func(*finder.Finder) *finder.Finder
        expected int
        validate func([]string) bool
    }{
        {
            name: "complex filtering",
            setup: func(f *finder.Finder) *finder.Finder {
                return f.
                    IncludeExt(".txt").
                    ExcludeName("secret*").
                    Add(finder.HumanSize(">100B"))
            },
            expected: 2,
            validate: func(paths []string) bool {
                // Validate specific files are found
                return containsPath(paths, "public.txt") && 
                       containsPath(paths, "data.txt")
            },
        },
        // More test cases...
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            f := tt.setup(finder.NewFinder(tempDir))
            results := f.FindPaths()
            
            if len(results) != tt.expected {
                t.Errorf("Expected %d results, got %d", tt.expected, len(results))
            }
            
            if !tt.validate(results) {
                t.Error("Results validation failed")
            }
        })
    }
}
```

### Performance Benchmarking

```go
func BenchmarkFinderPerformance(b *testing.B) {
    testDir := setupBenchmarkDirectory(b)
    
    b.Run("single-threaded", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            f := finder.NewFinder(testDir).SetConcurrency(1)
            _ = f.FindPaths()
        }
    })
    
    b.Run("multi-threaded", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            f := finder.NewFinder(testDir).SetConcurrency(4)
            _ = f.FindPaths()
        }
    })
    
    b.Run("with-filtering", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            f := finder.NewFinder(testDir).
                IncludeExt(".go").
                ExcludeDir("vendor").
                SetConcurrency(4)
            _ = f.FindPaths()
        }
    })
}
```

These advanced techniques will help you leverage the full power of the Finder package for complex file system operations.