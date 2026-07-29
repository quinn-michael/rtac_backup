# Create folder with date name
import json
import os
import sys
from datetime import date
from subprocess import Popen, PIPE

def load_config(config_file):
    with open(config_file, "r") as f:
        return json.load(f)

def create_backup_folder(base_path, group_name):
    today = date.today().strftime("%Y-%m-%d")

    backup_folder = os.path.join(base_path, group_name, today)

    os.makedirs(backup_folder, exist_ok=True)

    return backup_folder

def ReadRTAC_function(device, ipaddress, username, password, backup_folder):
    # This script follows the pattern: Define command, print command to screen for
    # the user, execute the command using Popen, capture output and errors, and print
    # the output to the screen for the user.

    command = "AcRtacCmd start"
    print("Command: ", command)
    p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
    output, error = p.communicate()
    print(output)

    # log in to the database before reading the project, default username considered
    command = "AcRtacCmd login -p TAIL admin"
    print("Command: ", command)
    p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
    output, error = p.communicate()
    print(output)

    # Read the project with all advanced items
    command = 'AcRtacCmd read -p {} -v ALL {} {}'.format(password, ipaddress, username)
    print("Command: ", command)
    p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
    output, error = p.communicate()
    print(output)

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

    print(f"Device: {device}")
    print(f"Project: {project}")

    # Back up the project: export as .exp
    command = 'AcRtacCmd exportexp -f "{}\\{}.exp" "{}"'.format(backup_folder, project, project)
    print("Command:", command)
    p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
    output, error = p.communicate()
    print(output)


#config = load_config("config_solar.json")

if len(sys.argv) != 2:
    print("Usage: RTACBackup.exe <config_file>")
    sys.exit(1)

config_file = sys.argv[1]

config = load_config(config_file)


backup_folder = create_backup_folder(
    config["backup_path"],
    config["group_name"]
    )

# Temporary test print
print(f"Backup Folder: {backup_folder}")
print(f"RTAC Count: {len(config['rtacs'])}")

for rtac in config["rtacs"]:

    if not rtac.get("enabled", True):
        continue

    print(f"Processing {rtac['device']}")

    ReadRTAC_function(
        rtac["device"],
        rtac["ip"],
        rtac["username"],
        rtac["password"],
        backup_folder
        )