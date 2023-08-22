
# Task Queueing Application

The Task Queueing Application is a Python program designed to manage and execute tasks in a queue. It provides a way to add tasks to a queue, process them one at a time, and log their execution times to a file. 

## Design Decisions

### Choice of Task Entering

The application allows tasks to be entered into the queue by watching a designated folder for task files. Whenever a new `.py` file is added to the folder, it is considered a new task and is added to the queue for processing.

### Configuration File (config.ini)

The application utilizes a configuration file named `configfile.ini` to specify various settings.  This design choice enables users to adjust parameters such as the maximum queue length, the log file name, and the tasks folder.

### General Design of the Code

The code is organized into several parts, each fulfilling a specific role:

1. **TaskQueueApplicationClass:** This class encapsulates the core functionality of the application. It handles task execution, adding tasks to the queue, watching the folder for new tasks, logging task times, and clearing the log file.

2. **Threading:** The application employs threading to achieve concurrency. It uses two threads: one for processing tasks (`process_tasks` method) and another for watching the folder for new task files (`watch_folder` method).

3. **Queue:** The application uses a queue from the `queue` module to manage tasks in a first-in-first-out (FIFO) manner. This ensures that tasks are executed in the order they are added to the queue.

4. **Threading Event:** A threading event (`stop_app`) is used to potentially stop the running threads when needed. This enables graceful termination of the application.

5. **Log File:** Task execution times are logged to a log file specified in the configuration. Successful task completions and failures are recorded with timestamps.

6. **Unit Testing:** The code includes basic unit tests to ensure the correctness of various methods in the `TaskQueueApplicationClass`. These tests help validate the behavior of the application's core components.

## Getting Started

1. Create a `configfile.ini` file with appropriate settings for your application.
2. Implement your tasks as `.py` files in the designated tasks folder.
3. Run sectionA.py, which will start processing tasks as they are added to the folder.
4. Run unit test by running the test_TaskQueueApplication.py file




For any further questions or enhancements, please feel free to reach out!


