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

# Define the task processing function
def task_function(task_id):
    # Construct the path to the task script
    script_path = f'{tasks_folder}/{task_id}.py'

    # Print a message indicating that the task has started
    print(f"Task {task_id} started")

    # Record the start time of the task
    start_time = time.time() - program_start_time

    try:
        # Execute the task script using subprocess
        subprocess.run(['python', script_path], check=True)

        # Record the end time of the task
        end_time = time.time() - program_start_time

        # Print a message indicating that the task has completed
        print(f"Task {task_id} completed")

        # Log task times to the task log
        log_task_times(task_id, start_time, end_time)
    except subprocess.CalledProcessError:
        # Print a message if the task fails
        print(f"Task {task_id} failed")

        # Log task times to the task log (failed task)
        log_task_times(task_id, 0, -1)

# Function to add a new task to the queue
def add_task(task_id):
    task_queue.put(task_id)

# Function to process tasks from the queue
def process_tasks():
    while True:
        # Get the next task from the queue
        task_id = task_queue.get()

        # Process the task using the task function
        task_function(task_id)

        # Indicate that the task has been completed
        task_queue.task_done()

# Function to watch the tasks folder for new task files
def watch_folder():
    print(f"Running tasks runner thread with args: {tasks_folder}")
    while True:
        for filename in os.listdir(tasks_folder):
            if filename.endswith('.py'):
                task_id = os.path.splitext(filename)[0]
                if task_id not in executed_task_names:
                    # Mark the task as executed and add it to the queue
                    executed_task_names.append(task_id)
                    add_task(task_id)
                    print(f"Task {task_id} added to the queue from tasks_files folder")
        # Wait before checking the folder again
        time.sleep(5)

# Function to log task execution times
def log_task_times(task_name, start_time, end_time):
    with open('task_log.txt', 'a') as log_file:
        if end_time == -1:
            # Log a failed task
            log_file.write(f"Task '{task_name}' Failed\n")
        else:
            # Log a completed task with start and end times
            log_file.write(f"Task '{task_name}' Completed: Started at {start_time}, Ended at {end_time}\n")

# Create a queue to hold the tasks
task_queue = queue.Queue(MAX_QUEUE_LENGTH)

# Start the task processing thread
task_thread = threading.Thread(target=process_tasks)
task_thread.daemon = True
task_thread.start()

# Start the folder watching thread
watch_folder_thread = threading.Thread(target=watch_folder)
watch_folder_thread.start()

# Wait for the tasks to complete
task_queue.join()

# Print a message when all tasks are completed
print("All tasks completed")
