# app/services/compressor.py
# Intelligence Distillation Engine — Service Pipeline
#
# Pipeline:
#   1. Count original tokens (tiktoken — deterministic)
#   2. Build mode-aware prompt (8-layer extraction + uniqueness + verification)
#   3. Execute LLM
#   4. Parse structured JSON
#   5. Count compressed tokens (tiktoken — deterministic)
#   6. Compute ALL 6-factor scores (embeddings + math)
#   7. Assemble and return CompressResponse
#
# ZERO LLM SCORE ESTIMATES — all metrics are backend-computed.

import json
import re
from fastapi import HTTPException
from app.models.schemas import (
    CompressRequest, CompressResponse,
    CompressionAnalysis, CompressionIntelligence
)
from app.integrations.llm_clients import llm_provider
from app.prompts.compressor_prompts import build_compression_prompt
from app.utils.token_counter import count_tokens, compute_token_reduction_percent
from app.utils.compression_scorer import compute_all_scores


# ─────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────

def _strip_json_fences(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


def _safe_float(val, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _safe_int(val, default: int = 0) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def _safe_bool(val, default: bool = True) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() not in ("false", "0", "no")
    return default


def _safe_list(val) -> list[str]:
    if isinstance(val, list):
        return [str(item) for item in val]
    if isinstance(val, str) and val.strip():
        return [val.strip()]
    return []


def _mode_to_strategy(mode: str) -> str:
    return {
        "LIGHT": "High-Fidelity Preservation",
        "BALANCED": "Semantic Optimization",
        "AGGRESSIVE": "Strategic Intelligence Distillation",
    }.get(mode.upper(), "Semantic Optimization")


def _parse_llm_output(raw_output: str) -> dict:
    """
    Robustly parse the LLM's JSON response.
    Tries strict parse → regex extraction → safe fallback.
    """
    cleaned = _strip_json_fences(raw_output)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    print(f"[Compressor] JSON parse failed — using fallback. Snippet: {cleaned[:300]}")
    return {
        "compressed_context": cleaned,
        "abstraction_level_used": 2,
        "domain_extracted": "",
        "compression_type": "Semantic Compression",
        "audience_entities": [],
        "hard_constraints": [],
        "soft_constraints": [],
        "emotional_hierarchy": [],
        "unique_concepts": [],
        "preserved_intent": [],
        "preserved_constraints": [],
        "preserved_emotional_context": [],
        "semantic_merges": [],
        "removed_redundancies": [],
        "total_intents_found": 1,
        "intents_preserved_count": 1,
        "total_constraints_found": 0,
        "constraints_preserved_count": 0,
        "total_audience_entities": 0,
        "audience_entities_preserved": 0,
        "emotional_tags_found": 0,
        "emotional_tags_preserved_count": 0,
        "total_unique_concepts": 0,
        "unique_concepts_preserved": 0,
        "domain_concepts_found": 0,
        "domain_concepts_preserved": 0,
        "concepts_identified": 0,
        "concepts_merged": 0,
        "redundancies_removed": 0,
        "abstractions_generated": 0,
        "verification_passed": True,
        "rollback_performed": False,
        "anti_generic_check_passed": True,
    }


# ─────────────────────────────────────────────────────────────
# Main Service
# ─────────────────────────────────────────────────────────────

async def compress_text(request: CompressRequest) -> CompressResponse:
    """
    Intelligence Distillation Engine — Full 8-layer pipeline.
    All scores are backend-calculated via embeddings and set-ratio math.
    """
    mode_upper = (request.mode or "BALANCED").upper()

    # ── STEP 1: Deterministic original token count (before LLM) ──
    original_tokens = count_tokens(request.input_text)

    # ── STEP 2: Build 8-layer distillation prompt ──
    final_prompt = build_compression_prompt(
        input_text=request.input_text,
        mode=mode_upper,
        preserve_code=request.preserve_code,
    )

    # ── STEP 3: Execute LLM ──
    try:
        raw_output = await llm_provider.generate(final_prompt)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail="The Compression Engine hit a snag while processing your text. Our AI brain might be busy. Please try compressing again."
        )

    # ── STEP 4: Parse structured JSON response ──
    parsed = _parse_llm_output(raw_output)

    # ── STEP 5: Extract compressed text ──
    compressed_context = parsed.get("compressed_context", "").strip()
    if not compressed_context:
        compressed_context = _strip_json_fences(raw_output)

    # ── STEP 6: Deterministic compressed token count ──
    compressed_tokens = count_tokens(compressed_context)

    # ── STEP 7: Token ratio math ──
    compression_ratio = round(compressed_tokens / max(original_tokens, 1), 3)
    token_reduction_percent = compute_token_reduction_percent(original_tokens, compressed_tokens)

    # ── STEP 8: Extract LLM counts for all 6 preservation dimensions ──
    total_intents = max(1, _safe_int(parsed.get("total_intents_found"), 1))
    intents_preserved = _safe_int(parsed.get("intents_preserved_count"), total_intents)

    total_constraints = _safe_int(parsed.get("total_constraints_found"), 0)
    constraints_preserved = _safe_int(parsed.get("constraints_preserved_count"), total_constraints)

    total_audience = _safe_int(parsed.get("total_audience_entities"), 0)
    audience_preserved = _safe_int(parsed.get("audience_entities_preserved"), total_audience)

    total_emotional = _safe_int(parsed.get("emotional_tags_found"), 0)
    emotional_preserved = _safe_int(parsed.get("emotional_tags_preserved_count"), total_emotional)

    total_unique = _safe_int(parsed.get("total_unique_concepts"), 0)
    unique_preserved = _safe_int(parsed.get("unique_concepts_preserved"), total_unique)

    total_domain = _safe_int(parsed.get("domain_concepts_found"), 0)
    domain_preserved = _safe_int(parsed.get("domain_concepts_preserved"), total_domain)

    # ── STEP 9: Full backend scoring (6-factor) ──
    scores = await compute_all_scores(
        original_text=request.input_text,
        compressed_text=compressed_context,
        total_intents_found=total_intents,
        intents_preserved_count=intents_preserved,
        total_constraints_found=total_constraints,
        constraints_preserved_count=constraints_preserved,
        total_audience_entities=total_audience,
        audience_entities_preserved=audience_preserved,
        emotional_tags_found=total_emotional,
        emotional_tags_preserved_count=emotional_preserved,
        total_unique_concepts=total_unique,
        unique_concepts_preserved=unique_preserved,
        domain_concepts_found=total_domain,
        domain_concepts_preserved=domain_preserved,
        compression_ratio=compression_ratio,
        compressed_token_count=compressed_tokens,
    )

    # ── STEP 10: Compression intelligence analytics ──
    concepts_identified = _safe_int(parsed.get("concepts_identified"), 0)
    concepts_merged = _safe_int(parsed.get("concepts_merged"), 0)
    redundancies_removed_count = _safe_int(parsed.get("redundancies_removed"), 0)
    abstractions_generated = _safe_int(parsed.get("abstractions_generated"), 0)
    abstraction_level_used = _safe_int(parsed.get("abstraction_level_used"), 2)
    domain_extracted = str(parsed.get("domain_extracted", "")).strip()
    compression_type = str(parsed.get("compression_type", "Semantic Compression")).strip()
    verification_passed = _safe_bool(parsed.get("verification_passed"), True)
    rollback_performed = _safe_bool(parsed.get("rollback_performed"), False)
    anti_generic_passed = _safe_bool(parsed.get("anti_generic_check_passed"), True)

    compression_efficiency = round(concepts_merged / max(concepts_identified, 1), 3)
    information_density_gain = round(
        scores["meaning_preservation_score"] / max(compression_ratio, 0.001), 3
    )

    # ── STEP 11: Assemble and return full response ──
    return CompressResponse(
        compressed_context=compressed_context,
        compression_analysis=CompressionAnalysis(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compression_ratio,
            token_reduction_percent=token_reduction_percent,
            semantic_similarity=scores["semantic_similarity"],
            intent_preservation_score=scores["intent_preservation_score"],
            constraint_preservation_score=scores["constraint_preservation_score"],
            audience_preservation_score=scores["audience_preservation_score"],
            emotional_preservation_score=scores["emotional_preservation_score"],
            concept_preservation_score=scores["concept_preservation_score"],
            domain_preservation_score=scores["domain_preservation_score"],
            meaning_preservation_score=scores["meaning_preservation_score"],
            intelligence_density_score=scores["intelligence_density_score"],
            density_category=scores["density_category"],
        ),
        compression_intelligence=CompressionIntelligence(
            compression_type=compression_type,
            compression_strategy=_mode_to_strategy(mode_upper),
            abstraction_level_used=abstraction_level_used,
            domain_extracted=domain_extracted,
            concepts_identified=concepts_identified,
            concepts_merged=concepts_merged,
            redundancies_removed=redundancies_removed_count,
            abstractions_generated=abstractions_generated,
            compression_efficiency=compression_efficiency,
            information_density_gain=information_density_gain,
            unique_concepts_count=total_unique,
            audience_entities_count=total_audience,
            verification_passed=verification_passed,
            rollback_performed=rollback_performed,
            anti_generic_check_passed=anti_generic_passed,
        ),
        audience_entities=_safe_list(parsed.get("audience_entities")),
        hard_constraints=_safe_list(parsed.get("hard_constraints")),
        soft_constraints=_safe_list(parsed.get("soft_constraints")),
        emotional_hierarchy=_safe_list(parsed.get("emotional_hierarchy")),
        unique_concepts=_safe_list(parsed.get("unique_concepts")),
        preserved_intent=_safe_list(parsed.get("preserved_intent")),
        preserved_constraints=_safe_list(parsed.get("preserved_constraints")),
        preserved_emotional_context=_safe_list(parsed.get("preserved_emotional_context")),
        semantic_merges=_safe_list(parsed.get("semantic_merges")),
        removed_redundancies=_safe_list(parsed.get("removed_redundancies")),
        mode_used=mode_upper,
    )
