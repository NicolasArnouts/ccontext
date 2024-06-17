from colorama import init

verbose_state = {"verbose": False}


def set_verbose(value: bool):
    verbose_state["verbose"] = value


def is_verbose():
    return verbose_state["verbose"]


def initialize_environment():
    """Initialize the environment settings."""
    init(autoreset=True)


def format_number(number: int) -> str:
    """Formats a number with commas as thousands separators."""
    return f"{number:,}"
