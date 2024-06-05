import tiktoken


def set_model_type_and_buffer(model_type: str, buffer_size: float):
    global MODEL_TYPE, BUFFER_SIZE
    MODEL_TYPE = model_type
    BUFFER_SIZE = buffer_size


def tokenize_text(text: str) -> list:
    encoding = tiktoken.encoding_for_model(MODEL_TYPE)
    return encoding.encode(text)


def chunk_text(file_contents: list, max_tokens: int) -> list:
    buffer_tokens = int(max_tokens * BUFFER_SIZE)  # 5% buffer
    available_tokens = max_tokens - buffer_tokens

    current_chunk = ""
    current_chunk_tokens = 0
    chunks = []

    for file_content in file_contents:
        tokens = tokenize_text(file_content)
        if current_chunk_tokens + len(tokens) <= available_tokens:
            current_chunk += file_content + "\n"
            current_chunk_tokens += len(tokens)
        else:
            if current_chunk_tokens > 0:
                chunks.append(current_chunk.strip())
            current_chunk = file_content + "\n"
            current_chunk_tokens = len(tokens)

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
