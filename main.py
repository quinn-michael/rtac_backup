# Create folder with date name
import os
from datetime import date


def create_folder_with_date():
    today = date.today()
    global folder_name
    # Format the date in YYYY-MM-DD
    folder_name = today.strftime("%Y-%m-%d")

    # Create a new directory with today's date
    try:
        os.mkdir(folder_name)
        print(f"Directory '{folder_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{folder_name}' already exists.")


# Read RTAC Project and backup
from subprocess import Popen, PIPE


def ReadRTAC_function(ipaddress, username, password):
    backup_path = 'C:\\Users\\gurwinder.singh\\Documents\\Backups\\Solar Project\\{}\\'.format(folder_name)

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
    lines = output.split('\n')
    for line in lines:
        # Look for a line containing "Project '"
        if "Project '" in line:
            items = line.split("'")
            project = items[1]
            # Project name found. Break out of the for loop.
            break
    # Back up the project: export as .exp
    command = 'AcRtacCmd exportexp -f "{}\\{}.exp" "{}"'.format(backup_path, project, project)
    print("Command:", command)
    p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
    output, error = p.communicate()
    print(output)


create_folder_with_date()
## Goodlight Solar RTU
ReadRTAC_function("10.127.90.13", "beam_ops", "NuclearOps$2063")
