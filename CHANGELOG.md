# Changelog

## v1.5.0

### Added
- Automatic backup retention management.
- Retention_backups configuration setting.
- Cleanup of old backup folders after successful backup runs.
- Retention cleanup logging and reporting.

### Changed
- Retention is now based on backup count instead of retention days.
- Backup folders are sorted by date and the newest backup sets are retained.
- Cleanup runs after successful backup completion to avoid removing restore points before a successful backup is created.

### Improved
- Automatically maintains a fixed number of historical backup sets.
- Preserves non-backup folders such as logs and manual exports.

## v1.4.0

### Added
- Connectivity pre-checks using ICMP ping
- Connectivity status logging for each RTAC
- Fast-fail behavior for unreachable RTACs

### Changed
- Skip backup attempts for RTACs that fail connectivity checks

### Improved
- Faster backup execution when sites are unreachable
- Clearer troubleshooting information in log files

## v1.3.0

### Added
- Configuration validation before backup execution
- Validation for required top-level configuration fields
- Validation for required RTAC fields
- Duplicate device name detection
- Duplicate IP address detection
- Validation to ensure at least one RTAC is enabled
- Configuration validation failure logging

### Changed
- Moved configured and enabled RTAC count logging into configuration validation
- Improved startup sequence so invalid configurations fail before backup folder creation, AcSELerator startup, project cleanup, or RTAC reads

### Fixed
- Prevented full Python tracebacks for configuration validation failures during normal execution

## v1.2.0
### Added
- Structured logging with daily log files
- Log file storage under backup group folders
- Log backup folder
- Log configured and enabled RTAC counts
- Export command success/fail validation
- Password masking in logged read commands
- JSON configuration files for wind and hydro

### Changed
- Replaced console output with logging framework
- Improved backup success and failure reporting
- Improved project cleanup logging

### Fixed
- Prevent false success reporting when export fails
- Prevent RTAC credentials from appearing in logs

## v1.1.0
### Added
- AcSELerator session lifecycle management
- AcSELerator project database cleanup

## v1.0.0

### Added
- JSON configuration files
- Device enabled/disabled flags
- Command-line config selection
- Backup summary reporting
- Connection failure handling

