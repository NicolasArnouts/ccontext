import os
from typing import List, Tuple
import pathspec
from ccontext.tokenizer import tokenize_text


def parse_gitignore(gitignore_path: str) -> List[str]:
    """Parses the .gitignore file and returns a list of patterns."""
    if not os.path.exists(gitignore_path):
        return []
    with open(gitignore_path, "r") as file:
        patterns = file.read().splitlines()
    return patterns


def is_excluded(path: str, excludes: List[str], includes: List[str]) -> bool:
    """Checks if a path should be excluded using pathspec."""
    spec = pathspec.PathSpec.from_lines("gitwildmatch", excludes)
    for include_pattern in includes:
        if spec.match_file(include_pattern):
            return False
    return spec.match_file(path)


def get_file_token_length(file_path: str) -> int:
    """Returns the token length of a file."""
    try:
        with open(file_path, "rb") as f:
            header = f.read(64)
            if b"\x00" in header:  # if binary data
                return 0
            f.seek(0)
            contents = f.read().decode("utf-8")
            tokens = tokenize_text(contents)
            return len(tokens)
    except Exception as e:
        return -1


def collect_excludes_includes(
    default_excludes: List[str],
    additional_excludes: List[str],
    additional_includes: List[str],
    root_path: str,
    ignore_gitignore: bool,
) -> Tuple[List[str], List[str]]:
    """Combines default excluded items with additional exclusions and includes, and parses .gitignore."""
    if isinstance(additional_excludes, str):
        additional_excludes = additional_excludes.split("|")
    if isinstance(additional_includes, str):
        additional_includes = additional_includes.split("|")

    excludes = default_excludes + (additional_excludes if additional_excludes else [])
    includes = additional_includes if additional_includes else []

    if not ignore_gitignore:
        gitignore_patterns = parse_gitignore(os.path.join(root_path, ".gitignore"))
        excludes.extend(gitignore_patterns)

    return excludes, includes


def print_tree(
    root: str,
    root_path: str,
    excludes: List[str],
    includes: List[str],
    indent: str = "",
) -> str:
    """Prints the file structure of the directory tree."""
    items = sorted(os.listdir(root))
    tree_output = ""
    for item in items:
        full_path   = os.path.join(root, item)
        relative_path = os.path.relpath(full_path, start=root_path)

        if os.path.isdir(full_path):
            if is_excluded(relative_path, excludes, includes):
                tree_output += f"{indent}[Excluded] 🚫📁 {relative_path}\n"
            else:
                tree_output += f"{indent}📁 {relative_path}\n"
                tree_output += print_tree(
                    full_path, root_path, excludes, includes, indent + "    "
                )
        else:
            token_length = get_file_token_length(full_path)
            if is_excluded(relative_path, excludes, includes):
                tree_output += f"{indent}[Excluded] 🚫📄 {relative_path}\n"
            else:
                tree_output += f"{indent}📄 {token_length} {relative_path}\n"
    return tree_output
