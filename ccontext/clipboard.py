import subprocess
import platform
from colorama import Fore, Style
import pyperclip


def is_wsl2() -> bool:
    """Detect if running under WSL2."""
    try:
        with open("/proc/version", "r") as file:
            version_info = file.read().lower()
            return "microsoft" in version_info
    except FileNotFoundError:
        return False


def check_and_install_utf8clip():
    """Check if utf8clip is installed, and install it if necessary."""
    try:
        result = subprocess.run(["utf8clip.exe"], stdin=subprocess.DEVNULL)
        if result.returncode != 0:
            raise FileNotFoundError
    except FileNotFoundError:
        print("utf8clip is not installed. Attempting to install...")
        install_process = subprocess.Popen(
            ["powershell.exe", "dotnet", "tool", "install", "--global", "utf8clip"],
            text=True,
        )
        install_process.communicate()
        if install_process.returncode != 0:
            raise RuntimeError("Error installing utf8clip using PowerShell.")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise RuntimeError("Failed to check or install utf8clip.")


def copy_to_clipboard(text: str):
    """Copies the given text to the clipboard."""
    system = platform.system()

    try:
        if system == "Windows":
            pyperclip.copy(text)
        elif system == "Darwin":
            pyperclip.copy(text)
        elif system == "Linux":
            if (
                is_wsl2()
            ):  # WSL2 requires utf8clip, https://github.com/asweigart/pyperclip/issues/244
                check_and_install_utf8clip()
                process = subprocess.Popen(
                    "utf8clip.exe", stdin=subprocess.PIPE, shell=True
                )
                process.communicate(text.encode("utf-8"))
            else:
                pyperclip.copy(text)
        else:
            # Fallback to pyperclip for other systems
            pyperclip.copy(text)

        print(f"{Fore.GREEN}\nOutput copied to clipboard!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}\nAn error occurred: {e}{Style.RESET_ALL}")
