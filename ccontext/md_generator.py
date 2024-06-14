import os


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


def generate_md(root_path, tree_content, file_contents_list):
    output_path = os.path.join(root_path, "output.md")
    md_gen = MDGenerator(output_path)

    md_gen.add_section("Directory and File Contents", "")
    md_gen.add_section("File Tree", tree_content)

    for file_content in file_contents_list:
        md_gen.add_section("File Content", file_content)

    md_gen.save_md()


if __name__ == "__main__":
    import argparse
    from ccontext.main import load_config, print_file_tree, gather_file_contents

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

    tree_content = print_file_tree(args.root_path, excludes, includes, max_tokens)
    file_contents_list, _ = gather_file_contents(args.root_path, excludes, includes)

    generate_md(args.root_path, tree_content, file_contents_list)
