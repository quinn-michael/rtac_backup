# Changelog

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

