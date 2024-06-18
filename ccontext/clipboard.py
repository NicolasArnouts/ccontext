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
    global CLIPBOARD_ERROR
    try:
        result = subprocess.run(["utf8clip.exe"], stdin=subprocess.DEVNULL)
        if result.returncode != 0:
            raise FileNotFoundError
    except FileNotFoundError:
        CLIPBOARD_ERROR = True
        print(
            f"{Fore.RED} WSL2 requires utf8clip. utf8clip is not installed. Attempting to install...{Style.RESET_ALL}"
        )
        print(
            f"{Fore.RED}Please install dotnet core runtime 3.03: https://dotnet.microsoft.com/en-us/download/dotnet/thank-you/runtime-3.0.3-windows-x64-installer {Style.RESET_ALL}"
        )
        install_process = subprocess.Popen(
            ["powershell.exe", "dotnet", "tool", "install", "--global", "utf8clip"],
            text=True,
        )
        install_process.communicate()
        if install_process.returncode != 0:
            raise RuntimeError(
                "Error installing utf8clip using PowerShell.\nPlease install .NET Runtime 3.03: https://dotnet.microsoft.com/en-us/download/dotnet/thank-you/runtime-3.0.3-windows-x64-installer"
            )
    except Exception as e:
        print(f"An error occurred: {e}")
        raise RuntimeError(
            "Failed to check or install utf8clip. Please install .NET Runtime 3.03: https://dotnet.microsoft.com/en-us/download/dotnet/thank-you/runtime-3.0.3-windows-x64-installer"
        )


def copy_to_clipboard(text: str):
    """Copies the given text to the clipboard."""
    global CLIPBOARD_ERROR
    CLIPBOARD_ERROR = False
    system = platform.system()

    try:
        if system == "Windows" or system == "Darwin":
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

        if CLIPBOARD_ERROR:
            print(f"{Fore.RED}\nFailed to copy to clipboard!{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}\nOutput copied to clipboard!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}\nAn error occurred: {e}{Style.RESET_ALL}")
