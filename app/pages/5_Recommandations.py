from __future__ import annotations

import streamlit as st

from utils.content_loader import ensure_initialized, inject_custom_css, load_content
from utils.search import display_results


def render_recommandations() -> None:
    ensure_initialized()
    inject_custom_css()
    content = load_content()

    st.title("🤝 Recommandations")

    query = st.session_state.get("search_query", "").strip()
    if query:
        st.markdown("#### Résultats liés à cette page")
        display_results(query, "recommandations", content)

    recommandations = content.get("recommandations", [])
    if not recommandations:
        st.info("Aucune recommandation disponible pour le moment.")
        return

    for reco in recommandations:
        points = "".join(f"<li>{point}</li>" for point in reco.get("points", []))
        st.markdown(
            f"""
            <div class="reco-card">
                <h3>{reco.get("auteur", "")}</h3>
                <p class="card-subtitle">{reco.get("poste", "")} · {reco.get("date", "")}</p>
                <p>{reco.get("resume", "")}</p>
                <ul>{points}</ul>
                <p><a href="mailto:{reco.get("contact", {}).get("email", "")}">Contacter par e-mail</a> · 
                <a href="tel:{reco.get("contact", {}).get("telephone", "")}">Téléphone</a></p>
            </div>
            """,
            unsafe_allow_html=True,
        )


render_recommandations()
