# import os
# import time
# from datetime import datetime


# folder_to_watch = os.getcwd()

# # Log file name
# log_file = "folder_log.txt"

# # Get initial list of files
# previous_files = set(os.listdir(folder_to_watch))

# print(f"Monitoring folder: {folder_to_watch}")
# print("Press Ctrl + C to stop\n")

# # Infinite loop for monitoring
# while True:
#     current_files = set(os.listdir(folder_to_watch))

#     # Detect new files
#     created_files = current_files - previous_files
#     # Detect deleted files
#     deleted_files = previous_files - current_files

#     # Log changes
#     if created_files or deleted_files:
#         with open(log_file, "a") as f:
#             f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")

#             for file in created_files:
#                 log_line = f"CREATED: {file}\n"
#                 f.write(log_line)
#                 print(log_line, end="")

#             for file in deleted_files:
#                 log_line = f"DELETED: {file}\n"
#                 f.write(log_line)
#                 print(log_line, end="")

#         # Correlation summary
#         if created_files and deleted_files:
#             print(f"EVENT CORRELATION: {len(created_files)} file(s) created, {len(deleted_files)} deleted\n")

#     # Update the previous state
#     previous_files = current_files

#     # Check every 2 seconds
#     time.sleep(2)

import os
import time
from datetime import datetime

# Folder to watch (current directory)
folder_to_watch = os.getcwd()

# Log file name
log_file = "folder_log.txt"

# Store initial state: filenames with their last modified times
previous_files = {f: os.path.getmtime(f) for f in os.listdir(folder_to_watch)}

print(f"Monitoring folder: {folder_to_watch}")
print("Press Ctrl + C to stop\n")

while True:
    current_files = {f: os.path.getmtime(f) for f in os.listdir(folder_to_watch)}

    # Detect new and deleted files
    created_files = set(current_files) - set(previous_files)
    deleted_files = set(previous_files) - set(current_files)

    # Detect potential renames:
    renamed_pairs = []
    if created_files and deleted_files:
        # Compare timestamps to match a deleted and created file with same modification time
        for old in deleted_files:
            old_time = previous_files.get(old)
            for new in created_files:
                new_time = current_files.get(new)
                # If modified times match closely, it's likely a rename
                if abs(old_time - new_time) < 0.001:
                    renamed_pairs.append((old, new))
                    break

    # Log events
    if created_files or deleted_files or renamed_pairs:
        with open(log_file, "a") as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")

            # Handle renames first
            for old, new in renamed_pairs:
                log_line = f"RENAMED: {old} -> {new}\n"
                f.write(log_line)
                print(log_line, end="")
                # Remove from created/deleted lists to avoid double logging
                created_files.discard(new)
                deleted_files.discard(old)

            for file in created_files:
                log_line = f"CREATED: {file}\n"
                f.write(log_line)
                print(log_line, end="")

            for file in deleted_files:
                log_line = f"DELETED: {file}\n"
                f.write(log_line)
                print(log_line, end="")

    # Update previous state
    previous_files = current_files

    # Wait 2 seconds before checking again
    time.sleep(2)
