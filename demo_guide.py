"""Demo guide — auto-navigates the app and sets input values for presentation."""

import streamlit as st

# Each step: text (plain, no markdown), page index, highlight selector, and optional field values to set
STEPS = [
    # ── Scenario 1: Bill Shock ─────────────────────────────────────────────────
    {
        "scenario": "Scenario 1: Bill Shock",
        "text": "Aisyah opens the app and sees her latest bill EXCEEDS her RM 200 budget",
        "page": 0,
        "highlight": ".stAlert",
    },
    {
        "scenario": "Scenario 1: Bill Shock",
        "text": "KPIs: Latest Bill RM 278.79 | Budget RM 200 | Status: Over",
        "page": 0,
        "highlight": "[data-testid='stMetric']",
    },
    {
        "scenario": "Scenario 1: Bill Shock",
        "text": "Bill history chart — clear spike over the last 3 months",
        "page": 0,
        "highlight": "[data-testid='stPlotlyChart']",
    },
    {
        "scenario": "Scenario 1: Bill Shock",
        "text": "Expand 'Understand Your Bill' — tiered breakdown Blocks 1 to 4",
        "page": 0,
        "highlight": "[data-testid='stExpander']",
    },
    {
        "scenario": "Scenario 1: Bill Shock",
        "text": "Usage Analysis: peak hours 12:00–20:00, AC running all afternoon",
        "page": 2,
        "highlight": "[data-testid='stPlotlyChart']",
    },
    {
        "scenario": "Scenario 1: Bill Shock",
        "text": "Personalized recommendations with savings: AC tip RM 15-30, standby RM 8-15",
        "page": 2,
        "highlight": "[data-testid='stMetric']",
    },

    # ── Scenario 2: AC Upgrade Decision ────────────────────────────────────────
    {
        "scenario": "Scenario 2: AC Upgrade",
        "text": "Aisyah checks if upgrading her old 2018 AC is worth it",
        "page": 3,
        "highlight": "[data-testid='stSelectbox']",
        "values": {"appliance_type": "air_conditioner"},
    },
    {
        "scenario": "Scenario 2: AC Upgrade",
        "text": "Her usage: 10 hours/day at 1500W (old 3-star unit)",
        "page": 3,
        "highlight": "[data-testid='stSlider'], [data-testid='stNumberInput']",
        "values": {"hours": 10.0, "current_watts": 1500.0},
    },
    {
        "scenario": "Scenario 2: AC Upgrade",
        "text": "Comparison: current cost vs efficient 5-star inverter model",
        "page": 3,
        "highlight": "[data-testid='stMetric']",
    },
    {
        "scenario": "Scenario 2: AC Upgrade",
        "text": "Yearly savings — new AC pays for itself in about 3 years",
        "page": 3,
        "highlight": "[data-testid='stPlotlyChart']",
    },
    {
        "scenario": "Scenario 2: AC Upgrade",
        "text": "SAVE 4.0 rebate: RM 200 off any 5-star AC — Eligible!",
        "page": 3,
        "highlight": ".stSuccess",
    },

    # ── Scenario 3: Bahasa Malaysia ────────────────────────────────────────────
    {
        "scenario": "Scenario 3: Bahasa Malaysia",
        "text": "Mother-in-law prefers BM — switch language to Bahasa Malaysia",
        "page": 4,
        "highlight": "[data-testid='stForm']",
        "values": {"language": "ms"},
    },
    {
        "scenario": "Scenario 3: Bahasa Malaysia",
        "text": "Entire UI updates — menu, titles, alerts all in Bahasa Malaysia",
        "page": 4,
        "highlight": "[data-testid='stSidebar']",
    },
    {
        "scenario": "Scenario 3: Bahasa Malaysia",
        "text": "Enter bill: 650 kWh for May 2026 — auto-calculates RM 278.79",
        "page": 1,
        "highlight": "[data-testid='stForm']",
        "values": {"bill_month": "2026-05", "bill_kwh": 650.0},
    },
    {
        "scenario": "Scenario 3: Bahasa Malaysia",
        "text": "Save — alert appears: 'Bil ini melebihi bajet anda'",
        "page": 1,
        "highlight": "[data-testid='stFormSubmitButton'], .stAlert",
    },
]


def init_demo_state():
    if "demo_active" not in st.session_state:
        st.session_state.demo_active = False
    if "demo_step" not in st.session_state:
        st.session_state.demo_step = 0


def render_toggle(lang):
    init_demo_state()
    label = "Demo Mode" if lang == "en" else "Mod Demo"
    st.sidebar.toggle(f"🎬 {label}", key="demo_active")


def get_target_page():
    """Return which page index the demo currently wants to show."""
    if not st.session_state.get("demo_active", False):
        return None
    step_idx = st.session_state.demo_step
    if step_idx < len(STEPS):
        return STEPS[step_idx]["page"]
    return None


def get_demo_values():
    """Return the current step's field values dict, or empty dict."""
    if not st.session_state.get("demo_active", False):
        return {}
    step_idx = st.session_state.get("demo_step", 0)
    if step_idx < len(STEPS):
        return STEPS[step_idx].get("values", {})
    return {}


def render_nav():
    """Render Prev/Next in sidebar."""
    if not st.session_state.get("demo_active", False):
        return

    step_idx = st.session_state.demo_step
    current = STEPS[min(step_idx, len(STEPS) - 1)]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"📍 {current['scenario']}")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("◀ Prev", key="demo_prev", use_container_width=True):
            if st.session_state.demo_step > 0:
                st.session_state.demo_step -= 1
            st.rerun()

    with col2:
        if st.button("Next ▶", key="demo_next", use_container_width=True):
            if st.session_state.demo_step < len(STEPS) - 1:
                st.session_state.demo_step += 1
            st.rerun()

    st.sidebar.progress((step_idx + 1) / len(STEPS))
    st.sidebar.caption(f"Step {step_idx + 1} / {len(STEPS)}")


def render_overlay():
    """Render the floating card and element highlight CSS."""
    if not st.session_state.get("demo_active", False):
        return

    step_idx = st.session_state.demo_step
    if step_idx >= len(STEPS):
        return

    current = STEPS[step_idx]
    scenario_name = current["scenario"]
    step_text = current["text"]
    selector = current.get("highlight", "")

    highlight_css = ""
    if selector:
        highlight_css = f"""
        {selector} {{
            outline: 3px solid #4fc3f7 !important;
            outline-offset: 4px !important;
            border-radius: 8px !important;
            animation: demo-pulse 1.5s ease-in-out infinite !important;
            position: relative !important;
            z-index: 1 !important;
        }}
        """

    st.markdown(f"""
    <style>
    @keyframes demo-pulse {{
        0%, 100% {{ outline-color: #4fc3f7; box-shadow: 0 0 8px rgba(79, 195, 247, 0.3); }}
        50% {{ outline-color: #81d4fa; box-shadow: 0 0 24px rgba(79, 195, 247, 0.6); }}
    }}
    {highlight_css}
    .demo-overlay {{
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 360px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #ffffff;
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        border: 1px solid rgba(79, 195, 247, 0.3);
    }}
    .demo-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }}
    .demo-badge {{
        font-size: 10px;
        font-weight: 700;
        color: #4fc3f7;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .demo-counter {{
        font-size: 11px;
        color: #666;
    }}
    .demo-scenario {{
        font-size: 13px;
        font-weight: 600;
        color: #aaa;
        margin-bottom: 8px;
    }}
    .demo-step {{
        font-size: 15px;
        line-height: 1.6;
        color: #e0e0e0;
        padding: 12px 14px;
        background: rgba(79, 195, 247, 0.08);
        border-radius: 8px;
        border-left: 3px solid #4fc3f7;
    }}
    </style>
    <div class="demo-overlay">
        <div class="demo-header">
            <span class="demo-badge">🎬 Demo Guide</span>
            <span class="demo-counter">{step_idx + 1} / {len(STEPS)}</span>
        </div>
        <div class="demo-scenario">{scenario_name}</div>
        <div class="demo-step">{step_text}</div>
    </div>
    """, unsafe_allow_html=True)
