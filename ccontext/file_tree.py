import os
import time
from typing import List
from ccontext.file_node import FileNode
from ccontext.file_system import is_excluded
from ccontext.tokenizer import tokenize_text
from ccontext.utils import is_verbose, get_color_for_percentage
from colorama import Fore, Style


# build a root FileNode using recursive path traversal
def build_file_tree(
    root_path: str, excludes: List[str], includes: List[str]
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
            tokens, content = tokenize_file_content(current_path)
            node.set_tokens_and_content(tokens, content)
        return node

    return traverse_directory(root_path)


def tokenize_file_content(file_path: str) -> tuple[int, str]:
    try:
        with open(file_path, "rb") as f:
            header = f.read(64)
            if b"\x00" in header:  # if binary data
                return 0, "Binary data"
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
        if node.excluded:
            output += f"{indent}[Excluded] 🚫📄 {node.name}\n"
        else:
            output += f"{indent}📄 {color}{node.tokens}{reset} {node.name}\n"
    return output
