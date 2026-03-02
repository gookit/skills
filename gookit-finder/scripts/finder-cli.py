#!/usr/bin/env python3
"""
finder-cli.py - Python CLI tool demonstrating Finder package concepts

This script demonstrates how the Go finder package concepts could be 
implemented in Python, serving as a reference for cross-language understanding.
"""

import argparse
import hashlib
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Callable, Dict, Any

class Element:
    """Represents a file or directory element, similar to Go's finder.Elem"""
    
    def __init__(self, path: Path):
        self.path = path
    
    def Path(self) -> str:
        return str(self.path)
    
    def Name(self) -> str:
        return self.path.name
    
    def IsDir(self) -> bool:
        return self.path.is_dir()
    
    def Info(self) -> os.stat_result:
        return self.path.stat()

class Matcher:
    """Base matcher interface"""
    
    def Apply(self, elem: Element) -> bool:
        raise NotImplementedError

class MatcherFunc(Matcher):
    """Function-based matcher"""
    
    def __init__(self, func: Callable[[Element], bool]):
        self.func = func
    
    def Apply(self, elem: Element) -> bool:
        return self.func(elem)

def MatchExt(*exts: str) -> MatcherFunc:
    """Match files by extension"""
    def matcher(elem: Element) -> bool:
        if elem.IsDir():
            return False
        ext = elem.path.suffix.lower()
        return ext in [e.lower() for e in exts]
    return MatcherFunc(matcher)

def MatchName(*names: str) -> MatcherFunc:
    """Match by filename"""
    def matcher(elem: Element) -> bool:
        return elem.Name() in names
    return MatcherFunc(matcher)

def GlobMatch(*patterns: str) -> MatcherFunc:
    """Match using glob patterns"""
    def matcher(elem: Element) -> bool:
        from fnmatch import fnmatch
        name = elem.Name()
        return any(fnmatch(name, pattern) for pattern in patterns)
    return MatcherFunc(matcher)

def HumanSize(expr: str) -> MatcherFunc:
    """Match by human-readable size (>1KB, <5MB, etc.)"""
    def parse_size(size_str: str) -> int:
        units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
        size_str = size_str.upper()
        for unit, multiplier in units.items():
            if size_str.endswith(unit):
                return int(float(size_str[:-len(unit)]) * multiplier)
        return int(size_str)
    
    def matcher(elem: Element) -> bool:
        if elem.IsDir():
            return False
        
        size = elem.Info().st_size
        
        if expr.startswith('>'):
            threshold = parse_size(expr[1:])
            return size > threshold
        elif expr.startswith('<'):
            threshold = parse_size(expr[1:])
            return size < threshold
        elif expr.startswith('>='):
            threshold = parse_size(expr[2:])
            return size >= threshold
        elif expr.startswith('<='):
            threshold = parse_size(expr[2:])
            return size <= threshold
        else:
            target = parse_size(expr)
            return size == target
    
    return MatcherFunc(matcher)

def HumanModTime(expr: str) -> MatcherFunc:
    """Match by human-readable modification time"""
    def parse_time(time_str: str) -> timedelta:
        if time_str.endswith('d'):
            return timedelta(days=int(time_str[:-1]))
        elif time_str.endswith('w'):
            return timedelta(weeks=int(time_str[:-1]))
        elif time_str.endswith('m'):
            return timedelta(days=int(time_str[:-1]) * 30)
        elif time_str.endswith('y'):
            return timedelta(days=int(time_str[:-1]) * 365)
        else:
            return timedelta(days=int(time_str))
    
    def matcher(elem: Element) -> bool:
        mod_time = datetime.fromtimestamp(elem.Info().st_mtime)
        age = datetime.now() - mod_time
        
        if expr.startswith('>'):
            threshold = parse_time(expr[1:])
            return age > threshold
        elif expr.startswith('<'):
            threshold = parse_time(expr[1:])
            return age < threshold
        else:
            threshold = parse_time(expr)
            return age <= threshold
    
    return MatcherFunc(matcher)

class Finder:
    """Main Finder class, similar to Go implementation"""
    
    def __init__(self, *dirs: str):
        self.scan_dirs = [Path(d) for d in dirs]
        self.matchers: List[Matcher] = []
        self.ex_matchers: List[Matcher] = []
        self.max_depth = 0
        self.concurrency = 1
        self.exclude_dot_dir = True
        self.exclude_dot_file = False
        self.find_flags = "file"  # file, dir, both
        
    def Add(self, matcher: Matcher) -> 'Finder':
        """Add a matcher"""
        self.matchers.append(matcher)
        return self
    
    def Exclude(self, matcher: Matcher) -> 'Finder':
        """Add an exclude matcher"""
        self.ex_matchers.append(matcher)
        return self
    
    def IncludeExt(self, *exts: str) -> 'Finder':
        """Include files with specific extensions"""
        return self.Add(MatchExt(*exts))
    
    def ExcludeExt(self, *exts: str) -> 'Finder':
        """Exclude files with specific extensions"""
        return self.Exclude(MatchExt(*exts))
    
    def IncludeName(self, *names: str) -> 'Finder':
        """Include files with specific names"""
        return self.Add(MatchName(*names))
    
    def ExcludeName(self, *names: str) -> 'Finder':
        """Exclude files with specific names"""
        return self.Exclude(MatchName(*names))
    
    def GlobMatch(self, *patterns: str) -> 'Finder':
        """Add glob pattern matching"""
        return self.Add(GlobMatch(*patterns))
    
    def SetMaxDepth(self, depth: int) -> 'Finder':
        """Set maximum directory depth"""
        self.max_depth = depth
        return self
    
    def SetConcurrency(self, concurrency: int) -> 'Finder':
        """Set concurrency level"""
        self.concurrency = concurrency
        return self
    
    def WithFlag(self, flag: str) -> 'Finder':
        """Set what to find (file, dir, both)"""
        self.find_flags = flag
        return self
    
    def _should_exclude(self, elem: Element) -> bool:
        """Check if element should be excluded"""
        for matcher in self.ex_matchers:
            if matcher.Apply(elem):
                return True
        return False
    
    def _should_include(self, elem: Element) -> bool:
        """Check if element should be included"""
        if not self.matchers:
            return True
            
        for matcher in self.matchers:
            if matcher.Apply(elem):
                return True
        return False
    
    def _is_valid_element(self, elem: Element) -> bool:
        """Check if element meets all criteria"""
        # Check exclude matchers first
        if self._should_exclude(elem):
            return False
        
        # Check dot file/directory exclusion
        name = elem.Name()
        if name.startswith('.'):
            if elem.IsDir() and self.exclude_dot_dir:
                return False
            if not elem.IsDir() and self.exclude_dot_file:
                return False
        
        # Check include matchers
        if not self._should_include(elem):
            return False
        
        # Check type flags
        if self.find_flags == "file" and elem.IsDir():
            return False
        if self.find_flags == "dir" and not elem.IsDir():
            return False
            
        return True
    
    def Find(self):
        """Find elements - generator version"""
        for scan_dir in self.scan_dirs:
            if not scan_dir.exists():
                continue
                
            for elem in self._walk_directory(scan_dir, 0):
                if self._is_valid_element(Element(elem)):
                    yield Element(elem)
    
    def FindPaths(self) -> List[str]:
        """Find and return paths as list"""
        return [elem.Path() for elem in self.Find()]
    
    def FindNames(self) -> List[str]:
        """Find and return names as list"""
        return [elem.Name() for elem in self.Find()]
    
    def Each(self, func: Callable[[Element], None]):
        """Process each found element"""
        for elem in self.Find():
            func(elem)
    
    def EachPath(self, func: Callable[[str], None]):
        """Process each found path"""
        for elem in self.Find():
            func(elem.Path())
    
    def _walk_directory(self, directory: Path, depth: int):
        """Walk directory with depth control"""
        if self.max_depth > 0 and depth >= self.max_depth:
            return
            
        try:
            for item in directory.iterdir():
                yield item
                if item.is_dir():
                    yield from self._walk_directory(item, depth + 1)
        except PermissionError:
            pass  # Skip directories we can't access

def find_duplicates(directory: str) -> Dict[str, List[str]]:
    """Find duplicate files by content hash"""
    hash_to_files = defaultdict(list)
    finder = Finder(directory).WithFlag("file")
    
    for elem in finder.Find():
        try:
            with open(elem.Path(), 'rb') as f:
                content = f.read()
                file_hash = hashlib.md5(content).hexdigest()
                hash_to_files[file_hash].append(elem.Path())
        except (IOError, OSError):
            continue
    
    # Return only actual duplicates
    return {hash_val: files for hash_val, files in hash_to_files.items() if len(files) > 1}

def clean_temp_files(directory: str) -> List[str]:
    """Clean temporary files"""
    temp_patterns = ["*.tmp", "*.temp", "*.bak", "*~"]
    removed = []
    
    finder = Finder(directory)
    for pattern in temp_patterns:
        finder.GlobMatch(pattern)
    
    for elem in finder.Find():
        try:
            os.remove(elem.Path())
            removed.append(elem.Path())
        except (IOError, OSError):
            pass
    
    return removed

def main():
    parser = argparse.ArgumentParser(description="Finder CLI Demo")
    parser.add_argument("command", choices=["find", "duplicates", "clean", "stats"])
    parser.add_argument("-d", "--dir", default=".", help="Target directory")
    parser.add_argument("-s", "--size", help="Size filter (e.g., >1KB, <5MB)")
    parser.add_argument("-t", "--time", help="Time filter (e.g., <7d, >1w)")
    parser.add_argument("--ext", action="append", help="File extensions to include")
    parser.add_argument("--exclude-ext", action="append", help="File extensions to exclude")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.command == "find":
        finder = Finder(args.dir)
        
        if args.ext:
            finder.IncludeExt(*args.ext)
        if args.exclude_ext:
            finder.ExcludeExt(*args.exclude_ext)
        if args.size:
            finder.Add(HumanSize(args.size))
        if args.time:
            finder.Add(HumanModTime(args.time))
        
        count = 0
        for elem in finder.Find():
            print(elem.Path())
            count += 1
        
        if args.verbose:
            print(f"\nFound {count} items")
            
    elif args.command == "duplicates":
        duplicates = find_duplicates(args.dir)
        total_duplicates = 0
        
        for hash_val, files in duplicates.items():
            print(f"Hash: {hash_val}")
            for file_path in files:
                print(f"  {file_path}")
                total_duplicates += 1
            print()
        
        print(f"Total duplicate files: {total_duplicates}")
        print(f"Unique file groups: {len(duplicates)}")
        
    elif args.command == "clean":
        removed = clean_temp_files(args.dir)
        print(f"Removed {len(removed)} temporary files:")
        for file_path in removed:
            print(f"  {file_path}")
            
    elif args.command == "stats":
        finder = Finder(args.dir)
        total_files = 0
        total_dirs = 0
        ext_counts = defaultdict(int)
        total_size = 0
        
        for elem in finder.Find():
            if elem.IsDir():
                total_dirs += 1
            else:
                total_files += 1
                ext = elem.path.suffix.lower()
                ext_counts[ext] += 1
                try:
                    total_size += elem.Info().st_size
                except (OSError, IOError):
                    pass
        
        print("=== Directory Statistics ===")
        print(f"Directory: {args.dir}")
        print(f"Total files: {total_files}")
        print(f"Total directories: {total_dirs}")
        print(f"Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
        print("\nFiles by extension:")
        for ext, count in sorted(ext_counts.items(), key=lambda x: x[1], reverse=True):
            if ext:
                print(f"  {ext}: {count}")
            else:
                print(f"  (no extension): {count}")

if __name__ == "__main__":
    main()