# app/utils/token_counter.py
# Deterministic token counting using tiktoken (BPE tokenizer).
# Uses cl100k_base encoding — the same BPE used by GPT-4 and Claude.
# ~5% variance from Gemini's internal tokenizer but fully deterministic
# and requires no API call, making it ideal for real-time metrics.

import tiktoken

# Singleton encoder — loaded once at module import, cached for all subsequent calls
_encoder = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """
    Counts the exact number of BPE tokens in the given text.
    
    Args:
        text: Any string to tokenize.
        
    Returns:
        Integer token count. Never estimates — always computes deterministically.
    """
    if not text:
        return 0
    return len(_encoder.encode(text))


def compute_token_reduction_percent(original: int, compressed: int) -> float:
    """
    Computes the percentage of tokens saved.
    
    Returns:
        A float rounded to 1 decimal place. 
        Positive = reduction. 0.0 if no change.
    """
    if original == 0:
        return 0.0
    reduction = ((original - compressed) / original) * 100
    return round(reduction, 1)
