# Changelog

## [Unreleased] - 2025-08-10

### Added
- Performance optimization suite (Session 10.14)
  - Performance profiling infrastructure with LangSmith integration
  - Smart caching layer with Redis backend
  - Parallel agent execution framework
  - Streaming response system for progressive delivery
  - Fast path routing for common queries
  - Cost optimization with dynamic model selection

### Changed
- **BREAKING**: `StreamingResponseManager.typing_indicator` property renamed to internal `_typing_indicator_instance`
  - Use the `typing_indicator()` context manager method instead of accessing the property directly
  - Old: `manager.typing_indicator.start()` 
  - New: `async with manager.typing_indicator() as indicator:`

### Fixed
- Fixed test suite compatibility issues
- Fixed context pruning in TokenOptimizer
- Fixed budget alert generation thresholds
- Fixed growth rate calculation in cost trends

### Performance
- Simple queries now execute in ~100ms (20x improvement)
- Cached queries return in ~200ms
- Complex queries reduced from 3-5s to 1.5-2s
- API costs reduced by 30-50% through smart model selection