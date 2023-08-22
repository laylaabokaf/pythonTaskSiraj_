import unittest
import queue
import threading
import time
import os
import subprocess
from unittest.mock import patch
from TaskQueueApplication import TaskQueueApplicationClass

# Unit tests for the TaskQueueApplication class
class TestTaskQueueApplication(unittest.TestCase):

    def test_add_task(self):
        stop_app = threading.Event()
        app = TaskQueueApplicationClass(tasks_folder='test_tasks_folder',queue_length = 20,log_file ='test_log_file.txt',event=stop_app)
        app.add_task('task1')
        self.assertEqual(app.task_queue.qsize(), 1)

    def test_process_tasks(self):
        # Mock task_function to avoid subprocess calls during testing
        def mock_task_function(task_id):
            pass
        stop_app = threading.Event()
        app = TaskQueueApplicationClass(tasks_folder='test_tasks_folder',queue_length = 20,log_file ='test_log_file.txt',event=stop_app)
        app.task_function = mock_task_function

        app.add_task('task1')
        app.add_task('task2')

        self.assertEqual(app.task_queue.qsize(), 2)

        # Start the process_tasks thread
        task_thread = threading.Thread(target=app.process_tasks)
        task_thread.daemon = True
        task_thread.start()


        time.sleep(5)
        self.assertEqual(app.task_queue.qsize(), 0)
        app.stop_app.set() #set event so process_tasks Thread stop waiting for tasks

    def test_watch_folder(self):
        stop_app = threading.Event()
        app = TaskQueueApplicationClass(tasks_folder='test_tasks_folder',queue_length = 20,log_file ='test_log_file.txt',event=stop_app)

        with patch('time.sleep'):  # Mock time.sleep to avoid waiting in tests
            watch_thread = threading.Thread(target=app.watch_folder)
            watch_thread.daemon = True
            watch_thread.start()

            # Simulate the creation of task files in the test folder
            task_file_path = os.path.join('test_tasks_folder', 'task_file.py')
            open(task_file_path, 'w').close()

            time.sleep(3)  # Wait a bit for the watch thread to process the file

            # Check if the task was added to the queue
            self.assertEqual(app.task_queue.qsize(), 1)

            task_found = False
            for task_id in app.task_queue.queue:
                if task_id == 'task_file':
                    task_found = True
                    break

            self.assertTrue(task_found)

            # Stop the watch_thread
            stop_app.set()

            # Clean up: Remove the task file
            os.remove(task_file_path)

    def test_log_task_times(self):
        stop_app = threading.Event()
        app = TaskQueueApplicationClass(tasks_folder='test_tasks_folder',queue_length = 20,log_file ='test_log_file.txt',event=stop_app)
        app.log_task_times('task1', 0.5, 2.5)
        app.log_task_times('task2', 1.5, 3.5)

        with open('test_log_file.txt', 'r') as log_file:
            log_contents = log_file.read()

        self.assertIn("Task 'task1' Completed: Started at 0.5, Ended at 2.5", log_contents)
        self.assertIn("Task 'task2' Completed: Started at 1.5, Ended at 3.5", log_contents)
        open('test_log_file.txt', 'w').close() #Clean-up
if __name__ == '__main__':
    unittest.main()