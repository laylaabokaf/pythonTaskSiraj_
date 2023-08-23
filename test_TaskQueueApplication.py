import unittest
import os
import threading
import time
from unittest.mock import patch
from TaskQueueApplication import TaskQueueApplicationClass

class TestTaskQueueApplication(unittest.TestCase):
    def setUp(self):
        self.tasks_folder = 'test_tasks_folder'
        self.log_file = 'test_log_file.txt'
        self.stop_app = threading.Event()
        self.app = TaskQueueApplicationClass(
            tasks_folder=self.tasks_folder,
            queue_length=20,
            log_file=self.log_file,
            event=self.stop_app
        )

    def tearDown(self):
        self.stop_app.set()  # Set event to stop threads
        time.sleep(1)  # Allow threads to stop
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_add_task(self):
        self.app.add_task('task1')
        self.assertEqual(self.app.task_queue.qsize(), 1)

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
            self.stop_app.set()

            # Clean up: Remove the task file
            os.remove(task_file_path)

    def test_log_task_times(self):
        self.app.log_task_times('task1', 0.5, 2.5)
        self.app.log_task_times('task2', 1.5, 3.5)

        with open(self.log_file, 'r') as log_file:
            log_contents = log_file.read()

        self.assertIn("Task 'task1' Completed: Started at 0.5, Ended at 2.5", log_contents)
        self.assertIn("Task 'task2' Completed: Started at 1.5, Ended at 3.5", log_contents)

    def test_failed_task(self):
        failed_content = """
def thisIsAFailer():
    raise Exception("This task is intentionally designed to fail")
thisIsAFailer()
        """

        tasks_folder = self.tasks_folder

        # Create the failed.py file and write the content to it
        failed_file_path = os.path.join(tasks_folder, "failed.py")
        with open(failed_file_path, "w") as failed_file:
            failed_file.write(failed_content)

        watch_folder_thread = threading.Thread(target=self.app.watch_folder)
        process_tasks_thread = threading.Thread(target=self.app.process_tasks)
        watch_folder_thread.daemon = True
        process_tasks_thread.daemon = True
        watch_folder_thread.start()

        time.sleep(5)

        task_found = False
        for task_id in self.app.task_queue.queue:
            if task_id == 'failed':
                task_found = True
                break

        self.assertTrue(task_found)
        process_tasks_thread.start()

        time.sleep(3)
        self.stop_app.set()  # Set event so process_tasks Thread stops waiting for tasks

        with open(self.log_file, 'r') as log_file:
            log_contents = log_file.read()

        self.assertIn("Task 'failed' Failed", log_contents)
        open(self.log_file, 'w').close()  # Clean-up

        # Clean up: Remove the task file
        os.remove(failed_file_path)
        open(self.log_file, 'w').close()

if __name__ == '__main__':
    unittest.main()
