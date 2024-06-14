# ccontext/file_node.py
from typing import List

class FileNode:
    def __init__(self, name: str, path: str, node_type: str, excludes: List[str], includes: List[str]):
        self.name = name
        self.path = path
        self.node_type = node_type  # 'file' or 'directory'
        self.children = []
        self.tokens = 0  # Token count for files
        self.content = ""  # Content of the file

    def add_child(self, child_node):
        self.children.append(child_node)

    def set_tokens_and_content(self, tokens: int, content: str):
        self.tokens = tokens
        self.content = content
