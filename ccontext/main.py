import os
import json
from colorama import Fore, Style
from pathlib import Path
import importlib.resources as resources
from run_crawlers import run_crawler

from ccontext.utils import initialize_environment, set_verbose
from ccontext.content_handler import (
    print_file_tree,
    gather_file_contents,
    combine_initial_content,
)
from ccontext.output_handler import handle_chunking_and_output
from ccontext.file_system import collect_excludes_includes
from ccontext.argument_parser import parse_arguments
from ccontext.tokenizer import set_model_type_and_buffer
from ccontext.pdf_generator import generate_pdf
from ccontext.md_generator import generate_md
from ccontext.file_tree import (
    build_file_tree,
    format_file_tree,
    extract_file_contents,
    sum_file_tokens,
)
from ccontext.file_node import FileNode

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

    with resources.files("ccontext").joinpath(DEFAULT_CONFIG_FILENAME).open("r") as f:
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
    generate_pdf_flag: bool = False,
    generate_md_flag: bool = False,
    crawl_flag: bool = False,
):
    root_path = os.path.abspath(root_path or os.getcwd())
    config = load_config(root_path, config_path)

    # Command line arguments have the highest priority
    cmd_includes = includes or []
    cmd_excludes = excludes or []

    # Collect excludes and includes, with priority rules applied
    config_includes = config.get("included_folders_files", [])
    config_excludes = config.get("excluded_folders_files", [])

    excludes, includes = collect_excludes_includes(
        config_excludes,
        cmd_excludes,
        cmd_includes,
        config_includes,
        root_path,
        ignore_gitignore,
    )

    max_tokens = max_tokens or int(config.get("max_tokens", 32000))

    verbose = verbose or config.get("verbose", False)
    set_verbose(verbose or config.get("verbose", False))

    context_prompt = config.get(
        "context_prompt",
        DEFAULT_CONTEXT_PROMPT,
    )
    set_model_type_and_buffer(
        config.get("model_type", "gpt-4o"), config.get("buffer_size", 0.05)
    )

    # init colorama
    initialize_environment()

    print(f"{Fore.CYAN}Root Path: {root_path}\n{Style.RESET_ALL}")

    # Build file tree once and use it
    root_node = build_file_tree(root_path, excludes, includes)

    # Always print the file tree in the CLI using the new format_file_tree function
    tree_output = format_file_tree(root_node, max_tokens, useColors=True)
    print(tree_output)

    if generate_pdf_flag:
        generate_pdf(root_path, root_node)

    if generate_md_flag:
        generate_md(root_node, root_path)

    if not generate_pdf_flag and not generate_md_flag:
        file_contents_list = extract_file_contents(root_node)
        initial_content = combine_initial_content(
            root_node, root_path, context_prompt, max_tokens
        )
        handle_chunking_and_output(
            initial_content, file_contents_list, max_tokens, verbose
        )

    if crawl_flag:
        urls_to_crawl = config.get("urls_to_crawl", [])
        #print("urls_to_crawl", urls_to_crawl)
        for url_config in urls_to_crawl:
            run_crawler(url_config)


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
        args.generate_pdf,
        args.generate_md,
        args.crawl,
    )
