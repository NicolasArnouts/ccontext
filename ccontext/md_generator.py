from ccontext.file_node import FileNode

class MDGenerator:
    def __init__(self, output_path):
        self.output_path = output_path
        self.md_content = []

    def add_section(self, title, content):
        self.md_content.append(f"### {title}\n")
        self.md_content.append(content)
        self.md_content.append("\n")

    def save_md(self):
        with open(self.output_path, "w") as f:
            f.writelines(self.md_content)
        print(f"Markdown file generated at {self.output_path}")

def generate_md(root_node: FileNode, output_path: str):
    md_gen = MDGenerator(output_path)

    def add_tree_section(node: FileNode, indent: str = ""):
        if node.node_type == 'directory':
            md_gen.add_section(f"{indent}📁 {node.name}", "")
            for child in node.children:
                add_tree_section(child, indent + "    ")
        else:
            md_gen.add_section(f"{indent}📄 {node.tokens} {node.name}", node.content if node.content else "<Binary data>")

    md_gen.add_section("Directory and File Contents", "")
    add_tree_section(root_node)

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
