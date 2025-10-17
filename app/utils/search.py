from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

import streamlit as st
from rapidfuzz import fuzz


def _iter_searchables(content: Dict[str, Any]) -> Iterable[Tuple[str, str, str, str]]:
    profile = content.get("profile", {})
    profile_text = " ".join(
        [
            profile.get("nom", ""),
            profile.get("email", ""),
            profile.get("linkedin", ""),
            " ".join(profile.get("interets", [])),
        ]
    )
    yield ("profile", profile.get("nom", "Profil"), profile_text, "Accueil")

    for diploma in content.get("formation", {}).get("diplomes", []):
        title = f"{diploma.get('intitule', '')} – {diploma.get('ecole', '')}"
        text = " ".join(
            [
                diploma.get("periode", ""),
                diploma.get("lieu", ""),
                " ".join(diploma.get("details", [])),
            ]
        )
        yield ("formation", title, text, "Formation")

    for cert in content.get("formation", {}).get("certifications", []):
        title = f"{cert.get('titre', '')} – {cert.get('organisme', '')}"
        text = " ".join(
            [
                cert.get("emission", ""),
                cert.get("expiration", ""),
                " ".join(cert.get("competences", [])),
            ]
        )
        yield ("formation", title, text, "Formation")

    for xp in content.get("experiences", []):
        title = f"{xp.get('poste', '')} – {xp.get('entreprise', '')}"
        text = " ".join(
            [
                xp.get("periode", ""),
                xp.get("lieu", ""),
                " ".join(xp.get("missions", [])),
                " ".join(xp.get("impacts", [])),
                " ".join(xp.get("tags", [])),
            ]
        )
        yield ("experiences", title, text, "Expériences")

    for project in content.get("projets", []):
        title = project.get("titre", "")
        text = " ".join(
            [
                project.get("periode", ""),
                " ".join(project.get("points", [])),
                " ".join(project.get("competences", [])),
            ]
        )
        yield ("projets", title, text, "Projets")

    for reco in content.get("recommandations", []):
        title = f"{reco.get('auteur', '')} – {reco.get('poste', '')}"
        text = " ".join([reco.get("resume", ""), " ".join(reco.get("points", []))])
        yield ("recommandations", title, text, "Recommandations")

    for category, skills in content.get("competences", {}).items():
        title = category.replace("_", " ").title()
        text = " ".join(skills)
        yield ("competences", title, text, "Compétences")


def search(query: str, content: Dict[str, Any], limit: int = 12) -> List[Dict[str, Any]]:
    if not query:
        return []
    query_norm = query.lower()
    candidates = []
    for page_key, title, text, page_label in _iter_searchables(content):
        haystack = f"{title} {text}".lower()
        score = fuzz.partial_ratio(query_norm, haystack)
        if score >= 60:
            candidates.append(
                {
                    "page_key": page_key,
                    "page_label": page_label,
                    "title": title,
                    "excerpt": text[:280] + ("…" if len(text) > 280 else ""),
                    "score": score,
                }
            )
    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates[:limit]


def display_results(query: str, page_key: str, content: Dict[str, Any]) -> None:
    if not query:
        return
    results = [res for res in search(query, content) if res["page_key"] == page_key]
    if not results:
        st.info("Aucun résultat pour cette page.")
        return
    for result in results:
        st.markdown(
            f"**{result['title']}** — {result['excerpt']}",
            unsafe_allow_html=False,
        )


__all__ = ["search", "display_results"]
