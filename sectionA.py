import queue
import threading
import time
import os
import subprocess

# Define the maximum length of the queue
MAX_QUEUE_LENGTH = 10

# Define the folder where task files are located
tasks_folder = 'tasks_files'

# Keep track of executed task names
executed_task_names = []

# Record the start time of the program
program_start_time = time.time()

# Clear log file before writing
open('task_log.txt', 'w').close()


app = TaskQueueApplication(tasks_folder='tasks_folder',queue_length=MAX_QUEUE_LENGTH)

# Start the task processing thread
task_thread = threading.Thread(target=app.process_tasks)
task_thread.daemon = True
task_thread.start()

# Start the folder watching thread
watch_folder_thread = threading.Thread(target=app.watch_folder)
watch_folder_thread.start()

# Wait for the tasks to complete
app.task_queue.join()

# Print a message when all tasks are completed
print("All tasks completed")
