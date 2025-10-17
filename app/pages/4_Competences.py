from __future__ import annotations

from collections import OrderedDict

import streamlit as st

from utils.content_loader import ensure_initialized, inject_custom_css, load_content
from utils.search import display_results
from utils.ui import tag


CATEGORY_META = OrderedDict(
    [
        ("data_ia", {"label": "Data IA", "icon": "🧠"}),
        ("langages_frameworks", {"label": "Langages & Frameworks", "icon": "💻"}),
        ("data_engineering_bi", {"label": "Data Engineering & BI", "icon": "🛠️"}),
        ("web", {"label": "Web", "icon": "🌐"}),
        ("outils_ops", {"label": "Outils & Ops", "icon": "⚙️"}),
        ("secteurs", {"label": "Secteurs", "icon": "🏢"}),
        ("softskills", {"label": "Soft Skills", "icon": "🤝"}),
    ]
)


def render_competences() -> None:
    ensure_initialized()
    inject_custom_css()
    content = load_content()

    st.title("🧰 Compétences")

    query = st.session_state.get("search_query", "").strip()
    if query:
        st.markdown("#### Résultats liés à cette page")
        display_results(query, "competences", content)

    local_query = st.text_input(
        "Recherche locale dans les compétences",
        placeholder="Ex : Docker, Gestion de projet...",
    ).strip()
    local_query_norm = local_query.lower()

    competences = content.get("competences", {})
    cards_html = []
    for key, meta in CATEGORY_META.items():
        items = competences.get(key, [])
        filtered_items = (
            [item for item in items if local_query_norm in item.lower()]
            if local_query_norm
            else items
        )
        if not filtered_items:
            continue

        count = len(filtered_items)
        tags_html = " ".join(tag(item) for item in filtered_items)
        cards_html.append(
            (
                "<article class='ui-card skill-card'>"
                "<header class='skill-card-header'>"
                f"<div class='skill-icon'>{meta.get('icon', '📌')}</div>"
                "<div>"
                f"<h3>{meta.get('label', key.replace('_', ' ').title())}</h3>"
                f"<p class='skill-count'>{count} compétence{'s' if count > 1 else ''}</p>"
                "</div>"
                "</header>"
                f"<div class='skill-tags'>{tags_html}</div>"
                "</article>"
            )
        )

    if not cards_html:
        st.info("Aucune compétence ne correspond à votre recherche.")
        return

    st.markdown(
        "<div class='skills-grid'>" + "".join(cards_html) + "</div>",
        unsafe_allow_html=True,
    )


render_competences()
