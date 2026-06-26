import streamlit as st
import requests
import json

st.set_page_config(page_title="Syntra AI", page_icon="🚀", layout="wide")

# ─── Custom CSS for Next-Gen UI ───────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global Theme Overrides - Clean Dark Mode */
    .stApp { 
        background-color: #0A0806;
        color: #F2ECE2; 
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Ensure all text uses the readable font */
    p, span, div, label {
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
    }
    
    /* Text Areas - Glassmorphic */
    .stTextArea textarea {
        background: rgba(15, 13, 10, 0.4) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
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
        transform: scale(1.01);
    }
    
    /* Force Code Blocks to Wrap text (No horizontal scrolling) */
    pre, code {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }
    
    /* Glowing Animated Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #FF512F, #DD2476, #FF512F);
        background-size: 200% auto;
        color: white; 
        border: none; 
        border-radius: 12px;
        font-weight: 800; 
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: 0.5s;
        box-shadow: 0 0 15px rgba(221, 36, 118, 0.4);
    }
    .stButton > button:hover { 
        background-position: right center; /* trigger gradient movement */
        box-shadow: 0 0 25px rgba(221, 36, 118, 0.8); 
        transform: translateY(-2px); 
    }
    
    /* Sidebar - Clean Dark */
    [data-testid="stSidebar"] { 
        background-color: #0C0A08 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05); 
    }
    
    /* Metric Cards - Neon Accents */
    [data-testid="stMetricValue"] { 
        color: transparent;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        font-weight: 900;
        text-shadow: 0 0 10px rgba(0, 201, 255, 0.3);
    }
    [data-testid="stMetricDelta"] { color: #92FE9D; }
    
    /* Highly Designed Custom Telemetry Dashboards */
    .telemetry-dashboard {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .telemetry-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: inset 0 0 0 rgba(0,0,0,0), 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .telemetry-card:hover {
        transform: translateY(-3px);
        border-color: rgba(217, 70, 239, 0.4);
        background: rgba(255, 255, 255, 0.04);
        box-shadow: 0 8px 25px rgba(217, 70, 239, 0.15);
    }
    .telemetry-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 10px;
        font-weight: 600;
    }
    .telemetry-value {
        font-size: 1.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        color: transparent;
        line-height: 1.2;
    }
    .telemetry-delta {
        font-size: 1rem;
        color: #22c55e;
        -webkit-text-fill-color: #22c55e;
        margin-left: 10px;
        vertical-align: middle;
    }
    
    /* Headers & Subheaders - Gradient Text */
    h1 { 
        background: linear-gradient(90deg, #f87171, #f472b6, #c084fc);
        -webkit-background-clip: text;
        color: transparent !important;
        font-family: 'Inter', sans-serif;
        font-weight: 900 !important;
        letter-spacing: -1px;
    }
    h2, h3 { 
        color: #E2E8F0 !important; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Sidebar Navigation Pills (Radio Buttons) */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.7rem;
    }
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 14px 16px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        display: flex;
        align-items: center;
        box-shadow: inset 0 0 0 rgba(0,0,0,0);
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: linear-gradient(90deg, rgba(217, 70, 239, 0.1) 0%, rgba(255, 255, 255, 0.02) 100%);
        transform: translateX(6px);
        border-color: rgba(217, 70, 239, 0.5);
        border-left: 4px solid #d946ef;
        box-shadow: -4px 0 20px rgba(217, 70, 239, 0.2);
    }
    [data-testid="stSidebar"] .stRadio label p {
        font-weight: 600 !important;
        color: #E2E8F0 !important;
        font-size: 0.95rem;
    }
    
    /* Hide Native Radio Circles */
    [data-testid="stSidebar"] .stRadio label > div:first-child {
        display: none !important;
    }
    
    /* Hide the 'TOOLS' main label completely */
    [data-testid="stSidebar"] .stRadio > label {
        display: none !important;
    }
    
    /* Center the text inside the pill */
    [data-testid="stSidebar"] .stRadio label > div:nth-child(2) {
        width: 100%;
        text-align: center;
        margin-left: 0 !important;
    }
    
    /* Animated Sidebar Logo */
    .sidebar-logo {
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        background: linear-gradient(to right, #f97316, #d946ef, #3b82f6);
        background-size: 200% auto;
        -webkit-background-clip: text;
        color: transparent;
        text-align: center;
        letter-spacing: 1px;
        margin-bottom: 0px !important;
        animation: shine 3s linear infinite;
    }
    .sidebar-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 4px;
        margin-top: -10px;
        margin-bottom: 30px !important;
    }
    @keyframes shine {
        to { background-position: 200% center; }
    }
    
    /* Custom Expanders */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.02);
        border-radius: 8px;
        transition: all 0.3s;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(255,255,255,0.05);
        color: #d946ef !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Configuration ─────────────────────────────────────────────────────────────
API_BASE = "http://127.0.0.1:8000/v1"

def display_error(res):
    """Parses FastAPI errors and displays ONLY non-technical, friendly text."""
    try:
        err_data = res.json()
        if res.status_code == 422:
            st.error("⚠️ Oops! Your input was a bit too short or missing details. Please provide a few more words!")
        else:
            detail = err_data.get("detail", "An unexpected error occurred.")
            # If it's a list (some FastApi internal errors), just convert to string
            if isinstance(detail, list):
                st.error("⚠️ Please check your input and try again.")
            else:
                st.error(f"⚠️ {detail}")
    except Exception:
        st.error("⚠️ Our servers are currently unreachable. Please try again in a moment.")

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
    

# ─── Main Interface ────────────────────────────────────────────────────────────

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
                    res = requests.post(f"{API_BASE}/enhance", json={"prompt": raw_prompt})
                    if res.status_code == 200:
                        data = res.json()
                        st.toast('✨ Neural Network Enhancement Complete', icon='🔥')
                        st.success("✅ Enhancement Complete!")
                        st.balloons()
                        
                        st.markdown("### ✨ Enhanced Prompt")
                        
                        # Use a large text area so the user can easily read and copy it
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
                        
                        orig_score = data.get('original_score', 0)
                        enh_score = data.get('enhanced_score', 0)
                        diff = data.get('improvement_score', 0)
                        risk = data.get('risk_classification', 'Unknown')
                        mode = data.get('output_mode', 'Unknown')
                        
                        html_dashboard = f"""
                        <div class="telemetry-dashboard">
                            <div class="telemetry-card">
                                <div class="telemetry-label">Original DNA</div>
                                <div class="telemetry-value">{orig_score}</div>
                            </div>
                            <div class="telemetry-card">
                                <div class="telemetry-label">Enhanced DNA</div>
                                <div class="telemetry-value">{enh_score} <span class="telemetry-delta">↑ +{diff}</span></div>
                            </div>
                            <div class="telemetry-card">
                                <div class="telemetry-label">Risk Level</div>
                                <div class="telemetry-value" style="font-size: 1.2rem;">{risk}</div>
                            </div>
                            <div class="telemetry-card">
                                <div class="telemetry-label">Engine Mode</div>
                                <div class="telemetry-value" style="font-size: 1.2rem;">{mode}</div>
                            </div>
                        </div>
                        """
                        st.markdown(html_dashboard, unsafe_allow_html=True)
                        
                        with st.expander("⚙️ View Raw Engine Metadata (Developer)"):
                            st.json(data.get("intent_intelligence", {}))
                    else:
                        display_error(res)
                except Exception as e:
                    st.error(f"Connection Failed: {e}")

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
                    res = requests.post(f"{API_BASE}/intent", json={"prompt": raw_prompt})
                    if res.status_code == 200:
                        data = res.json()
                        st.toast('🧠 Cognitive Extraction Finished', icon='👁️')
                        st.success("✅ Analysis Complete!")
                        
                        st.markdown("### 🌟 North Star Mission")
                        st.info(data.get("intent_hierarchy", {}).get("north_star_mission", "Unknown"))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### 🎯 Intent Hierarchy")
                            st.markdown("**Primary Intent:**")
                            st.write(data.get("intent_hierarchy", {}).get("primary_intent", "Unknown"))
                            st.markdown("**Long-Term Vision:**")
                            st.write(data.get("intent_hierarchy", {}).get("long_term_vision", "Unknown"))
                        with col2:
                            st.markdown("#### 🚀 Execution Intent")
                            st.markdown(f"**{data.get('execution_classification', {}).get('category', 'Unknown')}**")
                            st.markdown(f"*{data.get('execution_classification', {}).get('reasoning', '')}*")
                            
                        st.markdown("---")
                        biz = data.get("business_intelligence")
                        prod = data.get("product_intelligence")
                        if biz or prod:
                            st.markdown("### 💼 Strategic Intelligence")
                            tb1, tb2 = st.tabs(["Business Strategy", "Product Strategy"])
                            with tb1:
                                if biz:
                                    st.markdown(f"**Vision:** {biz.get('product_vision')}")
                                    st.markdown(f"**Advantage:** {biz.get('competitive_advantage')}")
                                    st.markdown(f"**Monetization:** {biz.get('monetization_opportunities')}")
                                else:
                                    st.write("No business intelligence inferred.")
                            with tb2:
                                if prod:
                                    st.markdown(f"**MVP Scope:** {prod.get('mvp_scope')}")
                                    st.markdown(f"**Value Proposition:** {prod.get('user_value_proposition')}")
                                    st.markdown("**Core Features:** " + ", ".join(prod.get("core_features", [])))
                                else:
                                    st.write("No product intelligence inferred.")
                            st.markdown("---")
                            
                        st.markdown("### 🧠 User Psychology & Outcomes")
                        mots = data.get("user_motivations", [])
                        if mots:
                            st.markdown("**Inferred Motivations:**")
                            for m in mots:
                                st.markdown(f"- **{m.get('motivation')}**: {m.get('reasoning')}")
                                
                        out = data.get("user_outcome_intelligence")
                        if out:
                            st.markdown(f"**Current Pain:** {out.get('current_user_pain')}")
                            st.markdown(f"**Desired Transformation:** {out.get('desired_transformation')}")
                            
                        st.markdown("---")
                        st.markdown("### ⚠️ Critical Gaps & Conflicts")
                        conf = data.get("hidden_conflicts", [])
                        if conf:
                            for c in conf:
                                st.error(f"**Conflict Detected ({c.get('conflict_type')}):** {c.get('explanation')}")
                        missing = data.get("missing_information", [])
                        if missing:
                            for m in missing:
                                st.warning(f"**Missing {m.get('missing_category')}:** {m.get('impact')}")
                        if not conf and not missing:
                            st.success("No conflicts or missing information detected.")
                            
                        st.markdown("---")
                        st.markdown("### 📊 Strategic Priorities")
                        ranks = data.get("strategic_priority_ranking", {})
                        if ranks:
                            for concept, score in sorted(ranks.items(), key=lambda item: item[1], reverse=True):
                                st.markdown(f"**{concept}**")
                                st.progress(score / 100.0)
                        
                        st.markdown("---")
                        st.markdown("#### 🧬 Cognitive Telemetry")
                        comp = data.get('complexity_analysis', {}).get('level', 'Unknown')
                        doms = [d.get("domain") for d in data.get("domain_intelligence", [])]
                        dom_str = ", ".join(doms) if doms else "Unknown"
                        
                        html_dashboard = f"""
                        <div class="telemetry-dashboard">
                            <div class="telemetry-card">
                                <div class="telemetry-label">Complexity</div>
                                <div class="telemetry-value" style="font-size: 1.2rem;">{comp}</div>
                            </div>
                            <div class="telemetry-card">
                                <div class="telemetry-label">Domains Detected</div>
                                <div class="telemetry-value" style="font-size: 1.2rem;">{dom_str}</div>
                            </div>
                        </div>
                        """
                        st.markdown(html_dashboard, unsafe_allow_html=True)
                            
                        with st.expander("⚙️ View Raw Engine Metadata (Developer)"):
                            st.json(data)
                    else:
                        display_error(res)
                except Exception as e:
                    st.error(f"Connection Failed: {e}")

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
                    res = requests.post(f"{API_BASE}/compress", json={"input_text": raw_prompt, "preserve_code": True, "mode": mode})
                    if res.status_code == 200:
                        data = res.json()
                        analysis = data.get("compression_analysis", {})
                        
                        st.toast(f'🗜️ Shrinkage Achieved: {analysis.get("token_reduction_percent", 0)}%', icon='📉')
                        st.success(f"✅ Compressed by {analysis.get('token_reduction_percent', 0)}%!")
                        
                        st.markdown("#### 📉 Compression Metrics")
                        
                        orig_len = analysis.get('original_tokens', 0)
                        comp_len = analysis.get('compressed_tokens', 0)
                        reduction = analysis.get('token_reduction_percent', 0)
                        meaning = round(analysis.get('meaning_preservation_score', 0) * 100, 2)
                        
                        html_dashboard = f"""
                        <div class="telemetry-dashboard">
                            <div class="telemetry-card">
                                <div class="telemetry-label">Original Size</div>
                                <div class="telemetry-value">{orig_len} <span style="font-size: 0.9rem; color: #94a3b8; -webkit-text-fill-color: #94a3b8;">tokens</span></div>
                            </div>
                            <div class="telemetry-card">
                                <div class="telemetry-label">Compressed Size</div>
                                <div class="telemetry-value">{comp_len} <span style="font-size: 1rem; color: #ef4444; -webkit-text-fill-color: #ef4444; margin-left: 8px;">↓ -{reduction}%</span></div>
                            </div>
                            <div class="telemetry-card">
                                <div class="telemetry-label">Meaning Preserved</div>
                                <div class="telemetry-value">{meaning}%</div>
                            </div>
                        </div>
                        """
                        st.markdown(html_dashboard, unsafe_allow_html=True)
                        
                        st.markdown("### 📦 Condensed Output")
                        st.text_area(
                            label="Condensed Output",
                            value=data.get("compressed_context", ""), 
                            height=300,
                            label_visibility="collapsed"
                        )
                    else:
                        display_error(res)
                except Exception as e:
                    st.error(f"Connection Failed: {e}")

elif active_tool == "Intelligent Router":
    st.title("🚦 Intelligent Router (Orchestrator)")
    st.markdown("""
    **Stop guessing which AI agent or tool you need.** 
    Simply describe what you want to build, and the Orchestrator will instantly analyze your complex request, assemble a specialized team of AI experts, and map out the exact execution pipeline needed to bring your vision to life. It acts as your project manager, ensuring nothing falls through the cracks.
    """)
    
    raw_prompt = st.text_area("User Query", height=100, placeholder="Ask anything. Syntra will route it...")
    code_ctx = st.text_area("Optional Code Context", height=100, placeholder="Paste any relevant code here...")
    
    if st.button("Execute Request", use_container_width=True):
        if not raw_prompt.strip():
            st.warning("Please enter a query.")
        else:
            with st.spinner("🚦 Routing to optimal agent..."):
                try:
                    payload = {"prompt": raw_prompt}
                    if code_ctx.strip():
                        payload["code_context"] = code_ctx
                        
                    res = requests.post(f"{API_BASE}/chat", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        orch = data.get("orchestration", {})
                        
                        st.toast(f'🚦 Pipeline Ready: {orch.get("execution_readiness", {}).get("status", "Unknown")}', icon='🤖')
                        
                        # ── TOP LEVEL READINESS ──
                        status = orch.get("execution_readiness", {}).get("status", "")
                        if "Ready" in status:
                            st.success(f"### ✅ {status}")
                        else:
                            st.warning(f"### ⚠️ {status}")
                        st.write(orch.get("execution_readiness", {}).get("reasoning", ""))
                        
                        # ── PRIMARY & SUPPORTING AGENTS ──
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### 🎯 Primary Agent")
                            pri_agent = orch.get("primary_agent", {})
                            st.markdown(f"**<span style='color: #3b82f6;'>{pri_agent.get('agent_name', 'Unknown')}</span>**", unsafe_allow_html=True)
                            st.caption(pri_agent.get('reasoning', ''))
                        
                        with col2:
                            st.markdown("#### 🤝 Supporting Agents")
                            for sa in orch.get("supporting_agents", []):
                                st.markdown(f"- **{sa.get('agent_name')}**")
                                st.caption(sa.get('reasoning'))
                                
                        st.divider()
                        
                        # ── EXECUTION PIPELINE VISUALIZATION ──
                        st.markdown("#### ⚙️ Execution Pipeline")
                        pipeline = orch.get("execution_pipeline", [])
                        if pipeline:
                            pipeline_html = " <br>⬇<br> ".join([f"<div style='background-color: #1e293b; padding: 10px; border-radius: 5px; text-align: center; border: 1px solid #334155;'><b>{step}</b></div>" for step in pipeline])
                            st.markdown(pipeline_html, unsafe_allow_html=True)
                        st.write("")
                        
                        # ── DETECTED INTENTS & CONFIDENCE ──
                        st.markdown("#### 📊 Detected Intents & Confidence")
                        st.write(f"**Primary Intent:** {orch.get('primary_intent', '')}")
                        st.write(f"**Secondary Intents:** {', '.join(orch.get('secondary_intents', []))}")
                        
                        conf_scores = orch.get("confidence_scoring", {}).get("intent_confidences", {})
                        for intent, conf in conf_scores.items():
                            st.progress(conf / 100.0, text=f"{intent} ({conf}%)")
                            
                        st.metric("Overall Routing Confidence", f"{orch.get('confidence_scoring', {}).get('overall_confidence', 0)}%")
                        
                        st.divider()
                        
                        # ── COMPLEXITY & MISSING INFO ──
                        col3, col4 = st.columns(2)
                        with col3:
                            st.markdown("#### 🧠 Task Complexity")
                            comp = orch.get("complexity", {})
                            st.info(f"**Level:** {comp.get('level', '')}\n\n**Reason:** {comp.get('reasoning', '')}")
                            
                        with col4:
                            st.markdown("#### ❓ Clarification Strategy")
                            clar = orch.get("clarification_strategy", {})
                            missing = clar.get("missing_information", [])
                            if missing:
                                st.warning("**Missing Information:**\n" + "\n".join([f"- {m}" for m in missing]))
                            question = clar.get("clarification_question")
                            if question:
                                st.error(f"**Highest-Impact Question:**\n{question}")
                            elif not missing:
                                st.success("No missing information detected. Fully actionable.")
                        
                        with st.expander("⚙️ View Orchestration Metadata (Developer)"):
                            st.json(orch)
                    else:
                        display_error(res)
                except Exception as e:
                    st.error(f"Connection Failed: {e}")
