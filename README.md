
# Task Queueing Application

The Task Queueing Application is a Python program designed to manage and execute tasks in a queue. It provides a way to add tasks to a queue, process them one at a time, and log their execution times to a file. 

## Design Decisions

### Choice of Task Entering

The application allows tasks to be entered into the queue by watching a designated folder for task files. Whenever a new `.py` file is added to the folder, it is considered a new task and is added to the queue for processing.

### Configuration File (config.ini)

The application utilizes a configuration file named `configfile.ini` to specify various settings. This design choice enables users to adjust parameters such as the maximum queue length, the log file name, and the tasks folder.

### General Design of the Code

The code is organized into several parts, each fulfilling a specific role:

1. **TaskQueueApplicationClass:** This class encapsulates the core functionality of the application for single-threaded execution. It handles task execution, adding tasks to the queue, watching the folder for new tasks, logging task times, and clearing the log file.

2. **TaskQueueApplicationMultiThreadingClass:** This class encapsulates the core functionality of the application for multi-threaded execution. It utilizes threading to process tasks concurrently, while ensuring that the maximum number of tasks are executed concurrently as specified in the configuration.

3. **Threading:** Both versions of the application employ threading to achieve concurrency. They use threads for processing tasks (`process_tasks` method) and for watching the folder for new task files (`watch_folder` method).

4. **Queue:** The application uses a queue from the `queue` module to manage tasks in a first-in-first-out (FIFO) manner. This ensures that tasks are executed in the order they are added to the queue.

5. **Threading Event:** A threading event (`stop_app`) is used to potentially stop the running threads when needed. This enables graceful termination of the application.

6. **Log File:** Task execution times are logged to a log file specified in the configuration. Successful task completions and failures are recorded with timestamps.

7. **Unit Testing:** The code includes unit tests for both `TaskQueueApplicationClass` and `TaskQueueApplicationMultiThreadingClass` to ensure the correctness of their methods. These tests help validate the behavior of the application's core components.

## Getting Started

1. Create a `configfile.ini` file with appropriate settings for your application.
2. Implement your tasks as `.py` files in the designated tasks folder.
3. Run `sectionA.py` for single-threaded execution or `sectionB.py` for multi-threaded execution, both of which will start processing tasks as they are added to the folder. Use CTRL-C to exit program
4. Run unit tests by executing the `test_TaskQueueApplication.py` and `test_TaskQueueApplicationMultiThreadingClass.py` files.

For any further questions or enhancements, please feel free to reach out!