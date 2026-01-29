# GoUtil - timex Package Reference

**Import**: `github.com/gookit/goutil/timex`

Extended time.Time implementation with additional convenience methods and PHP-style date formatting.

## Table of Contents

- [Overview](#overview)
- [Creating Time Objects](#creating-time-objects)
- [Date Arithmetic](#date-arithmetic)
- [Date Boundaries](#date-boundaries)
- [Formatting](#formatting)
- [Parsing](#parsing)
- [Complete Examples](#complete-examples)

---

## Overview

### Features

- PHP-style date format strings (`Y-m-d H:i:s`)
- Convenient date arithmetic methods
- Day/Month/Year boundary calculations
- Enhanced formatting options
- Simple parsing methods
- All standard time.Time methods available

### Installation

```bash
go get github.com/gookit/goutil/timex
```

---

## Creating Time Objects

### Current Time

```go
import "github.com/gookit/goutil/timex"

// Get current time as timex.Time
now := timex.Now()

// From standard time.Time
t := time.Now()
tx := timex.FromTime(t)

// From Unix timestamp
tx := timex.FromUnix(1640000000)

// From date components
tx := timex.FromDate(2024, 1, 15)          // Date only (00:00:00)
tx := timex.FromDateTime(2024, 1, 15, 14, 30, 0)  // Date and time
```

### Special Times

```go
// Today at 00:00:00
today := timex.Today()

// Yesterday
yesterday := timex.Yesterday()

// Tomorrow
tomorrow := timex.Tomorrow()
```

---

## Date Arithmetic

### Add/Subtract Duration

```go
now := timex.Now()

// Add duration
future := now.Add(24 * time.Hour)
future := now.Add(30 * time.Minute)

// Subtract duration
past := now.Sub(2 * time.Hour)
```

### Day Operations

```go
now := timex.Now()

// Days ahead
tomorrow := now.DayAfter(1)
nextWeek := now.DayAfter(7)

// Days ago
yesterday := now.DayAgo(1)
lastWeek := now.DayAgo(7)

// Add days
future := now.AddDay(5)
past := now.AddDay(-5)

// Add hours
later := now.AddHour(3)
earlier := now.AddHour(-2)

// Add minutes
later := now.AddMinute(30)

// Add seconds
later := now.AddSecond(45)
```

### Month and Year Operations

```go
now := timex.Now()

// Add months
nextMonth := now.AddMonth(1)
nextYear := now.AddMonth(12)

// Add years
nextYear := now.AddYear(1)
lastYear := now.AddYear(-1)
```

### Diff Operations

```go
t1 := timex.Now()
t2 := t1.AddDay(5)

// Days between
days := t1.DiffInDays(t2)      // 5
days := t2.DiffInDays(t1)      // -5

// Hours between
hours := t1.DiffInHours(t2)    // 120

// Seconds between
seconds := t1.DiffInSeconds(t2)
```

---

## Date Boundaries

### Day Boundaries

```go
now := timex.Now()  // 2024-01-15 14:30:45

// Start of day (00:00:00)
start := now.DayStart()  // 2024-01-15 00:00:00

// End of day (23:59:59)
end := now.DayEnd()      // 2024-01-15 23:59:59
```

### Week Boundaries

```go
now := timex.Now()

// Start of week (Monday 00:00:00)
weekStart := now.WeekStart()

// End of week (Sunday 23:59:59)
weekEnd := now.WeekEnd()

// Custom week start day
weekStart := now.WeekStartFrom(time.Sunday)
```

### Month Boundaries

```go
now := timex.Now()  // 2024-01-15 14:30:45

// Start of month (first day 00:00:00)
monthStart := now.MonthStart()  // 2024-01-01 00:00:00

// End of month (last day 23:59:59)
monthEnd := now.MonthEnd()      // 2024-01-31 23:59:59
```

### Year Boundaries

```go
now := timex.Now()  // 2024-01-15 14:30:45

// Start of year (Jan 1 00:00:00)
yearStart := now.YearStart()  // 2024-01-01 00:00:00

// End of year (Dec 31 23:59:59)
yearEnd := now.YearEnd()      // 2024-12-31 23:59:59
```

---

## Formatting

### PHP-Style Formatting

```go
now := timex.Now()

// Date formats
now.DateFormat("Y-m-d")              // "2024-01-15"
now.DateFormat("Y/m/d")              // "2024/01/15"
now.DateFormat("d-m-Y")              // "15-01-2024"
now.DateFormat("m/d/Y")              // "01/15/2024"

// Date and time
now.DateFormat("Y-m-d H:i:s")        // "2024-01-15 14:30:45"
now.DateFormat("Y-m-d H:i")          // "2024-01-15 14:30"
now.DateFormat("d/m/Y H:i:s")        // "15/01/2024 14:30:45"

// Time only
now.DateFormat("H:i:s")              // "14:30:45"
now.DateFormat("H:i")                // "14:30"
now.DateFormat("h:i A")              // "02:30 PM"

// Custom formats
now.DateFormat("l, F d, Y")          // "Monday, January 15, 2024"
now.DateFormat("D, M d, Y")          // "Mon, Jan 15, 2024"
```

### PHP Format Reference

| Format | Description | Example |
|--------|-------------|---------|
| Y | 4-digit year | 2024 |
| y | 2-digit year | 24 |
| m | Month (01-12) | 01 |
| n | Month (1-12) | 1 |
| d | Day (01-31) | 15 |
| j | Day (1-31) | 15 |
| H | Hour 24h (00-23) | 14 |
| h | Hour 12h (01-12) | 02 |
| i | Minutes (00-59) | 30 |
| s | Seconds (00-59) | 45 |
| A | AM/PM | PM |
| a | am/pm | pm |
| l | Full weekday | Monday |
| D | Short weekday | Mon |
| F | Full month | January |
| M | Short month | Jan |

### Standard Go Formatting

```go
now := timex.Now()

// Convert to time.Time and use standard Format
t := now.T()
formatted := t.Format("2006-01-02 15:04:05")

// Or use Format directly
formatted := now.Format("2006-01-02")
```

---

## Parsing

### Parse Date Strings

```go
// Parse with PHP-style format
date, err := timex.FromString("2024-01-15", "Y-m-d")
if err != nil {
    // Handle error
}

// Parse datetime
dt, err := timex.FromString("2024-01-15 14:30:45", "Y-m-d H:i:s")

// Parse with different formats
dt, err := timex.FromString("15/01/2024", "d/m/Y")
dt, err := timex.FromString("01-15-2024 14:30", "m-d-Y H:i")
```

### Parse Common Formats

```go
// Parse ISO 8601
date, err := timex.Parse("2024-01-15T14:30:45Z")

// Parse Unix timestamp string
date := timex.FromUnix(1640000000)
```

---

## Complete Examples

### Date Range Calculator

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/timex"
)

func main() {
    // Get date range for last 7 days
    end := timex.Today()
    start := end.DayAgo(7)

    fmt.Println("Last 7 Days:")
    fmt.Printf("Start: %s\n", start.DateFormat("Y-m-d"))
    fmt.Printf("End: %s\n", end.DateFormat("Y-m-d"))

    // Get this month's range
    monthStart := timex.Now().MonthStart()
    monthEnd := timex.Now().MonthEnd()

    fmt.Println("\nThis Month:")
    fmt.Printf("Start: %s\n", monthStart.DateFormat("Y-m-d H:i:s"))
    fmt.Printf("End: %s\n", monthEnd.DateFormat("Y-m-d H:i:s"))

    // Days in month
    days := monthStart.DiffInDays(monthEnd) + 1
    fmt.Printf("Days: %d\n", days)
}
```

### Event Scheduler

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/timex"
)

type Event struct {
    Title string
    Date  *timex.Time
}

func main() {
    now := timex.Now()

    events := []Event{
        {"Team Meeting", now.AddDay(1).Add(9 * time.Hour)},
        {"Project Deadline", now.AddDay(7)},
        {"Conference", now.AddDay(30)},
    }

    fmt.Println("Upcoming Events:")
    for _, event := range events {
        daysUntil := now.DiffInDays(event.Date)
        fmt.Printf("- %s: %s (%d days from now)\n",
            event.Title,
            event.Date.DateFormat("l, F d, Y"),
            daysUntil,
        )
    }
}
```

### Birthday Reminder

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/timex"
)

func main() {
    // Parse birthday
    birthday, _ := timex.FromString("1990-06-15", "Y-m-d")

    now := timex.Now()
    currentYear := now.Year()

    // Next birthday this year
    nextBirthday := timex.FromDate(currentYear, birthday.Month(), birthday.Day())

    // If birthday already passed this year, use next year
    if nextBirthday.Before(now.T()) {
        nextBirthday = timex.FromDate(currentYear+1, birthday.Month(), birthday.Day())
    }

    // Calculate age
    age := currentYear - birthday.Year()
    if now.Month() < birthday.Month() ||
        (now.Month() == birthday.Month() && now.Day() < birthday.Day()) {
        age--
    }

    daysUntil := now.DiffInDays(nextBirthday)

    fmt.Printf("Current Age: %d\n", age)
    fmt.Printf("Next Birthday: %s\n", nextBirthday.DateFormat("l, F d, Y"))
    fmt.Printf("Days Until Birthday: %d\n", daysUntil)
}
```

### Work Hours Tracker

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/timex"
)

type WorkSession struct {
    Start *timex.Time
    End   *timex.Time
}

func (w WorkSession) Duration() int {
    return w.Start.DiffInHours(w.End)
}

func main() {
    now := timex.Now()

    // This week's work sessions
    sessions := []WorkSession{
        {
            Start: now.WeekStart().Add(9 * time.Hour),
            End:   now.WeekStart().Add(17 * time.Hour),
        },
        {
            Start: now.WeekStart().AddDay(1).Add(9 * time.Hour),
            End:   now.WeekStart().AddDay(1).Add(18 * time.Hour),
        },
        {
            Start: now.WeekStart().AddDay(2).Add(9 * time.Hour),
            End:   now.WeekStart().AddDay(2).Add(17 * time.Hour),
        },
    }

    totalHours := 0
    fmt.Println("Work Sessions:")
    for i, session := range sessions {
        hours := session.Duration()
        totalHours += hours
        fmt.Printf("%d. %s - %s (%d hours)\n",
            i+1,
            session.Start.DateFormat("m/d H:i"),
            session.End.DateFormat("H:i"),
            hours,
        )
    }

    fmt.Printf("\nTotal Hours: %d\n", totalHours)
}
```

### Log File Rotation

```go
package main

import (
    "fmt"
    "github.com/gookit/goutil/timex"
    "github.com/gookit/goutil/fsutil"
)

func shouldRotateLog(logPath string, maxAge int) bool {
    if !fsutil.FileExists(logPath) {
        return false
    }

    // Get file modification time
    modTime, err := fsutil.ModTime(logPath)
    if err != nil {
        return false
    }

    fileTime := timex.FromTime(modTime)
    now := timex.Now()

    // Check if file is older than maxAge days
    age := fileTime.DiffInDays(now)
    return age >= maxAge
}

func rotateLogFile(logPath string) string {
    now := timex.Now()
    archiveName := fmt.Sprintf("%s.%s.gz",
        logPath,
        now.DateFormat("Y-m-d"),
    )
    return archiveName
}

func main() {
    logFile := "app.log"

    if shouldRotateLog(logFile, 7) {
        archiveName := rotateLogFile(logFile)
        fmt.Printf("Rotating %s to %s\n", logFile, archiveName)
    } else {
        fmt.Println("Log file is recent, no rotation needed")
    }
}
```

### Time Zone Converter

```go
package main

import (
    "fmt"
    "time"
    "github.com/gookit/goutil/timex"
)

func main() {
    // Create time in local timezone
    local := timex.Now()

    // Convert to different timezones
    locations := map[string]string{
        "New York":  "America/New_York",
        "London":    "Europe/London",
        "Tokyo":     "Asia/Tokyo",
        "Sydney":    "Australia/Sydney",
    }

    fmt.Printf("Local Time: %s\n\n", local.DateFormat("Y-m-d H:i:s"))
    fmt.Println("World Times:")

    for city, tzName := range locations {
        loc, err := time.LoadLocation(tzName)
        if err != nil {
            continue
        }

        cityTime := local.T().In(loc)
        tx := timex.FromTime(cityTime)

        fmt.Printf("%-12s: %s\n", city, tx.DateFormat("Y-m-d H:i:s"))
    }
}
```

---

## Best Practices

### 1. Use Appropriate Methods

```go
// Good: use specific methods
start := now.DayStart()
tomorrow := now.DayAfter(1)

// Avoid: manual calculation
start := timex.FromDate(now.Year(), now.Month(), now.Day())
```

### 2. Handle Time Zones

```go
// Be aware of time zones
local := timex.Now()  // Local timezone
utc := timex.FromTime(time.Now().UTC())  // UTC

// Convert when needed
localTime := timex.FromTime(utcTime.T().Local())
```

### 3. Use PHP Format for Display

```go
// Good: readable format
display := now.DateFormat("Y-m-d H:i:s")

// Good: for parsing
parsed, _ := timex.FromString(dateStr, "Y-m-d")
```

### 4. Consistent Date Storage

```go
// Store as Unix timestamp or ISO 8601 string
timestamp := now.Unix()
iso := now.Format(time.RFC3339)

// Parse back
restored := timex.FromUnix(timestamp)
```

---

## Comparison with Standard Library

### timex vs time.Time

```go
// Standard library
t := time.Now()
tomorrow := t.Add(24 * time.Hour)
start := time.Date(t.Year(), t.Month(), t.Day(), 0, 0, 0, 0, t.Location())

// With timex
tx := timex.Now()
tomorrow := tx.DayAfter(1)
start := tx.DayStart()
```

### Format Comparison

```go
// Go standard format
t.Format("2006-01-02 15:04:05")

// PHP-style format (timex)
tx.DateFormat("Y-m-d H:i:s")
```

---

**Related Documentation:**
- [Main Skill Documentation](SKILL.md)
- [System & CLI Packages](system-cli-packages.md)
- [cflag Reference](cflag-reference.md)
