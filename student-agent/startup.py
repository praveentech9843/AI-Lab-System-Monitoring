import os
import sys
import winreg

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_KEY_NAME = "StudentAgent"

def register_startup() -> bool:
    """Registers the student agent to start automatically on Windows logon."""
    try:
        # Determine paths
        main_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
        python_exe = sys.executable
        # Try to use pythonw.exe if it exists to avoid displaying a console window at startup
        pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
        executable = pythonw_exe if os.path.exists(pythonw_exe) else python_exe
        
        command = f'"{executable}" "{main_script_path}"'
        
        # Open user run registry key and set value
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, REG_KEY_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def unregister_startup() -> bool:
    """Removes the student agent from Windows Startup registry."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_ALL_ACCESS)
        try:
            winreg.DeleteValue(key, REG_KEY_NAME)
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False
