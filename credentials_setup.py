import getpass
import keyring

credential_name = input(
    "Credential Name: "
)

password = getpass.getpass(
    "Password: "
)

keyring.set_password(
    "RTACBackup",
    credential_name,
    password
)

print("Credential created.")