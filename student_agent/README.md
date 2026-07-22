# AI Lab System Monitoring — Student Workstation Agent

A lightweight, cross-platform Python agent designed to run silently on lab workstations. It collects active applications, active browser tabs (and domains), clipboard updates, USB storage events, CPU/RAM usage, and periodic screenshots. These events are forwarded to the security monitoring center backend.

## Architecture & Data Flow

```
+-----------------------------------------------------------+
|                      STUDENT MACHINE                      |
|                                                           |
|  [System Monitor] [App Monitor] [Browser Tab] [USB] [Clipboard]
|                           |                               |
|                           v                               |
|                  [Event Dispatcher]                       |
|                           |                               |
|              +------------+------------+                  |
|              | (Online)                | (Offline)        |
|              v                         v                  |
|      [POST /activities]        [SQLite Event Queue]       |
+--------------|-------------------------|------------------+
               |                         |
               | (HTTP/JSON)             | (Re-connected Sync)
               v                         v
+-----------------------------------------------------------+
|                      SECURITY BACKEND                     |
+-----------------------------------------------------------+
```

## Features

- **Active App Monitor**: Emits events whenever the active foreground window changes (e.g. `VS Code` -> `Chrome`).
- **Active Browser Monitor**: Decodes active tab titles to track domain names and flags matches in the blocklist (e.g. `chatgpt.com`).
- **USB Storage Detection**: Triggers warnings when USB mass storage devices are mounted.
- **Copy/Paste Monitor**: Detects new copy actions and captures changes to the clipboard.
- **System Metrics**: Emits CPU and RAM usage spikes and logs user idle states.
- **Screenshots**: Captures a full-screen capture every 30 seconds (configurable), resizes it for bandwidth conservation, and saves it locally.
- **Offline Resiliency**: Backed by a thread-safe SQLite queue to store collected logs locally if the network is down. The queue flushes automatically upon reconnection.

## Setup & Installation

### 1. Requirements

Ensure Python 3.8+ is installed on the machine.

Install required dependencies:
```bash
pip install -r requirements.txt
```

*Note on Linux:*
For active window and clipboard capture on Linux, make sure `xdotool` and `xclip` are installed:
```bash
sudo apt-get install xdotool xclip
```

### 2. Configuration

Edit `config.py` to specify the local machine details:

```python
COMPUTER_ID   = "PC-01"            # Unique ID for this station
STUDENT_EMAIL = "student@lab.com"  # Registered student email
STUDENT_PASS  = "password123"      # Student password
SESSION_ID    = ""                 # Leave blank to auto-detect latest session
BACKEND_URL    = "http://localhost:8000"
```

### 3. Run the Agent

Start the agent in the background or terminal:
```bash
python agent.py
```

The agent will authenticate, resolve its student/session details, and begin forwarding events immediately. Logs are printed to stdout and saved to `agent.log`.
