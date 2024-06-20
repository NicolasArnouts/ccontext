from ccontext.file_node import FileNode
from pathlib import Path

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
        with open(self.output_path, "w") as f:
            f.writelines(self.md_content)
        print(f"Markdown file generated at {self.output_path}")

def generate_md(root_node: FileNode, root_path: str):
    md_gen = MDGenerator(Path(root_path) / "ccontext-output.md")

    def format_file_tree(node: FileNode, indent: str = "", parent_anchor: str = ""):
        if node.node_type == 'directory':
            anchor = f"{parent_anchor}-{node.name.lower().replace(' ', '-')}"
            md_gen.add_toc_entry(f"{indent}📁 {node.name}", anchor)
            md_gen.add_section(f"<a id=\"{anchor}\"></a>", "")
            for child in node.children:
                format_file_tree(child, indent + "    ", anchor)
        elif node.node_type == 'file':
            anchor = node.path.lower().replace('/', '-').replace(' ', '-')
            link = f"[📄 {node.name}](#{anchor})"
            md_gen.add_toc_entry(f"{indent}📄 {link}", anchor)
            md_gen.add_section(f"#### 📄 [{node.path}](#{anchor})", f"```\n{node.content if node.content else '<Binary data>'}\n```")

    def add_file_contents(node: FileNode):
        if node.node_type == 'file':
            anchor = node.path.lower().replace('/', '-').replace(' ', '-')
            md_gen.add_section(f"#### 📄 [{node.path}](#{anchor})", f"```\n{node.content if node.content else '<Binary data>'}\n```")
        elif node.node_type == 'directory':
            for child in node.children:
                add_file_contents(child)

    md_gen.add_section("## [[SYSTEM INSTRUCTIONS]] The following output presents a detailed directory structure and file contents from a specified root path. The file tree includes both excluded and included files and directories, clearly marking exclusions. Each file's content is displayed with comprehensive headings and separators to enhance readability and facilitate detailed parsing for extracting hierarchical and content-related insights. If the data represents a codebase, interpret and handle it as such, providing appropriate assistance as a programmer AI assistant. [[END SYSTEM INSTRUCTIONS]]")
    md_gen.add_section(f"## Root Path: {root_path}")

    format_file_tree(root_node)
    md_gen.add_section("#### Detailed File Contents")
    add_file_contents(root_node)

    md_gen.save_md()

if __name__ == "__main__":
    import argparse
    from ccontext.main import load_config, build_file_tree

    parser = argparse.ArgumentParser(description="Generate Markdown file of directory tree and file contents.")
    parser.add_argument("root_path", type=str, help="The root path of the directory to process.")
    parser.add_argument("-c", "--config", type=str, help="Path to a custom configuration file.", default=None)
    args = parser.parse_args()

    config = load_config(args.root_path, args.config)
    excludes, includes = config.get("excluded_folders_files", []), []
    max_tokens = config.get("max_tokens", 32000)

    root_node = build_file_tree(args.root_path, excludes, includes)

    generate_md(root_node, args.root_path)
