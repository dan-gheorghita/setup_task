import subprocess
import sys
import os

def create_internet_check_script():
    """Create a helper script that checks for internet connectivity"""
    script_content = '''import sys
import socket
import time
from datetime import datetime

def check_internet():
    try:
        # Try to connect to a reliable host (Google's DNS)
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

attempt = 1
# Wait for internet connection
while not check_internet():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] Attempt {attempt}: No internet connection. Retrying in 60 seconds...")
    time.sleep(60)  # Wait for 60 seconds before retrying
    attempt += 1

# Once internet is available, run the main script
sys.exit(0)
'''
    
    check_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_internet.py")
    with open(check_script_path, 'w') as f:
        f.write(script_content)
    return check_script_path

def create_startup_task():
    task_name = "GitHubCodeUploader"
    python_exe = sys.executable
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "github_code_uploader.py")
    
    # Create the internet check script
    check_script_path = create_internet_check_script()
    
    # Create a batch script to run both scripts in sequence
    venv_activate = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Scripts", "activate.bat")
    
    batch_content = f'''@echo off
title GitHub Code Uploader
color 0A

REM Activate virtual environment
call "{venv_activate}"

REM Check if another instance is running
tasklist /FI "WINDOWTITLE eq GitHub Code Uploader" /NH | find /I /N "cmd.exe" > NUL
if %ERRORLEVEL% EQU 0 (
    echo Another instance of GitHub Code Uploader is already running.
    echo Press any key to exit...
    pause >nul
    exit
)

echo ====================================
echo GitHub Code Uploader - Status Window
echo ====================================
echo.
echo [%date% %time%] Checking internet connection...
"{python_exe}" "{check_script_path}"
if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] Internet connection established.
    echo [%date% %time%] Starting GitHub code uploader...
    echo.
    "{python_exe}" "{script_path}"
    echo.
    echo [%date% %time%] Task completed.
) else (
    echo [%date% %time%] Failed to establish internet connection.
)
echo.
echo ====================================
echo Press any key to close this window...
pause >nul
'''
    batch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_uploader.bat")
    with open(batch_path, 'w') as f:
        f.write(batch_content)
    
    # Create the task to run at system startup
    current_user = os.environ.get('USERNAME')
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT20S</Delay>
    </BootTrigger>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT20S</Delay>
      <UserId>{current_user}</UserId>
    </LogonTrigger>
  </Triggers>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>{batch_path}</Command>
    </Exec>
  </Actions>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
      <UserId>{current_user}</UserId>
    </Principal>
  </Principals>
</Task>'''
    
    xml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "task_config.xml")
    with open(xml_path, 'w', encoding='utf-16') as f:
        f.write(xml_content)
    
    command = [
        "schtasks",
        "/create",
        "/tn", task_name,
        "/xml", xml_path,
        "/f"  # Force creation/overwrite existing task
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Task '{task_name}' scheduled successfully.")
        print("The script will run automatically when the system starts.")
        
        # Print requirements
        print("\nBefore running, please ensure:")
        print("1. Install required packages:")
        print("   pip install PyGithub python-dotenv huggingface_hub")
        print("2. Configure the .env file with your GitHub and HuggingFace tokens")
        print("\nThe task will:")
        print("1. Wait for internet connectivity")
        print("2. Run the GitHub code uploader once connection is available")
    except subprocess.CalledProcessError as e:
        print(f"Error scheduling task: {e}")
        print("Try running this script as administrator.")

if __name__ == "__main__":
    create_startup_task()
