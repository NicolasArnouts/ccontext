import argparse
import sys
from colorama import Fore, Style
import os


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="A script to display a directory structure and file contents with chunking if needed."
    )
    parser.add_argument(
        "-p",
        "--root_path",
        required=False,
        default=os.getcwd(),
        help="The root path to start the directory tree (default: current directory).",
    )
    parser.add_argument(
        "-e",
        "--excludes",
        required=False,
        default="",
        help='Additional files or directories to exclude, separated by "|", e.g. "node_modules|.git"',
    )
    parser.add_argument(
        "-i",
        "--includes",
        required=False,
        default="",
        help='Files or directories to include, separated by "|", e.g. "important_file.txt|docs"',
    )
    parser.add_argument(
        "-m",
        "--max_tokens",
        required=False,
        type=int,
        help="Maximum number of tokens allowed before chunking.",
    )
    parser.add_argument(
        "-c",
        "--config",
        required=False,
        default=None,
        help="Path to a custom configuration file.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output to stdout.",
    )
    parser.add_argument(
        "-ig",
        "--ignore_gitignore",
        action="store_true",
        help="Ignore the .gitignore file for exclusions.",
    )
    parser.add_argument(
        "-g",
        "--generate-pdf",
        action="store_true",
        help="Generate a PDF of the directory tree and file contents.",
    )
    parser.add_argument(
        "-gm",
        "--generate-md",
        action="store_true",
        help="Generate a Markdown file of the directory tree and file contents.",
    )
    parser.add_argument(
        "--crawl",
        action="store_true",
        help="Crawls according to the urls_to_crawl set in the config.json",
    )

    args, unknown = parser.parse_known_args()
    if unknown:
        print(f"{Fore.RED}Unrecognized arguments: {' '.join(unknown)}{Fore.RESET}")
        parser.print_help()
        sys.exit(1)

    return args
