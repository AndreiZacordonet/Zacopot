
# Zacopot  

## Description

This project is an SSH honeypot written in Python using the Paramiko library. It simulates a Linux shell with a virtual file system and supports a set of common shell commands. The honeypot is designed to monitor and record unauthorized SSH access attempts in a safe and controlled environment.

It also includes a companion application, **`logViewer`**, which runs locally and is used to analyze and process the data collected by the honeypot.

**This project served as the practical foundation for my bachelor's thesis. Since the development took place in a private repository, this public version contains only a limited number of commits.**

---


## Implementation Details

-   **Language:** Python
-   **SSH Server:** Built using the Paramiko library
-   **Shell Simulation:** Emulates a Linux-like environment with basic command support (`ls`, `cd`, `cat`, etc.)
-   **Virtual File System:** Custom-built, isolated from the host machine to safely mimic file structures
-   **Command Handling:** Commands are parsed and processed manually, with predefined outputs for realism
-   **Logging:** All session activity (IP, credentials, commands, outputs) is recorded to structured log files
-   **Log Viewer:** A local Python application that reads, filters, and analyzes logs
-   **Deployment:** Hosted on an AWS EC2 instance for real-world accessibility
-   **Data Storage:** Collected logs are stored securely using S3 and EFS
-   **Security:** No actual system-level command execution; all activity is sandboxed

---

### Security Notice

This honeypot is intended for **educational and research use** in a **controlled environment only**.  
Do **NOT** expose it to the public internet unless proper safeguards are in place.


