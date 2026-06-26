import streamlit as st
import json
import os
import re
import httpx

st.set_page_config(page_title="Syntra AI", page_icon="🚀", layout="wide")

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp { background-color: #0A0806; color: #F2ECE2; font-family: 'Inter', sans-serif !important; }
    p, span, div, label { font-family: 'Inter', sans-serif; line-height: 1.6; }
    .stTextArea textarea {
        background: rgba(15, 13, 10, 0.4) !important; backdrop-filter: blur(12px);
        color: #F2ECE2 !important; border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        font-family: 'Courier New', Courier, monospace; transition: all 0.3s ease;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }
    .stTextArea textarea:focus {
        border-color: #d946ef !important;
        box-shadow: 0 0 20px rgba(217, 70, 239, 0.4), inset 0 0 10px rgba(0,0,0,0.5) !important;
    }
    pre, code { white-space: pre-wrap !important; word-wrap: break-word !important; }
    .stButton > button {
        background: linear-gradient(45deg, #FF512F, #DD2476, #FF512F);
        background-size: 200% auto; color: white; border: none; border-radius: 12px;
        font-weight: 800; letter-spacing: 1px; text-transform: uppercase;
        transition: 0.5s; box-shadow: 0 0 15px rgba(221, 36, 118, 0.4);
    }
    .stButton > button:hover { background-position: right center; box-shadow: 0 0 25px rgba(221, 36, 118, 0.8); transform: translateY(-2px); }
    [data-testid="stSidebar"] { background-color: #0C0A08 !important; border-right: 1px solid rgba(255, 255, 255, 0.05); }
    [data-testid="stMetricValue"] { color: transparent; background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%); -webkit-background-clip: text; font-weight: 900; }
    [data-testid="stMetricDelta"] { color: #92FE9D; }
    .telemetry-dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0 25px; }
    .telemetry-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 20px; transition: all 0.3s ease; }
    .telemetry-card:hover { transform: translateY(-3px); border-color: rgba(217, 70, 239, 0.4); box-shadow: 0 8px 25px rgba(217, 70, 239, 0.15); }
    .telemetry-label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 10px; font-weight: 600; }
    .telemetry-value { font-size: 1.5rem; font-weight: 900; background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%); -webkit-background-clip: text; color: transparent; }
    .telemetry-delta { font-size: 1rem; color: #22c55e; -webkit-text-fill-color: #22c55e; margin-left: 10px; }
    h1 { background: linear-gradient(90deg, #f87171, #f472b6, #c084fc); -webkit-background-clip: text; color: transparent !important; font-weight: 900 !important; letter-spacing: -1px; }
    h2, h3 { color: #E2E8F0 !important; }
    [data-testid="stSidebar"] .stRadio > div { gap: 0.7rem; }
    [data-testid="stSidebar"] .stRadio label { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 14px 16px; cursor: pointer; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); display: flex; align-items: center; }
    [data-testid="stSidebar"] .stRadio label:hover { background: linear-gradient(90deg, rgba(217,70,239,0.1) 0%, rgba(255,255,255,0.02) 100%); transform: translateX(6px); border-color: rgba(217,70,239,0.5); border-left: 4px solid #d946ef; }
    [data-testid="stSidebar"] .stRadio label p { font-weight: 600 !important; color: #E2E8F0 !important; font-size: 0.95rem; }
    [data-testid="stSidebar"] .stRadio label > div:first-child { display: none !important; }
    [data-testid="stSidebar"] .stRadio > label { display: none !important; }
    [data-testid="stSidebar"] .stRadio label > div:nth-child(2) { width: 100%; text-align: center; margin-left: 0 !important; }
    .sidebar-logo { font-size: 2.2rem !important; font-weight: 900 !important; background: linear-gradient(to right, #f97316, #d946ef, #3b82f6); background-size: 200% auto; -webkit-background-clip: text; color: transparent; text-align: center; letter-spacing: 1px; margin-bottom: 0px !important; animation: shine 3s linear infinite; }
    .sidebar-subtitle { text-align: center; color: #64748b; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 4px; margin-top: -10px; margin-bottom: 30px !important; }
    @keyframes shine { to { background-position: 200% center; } }
</style>
""", unsafe_allow_html=True)

# ─── Groq LLM Engine ──────────────────────────────────────────────────────────
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"

def call_llm(prompt: str) -> tuple[str, str]:
    """Calls Groq and returns (response_text, 'Groq')."""
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Add it in Hugging Face Space Settings → Variables and Secrets."
        )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    r = httpx.post(GROQ_API_URL, headers=headers, json=payload, timeout=60.0)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"], "Groq"

def parse_json_response(raw: str) -> dict:
    """Strips markdown fences and parses JSON."""
    clean = raw.strip()
    clean = re.sub(r'^```json\s*', '', clean)
    clean = re.sub(r'^```\s*', '', clean)
    clean = re.sub(r'\s*```$', '', clean)
    return json.loads(clean.strip())

# ─── Prompts (embedded directly) ──────────────────────────────────────────────
ENHANCER_SYSTEM_PROMPT = """
You are Syntra's Enhancement Intelligence Engine — an AI Intent Intelligence System, not a prompt rewriting tool.

Your mission: Transform a raw human prompt into a production-ready, fully executable AI prompt.
The enhanced_prompt must be immediately usable inside ChatGPT, Claude, Gemini, or Cursor without any modification.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STAGE 1 — INTENT INTELLIGENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Detect: Primary Goal, Secondary Goals, Domain Stack, Complexity Level, Ambiguity Level,
Execution Types (GENERATION|EXPLANATION|ARCHITECTURE|PLANNING|RESEARCH|OPTIMIZATION|DEBUGGING|BRAINSTORMING|EXECUTION|IDEATION),
Confidence Scores (0-100 per execution type).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STAGE 2 — OUTPUT MODE SELECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODE A — BLUEPRINT (ARCHITECTURE/PLANNING/EXECUTION detected) → strict multi-phase XML document.
MODE B — BRAINSTORMING (BRAINSTORMING/IDEATION/GENERATION) → lateral thinking prompt.
MODE C — RESEARCH (RESEARCH/EXPLANATION) → depth, evidence, sourcing prompt.
MODE D — OPTIMIZATION (OPTIMIZATION/DEBUGGING) → iterative diagnosis prompt.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STAGE 3 — PROMPT DNA ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score ORIGINAL prompt (0-100 each): intent_clarity, context_completeness, constraint_coverage,
reasoning_depth, specificity, output_structure, ambiguity_risk (higher = worse).
Then score ENHANCED prompt on the same dimensions.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STAGE 4 — MISSING INFORMATION & FALLBACK INJECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Identify missing variables. Inject fallback directives into the enhanced_prompt for each.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
User Input: {raw_prompt}

Return ONLY a valid JSON object. No markdown. No extra text.
{
  "enhanced_prompt": "...",
  "reasoning": "One sentence explaining the core transformation applied.",
  "intent_intelligence": {
    "primary_goal": "",
    "secondary_goals": [],
    "domains": [],
    "complexity": "",
    "ambiguity": "",
    "execution_types": [],
    "confidence_scores": {}
  },
  "output_mode": "BLUEPRINT",
  "original_dna": {"intent_clarity": 0, "context_completeness": 0, "constraint_coverage": 0, "reasoning_depth": 0, "output_structure": 0, "specificity": 0, "ambiguity_risk": 0},
  "enhanced_dna": {"intent_clarity": 0, "context_completeness": 0, "constraint_coverage": 0, "reasoning_depth": 0, "output_structure": 0, "specificity": 0, "ambiguity_risk": 0},
  "missing_information": [],
  "enhancement_strategy_used": "",
  "recommended_routes": [],
  "improvement_summary": []
}
"""

INTENT_SYSTEM_PROMPT = """
You are Syntra's Intent Intelligence Engine. Analyze the user's prompt deeply.
Extract: primary intent, secondary intents, north star mission, long-term vision,
execution classification, business intelligence, product intelligence, user motivations,
user outcome intelligence, hidden conflicts, missing information, strategic priority ranking,
complexity analysis, domain intelligence.

User Input: {raw_prompt}

Return ONLY valid JSON matching this structure (no markdown):
{
  "intent_hierarchy": {"primary_intent": "", "north_star_mission": "", "long_term_vision": ""},
  "execution_classification": {"category": "", "reasoning": ""},
  "business_intelligence": {"product_vision": "", "competitive_advantage": "", "monetization_opportunities": ""},
  "product_intelligence": {"mvp_scope": "", "user_value_proposition": "", "core_features": []},
  "user_motivations": [{"motivation": "", "reasoning": ""}],
  "user_outcome_intelligence": {"current_user_pain": "", "desired_transformation": ""},
  "hidden_conflicts": [{"conflict_type": "", "explanation": ""}],
  "missing_information": [{"missing_category": "", "impact": ""}],
  "strategic_priority_ranking": {},
  "complexity_analysis": {"level": "", "reasoning": ""},
  "domain_intelligence": [{"domain": "", "relevance": ""}]
}
"""

ORCHESTRATOR_PROMPT = """
You are Syntra's Intelligent Routing Orchestrator. Analyze the user's request and select the optimal team of specialized agents.

Available Agents: Architecture Design, MVP Planning, Business Strategist, Pricing Strategy, Technical Roadmap,
Debugging Specialist, Optimization Engineer, Refactoring Architect, Code Generator, Explanation Agent, Product Planner, General Assistant.

User Input: {raw_prompt}
Code Context: {code_context}

Return ONLY valid JSON (no markdown):
{
  "primary_intent": "",
  "secondary_intents": [],
  "primary_agent": {"agent_name": "", "reasoning": ""},
  "supporting_agents": [{"agent_name": "", "reasoning": ""}],
  "execution_pipeline": [],
  "complexity": {"level": "", "reasoning": ""},
  "confidence_scoring": {"intent_confidences": {}, "overall_confidence": 0},
  "clarification_strategy": {"missing_information": [], "clarification_question": null},
  "execution_readiness": {"status": "Ready to Execute", "reasoning": ""}
}
"""

def build_compression_prompt(input_text: str, mode: str) -> str:
    mode_instructions = {
        "LIGHT": "Apply LIGHT compression: remove only redundant filler words. Preserve all specifics, examples, and emotional nuance. Target 5-20% token reduction.",
        "BALANCED": "Apply BALANCED compression: merge overlapping concepts, preserve audience identity and hard constraints. Target 20-40% token reduction.",
        "AGGRESSIVE": "Apply AGGRESSIVE compression: abstract clusters into higher-order concepts. Maximize intelligence density. Target 45-60% token reduction. Output must be executive prose, not bullet points."
    }
    instruction = mode_instructions.get(mode.upper(), mode_instructions["BALANCED"])
    return f"""You are Syntra's Intelligence Distillation Engine. Compress the following text while preserving maximum meaning.

{instruction}

Return ONLY valid JSON (no markdown):
{{
  "compressed_context": "<distilled output>",
  "compression_analysis": {{
    "original_tokens": <int>,
    "compressed_tokens": <int>,
    "token_reduction_percent": <int>,
    "meaning_preservation_score": <float 0.0-1.0>
  }}
}}

INPUT TO COMPRESS:
{input_text}"""

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sidebar-logo'>SYNTRA</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-subtitle'>Distillation Engine</div>", unsafe_allow_html=True)
    st.markdown("---")
    active_tool = st.radio(
        "",
        options=["Prompt Refinement", "Intent Intelligence", "Context Compressor", "Intelligent Router"],
        label_visibility="hidden"
    )
    st.markdown("---")

# ─── Helper: calc DNA score ────────────────────────────────────────────────────
def calc_score(dna: dict) -> int:
    s = (dna.get("intent_clarity", 0) * 0.20 +
         dna.get("context_completeness", 0) * 0.20 +
         dna.get("constraint_coverage", 0) * 0.15 +
         dna.get("reasoning_depth", 0) * 0.15 +
         dna.get("output_structure", 0) * 0.15 +
         dna.get("specificity", 0) * 0.10 +
         (100 - dna.get("ambiguity_risk", 100)) * 0.05)
    return min(100, max(0, int(round(s))))

# ─── Prompt Refinement ─────────────────────────────────────────────────────────
if active_tool == "Prompt Refinement":
    st.title("🎯 Prompt Refinement")
    st.markdown("Transforms vague inputs into structured, token-dense prompts.")
    raw_prompt = st.text_area("Raw Thought Input", height=150, placeholder="Paste your messy, vague idea here...")
    if st.button("Enhance Prompt", use_container_width=True):
        if not raw_prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("📡 Orchestrating..."):
                try:
                    full_prompt = ENHANCER_SYSTEM_PROMPT.replace("{raw_prompt}", raw_prompt)
                    raw = call_gemini(full_prompt)
                    data = parse_json_response(raw)

                    st.toast('✨ Neural Network Enhancement Complete', icon='🔥')
                    st.success("✅ Enhancement Complete!")
                    st.balloons()

                    st.markdown("### ✨ Enhanced Prompt")
                    st.text_area("Enhanced Prompt Output", value=data.get("enhanced_prompt", ""), height=350, label_visibility="collapsed")

                    col_left, col_right = st.columns(2)
                    with col_left:
                        st.markdown("#### 🧠 AI Reasoning")
                        st.info(data.get("reasoning", "No reasoning provided."))
                    with col_right:
                        st.markdown("#### ⚠️ Critical Gaps Found")
                        missing = data.get("missing_information", [])
                        if missing:
                            for m in missing:
                                st.error(f"• {m}")
                        else:
                            st.success("No missing information! Your prompt is perfectly complete.")

                    st.markdown("---")
                    st.markdown("#### 🧬 Telemetry & DNA Metrics")
                    orig_dna = data.get("original_dna", {})
                    enh_dna = data.get("enhanced_dna", {})
                    orig_score = calc_score(orig_dna)
                    enh_score = calc_score(enh_dna)
                    diff = enh_score - orig_score
                    risk = data.get("risk_classification", data.get("output_mode", "Unknown"))
                    mode_val = data.get("output_mode", "Unknown")

                    st.markdown(f"""
                    <div class="telemetry-dashboard">
                        <div class="telemetry-card"><div class="telemetry-label">Original DNA</div><div class="telemetry-value">{orig_score}</div></div>
                        <div class="telemetry-card"><div class="telemetry-label">Enhanced DNA</div><div class="telemetry-value">{enh_score} <span class="telemetry-delta">↑ +{diff}</span></div></div>
                        <div class="telemetry-card"><div class="telemetry-label">Output Mode</div><div class="telemetry-value" style="font-size:1.1rem">{mode_val}</div></div>
                        <div class="telemetry-card"><div class="telemetry-label">Strategy</div><div class="telemetry-value" style="font-size:0.9rem">{data.get('enhancement_strategy_used','—')}</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("⚙️ View Raw Engine Metadata (Developer)"):
                        st.json(data.get("intent_intelligence", {}))
                except ValueError as e:
                    st.error(f"⚠️ {e}")
                except Exception as e:
                    st.error(f"⚠️ Enhancement failed: {e}")

# ─── Intent Intelligence ───────────────────────────────────────────────────────
elif active_tool == "Intent Intelligence":
    st.title("🧠 Intent Intelligence")
    st.markdown("Extracts cognitive metadata, goals, and hidden objectives from human thought.")
    raw_prompt = st.text_area("Input Prompt", height=150, placeholder="Describe your intent or requirements...")
    if st.button("Analyze Intent", use_container_width=True):
        if not raw_prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("🧠 Analyzing Cognition..."):
                try:
                    full_prompt = INTENT_SYSTEM_PROMPT.replace("{raw_prompt}", raw_prompt)
                    raw = call_gemini(full_prompt)
                    data = parse_json_response(raw)
                    st.toast('🧠 Cognitive Extraction Finished', icon='👁️')
                    st.success("✅ Analysis Complete!")
                    st.markdown("### 🌟 North Star Mission")
                    st.info(data.get("intent_hierarchy", {}).get("north_star_mission", "Unknown"))
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### 🎯 Intent Hierarchy")
                        st.markdown(f"**Primary Intent:** {data.get('intent_hierarchy', {}).get('primary_intent', 'Unknown')}")
                        st.markdown(f"**Long-Term Vision:** {data.get('intent_hierarchy', {}).get('long_term_vision', 'Unknown')}")
                    with col2:
                        st.markdown("#### 🚀 Execution Intent")
                        st.markdown(f"**{data.get('execution_classification', {}).get('category', 'Unknown')}**")
                        st.markdown(f"*{data.get('execution_classification', {}).get('reasoning', '')}*")
                    st.markdown("---")
                    st.markdown("### 🧠 User Psychology & Outcomes")
                    for m in data.get("user_motivations", []):
                        st.markdown(f"- **{m.get('motivation')}**: {m.get('reasoning')}")
                    out = data.get("user_outcome_intelligence")
                    if out:
                        st.markdown(f"**Current Pain:** {out.get('current_user_pain')}")
                        st.markdown(f"**Desired Transformation:** {out.get('desired_transformation')}")
                    st.markdown("---")
                    st.markdown("### ⚠️ Critical Gaps & Conflicts")
                    for c in data.get("hidden_conflicts", []):
                        st.error(f"**Conflict ({c.get('conflict_type')}):** {c.get('explanation')}")
                    for m in data.get("missing_information", []):
                        st.warning(f"**Missing {m.get('missing_category')}:** {m.get('impact')}")
                    with st.expander("⚙️ View Raw Engine Metadata (Developer)"):
                        st.json(data)
                except ValueError as e:
                    st.error(f"⚠️ {e}")
                except Exception as e:
                    st.error(f"⚠️ Analysis failed: {e}")

# ─── Context Compressor ────────────────────────────────────────────────────────
elif active_tool == "Context Compressor":
    st.title("🗜️ Context Compressor")
    st.markdown("Semantically compresses noisy text while preserving critical meaning.")
    raw_prompt = st.text_area("Verbose Input", height=150, placeholder="Paste verbose logs, articles, or noisy text here...")
    mode = st.radio("Compression Mode", ["LIGHT", "BALANCED", "AGGRESSIVE"], horizontal=True, index=1)
    if st.button("Compress Context", use_container_width=True):
        if not raw_prompt.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("🗜️ Compressing semantics..."):
                try:
                    full_prompt = build_compression_prompt(raw_prompt, mode)
                    raw = call_gemini(full_prompt)
                    data = parse_json_response(raw)
                    analysis = data.get("compression_analysis", {})
                    reduction = analysis.get("token_reduction_percent", 0)
                    st.toast(f'🗜️ Shrinkage Achieved: {reduction}%', icon='📉')
                    st.success(f"✅ Compressed by {reduction}%!")
                    orig_len = analysis.get("original_tokens", 0)
                    comp_len = analysis.get("compressed_tokens", 0)
                    meaning = round(analysis.get("meaning_preservation_score", 0) * 100, 2)
                    st.markdown(f"""
                    <div class="telemetry-dashboard">
                        <div class="telemetry-card"><div class="telemetry-label">Original Size</div><div class="telemetry-value">{orig_len} <span style="font-size:0.9rem;color:#94a3b8;-webkit-text-fill-color:#94a3b8">tokens</span></div></div>
                        <div class="telemetry-card"><div class="telemetry-label">Compressed Size</div><div class="telemetry-value">{comp_len} <span style="color:#ef4444;-webkit-text-fill-color:#ef4444;margin-left:8px">↓ -{reduction}%</span></div></div>
                        <div class="telemetry-card"><div class="telemetry-label">Meaning Preserved</div><div class="telemetry-value">{meaning}%</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("### 📦 Condensed Output")
                    st.text_area("Condensed Output", value=data.get("compressed_context", ""), height=300, label_visibility="collapsed")
                except ValueError as e:
                    st.error(f"⚠️ {e}")
                except Exception as e:
                    st.error(f"⚠️ Compression failed: {e}")

# ─── Intelligent Router ────────────────────────────────────────────────────────
elif active_tool == "Intelligent Router":
    st.title("🚦 Intelligent Router (Orchestrator)")
    st.markdown("Stop guessing which AI agent you need. Describe what you want to build — Syntra assembles the optimal execution pipeline.")
    raw_prompt = st.text_area("User Query", height=100, placeholder="Ask anything. Syntra will route it...")
    code_ctx = st.text_area("Optional Code Context", height=100, placeholder="Paste any relevant code here...")
    if st.button("Execute Request", use_container_width=True):
        if not raw_prompt.strip():
            st.warning("Please enter a query.")
        else:
            with st.spinner("🚦 Routing to optimal agent..."):
                try:
                    full_prompt = ORCHESTRATOR_PROMPT.replace("{raw_prompt}", raw_prompt).replace("{code_context}", code_ctx or "None")
                    raw = call_gemini(full_prompt)
                    orch = parse_json_response(raw)
                    st.toast(f'🚦 Pipeline Ready: {orch.get("execution_readiness", {}).get("status", "Unknown")}', icon='🤖')
                    status = orch.get("execution_readiness", {}).get("status", "")
                    if "Ready" in status:
                        st.success(f"### ✅ {status}")
                    else:
                        st.warning(f"### ⚠️ {status}")
                    st.write(orch.get("execution_readiness", {}).get("reasoning", ""))
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### 🎯 Primary Agent")
                        pri = orch.get("primary_agent", {})
                        st.markdown(f"**<span style='color:#3b82f6'>{pri.get('agent_name','Unknown')}</span>**", unsafe_allow_html=True)
                        st.caption(pri.get("reasoning", ""))
                    with col2:
                        st.markdown("#### 🤝 Supporting Agents")
                        for sa in orch.get("supporting_agents", []):
                            st.markdown(f"- **{sa.get('agent_name')}**")
                            st.caption(sa.get("reasoning", ""))
                    st.divider()
                    st.markdown("#### ⚙️ Execution Pipeline")
                    pipeline = orch.get("execution_pipeline", [])
                    if pipeline:
                        pipeline_html = " <br>⬇<br> ".join([f"<div style='background:#1e293b;padding:10px;border-radius:5px;text-align:center;border:1px solid #334155'><b>{step}</b></div>" for step in pipeline])
                        st.markdown(pipeline_html, unsafe_allow_html=True)
                    st.markdown("#### 📊 Detected Intents & Confidence")
                    st.write(f"**Primary Intent:** {orch.get('primary_intent','')}")
                    st.write(f"**Secondary Intents:** {', '.join(orch.get('secondary_intents',[]))}")
                    for intent, conf in orch.get("confidence_scoring", {}).get("intent_confidences", {}).items():
                        st.progress(conf / 100.0, text=f"{intent} ({conf}%)")
                    st.metric("Overall Routing Confidence", f"{orch.get('confidence_scoring', {}).get('overall_confidence', 0)}%")
                    with st.expander("⚙️ View Orchestration Metadata (Developer)"):
                        st.json(orch)
                except ValueError as e:
                    st.error(f"⚠️ {e}")
                except Exception as e:
                    st.error(f"⚠️ Routing failed: {e}")
