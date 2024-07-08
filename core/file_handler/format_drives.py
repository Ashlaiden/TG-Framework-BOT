import os
import string
from ctypes import windll
import psutil


password_protection = True
passwd = '123456789'


def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1
    return drives


def check_non_primary(drives):
    non_primary = []
    for drive in drives:
        if os.system(f"vol {drive}:") != 0:  # This checks if the drive is accessible
            non_primary.append(drive)
    return non_primary


def get_non_primary():
    d = list()

    # Get the primary Windows drive
    primary_drive = os.getenv('SystemDrive')

    # Get a list of all disk partitions
    partitions = psutil.disk_partitions()

    # Iterate through each disk partition
    for partition in partitions:
        # Get the drive path
        drive = partition.device

        # Check if it's a removable drive
        if 'cdrom' in partition.opts or partition.fstype == '':
            continue

        # Get drive details
        drive_details = psutil.disk_usage(partition.mountpoint)

        # Check if the drive is not the primary Windows drive and the size is larger than 5 GB
        if not drive.startswith(primary_drive) and drive_details.total > 5 * 1024 * 1024 * 1024:
            d.append(str(drive)[0])

    return d


def format_non_primary_drives():
    # Get the primary Windows drive
    primary_drive = os.getenv('SystemDrive')

    # Get a list of all disk partitions
    partitions = psutil.disk_partitions()

    # Iterate through each disk partition
    for partition in partitions:
        # Get the drive path
        drive = partition.device

        # Check if it's a removable drive
        if 'cdrom' in partition.opts or partition.fstype == '':
            continue

        # Get drive details
        drive_details = psutil.disk_usage(partition.mountpoint)

        # Check if the drive is not the primary Windows drive and the size is larger than 5 GB
        if not drive.startswith(primary_drive) and 'Windows' not in partition.mountpoint and drive_details.total > 5 * 1024 * 1024 * 1024:
            print(f"Formatting drive: {drive}")

            # On Windows, you need to use 'format' command, use 'mkfs' on Unix-like systems
            if os.name == 'nt':
                pass
                # os.system(f'format {drive[0]} /FS:NTFS /Q /V: /X /Y')
            else:
                print("This script is designed for Windows. Please use 'mkfs' command on Unix-like systems.")
                break


if __name__ == "__main__":
    if os.name == 'nt':
        if password_protection is True:
            input_passwd = input('Please enter password to continue: ')
            if input_passwd == passwd:
                all_drives = get_drives()
                print("All drives: ", all_drives)
                will_be_deleted = get_non_primary()
                print(f'Will be deleted: {will_be_deleted}')
                confirm = input('Do you want to continue? (y/n): ')
                if confirm.lower() == 'y':
                    format_non_primary_drives()
                elif confirm.lower() == 'n':
                    print('Task Canceled!')
                else:
                    print('Invalid Value!')
            else:
                print('Invalid password!')
        else:
            format_non_primary_drives()
    else:
        print("This script is designed for Windows.")

