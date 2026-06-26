from pydantic import BaseModel, Field

# ==========================================
# Feature: 1-Prompt Enhancement
# ==========================================

class EnhanceRequest(BaseModel):
    # Field(...) allows us to add validation and descriptions for the API docs
    
    prompt:str = Field(...,  min_length=2, description = "The raw prompt to be enhanced")

class PromptDNA(BaseModel):
    intent_clarity: int = Field(description="Score 0-100 for Intent Clarity")
    context_completeness: int = Field(description="Score 0-100 for Context Completeness")
    constraint_coverage: int = Field(description="Score 0-100 for Constraint Coverage")
    reasoning_depth: int = Field(description="Score 0-100 for Reasoning Depth")
    output_structure: int = Field(description="Score 0-100 for Output Structure Quality")
    specificity: int = Field(description="Score 0-100 for Specificity vs Vague Language")
    ambiguity_risk: int = Field(description="Score 0-100 for Ambiguity Risk (Higher = Worse)")

class IntentIntelligence(BaseModel):
    primary_goal: str = Field(description="Primary goal detected from the prompt")
    secondary_goals: list[str] = Field(description="List of secondary goals")
    domains: list[str] = Field(description="Domain stacks detected (e.g. healthcare, fintech, AI)")
    complexity: str = Field(description="Complexity level: simple / moderate / complex / enterprise")
    ambiguity: str = Field(description="Ambiguity level: low / medium / high / critical")
    execution_types: list[str] = Field(description="Execution types: GENERATION, PLANNING, RESEARCH, etc.")
    confidence_scores: dict = Field(description="Confidence scores per execution type")

class EnhanceResponse(BaseModel):
    original_prompt: str
    enhanced_prompt: str
    reasoning: str = Field(description="One sentence explaining the core transformation")
    intent_intelligence: IntentIntelligence = Field(description="Deep intent analysis of the original prompt")
    output_mode: str = Field(description="Output mode selected: BLUEPRINT | BRAINSTORMING | RESEARCH | OPTIMIZATION")
    original_dna: PromptDNA = Field(description="DNA profile of the original prompt")
    enhanced_dna: PromptDNA = Field(description="DNA profile of the enhanced prompt")
    original_score: int = Field(description="Calculated quality score of original prompt")
    enhanced_score: int = Field(description="Calculated quality score of enhanced prompt")
    improvement_score: int = Field(description="Difference between enhanced and original score")
    risk_classification: str = Field(description="Risk level of original prompt")
    missing_information: list[str] = Field(description="List of critical missing information")
    enhancement_strategy_used: str = Field(description="The strategy used to enhance the prompt")
    recommended_routes: list[str] = Field(description="Recommended LLMs or tools for the enhanced prompt")
    improvement_summary: list[str] = Field(description="Summary of improvements applied")
# ==========================================
# Feature: 2-Intent Detection
# ==========================================

class IntentRequest(BaseModel):
    prompt: str = Field(..., min_length=2, description="The raw user prompt for intent detection")

class IntentHierarchy(BaseModel):
    north_star_mission: str = Field(description="Highest-level human purpose")
    primary_intent: str = Field(description="The dominant goal")
    secondary_intents: list[str] = Field(default=[], description="Supporting goals")
    execution_intent: str = Field(description="e.g. Research, Planning, Architecture")
    long_term_vision: str = Field(description="The long-term desired outcome")

class UserMotivation(BaseModel):
    motivation: str = Field(description="e.g. Founder Mindset, Desire for Meaningful Impact")
    reasoning: str = Field(description="Why this was inferred")

class ExecutionIntentClass(BaseModel):
    category: str = Field(description="e.g. Architecture Design, MVP Planning")
    confidence: int = Field(description="Confidence score 0-100")
    reasoning: str = Field(description="Why this execution path is expected")

class DomainIntelligence(BaseModel):
    domain: str = Field(description="e.g. Artificial Intelligence, Healthcare, Education")
    reasoning: str = Field(description="Why this domain applies")

class BusinessIntelligence(BaseModel):
    product_vision: str = Field(default="", description="The overall vision")
    competitive_advantage: str = Field(default="", description="How this wins")
    monetization_opportunities: str = Field(default="", description="How this makes money")
    retention_strategy: str = Field(default="", description="How this keeps users")
    growth_strategy: str = Field(default="", description="How this acquires users")
    market_positioning: str = Field(default="", description="Where this fits in the market")

class ProductIntelligence(BaseModel):
    mvp_scope: str = Field(default="", description="What belongs in the MVP")
    core_features: list[str] = Field(default=[], description="Must-have features")
    future_features: list[str] = Field(default=[], description="Later features")
    technical_priorities: list[str] = Field(default=[], description="Tech priorities")
    user_value_proposition: str = Field(default="", description="Why users will care")

class UserOutcomeIntelligence(BaseModel):
    current_user_pain: str = Field(default="", description="Current state of user")
    desired_transformation: str = Field(default="", description="Desired state of user")
    expected_end_state: str = Field(default="", description="The final outcome")
    success_definition: str = Field(default="", description="How success is measured")

class ConflictDetection(BaseModel):
    conflict_type: str = Field(description="e.g. Enterprise Scale vs Startup Budget")
    explanation: str = Field(description="Why these contradict")

class MissingInformation(BaseModel):
    missing_category: str = Field(description="e.g. Budget, Target Audience")
    impact: str = Field(description="Why this information is needed")

class AdvancedEmotionalIntelligence(BaseModel):
    surface_emotion: str = Field(default="", description="Explicit emotion detected")
    underlying_psychological_need: str = Field(default="", description="Implicit need")
    desired_emotional_outcome: str = Field(default="", description="What they want to feel")
    psychological_drivers: list[str] = Field(default=[], description="Core drivers")

class ComplexityAnalysis(BaseModel):
    level: str = Field(description="Simple | Moderate | Advanced | Enterprise | Critical")
    reasoning: list[str] = Field(default=[], description="Why this complexity level")

class IntentResponse(BaseModel):
    original_prompt: str
    intent_hierarchy: IntentHierarchy
    user_motivations: list[UserMotivation] = Field(default=[], description="Inferred motivations")
    execution_classification: ExecutionIntentClass
    domain_intelligence: list[DomainIntelligence] = Field(default=[], description="Inferred domains")
    business_intelligence: BusinessIntelligence | None = Field(default=None, description="Only if applicable")
    product_intelligence: ProductIntelligence | None = Field(default=None, description="Only if applicable")
    user_outcome_intelligence: UserOutcomeIntelligence | None = Field(default=None, description="Only if applicable")
    hidden_conflicts: list[ConflictDetection] = Field(default=[], description="Detected contradictions")
    missing_information: list[MissingInformation] = Field(default=[], description="Identified missing pieces")
    emotional_intelligence: AdvancedEmotionalIntelligence | None = Field(default=None, description="Psychological profile")
    strategic_priority_ranking: dict[str, int] = Field(default={}, description="Dict mapping concepts to 0-100 scores")
    complexity_analysis: ComplexityAnalysis

# ==========================================
# Feature: 3-Routing & Execution System
# ==========================================

class RoutingRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length = 2,
        description = "The raw developer propt to be classified and executed."
    )

    code_context: str | None = Field(
        default = None,
        description = "Optional block of source code to be analuzed or referenced"
    )

    language: str | None = Field(
        default = None,
        description = "Optional target programming language (e.g., 'python', 'typescript"
    )

class AgentAssignment(BaseModel):
    agent_name: str = Field(description="Name of the selected agent")
    reasoning: str = Field(description="Why this agent was selected")

class ConfidenceScoring(BaseModel):
    intent_confidences: dict[str, int] = Field(description="Confidence percentage for each detected intent")
    overall_confidence: int = Field(description="Overall routing confidence percentage")

class ClarificationStrategy(BaseModel):
    missing_information: list[str] = Field(default=[], description="Information genuinely required before execution")
    clarification_question: str | None = Field(default=None, description="The single highest-impact question")

class ExecutionReadiness(BaseModel):
    status: str = Field(description="'Ready to Execute' or 'Needs Clarification'")
    reasoning: str = Field(description="Why this status was assigned")

class OrchestrationMetadata(BaseModel):
    estimated_steps: int = Field(description="Estimated number of steps in the pipeline")
    estimated_context_size: str = Field(description="Small, Medium, or Large")

class OrchestrationResponse(BaseModel):
    primary_intent: str
    secondary_intents: list[str] = Field(default=[])
    primary_agent: AgentAssignment
    supporting_agents: list[AgentAssignment] = Field(default=[])
    execution_pipeline: list[str] = Field(description="Ordered list of execution steps")
    complexity: ComplexityAnalysis
    confidence_scoring: ConfidenceScoring
    clarification_strategy: ClarificationStrategy
    execution_readiness: ExecutionReadiness
    orchestration_metadata: OrchestrationMetadata

class RoutingResponse(BaseModel):
    orchestration: OrchestrationResponse # Structured execution pipeline
    execution_result: str | None = None  # Result if executed

# ==========================================
# 4. Compressor Engine Schemas
# ==========================================

class CompressRequest(BaseModel):
    input_text: str = Field(..., min_length=10, description="The raw, noisy text to compress")
    preserve_code: bool = Field(default=True, description="If True, code blocks and error traces will not be summarized")
    mode: str = Field(default="BALANCED", description="Compression mode: LIGHT | BALANCED | AGGRESSIVE")


class CompressionAnalysis(BaseModel):
    """All metrics are backend-calculated. Zero LLM estimation."""

    # ── Token Metrics (tiktoken BPE — deterministic) ──
    original_tokens: int = Field(..., description="Deterministic BPE token count of the original input")
    compressed_tokens: int = Field(..., description="Deterministic BPE token count of the compressed output")
    compression_ratio: float = Field(..., description="compressed_tokens / original_tokens (lower is better)")
    token_reduction_percent: float = Field(..., description="Percentage of tokens eliminated")

    # ── Semantic Similarity (Gemini embeddings cosine distance) ──
    semantic_similarity: float = Field(..., description="Cosine similarity of embeddings: original vs compressed (0.0-1.0)")

    # ── 6-Factor Preservation Scores (set-based mathematical ratios) ──
    intent_preservation_score: float = Field(..., description="preserved_intents / total_intents (0.0-1.0) — weight: 30%")
    constraint_preservation_score: float = Field(..., description="preserved_constraints / total_constraints (0.0-1.0) — weight: 25%")
    audience_preservation_score: float = Field(..., description="preserved_audience_entities / total_audience_entities (0.0-1.0) — weight: 15%")
    emotional_preservation_score: float = Field(..., description="preserved_emotional_tags / total_emotional_tags (0.0-1.0) — weight: 10%")
    concept_preservation_score: float = Field(..., description="preserved_unique_concepts / total_unique_concepts (0.0-1.0) — weight: 10%")
    domain_preservation_score: float = Field(..., description="preserved_domain_concepts / total_domain_concepts (0.0-1.0) — weight: 10%")

    # ── Composite Meaning Score (6-factor weighted formula) ──
    meaning_preservation_score: float = Field(
        ...,
        description=(
            "Meaning = 0.30×Intent + 0.25×Constraint + 0.15×Audience "
            "+ 0.10×Emotional + 0.10×Concept + 0.10×Domain"
        )
    )

    # ── Intelligence Density ──
    intelligence_density_score: float = Field(
        ...,
        description="Density = (sum of 6 preservation scores / output_tokens) × 100. Higher = more intelligence per token."
    )
    density_category: str = Field(
        ...,
        description="Basic | Good | Advanced | Elite Intelligence Distillation"
    )


class CompressionIntelligence(BaseModel):
    """Analytics about the compression operation and quality verification."""

    # ── Operation Metadata ──
    compression_type: str = Field(
        default="Semantic Compression",
        description="Redundancy Removal | Semantic Merge | Concept Distillation | Strategic Abstraction | Strategic Distillation"
    )
    compression_strategy: str = Field(
        default="Semantic Optimization",
        description="High-Fidelity Preservation | Semantic Optimization | Strategic Intelligence Distillation"
    )
    abstraction_level_used: int = Field(
        default=2,
        description="Final abstraction level applied: 1=Redundancy, 2=SemanticMerge, 3=Distillation, 4=Strategic"
    )
    domain_extracted: str = Field(default="", description="Primary domain detected (e.g. EdTech / behavioral psychology)")

    # ── Concept Analytics ──
    concepts_identified: int = Field(default=0, description="Total distinct concepts before merging")
    concepts_merged: int = Field(default=0, description="Concepts combined via abstraction")
    redundancies_removed: int = Field(default=0, description="Redundant phrases eliminated")
    abstractions_generated: int = Field(default=0, description="New abstraction phrases created")

    # ── Efficiency Metrics ──
    compression_efficiency: float = Field(
        default=0.0,
        description="concepts_merged / max(concepts_identified, 1)"
    )
    information_density_gain: float = Field(
        default=0.0,
        description="meaning_score / compression_ratio"
    )

    # ── Uniqueness & Identity ──
    unique_concepts_count: int = Field(default=0, description="Number of high-uniqueness concepts detected")
    audience_entities_count: int = Field(default=0, description="Number of specific audience identity entities detected")

    # ── Verification Flags ──
    verification_passed: bool = Field(default=True, description="Whether semantic verification thresholds were met")
    rollback_performed: bool = Field(default=False, description="Whether a rollback to lower abstraction level was needed")
    anti_generic_check_passed: bool = Field(default=True, description="Whether the anti-generic guardrail was satisfied")


class CompressResponse(BaseModel):
    # ── Primary Output ──
    compressed_context: str = Field(..., description="The final distilled output — dense prose, never bullets")

    # ── Backend Metrics ──
    compression_analysis: CompressionAnalysis = Field(..., description="All backend-calculated metrics, zero LLM estimates")
    compression_intelligence: CompressionIntelligence = Field(..., description="Analytics, verification, and quality flags")

    # ── Extracted Semantic Layers ──
    audience_entities: list[str] = Field(default=[], description="Specific audience identities extracted (never generalized)")
    hard_constraints: list[str] = Field(default=[], description="Non-negotiable constraints classified as HARD")
    soft_constraints: list[str] = Field(default=[], description="Flexible constraints classified as SOFT/PREFERENCE")
    emotional_hierarchy: list[str] = Field(default=[], description="Emotional signals with hierarchy level (psychological safety → motivation → empowerment)")
    unique_concepts: list[str] = Field(default=[], description="High-uniqueness concepts with scores (concept: uniqueness)")

    # ── Preserved Intelligence ──
    preserved_intent: list[str] = Field(default=[], description="Core objectives confirmed as preserved")
    preserved_constraints: list[str] = Field(default=[], description="Hard constraints confirmed as preserved")
    preserved_emotional_context: list[str] = Field(default=[], description="Emotional signals confirmed as preserved")

    # ── Compression Operations ──
    semantic_merges: list[str] = Field(default=[], description="Concept merges: 'A + B + C → abstraction'")
    removed_redundancies: list[str] = Field(default=[], description="Redundant phrases eliminated with reason")

    mode_used: str = Field(default="BALANCED", description="The compression mode applied")
