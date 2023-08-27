import queue
import threading
import time
import os
import subprocess
import configparser
from TaskQueueApplication import TaskQueueApplicationClass
import signal
import sys

# Read configuration from config.ini file
config_obj = configparser.ConfigParser()
config_obj.read("configfile.ini")
param = config_obj["sectionA"]

# Extract configuration parameters
MAX_QUEUE_LENGTH = int(param["max_queue_length"])
log_task_file_name = param["log_task_file_name"]
tasks_folder = param["tasks_folder"]

# Create a threading event to potentially stop the running threads
stop_app = threading.Event()

# Initialize the TaskQueueApplicationClass with configuration parameters
app = TaskQueueApplicationClass(
    tasks_folder=tasks_folder,
    queue_length=MAX_QUEUE_LENGTH,
    log_file=log_task_file_name,
    event=stop_app
)

# Clear the log file before starting
app.clear_log_file()

def handler(signal_received, frame):
    stop_app.set()
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)

signal.signal(signal.SIGINT, handler)
# Start the task processing thread
task_thread = threading.Thread(target=app.process_tasks)
task_thread.daemon = True

# Start the folder watching thread
watch_folder_thread = threading.Thread(target=app.watch_folder)
watch_folder_thread.daemon = True

# Start both threads
task_thread.start()
watch_folder_thread.start()

# Wait for the watch_folder thread to terminate
#watch_folder_thread.join()
while True:
     time.sleep(2)
