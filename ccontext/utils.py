# ccontext/utils.py
import os

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


def interpolate_color(percentage, color1, color2):
    """
    Interpolates between two RGB colors based on the given percentage.
    """
    r = int(color1[0] + (color2[0] - color1[0]) * percentage)
    g = int(color1[1] + (color2[1] - color1[1]) * percentage)
    b = int(color1[2] + (color2[2] - color1[2]) * percentage)
    return (r, g, b)


def rgb_to_ansi(r, g, b):
    """
    Converts an RGB color to the closest ANSI color code.
    """
    return f"\033[38;2;{r};{g};{b}m"


def get_color_for_percentage(percentage):
    """
    Returns a color from white to yellow to red based on the given percentage.
    """
    percentage = percentage * 100

    # max percentage is 100, necessary for logic below
    if percentage > 100:
        percentage = 100

    if percentage <= 50:
        color = interpolate_color(
            percentage / 50, (255, 255, 255), (255, 255, 0)
        )  # White to Yellow
    else:
        color = interpolate_color(
            (percentage - 50) / 50, (255, 165, 0), (255, 0, 0)
        )  # Orange to Red
    return rgb_to_ansi(*color)


def is_binary_file(file_path: str) -> bool:
    """
    Simple check if file is binary by attempting to read it as text.
    Returns True if file is binary, False if it's text.
    """
    try:
        with open(file_path, "tr") as check_file:  # try open file in text mode
            check_file.read()
            return False
    except UnicodeDecodeError:  # if fail then file is non-text (binary)
        return True


def should_upload_file(file_path: str, uploadable_extensions: set) -> bool:
    """
    Determines if a file should be uploaded based on its extension.
    """

    if not uploadable_extensions:
        return False
    ext = os.path.splitext(file_path)[1].lower()
    return ext in uploadable_extensions
