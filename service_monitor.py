import subprocess
import time
from datetime import datetime
import ctypes
import winsound

# Step 1: Get current services
def get_current_services():
    output = subprocess.check_output("sc query type= service state= all", shell=True)
    output = output.decode().splitlines()

    service_names = []
    for line in output:
        if line.strip().startswith("SERVICE_NAME:"):
            name = line.strip().split("SERVICE_NAME:")[1].strip()
            service_names.append(name)

    return service_names

# Step 2: Initial baseline
baseline_services = get_current_services()

# Step 3: Suspicious keywords
suspicious_keywords = ["remote", "control", "viewer", "connect", "hack", "spy", "monitor", "trojan", "malware", "virus"]

# Step 4: Monitor continuously
while True:
    time.sleep(10)  # wait for 10 seconds
    current_services = get_current_services()

    # Simulate a suspicious service for testing (uncomment for test)
    #current_services.append("RemoteHackTool")

    # Compare with baseline
    new_services = [svc for svc in current_services if svc not in baseline_services]

    if new_services:
        for service in new_services:
            lower_name = service.lower()
            if any(keyword in lower_name for keyword in suspicious_keywords):
                print(f"[ALERT] Suspicious service detected: {service}")
                
                # Beep sound
                winsound.Beep(1000, 500)

                # Pop-up alert
                ctypes.windll.user32.MessageBoxW(0, f"Suspicious service detected: {service}", "Anti-Scammer Alert", 1)

                # Log to file
                with open("logs/service_alert_log.txt", "a") as log_file:
                    log_file.write(f"{datetime.now()} - Suspicious service: {service}\n")

                # Try to stop and disable the service
                try:
                    subprocess.call(f"sc stop {service}", shell=True)
                    subprocess.call(f"sc config {service} start= disabled", shell=True)
                    print(f"[BLOCKED] Service '{service}' stopped and disabled.")
                except Exception as e:
                    print(f"[ERROR] Couldn't stop service {service}: {e}")
            else:
                print(f"[INFO] New but not suspicious: {service}")

        # Update baseline to include new services
        baseline_services.extend(new_services)
    else:
        print("No new services detected.")
