from __future__ import annotations

import io
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List

import pandas as pd
import streamlit as st
from slugify import slugify

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from theme import apply_theme

from utils import auth
from utils.content_loader import (
    PROFILE_IMAGE,
    PROFILE_PDF,
    ensure_initialized,
    inject_custom_css,
    load_content,
    load_messages,
    save_content,
    save_messages,
)
from utils.storage import ASSETS_DIR, UPLOADS_DIR, uuid_str


p = apply_theme(default="Deep Navy Pro", show_toggle=True)

def rerun() -> None:
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()


def admin_page() -> None:
    ensure_initialized()
    inject_custom_css()
    st.title("🔐 Administration du site")

    if not auth.is_authenticated():
        if not auth.login_form():
            return
        rerun()

    if st.sidebar.button("Se déconnecter"):
        auth.logout()
        rerun()

    content = load_content()
    messages = load_messages()

    tabs = st.tabs(
        [
            "Profil",
            "Formation",
            "Expériences",
            "Projets",
            "Compétences",
            "Recommandations",
            "Messages",
            "Fichiers",
            "Paramètres",
            "Sauvegarde & Restauration",
        ]
    )

    with tabs[0]:
        manage_profile(content)
    with tabs[1]:
        manage_formation(content)
    with tabs[2]:
        manage_experiences(content)
    with tabs[3]:
        manage_projects(content)
    with tabs[4]:
        manage_skills(content)
    with tabs[5]:
        manage_recommendations(content)
    with tabs[6]:
        manage_messages(messages)
    with tabs[7]:
        manage_files()
    with tabs[8]:
        manage_settings()
    with tabs[9]:
        manage_backup(content)


def persist_content(content: Dict) -> None:
    save_content(content)
    st.success("Contenu enregistré.")
    rerun()


def manage_profile(content: Dict) -> None:
    st.subheader("Profil public")
    profile = content.get("profile", {})
    with st.form("profile-form"):
        nom = st.text_input("Nom complet", value=profile.get("nom", ""))
        headline = st.text_input("Titre / headline", value=profile.get("headline", ""))
        email = st.text_input("Email", value=profile.get("email", ""))
        telephone = st.text_input("Téléphone", value=profile.get("telephone", ""))
        linkedin = st.text_input("Lien LinkedIn", value=profile.get("linkedin", ""))
        anniversaire_str = profile.get("anniversaire", "1997-07-14")
        anniversaire_dt = pd.to_datetime(anniversaire_str, errors="coerce")
        if pd.isna(anniversaire_dt):
            anniversaire_dt = pd.Timestamp("1997-07-14")
        anniversaire = st.date_input("Anniversaire", value=anniversaire_dt.date())
        adresses = st.text_area(
            "Adresses (une par ligne)",
            value="\n".join(profile.get("adresses", [])),
        )
        interets = st.text_area(
            "Centres d'intérêt (une ligne par élément)",
            value="\n".join(profile.get("interets", [])),
        )
        bio = st.text_area("Bio courte", value=profile.get("bio", ""), height=150)
        photo = st.file_uploader("Photo de profil (jpg/png)", type=["jpg", "jpeg", "png"])
        cv_pdf = st.file_uploader("CV (PDF)", type=["pdf"])
        submitted = st.form_submit_button("Enregistrer le profil")

    if not submitted:
        return

    updated_profile = {
        "nom": nom,
        "headline": headline,
        "email": email,
        "telephone": telephone,
        "linkedin": linkedin,
        "anniversaire": anniversaire.strftime("%Y-%m-%d")
        if isinstance(anniversaire, date)
        else anniversaire_dt.strftime("%Y-%m-%d"),
        "adresses": [addr.strip() for addr in adresses.splitlines() if addr.strip()],
        "interets": [line.strip() for line in interets.splitlines() if line.strip()],
        "photo": profile.get("photo", "assets/profile.jpg"),
        "cv_pdf": profile.get("cv_pdf", "assets/cv_jean_direl.pdf"),
        "bio": bio,
    }

    if photo is not None:
        photo_bytes = photo.getvalue()
        ext = Path(photo.name or "").suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png"}:
            ext = ".jpg"
        filename = f"profile-{uuid_str()}{ext}"
        destination = UPLOADS_DIR / filename
        destination.write_bytes(photo_bytes)
        PROFILE_IMAGE.write_bytes(photo_bytes)

        old_photo_ref = profile.get("photo", "")
        if old_photo_ref:
            old_path = Path(old_photo_ref)
            if not old_path.is_absolute():
                old_path = ASSETS_DIR / old_photo_ref
            if (
                old_path.exists()
                and old_path.parent == UPLOADS_DIR
                and old_path.name != filename
            ):
                old_path.unlink(missing_ok=True)
        updated_profile["photo"] = f"uploads/{filename}"

    if cv_pdf is not None:
        pdf_bytes = cv_pdf.getvalue()
        PROFILE_PDF.write_bytes(pdf_bytes)
        updated_profile["cv_pdf"] = "assets/cv_jean_direl.pdf"

    content["profile"] = updated_profile
    persist_content(content)


def manage_formation(content: Dict) -> None:
    st.subheader("Diplômes")
    diplomes = content.setdefault("formation", {}).setdefault("diplomes", [])

    add_diplome(diplomes, content)

    if diplomes:
        select = st.selectbox(
            "Sélectionner un diplôme",
            options=diplomes,
            format_func=lambda d: d.get("intitule", "")[:60],
        )
        if select:
            with st.form(f"edit-diplome-{select['id']}"):
                ecole = st.text_input("École", value=select.get("ecole", ""))
                intitule = st.text_input("Intitulé", value=select.get("intitule", ""))
                periode = st.text_input("Période", value=select.get("periode", ""))
                lieu = st.text_input("Lieu", value=select.get("lieu", ""))
                details = st.text_area(
                    "Détails (une ligne par élément)",
                    value="\n".join(select.get("details", [])),
                )
                save_btn = st.form_submit_button("Mettre à jour")
            delete_btn = st.button("Supprimer ce diplôme", key=f"delete-diplome-{select['id']}")
            if save_btn:
                select.update(
                    {
                        "ecole": ecole,
                        "intitule": intitule,
                        "periode": periode,
                        "lieu": lieu,
                        "details": [line.strip() for line in details.splitlines() if line.strip()],
                    }
                )
                persist_content(content)
            if delete_btn:
                diplomes[:] = [d for d in diplomes if d.get("id") != select["id"]]
                persist_content(content)

    st.markdown("---")
    st.subheader("Certifications")
    certifications = content.setdefault("formation", {}).setdefault("certifications", [])
    add_certification(certifications, content)
    if certifications:
        cert = st.selectbox(
            "Sélectionner une certification",
            options=certifications,
            format_func=lambda c: c.get("titre", "")[:60],
        )
        if cert:
            with st.form(f"edit-cert-{cert['id']}"):
                organisme = st.text_input("Organisme", value=cert.get("organisme", ""))
                titre = st.text_input("Titre", value=cert.get("titre", ""))
                emission = st.text_input("Date d'émission", value=cert.get("emission", ""))
                expiration = st.text_input("Date d'expiration", value=cert.get("expiration", ""))
                competences = st.text_area(
                    "Compétences (une par ligne)",
                    value="\n".join(cert.get("competences", [])),
                )
                save_btn = st.form_submit_button("Mettre à jour")
            delete_btn = st.button("Supprimer cette certification", key=f"delete-cert-{cert['id']}")
            if save_btn:
                cert.update(
                    {
                        "organisme": organisme,
                        "titre": titre,
                        "emission": emission,
                        "expiration": expiration,
                        "competences": [c.strip() for c in competences.splitlines() if c.strip()],
                    }
                )
                persist_content(content)
            if delete_btn:
                certifications[:] = [c for c in certifications if c.get("id") != cert["id"]]
                persist_content(content)


def add_diplome(diplomes: List[Dict], content: Dict) -> None:
    with st.form("add-diplome", clear_on_submit=True):
        st.write("Ajouter un diplôme")
        ecole = st.text_input("École *")
        intitule = st.text_input("Intitulé *")
        periode = st.text_input("Période *")
        lieu = st.text_input("Lieu *")
        details = st.text_area("Détails (une ligne par élément)")
        submitted = st.form_submit_button("Ajouter")
    if submitted:
        if not ecole or not intitule:
            st.error("Les champs École et Intitulé sont obligatoires.")
        else:
            diplomes.append(
                {
                    "id": uuid_str(),
                    "ecole": ecole,
                    "intitule": intitule,
                    "periode": periode,
                    "lieu": lieu,
                    "details": [line.strip() for line in details.splitlines() if line.strip()],
                }
            )
            persist_content(content)


def add_certification(certifications: List[Dict], content: Dict) -> None:
    with st.form("add-certification", clear_on_submit=True):
        st.write("Ajouter une certification")
        organisme = st.text_input("Organisme *")
        titre = st.text_input("Titre *")
        emission = st.text_input("Date d'émission")
        expiration = st.text_input("Date d'expiration")
        competences = st.text_area("Compétences (une par ligne)")
        submitted = st.form_submit_button("Ajouter")
    if submitted:
        if not organisme or not titre:
            st.error("Les champs Organisme et Titre sont obligatoires.")
        else:
            certifications.append(
                {
                    "id": uuid_str(),
                    "organisme": organisme,
                    "titre": titre,
                    "emission": emission,
                    "expiration": expiration,
                    "competences": [c.strip() for c in competences.splitlines() if c.strip()],
                }
            )
            persist_content(content)


def manage_experiences(content: Dict) -> None:
    st.subheader("Gestion des expériences")
    experiences = content.setdefault("experiences", [])
    with st.form("add-experience", clear_on_submit=True):
        st.write("Ajouter une expérience")
        poste = st.text_input("Poste *")
        entreprise = st.text_input("Entreprise *")
        lieu = st.text_input("Lieu")
        periode = st.text_input("Période")
        missions = st.text_area("Missions (une par ligne)")
        impacts = st.text_area("Impacts (une par ligne)")
        tags = st.text_input("Tags (séparés par des virgules)")
        submitted = st.form_submit_button("Ajouter")
    if submitted:
        if not poste or not entreprise:
            st.error("Poste et Entreprise sont obligatoires.")
        else:
            experiences.append(
                {
                    "id": uuid_str(),
                    "poste": poste,
                    "entreprise": entreprise,
                    "lieu": lieu,
                    "periode": periode,
                    "missions": [m.strip() for m in missions.splitlines() if m.strip()],
                    "impacts": [i.strip() for i in impacts.splitlines() if i.strip()],
                    "tags": [t.strip() for t in tags.split(",") if t.strip()],
                }
            )
            persist_content(content)

    if experiences:
        xp = st.selectbox(
            "Sélectionner une expérience",
            options=experiences,
            format_func=lambda x: f"{x.get('poste', '')} · {x.get('entreprise', '')}"[:60],
        )
        if xp:
            with st.form(f"edit-xp-{xp['id']}"):
                poste = st.text_input("Poste", value=xp.get("poste", ""))
                entreprise = st.text_input("Entreprise", value=xp.get("entreprise", ""))
                lieu = st.text_input("Lieu", value=xp.get("lieu", ""))
                periode = st.text_input("Période", value=xp.get("periode", ""))
                missions = st.text_area("Missions", value="\n".join(xp.get("missions", [])))
                impacts = st.text_area("Impacts", value="\n".join(xp.get("impacts", [])))
                tags = st.text_input("Tags (séparés par des virgules)", value=", ".join(xp.get("tags", [])))
                save_btn = st.form_submit_button("Mettre à jour")
            delete_btn = st.button("Supprimer cette expérience", key=f"delete-xp-{xp['id']}")
            if save_btn:
                xp.update(
                    {
                        "poste": poste,
                        "entreprise": entreprise,
                        "lieu": lieu,
                        "periode": periode,
                        "missions": [m.strip() for m in missions.splitlines() if m.strip()],
                        "impacts": [i.strip() for i in impacts.splitlines() if i.strip()],
                        "tags": [t.strip() for t in tags.split(",") if t.strip()],
                    }
                )
                persist_content(content)
            if delete_btn:
                content["experiences"] = [item for item in experiences if item.get("id") != xp["id"]]
                persist_content(content)


def manage_projects(content: Dict) -> None:
    st.subheader("Projets")
    projets = content.setdefault("projets", [])

    with st.form("add-project", clear_on_submit=True):
        titre = st.text_input("Titre *")
        periode = st.text_input("Période")
        points = st.text_area("Points clés (une ligne par élément)")
        competences = st.text_input("Compétences (séparées par des virgules)")
        lien = st.text_input("Lien externe (optionnel)")
        image_file = st.file_uploader("Illustration (jpg/png)", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Ajouter")
    if submitted:
        if not titre:
            st.error("Le titre est obligatoire.")
        else:
            image_path = None
            if image_file is not None:
                slug = slugify(titre) or "projet"
                extension = Path(image_file.name).suffix.lower()
                filename = f"{slug}-{uuid_str()}{extension}"
                target = UPLOADS_DIR / filename
                target.write_bytes(image_file.read())
                image_path = f"assets/uploads/{filename}"
            projets.append(
                {
                    "id": uuid_str(),
                    "titre": titre,
                    "periode": periode,
                    "points": [p.strip() for p in points.splitlines() if p.strip()],
                    "competences": [c.strip() for c in competences.split(",") if c.strip()],
                    "lien": lien,
                    "image": image_path,
                }
            )
            persist_content(content)

    if projets:
        proj = st.selectbox(
            "Sélectionner un projet",
            options=projets,
            format_func=lambda p: p.get("titre", "")[:60],
        )
        if proj:
            with st.form(f"edit-project-{proj['id']}"):
                titre = st.text_input("Titre", value=proj.get("titre", ""))
                periode = st.text_input("Période", value=proj.get("periode", ""))
                points = st.text_area("Points clés", value="\n".join(proj.get("points", [])))
                competences = st.text_input("Compétences", value=", ".join(proj.get("competences", [])))
                lien = st.text_input("Lien externe", value=proj.get("lien", ""))
                image_file = st.file_uploader("Remplacer l'image", type=["jpg", "jpeg", "png"], key=f"replace-img-{proj['id']}")
                save_btn = st.form_submit_button("Mettre à jour")
            delete_btn = st.button("Supprimer ce projet", key=f"delete-proj-{proj['id']}")
            if save_btn:
                if image_file is not None:
                    slug = slugify(titre) or "projet"
                    extension = Path(image_file.name).suffix.lower()
                    filename = f"{slug}-{uuid_str()}{extension}"
                    target = UPLOADS_DIR / filename
                    target.write_bytes(image_file.read())
                    proj["image"] = f"assets/uploads/{filename}"
                proj.update(
                    {
                        "titre": titre,
                        "periode": periode,
                        "points": [p.strip() for p in points.splitlines() if p.strip()],
                        "competences": [c.strip() for c in competences.split(",") if c.strip()],
                        "lien": lien,
                    }
                )
                persist_content(content)
            if delete_btn:
                content["projets"] = [p for p in projets if p.get("id") != proj["id"]]
                persist_content(content)


def manage_skills(content: Dict) -> None:
    st.subheader("Compétences par catégorie")
    competences = content.setdefault("competences", {})
    categories = list(competences.keys())
    if not categories:
        st.info("Aucune catégorie. Ajoutez-en dans le fichier content.json.")
        return

    category = st.selectbox("Catégorie", options=categories)
    items = competences.get(category, [])
    st.write("Compétences actuelles :")
    st.write(" ".join(f"<span class='ui-tag'>{item}</span>" for item in items), unsafe_allow_html=True)

    with st.form("add-skill", clear_on_submit=True):
        new_skill = st.text_input("Ajouter une compétence")
        submitted = st.form_submit_button("Ajouter")
    if submitted:
        if not new_skill:
            st.error("La compétence ne peut pas être vide.")
        else:
            items.append(new_skill.strip())
            competences[category] = sorted(set(items))
            persist_content(content)

    to_remove = st.multiselect("Retirer des compétences", options=items)
    if st.button("Supprimer les éléments sélectionnés"):
        competences[category] = [item for item in items if item not in to_remove]
        persist_content(content)


def manage_recommendations(content: Dict) -> None:
    st.subheader("Recommandations")
    recommandations = content.setdefault("recommandations", [])
    with st.form("add-reco", clear_on_submit=True):
        auteur = st.text_input("Auteur *")
        poste = st.text_input("Poste / Relation *")
        date = st.text_input("Date")
        resume = st.text_area("Résumé")
        points = st.text_area("Points clés (une ligne par élément)")
        tel = st.text_input("Téléphone de contact")
        email = st.text_input("Email de contact")
        submitted = st.form_submit_button("Ajouter")
    if submitted:
        if not auteur or not poste:
            st.error("Auteur et poste sont obligatoires.")
        else:
            recommandations.append(
                {
                    "id": uuid_str(),
                    "auteur": auteur,
                    "poste": poste,
                    "date": date,
                    "resume": resume,
                    "points": [p.strip() for p in points.splitlines() if p.strip()],
                    "contact": {"telephone": tel, "email": email},
                }
            )
            persist_content(content)

    if recommandations:
        reco = st.selectbox(
            "Sélectionner une recommandation",
            options=recommandations,
            format_func=lambda r: r.get("auteur", "")[:60],
        )
        if reco:
            with st.form(f"edit-reco-{reco['id']}"):
                auteur = st.text_input("Auteur", value=reco.get("auteur", ""))
                poste = st.text_input("Poste / Relation", value=reco.get("poste", ""))
                date = st.text_input("Date", value=reco.get("date", ""))
                resume = st.text_area("Résumé", value=reco.get("resume", ""))
                points = st.text_area("Points clés", value="\n".join(reco.get("points", [])))
                tel = st.text_input("Téléphone", value=reco.get("contact", {}).get("telephone", ""))
                email = st.text_input("Email", value=reco.get("contact", {}).get("email", ""))
                save_btn = st.form_submit_button("Mettre à jour")
            delete_btn = st.button("Supprimer cette recommandation", key=f"delete-reco-{reco['id']}")
            if save_btn:
                reco.update(
                    {
                        "auteur": auteur,
                        "poste": poste,
                        "date": date,
                        "resume": resume,
                        "points": [p.strip() for p in points.splitlines() if p.strip()],
                        "contact": {"telephone": tel, "email": email},
                    }
                )
                persist_content(content)
            if delete_btn:
                content["recommandations"] = [r for r in recommandations if r.get("id") != reco["id"]]
                persist_content(content)


def manage_messages(messages: List[Dict]) -> None:
    st.subheader("Messages de contact")
    if not messages:
        st.info("Aucun message reçu pour l'instant.")
        return

    df = pd.DataFrame(messages)
    if "created_at" in df.columns:
        df = df.sort_values("created_at", ascending=False)
    st.dataframe(df, use_container_width=True)

    csv_data = df.to_csv(index=False).encode("utf-8")
    json_data = json.dumps(messages, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button("Exporter en CSV", data=csv_data, file_name="messages.csv", mime="text/csv")
    st.download_button("Exporter en JSON", data=json_data, file_name="messages.json", mime="application/json")

    for msg in messages:
        if msg.get("status") != "traité":
            if st.button(f"Marquer comme traité ({msg.get('sujet', '')})", key=f"msg-{msg['id']}"):
                msg["status"] = "traité"
                save_messages(messages)
                st.success("Message mis à jour.")
                rerun()


def manage_files() -> None:
    st.subheader("Fichiers uploadés")
    files = sorted(UPLOADS_DIR.iterdir())
    displayed = False
    for file in files:
        if file.name == ".gitkeep":
            continue
        displayed = True
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"{file.name} ({human_readable_size(file.stat().st_size)})")
        with col2:
            if st.button("Supprimer", key=f"delete-file-{file.name}"):
                file.unlink(missing_ok=True)
                st.success("Fichier supprimé.")
                rerun()
    if not displayed:
        st.info("Aucun fichier dans assets/uploads pour l'instant.")


def human_readable_size(num: int, suffix: str = "B") -> str:
    for unit in ["", "K", "M", "G", "T"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}P{suffix}"


def manage_settings() -> None:
    st.subheader("Paramètres d'apparence")
    config_path = Path(__file__).resolve().parent.parent / ".streamlit" / "config.toml"
    if not config_path.exists():
        st.error("Le fichier .streamlit/config.toml est introuvable.")
        return
    current_config = config_path.read_text(encoding="utf-8")
    default_theme = "dark" if "colorMode = \"dark\"" in current_config else "light"
    choice = st.radio("Thème par défaut", options=["light", "dark"], index=0 if default_theme == "light" else 1)
    if st.button("Mettre à jour le thème"):
        updated_config = []
        for line in current_config.splitlines():
            if line.strip().startswith("colorMode"):
                updated_config.append(f'colorMode = "{choice}"')
            else:
                updated_config.append(line)
        config_path.write_text("\n".join(updated_config), encoding="utf-8")
        st.success("Configuration mise à jour. Relancez l'application pour appliquer le thème.")


def manage_backup(content: Dict) -> None:
    st.subheader("Sauvegarde & restauration")
    json_data = json.dumps(content, ensure_ascii=False, indent=2)
    st.download_button(
        "Télécharger le contenu (JSON)",
        data=json_data.encode("utf-8"),
        file_name="backup_content.json",
        mime="application/json",
    )

    uploaded = st.file_uploader("Importer un fichier JSON pour restauration", type=["json"])
    if uploaded is not None:
        try:
            data = json.loads(uploaded.read().decode("utf-8"))
            if st.button("Confirmer l'import"):
                save_content(data)
                st.success("Importation réalisée.")
                rerun()
        except json.JSONDecodeError as exc:
            st.error(f"JSON invalide : {exc}")


admin_page()
