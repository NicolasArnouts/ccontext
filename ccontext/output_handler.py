from colorama import Fore, Style
from ccontext.utils import format_number
from ccontext.tokenizer import chunk_text, tokenize_text
from ccontext.clipboard import copy_to_clipboard


def handle_chunking_and_output(
    initial_content: str,
    file_contents_list: list,
    max_tokens: int,
    verbose: bool,
):
    """Calculate token length and handle chunking if necessary."""
    end_marker = "### ========== End of Detailed File Contents ==========\n"
    full_output = initial_content + "".join(file_contents_list) + end_marker
    total_tokens = len(tokenize_text(full_output))

    token_info = f"\nTokens: {Fore.GREEN if total_tokens <= max_tokens else Fore.RED}{format_number(total_tokens)}{Style.RESET_ALL}/{format_number(max_tokens)}"

    if total_tokens > max_tokens:
        print(
            f"{Fore.RED}The output exceeds the token limit and will need to be chunked.{Style.RESET_ALL}"
        )
        print(f"\n{token_info}")

        chunks = chunk_text(
            [initial_content] + file_contents_list + [end_marker], max_tokens
        )

        # uncomment to view all chunks, warning: stdout overload
        # print("CHUNKS: ", chunks)

        # Print chunk sizes
        chunk_sizes = [len(tokenize_text(chunk)) for chunk in chunks]
        for i, size in enumerate(chunk_sizes):
            print(f"Chunk {i + 1}: {size} tokens")

        for i, chunk in enumerate(chunks):
            chunk_header = f"### Chunk {i + 1} of {len(chunks)}"
            if i == 0:
                chunk = f"""## Initialization\nThe following content will be delivered in multiple chunks. This is to ensure all data is processed correctly. There will be a total of {len(chunks)} chunks. Thoroughly read the chunk and reply with a short summary of the content that was inserted. Until you receive the final chunk, this will be marked by '###This is the final chunk.###', you will have to make a summary of all the summaries that you gave. Once you have received the final chunk, reply with the final summary. '\n\n{chunk_header}: File Tree and Initial File Contents\n{chunk}\n###More chunks to follow...###"""
            elif i == len(chunks) - 1:
                chunk = f"{chunk_header}\n{chunk}\n###This is the final chunk.###"
            else:
                previous_chunk_summary = "Previous chunk ended with:\n" + "\n".join(
                    chunks[i - 1].splitlines()[-10:]
                )
                chunk = f"{chunk_header} (continued from Chunk {i})\n{previous_chunk_summary}\n{chunk}\n###More chunks to follow...###"

            print(
                f"{Fore.MAGENTA}(Chunk {i + 1}/{len(chunks)}){Style.RESET_ALL} {Fore.CYAN}Press Enter to continue or type 'q' to abort: {Style.RESET_ALL}",
                end="",
            )
            user_input = input()
            if user_input.lower() == "q":
                print(f"{Fore.YELLOW}Operation aborted by user.{Style.RESET_ALL}")
                break

            if verbose:
                print(f"\n{chunk_header}:")
                print(chunk)
            copy_to_clipboard(chunk)

        if verbose:
            print(
                f"{Fore.MAGENTA}\nSuccessfully finished all chunks ({len(chunks)}/{len(chunks)}){Style.RESET_ALL}"
            )
    else:
        print(token_info)
        if verbose:
            print(full_output)
        copy_to_clipboard(full_output)
