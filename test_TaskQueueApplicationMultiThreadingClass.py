import unittest
import os
import threading
import time
from unittest.mock import patch, Mock
from TaskQueueApplicationMultiThreading import TaskQueueApplicationMultiThreadingClass
from io import StringIO


class TestTaskQueueApplicationMultiThreadingClass(unittest.TestCase):
    def setUp(self):
        self.tasks_folder = 'test_tasks_folder'
        #creates a directory specified by self.tasks_folder if it doesn't already exist
        os.makedirs(self.tasks_folder, exist_ok=True)
        self.queue_length = 10
        self.max_concurrent_tasks = 3
        self.log_file = 'test_log_file.txt'
        # Check if the log file exists
        if not os.path.exists(self.log_file):
            # Create an empty log file if it doesn't exist
            with open(self.log_file, 'w') as log_file:
                pass
        self.stop_app = threading.Event()
        self.app = TaskQueueApplicationMultiThreadingClass(
            tasks_folder=self.tasks_folder,
            queue_length=self.queue_length,
            max_concurrent_tasks=self.max_concurrent_tasks,
            log_file=self.log_file,
            event=self.stop_app,
            debugMode = True
        )
        self.app.clear_log_file()
        for filename in os.listdir(self.tasks_folder):
            if filename.endswith('.py'):
               os.remove(os.path.join(self.tasks_folder, filename))

    def tearDown(self):
        self.stop_app.set()  # Stop the application if it's still running
        for filename in os.listdir(self.tasks_folder):
            if filename.endswith('.py'):
               os.remove(os.path.join(self.tasks_folder, filename))
        os.rmdir(self.tasks_folder)
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
    #basic test,task1 added to the queue
    def test_add_task(self):
        self.app.add_task('task1')
        self.assertEqual(self.app.task_queue.qsize(), 1)

    def test_watch_folder(self):
        with patch('time.sleep'):  # Mock time.sleep to avoid waiting in tests
            watch_thread = threading.Thread(target=self.app.watch_folder)
            watch_thread.daemon = True
            watch_thread.start()

            # Simulate the creation of task files in the test folder
            task_file_path = os.path.join(self.tasks_folder, 'task_file.py')
            open(task_file_path, 'w').close()

            time.sleep(3)  # Wait a bit for the watch thread to process the file

            # Check if the task was added to the queue
            task_found = False
            for task_id in self.app.task_queue.queue:
                if task_id == 'task_file':
                    task_found = True
                    break

            self.assertTrue(task_found)

            # Stop the watch_thread
           # os.remove(task_file_path)
            self.stop_app.set()

            # Clean up: Remove the task file
            os.remove(task_file_path)

    def test_process_tasks(self):
        # Mock task_function to avoid subprocess calls during testing
        def mock_task_function(task_id):
            pass
        self.app.task_function = mock_task_function

        self.app.add_task('task1')
        self.app.add_task('task2')

        self.assertEqual(self.app.task_queue.qsize(), 2)

        # Start the process_tasks thread
        task_thread = threading.Thread(target=self.app.process_tasks)
        task_thread.daemon = True
        task_thread.start()

        time.sleep(5)
        self.assertEqual(self.app.task_queue.qsize(), 0)



    def test_log_task_times(self):
        self.app.log_task_times('task1', 1.0, 2.0, 123)
        self.app.log_task_times('task2', 2.0, 3.0, 456)

        with open(self.log_file, 'r') as log_file:
            log_contents = log_file.read()

        self.assertIn("Thread 123: Task 'task1' Completed: Started at 1.0, Ended at 2.0", log_contents)
        self.assertIn("Thread 456: Task 'task2' Completed: Started at 2.0, Ended at 3.0", log_contents)
        self.app.clear_log_file()

    def test_task_execution_and_logging(self):
        # Create a mock task file
        task_content = "import time\ntime.sleep(1)\nprint('Task executed')"
        task_file_path = os.path.join(self.tasks_folder, 'task.py')
        with open(task_file_path, 'w') as f:
            f.write(task_content)
            f.flush()

        # Start the application
        self.app.run()
        time.sleep(2)
        self.stop_app.set()
        # Check if task file was executed and log entry was created
        self.assertTrue(os.path.exists(task_file_path))
        with open(self.log_file, 'r') as f:
            log_contents = f.read()
        self.assertIn("Task 'task' Completed", log_contents)


    def test_concurrent_task_execution(self):
        # Create mock task files
        num_tasks = 5
        for i in range(num_tasks):
            task_content = f"import time\ntime.sleep(1)\nprint('Task {i} executed')"
            task_file_path = os.path.join(self.tasks_folder, f'task{i}.py')
            with open(task_file_path, 'w') as f:
                f.write(task_content)

        # Start the application
        self.app.run()
        time.sleep(3)
        self.stop_app.set()

        # Check if all task files were executed
        for i in range(num_tasks):
            task_file_path = os.path.join(self.tasks_folder, f'task{i}.py')
            self.assertTrue(os.path.exists(task_file_path))
        #____ add to this task another assert , check if the printed oytput are true____

    #if the task number more then the threads number , all the threads work
    def test_threaded_logging(self):
        # Create a single mock task file
        task_content = "import time\ntime.sleep(1)\nprint('Task executed')"
        task_file_path = os.path.join(self.tasks_folder, 'task_check_threads.py')
        with open(task_file_path, 'w') as f:
            f.write(task_content)

        self.app.run()

        # Temporarily add more tasks to ensure multiple threads
        for _ in range(self.max_concurrent_tasks):
            temp_task_path = os.path.join(self.tasks_folder, f'temp_task_{_}.py')
            with open(temp_task_path, 'w') as f:
                f.write(task_content)
                f.flush()

        time.sleep(7)
        self.stop_app.set()

        # Read and analyze the log file
        thread_ids = set()
        with open(self.log_file, 'r') as log_file:
            log_contents = log_file.readlines()

        for line in log_contents:
            if 'Thread' in line:
                thread_id = line.split(':')[0].strip()
                thread_ids.add(thread_id)

        self.assertEqual(len(thread_ids), self.max_concurrent_tasks)

    #every task executed one time by one thread only
    def test_unique_execution(self):
        # Create mock task files
        num_tasks = 10
        for i in range(num_tasks):
            task_content = f"import time\ntime.sleep(1)\nprint('Task{i} executed')"
            task_file_path = os.path.join(self.tasks_folder, f'task{i}.py')
            with open(task_file_path, 'w') as f:
                f.write(task_content)

        # Start the application
        self.app.run()
        time.sleep(10)  # Adjust as needed
        self.stop_app.set()

        # Read the log file and extract executed tasks and threads
        task_executions = {}  # Mapping thread ID to executed tasks
        with open(self.log_file, 'r') as log_file:
            for line in log_file:
                parts = line.strip().split(':')
                thread_id = parts[0].split()[1]
                task = parts[1].split("'")[1].strip()
                if task in task_executions:
                    self.assertEqual(task_executions[task], thread_id,
                                     f"Task '{task}' executed by multiple threads")
                task_executions[task] = thread_id

    #threads work concurrently
    def test_concurrent_execution(self):
        # Create mock task files
        self.app.clear_log_file()
        num_tasks = self.app.max_concurrent_tasks * 3
        for i in range(num_tasks):
            task_content = f"import time\ntime.sleep(1)\nprint('Task{i} executed')"
            task_file_path = os.path.join(self.tasks_folder, f'task{i}.py')
            with open(task_file_path, 'w') as f:
                f.write(task_content)

        # Start the application
        start_time = time.time()
        self.app.run()
        time.sleep(5)  # Adjust as needed
        self.stop_app.set()

        # Read the log file and extract start and end times
        task_times = {}  # Mapping task name to start and end times
        with open(self.log_file, 'r') as log_file:
            for line in log_file:
                parts = line.strip().split(':')
                thread_id = parts[0].split()[1]
                task = parts[1].split("'")[1].strip()
                time_parts = parts[2].split(',')
                start_time = float(time_parts[0].split()[-1])
                end_time = float(time_parts[1].split()[-1])
                task_times[task] = (start_time, end_time)

        # Check that exactly max_concurrent_tasks tasks were executed concurrently
        max_concurrent_execution = self.app.max_concurrent_tasks
        concurrent_executions = [
            sum(
                1 for task, (s, e) in task_times.items() if start_time < e and end_time > s
            )
            for task_name, (start_time, end_time) in task_times.items()
        ]
        print(concurrent_executions)
        self.assertTrue(all(executions >= max_concurrent_execution for executions in concurrent_executions))


    def test_Threads_execute(self):
        # Create mock task files
        mock_tasks = ['task1.py', 'task2.py', 'task3.py']

        for task_file in mock_tasks:
            task_file_path = os.path.join(self.tasks_folder, task_file)
            with open(task_file_path, 'w') as f:
                f.write(f'print("{task_file} executed")')
                f.flush()

        print("before captured_output")
        # Capture printed output
        captured_output = StringIO()

        with patch('sys.stdout', new=captured_output):
            self.app.run()
            time.sleep(3)
            self.stop_app.set()  # Set event to stop threads

            v = captured_output.getvalue()
        print(v)
        captured_output.seek(0)
        output_lines = captured_output.readlines()

        # Check that all tasks were executed
        for task_file in mock_tasks:
            expected_output = f'{task_file} executed\r\n'
            self.assertIn(expected_output, output_lines)



if __name__ == '__main__':
    unittest.main()
