import configparser
config = configparser.ConfigParser()
# Add the structure to the file we will create
config.add_section('sectionA')
config.set('sectionA', 'MAX_QUEUE_LENGTH', '30')
config.set('sectionA', 'log_task_file_name', 'task_log.txt')
config.set('sectionA', 'tasks_folder', 'tasks_files')

config.add_section('sectionB')
config.set('sectionB', 'MAX_QUEUE_LENGTH', '30')
config.set('sectionB', 'log_task_file_name', 'task_log.txt')
config.set('sectionB', 'tasks_folder', 'tasks_files')
config.set('sectionB', 'max_concurrent_tasks', '3')

# Write the new structure to the new file
with open(r"configfile.ini", 'w') as configfile:
    config.write(configfile)