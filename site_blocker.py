import datetime
import os

# -------- Settings --------
# site_block = [
#     "www.anydesk.com",
#     "anydesk.com",
#     "www.teamviewer.com",
#     "teamviewer.com",
#     "www.ultraviewer.net",
#     "ultraviewer.net",
#     "www.remotepc.com",
#     "remotepc.com",
#     "get.teamviewer.com",
#     "www.connectwise.com",
#     "connectwise.com",
#     "www.logmein.com",
#     "logmein.com"
# ]

redirect = "127.0.0.1"  # or "0.0.0.0"
host_path = r"C:\Windows\System32\drivers\etc\hosts"
blocklist_file = "blocked_sites.txt"
log_file = "logs/block_log.txt"

# Optional: set an end time for temporary blocking
# You can also remove this if not needed
end_time = datetime.datetime(2025, 7, 31)  # You can modify the date

# -------- Load Sites from File --------
if not os.path.exists(blocklist_file):
    print(f"[ERROR] Blocklist file '{blocklist_file}' not found.")
    exit()

with open(blocklist_file, "r") as f:
    site_block = [line.strip() for line in f if line.strip()]


# -------- Block Logic --------
print("[INFO] Starting site blocker...")

try:
    if datetime.datetime.now() < end_time:
        print("[INFO] Blocking is active.")
        with open(host_path, "r+") as file:
            content = file.read()

            for website in site_block:
                if website in content:
                    print(f"[SKIP] Already blocked: {website}")
                else:
                    file.write(f"{redirect} {website}\n")
                    print(f"[BLOCKED] {website} redirected to {redirect}")
                    
                    # Log to block_log.txt
                    with open(log_file, "a") as log:
                        log.write(f"{website} was BLOCKED at {datetime.datetime.now()}\n")

    else:
        print("[INFO] Blocking time is over. No changes made.")

except PermissionError:
    print("[ERROR] Permission denied. Please run this script as administrator.")
except Exception as e:
    print(f"[ERROR] An unexpected error occurred: {e}")
