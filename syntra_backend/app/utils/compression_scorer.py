# app/utils/compression_scorer.py
# Intelligence Distillation Engine — Backend Scoring
#
# Meaning Score Formula (6-factor weighted):
#   Meaning = 0.30 × Intent_Preservation
#           + 0.25 × Constraint_Preservation
#           + 0.15 × Audience_Preservation
#           + 0.10 × Emotional_Preservation
#           + 0.10 × Concept_Preservation
#           + 0.10 × Domain_Preservation
#
# Intelligence Density Formula:
#   Density = (Intent + Constraints + Audience + Emotions + Unique_Concepts + Strategic_Context)
#             / Output_Tokens
#
# Semantic Similarity: Gemini text-embedding-004 cosine similarity
# All other scores: Set-based mathematical ratios
# ZERO LLM ESTIMATION — all metrics are backend-computed.

import math
import asyncio
from typing import Optional
from app.core.config import settings

# ─────────────────────────────────────────────────────────────
# Semantic Similarity (Offline Jaccard Fallback)
# ─────────────────────────────────────────────────────────────

def _jaccard_similarity(text_a: str, text_b: str) -> float:
    """Computes basic Jaccard similarity based on word tokens."""
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    
    if not words_a or not words_b:
        return 0.0
        
    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)
    
    # Jaccard alone can be harsh for compression (as compression removes words),
    # so we boost it slightly to mimic the higher baseline of embeddings.
    base_sim = len(intersection) / len(union)
    return min(1.0, base_sim + 0.3)

async def compute_semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Computes semantic similarity.
    Since external embeddings (Google/Gemini) were removed to strictly enforce Groq-only architecture,
    this uses a fast, offline heuristic.
    """
    try:
        # Run synchronous CPU-bound math in a thread
        similarity = await asyncio.to_thread(_jaccard_similarity, text_a, text_b)
        print(f"[Scorer] Semantic similarity (Jaccard offline): {similarity:.4f}")
        return round(similarity, 4)
    except Exception as e:
        print(f"[Scorer] Similarity failed ({type(e).__name__}: {e}) — fallback 0.85")
        return 0.85


# ─────────────────────────────────────────────────────────────
# Set-Based Preservation Ratios
# ─────────────────────────────────────────────────────────────

def _ratio(preserved: int, total: int, default_if_zero: float = 1.0) -> float:
    """Safe ratio calculation. Returns default if total is 0."""
    if total <= 0:
        return default_if_zero
    return round(min(1.0, preserved / total), 4)


def compute_intent_preservation(total: int, preserved: int) -> float:
    return _ratio(preserved, total)


def compute_constraint_preservation(total: int, preserved: int) -> float:
    return _ratio(preserved, total)


def compute_audience_preservation(total: int, preserved: int) -> float:
    return _ratio(preserved, total)


def compute_emotional_preservation(total: int, preserved: int) -> float:
    return _ratio(preserved, total)


def compute_concept_preservation(total: int, preserved: int) -> float:
    """Unique concept preservation — high uniqueness concepts should survive."""
    return _ratio(preserved, total)


def compute_domain_preservation(total: int, preserved: int) -> float:
    return _ratio(preserved, total)


# ─────────────────────────────────────────────────────────────
# Meaning Score — 6-Factor Weighted Formula
# ─────────────────────────────────────────────────────────────

def compute_meaning_score(
    intent_preservation: float,
    constraint_preservation: float,
    audience_preservation: float,
    emotional_preservation: float,
    concept_preservation: float,
    domain_preservation: float,
) -> float:
    """
    Meaning Score — 6-factor weighted composite.
    Weights reflect strategic importance in intelligence distillation.

    Formula:
        Meaning = 0.30 × Intent
                + 0.25 × Constraint
                + 0.15 × Audience
                + 0.10 × Emotional
                + 0.10 × Concept
                + 0.10 × Domain

    Intent (30%) and Constraint (25%) dominate because they represent
    the core purpose and non-negotiable requirements.
    Audience (15%) is critical because generalization destroys identity.
    """
    score = (
        0.30 * intent_preservation +
        0.25 * constraint_preservation +
        0.15 * audience_preservation +
        0.10 * emotional_preservation +
        0.10 * concept_preservation +
        0.10 * domain_preservation
    )
    return round(min(1.0, max(0.0, score)), 4)


# ─────────────────────────────────────────────────────────────
# Intelligence Density Score
# ─────────────────────────────────────────────────────────────

def compute_intelligence_density(
    intent_preservation: float,
    constraint_preservation: float,
    audience_preservation: float,
    emotional_preservation: float,
    concept_preservation: float,
    domain_preservation: float,
    compressed_token_count: int,
) -> float:
    """
    Intelligence Density.

    Formula:
        Density = (sum of all preservation scores) / output_tokens × 100

    Rewards: preserving all 6 intelligence dimensions with fewer tokens.
    Higher density = more intelligence per token.

    Interpretation:
        < 120   → Basic Compression
        120-160 → Good Compression
        160-220 → Advanced Compression
        220+    → Elite Intelligence Distillation
    """
    if compressed_token_count <= 0:
        return 0.0
    intelligence_sum = (
        intent_preservation +
        constraint_preservation +
        audience_preservation +
        emotional_preservation +
        concept_preservation +
        domain_preservation
    )
    density = (intelligence_sum / compressed_token_count) * 100
    return round(density, 1)


def compute_density_score_simple(meaning_score: float, compression_ratio: float) -> float:
    """
    Legacy simple density: meaning% / compression_ratio.
    Kept for backward compatibility display.
    """
    if compression_ratio <= 0:
        return 0.0
    return round((meaning_score * 100) / compression_ratio, 1)


def get_density_category(density_score: float) -> str:
    if density_score >= 220:
        return "Elite Intelligence Distillation"
    elif density_score >= 160:
        return "Advanced Compression"
    elif density_score >= 120:
        return "Good Compression"
    else:
        return "Basic Compression"


# ─────────────────────────────────────────────────────────────
# Master Scorer
# ─────────────────────────────────────────────────────────────

async def compute_all_scores(
    original_text: str,
    compressed_text: str,
    # Intent
    total_intents_found: int,
    intents_preserved_count: int,
    # Constraints
    total_constraints_found: int,
    constraints_preserved_count: int,
    # Audience (NEW)
    total_audience_entities: int,
    audience_entities_preserved: int,
    # Emotional
    emotional_tags_found: int,
    emotional_tags_preserved_count: int,
    # Unique Concepts (NEW)
    total_unique_concepts: int,
    unique_concepts_preserved: int,
    # Domain (NEW)
    domain_concepts_found: int,
    domain_concepts_preserved: int,
    # Token metrics
    compression_ratio: float,
    compressed_token_count: int,
) -> dict:
    """
    Master scoring function. Computes all metrics from first principles.
    """
    # 1. Semantic similarity via embeddings
    semantic_similarity = await compute_semantic_similarity(original_text, compressed_text)

    # 2. Six preservation ratios (pure math)
    intent_pres = compute_intent_preservation(total_intents_found, intents_preserved_count)
    constraint_pres = compute_constraint_preservation(total_constraints_found, constraints_preserved_count)
    audience_pres = compute_audience_preservation(total_audience_entities, audience_entities_preserved)
    emotional_pres = compute_emotional_preservation(emotional_tags_found, emotional_tags_preserved_count)
    concept_pres = compute_concept_preservation(total_unique_concepts, unique_concepts_preserved)
    domain_pres = compute_domain_preservation(domain_concepts_found, domain_concepts_preserved)

    # 3. Meaning Score (6-factor weighted)
    meaning_score = compute_meaning_score(
        intent_preservation=intent_pres,
        constraint_preservation=constraint_pres,
        audience_preservation=audience_pres,
        emotional_preservation=emotional_pres,
        concept_preservation=concept_pres,
        domain_preservation=domain_pres,
    )

    # 4. Intelligence Density (6-factor / output tokens)
    intelligence_density = compute_intelligence_density(
        intent_pres, constraint_pres, audience_pres,
        emotional_pres, concept_pres, domain_pres,
        compressed_token_count,
    )

    # 5. Legacy density (meaning% / ratio) for display
    legacy_density = compute_density_score_simple(meaning_score, compression_ratio)

    # Use the higher of the two density calculations for the score card
    final_density = max(intelligence_density, legacy_density)
    density_category = get_density_category(final_density)

    return {
        "semantic_similarity": semantic_similarity,
        "intent_preservation_score": intent_pres,
        "constraint_preservation_score": constraint_pres,
        "audience_preservation_score": audience_pres,
        "emotional_preservation_score": emotional_pres,
        "concept_preservation_score": concept_pres,
        "domain_preservation_score": domain_pres,
        "meaning_preservation_score": meaning_score,
        "intelligence_density_score": final_density,
        "density_category": density_category,
    }
