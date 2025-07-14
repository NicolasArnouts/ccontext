# ccontext/file_system.py
import os
from pathlib import Path  # Add this import at the top
from typing import List, Tuple, Union

import mammoth
from colorama import Style
from pypdf import PdfReader
from wcmatch import glob

from ccontext.tokenizer import tokenize_text
from ccontext.utils import get_color_for_percentage, is_binary_file


def parse_gitignore(gitignore_path: str) -> List[str]:
    """Parses the .gitignore file and returns a list of patterns."""
    if not os.path.exists(gitignore_path):
        return []
    with open(gitignore_path, "r") as file:
        patterns = file.read().splitlines()
    return patterns


def is_excluded(path: str, excludes: List[str], includes: List[str]) -> bool:
    """Checks if a path should be excluded using wcmatch."""
    # Normalize the path to POSIX-style for consistent matching
    normalized_path = Path(path).as_posix()

    # If the path matches any include pattern, it should not be excluded
    if any(
        glob.globmatch(normalized_path, pattern, flags=glob.GLOBSTAR)
        for pattern in includes
    ):
        return False

    # Otherwise, apply the exclusion patterns
    return any(
        glob.globmatch(normalized_path, pattern, flags=glob.GLOBSTAR)
        for pattern in excludes
    )


def get_file_token_length(file_path: str) -> int:
    """Returns the token length of a file."""
    try:
        # For binary/uploadable files, return 1 token (for the reference)
        if is_binary_file(file_path):
            return -1

        # For text files, calculate tokens
        with open(file_path, "rb") as f:
            content = f.read()
            if b"\x00" in content[:1024]:  # Quick binary check
                return 1
            try:
                text = content.decode("utf-8")
                tokens = tokenize_text(text)
                return len(tokens)
            except UnicodeDecodeError:
                return 1  # Treat as binary if we can't decode
    except Exception:
        return -1


def get_pdf_token_length(file_path: str) -> int:
    """Returns the token length of a PDF file."""
    try:
        with open(file_path, "rb") as f:
            pdf_reader = PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            tokens = tokenize_text(text)
            return len(tokens)
    except Exception:
        return -1


def get_docx_token_length(file_path: str) -> int:
    """Returns the token length of a DOCX file."""
    try:
        with open(file_path, "rb") as docx_file:
            result = mammoth.extract_raw_text(docx_file)
            text = result.value
            tokens = tokenize_text(text)
            return len(tokens)
    except Exception:
        return -1


def collect_excludes_includes(
    default_excludes: List[str],
    additional_excludes: Union[str, List[str], None],
    additional_includes: Union[str, List[str], None],
    included_folders_files: Union[str, List[str], None],
    root_path: str,
    ignore_gitignore: bool,
) -> Tuple[List[str], List[str]]:
    """Combines default excluded items with additional exclusions and includes, and parses .gitignore."""
    # Ensure additional_excludes is a list
    if isinstance(additional_excludes, str):
        additional_excludes = [
            pattern.strip()
            for pattern in additional_excludes.split("|")
            if pattern.strip()
        ]
    elif isinstance(additional_excludes, list):
        additional_excludes = [
            pattern.strip() for pattern in additional_excludes if pattern.strip()
        ]
    else:
        additional_excludes = []

    # Ensure additional_includes is a list
    if isinstance(additional_includes, str):
        additional_includes = [
            pattern.strip()
            for pattern in additional_includes.split("|")
            if pattern.strip()
        ]
    elif isinstance(additional_includes, list):
        additional_includes = [
            pattern.strip() for pattern in additional_includes if pattern.strip()
        ]
    else:
        additional_includes = []

    # Ensure included_folders_files is a list
    if isinstance(included_folders_files, str):
        included_folders_files = [
            pattern.strip()
            for pattern in included_folders_files.split("|")
            if pattern.strip()
        ]
    elif isinstance(included_folders_files, list):
        included_folders_files = [
            pattern.strip() for pattern in included_folders_files if pattern.strip()
        ]
    else:
        included_folders_files = []

    # Command line arguments have highest priority
    includes = additional_includes  # Now a List[str]
    excludes = additional_excludes  # Now a List[str]

    # Include files from config if not already included via command line
    includes += [item for item in included_folders_files if item not in includes]

    # Exclude files from config if not already excluded via command line
    excludes += [item for item in default_excludes if item not in excludes]

    if not ignore_gitignore:
        gitignore_patterns = parse_gitignore(os.path.join(root_path, ".gitignore"))
        excludes.extend(gitignore_patterns)

    return excludes, includes


def print_tree(
    root: str,
    root_path: str,
    excludes: List[str],
    includes: List[str],
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
            percentage = (token_length / max_tokens) * 100
            color = get_color_for_percentage(percentage)
            if is_excluded(relative_path, excludes, includes):
                tree_output += f"{indent}[Excluded] 🚫📄 {relative_path}\n"
            else:
                tree_output += f"{indent}📄 {color} {token_length}{Style.RESET_ALL} {relative_path}\n"
    return tree_output
