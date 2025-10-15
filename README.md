# setup_task.py

This Python script is designed to automate the process of uploading code to GitHub at system startup. Here's a breakdown of what the script does:

**Main Functionality**

1. **Create an Internet Check Script**: The script generates a Python script (`check_internet.py`) that checks for internet connectivity by attempting to connect to Google's DNS server. If the connection is successful, it returns `True`, otherwise, it returns `False`.
2. **Create a Batch Script**: The script generates a batch script (`run_uploader.bat`) that:
	* Activates the virtual environment.
	* Checks if another instance of the script is already running.
	* Runs the internet check script.
	* If the internet connection is established, it runs the main script (`github_code_uploader.py`).
3. **Create a Task to Run at System Startup**: The script generates a task configuration file (`task_config.xml`) that defines a task to run at system startup. The task:
	* Wa