package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/gookit/goutil/dump"
	"github.com/gookit/goutil/x/finder"
)

// Example demonstrating basic finder usage
func basicExample() {
	fmt.Println("=== Basic Finder Example ===")
	
	// Simple file finding
	f := finder.NewFinder(".").
		IncludeExt(".go").
		ExcludeDir("vendor", ".git")
	
	paths := f.FindPaths()
	fmt.Printf("Found %d Go files:\n", len(paths))
	for i, path := range paths {
		if i >= 5 { // Limit output
			fmt.Println("...")
			break
		}
		fmt.Printf("  %s\n", path)
	}
}

// Example showing advanced filtering
func advancedFilteringExample() {
	fmt.Println("\n=== Advanced Filtering Example ===")
	
	f := finder.NewFinder(".").
		IncludeExt(".go", ".md").
		ExcludeName("*_test.go").
		Add(finder.HumanSize(">1KB")).
		Add(finder.HumanModTime("<30d"))
	
	fmt.Println("Recent files (>1KB, modified within 30 days):")
	f.Each(func(el finder.Elem) {
		info, _ := el.Info()
		modTime := info.ModTime()
		fmt.Printf("  %s (%v)\n", el.Path(), modTime.Format("2006-01-02"))
	})
}

// Example showing custom matcher
func customMatcherExample() {
	fmt.Println("\n=== Custom Matcher Example ===")
	
	// Custom matcher for files containing specific text
	containsTextMatcher := finder.MatcherFunc(func(el finder.Elem) bool {
		if el.IsDir() {
			return false
		}
		
		// Only check text files
		ext := filepath.Ext(el.Path())
		textExts := []string{".go", ".md", ".txt", ".yaml", ".yml", ".json"}
		isTextFile := false
		for _, textExt := range textExts {
			if ext == textExt {
				isTextFile = true
				break
			}
		}
		
		if !isTextFile {
			return false
		}
		
		// Read file content
		content, err := os.ReadFile(el.Path())
		if err != nil {
			return false
		}
		
		// Check if contains "finder"
		return strings.Contains(strings.ToLower(string(content)), "finder")
	})
	
	f := finder.NewFinder(".").
		Add(containsTextMatcher)
	
	fmt.Println("Files containing 'finder':")
	count := 0
	f.EachPath(func(path string) {
		fmt.Printf("  %s\n", path)
		count++
	})
	fmt.Printf("Total: %d files\n", count)
}

// Example showing duplicate file detection
func duplicateDetectionExample() {
	fmt.Println("\n=== Duplicate File Detection Example ===")
	
	// This is a simplified example - real implementation would be more complex
	type fileInfo struct {
		path string
		size int64
	}
	
	// Group files by size first (quick pre-filter)
	sizeMap := make(map[int64][]fileInfo)
	
	f := finder.NewFinder(".").
		WithFlag(finder.FlagFile).
		ExcludeDir(".git", "vendor", "node_modules")
	
	f.EachStat(func(info os.FileInfo, path string) {
		if info.Size() > 1024 { // Only check files > 1KB
			sizeMap[info.Size()] = append(sizeMap[info.Size()], fileInfo{
				path: path,
				size: info.Size(),
			})
		}
	})
	
	// Show files with same sizes (potential duplicates)
	fmt.Println("Files with identical sizes (potential duplicates):")
	duplicateGroups := 0
	for size, files := range sizeMap {
		if len(files) > 1 {
			duplicateGroups++
			fmt.Printf("Size: %d bytes\n", size)
			for _, file := range files {
				fmt.Printf("  %s\n", file.path)
			}
			fmt.Println()
		}
	}
	
	fmt.Printf("Found %d groups of files with identical sizes\n", duplicateGroups)
}

// Example showing performance comparison
func performanceComparisonExample() {
	fmt.Println("\n=== Performance Comparison Example ===")
	
	testDir := "."
	
	// Single threaded
	start := time.Now()
	f1 := finder.NewFinder(testDir).SetConcurrency(1)
	_ = f1.FindPaths()
	singleThreaded := time.Since(start)
	
	// Multi threaded
	start = time.Now()
	f2 := finder.NewFinder(testDir).SetConcurrency(4)
	_ = f2.FindPaths()
	multiThreaded := time.Since(start)
	
	fmt.Printf("Single threaded: %v\n", singleThreaded)
	fmt.Printf("Multi threaded:  %v\n", multiThreaded)
	fmt.Printf("Speedup: %.2fx\n", float64(singleThreaded)/float64(multiThreaded))
}

// Example showing configuration patterns
func configurationPatternsExample() {
	fmt.Println("\n=== Configuration Patterns Example ===")
	
	// Profile-based configuration
	type ScanProfile struct {
		Name        string
		Extensions  []string
		ExcludeDirs []string
		MaxDepth    int
	}
	
	profiles := map[string]ScanProfile{
		"go-project": {
			Name:        "Go Project",
			Extensions:  []string{".go", ".mod", ".sum"},
			ExcludeDirs: []string{"vendor", ".git"},
			MaxDepth:    10,
		},
		"web-project": {
			Name:        "Web Project",
			Extensions:  []string{".js", ".ts", ".jsx", ".tsx", ".html", ".css"},
			ExcludeDirs: []string{"node_modules", "dist", "build", ".git"},
			MaxDepth:    5,
		},
		"docs": {
			Name:        "Documentation",
			Extensions:  []string{".md", ".rst", ".txt", ".pdf"},
			ExcludeDirs: []string{".git"},
			MaxDepth:    3,
		},
	}
	
	// Apply profile
	profile := profiles["go-project"]
	f := finder.NewFinder(".").
		IncludeExt(profile.Extensions...).
		ExcludeDir(profile.ExcludeDirs...).
		SetMaxDepth(profile.MaxDepth)
	
	fmt.Printf("Using profile: %s\n", profile.Name)
	fmt.Printf("Extensions: %v\n", profile.Extensions)
	fmt.Printf("Excluded dirs: %v\n", profile.ExcludeDirs)
	
	paths := f.FindPaths()
	fmt.Printf("Found %d files matching profile\n", len(paths))
}

// Example showing error handling
func errorHandlingExample() {
	fmt.Println("\n=== Error Handling Example ===")
	
	// Test with non-existent directory
	f := finder.NewFinder("/non/existent/path")
	paths := f.FindPaths()
	
	if f.Err() != nil {
		fmt.Printf("Expected error occurred: %v\n", f.Err())
	} else {
		fmt.Printf("Found %d paths (unexpected)\n", len(paths))
	}
	
	// Test with permission issues
	f = finder.NewFinder("/root/protected")
	paths = f.FindPaths()
	
	if f.Err() != nil {
		fmt.Printf("Permission error handled: %v\n", f.Err())
	}
	fmt.Printf("Successfully found %d paths despite errors\n", len(paths))
}

// Example showing integration with other tools
func integrationExample() {
	fmt.Println("\n=== Integration Example ===")
	
	// Find and process files with specific characteristics
	type ProcessResult struct {
		Path      string
		Extension string
		Size      int64
		Lines     int
	}
	
	var results []ProcessResult
	
	f := finder.NewFinder(".").
		IncludeExt(".go").
		ExcludeName("*_test.go").
		Add(finder.HumanSize(">500B"))
	
	f.EachFile(func(file *os.File) {
		defer file.Close()
		
		// Get file info
		info, err := file.Stat()
		if err != nil {
			return
		}
		
		// Count lines
		content, err := os.ReadFile(file.Name())
		if err != nil {
			return
		}
		
		lines := strings.Count(string(content), "\n") + 1
		
		results = append(results, ProcessResult{
			Path:      file.Name(),
			Extension: filepath.Ext(file.Name()),
			Size:      info.Size(),
			Lines:     lines,
		})
	})
	
	fmt.Printf("Processed %d files:\n", len(results))
	for i, result := range results {
		if i >= 3 { // Limit output
			fmt.Println("  ...")
			break
		}
		fmt.Printf("  %s: %d bytes, %d lines\n", 
			result.Path, result.Size, result.Lines)
	}
}

func main() {
	fmt.Println("Finder Package Examples")
	fmt.Println("======================")
	
	// Check if we're in a directory with files to search
	if _, err := os.Stat("."); os.IsNotExist(err) {
		fmt.Println("Please run this example in a directory with files to search")
		return
	}
	
	// Run examples
	basicExample()
	advancedFilteringExample()
	customMatcherExample()
	duplicateDetectionExample()
	performanceComparisonExample()
	configurationPatternsExample()
	errorHandlingExample()
	integrationExample()
	
	fmt.Println("\n=== All Examples Completed ===")
	
	// Show summary
	f := finder.NewFinder(".").IncludeExt(".go")
	goFiles := f.FindPaths()
	fmt.Printf("\nSummary: Found %d Go files in current directory\n", len(goFiles))
	
	// Dump some debug info
	if f.Err() != nil {
		dump.V(f.Err())
	}
	dump.V(f.Num())
}