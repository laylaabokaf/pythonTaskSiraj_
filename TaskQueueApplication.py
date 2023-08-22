import queue
import threading
import time
import os
import subprocess
import unittest
from threading import Event

class TaskQueueApplicationClass:
    def __init__(self, tasks_folder, queue_length, log_file, event):
        self.tasks_folder = tasks_folder
        self.executed_task_names = []
        self.program_start_time = time.time()
        self.task_queue = queue.Queue(queue_length)
        self.stop_app = event
        self.log_file = log_file

    def task_function(self, task_id):
        script_path = f'{self.tasks_folder}/{task_id}.py'
        print(f"Task {task_id} started")
        start_time = time.time() - self.program_start_time
        try:
            subprocess.run(['python', script_path], check=True)
            end_time = time.time() - self.program_start_time
            print(f"Task {task_id} completed")
            self.log_task_times(task_id, start_time, end_time)
        except subprocess.CalledProcessError:
            print(f"Task {task_id} failed")
            self.log_task_times(task_id, 0, -1)

    def add_task(self, task_id):
        self.task_queue.put(task_id)

    def process_tasks(self):
        while True:
            task_id = self.task_queue.get()
            self.task_function(task_id)
            self.task_queue.task_done()
            if self.stop_app.is_set():
                break

    def watch_folder(self):
        print(f"Running tasks runner thread with args: {self.tasks_folder}")
        while True:
            for filename in os.listdir(self.tasks_folder):
                if filename.endswith('.py'):
                    task_id = os.path.splitext(filename)[0]
                    if task_id not in self.executed_task_names:
                        self.executed_task_names.append(task_id)
                        self.add_task(task_id)
                        print(f"Task {task_id} added to the queue from tasks_files folder")
            if self.stop_app.is_set():
                break

    def log_task_times(self, task_name, start_time, end_time):
        with open(self.log_file, 'a') as record_file:
            if end_time == -1:
                record_file.write(f"Task '{task_name}' Failed\n")
            else:
                record_file.write(f"Task '{task_name}' Completed: Started at {start_time}, Ended at {end_time}\n")

    def clear_log_file(self):
        # Clear log file before writing
        open(self.log_file, 'w').close()
