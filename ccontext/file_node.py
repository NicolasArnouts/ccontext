from typing import List


class FileNode:
    def __init__(self, name: str, path: str, node_type: str, excluded=False):
        self.name = name
        self.path = path
        self.node_type = node_type  # 'file' or 'directory'
        self.children = []
        self.tokens = 0  # Token count for files
        self.content = ""  # Content of the file
        self.excluded = excluded  # Flag to mark if the node is excluded

    def add_child(self, child_node):
        self.children.append(child_node)

    def set_tokens_and_content(self, tokens: int, content: str):
        self.tokens = tokens
        self.content = content

    def calculate_size(self) -> int:
        """
        Calculate the total size of the node and its children.
        Returns the total size in tokens.
        """
        total_size = self.tokens
        for child in self.children:
            total_size += child.calculate_size()
        return total_size
