import streamlit as st
import streamlit.components.v1 as components
import ast
import random
from langchain_core.messages import HumanMessage

# ── Content extractor ─────────────────────────────────────────────────────────
def extract_text(raw) -> str:
    if isinstance(raw, str):
        stripped = raw.strip()
        if stripped.startswith("[{") or stripped.startswith("[{'"):
            try:
                parsed = ast.literal_eval(stripped)
            except Exception:
                try:
                    import json
                    parsed = json.loads(stripped)
                except Exception:
                    return stripped
            if isinstance(parsed, list):
                parts = [
                    block.get("text", "")
                    for block in parsed
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                return "\n\n".join(p for p in parts if p).strip() or stripped
        return stripped

    if isinstance(raw, list):
        parts = [
            block.get("text", "")
            for block in raw
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "\n\n".join(p for p in parts if p).strip()

    return str(raw)


st.set_page_config(
    page_title="Verity — AI Research",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Tab-to-Fill Javascript Hack ───────────────────────────────────────────────
# We must use components.html because st.html() explicitly blocks JavaScript execution.
components.html(
    """
    <script>
    const doc = window.parent.document;
    const initTabListener = () => {
        const inputs = doc.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            if (!input.hasAttribute('data-tab-listener')) {
                input.setAttribute('data-tab-listener', 'true');
                input.addEventListener('keydown', function(e) {
                    if (e.key === 'Tab' && this.value === '') {
                        e.preventDefault();
                        let fillText = this.placeholder;
                        // Strip 'e.g. ' prefix so it inputs clean text
                        if (fillText.startsWith('e.g. ')) {
                            fillText = fillText.substring(5);
                        }
                        // React input hack to force state update
                        let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                        nativeInputValueSetter.call(this, fillText);
                        this.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                });
            }
        });
    };
    // Run periodically to catch the input when Streamlit re-renders it
    setInterval(initTabListener, 500);
    </script>
    """,
    height=0,
    width=0,
)


# ── Session State Management ──────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "pipeline_state" not in st.session_state:
    st.session_state.pipeline_state = {
        "status": "idle",
        "topic": "",
        "search_text": "",
        "scraped_text": "",
        "report": "",
        "feedback": ""
    }

# Dynamic placeholders
PLACEHOLDERS = [
    "e.g. Impact of LLMs on software engineering",
    "e.g. Recent breakthroughs in solid-state batteries",
    "e.g. The economic effects of global aging populations",
    "e.g. How does quantum error correction work?",
    "e.g. The history and evolution of the Silk Road",
    "e.g. Architectural differences between Transformer and Mamba models"
]

if "current_placeholder" not in st.session_state:
    st.session_state.current_placeholder = random.choice(PLACEHOLDERS)

# ── Colour tokens ─────────────────────────────────────────────────────────────
if st.session_state.theme == "light":
    BG_PAGE    = "#f2f0eb"
    BG_CARD    = "#ffffff"
    BG_RAISED  = "#eceae4"
    BORDER     = "#d4d0c8"
    BORDER_DIM = "#e2dfd8"
    
    # Darker font colours for light theme
    TXT_PRIMARY   = "#000000"   # Pitch black
    TXT_SECONDARY = "#111827"   # Very dark grey
    TXT_MUTED     = "#374151"   
    TXT_DIMMED    = "#4b5563"   
    
    GOLD        = "#a07820"
    GOLD_BG     = "rgba(160,120,32,0.08)"
    GOLD_BORDER = "rgba(160,120,32,0.28)"
    GREEN        = "#1a7a4a"
    GREEN_BG     = "rgba(26,122,74,0.08)"
    GREEN_BORDER = "rgba(26,122,74,0.28)"
    BTN_TEXT     = "#000000"
    
    # Opposite theme (Dark) for the toggle button
    OPP_BG     = "#111827"
    OPP_TXT    = "#ffffff"
    OPP_BORDER = "#374151"
    OPP_HOVER  = "#484f58"
else:
    # High-contrast Dark Theme 
    BG_PAGE    = "#0b0f19"   
    BG_CARD    = "#111827"   
    BG_RAISED  = "#1f2937"   
    BORDER     = "#374151"   
    BORDER_DIM = "#1f2937"   
    
    # Whiter font colours for dark theme
    TXT_PRIMARY   = "#ffffff"   # Pure white
    TXT_SECONDARY = "#f3f4f6"   # Bright off-white
    TXT_MUTED     = "#d1d5db"   
    TXT_DIMMED    = "#9ca3af"   
    
    GOLD        = "#f59e0b"     
    GOLD_BG     = "rgba(245, 158, 11, 0.15)"
    GOLD_BORDER = "rgba(245, 158, 11, 0.4)"
    GREEN        = "#10b981"    
    GREEN_BG     = "rgba(16, 185, 129, 0.15)"
    GREEN_BORDER = "rgba(16, 185, 129, 0.4)"
    BTN_TEXT     = "#ffffff"    
    
    # Opposite theme (Light) for the toggle button
    OPP_BG     = "#ffffff"
    OPP_TXT    = "#000000"
    OPP_BORDER = "#d4d0c8"
    OPP_HOVER  = "#e2dfd8"


# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {TXT_SECONDARY}; }}
.stApp {{ background: {BG_PAGE}; }}
#MainMenu, footer, header {{ visibility: hidden; }}

/* Pulled top spacing as tight as possible */
.block-container {{ 
    padding-top: 0rem !important; 
    padding-left: 2.8rem;
    padding-right: 2.8rem;
    padding-bottom: 3rem;
    margin-top: -1.5rem;
    max-width: 100%; 
}}

/* Larger Logo */
h1 {{
    font-family: 'Playfair Display', serif !important;
    color: {TXT_PRIMARY} !important;
    font-size: 3.8rem !important; 
    letter-spacing: -0.4px;
    margin-bottom: 0 !important;
}}

/* global prose */
p, li, span, div {{ color: {TXT_SECONDARY}; }}

/* ── input ── */
.stTextInput > label {{
    color: {TXT_MUTED} !important;
    font-size: 0.85rem !important; 
    letter-spacing: 1.4px;
    text-transform: uppercase;
    font-weight: 500 !important;
}}

/* Target the baseweb wrapper to prevent Streamlit from turning it dark on focus */
.stTextInput div[data-baseweb="input"], .stTextInput div[data-baseweb="base-input"] {{
    background-color: {BG_CARD} !important;
}}
.stTextInput div[data-baseweb="input"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    overflow: hidden;
}}
.stTextInput div[data-baseweb="input"]:focus-within {{
    border-color: {GOLD} !important;
    box-shadow: 0 0 0 3px rgba(160,120,32,0.12) !important;
    background-color: {BG_CARD} !important;
}}

/* Target the actual input text box */
.stTextInput input {{
    background-color: transparent !important;
    color: {TXT_PRIMARY} !important;
    caret-color: {TXT_PRIMARY} !important; 
    font-family: 'Inter', sans-serif !important;
    font-size: 1.05rem !important;
    padding: 0.6rem 1rem !important;
}}
.stTextInput input::placeholder {{ color: {TXT_DIMMED} !important; }}

/* ── primary button ── */
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
    background: {GOLD} !important;
    color: {BTN_TEXT} !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    height: 44px !important;
    transition: all 0.18s ease !important;
}}
/* Override Streamlit's inner p tag color specifically for the primary button */
.stButton > button[kind="primary"] p, .stFormSubmitButton > button[kind="primary"] p {{
    color: {BTN_TEXT} !important;
}}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{
    opacity: 0.85 !important;
    box-shadow: 0 4px 14px rgba(160,120,32,0.22) !important;
    transform: translateY(-1px) !important;
}}

/* ── standard button (used for opposite theme toggle) ── */
.stButton > button[kind="secondary"] {{
    background: {OPP_BG} !important;
    color: {OPP_TXT} !important;
    border: 1px solid {OPP_BORDER} !important;
    border-radius: 8px !important;
    font-size: 1.0rem !important;
    font-weight: 500 !important;
}}
/* Override Streamlit's inner p tag color specifically for the theme button */
.stButton > button[kind="secondary"] p {{
    color: {OPP_TXT} !important;
}}
.stButton > button[kind="secondary"]:hover {{
    border-color: {OPP_HOVER} !important;
    background: {OPP_HOVER} !important;
    color: {OPP_TXT} !important;
}}
.stButton > button[kind="secondary"]:hover p {{
    color: {OPP_TXT} !important;
}}

/* ── download button ── */
.stDownloadButton > button {{
    background: {BG_CARD} !important;
    color: {GOLD} !important;
    border: 1px solid {GOLD_BORDER} !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 1.0rem !important;
    margin-top: 0.8rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}}
.stDownloadButton > button p {{
    color: {GOLD} !important;
}}
.stDownloadButton > button:hover {{
    background: {GOLD_BG} !important;
}}

/* ── divider ── */
hr {{ border-color: {BORDER_DIM} !important; margin: 1rem 0 !important; }}

/* ── spinner ── */
.stSpinner p, .stSpinner > div {{ color: {TXT_MUTED} !important; font-size: 1.0rem !important; }}

/* ── expander header ── */
details > summary,
.streamlit-expanderHeader,
[data-testid="stExpander"] summary {{
    background: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {TXT_PRIMARY} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.0rem !important;
    font-weight: 500 !important;
    padding: 0.7rem 1rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}}

/* ── expander body ── */
.streamlit-expanderContent,
[data-testid="stExpander"] > div:last-child,
details > div {{
    background: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 1rem 1.1rem !important;
}}

/* Force readable text inside expanders */
[data-testid="stExpander"] p,
[data-testid="stExpander"] li,
[data-testid="stExpander"] span:not(.stMarkdownContainer),
[data-testid="stExpander"] div {{
    color: {TXT_SECONDARY} !important;
    font-size: 1.0rem !important;
    line-height: 1.75 !important;
}}
[data-testid="stExpander"] h1,
[data-testid="stExpander"] h2,
[data-testid="stExpander"] h3,
[data-testid="stExpander"] h4,
[data-testid="stExpander"] strong,
[data-testid="stExpander"] b {{
    color: {TXT_PRIMARY} !important;
    font-size: unset !important;
}}
.streamlit-expanderContent * {{
    color: {TXT_SECONDARY} !important;
    line-height: 1.75 !important;
}}
.streamlit-expanderContent h1,
.streamlit-expanderContent h2,
.streamlit-expanderContent h3,
.streamlit-expanderContent strong {{
    color: {TXT_PRIMARY} !important;
}}

/* ── hint card ── */
.v-hint {{
    background: {BG_CARD};
    border: 1px dashed {BORDER};
    border-radius: 10px;
    padding: 1.3rem 1.5rem;
    color: {TXT_MUTED};
    font-size: 1.0rem;
    line-height: 1.7;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}}
.v-hint strong {{ color: {GOLD}; font-weight: 600; }}

/* ── topic chip ── */
.v-chip {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {GOLD_BG};
    border: 1px solid {GOLD_BORDER};
    color: {GOLD};
    border-radius: 20px;
    padding: 4px 13px;
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 1rem;
}}
</style>
""", unsafe_allow_html=True)


# ── Step tracker ──────────────────────────────────────────────────────────────
def tracker_html(current: int) -> str:
    """current: 0=idle, 1-4=that step active, 5=done"""

    steps = [
        ("01", "Search",   "Scan web sources"),
        ("02", "Scrape",   "Extract page content"),
        ("03", "Write",    "Draft the report"),
        ("04", "Critique", "Evaluate the draft"),
    ]

    def step_styles(state):
        if state == "done":
            return dict(
                circ_bg    = GREEN_BG,
                circ_bdr   = GREEN,
                circ_color = GREEN,
                circ_shadow= "",
                name_color = GREEN,
                desc_color = "#3d8060" if st.session_state.theme == 'light' else "#34d399",
                badge_bg   = GREEN_BG,
                badge_color= GREEN,
                badge_text = "✓  Done",
            )
        if state == "active":
            return dict(
                circ_bg    = GOLD_BG,
                circ_bdr   = GOLD,
                circ_color = GOLD,
                circ_shadow= "box-shadow:0 0 14px rgba(217,183,87,0.22);",
                name_color = TXT_PRIMARY,
                desc_color = TXT_SECONDARY,
                badge_bg   = GOLD_BG,
                badge_color= GOLD,
                badge_text = "●  Running",
            )
        # pending
        return dict(
            circ_bg    = BG_RAISED,
            circ_bdr   = BORDER,
            circ_color = TXT_MUTED,        
            circ_shadow= "",
            name_color = TXT_MUTED,        
            desc_color = TXT_DIMMED,       
            badge_bg   = "transparent",
            badge_color= "transparent",
            badge_text = "",
        )

    html = (
        f'<div style="background:{BG_CARD};border:1px solid {BORDER};'
        f'border-radius:12px;padding:1.3rem 1.4rem;'
        f'box-shadow:0 2px 8px rgba(0,0,0,0.07);">'
        f'<p style="font-size:0.75rem;font-weight:600;letter-spacing:2px;'
        f'text-transform:uppercase;color:{TXT_DIMMED};margin:0 0 1.4rem;">'
        f'Verity · 4 steps</p>'
    )

    for i, (num, name, desc) in enumerate(steps, start=1):
        state = "done" if current > i else ("active" if current == i else "pending")
        s     = step_styles(state)
        conn_color = GREEN if current > i else BORDER

        connector = (
            f'<div style="width:2px;height:22px;margin:3px auto 3px;'
            f'border-radius:2px;background:{conn_color};opacity:0.45;"></div>'
        ) if i < 4 else ""

        badge = (
            f'<span style="display:inline-block;margin-top:5px;'
            f'background:{s["badge_bg"]};color:{s["badge_color"]};'
            f'border-radius:20px;padding:2px 8px;font-size:0.75rem;'
            f'font-weight:600;letter-spacing:0.5px;text-transform:uppercase;">'
            f'{s["badge_text"]}</span>'
        ) if s["badge_text"] else ""

        html += (
            f'<div style="display:flex;align-items:flex-start;gap:0.8rem;">'
            f'  <div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0;">'
            f'    <div style="width:34px;height:34px;border-radius:50%;'
            f'background:{s["circ_bg"]};border:2px solid {s["circ_bdr"]};'
            f'color:{s["circ_color"]};{s["circ_shadow"]}'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:0.8rem;font-weight:700;flex-shrink:0;">{num}</div>'
            f'    {connector}'
            f'  </div>'
            f'  <div style="padding-top:5px;padding-bottom:2px;min-width:0;">'
            f'    <div style="font-size:1.0rem;font-weight:600;'
            f'color:{s["name_color"]};line-height:1.3;">{name}</div>'
            f'    <div style="font-size:0.85rem;color:{s["desc_color"]};margin-top:2px;">{desc}</div>'
            f'    {badge}'
            f'  </div>'
            f'</div>'
        )

    if current > 0:
        pct       = 100 if current >= 5 else int((current - 1) / 4 * 100)
        label     = "Complete" if current >= 5 else f"Step {min(current,4)} of 4"
        bar_color = GREEN if current >= 5 else GOLD
        html += (
            f'<div style="margin-top:1.2rem;padding-top:1rem;'
            f'border-top:1px solid {BORDER_DIM};">'
            f'  <div style="font-size:0.75rem;color:{TXT_DIMMED};letter-spacing:1.2px;'
            f'text-transform:uppercase;margin-bottom:6px;">{label}</div>'
            f'  <div style="background:{BG_RAISED};border-radius:4px;height:4px;">'
            f'    <div style="background:{bar_color};height:4px;border-radius:4px;'
            f'width:{pct}%;"></div>'
            f'  </div>'
            f'</div>'
        )

    if current >= 5:
        html += (
            f'<div style="margin-top:0.9rem;background:{GREEN_BG};'
            f'border:1px solid {GREEN_BORDER};border-radius:8px;'
            f'padding:0.6rem 1rem;color:{GREEN};font-size:0.9rem;'
            f'font-weight:600;text-align:center;">'
            f'✓ Pipeline complete</div>'
        )

    html += "</div>"
    return html


# ── Header & Top Nav ──────────────────────────────────────────────────────────
col_title, col_toggle = st.columns([5, 1])

with col_title:
    st.markdown("# Verity")
    st.markdown(
        f'<p style="color:{TXT_MUTED};font-size:1.0rem;margin-top:-0.4rem;'
        f'margin-bottom:1.5rem;letter-spacing:0.3px;">'
        f'AI-powered research · Search · Scrape · Write · Critique</p>',
        unsafe_allow_html=True,
    )

with col_toggle:
    st.markdown("<div style='height: 18px'></div>", unsafe_allow_html=True) 
    theme_label = "☀️ Light Mode" if st.session_state.theme == "dark" else "🌙 Dark Mode"
    if st.button(theme_label, use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

# ── Input row ─────────────────────────────────────────────────────────────────
with st.form(key="research_form", border=False):
    inp_col, btn_col = st.columns([5, 1])
    with inp_col:
        topic = st.text_input(
            "Research topic",
            placeholder=st.session_state.current_placeholder,
            key="topic_input"
        )
    with btn_col:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        run_btn = st.form_submit_button("Run →", use_container_width=True, type="primary")

st.divider()

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([11, 4], gap="large")

with right:
    tracker_ph = st.empty()

with left:
    hint_ph     = st.empty()
    topic_ph    = st.empty()
    search_ph   = st.empty()
    scrape_ph   = st.empty()
    report_ph   = st.empty()
    feedback_ph = st.empty()
    download_ph = st.empty()


# ── Pipeline Execution & Rendering ────────────────────────────────────────────

if run_btn:
    if not topic.strip():
        with left:
            hint_ph.warning("Please enter a topic first.")
        st.stop()

    # Reset state for new run
    st.session_state.pipeline_state = {
        "status": "running",
        "topic": topic,
        "search_text": "",
        "scraped_text": "",
        "report": "",
        "feedback": ""
    }

    with left:
        hint_ph.empty()
        topic_ph.markdown(
            f'<div class="v-chip">✦ {topic}</div>',
            unsafe_allow_html=True,
        )

    # Step 1 — Search
    tracker_ph.markdown(tracker_html(1), unsafe_allow_html=True)
    with left:
        with st.spinner("Search agent scanning the web…"):
            from agents import build_search_agent
            search_agent = build_search_agent()
            res = search_agent.invoke({
                "messages": [
                    HumanMessage(
                        content=f"Find recent, reliable, and detailed information about: {topic}"
                    )
                ]
            })
        search_text = extract_text(res["messages"][-1].content)
        st.session_state.pipeline_state["search_text"] = search_text
        with search_ph.expander("🔍  Search Results", expanded=False):
            st.markdown(search_text)

    # Step 2 — Scrape
    tracker_ph.markdown(tracker_html(2), unsafe_allow_html=True)
    with left:
        with st.spinner("Reader agent scraping top resource…"):
            from agents import build_scrape_agent
            reader_agent = build_scrape_agent()
            res2 = reader_agent.invoke({
                "messages": [
                    HumanMessage(
                        content=(
                            f"Based on the following search results about '{topic}', "
                            f"select the most relevant and credible URL, then scrape it for deeper insights.\n\n"
                            f"Search Results:\n{search_text[:500]}"
                        )
                    )
                ]
            })
        scraped_text = extract_text(res2["messages"][-1].content)
        st.session_state.pipeline_state["scraped_text"] = scraped_text
        with scrape_ph.expander("🌐  Scraped Content", expanded=False):
            st.markdown(scraped_text)

    # Step 3 — Write
    tracker_ph.markdown(tracker_html(3), unsafe_allow_html=True)
    with left:
        with st.spinner("Writer agent drafting the report…"):
            from agents import writer_chain
            combined = (
                f"SEARCH RESULTS:\n{search_text}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{scraped_text}"
            )
            report = extract_text(writer_chain.invoke({"topic": topic, "research": combined}))
        st.session_state.pipeline_state["report"] = report
        with report_ph.expander("📝  Report", expanded=True):
            st.markdown(report)

    # Step 4 — Critique
    tracker_ph.markdown(tracker_html(4), unsafe_allow_html=True)
    with left:
        with st.spinner("Critic agent reviewing the report…"):
            from agents import critic_chain
            feedback = extract_text(critic_chain.invoke({"report": report}))
        st.session_state.pipeline_state["feedback"] = feedback
        with feedback_ph.expander("💬  Critic Feedback", expanded=True):
            st.markdown(feedback)

    # Done - Save status
    st.session_state.pipeline_state["status"] = "done"
    tracker_ph.markdown(tracker_html(5), unsafe_allow_html=True)

    full_md = (
        f"# {topic}\n\n## Report\n{report}\n\n"
        f"## Critic Feedback\n{feedback}\n\n---\n"
        f"## Search Results\n{search_text}\n\n"
        f"## Scraped Content\n{scraped_text}"
    )
    with left:
        download_ph.download_button(
            "⬇️  Download report as Markdown",
            data=full_md,
            file_name=f"{topic[:40].replace(' ', '_')}.md",
            mime="text/markdown",
        )

# ── Render from State (if theme was toggled after running) ────────────────────
elif st.session_state.pipeline_state["status"] == "done":
    state = st.session_state.pipeline_state
    tracker_ph.markdown(tracker_html(5), unsafe_allow_html=True)
    
    with left:
        hint_ph.empty()
        topic_ph.markdown(
            f'<div class="v-chip">✦ {state["topic"]}</div>',
            unsafe_allow_html=True,
        )
        with search_ph.expander("🔍  Search Results", expanded=False):
            st.markdown(state["search_text"])
        with scrape_ph.expander("🌐  Scraped Content", expanded=False):
            st.markdown(state["scraped_text"])
        with report_ph.expander("📝  Report", expanded=True):
            st.markdown(state["report"])
        with feedback_ph.expander("💬  Critic Feedback", expanded=True):
            st.markdown(state["feedback"])
            
        full_md = (
            f"# {state['topic']}\n\n## Report\n{state['report']}\n\n"
            f"## Critic Feedback\n{state['feedback']}\n\n---\n"
            f"## Search Results\n{state['search_text']}\n\n"
            f"## Scraped Content\n{state['scraped_text']}"
        )
        download_ph.download_button(
            "⬇️  Download report as Markdown",
            data=full_md,
            file_name=f"{state['topic'][:40].replace(' ', '_')}.md",
            mime="text/markdown",
        )

# Render idle tracker if nothing is running or done
else:
    tracker_ph.markdown(tracker_html(0), unsafe_allow_html=True)
    with left:
        hint_ph.markdown(
            '<div class="v-hint">Enter a topic above and press '
            '<strong>Run →</strong> — outputs appear here as each agent finishes. '
            '<br><br><em>💡 Hint: Press <strong>Tab</strong> to quickly fill in the placeholder topic!</em></div>',
            unsafe_allow_html=True,
        )