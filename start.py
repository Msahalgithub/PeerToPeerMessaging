import subprocess
import os

# Number of terminal windows to open
num_windows = 3

# Target directory
target_directory = "/home/your_username/Documents"

# Terminal command (adapt depending on what terminal emulator you use)
terminal_command = ["gnome-terminal", "--working-directory", target_directory]

# Launch terminals
for _ in range(num_windows):
    subprocess.Popen(terminal_command)
