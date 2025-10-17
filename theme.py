from __future__ import annotations

import altair as alt
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


PALETTES = {
    "Deep Navy Pro": {
        "bg": "#0B1220",
        "bg2": "#0F1A2B",
        "bg3": "#132235",
        "text": "#E5E7EB",
        "titles": "#F8FAFC",
        "muted": "#9CA3AF",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "link": "#93C5FD",
        "ok": "#10B981",
        "warn": "#F59E0B",
        "err": "#EF4444",
        "border": "rgba(255,255,255,0.06)",
        "shadow": "0 8px 24px rgba(0,0,0,0.25)",
    },
    "Petrol Teal": {
        "bg": "#0B1220",
        "bg2": "#0E1B2A",
        "bg3": "#122235",
        "text": "#E5E7EB",
        "titles": "#F8FAFC",
        "muted": "#9CA3AF",
        "accent": "#14B8A6",
        "accent_hover": "#0EA5A4",
        "link": "#5EEAD4",
        "ok": "#10B981",
        "warn": "#F59E0B",
        "err": "#EF4444",
        "border": "rgba(255,255,255,0.06)",
        "shadow": "0 8px 24px rgba(0,0,0,0.25)",
    },
    "Light Pro": {
        "bg": "#FFFFFF",
        "bg2": "#F5F7FB",
        "bg3": "#EEF2F7",
        "text": "#1F2937",
        "titles": "#0F172A",
        "muted": "#6B7280",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "link": "#2563EB",
        "ok": "#059669",
        "warn": "#D97706",
        "err": "#DC2626",
        "border": "#E5E7EB",
        "shadow": "0 8px 24px rgba(0,0,0,0.06)",
    },
}


def apply_theme(default: str = "Deep Navy Pro", show_toggle: bool = True) -> dict:
    """Apply the selected palette and configure global theming."""
    if "theme" not in st.session_state:
        st.session_state.theme = default
    if show_toggle:
        st.session_state.theme = st.sidebar.radio(
            "Thème",
            list(PALETTES.keys()),
            index=list(PALETTES.keys()).index(st.session_state.theme),
        )
    palette = PALETTES[st.session_state.theme]

    st.markdown(
        f"""
    <style>
    :root {{
      --bg:{palette['bg']}; --bg2:{palette['bg2']}; --bg3:{palette['bg3']};
      --text:{palette['text']}; --titles:{palette['titles']}; --muted:{palette['muted']};
      --accent:{palette['accent']}; --accentH:{palette['accent_hover']}; --link:{palette['link']};
      --ok:{palette['ok']}; --warn:{palette['warn']}; --err:{palette['err']};
      --border:{palette['border']};
    }}
    html, body, .stApp {{ background:var(--bg); color:var(--text); }}
    .block-container {{ padding-top: 1.25rem; }}

    h1,h2,h3,h4,h5,h6 {{ color:var(--titles) !important; letter-spacing:.2px; }}
    p,li,span,small {{ color:var(--text); line-height:1.6; }}
    .muted, .small, .markdown-text-container p em {{ color:var(--muted) !important; }}

    a {{ color:var(--link) !important; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}

    [data-testid="stSidebar"] {{
      background: linear-gradient(180deg, var(--bg) 0%, var(--bg2) 100%);
      border-right: 1px solid var(--border);
    }}
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{ color:var(--titles) !important; }}
    [data-testid="stSidebarNav"] li a {{
      display:flex; align-items:center; gap:.5rem;
      color:var(--text) !important; padding:.55rem .8rem; border-radius:12px;
      border:1px solid transparent; transition: all .15s ease; background:transparent;
    }}
    [data-testid="stSidebarNav"] li a:hover {{ background: rgba(255,255,255,0.035); border-color: var(--border); }}
    [data-testid="stSidebarNav"] li a[aria-current="page"] {{
      color: var(--titles) !important; font-weight: 600;
      background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(0,0,0,0.06));
      border-color: rgba(255,255,255,0.08);
      box-shadow: 0 1px 0 rgba(255,255,255,0.06) inset, 0 6px 14px rgba(0,0,0,0.35);
    }}
    [data-testid="stSidebarNav"] li a[aria-current="page"]::before {{
      content:""; width:8px; height:8px; border-radius:999px; margin-right:.25rem;
      background: var(--accent); box-shadow: 0 0 0 3px rgba(37,99,235,0.18);
    }}

    .section, .stMarkdown div > div, .stContainer > div > div {{
      background: linear-gradient(135deg, var(--bg2) 0%, var(--bg) 80%);
      border: 1px solid var(--border); border-radius: 18px; padding: 18px 22px;
      box-shadow: {palette['shadow']};
    }}
    .hero {{
      background: radial-gradient(1200px 600px at 10% -20%, rgba(255,255,255,.06), transparent),
                  linear-gradient(135deg, var(--bg3), var(--bg2));
      border:1px solid var(--border); border-radius:24px; padding:28px 28px 24px;
      box-shadow:{palette['shadow']};
    }}

    div.stButton > button {{
      background: var(--accent); color:#fff; border:0; border-radius:999px;
      padding:.6rem 1.1rem; font-weight:600;
    }}
    div.stButton > button:hover {{ background: var(--accentH); }}

    .badge {{ background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:.25rem .6rem; }}
    .badge--ok {{ background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.35); }}
    .badge--warn {{ background: rgba(245,158,11,0.14); border-color: rgba(245,158,11,0.35); }}
    .badge--err {{ background: rgba(239,68,68,0.14); border-color: rgba(239,68,68,0.35); }}

    input, textarea, select {{ background:var(--bg2) !important; color:var(--text) !important; border:1px solid var(--border) !important; border-radius:10px !important; }}

    [data-testid="stTable"], .stDataFrame {{ border:1px solid var(--border); border-radius:12px; overflow:hidden; }}
    table {{ color:var(--text); }}
    thead th {{ background:var(--bg3) !important; color:var(--titles) !important; }}

    .stTabs [data-baseweb="tab"] {{ color:var(--text); }}
    .stTabs [aria-selected="true"] {{ color:var(--titles); border-bottom:3px solid var(--accent); }}

    a:focus, button:focus {{ outline:2px solid var(--link); outline-offset:2px; border-radius:10px; }}

    ::-webkit-scrollbar {{ width: 10px; height:10px; }}
    ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 10px; border:2px solid var(--bg); }}
    ::-webkit-scrollbar-track {{ background: var(--bg); }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    pio.templates["site"] = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor=palette["bg"],
            plot_bgcolor=palette["bg2"],
            font=dict(color=palette["text"]),
            colorway=[
                palette["accent"],
                palette["link"],
                "#F59E0B",
                "#10B981",
                "#F472B6",
            ],
        )
    )
    pio.templates.default = "site"

    def _alt() -> dict:
        return {
            "config": {
                "background": palette["bg"],
                "view": {"fill": palette["bg2"]},
                "title": {"color": palette["titles"]},
                "axis": {"labelColor": palette["text"], "titleColor": palette["text"]},
                "legend": {
                    "labelColor": palette["text"],
                    "titleColor": palette["text"],
                },
                "range": {
                    "category": [
                        palette["accent"],
                        palette["link"],
                        "#F59E0B",
                        "#10B981",
                        "#F472B6",
                    ]
                },
            }
        }

    alt.themes.register("site", _alt)
    alt.themes.enable("site")
    return palette
