# ccontext/file_tree.py
import os
from typing import List
from ccontext.file_node import FileNode
from ccontext.file_system import is_excluded
from ccontext.tokenizer import tokenize_text
from ccontext.utils import is_verbose

from colorama import Fore, Style


# build a root FileNode using recursive path traversal
def build_file_tree(
    root_path: str, excludes: List[str], includes: List[str]
) -> FileNode:
    def traverse_directory(current_path: str) -> FileNode:
        relative_path = os.path.relpath(current_path, start=root_path)
        node_type = "directory" if os.path.isdir(current_path) else "file"
        node = FileNode(
            os.path.basename(current_path), relative_path, node_type, excludes, includes
        )

        if node_type == "directory":
            for item in sorted(os.listdir(current_path)):
                full_path = os.path.join(current_path, item)
                if not is_excluded(full_path, excludes, includes):
                    child_node = traverse_directory(full_path)
                    node.add_child(child_node)
        else:
            tokens, content = tokenize_file_content(
                current_path
            )  # Use current_path instead of full_path
            node.set_tokens_and_content(tokens, content)
        return node

    return traverse_directory(root_path)


def tokenize_file_content(file_path: str) -> (int, str):
    try:
        with open(file_path, "rb") as f:
            header = f.read(64)
            if b"\x00" in header:  # if binary data
                return 0, ""
            f.seek(0)
            if is_verbose():
                print(file_path)
            contents = f.read().decode("utf-8")
            tokens = tokenize_text(contents)
            return len(tokens), contents
    except Exception as e:
        return 0, f"Error reading file {file_path}: {e}"


def extract_file_contents(node: FileNode) -> list:
    contents = []
    if node.node_type == "file":
        contents.append(f"\n#### 📄 {node.path}\n**Contents:**\n{node.content}\n")
    elif node.node_type == "directory":
        for child in node.children:
            contents.extend(extract_file_contents(child))
    return contents


def sum_file_tokens(node: FileNode) -> int:
    if node.node_type == "file":
        return node.tokens
    else:
        return sum(sum_file_tokens(child) for child in node.children)


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
    Converts an RGB color to an ANSI color code.
    """
    return f"\033[38;2;{r};{g};{b}m"


def get_color_for_percentage(percentage):
    """
    Returns a color from white to yellow to orange to red based on the given percentage.
    """
    if percentage <= 0.33:
        color = interpolate_color(
            percentage / 0.33, (255, 255, 255), (255, 255, 0)
        )  # White to Yellow
    elif percentage <= 0.66:
        color = interpolate_color(
            (percentage - 0.33) / 0.33, (255, 255, 0), (255, 165, 0)
        )  # Yellow to Orange
    else:
        color = interpolate_color(
            (percentage - 0.66) / 0.34, (255, 165, 0), (255, 0, 0)
        )  # Orange to Red
    return rgb_to_ansi(*color)


def format_file_tree(node: FileNode, max_tokens: int, indent: str = "") -> str:
    output = ""
    if node.node_type == "directory":
        output += f"{indent}📁 {node.name}\n"
        for child in node.children:
            output += format_file_tree(child, max_tokens, indent + "    ")
    else:
        percentage = node.tokens / max_tokens if max_tokens else 0
        color = get_color_for_percentage(percentage)
        output += f"{indent}📄 {color}{node.tokens}{Style.RESET_ALL} {node.name}\n"
    return output
