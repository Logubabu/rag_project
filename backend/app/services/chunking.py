import re
from typing import List

def recursive_character_text_splitter(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> List[str]:
    """
    Splits text into chunks of maximum size `chunk_size` with an overlap of `chunk_overlap`.
    It tries to split by double newline, single newline, then space.
    """
    if not text:
        return []
        
    separators = ["\n\n", "\n", " ", ""]
    
    def _split_text(text: str, separator: str) -> List[str]:
        if separator == "":
            return list(text)
        return text.split(separator)
        
    def _merge_splits(splits: List[str], separator: str) -> List[str]:
        docs = []
        current_doc = []
        total_length = 0
        
        for d in splits:
            _len = len(d)
            if total_length + _len + (len(separator) if len(current_doc) > 0 else 0) > chunk_size:
                if total_length > 0:
                    docs.append(separator.join(current_doc))
                    
                    # Compute overlap
                    while total_length > chunk_overlap or (
                        total_length + _len + (len(separator) if len(current_doc) > 0 else 0) > chunk_size
                        and total_length > 0
                    ):
                        if not current_doc:
                            break
                        removed = current_doc.pop(0)
                        total_length -= len(removed) + (len(separator) if len(current_doc) > 0 else 0)
                        
            current_doc.append(d)
            total_length += _len + (len(separator) if len(current_doc) > 1 else 0)
            
        if current_doc:
            docs.append(separator.join(current_doc))
            
        return docs

    for sep in separators:
        splits = _split_text(text, sep)
        if any(len(s) > chunk_size for s in splits) and sep != "":
            continue
        
        merged = _merge_splits(splits, sep)
        
        # Check if we still have chunks that are too large (can happen if split is too big and next separator is needed)
        final_docs = []
        needs_further_splitting = False
        for m in merged:
            if len(m) > chunk_size and sep != "":
                needs_further_splitting = True
                break
                
        if needs_further_splitting:
            continue
            
        return merged
        
    # If all else fails, force split by character
    splits = _split_text(text, "")
    return _merge_splits(splits, "")
