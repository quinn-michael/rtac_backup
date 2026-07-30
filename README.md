# RTAC Backup Utility

A Python utility for performing automated backups of SEL RTAC projects using AcSELerator RTAC Command Line (AcRtacCmd).

The tool is designed to support unattended execution through Windows Task Scheduler and provides centralized backup management, logging, validation, and project cleanup.

---

## Features

### Configuration Management
- JSON-based configuration files
- Support for multiple RTAC groups
- Enable/disable RTACs without removing them from configuration
- Configuration validation before execution

### Connectivity Validation
- ICMP ping connectivity check before attempting backup
- Fast failure for unreachable devices
- Clear logging for connectivity issues

### Backup Management
- Reads RTAC projects using AcRtacCmd
- Exports projects to .exp files
- Organizes backups by group and date

### Project Cleanup
- Removes existing AcSELerator projects before backup
- Prevents duplicate project names (.0, .1, .2, etc.)

### Logging
- Daily log files
- Console and file logging
- Success/failure reporting
- Connectivity and backup status tracking

### Session Management
- Starts AcSELerator session once
- Logs in once
- Cleans up projects
- Processes all configured RTACs
- Shuts down AcSELerator on completion

---

## Requirements

### Software

- Windows 10 or Windows 11
- Python 3.10+
- SEL AcSELerator RTAC
- AcRtacCmd accessible from the system PATH

### Network

The backup host must have:

- Network connectivity to RTAC devices
- Firewall access to RTAC communications
- ICMP (Ping) permitted to RTAC devices

---

## Configuration

Example:

```json
{
    "backup_path": "C:\\RTACBackups",
    "group_name": "Solar",

    "rtacs": [
        {
            "device": "BUR-PPC01",
            "ip": "10.127.219.10",
            "username": "SEL",
            "password": "password",
            "enabled": true
        },
        {
            "device": "BUR-AXION01",
            "ip": "10.127.219.11",
            "username": "SEL",
            "password": "password",
            "enabled": false
        }
    ]
}
```

### Configuration Fields

| Field | Description |
|---------|-------------|
| backup_path | Root backup directory |
| group_name | Backup group name |
| device | Friendly device name |
| ip | RTAC IP address |
| username | RTAC username |
| password | RTAC password |
| enabled | Include device in backup run |

---

## Execution

### Run with Python

```cmd
python main.py config_solar.json
```

### Run as Executable

```cmd
RTACBackup.exe config_solar.json
```

---

## Backup Structure

Example:

```text
C:\RTACBackups
└── Solar
    ├── 2026-07-30
    │   ├── Burdett DAM1 2026.04.exp
    │   └── Burdett DAM2 2024.01.exp
    │
    └── logs
        └── rtac_backup_2026-07-30.log
```

---

## Logging

Log files are stored under:

```text
<backup_path>\<group_name>\logs
```

Example:

```text
C:\RTACBackups\Solar\logs\rtac_backup_2026-07-30.log
```

Example log output:

```text
INFO Validating configuration
INFO Configuration validation passed
INFO Starting backup of BUR-PPC01
INFO BUR-PPC01 connectivity check passed
INFO BUR-PPC01 successfully backed up as Burdett DAM1 2026.04.exp
INFO Projects Removed: 16
INFO Successful: 2
INFO Failed: 0
```

---

## Configuration Validation

The utility validates configuration before starting any backup operations.

Checks include:

- Required configuration fields
- Required RTAC fields
- Duplicate device names
- Duplicate IP addresses
- At least one enabled RTAC

If validation fails, execution stops immediately.

---

## Connectivity Checks

Before attempting a backup, the utility performs a ping test to each enabled RTAC.

If connectivity fails:

- The RTAC is skipped
- An error is logged
- Remaining RTACs continue processing

---

## Backup Workflow

```text
Load Configuration
        ↓
Validate Configuration
        ↓
Create Backup Folder
        ↓
Start AcSELerator
        ↓
Login
        ↓
Clear Existing Projects
        ↓
Connectivity Check
        ↓
Read RTAC
        ↓
Export Project
        ↓
Repeat for Remaining RTACs
        ↓
Summary Logging
        ↓
Stop AcSELerator
```

---

## Version History

### v1.4.0
- Added connectivity pre-checks
- Added RTAC reachability logging

### v1.3.0
- Added configuration validation
- Added duplicate device and IP detection

### v1.2.0
- Added structured logging
- Added export validation
- Added log file management

### v1.1.0
- Added AcSELerator session lifecycle management
- Added project cleanup

### v1.0.0
- Added JSON configuration files
- Added command-line configuration selection
- Added enabled/disabled RTAC support

---

## Future Enhancements

- Backup retention management
- Windows Credential Manager integration
- Email notifications
- Connectivity retry logic
- Detailed backup metrics

