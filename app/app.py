from __future__ import annotations

import base64
import sys
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from theme import apply_theme
from utils.content_loader import (
    PROFILE_IMAGE,
    ensure_initialized,
    inject_custom_css,
    load_content,
)
from utils.search import search
from utils.ui import badge, card, metric, tag


st.set_page_config(
    page_title="Jean Direl · Ingénieur IA & Data Scientist",
    page_icon="🤖",
    layout="wide",
)
p = apply_theme(default="Deep Navy Pro", show_toggle=True)


def main() -> None:
    ensure_initialized()
    inject_custom_css()
    content = load_content()

    st.sidebar.header("Navigation")
    st.sidebar.write("Pages disponibles via le menu Streamlit.")

    st.session_state.setdefault("search_query", "")
    query = st.sidebar.text_input(
        "Rechercher dans le site",
        value=st.session_state["search_query"],
        key="sidebar-search",
        placeholder="Mots-clés (ex: RAG, CamemBERT, IA...)",
    )
    st.session_state["search_query"] = query
    active_query = query.strip()

    if active_query:
        with st.container():
            st.markdown("### 🔍 Résultats de recherche")
            results = search(active_query, content)
            if not results:
                st.info("Aucun résultat trouvé. Essayez d'autres mots-clés.")
            for res in results:
                st.markdown(
                    f"- **{res['title']}** · {res['page_label']} — {res['excerpt']}"
                )

    render_home(content)


def render_home(content: Dict[str, Any]) -> None:
    profile = content.get("profile", {})
    projets: List[Dict[str, Any]] = content.get("projets", [])
    experiences: List[Dict[str, Any]] = content.get("experiences", [])

    photo_src = resolve_profile_photo(profile)
    hero_html = f"""
    <div class="hero">
        <img src="{photo_src}" alt="Portrait de {profile.get('nom', '')}">
        <div class="hero-content">
            <h1>{profile.get('nom', '')}</h1>
            <h2>{profile.get('headline', '')}</h2>
            <p>{profile.get('bio', '')}</p>
            <div class="hero-actions">
                <a href="mailto:{profile.get('email', '')}">✉️ Me contacter</a>
                <a href="{profile.get('linkedin', '')}" target="_blank">💼 LinkedIn</a>
                <a href="{profile.get('cv_pdf', '')}" download>📄 Télécharger le CV</a>
            </div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    st.markdown("### Indicateurs clés")
    stats_cols = st.columns(3)
    with stats_cols[0]:
        metric("Projets menés", f"{len(projets)}", "Sélection d'études IA & data")
    with stats_cols[1]:
        metric("Expériences", f"{len(experiences)}", "Rôles techniques & data")
    with stats_cols[2]:
        metric("Années d'apprentissage", f"{estimate_years(experiences)}+", "IA, Data & Télécoms")

    st.markdown("### Derniers projets")
    cols = st.columns(3)
    for col, project in zip(cols, projets[:3]):
        with col:
            tags_html = " ".join(
                tag(skill) for skill in project.get("competences", [])[:3]
            )
            card(
                title=project.get("titre", ""),
                subtitle=project.get("periode", ""),
                content="<br>".join(project.get("points", [])[:2]),
                footer=tags_html,
            )

    st.markdown("### Compétences phares")
    key_skills = content.get("competences", {}).get("data_ia", [])[:6]
    st.markdown(" ".join(badge(skill) for skill in key_skills), unsafe_allow_html=True)


def estimate_years(experiences: List[Dict[str, Any]]) -> int:
    import re

    years = []
    for xp in experiences:
        period = xp.get("periode", "")
        matches = re.findall(r"(20\d{2})", period)
        years.extend(int(match) for match in matches)
    if not years:
        return 1
    return max(1, max(years) - min(years) + 1)


def resolve_profile_photo(profile: Dict[str, Any]) -> str:
    photo_ref = profile.get("photo")
    candidates: List[Path] = []
    if isinstance(photo_ref, str) and photo_ref:
        ref_path = Path(photo_ref)
        if ref_path.is_absolute():
            candidates.append(ref_path)
        else:
            assets_dir = PROFILE_IMAGE.parent
            app_dir = assets_dir.parent
            candidates.extend(
                [
                    (assets_dir / ref_path).resolve(),
                    (app_dir / ref_path).resolve(),
                ]
            )
    candidates.append(PROFILE_IMAGE)

    for path in candidates:
        try:
            if path.exists():
                data = path.read_bytes()
                suffix = path.suffix.lower()
                mime = "image/png" if suffix == ".png" else "image/jpeg"
                b64 = base64.b64encode(data).decode("ascii")
                return f"data:{mime};base64,{b64}"
        except OSError:
            continue
    return ""


if __name__ == "__main__":
    main()
