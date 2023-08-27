import queue
import threading
import time
import os
import subprocess
import configparser
from TaskQueueApplicationMultiThreading import TaskQueueApplicationMultiThreadingClass


# Read configuration from config.ini file
config_obj = configparser.ConfigParser()
config_obj.read("configfile.ini")
param = config_obj["sectionB"]

# Extract configuration parameters
queue_length = int(param["max_queue_length"])
log_file = param["log_task_file_name"]
tasks_folder = param["tasks_folder"]
max_concurrent_tasks = param["max_concurrent_tasks"]

# Create a threading event to potentially stop the running threads
stop_app = threading.Event()

# Initialize the TaskQueueApplicationMultiThreadingClass
app = TaskQueueApplicationMultiThreadingClass(
    tasks_folder=tasks_folder,
    queue_length=queue_length,
    max_concurrent_tasks=int(max_concurrent_tasks),
    log_file=log_file,
    event=stop_app
)
app.clear_log_file()
try:
    # Run the application
    [task_thread,watch_folder_thread] = app.run()
    watch_folder_thread.join()
    task_queue.join()
except KeyboardInterrupt:
    print("Stopping the application...")
    stop_app.set()  # Set event to stop the application