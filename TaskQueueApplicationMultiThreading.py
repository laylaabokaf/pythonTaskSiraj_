import queue
import threading
import time
import os
import subprocess
import concurrent.futures

class TaskQueueApplicationMultiThreadingClass:
    def __init__(self, tasks_folder, queue_length, max_concurrent_tasks, log_file, event,debugMode=False):
        self.tasks_folder = tasks_folder
        self.executed_task_names = []
        self.program_start_time = time.time()
        self.task_queue = queue.Queue(queue_length)
        self.max_concurrent_tasks = max_concurrent_tasks
        self.stop_app = event
        self.log_file = log_file
        self.log_lock = threading.Lock()
        self.file_access_lock = threading.Lock()
        self.debugMode = debugMode

    def task_function(self, task_id):
        script_path = f'{self.tasks_folder}/{task_id}.py'
        start_time = time.time() - self.program_start_time
        try:
            output =  subprocess.run(['python', script_path], check=True, capture_output=True)
            print(output.stdout.decode("utf-8"))
            end_time = time.time() - self.program_start_time
            thread_id = threading.get_ident()  # Get the current thread ID
            self.log_task_times(task_id, start_time, end_time, thread_id)
        except subprocess.CalledProcessError:
            self.log_task_times(task_id, 0, -1, threading.get_ident())

    def add_task(self, task_id):
        self.task_queue.put(task_id)

    def process_task(self, task_id):
        self.task_function(task_id)
        self.task_queue.task_done()

    def process_tasks(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_tasks) as executor:
            while not self.stop_app.is_set():
                task_id = self.task_queue.get()
                executor.submit(self.process_task, task_id)

    def watch_folder(self):
        while not self.stop_app.is_set():
            for filename in os.listdir(self.tasks_folder):
                if filename.endswith('.py'):
                    task_id = os.path.splitext(filename)[0]
                    if task_id not in self.executed_task_names:
                        with self.file_access_lock:
                            self.executed_task_names.append(task_id)
                            self.add_task(task_id)
            time.sleep(5)

    def log_task_times(self, task_name, start_time, end_time, thread_id):
        with self.log_lock:
            with open(self.log_file, 'a') as record_file:
                if end_time == -1:
                    record_file.write(f"Thread {thread_id}: Task '{task_name}' Failed\n")
                else:
                    record_file.write(f"Thread {thread_id}: Task '{task_name}' Completed: Started at {start_time}, Ended at {end_time}\n")

    def clear_log_file(self):
        open(self.log_file, 'w').close()

    def run(self):
        task_thread = threading.Thread(target=self.process_tasks)
        task_thread.daemon = True

        watch_folder_thread = threading.Thread(target=self.watch_folder)
        watch_folder_thread.daemon = True

        task_thread.start()
        watch_folder_thread.start()

        return [task_thread,watch_folder_thread]
        #watch_folder_thread.join()
        #self.task_queue.join()
