import threading
import time
from core.log import Log

log_obj = Log('test')
log = log_obj.logger

# Function that takes a while to respond
def long_running_function():
    print("Starting long_running_function")
    while not exit_flag:
        time.sleep(1)
    print("Exiting long_running_function")

# Function to cancel the long_running_function
def cancel_function():
    global exit_flag
    exit_flag = True
    print("Cancellation requested")

# Set up exit flag
exit_flag = False


if __name__ == '__main__':
    log.info('LOG: Starting long_running_function')
    log_obj.archive_log_file()
    log_obj.save_zip_file(log_obj.get_archives_in_zip())
    # Start long_running_function in a separate thread
    thread = threading.Thread(target=long_running_function)
    thread.start()

    # Simulate some time passing
    time.sleep(5)

    # Cancel the long_running_function
    cancel_function()

    # Wait for the thread to finish
    thread.join()
