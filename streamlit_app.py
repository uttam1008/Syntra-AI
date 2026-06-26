import sys
import os
import asyncio
import streamlit as st

# ── Make backend importable as a Python package ────────────────────────────────
# Works both locally (syntra_backend/) and in Docker (/app/backend/)
_here = os.path.dirname(os.path.abspath(__file__))
for _candidate in [
    os.path.join(_here, "backend"),          # Docker path: /app/backend
    os.path.join(_here, "syntra_backend"),   # Local path
]:
    if os.path.isdir(_candidate) and _candidate not in sys.path:
        sys.path.insert(0, _candidate)

# ── Import original backend services (all prompts intact) ─────────────────────
from app.services.enhancer import generate_enhanced_prompt
from app.services.intent_detection_service import intent_detect_service
from app.services.compressor import run_compression_pipeline
from app.services.routing_service import routing_service
from app.models.schemas import CompressRequest

# ── Async runner ───────────────────────────────────────────────────────────────
def run(coro):
    """Run an async coroutine from synchronous Streamlit context."""
    return asyncio.run(coro)

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Syntra AI", page_icon="🚀", layout="wide")

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp { background-color: #0A0806; color: #F2ECE2; font-family: 'Inter', sans-serif !important; }
    p, span, div, label { font-family: 'Inter', sans-serif; line-height: 1.6; }

    .stTextArea textarea {
        background: rgba(15, 13, 10, 0.4) !important;
        backdrop-filter: blur(12px);
        color: #F2ECE2 !important;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        font-family: 'Courier New', Courier, monospace;
        transition: all 0.3s ease;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }
    .stTextArea textarea:focus {
        border-color: #d946ef !important;
        box-shadow: 0 0 20px rgba(217, 70, 239, 0.4), inset 0 0 10px rgba(0,0,0,0.5) !important;
    }

    pre, code { white-space: pre-wrap !important; word-wrap: break-word !important; }

    .stButton > button {
        background: linear-gradient(45deg, #FF512F, #DD2476, #FF512F);
        background-size: 200% auto;
        color: white; border: none; border-radius: 12px;
        font-weight: 800; letter-spacing: 1px; text-transform: uppercase;
        transition: 0.5s; box-shadow: 0 0 15px rgba(221, 36, 118, 0.4);
    }
    .stButton > button:hover {
        background-position: right center;
        box-shadow: 0 0 25px rgba(221, 36, 118, 0.8);
        transform: translateY(-2px);
    }

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

# ─── Sidebar Navigation ────────────────────────────────────────────────────────
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

# ─── DNA Score Helper ──────────────────────────────────────────────────────────
def calc_dna_score(dna: dict) -> int:
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
                    data = run(generate_enhanced_prompt(raw_prompt))

                    st.toast('✨ Neural Network Enhancement Complete', icon='🔥')
                    st.success("✅ Enhancement Complete!")
                    st.balloons()

                    st.markdown("### ✨ Enhanced Prompt")
                    st.text_area(
                        label="Enhanced Prompt Output",
                        value=data.get("enhanced_prompt", ""),
                        height=350,
                        label_visibility="collapsed"
                    )

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

                    orig_dna  = data.get("original_dna", {})
                    enh_dna   = data.get("enhanced_dna", {})
                    orig_score = calc_dna_score(orig_dna)
                    enh_score  = calc_dna_score(enh_dna)
                    diff       = enh_score - orig_score
                    mode_val   = data.get("output_mode", "Unknown")
                    strategy   = data.get("enhancement_strategy_used", "—")

                    st.markdown(f"""
                    <div class="telemetry-dashboard">
                        <div class="telemetry-card"><div class="telemetry-label">Original DNA</div><div class="telemetry-value">{orig_score}</div></div>
                        <div class="telemetry-card"><div class="telemetry-label">Enhanced DNA</div><div class="telemetry-value">{enh_score} <span class="telemetry-delta">↑ +{diff}</span></div></div>
                        <div class="telemetry-card"><div class="telemetry-label">Output Mode</div><div class="telemetry-value" style="font-size:1.1rem">{mode_val}</div></div>
                        <div class="telemetry-card"><div class="telemetry-label">Strategy</div><div class="telemetry-value" style="font-size:0.85rem">{strategy}</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("⚙️ View Raw Engine Metadata (Developer)"):
                        st.json(data.get("intent_intelligence", {}))
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
                    data = run(intent_detect_service(raw_prompt))

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
                    biz  = data.get("business_intelligence")
                    prod = data.get("product_intelligence")
                    if biz or prod:
                        st.markdown("### 💼 Strategic Intelligence")
                        tb1, tb2 = st.tabs(["Business Strategy", "Product Strategy"])
                        with tb1:
                            if biz:
                                st.markdown(f"**Vision:** {biz.get('product_vision')}")
                                st.markdown(f"**Advantage:** {biz.get('competitive_advantage')}")
                                st.markdown(f"**Monetization:** {biz.get('monetization_opportunities')}")
                        with tb2:
                            if prod:
                                st.markdown(f"**MVP Scope:** {prod.get('mvp_scope')}")
                                st.markdown(f"**Value Proposition:** {prod.get('user_value_proposition')}")
                                features = prod.get("core_features", [])
                                if features:
                                    st.markdown("**Core Features:** " + ", ".join(features))
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
                    if not data.get("hidden_conflicts") and not data.get("missing_information"):
                        st.success("No conflicts or missing information detected.")

                    st.markdown("---")
                    st.markdown("### 📊 Strategic Priorities")
                    ranks = data.get("strategic_priority_ranking", {})
                    if ranks:
                        for concept, score in sorted(ranks.items(), key=lambda x: x[1], reverse=True):
                            st.markdown(f"**{concept}**")
                            st.progress(int(score) / 100.0)

                    comp    = data.get("complexity_analysis", {}).get("level", "Unknown")
                    doms    = [d.get("domain") for d in data.get("domain_intelligence", [])]
                    dom_str = ", ".join(doms) if doms else "Unknown"
                    st.markdown(f"""
                    <div class="telemetry-dashboard">
                        <div class="telemetry-card"><div class="telemetry-label">Complexity</div><div class="telemetry-value" style="font-size:1.2rem">{comp}</div></div>
                        <div class="telemetry-card"><div class="telemetry-label">Domains</div><div class="telemetry-value" style="font-size:1rem">{dom_str}</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("⚙️ View Raw Engine Metadata (Developer)"):
                        st.json(data)
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
                    req  = CompressRequest(input_text=raw_prompt, preserve_code=True, mode=mode)
                    data = run(run_compression_pipeline(req))

                    # data is a CompressResponse Pydantic model
                    analysis  = data.compression_analysis
                    reduction = analysis.token_reduction_percent
                    orig_len  = analysis.original_tokens
                    comp_len  = analysis.compressed_tokens
                    meaning   = round(analysis.meaning_preservation_score * 100, 2)

                    st.toast(f'🗜️ Shrinkage Achieved: {reduction}%', icon='📉')
                    st.success(f"✅ Compressed by {reduction}%!")

                    st.markdown(f"""
                    <div class="telemetry-dashboard">
                        <div class="telemetry-card"><div class="telemetry-label">Original Size</div><div class="telemetry-value">{orig_len} <span style="font-size:0.9rem;color:#94a3b8;-webkit-text-fill-color:#94a3b8">tokens</span></div></div>
                        <div class="telemetry-card"><div class="telemetry-label">Compressed Size</div><div class="telemetry-value">{comp_len} <span style="color:#ef4444;-webkit-text-fill-color:#ef4444;margin-left:8px">↓ -{reduction}%</span></div></div>
                        <div class="telemetry-card"><div class="telemetry-label">Meaning Preserved</div><div class="telemetry-value">{meaning}%</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("### 📦 Condensed Output")
                    st.text_area(
                        label="Condensed Output",
                        value=data.compressed_context,
                        height=300,
                        label_visibility="collapsed"
                    )
                except Exception as e:
                    st.error(f"⚠️ Compression failed: {e}")

# ─── Intelligent Router ────────────────────────────────────────────────────────
elif active_tool == "Intelligent Router":
    st.title("🚦 Intelligent Router (Orchestrator)")
    st.markdown("Stop guessing which AI agent you need. Describe what you want — Syntra assembles the optimal execution pipeline.")

    raw_prompt = st.text_area("User Query", height=100, placeholder="Ask anything. Syntra will route it...")
    code_ctx   = st.text_area("Optional Code Context", height=100, placeholder="Paste any relevant code here...")

    if st.button("Execute Request", use_container_width=True):
        if not raw_prompt.strip():
            st.warning("Please enter a query.")
        else:
            with st.spinner("🚦 Routing to optimal agent..."):
                try:
                    result = run(routing_service(
                        prompt=raw_prompt,
                        code_context=code_ctx.strip() or None,
                        language=None
                    ))
                    orch = result.orchestration

                    st.toast(f'🚦 Pipeline Ready: {orch.execution_readiness.status}', icon='🤖')

                    status = orch.execution_readiness.status
                    if "Ready" in status:
                        st.success(f"### ✅ {status}")
                    else:
                        st.warning(f"### ⚠️ {status}")
                    st.write(orch.execution_readiness.reasoning)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### 🎯 Primary Agent")
                        st.markdown(f"**<span style='color:#3b82f6'>{orch.primary_agent.agent_name}</span>**", unsafe_allow_html=True)
                        st.caption(orch.primary_agent.reasoning)
                    with col2:
                        st.markdown("#### 🤝 Supporting Agents")
                        for sa in orch.supporting_agents:
                            st.markdown(f"- **{sa.agent_name}**")
                            st.caption(sa.reasoning)

                    st.divider()

                    st.markdown("#### ⚙️ Execution Pipeline")
                    if orch.execution_pipeline:
                        pipeline_html = " <br>⬇<br> ".join([
                            f"<div style='background:#1e293b;padding:10px;border-radius:5px;text-align:center;border:1px solid #334155'><b>{step}</b></div>"
                            for step in orch.execution_pipeline
                        ])
                        st.markdown(pipeline_html, unsafe_allow_html=True)

                    st.markdown("#### 📊 Detected Intents & Confidence")
                    st.write(f"**Primary Intent:** {orch.primary_intent}")
                    st.write(f"**Secondary Intents:** {', '.join(orch.secondary_intents)}")
                    for intent, conf in orch.confidence_scoring.intent_confidences.items():
                        st.progress(int(conf) / 100, text=f"{intent} ({conf}%)")
                    st.metric("Overall Routing Confidence", f"{orch.confidence_scoring.overall_confidence}%")

                    st.divider()
                    col3, col4 = st.columns(2)
                    with col3:
                        st.markdown("#### 🧠 Task Complexity")
                        st.info(f"**Level:** {orch.complexity.level}\n\n**Reason:** {orch.complexity.reasoning}")
                    with col4:
                        st.markdown("#### ❓ Clarification Strategy")
                        missing  = orch.clarification_strategy.missing_information
                        question = orch.clarification_strategy.clarification_question
                        if missing:
                            st.warning("**Missing Info:**\n" + "\n".join([f"- {m}" for m in missing]))
                        if question:
                            st.error(f"**Key Question:** {question}")
                        elif not missing:
                            st.success("No clarification needed.")

                    with st.expander("⚙️ View Orchestration Metadata (Developer)"):
                        st.json(orch.model_dump())
                except Exception as e:
                    st.error(f"⚠️ Routing failed: {e}")
