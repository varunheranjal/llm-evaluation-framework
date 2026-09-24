# Splits the input text into fixed-size chunks, with each new chunk overlapping part of the previous one to preserve context between chunks.

# Example: chunk_size=10, chunk_overlap=2 -> chunks start at 0, 8, 16, 24, etc.

# Basically --->> fixed_size_chunk("abcdefghijklmnopqrstuvwxyz", 10, 2) will output -->> ['abcdefghij', 'ijklmnopqr', 'qrstuvwxyz']


def fixed_size_chunk(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:

    if not text:
        return []

    step = chunk_size - chunk_overlap
    chunks = []

    start = 0
    while start < len(text):
        chunk = text[start: start + chunk_size].strip()

        if chunk:
            chunks.append(chunk)
        
        start += step
    
    return chunks
    