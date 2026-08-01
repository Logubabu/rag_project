import re

def recursive_text_splitter(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """
    Splits text recursively. 
    First tries to split by double newlines, then single newlines, then spaces, then chars.
    """
    separators = ["\n\n", "\n", " ", ""]
    
    def _split(text: str, separators: list[str]) -> list[str]:
        if len(text) <= chunk_size:
            return [text]
            
        separator = separators[0]
        for sep in separators:
            if sep == "":
                separator = sep
                break
            if sep in text:
                separator = sep
                break
                
        if separator != "":
            splits = text.split(separator)
        else:
            splits = list(text)
            
        chunks = []
        current_chunk = ""
        
        for s in splits:
            if len(current_chunk) + len(separator) + len(s) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Add overlap by keeping the last part of current_chunk
                if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                    current_chunk = current_chunk[-chunk_overlap:] + separator + s
                else:
                    current_chunk = s
            else:
                if current_chunk:
                    current_chunk += separator + s
                else:
                    current_chunk = s
                    
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        # Recursive check if any chunk is still too large
        final_chunks = []
        next_seps = separators[separators.index(separator) + 1:] if separator in separators else [""]
        
        for chunk in chunks:
            if len(chunk) > chunk_size and next_seps:
                final_chunks.extend(_split(chunk, next_seps))
            else:
                # If still too large but no more separators (should not happen with char split)
                while len(chunk) > chunk_size:
                    final_chunks.append(chunk[:chunk_size])
                    chunk = chunk[chunk_size - chunk_overlap:]
                if chunk:
                    final_chunks.append(chunk)
                    
        return final_chunks
        
    return _split(text, separators)
