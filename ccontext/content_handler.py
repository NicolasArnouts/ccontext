import os
from ccontext.file_tree import (
    format_file_tree,
    extract_file_contents,
    sum_file_tokens,
)
from ccontext.file_node import FileNode


def print_file_tree(root_node: FileNode, max_tokens: int) -> str:
    return format_file_tree(root_node, max_tokens)


def gather_file_contents(root_node: FileNode, max_tokens: int) -> tuple[list, int]:
    return extract_file_contents(root_node), sum_file_tokens(root_node)


def combine_initial_content(
    root_node: FileNode, root_path: str, context_prompt: str, max_tokens: int
) -> str:
    tree_output = print_file_tree(root_node, max_tokens)
    return f"## {context_prompt}\n\n## Root Path: {root_path}\n\n{tree_output}"
