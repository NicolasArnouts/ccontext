# ccontext/file_tree.py
import os
from typing import List
from ccontext.file_node import FileNode
from ccontext.file_system import is_excluded
from ccontext.tokenizer import tokenize_text

def build_file_tree(root_path: str, excludes: List[str], includes: List[str]) -> FileNode:
    def traverse_directory(current_path: str) -> FileNode:
        relative_path = os.path.relpath(current_path, start=root_path)
        node_type = 'directory' if os.path.isdir(current_path) else 'file'
        node = FileNode(os.path.basename(current_path), relative_path, node_type, excludes, includes)
        
        if node_type == 'directory':
            for item in sorted(os.listdir(current_path)):
                full_path = os.path.join(current_path, item)
                if not is_excluded(full_path, excludes, includes):
                    child_node = traverse_directory(full_path)
                    node.add_child(child_node)
        else:
            tokens, content = tokenize_file_content(current_path)  # Use current_path instead of full_path
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
            contents = f.read().decode("utf-8")
            tokens = tokenize_text(contents)
            return len(tokens), contents
    except Exception as e:
        return 0, f"Error reading file {file_path}: {e}"

def format_file_tree(node: FileNode, indent: str = "") -> str:
    output = ""
    if node.node_type == 'directory':
        output += f"{indent}📁 {node.name}\n"
        for child in node.children:
            output += format_file_tree(child, indent + "    ")
    else:
        output += f"{indent}📄 {node.tokens} {node.name}\n"
    return output

def extract_file_contents(node: FileNode) -> list:
    contents = []
    if node.node_type == 'file':
        contents.append(f"\n#### 📄 {node.path}\n**Contents:**\n{node.content}\n")
    elif node.node_type == 'directory':
        for child in node.children:
            contents.extend(extract_file_contents(child))
    return contents

def sum_file_tokens(node: FileNode) -> int:
    if node.node_type == 'file':
        return node.tokens
    else:
        return sum(sum_file_tokens(child) for child in node.children)
