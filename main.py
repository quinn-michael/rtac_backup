# Create folder with date name
import json
import os
import sys
import logging
from datetime import date
from subprocess import Popen, PIPE

def load_config(config_file):
    with open(config_file, "r") as f:
        return json.load(f)

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
        "rtacs"
    ]

    for field in required_top_level:

        if field not in config:
            raise Exception(
                f"Missing required config field: {field}"
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


if len(sys.argv) != 2:
    print("Usage: RTACBackup.exe <config_file>")
    sys.exit(1)

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

logging.info("RTAC backup started")
logging.info(f"Configuration file: {config_file}")
logging.info(f"Log file: {log_file}")

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

finally:

    try:
        shutdown()

    except Exception as ex:
        logging.warning(
            f"Failed to stop AcSELerator: {ex}"
        )