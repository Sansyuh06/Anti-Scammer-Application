import ctypes
from datetime import datetime

# -------- Admin Check --------
if not ctypes.windll.shell32.IsUserAnAdmin():
    print("Please run this script as Administrator!")
    exit()

# -------- File Paths --------
host_path = "C:/Windows/System32/drivers/etc/hosts"
site_list_path = "blocked_sites.txt"

# -------- Read the list from external file --------
try:
    with open(site_list_path, "r") as f:
        site_block = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"File '{site_list_path}' not found!")
    exit()

# -------- Unblock Logic --------
with open(host_path, "r") as file:
    lines = file.readlines()

unblocked_sites = []
new_lines = []

for line in lines:
    if any(site in line for site in site_block):
        unblocked_sites.append(line.strip())
    else:
        new_lines.append(line)

with open(host_path, "w") as file:
    file.writelines(new_lines)

# -------- Log Unblocked Sites --------
with open("logs/block_log.txt", "a") as log_file:
    for entry in unblocked_sites:
        log_file.write(f"{entry} was UNBLOCKED at {datetime.now()}\n")

print("Sites unblocked based on blocked_sites.txt and logged.")
# -------- End of Script --------