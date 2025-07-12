# Anti_Scammer Python Project

## Overview

**Anti_Scammer** is a cybersecurity tool built entirely in Python, designed to **protect elderly and less tech-savvy users** from falling victim to online scams and unauthorized access tools. It focuses on:

- Blocking scam-related **remote access websites**
- Detecting and disabling **suspicious services**
- Logging every action for future tracking and transparency

This project is a part of our **minor project submission**, built by a team of 3 students as part of a cybersecurity-focused learning path.

---

## Features

### 1. Website Blocker

- Blocks access to known scammer tools like:
  - `anydesk.com`, `teamviewer.com`, `ultraviewer.net`, etc.
- Modifies Windows `hosts` file to redirect these domains to `127.0.0.1`.
- **Log file maintained** to record every site blocked or unblocked.

### 2. Suspicious Service Detector & Blocker

- Continuously monitors background Windows services.
- If a **new or suspicious service** (like remote-control software) appears:
  - Logs it.
  - Immediately stops and disables it.
- Keywords checked include: `"remote"`, `"connect"`, `"control"`, `"viewer"`, etc.

### 3. Site Unblocker

- Safely unblocks previously blocked domains if needed.
- Restores `hosts` file to clean state.
- Logs every unblock action with timestamp.

---

## Tech Stack

| Component          | Tool                                       |
| ------------------ | ------------------------------------------ |
| Language           | Python 3.x                                 |
| OS Support         | Windows                                    |
| Host File Control  | `os`, `datetime`, `ctypes`                 |
| Service Monitoring | `subprocess`, `time`                       |
| Log Handling       | `with open()` and timestamped `.txt` files |

---

## Project Folder Structure

Anti_Scammer/
│
├── block_sites.py # Blocks known scam websites
├── unblock_sites.py # Unblocks previously blocked websites
├── detect_services.py # Detects & blocks suspicious services
│
├── logs/
│ ├── block_log.txt # Log of blocked/unblocked websites
│ └── service_alert_log.txt # Log of suspicious services detected
│
├── README.md # You’re reading it!

---

## How to Run

1. **Important:** All scripts must be run as **Administrator** (required to modify system files/services).
2. Open command prompt with admin privileges.
3. Run each script individually:
   ```bash
   python block_sites.py
   python detect_services.py
   python unblock_sites.py
   ```
