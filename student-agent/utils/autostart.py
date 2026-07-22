import os
import sys
import winreg
import logging

logger = logging.getLogger("AutoStart")

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_KEY_NAME = "StudentAgent"

def register_startup():
    """Add a registry entry to run the student agent on startup."""
    try:
        # Get path to main.py
        # Since this script is inside student-agent/utils/autostart.py, main.py is in the parent directory
        main_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
        
        # Decide between python.exe and pythonw.exe (pythonw runs without displaying a terminal window)
        python_exe = sys.executable
        pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
        executable = pythonw_exe if os.path.exists(pythonw_exe) else python_exe
        
        # Build the command: e.g. "C:\Path\To\pythonw.exe" "C:\Path\To\main.py"
        command = f'"{executable}" "{main_script_path}"'
        
        # Open registry key and write value
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, REG_KEY_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        
        logger.info(f"Successfully registered student agent to start automatically: {command}")
        return True
    except Exception as e:
        logger.error(f"Failed to register startup registry key: {e}")
        return False

def unregister_startup():
    """Remove the registry entry to prevent the student agent from starting automatically."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_ALL_ACCESS)
        try:
            winreg.DeleteValue(key, REG_KEY_NAME)
            logger.info("Successfully removed student agent startup registration")
            success = True
        except FileNotFoundError:
            logger.info("Student agent startup registration was not found in registry")
            success = True
        winreg.CloseKey(key)
        return success
    except Exception as e:
        logger.error(f"Failed to unregister startup registry key: {e}")
        return False
