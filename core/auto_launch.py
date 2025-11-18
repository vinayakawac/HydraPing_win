"""
Auto-launch utility for HydraPing.
Handles Windows startup registry integration.
"""

import sys
from pathlib import Path


def get_executable_path():
    """Get the path to the current executable or script."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve()
    else:
        return Path(__file__).parent.parent / "main.py"


def is_auto_launch_supported():
    """Check if auto-launch is supported on this platform."""
    return sys.platform == "win32"


def is_auto_launch_enabled():
    """
    Check if auto-launch is currently enabled.
    
    Returns:
        bool: True if enabled, False otherwise
    """
    if not is_auto_launch_supported():
        return False
    
    try:
        import winreg
        from core.config import WINDOWS_REGISTRY_KEY, WINDOWS_REGISTRY_VALUE_NAME
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            WINDOWS_REGISTRY_KEY,
            0,
            winreg.KEY_READ
        )
        
        try:
            value, _ = winreg.QueryValueEx(key, WINDOWS_REGISTRY_VALUE_NAME)
            winreg.CloseKey(key)
            
            exe_path = str(get_executable_path())
            return exe_path in value or value in exe_path
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception as e:
        print(f"[AutoLaunch] Error checking status: {e}")
        return False


def enable_auto_launch():
    """
    Enable auto-launch on Windows startup.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not is_auto_launch_supported():
        return False, "Auto-launch is only supported on Windows"
    
    try:
        import winreg
        from core.config import WINDOWS_REGISTRY_KEY, WINDOWS_REGISTRY_VALUE_NAME, APP_NAME
        
        exe_path = get_executable_path()
        
        if exe_path.suffix == '.py':
            python_path = Path(sys.executable)
            if python_path.name == 'python.exe':
                pythonw_path = python_path.parent / 'pythonw.exe'
                if pythonw_path.exists():
                    command = f'"{pythonw_path}" "{exe_path}"'
                else:
                    command = f'"{python_path}" "{exe_path}"'
            else:
                command = f'"{sys.executable}" "{exe_path}"'
        else:
            command = f'"{exe_path}"'
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            WINDOWS_REGISTRY_KEY,
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(key, WINDOWS_REGISTRY_VALUE_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        
        print(f"[AutoLaunch] Enabled: {command}")
        return True, f"Auto-launch enabled for {APP_NAME}"
    except Exception as e:
        error_msg = f"Failed to enable auto-launch: {e}"
        print(f"[AutoLaunch] {error_msg}")
        return False, error_msg


def disable_auto_launch():
    """
    Disable auto-launch on Windows startup.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not is_auto_launch_supported():
        return False, "Auto-launch is only supported on Windows"
    
    try:
        import winreg
        from core.config import WINDOWS_REGISTRY_KEY, WINDOWS_REGISTRY_VALUE_NAME, APP_NAME
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            WINDOWS_REGISTRY_KEY,
            0,
            winreg.KEY_SET_VALUE
        )
        
        try:
            winreg.DeleteValue(key, WINDOWS_REGISTRY_VALUE_NAME)
            print(f"[AutoLaunch] Disabled")
            winreg.CloseKey(key)
            return True, f"Auto-launch disabled for {APP_NAME}"
        except FileNotFoundError:
            winreg.CloseKey(key)
            return True, "Auto-launch was not enabled"
    except Exception as e:
        error_msg = f"Failed to disable auto-launch: {e}"
        print(f"[AutoLaunch] {error_msg}")
        return False, error_msg


def toggle_auto_launch(enable):
    """
    Toggle auto-launch on or off.
    
    Args:
        enable: True to enable, False to disable
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if enable:
        return enable_auto_launch()
    else:
        return disable_auto_launch()
