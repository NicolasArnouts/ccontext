import os
from ccontext.file_system import is_excluded, print_tree
from ccontext.tokenizer import tokenize_text


def print_file_tree(
    root_path: str,
    excludes: list,
    includes: list,
    for_preview: bool = False,
) -> str:
    """Print and capture the file tree section."""
    tree_output = print_tree(root_path, root_path, excludes, includes)

    header = (
        "========== File Tree ==========\n"
        if for_preview
        else "### ========== File Tree ==========\n"
    )
    footer = (
        "========== End of File Tree ==========\n"
        if for_preview
        else "### ========== End of File Tree ==========\n"
    )

    return f"{header}{tree_output}{footer}"


def gather_file_contents(root_path: str, excludes: list, includes: list) -> list:
    """Gather individual file contents for chunking."""
    file_contents_list = []
    total_tokens = 0

    for dirpath, dirs, files in os.walk(root_path, topdown=True):
        dirs[:] = [
            d
            for d in dirs
            if not is_excluded(
                os.path.relpath(os.path.join(dirpath, d), start=root_path),
                excludes,
                includes,
            )
        ]
        for file in files:
            full_path = os.path.join(dirpath, file)
            relative_file_path = os.path.relpath(full_path, start=root_path)
            if is_excluded(relative_file_path, excludes, includes):
                continue  # Skip excluded files
            try:
                with open(full_path, "rb") as f:
                    header = f.read(64)
                    if b"\x00" in header:  # if binary data
                        outputString = f"\n#### 📄 {relative_file_path}\n**Contents:**\n<Binary data>\n"
                        file_contents_list.append(outputString)
                    else:  # if text data
                        f.seek(0)
                        contents = f.read().decode("utf-8")
                        tokens = tokenize_text(contents)
                        total_tokens += len(tokens)
                        outputString = f"\n#### 📄 {relative_file_path}\n**Contents:**\n{contents}\n"
                        file_contents_list.append(outputString)
            except Exception as e:
                file_contents_list.append(
                    f"\n#### ⚠️ {relative_file_path}\n**Contents:**\nError reading file {relative_file_path}: {e}\n"
                )
            # # Add the token count to the tree output
            #file_contents_list.append(f"\n**Token Count:** {total_tokens}\n")
    return file_contents_list, total_tokens


def combine_initial_content(
    root_path: str, excludes: list, includes: list, context_prompt: str
) -> str:
    """Combine the initial content for the output."""
    context_prompt = f"## {context_prompt}\n\n"
    header = f"## Root Path: {root_path}\n\n"
    tree_output = print_file_tree(root_path, excludes, includes)

    return f"{context_prompt}{header}{tree_output}"
