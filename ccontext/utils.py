from colorama import init


def initialize_environment():
    """Initialize the environment settings."""
    init(autoreset=True)


def format_number(number: int) -> str:
    """Formats a number with commas as thousands separators."""
    return f"{number:,}"
