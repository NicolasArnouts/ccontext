# ccontext

**ccontext (collect context)** is a cross-platform utility designed to streamline the process of gathering and sending the context of a directory to large language models (LLMs) like ChatGPT-4o. Our mission is to make collecting and sending context to an LLM as easy as possible.


## Features

- 🌟 **Easy Setup**: Quick installation and configuration.
- 🔧 **Configurable Exclusions and Inclusions**: Flexibly specify which files and directories to include or exclude.
- ✂️ **Tokenization and Chunking**: Automatically handles tokenization and chunking to stay within LLM token limits.
- 🌍 **Cross-Platform Support**: Supports Windows, macOS, and Linux.
- 🗣️ **Verbose Output**: Optional verbose mode for detailed output and debugging.
- 📝 **Prompt Templates** (Upcoming): Create and use custom templates for different types of prompts.

## Installation

### Using pip

ccontext is available on PyPI and can be installed using pip:

```sh
pip install ccontext
```

### From Source

1. Clone the repository:

    ```sh
    git clone https://github.com/oxillix/ccontext.git
    cd ccontext
    ```

2. Set up a virtual environment:

    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Install the package:

    ```sh
    pip install .
    ```

## Usage

### Basic Usage

1. Run `ccontext` in the current folder with default settings defined in `~/.ccontext/config.json`:

    ```sh
    ccontext
    ```

2. Specify a root path, exclusions, and inclusions:

    ```sh
    ccontext -p /path/to/directory -e ".git|node_modules" -i "important_file.txt|docs"
    ```

### Command-Line Arguments

- `-p, --root_path`: The root path to start the directory tree (default: current directory).
- `-e, --excludes`: Additional files or directories to exclude, separated by `|`, e.g., `node_modules|.git`.
- `-i, --includes`: Files or directories to include, separated by `|`, e.g., `important_file.txt|docs`.
- `-m, --max_tokens`: Maximum number of tokens allowed before chunking.
- `-c, --config`: Path to a custom configuration file.
- `-v, --verbose`: Enable verbose output to stdout.
- `-ig, --ignore_gitignore`: Ignore the `.gitignore` file for exclusions.

### Example

```sh
ccontext -p /home/user/project -e ".git|build" -i "README.md|src"
```

### Configuration

You can customize the behavior of `ccontext` by creating a configuration file. The default configuration file is `config.json` located in the user's home directory under `.ccontext`. You can also provide a custom configuration file via the `-c` argument.

### Sample `config.json`

```json
{
  "verbose": false,
  "max_tokens": 120000,
  "model_type": "gpt-4o",
  "buffer_size": 0.05,
  "excluded_folders_files": [
    ".git",
    "bin",
    "build",
    "node_modules",
    "venv",
    "__pycache__",
    "package-lock.json",
    "ccontext.egg-info",
    "dist"
  ],
  "context_prompt": "[[SYSTEM INSTRUCTIONS]] The following output presents a detailed directory structure and file contents from a specified root path. The file tree includes both excluded and included files and directories, clearly marking exclusions. Each file's content is displayed with comprehensive headings and separators to enhance readability and facilitate detailed parsing for extracting hierarchical and content-related insights. If the data represents a codebase, interpret and handle it as such, providing appropriate assistance as a programmer AI assistant. [[END SYSTEM INSTRUCTIONS]]"
}
```

## Use Cases

- **Codebase Context**: Send the entire codebase as context to an LLM in one go, avoiding the need to copy and paste snippets manually.

## Contributing

We welcome contributions to `ccontext`! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push them to your branch.
4. Submit a pull request with a description of your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the need to streamline the process of providing context to LLMs.
- Thanks to the contributors and users who have provided valuable feedback and suggestions.

## Future Ideas

Here are some ideas that might be implemented in future versions of `ccontext`:

Future versions of ccontext may include:

- **Document Support:** Incorporate the ability to handle documents such as PDFs and image files in prompts.
- **Binary File Handling:** Introduce mechanisms to manage non-text file types effectively.

---

Feel free to raise issues or contribute to the project. We appreciate your support!

**Nicolas Arnouts**  
[arnouts.software@gmail.com](mailto:arnouts.software@gmail.com)

[GitHub Repository](https://github.com/NicolasArnouts/ccontext)

---

### Badges

[![PyPI version](https://badge.fury.io/py/ccontext.svg)](https://badge.fury.io/py/ccontext)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/NicolasArnouts/ccontext/blob/main/LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg)]()

---