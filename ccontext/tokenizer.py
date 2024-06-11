import tiktoken


def set_model_type_and_buffer(model_type: str, buffer_size: float):
    """
    Sets the model type and buffer size for tokenization.

    Args:
        model_type (str): The type of model to use for encoding.
        buffer_size (float): The buffer size as a fraction of max_tokens.
    """
    global MODEL_TYPE, BUFFER_SIZE
    MODEL_TYPE = model_type
    BUFFER_SIZE = buffer_size


def tokenize_text(text: str) -> list:
    """
    Tokenizes the given text using the specified model type.

    Args:
        text (str): The text to be tokenized.

    Returns:
        list: A list of token ids.
    """
    encoding = tiktoken.encoding_for_model(MODEL_TYPE)
    return encoding.encode(text)


def chunk_text(file_contents: list, max_tokens: int) -> list:
    """
    Splits the file contents into chunks that fit within the max_tokens limit, considering a buffer size.

    Args:
        file_contents (list): A list of strings representing file contents.
        max_tokens (int): The maximum number of tokens allowed per chunk.

    Returns:
        list: A list of strings, each representing a chunk.
    """
    # Calculate the number of tokens to reserve as a buffer
    buffer_tokens = int(max_tokens * BUFFER_SIZE)
    available_tokens = max_tokens - buffer_tokens

    current_chunk = ""  # The current chunk being built
    current_chunk_tokens = 0  # The token count of the current chunk
    chunks = []  # List to store all the chunks

    def add_chunk():
        """
        Adds the current chunk to the list of chunks and resets the current chunk.
        """
        nonlocal current_chunk, current_chunk_tokens
        if current_chunk.strip():  # Check if the current chunk is not empty
            chunks.append(current_chunk.strip())
        current_chunk = ""
        current_chunk_tokens = 0

    for file_content in file_contents:
        # Ensure the file content is a string
        if not isinstance(file_content, str):
            raise ValueError(f"Expected a string but got {type(file_content)}")

        # Tokenize the current file content
        tokens = tokenize_text(file_content)
        token_count = len(tokens)

        # If the file content exceeds the available tokens, split it into smaller pieces
        if token_count > available_tokens:
            split_contents = [
                file_content[i : i + available_tokens]
                for i in range(0, len(file_content), available_tokens)
            ]
            for split_content in split_contents:
                split_tokens = tokenize_text(split_content)
                split_token_count = len(split_tokens)
                if current_chunk_tokens + split_token_count > available_tokens:
                    add_chunk()
                current_chunk += split_content
                current_chunk_tokens += split_token_count
        else:
            # If adding the current file content exceeds the available tokens, create a new chunk
            if current_chunk_tokens + token_count > available_tokens:
                add_chunk()
            current_chunk += file_content
            current_chunk_tokens += token_count

    # Add the final chunk if it contains any content
    if current_chunk.strip():
        add_chunk()

    return chunks


# Example usage
set_model_type_and_buffer("gpt-4", 0.05)  # Set model type and buffer size

# Replace the ellipsis with actual file contents, for example:
file_contents = [
    "This is the content of file 1.",
    "This is the content of file 2.",
    "This is the content of file 3.",
    # Add more file contents as needed
]

max_tokens = 32000  # Set the maximum number of tokens per chunk

chunks = chunk_text(file_contents, max_tokens)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i + 1}: {len(tokenize_text(chunk))} tokens")
