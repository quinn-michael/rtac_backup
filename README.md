# RTAC Backup Utility

A Python utility for performing automated backups of SEL RTAC projects using AcSELerator RTAC Command Line (AcRtacCmd).

The tool is designed to support unattended execution through Windows Task Scheduler and provides centralized backup management, logging, validation, and project cleanup.

Features include:
- Automated RTAC project backups
- Email summary notifications
- Backup retention management
- Connectivity testing
- Credential validation
- Windows Credential Manager integration
- Task Scheduler support
- Service account deployment support

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
- Connectivity-only test mode for validating network access without performing backups.

### Backup Management
- Reads RTAC projects using AcRtacCmd
- Exports projects to .exp files
- Organizes backups by group and date

### Backup Retention
- Automatically removes older backup sets
- Retains a configurable number of backup folders
- Only processes folders matching the YYYY-MM-DD format
- Ignores logs and other non-backup folders
- Runs after successful backup completion

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

### Email Notifications

- Automatic email summary after backup completion.
- Backup log attachment.
- Reports successful and failed devices.
- Indicates project cleanup and retention activity.

---

## Requirements

### Software

- Windows Operating System running on the backup host
- SEL AcSELerator RTAC
- AcRtacCmd accessible from the system PATH
- RTACBackup.exe for automated scheduling
- credentials_setup.exe for adding credentials to Windows Credential Manager on the backup host
- Python 3.10+ (for development or testing)

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
    "retention_backups": 6,

    "smtp_server": "smtphostname.com",
    "smtp_port": 465,
    "smtp_username": "smtp-user",
    "smtp_credential_name": "SMTP-PROD",
    "smtp_sender": "rtac-backups@bluearth.ca",
    
    "notification_recipients": [
        "user@bluearth.ca"
    ],

    "rtacs": [
        {
            "device": "BUR-PPC01",
            "ip": "10.10.10.10",
            "username": "SEL",
            "credential_name": "RTAC-BUR-PPC01"
            "enabled": true
        },
        {
            "device": "BUR-AXION01",
            "ip": "10.10.10.11",
            "username": "SEL",
            "credential_name": "RTAC-BUR-AXION01"
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
| retention_backups| Number of backup sets to retain |
| smtp_server | SMTP server hostname |
| smtp_port | SMTP server port |
| smtp_username | SMTP account username |
| smtp_credential_name | SMTP credential name in Credential Manager |
| smtp_sender | Email sender address |
| notification_recipients | List of notification recipients |
| device | Friendly device name |
| ip | RTAC IP address |
| username | RTAC username |
| credential_name | RTAC credential name in Credential Manager |
| enabled | Include device in backup run |

---

## Execution

### Install Dependencies
```cmd
pip install keyring
```

### Full Backup Run

```cmd
RTACBackup.exe config_solar.json
```

or

```cmd
python main.py config_solar.json
```

Performs:

- Configuration validation
- AcSELerator startup
- Project cleanup
- RTAC backup and export
- Retention cleanup

### Connectivity Test Only

```cmd
RTACBackup.exe config_solar.json --test-connectivity
```

or

```cmd
python main.py config_solar.json --test-connectivity
```

Performs:

- Configuration validation
- RTAC connectivity testing

Does not perform:

- AcSELerator startup
- AcSELerator login
- Project cleanup
- RTAC read operations
- Project exports
- Backup retention cleanup

### Credential Validation

```cmd
RTACBackup.exe config_solar.json --validate-credentials
```

or

```cmd
python main.py config_solar.json --validate-credentials
```

Validates:

- RTAC credentials
- SMTP credentials

Does not perform:

- AcSELerator startup
- AcSELerator login
- Project cleanup
- RTAC read operations
- Project exports
- Backup retention cleanup

---

## Windows Credential Manager

### Why Windows Credential Manager
Passwords are no longer stored in configuration files.
Credentials are stored securely in Windows Credential Manager and referenced by name.

### Create Credentials
On the backup host, run:

```cmd
credentials_setup.exe
```

Example:

```text
Credential Name:
RTAC-BUR-PPC01

Password:
********
```

### Verify Credentials
On the backup host, run

```cmd
RTACBackup.exe config_solar.json --validate-credentials
```

---

## Production Deployment

### Create Service Account
On the Domain Controller, create a service account.

Minimum Requirements:
- Log on as batch job
- Read/write permission to the backup location
- Access Windows Credential Manager entries
- Access to AcRtacCmd

### Initial Setup
Log in as the service account and:
1. Create all RTAC credentials using credentials_setup.exe
2. Create SMTP credentials using credentials_setup.exe
3. Run credential validation using RTACBackup.exe

This ensure Credential Manager entries are stored in the correct user profile.

### Firewall Requirements
The backup host must be permitted to:
1. Ping all RTAC hosts
2. Access the RTAC with the AcSELerator RTAC software (ports)

### Validate Firewall Configuration
Run:
```cmd
RTACBackup.exe config_solar.json --test-connectivity
```

### Validate Credential Manager
Run:
```cmd
RTACBackup.exe config_solar.json --validate-credentials
```

---

## Building RTACBackup Executable

Run the following commands on a computer with Python installed:

### Install PyInstaller

```cmd
pip install pyinstaller
```

### Generate Executable

```cmd
pyinstaller --onefile --name RTACBackup main.py
```

---

## Building RTACBackup Executable

Run the following commands on a computer with Python installed:

### Install PyInstaller

```cmd
pip install pyinstaller
```

### Generate Executable

```cmd
pyinstaller --onefile --name RTACBackup main.py
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

## Backup Retention

The utility can automatically retain a fixed number of backup sets.

Example:

retention_backups = 6

Backup folders:
```text
2026-01-01
2026-02-01
2026-03-01
2026-04-01
2026-05-01
2026-06-01
2026-07-01
2026-08-01
```

After cleanup:
```text
2026-03-01
2026-04-01
2026-05-01
2026-06-01
2026-07-01
2026-08-01
```

Only folders matching the YYYY-MM-DD naming format are considered backup folders.

---

## Connectivity Test Mode

Connectivity test mode allows network access to be verified before performing backups.

Example:

```cmd
RTACBackup.exe config_solar.json --test-connectivity
```

Example output:

```text
INFO Running connectivity test only

INFO Checking connectivity to BUR-PPC01 (10.127.219.10)
INFO BUR-PPC01 connectivity check passed

INFO Checking connectivity to BUR-AXION01 (10.127.219.11)
ERROR BUR-AXION01 connectivity check failed

============================================================
Connectivity Passed: 1
Connectivity Failed: 1
```

This mode is useful for:

- Firewall rule validation
- VPN testing
- New host commissioning
- Network troubleshooting
- Confirming RTAC reachability before scheduled backups

---

## Connectivity Checks

Before attempting a backup, the utility performs a ping test to each enabled RTAC.

If connectivity fails:

- The RTAC is skipped
- An error is logged
- Remaining RTACs continue processing

---

## Email Notifications

The utility can send a summary email after backup completion.

Email content includes:

- Backup group name
- Execution date
- Projects removed
- Backup folders removed
- Successful backup count
- Failed backup count
- Failed device details

The daily log file is attached to the email.

Example Subject:

```text
RTAC Backup Summary - Solar - Success
```

Example Summary:

```text
RTAC Backup Summary

Group: Solar
Date: 2026-07-30

Projects Removed: 1
Backup Folders Removed: 0

Successful: 4
Failed: 0
```

---

## Backup Workflow

### Full Backup Mode

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
Cleanup Old Backup Sets
        ↓
Summary Logging
        ↓
Send Summary Email
        ↓
Stop AcSELerator
```

### Connectivity Test Mode

```text
Load Configuration
        ↓
Validate Configuration
        ↓
Connectivity Check
        ↓
Summary Logging
        ↓
Exit
```

---

## Version History

### v1.8.0
- Windows Credential Manager support for RTAC and SMTP credentials
- Added validate-configuration test mode
- Added --validate-configuration command-line option

### v1.7.0
- Added email notifications
- Added backup summary emails
- Added log file email attachments
- Added failed device reporting

### v1.6.0
- Added connectivity-only test mode
- Added --test-connectivity command-line option
- Added connectivity summary reporting

### v1.5.0
- Added backup retention management
- Added retention_backups configuration option
- Added automatic cleanup of old backup folders

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

- Push to Sharepoint with Microsoft Graph
- Connectivity retry logic
- Detailed backup metrics

