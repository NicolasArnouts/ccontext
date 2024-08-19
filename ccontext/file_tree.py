import os
import time
from typing import List, Tuple
from ccontext.file_node import FileNode
from ccontext.file_system import is_excluded
from ccontext.tokenizer import tokenize_text
from ccontext.utils import is_verbose, get_color_for_percentage
from colorama import Fore, Style
from wcmatch import glob
from pypdf import PdfReader
import io

def build_file_tree(
    root_path: str, excludes: List[str], includes: List[str]
) -> FileNode:
    # Record the start time
    start_time = time.time()

    def traverse_directory(current_path: str) -> FileNode:
        relative_path = os.path.relpath(current_path, start=root_path)
        node_type = "directory" if os.path.isdir(current_path) else "file"
        excluded = is_excluded(relative_path, excludes, includes)
        node = FileNode(
            os.path.basename(current_path),
            relative_path,
            node_type,
            excluded,
        )

        # Check elapsed time
        elapsed_time = time.time() - start_time

        # Check if 10 seconds have elapsed and print path in red if true
        if elapsed_time > 10:
            print(Fore.RED + relative_path + Style.RESET_ALL)

        if node_type == "directory" and not excluded:
            for item in sorted(os.listdir(current_path)):
                full_path = os.path.join(current_path, item)
                child_node = traverse_directory(full_path)
                node.add_child(child_node)
        elif node_type == "file" and not excluded:
            tokens, content = tokenize_file_content(current_path)
            node.set_tokens_and_content(tokens, content)
        return node

    return traverse_directory(root_path)

def is_excluded(path: str, excludes: List[str], includes: List[str]) -> bool:
    """Checks if a path should be excluded using wcmatch."""
    # If the path matches any include pattern, it should not be excluded
    if any(glob.globmatch(path, pattern, flags=glob.GLOBSTAR) for pattern in includes):
        return False

    # Otherwise, apply the exclusion patterns
    return any(
        glob.globmatch(path, pattern, flags=glob.GLOBSTAR) for pattern in excludes
    )

def tokenize_file_content(file_path: str) -> Tuple[int, str]:
    try:
        if file_path.lower().endswith('.pdf'):
            return extract_pdf_content(file_path)
        
        with open(file_path, "rb") as f:
            content = f.read()
            
        if b'\x00' in content[:1024]:  # Check if file is binary
            return 0, "Binary data"
        
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            text_content = content.decode('latin-1')  # Fallback encoding
        
        if is_verbose():
            print(file_path)
        
        tokens = tokenize_text(text_content)
        return len(tokens), text_content
    except Exception as e:
        return 0, f"Error reading file {file_path}: {str(e)}"

def extract_pdf_content(file_path: str) -> Tuple[int, str]:
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n\n"
        
        if is_verbose():
            print(f"Processing PDF: {file_path}")
        
        clean_text = text.strip()
        tokens = tokenize_text(clean_text)
        return len(tokens), clean_text
    except Exception as e:
        return 0, f"Error reading PDF file {file_path}: {str(e)}"

def extract_file_contents(node: FileNode) -> list:
    contents = []
    if node.node_type == "file":
        contents.append(f"\n#### 📄 {node.path}\n**Contents:**\n{node.content}\n")
    elif node.node_type == "directory":
        for child in node.children:
            contents.extend(extract_file_contents(child))
    return contents


def sum_file_tokens(node: FileNode) -> int:
    if node.node_type == "file":
        return node.tokens
    else:
        return sum(sum_file_tokens(child) for child in node.children)

def format_file_tree(
    node: FileNode, max_tokens: int, indent: str = "", useColors: bool = False
) -> str:
    output = ""
    if node.node_type == "directory":
        if node.excluded:
            output += f"{indent}[Excluded] 🚫📁 {node.name}\n"
        else:
            output += f"{indent}📁 {node.name}\n"
            for child in node.children:
                output += format_file_tree(
                    child, max_tokens, indent + "    ", useColors
                )
    else:
        percentage = node.tokens / max_tokens if max_tokens else 0
        color = get_color_for_percentage(percentage) if useColors else ""
        reset = Style.RESET_ALL if useColors else ""
        if node.excluded:
            output += f"{indent}[Excluded] 🚫📄 {node.name}\n"
        else:
            output += f"{indent}📄 {color}{node.tokens}{reset} {node.name}\n"
    return output