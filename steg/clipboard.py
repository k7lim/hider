"""
Clipboard operations for copying and reading text across platforms.
"""

import subprocess
import platform


def copy_to_clipboard(text):
    """Copy text to clipboard using platform-appropriate command."""
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["pbcopy"], input=text.encode(), check=True, timeout=10)
        elif system == "Linux":
            subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True, timeout=10)
        elif system == "Windows":
            subprocess.run(["clip"], input=text.encode(), check=True, timeout=10)
        else:
            return False
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def read_from_clipboard():
    """Read text from clipboard using platform-appropriate command."""
    # Security limits
    MAX_CLIPBOARD_SIZE = 10 * 1024 * 1024  # 10MB limit
    
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            result = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True, timeout=10)
        elif system == "Linux":
            result = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True, text=True, check=True, timeout=10)
        elif system == "Windows":
            result = subprocess.run(["powershell", "-command", "Get-Clipboard"], capture_output=True, text=True, check=True, timeout=10)
        else:
            return None
        
        # Security: Limit clipboard content size
        if len(result.stdout) > MAX_CLIPBOARD_SIZE:
            print(f"Warning: Clipboard content too large (max {MAX_CLIPBOARD_SIZE // 1024 // 1024}MB), truncating...")
            return result.stdout[:MAX_CLIPBOARD_SIZE]
        
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None