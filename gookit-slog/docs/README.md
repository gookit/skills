# slog Documentation

Complete documentation for gookit/slog logging library.

## Documentation Structure

### 📘 [Handlers Guide](HANDLERS.md) - 401 lines
All built-in handlers and their configuration:
- Console, File, Buffered File, Rotate File handlers
- Handler configuration with Config and Builder
- Multiple handlers setup
- Custom handler creation

### 🔧 [Advanced Usage](ADVANCED.md) - 511 lines
Advanced features and customization:
- Custom formatters (Text, JSON)
- Processors for adding fields
- rotatefile package usage
- Integration with web frameworks (Gin, Echo, GORM)
- Buffer writers
- Testing strategies

### 📝 [Practical Examples](EXAMPLES.md) - 608 lines
Real-world usage patterns:
- Web application logging setup
- HTTP request logging
- Microservice logging with tracing
- Background job logging
- Database query logging
- Error tracking with stack traces
- Performance monitoring
- Configuration from YAML

## Quick Navigation

**Getting Started:**
1. Read [main SKILL.md](../SKILL.md) for overview
2. Follow Quick Start examples
3. Explore specific handlers in [HANDLERS.md](HANDLERS.md)

**Common Tasks:**
- Output to file → [HANDLERS.md#filehandler](HANDLERS.md)
- Rotate logs → [HANDLERS.md#rotatefilehandler](HANDLERS.md)
- JSON format → [main SKILL.md](../SKILL.md#json-format)
- Add fields → [main SKILL.md](../SKILL.md#with-fields)
- Custom formatting → [ADVANCED.md#custom-formatters](ADVANCED.md)
- Web logging → [EXAMPLES.md#web-application-logging](EXAMPLES.md)

**By Use Case:**
- **Web Apps**: [EXAMPLES.md](EXAMPLES.md#web-application-logging)
- **Microservices**: [EXAMPLES.md](EXAMPLES.md#microservice-logging)
- **Background Jobs**: [EXAMPLES.md](EXAMPLES.md#background-jobs)
- **Custom Integration**: [ADVANCED.md](ADVANCED.md#integration-patterns)

## Document Stats

| Document | Lines | Focus |
|----------|-------|-------|
| SKILL.md | 331 | Overview, quick start, basics |
| HANDLERS.md | 401 | Handler configuration |
| ADVANCED.md | 511 | Customization, integration |
| EXAMPLES.md | 608 | Real-world patterns |
| **Total** | **1,851** | **Complete coverage** |

Designed for clarity - each document focuses on one topic, avoiding redundancy while providing comprehensive coverage.
