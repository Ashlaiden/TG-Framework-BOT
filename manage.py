import subprocess
import os
import argparse
import sys

# Get the parent directory of the current file (manage.py)
current = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current)
# Add the parent directory to the Python path
# sys.path.append(parent_dir)


# Address Class for managing path addresses
class Address:
    def __init__(self, current_path):
        self.root = current_path
        self.db = os.path.join(current, 'db')
        self.assets = os.path.join(current, 'assets')
        self.log = os.path.join(current, 'log')
        self.archive = os.path.join(current, 'archive')
        self.bots = os.path.join(current, 'bots')
        self.core = os.path.join(current, 'core')


# Create an instance form Address Model
address = Address(current)

# Addresses
# address = {
#     'root': current,
#     'db': os.path.join(current, 'db'),
#     'assets': os.path.join(current, 'assets'),
#     'log': os.path.join(current, 'log'),
#     'archive': os.path.join(current, 'archive')
# }

files_dir = 'bots'
main_path = os.path.join(current, files_dir)
sys.path.append(address.core)
# python_interpreter = 'python'

# DEBUG OPTION
DEBUG = True
RUNNING = False

# Replace 'python' with the path to your Python interpreter (e.g., 'python.exe')
if DEBUG:
    script_py = 'venv/Scripts/python.exe'
    python_interpreter = os.path.join(current, script_py)
else:
    python_interpreter = 'python'


def all_files(folder_path):
    data_files = list()

    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return data_files

    # Iterate over files in the folder
    # print(f"Files in the folder '{folder_path}':")
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            data = dict()
            data['name'] = file_name
            data['path'] = file_path
            data_files.append(data)
    # print(f'files: {data_files}')

    return data_files


def main():
    parser = argparse.ArgumentParser(description="Manage script for the application")
    parser.add_argument("command", choices=["start"], help="Command to execute")
    parser.add_argument("--port", type=int, help="Port number")

    args = parser.parse_args()

    if args.command == "start":
        # manage.start(args.port)
        run()
    else:
        print("Invalid command. Use 'start'.")


def run():
    files = all_files(folder_path=main_path)
    for file in files:
        subprocess.run([python_interpreter, file['path']])


if __name__ == "__main__":
    # main()
    run()


