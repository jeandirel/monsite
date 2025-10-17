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
from utils.ui import badge, timeline

p = apply_theme(default="Deep Navy Pro", show_toggle=True)


def render_formation() -> None:
    ensure_initialized()
    inject_custom_css()
    content = load_content()

    st.title("🎓 Formation & certifications")

    query = st.session_state.get("search_query", "").strip()
    if query:
        st.markdown("#### Résultats liés à cette page")
        display_results(query, "formation", content)

    diplomes = content.get("formation", {}).get("diplomes", [])
    timeline(
        {
            "title": diploma.get("intitule", ""),
            "subtitle": diploma.get("ecole", ""),
            "period": " · ".join(
                element
                for element in (
                    diploma.get("periode", ""),
                    diploma.get("lieu", ""),
                )
                if element
            ),
            "details": diploma.get("details", []),
        }
        for diploma in diplomes
    )

    st.markdown("### Certifications")
    certifications = content.get("formation", {}).get("certifications", [])
    if not certifications:
        st.info("Aucune certification renseignée pour le moment.")
        return

    cards_html = []
    for cert in certifications:
        skills_html = " ".join(badge(skill) for skill in cert.get("competences", []))
        expiration = cert.get("expiration", "")
        expiration_html = (
            f"<p><strong>Expiration :</strong> {expiration}</p>"
            if expiration
            else ""
        )
        cards_html.append(
            (
                "<article class='ui-card cert-card'>"
                f"<h3>{cert.get('titre', '')}</h3>"
                f"<p class='card-subtitle'>{cert.get('organisme', '')}</p>"
                "<div class='cert-card-meta'>"
                f"<p><strong>Émission :</strong> {cert.get('emission', '')}</p>"
                f"{expiration_html}"
                "</div>"
                f"<div class='chips cert-chips'>{skills_html}</div>"
                "</article>"
            )
        )

    st.markdown(
        "<div class='cert-grid'>" + "".join(cards_html) + "</div>",
        unsafe_allow_html=True,
    )


render_formation()
