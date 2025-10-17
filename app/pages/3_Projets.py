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
from utils.ui import tag

p = apply_theme(default="Deep Navy Pro", show_toggle=True)


def render_projets() -> None:
    ensure_initialized()
    inject_custom_css()
    content = load_content()
    st.title("🚀 Projets IA & Data")

    query = st.session_state.get("search_query", "").strip()
    if query:
        st.markdown("#### Résultats liés à cette page")
        display_results(query, "projets", content)

    projets = content.get("projets", [])
    toutes_competences = sorted(
        {skill for proj in projets for skill in proj.get("competences", [])}
    )
    selection = st.multiselect(
        "Filtrer par compétences/tags",
        options=toutes_competences,
    )

    filtered = []
    for proj in projets:
        competences = proj.get("competences", [])
        if selection and not any(skill in competences for skill in selection):
            continue
        filtered.append(proj)

    if not filtered:
        st.info("Aucun projet ne correspond aux filtres sélectionnés.")
        return

    project_cards = []
    for proj in filtered:
        tags_html = " ".join(tag(skill) for skill in proj.get("competences", []))
        image_html = ""
        if proj.get("image"):
            image_html = (
                "<div class='project-thumb'>"
                f"<img src='{proj['image']}' alt='{proj.get('titre', '')}'>"
                "</div>"
            )
        project_cards.append(
            (
                "<article class='ui-card project-card'>"
                f"{image_html}"
                f"<h3>{proj.get('titre', '')}</h3>"
                f"<p class='card-subtitle'>{proj.get('periode', '')}</p>"
                "<div class='card-body'>"
                + "<br>".join(proj.get("points", []))
                + "</div>"
                f"<div class='chips project-chips'>{tags_html}</div>"
                "</article>"
            )
        )

    st.markdown(
        "<div class='project-grid'>" + "".join(project_cards) + "</div>",
        unsafe_allow_html=True,
    )


render_projets()
