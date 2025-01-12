import os
from pathlib import Path

from ccontext.file_node import FileNode
from ccontext.utils import is_binary_file


class MDGenerator:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.md_content = []

    def add_section(self, title: str, content: str = ""):
        self.md_content.append(f"{title}\n")
        if content:
            self.md_content.append(f"{content}\n")

    def add_toc_entry(self, title: str, anchor: str):
        self.md_content.append(f" - [{title}](#{anchor})\n")

    def save_md(self):
        # Clear the existing file contents before writing new content
        with open(self.output_path, "w") as f:
            f.writelines(self.md_content)
        print(f"Markdown file generated at {self.output_path}")

    def generate_md(self, root_node: FileNode, root_path: str):
        self.add_section(
            "## [[SYSTEM INSTRUCTIONS]]",
            "The following output presents a detailed directory structure and file contents from a specified root path. The file tree includes both excluded and included files and directories, clearly marking exclusions. Each file's content is displayed with comprehensive headings and separators to enhance readability and facilitate detailed parsing for extracting hierarchical and content-related insights. If the data represents a codebase, interpret and handle it as such, providing appropriate assistance as a programmer AI assistant.\n## [[END SYSTEM INSTRUCTIONS]]",
        )
        self.add_section(f"## Root Path: {root_path}")
        self.add_section("## FILE TREE ##")
        self.format_file_tree(root_node)
        self.add_section("## END FILE TREE ##")
        self.add_section("\n#### Detailed File Contents")
        self.add_file_contents(root_node)
        self.save_md()

    def format_file_tree(
        self, node: FileNode, indent: str = "", parent_anchor: str = ""
    ):
        anchor = f"{parent_anchor}-{node.name.lower().replace(' ', '-')}"
        if node.node_type == "directory":
            self.md_content.append(f"{indent}📁 {node.name}\n")
            for child in node.children:
                self.format_file_tree(child, indent + ("-" * 4), anchor)
        elif node.node_type == "file":
            anchor = node.path.lower().replace("/", "-").replace(" ", "-")
            # Check if it's a binary file
            is_binary = is_binary_file(os.path.join(os.getcwd(), node.path))
            file_emoji = "📎" if is_binary else "📄"

            # Add a note for binary files using emphasis
            name_display = f"*{node.name}*" if is_binary else node.name
            self.md_content.append(
                f"{indent} [{file_emoji} {node.tokens} {name_display}](#{anchor})\n"
            )

    def add_file_contents(self, node: FileNode):
        if node.node_type == "file":
            anchor = node.path.lower().replace("/", "-").replace(" ", "-")
            content = node.get_content()
            self.add_section(
                f'##### 📄 <a id="{anchor}"></a>{node.path} - {node.tokens} tokens',
                f"```\n{content}\n```",
            )
        elif node.node_type == "directory":
            for child in node.children:
                self.add_file_contents(child)


def generate_md(root_node: FileNode, root_path: str):
    output_path = str(Path(root_path) / "ccontext-output.md")
    md_gen = MDGenerator(output_path)
    md_gen.generate_md(root_node, root_path)


if __name__ == "__main__":
    import argparse

    from ccontext.main import build_file_tree, load_config

    parser = argparse.ArgumentParser(
        description="Generate Markdown file of directory tree and file contents."
    )
    parser.add_argument(
        "root_path", type=str, help="The root path of the directory to process."
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Path to a custom configuration file.",
        default=None,
    )
    args = parser.parse_args()

    config = load_config(args.root_path, args.config)
    excludes, includes = config.get("excluded_folders_files", []), []
    max_tokens = config.get("max_tokens", 32000)

    root_node = build_file_tree(args.root_path, excludes, includes)
    generate_md(root_node, args.root_path)
