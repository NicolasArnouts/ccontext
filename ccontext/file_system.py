# ccontext/file_system.py
import os
from pathlib import Path
from typing import Dict, List, Tuple, Union

import mammoth
from colorama import Style
from pypdf import PdfReader
from wcmatch import glob

from ccontext.tokenizer import tokenize_text
from ccontext.utils import get_color_for_percentage, is_binary_file


class GitignoreHandler:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.gitignore_patterns: Dict[Path, List[str]] = {}
        self._find_all_gitignores()

    def _find_all_gitignores(self):
        """Recursively find all .gitignore files in the directory tree."""
        for dirpath, _, filenames in os.walk(self.root_path):
            if ".gitignore" in filenames:
                dir_path = Path(dirpath)
                patterns = self._parse_gitignore(dir_path / ".gitignore")
                if patterns:
                    self.gitignore_patterns[dir_path] = patterns

    def _parse_gitignore(self, gitignore_path: Path) -> List[str]:
        """Parse a single .gitignore file and return its patterns."""
        try:
            with open(gitignore_path, "r") as file:
                lines = file.read().splitlines()

            patterns = []
            for line in lines:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Handle negation patterns (!)
                if line.startswith("!"):
                    # Convert negation pattern to include pattern
                    continue  # Skip for now as it requires special handling

                # Handle directory-only patterns
                is_dir_pattern = line.endswith("/")

                # Convert .gitignore pattern to glob pattern
                if not line.startswith("/"):
                    # Pattern matches files in any directory
                    pattern = f"**/{line}"
                else:
                    # Pattern is relative to the .gitignore file location
                    pattern = line[1:]  # Remove leading slash

                if is_dir_pattern:
                    pattern = f"{pattern}**"

                patterns.append(pattern)

            return patterns
        except Exception as e:
            print(f"Error parsing .gitignore at {gitignore_path}: {str(e)}")
            return []

    def should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored based on all relevant .gitignore files."""
        path = Path(path)
        try:
            relative_path = path.relative_to(self.root_path)
        except ValueError:
            return False

        # Check patterns from root to the file's location
        current = self.root_path
        for part in relative_path.parts[:-1]:
            current = current / part
            if current in self.gitignore_patterns:
                if self._matches_any_pattern(
                    relative_path, self.gitignore_patterns[current]
                ):
                    return True

        # Check patterns in the file's own directory
        file_dir = path.parent
        if file_dir in self.gitignore_patterns:
            return self._matches_any_pattern(
                relative_path, self.gitignore_patterns[file_dir]
            )

        return False

    def _matches_any_pattern(self, path: Path, patterns: List[str]) -> bool:
        """Check if a path matches any of the given patterns."""
        path_str = str(path.as_posix())
        return any(
            glob.globmatch(path_str, pattern, flags=glob.GLOBSTAR)
            for pattern in patterns
        )


def get_file_token_length(file_path: str) -> int:
    """Returns the token length of a file."""
    try:
        # For binary files, return -1 to indicate special handling needed
        if is_binary_file(file_path):
            return -1

        # For text files, calculate tokens
        with open(file_path, "rb") as f:
            content = f.read()
            if b"\x00" in content[:1024]:  # Quick binary check
                return -1
            try:
                text = content.decode("utf-8")
                tokens = tokenize_text(text)
                return len(tokens)
            except UnicodeDecodeError:
                return -1  # Treat as binary if we can't decode
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
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
    except Exception as e:
        print(f"Error processing PDF {file_path}: {str(e)}")
        return -1


def get_docx_token_length(file_path: str) -> int:
    """Returns the token length of a DOCX file."""
    try:
        with open(file_path, "rb") as docx_file:
            result = mammoth.extract_raw_text(docx_file)
            text = result.value
            tokens = tokenize_text(text)
            return len(tokens)
    except Exception as e:
        print(f"Error processing DOCX {file_path}: {str(e)}")
        return -1


def is_excluded(
    path: str,
    excludes: List[str],
    includes: List[str],
    gitignore_handler: GitignoreHandler | None = None,
) -> bool:
    """Checks if a path should be excluded using wcmatch and gitignore rules."""
    normalized_path = Path(path).as_posix()

    # First check includes - if included, never exclude
    if any(
        glob.globmatch(normalized_path, pattern, flags=glob.GLOBSTAR)
        for pattern in includes
    ):
        return False

    # Check gitignore rules if handler is provided
    if gitignore_handler and gitignore_handler.should_ignore(Path(path)):
        return True

    # Finally check explicit exclude patterns
    return any(
        glob.globmatch(normalized_path, pattern, flags=glob.GLOBSTAR)
        for pattern in excludes
    )


def collect_excludes_includes(
    default_excludes: List[str],
    additional_excludes: Union[str, List[str], None],
    additional_includes: Union[str, List[str], None],
    included_folders_files: Union[str, List[str], None],
    root_path: str,
    ignore_gitignore: bool,
) -> Tuple[List[str], List[str], GitignoreHandler]:
    """Combines default excluded items with additional exclusions and includes."""

    # Convert all inputs to lists
    def to_list(value: Union[str, List[str], None]) -> List[str]:
        if isinstance(value, str):
            return [pattern.strip() for pattern in value.split("|") if pattern.strip()]
        elif isinstance(value, list):
            return [pattern.strip() for pattern in value if pattern.strip()]
        return []

    additional_excludes = to_list(additional_excludes)
    additional_includes = to_list(additional_includes)
    included_folders_files = to_list(included_folders_files)

    # Command line includes have highest priority
    includes = additional_includes.copy()

    # Add config includes if not already included
    includes.extend([item for item in included_folders_files if item not in includes])

    # Command line excludes have highest priority
    excludes = additional_excludes.copy()

    # Add default excludes if not already excluded
    excludes.extend([item for item in default_excludes if item not in excludes])

    # Create gitignore handler if needed
    gitignore_handler = None if ignore_gitignore else GitignoreHandler(root_path)

    return excludes, includes, gitignore_handler


def print_tree(
    root: str,
    root_path: str,
    excludes: List[str],
    includes: List[str],
    max_tokens: int,
    gitignore_handler: GitignoreHandler = None,
    indent: str = "",
) -> str:
    """Prints the file structure of the directory tree."""
    items = sorted(os.listdir(root))
    tree_output = ""

    for item in items:
        full_path = os.path.join(root, item)
        relative_path = os.path.relpath(full_path, start=root_path)

        if os.path.isdir(full_path):
            if is_excluded(relative_path, excludes, includes, gitignore_handler):
                tree_output += f"{indent}[Excluded] 🚫📁 {relative_path}\n"
            else:
                tree_output += f"{indent}📁 {relative_path}\n"
                tree_output += print_tree(
                    full_path,
                    root_path,
                    excludes,
                    includes,
                    max_tokens,
                    gitignore_handler,
                    indent + "    ",
                )
        else:
            token_length = get_file_token_length(full_path)
            percentage = (token_length / max_tokens) * 100 if token_length > 0 else 0
            color = get_color_for_percentage(percentage)

            if is_excluded(relative_path, excludes, includes, gitignore_handler):
                tree_output += f"{indent}[Excluded] 🚫📄 {relative_path}\n"
            else:
                if token_length == -1:  # Binary file
                    tree_output += f"{indent}📎 {relative_path}\n"
                else:
                    tree_output += f"{indent}📄 {color} {token_length}{Style.RESET_ALL} {relative_path}\n"

    return tree_output
