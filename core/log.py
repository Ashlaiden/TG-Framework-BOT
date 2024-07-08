import logging
import os
import threading
import zipfile
import datetime
from io import BytesIO
from manage import address


class Log:
    def __init__(self, module_name, use_module_name_in_log=False, daily_archive=True, archive_hour=24):
        self.zip_path = None
        self.cleaned = False
        self.archive_hour = archive_hour
        self.have_archive = False
        self.archive_path = None
        self.logging = logging
        self.types = list()
        self.file_loger = None
        self.logger = None
        self.format_conf = None
        self.log_file = None
        self.module_name = module_name
        self.use_module_name_in_log = use_module_name_in_log
        # Define custom logging levels
        self.archive_level = 25
        self.setup_logger()
        self.log_type()
        self.daily_archive = daily_archive
        self.archive_every__()

    def return_logger(self):
        return self.logger

    def return_logging(self):
        return self.logging

    def set_format(self):
        if self.use_module_name_in_log:
            self.format_conf = self.LogFormatter(self.module_name, self.use_module_name_in_log, '%(module_name)s - %(levelname)s - %(asctime)s - %(message)s')
        else:
            self.format_conf = self.LogFormatter(self.module_name, self.use_module_name_in_log, '%(levelname)s - %(asctime)s - %(message)s')
        return self.format_conf

    def create_log_file(self):
        path = address.log
        final_path = path + '\\' + self.module_name + '\\'
        # Extract directory path from the log file path
        directory = os.path.dirname(final_path)
        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        log_file_path = os.path.join(directory, (self.module_name + '.log'))

        # Check if the file already exists
        if not os.path.exists(log_file_path):
            # Create the file
            with open(log_file_path, 'w'):
                pass  # File created successfully

        self.log_file = log_file_path

        return self.log_file

    def setup_logger(self):
        self.logging.addLevelName(self.archive_level, "ARCHIVE")
        # Configure logging
        self.logging.basicConfig(level=self.archive_level)

        # Create a logger
        self.logger = self.logging.getLogger()
        self.logger.setLevel(self.logging.DEBUG)

        self.create_log_file()

        # Create a file handler and set the logging level
        self.file_loger = self.logging.FileHandler(self.log_file)
        self.file_loger.setLevel(self.logging.DEBUG)

        # Create a formatter with custom parameters
        formatter = self.set_format()

        # Add the formatter to the file handler
        self.file_loger.setFormatter(formatter)

        # Add the file handler to the logger
        self.logger.addHandler(self.file_loger)

    def log_file_path(self):
        l_file = self.log_file
        if l_file is not None:
            return l_file
        else:
            self.create_log_file()
            return self.log_file

    def get_logs_by_level(self, log_level):
        logs = []
        with open(self.log_file, 'r') as file:
            for line in file:
                if line.strip():  # Check if the line is not empty
                    log_record = self.logger.makeLogRecord(
                        self.logger.LogRecord(None, None, '', 0, logging.getLevelName(log_level), line.strip(), None))
                    if log_record.levelno == log_level:
                        logs.append(line.strip())
        return logs

    def log_type(self):
        text = 'TypeError: Level not an integer or a valid string: '
        self.types = ['BASIC_FORMAT', 'BufferingFormatter', 'CRITICAL', 'DEBUG', 'ERROR', 'FATAL', 'FileHandler', 'Filter', 'Formatter', 'Handler', 'INFO', 'LogRecord', 'Logger', 'LoggerAdapter', 'NOTSET', 'NullHandler', 'StreamHandler', 'WARN', 'WARNING', 'addLevelName', 'basicConfig', 'captureWarnings', 'critical', 'debug', 'disable', 'error', 'exception', 'fatal', 'getLevelName', 'getLogger', 'getLoggerClass', 'info', 'log', 'makeLogRecord', 'setLoggerClass', 'shutdown', 'warn', 'warning', 'getLogRecordFactory', 'setLogRecordFactory', 'lastResort', 'raiseExceptions', 'getLevelNamesMapping', 'getHandlerByName', 'getHandlerNames']
        return self.types

    def archive_log_file(self):
        from manage import address
        path = address.archive
        self.have_archive = True
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        final_path = path + '\\' + self.module_name + '\\'
        # Extract directory path from the log file path
        directory = os.path.dirname(final_path)
        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.archive_path = directory

        log_filename = os.path.basename(self.log_file)
        new_log_filename = f"{current_date}---{log_filename}"
        archive_log_file_path = os.path.join(directory, new_log_filename)

        # Check if the file already exists
        if os.path.exists(archive_log_file_path):
            # Read the content of the source log file
            with open(self.log_file, 'r') as source_file:
                log_content = source_file.read()

            # Append the content to the end of the destination log file
            with open(archive_log_file_path, 'a') as destination_file:
                destination_file.write(log_content)
        else:
            with open(archive_log_file_path, 'w'):
                pass

            with open(self.log_file, 'r') as source_file:
                log_content = source_file.read()

            # Append the content to the end of the destination log file
            with open(archive_log_file_path, 'a') as destination_file:
                destination_file.write(log_content)

        with open(self.log_file, 'w'):
            pass

        self.logger.log(self.archive_level, f'Log File Archived in archive directory at filename: [{new_log_filename}]')

    def get_archives_in_zip(self, save_zip=False):
        # List all files in the directory
        from manage import address
        self.archive_path = address.archive + '\\' + self.module_name + '\\'
        files = os.listdir(self.archive_path)
        # Check if any file has the .log extension
        if any(file.endswith('.log') for file in files):
            self.have_archive = True  # Call func1 if any .log files exist
        else:
            return None  # Call func2 otherwise
        # Create an in-memory binary data object
        zip_buffer = BytesIO()

        # Create a ZipFile object
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Iterate over files in the log directory
            for root, _, files in os.walk(self.archive_path):
                for file in files:
                    # Get the full path of the file
                    path_of_file = os.path.join(root, file)
                    # Add the file to the zip archive
                    zip_file.write(str(path_of_file), os.path.relpath(str(path_of_file), self.archive_path))

        # Reset the buffer position to the beginning
        zip_buffer.seek(0)

        if save_zip is True:
            print('started...')
            path = address.archive
            self.zip_path = path + '\\' + self.module_name + '\\' + 'zip' + '\\'
            self.remove_with_ext(single_file=False, extension='.zip', dir_path=self.zip_path)
            path = self.save_zip_file(zip_buffer)
            self.remove_with_ext(single_file=False, extension='.log', dir_path=self.archive_path)
            return path

        return zip_buffer

    def remove_with_ext(self, single_file: bool, extension: str = None, dir_path=None, file_path: str = None):
        if single_file is True:
            print(1)
            try:
                print(2)
                os.remove(file_path)
            except FileNotFoundError:
                print(3)
                pass
            # self.cleaned = True
        else:
            print(4)
            files = os.listdir(dir_path)
            print(5)
            if any(file.endswith(f'{extension}') for file in files):
                print(6)
                for root, _, files in os.walk(dir_path):
                    print('a')
                    for file in files:
                        print('b')
                        # Get the full path of the file
                        path_of_file = os.path.join(root, file)
                        if file.endswith(f'{extension}'):
                            print('c')
                            os.remove(path_of_file)
                            print('d')
            self.cleaned = True
            print(7)

    def save_zip_file(self, zip_buffer):
        path = address.archive
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.zip_path = path + '\\' + self.module_name + '\\' + 'zip' + '\\'
        directory = os.path.dirname(self.zip_path)
        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        zip_file_path = self.zip_path + f'{current_date}---{self.module_name}.zip'

        if os.path.exists(zip_file_path):
            init = 1
            new_path = zip_file_path
            while True:
                if os.path.exists(new_path):
                    new_path = self.zip_path + f'{current_date}---{self.module_name}--{init:03}.zip'
                else:
                    zip_file_path = new_path
                    break
                init += 1

        with open(zip_file_path, 'wb') as file:
            file.write(zip_buffer.read())

        return zip_file_path

    def archive_every__(self,):
        def run():
            if self.daily_archive:
                self.archive_log_file()
            # Calculate the time until the next run
            current_time = datetime.datetime.now()
            next_run = (current_time + datetime.timedelta(days=1)).replace(hour=self.archive_hour % 24, minute=0, second=0, microsecond=0)
            delay = (next_run - current_time).total_seconds()
            threading.Timer(delay, run).start()

        # Calculate the delay until the first run
        time_now = datetime.datetime.now()
        if time_now.hour < self.archive_hour:
            # Run today at the specified hour
            first_run = time_now.replace(hour=(self.archive_hour - 1) % 24, minute=59, second=59, microsecond=0)
        else:
            # Run tomorrow at the specified hour
            first_run = (time_now + datetime.timedelta(days=1)).replace(hour=(self.archive_hour - 1) % 24, minute=59, second=59, microsecond=0)
        initial_delay = (first_run - time_now).total_seconds() + 1

        # Start the timer
        threading.Timer(initial_delay, run).start()

    class LogFormatter(logging.Formatter):
        def __init__(self, module_name, use_module_name=False, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.module_name = module_name
            self.use_module_name = use_module_name

        def format(self, record):
            if self.use_module_name:
                record.module_name = self.module_name
            return super().format(record)
