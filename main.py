# Create folder with date name
import json
import os
import sys
import logging
import shutil
import smtplib
from datetime import date, datetime
from subprocess import Popen, PIPE, run
from email.message import EmailMessage

def load_config(config_file):
    with open(config_file, "r") as f:
        return json.load(f)

def cleanup_old_backups(
    base_path,
    group_name,
    retention_backups
):

    backup_root = os.path.join(
        base_path,
        group_name
    )

    if not os.path.exists(backup_root):

        logging.info(
            "Backup root does not exist"
        )

        return 0

    backup_folders = []

    for entry in os.listdir(backup_root):

        folder_path = os.path.join(
            backup_root,
            entry
        )

        if not os.path.isdir(folder_path):
            continue

        try:

            folder_date = datetime.strptime(
                entry,
                "%Y-%m-%d"
            )

            backup_folders.append(
                (folder_date, folder_path)
            )

        except ValueError:

            logging.debug(
                f"Skipping folder: {entry}"
            )

            continue

    logging.info(
        f"Found {len(backup_folders)} backup folders"
    )

    logging.info(
        f"Retention count: {retention_backups}"
    )

    backup_folders.sort()

    if len(backup_folders) <= retention_backups:

        logging.info(
            "No backup folders require removal"
        )

        return 0

    folders_to_delete = backup_folders[
        :-retention_backups
    ]

    logging.info(
        f"Backup folders to remove: "
        f"{len(folders_to_delete)}"
    )

    deleted_count = 0

    for folder_date, folder_path in folders_to_delete:

        logging.info(
            f"Removing backup folder: {folder_path}"
        )

        shutil.rmtree(folder_path)

        deleted_count += 1

    logging.info(
        f"Removed {deleted_count} "
        f"old backup folders"
    )

    return deleted_count

def clear_projects():

    command = "AcRtacCmd list"

    p = Popen(
        command,
        stdout=PIPE,
        stdin=PIPE,
        stderr=PIPE,
        universal_newlines=True
    )

    output, error = p.communicate()

    projects = []

    for line in output.splitlines():

        line = line.strip()

        if (
            not line
            or line.startswith("|")
            or line.startswith("-")
            or line.startswith("list:")
        ):
            continue

        project_name = line.rsplit(":", 2)[0]

        projects.append(project_name)

    logging.info(
        f"Found {len(projects)} existing projects"
    )

    for project in projects:

        logging.info(
            f"Deleting project: {project}"
        )

        command = f'AcRtacCmd delete "{project}"'

        p = Popen(
            command,
            stdout=PIPE,
            stdin=PIPE,
            stderr=PIPE,
            universal_newlines=True
        )

        output, error = p.communicate()

        logging.info(output.strip())

    return len(projects)

def connectivity_check(device, ipaddress):

    logging.info(
        f"Checking connectivity to {device} ({ipaddress})"
    )

    result = run(
        ["ping", "-n", "1", ipaddress],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:

        logging.info(
            f"{device} connectivity check passed"
        )

        return True

    logging.error(
        f"{device} connectivity check failed ({ipaddress})"
    )

    return False

def create_backup_folder(base_path, group_name):
    today = date.today().strftime("%Y-%m-%d")

    backup_folder = os.path.join(base_path, group_name, today)

    os.makedirs(backup_folder, exist_ok=True)

    return backup_folder

def read_and_backup_rtac(device, ipaddress, username, password, backup_folder):

    logging.info(
        f"Starting backup of {device}"
    )

    # Read the project with all advanced items
    command = 'AcRtacCmd read -p {} -v ALL {} {}'.format(password, ipaddress, username)
    logging.info(
        f"AcRtacCmd read -p ******** "
        f"-v ALL {ipaddress} {username}"
    )

    p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
    output, error = p.communicate()
    logging.info(output.strip())

    # Parse the return message for any errors.
    if "read:0:success" not in output:

        if "Network error" in output:
            raise Exception(
                f"Network connection failed ({ipaddress})")
        if "login parameters correct" in output:
            raise Exception(
                f"Authentication failed ({ipaddress})")
        raise Exception(
            f"AcRtacCmd read failed")

    # To back up and convert the project, find its name in the RTAC response
    # by splitting on the newline character
    project = None
    lines = output.split('\n')
    for line in lines:
        # Look for a line containing "Project '"
        if "Project '" in line:
            items = line.split("'")
            project = items[1]
            # Project name found. Break out of the for loop.
            break

    if project is None:
        raise Exception(
            f"Unable to determine project name from {device}"
            ) 

    logging.info(
        f"{device} mapped to project '{project}'"
    )

    # Back up the project: export as .exp
    command = 'AcRtacCmd exportexp -f "{}\\{}.exp" "{}"'.format(backup_folder, project, project)
    logging.info(f"Command: {command}")

    p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
    output, error = p.communicate()
    logging.info(output.strip())

    if "exportexp:0:success" not in output:
        raise Exception(
            f"Project export failed ({project})\n{output}"
        )

    logging.info(
        f"{device} successfully backed up as "
        f"{project}.exp"
    )

def run_connectivity_test(config):

    passed = 0
    failed = 0

    for rtac in config["rtacs"]:

        if not rtac.get("enabled", True):
            continue

        if connectivity_check(
            rtac["device"],
            rtac["ip"]
        ):
            passed += 1
        else:
            failed += 1

    logging.info("=" * 60)
    logging.info(
        f"Connectivity Passed: {passed}"
    )
    logging.info(
        f"Connectivity Failed: {failed}"
    )

    return failed

def send_summary_email(
    config,
    log_file,
    success_count,
    failure_count,
    deleted_projects,
    deleted_backup_folders,
    results
):

    subject_status = (
        "Success"
        if failure_count == 0
        else "Failures Detected"
    )

    subject = (
        f"RTAC Backup Summary - "
        f"{config['group_name']} - "
        f"{subject_status}"
    )

    body = []

    body.append("RTAC Backup Summary")
    body.append("")
    body.append(
        f"Group: {config['group_name']}"
    )
    body.append(
        f"Date: {date.today()}"
    )
    body.append("")
    body.append(
        f"Projects Removed: {deleted_projects}"
    )
    body.append(
        f"Backup Folders Removed: "
        f"{deleted_backup_folders}"
    )
    body.append("")
    body.append(
        f"Successful: {success_count}"
    )
    body.append(
        f"Failed: {failure_count}"
    )

    failed_devices = [
        r for r in results
        if r["status"] == "Failed"
    ]

    if failed_devices:

        body.append("")
        body.append("Failed Devices:")
        body.append("")

        for device in failed_devices:

            body.append(
                f"{device['device']}: "
                f"{device['message']}"
            )

    msg = EmailMessage()

    msg["Subject"] = subject

    msg["From"] = config["smtp_sender"]

    msg["To"] = ", ".join(
        config["notification_recipients"]
    )

    msg.set_content(
        "\n".join(body)
    )

    with open(log_file, "rb") as f:

        msg.add_attachment(
            f.read(),
            maintype="text",
            subtype="plain",
            filename=os.path.basename(log_file)
        )

    server = smtplib.SMTP_SSL(
        config["smtp_server"],
        config["smtp_port"]
    )

    try:

        server.login(
            config["smtp_username"],
            config["smtp_password"]
        )

        server.send_message(msg)

        logging.info(
            "Summary email sent successfully"
        )

    finally:

        server.quit()

def setup_logging(base_path, group_name):

    log_folder = os.path.join(
            base_path,
            group_name,
            "logs"
    )

    os.makedirs(log_folder, exist_ok=True)

    log_file = os.path.join(
        log_folder,
        f"rtac_backup_{date.today().strftime('%Y-%m-%d')}.log"
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    return log_file

def startup():

    command = "AcRtacCmd start"
    logging.info(f"Command: {command}")

    p = Popen(
        command,
        stdout=PIPE,
        stdin=PIPE,
        stderr=PIPE,
        universal_newlines=True
    )

    output, error = p.communicate()

    logging.info(output.strip())

    if "start:0:success" not in output:
        raise Exception("Unable to start AcSELerator RTAC")

    command = "AcRtacCmd login -p TAIL admin"
    logging.info(f"Command: {command}")

    p = Popen(
        command,
        stdout=PIPE,
        stdin=PIPE,
        stderr=PIPE,
        universal_newlines=True
    )

    output, error = p.communicate()

    logging.info(output.strip())

    if "login:0:success" not in output:
        raise Exception("Unable to login to AcSELerator RTAC")

def shutdown():

    command = "AcRtacCmd stop"
    logging.info(f"Command: {command}")

    p = Popen(
        command,
        stdout=PIPE,
        stdin=PIPE,
        stderr=PIPE,
        universal_newlines=True
    )

    output, error = p.communicate()

    logging.info(output.strip())

    if "stop:0:success" not in output:
        raise Exception(
            "Unable to stop AcSELerator RTAC"
        )

def validate_config(config):

    logging.info("Validating configuration")

    required_top_level = [
        "backup_path",
        "group_name",
        "retention_backups",
        "rtacs"
    ]

    for field in required_top_level:

        if field not in config:
            raise Exception(
                f"Missing required config field: {field}"
            )

    if config["retention_backups"] < 1:

        raise Exception(
            "retention_backups must be greater than 0"
        )
    
    required_email_fields = [
        "smtp_server",
        "smtp_port",
        "smtp_username",
        "smtp_password",
        "smtp_sender",
        "notification_recipients"
    ]

    for field in required_email_fields:

        if field not in config:

            raise Exception(
                f"Missing email config field: {field}"
            )

    if not isinstance(config["rtacs"], list):
        raise Exception(
            "Configuration error: RTACs must be a list"
        )

    if len(config["rtacs"]) == 0:
        raise Exception(
            "Configuration error: no RTACs defined"
        )

    enabled_rtacs = [
        rtac
        for rtac in config["rtacs"]
        if rtac.get("enabled", True)
    ]

    if len(enabled_rtacs) == 0:
        raise Exception(
            "Configuration error: no enabled RTACs"
        )

    device_names = set()
    ip_addresses = set()

    required_rtac_fields = [
        "device",
        "ip",
        "username",
        "password"
    ]

    for rtac in config["rtacs"]:

        for field in required_rtac_fields:

            if field not in rtac:
                raise Exception(
                    f"RTAC missing field: {field}"
                )

        if rtac["device"] in device_names:
            raise Exception(
                f"Duplicate device name: {rtac['device']}"
            )

        device_names.add(rtac["device"])

        if rtac["ip"] in ip_addresses:
            raise Exception(
                f"Duplicate IP address: {rtac['ip']}"
            )

        ip_addresses.add(rtac["ip"])

    logging.info(
        f"Configured RTACs: {len(config['rtacs'])}"
    )

    logging.info(
        f"Enabled RTACs: {len(enabled_rtacs)}"
    )

    logging.info(
        "Configuration validation passed"
    )


if len(sys.argv) not in [2, 3]:
    print("Usage: RTACBackup.exe <config_file> [--test-connectivity]")
    sys.exit(1)

if len(sys.argv) == 3 and sys.argv[2] != "--test-connectivity":
    print("Usage: RTACBackup.exe <config_file> [--test-connectivity]")
    print(f"Unknown option: {sys.argv[2]}")
    sys.exit(1)

connectivity_only = (
    len(sys.argv) == 3
    and sys.argv[2] == "--test-connectivity"
)

config_file = sys.argv[1]

config = load_config(config_file)

log_file = setup_logging(
    config["backup_path"],
    config["group_name"]
)

try:
    validate_config(config)
except Exception as ex:
    logging.error(
        f"Configuration validation failed: {ex}"
    )
    sys.exit(1)

logging.info(
    "=" * 60
)

if connectivity_only:
    logging.info("RTAC connectivity test started")
else:
    logging.info("RTAC backup started")

logging.info(f"Configuration file: {config_file}")
logging.info(f"Log file: {log_file}")

if connectivity_only:

    logging.info(
        "Running connectivity test only"
    )

    failed_count = run_connectivity_test(config)

    if failed_count > 0:
        sys.exit(1)

    sys.exit(0)

backup_folder = create_backup_folder(
    config["backup_path"],
    config["group_name"]
    )

logging.info(f"Backup folder: {backup_folder}")

try:

    startup()

    deleted_projects = clear_projects()

    results = []

    for rtac in config["rtacs"]:

        if not rtac.get("enabled", True):
            continue

        logging.info(
            f"Processing {rtac['device']}"
        )

        try:
            if not connectivity_check(
                rtac["device"],
                rtac["ip"]
            ):

                results.append({
                    "device": rtac["device"],
                    "status": "Failed",
                    "message": (
                        f"Connectivity check failed "
                        f"({rtac['ip']})"
                    )
                })

                continue

            read_and_backup_rtac(
                rtac["device"],
                rtac["ip"],
                rtac["username"],
                rtac["password"],
                backup_folder
                )

            results.append({
                "device": rtac["device"],
                "status": "Success",
                "message": ""})

        except Exception as ex:
            logging.error(
                f"{rtac['device']} - {ex}"
            )

            results.append({
                "device": rtac["device"],
                "status": "Failed",
                "message": str(ex)})

    success_count = sum(
        1 for r in results
        if r["status"] == "Success"
    )

    failure_count = sum(
        1 for r in results
        if r["status"] == "Failed"
    )

    deleted_backup_folders = 0

    if success_count > 0:

        deleted_backup_folders = cleanup_old_backups(
            config["backup_path"],
            config["group_name"],
            config["retention_backups"]
        )

    logging.info(
        "=" * 60
    )

    logging.info(
        f"Projects Removed: {deleted_projects}"
    )

    logging.info(
        f"Successful: {success_count}"
    )

    logging.info(
        f"Failed: {failure_count}"
    )

    logging.info(
        f"Backup Folders Removed: "
        f"{deleted_backup_folders}"
    )

    try:
        send_summary_email(
            config,
            log_file,
            success_count,
            failure_count,
            deleted_projects,
            deleted_backup_folders,
            results
        )

    except Exception as ex:
        logging.error(
            f"Failed to send summary email: {ex}"
        )   

finally:

    try:
        shutdown()

    except Exception as ex:
        logging.warning(
            f"Failed to stop AcSELerator: {ex}"
        )