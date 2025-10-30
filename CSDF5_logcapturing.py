import os
import time
from datetime import datetime


folder_to_watch = os.getcwd()

# Log file name
log_file = "folder_log.txt"

# Get initial list of files
previous_files = set(os.listdir(folder_to_watch))

print(f"Monitoring folder: {folder_to_watch}")
print("Press Ctrl + C to stop\n")

# Infinite loop for monitoring
while True:
    current_files = set(os.listdir(folder_to_watch))

    # Detect new files
    created_files = current_files - previous_files
    # Detect deleted files
    deleted_files = previous_files - current_files

    # Log changes
    if created_files or deleted_files:
        with open(log_file, "a") as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")

            for file in created_files:
                log_line = f"CREATED: {file}\n"
                f.write(log_line)
                print(log_line, end="")

            for file in deleted_files:
                log_line = f"DELETED: {file}\n"
                f.write(log_line)
                print(log_line, end="")

        # Correlation summary
        if created_files and deleted_files:
            print(f"EVENT CORRELATION: {len(created_files)} file(s) created, {len(deleted_files)} deleted\n")

    # Update the previous state
    previous_files = current_files

    # Check every 2 seconds
    time.sleep(2)
