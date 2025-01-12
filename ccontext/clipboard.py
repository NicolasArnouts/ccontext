import os
import platform
import re
import subprocess

import pyperclip
from colorama import Fore, Style


def is_wsl2() -> bool:
    """Detect if running under WSL2."""
    try:
        with open("/proc/version", "r") as file:
            version_info = file.read().lower()
            return "microsoft" in version_info
    except FileNotFoundError:
        return False


def copy_files_to_clipboard(file_paths: list):
    """Copies multiple file references to the clipboard for pasting as files."""
    system = platform.system()

    try:
        if system == "Darwin":  # macOS
            import AppKit

            pasteboard = AppKit.NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            urls = [
                AppKit.NSURL.fileURLWithPath_(file_path) for file_path in file_paths
            ]
            pasteboard.writeObjects_(urls)
        elif system == "Windows":
            import ctypes
            from ctypes import Structure, wintypes

            # Define the DROPFILES structure
            class DROPFILES(Structure):
                _fields_ = [
                    ("pFiles", wintypes.DWORD),
                    ("pt", wintypes.POINT),
                    ("fNC", wintypes.BOOL),
                    ("fWide", wintypes.BOOL),
                ]

            # Create the DROPFILES structure
            offset = ctypes.sizeof(DROPFILES)
            files = ("\0".join(file_paths) + "\0\0").encode("utf-16le")
            total_size = offset + len(files)

            # Allocate global memory for DROPFILES structure and file list
            h_mem = ctypes.windll.kernel32.GlobalAlloc(
                0x2000, total_size
            )  # GMEM_ZEROINIT = 0x2000
            block = ctypes.windll.kernel32.GlobalLock(h_mem)

            # Initialize DROPFILES structure
            dropfiles = DROPFILES()
            dropfiles.pFiles = offset
            dropfiles.fWide = True

            # Copy the DROPFILES structure to the allocated memory
            ctypes.memmove(block, ctypes.byref(dropfiles), ctypes.sizeof(DROPFILES))

            # Copy the file list right after the DROPFILES structure
            ctypes.memmove(block + offset, files, len(files))

            ctypes.windll.kernel32.GlobalUnlock(h_mem)

            # Open the clipboard and set the data
            if ctypes.windll.user32.OpenClipboard(0):
                ctypes.windll.user32.EmptyClipboard()
                ctypes.windll.user32.SetClipboardData(15, h_mem)  # CF_HDROP = 15
                ctypes.windll.user32.CloseClipboard()
            else:
                raise Exception("Failed to open clipboard.")

        elif system == "Linux":
            # Check for SSH connection without DISPLAY
            if "SSH_CONNECTION" in os.environ and "DISPLAY" not in os.environ:
                print(
                    f"{Fore.YELLOW}SSH connection detected without DISPLAY. Clipboard operations are limited.{Style.RESET_ALL}\n"
                    f"{Fore.YELLOW}ssh -X user@host{Style.RESET_ALL}"
                )
                raise Exception("Clipboard functionality limited in headless SSH.")

            uri_list = "\r\n".join([f"file://{file_path}" for file_path in file_paths])

            # Try xclip first
            try:
                subprocess.run(
                    ["xclip", "-selection", "clipboard", "-t", "text/uri-list", "-i"],
                    input=uri_list.encode(),
                    check=True,
                )
            except (subprocess.SubprocessError, FileNotFoundError):
                # Try xsel as fallback
                try:
                    subprocess.run(
                        ["xsel", "--clipboard", "--input"],
                        input=uri_list.encode(),
                        check=True,
                    )
                except (subprocess.SubprocessError, FileNotFoundError):
                    raise Exception("xclip or xsel is required for clipboard support.")

        print(
            f"{Fore.GREEN}{len(file_paths)} Binary file references copied to clipboard. Paste into LLM to upload them.{Style.RESET_ALL}"
        )

    except Exception as e:
        print(
            f"{Fore.RED}Failed to copy file reference to clipboard: {e}{Style.RESET_ALL}"
        )
        # Fallback to copying the file paths as text
        pyperclip.copy("\n".join(file_paths))
        print(
            f"{Fore.YELLOW}Fallback: Copied file paths as text instead{Style.RESET_ALL}"
        )


def copy_to_clipboard(text: str):
    """
    Handles both text and file references for clipboard copying.
    Extracts file paths from <file> tags and copies them individually.
    Copies any remaining text to the clipboard with user confirmation between steps.
    """
    file_pattern = r"<file>(.*?)</file>"

    # Extract file paths and non-file text
    non_file_text = re.sub(file_pattern, "", text).strip()
    file_paths = [
        path for path in re.findall(file_pattern, text) if os.path.exists(path)
    ]

    # First step: Copy text content if present
    if non_file_text:
        try:
            pyperclip.copy(non_file_text)
            print(
                f"{Fore.GREEN}\nText content copied to clipboard! Paste into LLM before proceeding.{Style.RESET_ALL}"
            )
        except Exception as e:
            print(f"{Fore.RED}\nFailed to copy text to clipboard: {e}{Style.RESET_ALL}")

    if file_paths:
        print(
            f"\n{Fore.CYAN}Press Enter to copy binary file references to clipboard, or 'q' to skip: {Style.RESET_ALL}",
            end="",
        )
        user_input = input()
        if user_input.lower() != "q":
            copy_files_to_clipboard(file_paths)
        else:
            print(f"{Fore.YELLOW}File path copying skipped.{Style.RESET_ALL}")
