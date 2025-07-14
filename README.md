# ccontext

**ccontext (collect-context)** is a cross-platform utility designed to streamline the process of gathering and sending the context of a directory to large language models (LLMs) like ChatGPT-4o. Our mission is to make collecting and sending context to an LLM as easy as possible.

## 🚀 Demo: Witness ccontext in Action! 🎥

⚠️ Warning: You May Be Amazed! 🤯

https://github.com/user-attachments/assets/c0a98dbc-d971-41dc-abe1-dad4be42e1ee

## Features

**Features**

- 🌟 **Easy Setup**: Quick installation and configuration.
- 🌍 **Cross-Platform Support**: Supports Windows, macOS, and Linux.
- 💾 **Binary File Support**: Handle various binary files including PDFs, Word documents, images, audio, and video files.
- 📄 **Markdown and PDF Generation**: Generate detailed Markdown and PDF files of the directory structure and file contents.
- 🌐 **Crawling of (documentation) Sites**: Crawl and gather data from multiple sites using a specified list of URLs.
- ✂️ **Tokenization and Chunking**: Automatically handles tokenization and chunking to stay within LLM token limits.
- 🔧 **Configurable Exclusions and Inclusions**: Flexibly specify which files and directories to include or exclude.
- 🗣️ **Verbose Output**: Optional verbose mode for detailed output and debugging.
- 📝 **Prompt Templates** (Upcoming): Create and use custom templates for different types of prompts.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Binary File Handling](#binary-file-handling)
- [Document Crawling](#document-crawling)
- [Use Cases and Examples](#use-cases-and-examples)
- [Troubleshooting](#troubleshooting)
- [Development Guide](#development-guide)

## Installation

### Using pipx (Recommended)

We recommend installing ccontext using pipx. pipx is a tool that lets you install and run Python applications in isolated environments, ensuring clean installation and easy management of CLI applications.

1. First, install pipx if you haven't already:

   ```sh
   # On macOS
   brew install pipx
   pipx ensurepath

   # On Ubuntu/Debian
   sudo apt install pipx
   pipx ensurepath

   # On Windows
   python -m pip install --user pipx
   python -m pipx ensurepath
   # or read https://pipx.pypa.io/stable/installation/#on-windows
   ```

2. Install ccontext using pipx:

   ```sh
   pipx install ccontext
   ```

Why use pipx?

- **Isolated Environment**: Each application runs in its own virtual environment
- **No Dependency Conflicts**: Avoids conflicts with other Python packages
- **Easy Updates**: Simple command to upgrade (`pipx upgrade ccontext`)
- **Clean Uninstallation**: Remove everything with one command (`pipx uninstall ccontext`)
- **Global Access**: Installed applications are available system-wide

### Alternative: Installing from Source

If you prefer to install from source:

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

1. Run `ccontext` in the folder to ccollect with default settings defined in `~/.ccontext/config.json`:

   ```sh
   ccontext
   ```

2. Specify a root path, exclusions, and inclusions:

   ```sh
   ccontext -p /path/to/directory -e ".git|node_modules" -i "important_file.txt|docs"
   ```

### Command-Line Arguments

- `-h, --help`: Show help message.
- `-p, --root_path`: The root path to start the directory tree (default: current directory).
- `-e, --excludes`: Additional files or directories to exclude, separated by `|`, e.g., `node_modules|.git`.
- `-i, --includes`: Files or directories to include, separated by `|`, e.g., `important_file.txt|docs`.
- `-m, --max_tokens`: Maximum number of tokens allowed before chunking.
- `-c, --config`: Path to a custom configuration file.
- `-v, --verbose`: Enable verbose output to stdout.
- `-ig, --ignore_gitignore`: Ignore the `.gitignore` file for exclusions.
- `-g, --generate-pdf`: Generate a PDF of the directory tree and file contents.
- `-gm, --generate-md`: Generate a Markdown file of the directory tree and file contents.
- `--crawl`: Crawls the sites specified in the config.

### Example

```sh
ccontext -p /home/user/project -e ".git|build" -i "README.md|src"
```

## Configuration

### Configuration File Location

ccontext looks for configuration in the following order:

1. Custom config file specified via `-c` argument
2. `.ccontext-config.json` in the current directory
   - If present, ccontext will automatically detect and use this local configuration file
   - Create this file in the same directory where you run the ccontext command
3. `~/.ccontext/config.json` (default user configuration)

### Configuration Options

```json
{
  "verbose": false, // Enable detailed output
  "max_tokens": 115000, // Maximum tokens before chunking
  "model_type": "gpt-4o", // LLM model type for tokenization
  "buffer_size": 0.05, // Token buffer size (0-1)

  // System prompt for LLM context
  "context_prompt": "[[SYSTEM INSTRUCTIONS]] The following output represents...",

  // Web crawler configuration
  "urls_to_crawl": [
    {
      "url": "https://www.django-rest-framework.org/",
      "match": ["https://www.django-rest-framework.org/**"],
      "exclude": ["https://www.django-rest-framework.org/community/**"],
      "selector": "",
      "maxPagesToCrawl": 100,
      "outputFileName": "django-rest-framework.org.json",
      "maxTokens": 10000000
    }
  ],

  // Files/folders to explicitly include
  "included_folders_files": [],

  // Files/folders to exclude (supports glob patterns)
  "excluded_folders_files": [
    "**/.git",
    "**/bin",
    "**/build",
    "**/node_modules/**",
    "**/venv",
    "**/__pycache__",
    "**/package-lock.json",
    "**/ccontext.egg-info",
    "**/dist",
    "**/__tests__",
    "**/coverage",
    "**/.next",
    "**/pnpm-lock.yaml",
    "**/poetry.lock",
    "**/ccontext-output.pdf",
    "**/ccontext-output.md",
    "**/*.phpstorm.meta.php",
    "**/*.min.js",
    "**/composer.lock",
    "**/*.lock",
    "**/vendor",
    "**/laravel_access.log",
    "**/*.DS_Store",
    "**/*.tox"
  ],

  // File extensions that can be uploaded to LLMs
  "uploadable_extensions": [
    // Documents
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",

    // Images
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".tiff",
    ".webp",
    ".heic",

    // Audio
    ".mp3",
    ".wav",
    ".ogg",
    ".flac",
    ".aac",
    ".m4a",

    // Video
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".webm",

    // Archives
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",

    // Binary/System
    ".exe",
    ".dll",
    ".iso",
    ".dmg",
    ".bin",
    ".dat",
    ".apk",
    ".img",
    ".so",
    ".swf",
    ".psd"
  ]
}
```

### Understanding Glob Patterns

ccontext uses the `wcmatch` library for glob pattern matching, which gives you powerful but easy-to-use file matching capabilities. Here's a simple guide to using glob patterns:

1. **Important Wildcards Explained:**

   - `*` (single star): Matches anything in the current folder only

     ```
     "*.txt"      # Matches: a.txt, b.txt  (in current folder)
     "*.txt"      # Won't match: sub/a.txt, deep/sub/b.txt
     ```

   - `**` (double star): Matches any number of folders

     ```
     "**/temp"    # Matches: temp, sub/temp, deep/sub/temp
     "**/temp"    # Won't match: temp/file.txt
     ```

   - `**/*` (double star slash star): Matches everything in all folders

     ```
     "**/*.txt"   # Matches: a.txt, sub/b.txt, very/deep/c.txt
     "**/*"       # Matches everything, everywhere
     ```

   - `?` matches any single character
   - `.txt` matches exact file extension

2. **Simple Examples:**

   ```json
   {
     "excluded_folders_files": [
       // Basic matching
       "temp.txt", // Matches exact file temp.txt
       "*.txt", // Matches all .txt files in root folder
       "**/*.txt", // Matches all .txt files in any folder

       // Folder matching
       "temp/*", // Matches everything in temp folder
       "**/temp", // Matches temp folder anywhere
       "**/temp/**", // Matches everything in any temp folder

       // Common use cases
       "**/node_modules", // Matches node_modules folders anywhere
       "**/__pycache__", // Matches Python cache folders
       "**/*.pyc", // Matches Python compiled files
       "build/*" // Matches everything in build folder
     ]
   }
   ```

3. **Tips for Beginners:**
   - Start simple! Use `*.ext` for file extensions
   - Use `**/` when you want to match in any folder
   - Test your patterns with a small folder first
   - When in doubt, be more specific
   - Remember, patterns are case-sensitive

The glob system is very forgiving - if you make a mistake, it usually just won't match anything rather than causing errors. Feel free to experiment!

### Configuration Options Explained

| Option                 | Description                     | Default       |
| ---------------------- | ------------------------------- | ------------- |
| verbose                | Enable detailed output          | false         |
| max_tokens             | Maximum tokens before chunking  | 115000        |
| model_type             | LLM model type for tokenization | "gpt-4o"      |
| buffer_size            | Token buffer size (0-1)         | 0.05          |
| excluded_folders_files | Glob patterns for exclusion     | [".git", ...] |
| included_folders_files | Glob patterns for inclusion     | []            |
| uploadable_extensions  | File extensions to upload       | [".pdf", ...] |

## Binary File Handling

ccontext supports handling binary files through the `uploadable_extensions` configuration.

### Supported Binary Files

- **Documents**: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.heic`
- **Audio**: `.mp3`, `.wav`, `.ogg`, `.flac`, `.aac`, `.m4a`
- **Video**: `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.webm`
- **Archives**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`
- **Binary/System**: `.exe`, `.dll`, `.iso`, `.dmg`, `.bin`, `.dat`, `.apk`, `.img`, `.so`, `.swf`, `.psd`

### Binary File Processing

- Binary files matching `uploadable_extensions` are prepared for upload to LLMs
- File references are automatically copied to clipboard
- Most LLM providers limit maximum of X binary files per prompt
- Rate limits may apply based on your LLM provider

Example configuration for handling specific file types:

```json
{
  "uploadable_extensions": [".pdf", ".jpg", ".png", ".xlsx"]
}
```

## Document Crawling

The crawling feature allows you to gather documentation from websites for context.

### Crawler Configuration

```json
{
  "urls_to_crawl": [
    {
      "url": "https://docs.example.com",
      "match": ["https://docs.example.com/**"],
      "exclude": ["https://docs.example.com/internal/**"],
      "selector": "",
      "maxPagesToCrawl": 100,
      "outputFileName": "docs.json",
      "maxTokens": 2000000
    }
  ]
}
```

### Crawler Options

- **url**: Starting URL for crawling
- **match**: Glob patterns for URLs to include
- **exclude**: Glob patterns for URLs to exclude
- **selector**: CSS selector for content extraction
- **maxPagesToCrawl**: Limit on pages to crawl
- **outputFileName**: Name of output file
- **maxTokens**: Maximum tokens to collect

### Best Practices

- Use specific `match` patterns
- Respect robots.txt and site policies

## Use Cases and Examples

### Common Usage Patterns

1. **Analyzing a Python Project**

```sh
ccontext -p /path/to/project -e "venv|__pycache__|*.pyc"
```

2. **Processing Documentation**

```sh
ccontext -p ./docs --crawl -gm
```

3. **Including Specific Files**

```sh
ccontext -i "README.md|docs/*|*.py"
```

4. **Generating PDF and Markdown**

```sh
ccontext -g -gm  # Generates both PDF and Markdown
```

### Integration Examples

1. **With GitHub Copilot**

```sh
ccontext -p . -e "node_modules|dist" -i "src/**/*.ts"
```

2. **With ChatGPT (webapp has max 32k) **

```sh
ccontext -p . --max_tokens 32000
```

## Troubleshooting

### Common Issues

1. **Clipboard Issues in SSH**

   - Issue: Cannot copy to clipboard in SSH session
   - Solution:
     - Use SSH with X11 forwarding (`ssh -X user@host`), test using xeyes
     - On Mac, install XQuartz (`brew install --cask xquartz`)

2. **Token Limit Exceeded**

   - Issue: Content too large for LLM
   - Solution: Adjust `max_tokens` or use chunking feature

3. **Binary File Handling**
   - Issue: Binary files not being processed
   - Solution: Check `uploadable_extensions` configuration

### Platform-Specific Issues

#### Windows: Use WSL if possible!

Otherwise:

- Issue: Path separators in configuration
- Solution: Use forward slashes or escaped backslashes

#### Linux

- Issue: X11 clipboard support
- Solution: Install xclip or xsel

#### macOS

- Issue: Clipboard permissions
- Solution: Grant terminal app accessibility permissions

## Development Guide

### Project Structure

```
ccontext/
├── ccontext/           # Main package directory
│   ├── __init__.py
│   ├── main.py         # Entry point
│   ├── file_tree.py    # Tree operations
│   └── ...
├── tests/              # Test directory
├── docs/               # Documentation
└── examples/           # Example configurations
```

### Development Setup

1. Clone the repository
2. Create a virtual environment
3. Install development dependencies
4. Run tests

```sh
git clone https://github.com/oxillix/ccontext.git
# or
git clone git@github.com:NicolasArnouts/ccontext.git
cd ccontext
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
pip3 install -e .
```

### Contributing Guidelines

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- use isort and black
- Use type hints
- Keep functions focused and small

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors! 😊
- Inspired by the need for better context handling in AI interactions.
- Built with love and passion for the developer community! 💖

---

Feel free to raise issues or contribute to the project. We appreciate your support!

Happy coding adventures! 🚀
**Nicolas Arnouts**

Looking for a skilled freelancer? I'm available for hire!
Let's collaborate — reach out to me at:
arnouts.software@gmail.com

---

### Badges

[![PyPI version](https://badge.fury.io/py/ccontext.svg)](https://badge.fury.io/py/ccontext)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/NicolasArnouts/ccontext/blob/main/LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg)]()

## Using in WSL2 Environment

When using ccontext's web crawling feature in WSL2, you can use crawl4ai for reliable web content extraction:

1. First, set up the WSL2 environment:

```bash
python -m ccontext.fix_wsl
```

2. Then run the crawler as usual:

```bash
python -m ccontext --crawl
```

The crawler will automatically detect WSL2 and configure the environment appropriately. If you prefer to use the crawler directly:

```bash
python -m ccontext.run_crawlers --url https://example.com --output example.md
```

### WSL2 Troubleshooting

If you encounter issues with the crawler in WSL2:

1. Ensure Python and dependencies are properly installed
2. Try running with explicit parameters:
   ```bash
   python -m ccontext.run_crawlers --url https://example.com --output example.md --max-pages 10
   ```
3. Check that any security software isn't blocking the network connections
4. For more detailed logging, add the --verbose flag
