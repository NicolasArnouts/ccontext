import importlib.resources as resources
import json
import os
from pathlib import Path

from colorama import Fore, Style

from ccontext.argument_parser import parse_arguments
from ccontext.configurator import copy_default_config
from ccontext.content_handler import combine_initial_content
from ccontext.file_system import collect_excludes_includes
from ccontext.file_tree import build_file_tree, extract_file_contents, format_file_tree
from ccontext.md_generator import generate_md
from ccontext.output_handler import handle_chunking_and_output
from ccontext.pdf_generator import generate_pdf
from ccontext.run_crawlers import run_crawler
from ccontext.tokenizer import set_model_type_and_buffer
from ccontext.utils import initialize_environment, set_verbose

DEFAULT_CONFIG_FILENAME = "config.json"
USER_CONFIG_DIR = Path.home() / ".ccontext"
USER_CONFIG_PATH = USER_CONFIG_DIR / DEFAULT_CONFIG_FILENAME
CURRENT_CONFIG_FILENAME = ".ccontext-config.json"
DEFAULT_CONTEXT_PROMPT = """
[[SYSTEM INSTRUCTIONS]]
The following output represents a detailed directory structure and file contents from a specified root path. The file tree includes both excluded and included files and directories, clearly marking exclusions. Each file's content is displayed with comprehensive headings and separators to enhance readability and facilitate detailed parsing for extracting hierarchical and content-related insights. If the data represents a codebase, interpret and handle it as such, providing appropriate assistance as a programmer AI assistant. Always give full code file contents and the relative file paths of the files where you change code. Clearly explain what steps you are going to undertake, then proceed action and complete them one by one. Think ahead.
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

    if not USER_CONFIG_PATH.exists():
        print(f"{USER_CONFIG_PATH} does not exist yet, creating one")
        copy_default_config()

    with open(USER_CONFIG_PATH, "r") as f:
        print(f"{Fore.CYAN}Using user config file: {USER_CONFIG_PATH}{Style.RESET_ALL}")
        return json.load(f)


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
    crawl: bool = False,
):
    root_path = os.path.abspath(root_path or os.getcwd())
    config = load_config(root_path, config_path)

    # Get uploadable extensions from config
    uploadable_extensions = set(config.get("uploadable_extensions", []))

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
    # END CONFIG LOGIC

    # START MAIN LOGIC
    # init colorama
    initialize_environment()

    print(f"{Fore.CYAN}Root Path: {root_path}\n{Style.RESET_ALL}")

    # crawling should happen before tree building
    if crawl:
        urls_to_crawl = config.get("urls_to_crawl", [])
        # print("urls_to_crawl", urls_to_crawl)
        for url_config in urls_to_crawl:
            run_crawler(url_config)

    # Build file tree once and use it
    root_node = build_file_tree(root_path, excludes, includes, uploadable_extensions)

    # Always print the file tree in the CLI using the new format_file_tree function
    tree_output = format_file_tree(root_node, max_tokens, useColors=True)
    print(tree_output)

    if generate_pdf_flag:
        generate_pdf(root_path, root_node)

    if generate_md_flag:
        generate_md(root_node, root_path)

    # Generate clipboard output
    file_contents_list = extract_file_contents(root_node)
    initial_content = combine_initial_content(
        root_node, root_path, context_prompt, max_tokens
    )
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
        args.generate_pdf,
        args.generate_md,
        args.crawl,
    )
