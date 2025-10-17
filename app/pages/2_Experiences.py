from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from theme import apply_theme

from utils.content_loader import ensure_initialized, inject_custom_css, load_content
from utils.search import display_results

p = apply_theme(default="Deep Navy Pro", show_toggle=True)


def render_experiences() -> None:
    ensure_initialized()
    inject_custom_css()
    content = load_content()
    st.title("🚀 Expériences professionnelles")

    query = st.session_state.get("search_query", "").strip()
    if query:
        st.markdown("#### Résultats liés à cette page")
        display_results(query, "experiences", content)

    experiences = content.get("experiences", [])
    entreprises = sorted({xp.get("entreprise", "") for xp in experiences})
    all_tags = sorted({tag for xp in experiences for tag in xp.get("tags", [])})

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        selected_entreprises = st.multiselect(
            "Filtrer par entreprise",
            options=entreprises,
            default=entreprises,
        )
    with col_filter2:
        selected_tags = st.multiselect(
            "Filtrer par tags",
            options=all_tags,
        )

    filtered = []
    for xp in experiences:
        in_company = xp.get("entreprise") in selected_entreprises if selected_entreprises else True
        tags = xp.get("tags", [])
        in_tags = True
        if selected_tags:
            in_tags = any(tag in selected_tags for tag in tags)
        if in_company and in_tags:
            filtered.append(xp)

    if not filtered:
        st.info("Aucune expérience ne correspond aux filtres sélectionnés.")
        return

    for xp in filtered:
        tags_html = " ".join(f"<span class='ui-tag'>{tag}</span>" for tag in xp.get("tags", []))
        missions_list = "".join(f"<li>{mission}</li>" for mission in xp.get("missions", []))
        impacts_list = "".join(f"<li>{impact}</li>" for impact in xp.get("impacts", []))
        st.markdown(
            f"""
            <div class="ui-card">
                <h3>{xp.get("poste", "")}</h3>
                <p class="card-subtitle">{xp.get("entreprise", "")} · {xp.get("lieu", "")}</p>
                <p><strong>Période :</strong> {xp.get("periode", "")}</p>
                <div class="chips">{tags_html}</div>
                <h4>Missions</h4>
                <ul>{missions_list}</ul>
                <h4>Impact</h4>
                <ul>{impacts_list}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


render_experiences()
