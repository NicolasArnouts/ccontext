# ccontext/file_tree.py
import os
import time
from typing import List, Tuple

from colorama import Fore, Style

from ccontext.file_node import FileNode
from ccontext.file_system import is_excluded
from ccontext.tokenizer import tokenize_text
from ccontext.utils import (
    get_color_for_percentage,
    is_binary_file,
    is_verbose,
    should_upload_file,
)


def build_file_tree(
    root_path: str, excludes: List[str], includes: List[str], uploadable_extensions: set
) -> FileNode:
    # Record the start time
    start_time = time.time()

    def traverse_directory(current_path: str) -> FileNode:
        relative_path = os.path.relpath(current_path, start=root_path)
        node_type = "directory" if os.path.isdir(current_path) else "file"
        excluded = is_excluded(relative_path, excludes, includes)
        node = FileNode(
            os.path.basename(current_path),
            relative_path,
            node_type,
            excluded,
        )

        # Check elapsed time
        elapsed_time = time.time() - start_time

        # Check if 10 seconds have elapsed and print path in red if true
        if elapsed_time > 10:
            print(Fore.RED + relative_path + Style.RESET_ALL)

        if node_type == "directory" and not excluded:
            for item in sorted(os.listdir(current_path)):
                full_path = os.path.join(current_path, item)
                child_node = traverse_directory(full_path)
                node.add_child(child_node)
        elif node_type == "file" and not excluded:
            tokens, content = tokenize_file_content(current_path, uploadable_extensions)
            node.set_tokens_and_content(tokens, content)
        return node

    return traverse_directory(root_path)


def tokenize_file_content(
    file_path: str, uploadable_extensions: set
) -> Tuple[int, str]:
    """Returns token count and content for a file."""
    try:
        # First check if file should be uploaded regardless of binary status
        if should_upload_file(file_path, uploadable_extensions):
            file_ref = f"<file>{os.path.abspath(file_path)}</file>"
            return 1, file_ref

        # If not uploadable, check if it's binary
        if is_binary_file(file_path):
            return 0, ""  # Skip binary files that aren't in uploadable list

        # Handle text files
        with open(file_path, "r", encoding="utf-8") as f:
            text_content = f.read()
            if is_verbose():
                print(file_path)
            tokens = tokenize_text(text_content)
            return len(tokens), text_content

    except Exception as e:
        print(f"{Fore.YELLOW}Error reading file {file_path}: {str(e)}{Style.RESET_ALL}")
        return 0, ""


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


def format_file_tree(
    node: FileNode, max_tokens: int, indent: str = "", useColors: bool = False
) -> str:
    output = ""
    if node.node_type == "directory":
        if node.excluded:
            output += f"{indent}[Excluded] 🚫📁 {node.name}\n"
        else:
            output += f"{indent}📁 {node.name}\n"
            for child in node.children:
                output += format_file_tree(
                    child, max_tokens, indent + "    ", useColors
                )
    else:
        percentage = node.tokens / max_tokens if max_tokens else 0
        color = get_color_for_percentage(percentage) if useColors else ""
        reset = Style.RESET_ALL if useColors else ""

        # Check if it's a binary file
        is_binary = is_binary_file(os.path.join(os.getcwd(), node.path))
        file_emoji = "📎" if is_binary else "📄"

        # Format the name - yellow for binary files
        if is_binary:
            name_display = (
                f"{Fore.YELLOW}{node.name}{Style.RESET_ALL}" if useColors else node.name
            )
        else:
            name_display = node.name

        if node.excluded:
            output += f"{indent}[Excluded] 🚫{file_emoji} {name_display}\n"
        else:
            output += (
                f"{indent}{file_emoji} {color}{node.tokens}{reset} {name_display}\n"
            )
    return output
