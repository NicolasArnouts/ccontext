#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

from colorama import Fore, Style


def is_wsl():
    """Check if running in WSL"""
    if os.path.exists("/proc/version"):
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    return False


def check_and_fix_wsl_environment():
    """Check and fix WSL environment for running crawl4ai."""
    if not is_wsl():
        print(f"{Fore.YELLOW}Not running in WSL, no fixes needed.{Style.RESET_ALL}")
        return False

    print(f"{Fore.CYAN}WSL environment detected.{Style.RESET_ALL}")

    # Check if crawl4ai is installed
    try:
        import crawl4ai

        print(f"{Fore.GREEN}crawl4ai is already installed.{Style.RESET_ALL}")
    except ImportError:
        print(f"{Fore.YELLOW}crawl4ai not found, installing...{Style.RESET_ALL}")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-U", "crawl4ai"], check=True
            )
            print(f"{Fore.GREEN}crawl4ai installed successfully.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Failed to install crawl4ai: {str(e)}{Style.RESET_ALL}")
            print(
                f"{Fore.YELLOW}Please install manually with: pip install -U crawl4ai{Style.RESET_ALL}"
            )
            return False

    # Install required system dependencies for WSL
    try:
        print(f"{Fore.CYAN}Installing system dependencies for WSL...{Style.RESET_ALL}")

        # Basic dependencies that might be needed
        dependencies = [
            "python3-dev",
            "build-essential",
            "libssl-dev",
            "libffi-dev",
        ]

        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y"] + dependencies, check=True)
        print(
            f"{Fore.GREEN}System dependencies installed successfully.{Style.RESET_ALL}"
        )
    except Exception as e:
        print(
            f"{Fore.YELLOW}Warning: Could not install all system dependencies: {str(e)}{Style.RESET_ALL}"
        )
        print(f"{Fore.YELLOW}You may need to install them manually.{Style.RESET_ALL}")

    print(f"{Fore.GREEN}WSL environment setup complete.{Style.RESET_ALL}")
    print(
        f"{Fore.CYAN}You can now use crawl4ai in WSL with: python -m ccontext --crawl{Style.RESET_ALL}"
    )
    return True


def main():
    """Main function for the fix_wsl module."""
    check_and_fix_wsl_environment()


if __name__ == "__main__":
    main()
