import os
import re


def generate_md(root_path, tree_content, file_contents_list):
    output_path = os.path.join(root_path, "output.md")

    with open(output_path, "w", encoding="utf-8") as md_file:
        md_file.write("# Directory and File Contents\n\n")

        # File Tree
        md_file.write("## File Tree\n\n")
        md_file.write(f"{tree_content}\n\n")

        # File Contents
        md_file.write("## File Contents\n\n")
        for file_content in file_contents_list:
            match = re.match(
                r"#### 📄 (.+)\n\*\*Contents:\*\*\n(.+)", file_content, re.DOTALL
            )
            if match:
                file_path = match.group(1)
                content = match.group(2)
                md_file.write(f"### {file_path}\n\n")
                md_file.write("#### Contents\n\n")
                md_file.write("```\n")
                md_file.write(content)
                md_file.write("\n```\n\n")

    print(f"Markdown file generated at {output_path}")


def gather_file_contents(root_path: str, excludes: list, includes: list) -> list:
    """Gather individual file contents for chunking."""
    file_contents_list = []
    total_tokens = 0

    for dirpath, dirs, files in os.walk(root_path, topdown=True):
        dirs[:] = [
            d
            for d in dirs
            if not is_excluded(
                os.path.relpath(os.path.join(dirpath, d), start=root_path),
                excludes,
                includes,
            )
        ]
        for file in files:
            full_path = os.path.join(dirpath, file)
            relative_file_path = os.path.relpath(full_path, start=root_path)
            if is_excluded(relative_file_path, excludes, includes):
                continue  # Skip excluded files
            try:
                with open(full_path, "rb") as f:
                    header = f.read(64)
                    if b"\x00" in header:  # if binary data
                        outputString = f"\n#### 📄 {relative_file_path}\n**Contents:**\n<Binary data>\n"
                        file_contents_list.append(outputString)
                    else:  # if text data
                        f.seek(0)
                        contents = f.read().decode("utf-8")
                        outputString = f"\n#### 📄 {relative_file_path}\n**Contents:**\n{contents}\n"
                        file_contents_list.append(outputString)
            except Exception as e:
                file_contents_list.append(
                    f"\n#### ⚠️ {relative_file_path}\n**Contents:**\nError reading file {relative_file_path}: {e}\n"
                )
    return file_contents_list, total_tokens


def is_excluded(path: str, excludes: list, includes: list) -> bool:
    """Checks if a path should be excluded using pathspec."""
    spec = pathspec.PathSpec.from_lines("gitwildmatch", excludes)
    for include_pattern in includes:
        if spec.match_file(include_pattern):
            return False
    return spec.match_file(path)


def print_tree(
    root: str,
    root_path: str,
    excludes: list,
    includes: list,
    max_tokens: int,
    indent: str = "",
) -> str:
    """Prints the file structure of the directory tree."""
    items = sorted(os.listdir(root))
    tree_output = ""
    for item in items:
        full_path = os.path.join(root, item)
        relative_path = os.path.relpath(full_path, start=root_path)

        if os.path.isdir(full_path):
            if is_excluded(relative_path, excludes, includes):
                tree_output += f"{indent}[Excluded] 🚫📁 {relative_path}\n"
            else:
                tree_output += f"{indent}📁 {relative_path}\n"
                tree_output += print_tree(
                    full_path,
                    root_path,
                    excludes,
                    includes,
                    max_tokens,
                    indent + "    ",
                )
        else:
            token_length = get_file_token_length(full_path)
            if is_excluded(relative_path, excludes, includes):
                tree_output += f"{indent}[Excluded] 🚫📄 {relative_path}\n"
            else:
                if token_length > max_tokens:
                    tree_output += f"{indent}📄 {Fore.RED}{token_length}{Style.RESET_ALL} {relative_path}\n"
                else:
                    tree_output += f"{indent}📄 {token_length} {relative_path}\n"
    return tree_output


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
