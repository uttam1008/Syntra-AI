# Context Compressor — Technical Specification

| Field | Detail |
|---|---|
| **Engine** | Context Compressor |
| **Endpoint** | `POST /v1/compress` |
| **LLM Model** | Gemini 2.5 Flash |
| **Status** | ✅ Implemented & Live |

## 1. Core Purpose
Developers frequently submit large, noisy payloads (e.g., thousands of lines of server logs mixed with conversational filler). Passing this raw text to expensive reasoning models (like Gemini Pro or Claude) wastes tokens and dilutes the model's attention.

The **Context Compressor** acts as an aggressive semantic filter. It uses a fast, cheap model (Gemini Flash) to condense the input into the minimum required tokens, while strictly preserving technical signals (code blocks, error traces, file paths).

## 2. Pydantic Schemas

**Request (`CompressRequest`)**
- `input_text` (str): The raw text to compress. Minimum 10 characters.
- `preserve_code` (bool): Defaults to `True`. Instructs the engine not to summarize code blocks.

**Response (`CompressResponse`)**
- `original_length` (int): Total character count before compression.
- `compressed_length` (int): Total character count after compression.
- `compression_ratio` (float): Mathematical ratio (e.g., `0.45` means the text was reduced by 55%).
- `compressed_text` (str): The clean, high-signal payload.

## 3. Prompt Engineering Strategy
The System Prompt instructs the LLM to:
1. Remove all pleasantries, filler words, and conversational noise.
2. Summarize long-winded explanations into bullet points.
3. NEVER alter or summarize code blocks, JSON, error traces, or URLs.
4. Output *only* the compressed text, with no introductory dialogue.

## 4. Failure Modes
- If the LLM returns an empty string or malformed data, it raises an `HTTP 502 Bad Gateway`.
- If the input is too short, Pydantic immediately rejects it with `HTTP 422 Unprocessable Entity`.
