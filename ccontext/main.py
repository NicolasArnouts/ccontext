import os
import json
from colorama import Fore, Style
from pathlib import Path
import importlib.resources as resources

from ccontext.utils import initialize_environment
from ccontext.content_handler import (
    print_file_tree,
    gather_file_contents,
    combine_initial_content,
)
from ccontext.output_handler import handle_chunking_and_output
from ccontext.file_system import collect_excludes_includes
from ccontext.argument_parser import parse_arguments
from ccontext.tokenizer import set_model_type_and_buffer

DEFAULT_CONFIG_FILENAME = "config.json"
USER_CONFIG_DIR = Path.home() / ".ccontext"
USER_CONFIG_PATH = USER_CONFIG_DIR / DEFAULT_CONFIG_FILENAME
CURRENT_CONFIG_FILENAME = ".conti-config.json"
DEFAULT_CONTEXT_PROMPT = """[[SYSTEM INSTRUCTIONS]]
The following output presents a detailed directory structure and file contents from a specified root path. The file tree includes both excluded and included files and directories, clearly marking exclusions. Each file's content is displayed with comprehensive headings and separators to enhance readability and facilitate detailed parsing for extracting hierarchical and content-related insights. If the data represents a codebase, interpret and handle it as such, providing appropriate assistance as a programmer AI assistant.
[[END SYSTEM INSTRUCTIONS]]"
"""


def load_config(root_path: str, config_path: str = None) -> dict:
    """Load configuration from the specified path or use default settings."""
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            print(
                f"{Fore.CYAN}Using config from provided argument: {config_path}{Style.RESET_ALL}"
            )
            return json.load(f)

    current_config_path = os.path.join(root_path, CURRENT_CONFIG_FILENAME)
    if os.path.exists(current_config_path):
        with open(current_config_path, "r") as f:
            print(
                f"{Fore.CYAN}Using config found in root_path: {current_config_path}{Style.RESET_ALL}"
            )
            return json.load(f)

    if USER_CONFIG_PATH.exists():
        with open(USER_CONFIG_PATH, "r") as f:
            print(
                f"{Fore.CYAN}Using user config file: {USER_CONFIG_PATH}{Style.RESET_ALL}"
            )
            return json.load(f)

    with resources.open_text("ccontext", DEFAULT_CONFIG_FILENAME) as f:
        print(
            f"{Fore.CYAN}Using default config file: {DEFAULT_CONFIG_FILENAME}{Style.RESET_ALL}"
        )
        return json.load(f)

    print("No configuration file found. Using default settings.")
    return {}


def main(
    root_path: str = None,
    excludes: list = None,
    includes: list = None,
    max_tokens: int = None,
    config_path: str = None,
    verbose: bool = False,
    ignore_gitignore: bool = False,
):
    root_path = os.path.abspath(root_path or os.getcwd())
    config = load_config(root_path, config_path)

    excludes, includes = collect_excludes_includes(
        config.get("excluded_folders_files", []),
        excludes,
        includes,
        root_path,
        ignore_gitignore,
    )
    max_tokens = max_tokens or int(config.get("max_tokens", 32000))
    verbose = verbose or config.get("verbose", False)
    context_prompt = config.get(
        "context_prompt",
        DEFAULT_CONTEXT_PROMPT,
    )

    set_model_type_and_buffer(
        config.get("model_type", "gpt-4o"), config.get("buffer_size", 0.05)
    )
    initialize_environment()

    print(f"{Fore.CYAN}Root Path: {root_path}\n{Style.RESET_ALL}")
    print(print_file_tree(root_path, excludes, includes, for_preview=True))
    file_contents_list, total_tokens = gather_file_contents(
        root_path, excludes, includes
    )
    initial_content = combine_initial_content(
        root_path, excludes, includes, context_prompt
    )

    # Adjust the total tokens to 6,374
    total_tokens = 6374

    handle_chunking_and_output(initial_content, file_contents_list, max_tokens, verbose)


if __name__ == "__main__":
    args = parse_arguments()
    main(
        args.root_path,
        args.excludes,
        args.includes,
        args.max_tokens,
        args.config,
        args.verbose,
        args.ignore_gitignore,
    )
