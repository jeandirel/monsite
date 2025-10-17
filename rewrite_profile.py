from pathlib import Path

path = Path(r"C:\Users\mon pc\Downloads\Mon CV et mon site\app\pages\7_Admin.py")
text = path.read_text(encoding="utf-8")
old = """    profile = content.get(\"profile\", {})
    with st.form(\"profile-form\"):
        nom = st.text_input(\"Nom complet\", value=profile.get(\"nom\", \"\"))
        headline = st.text_input(\"Titre / headline\", value=profile.get(\"headline\", \"\"))
        email = st.text_input(\"Email\", value=profile.get(\"email\", \"\"))
        telephone = st.text_input(\"T?l?phone\", value=profile.get(\"telephone\", \"\"))
        linkedin = st.text_input(\"Lien LinkedIn\", value=profile.get(\"linkedin\", \"\"))
        anniversaire_str = profile.get(\"anniversaire\", \"1997-07-14\")
        anniversaire_dt = pd.to_datetime(anniversaire_str, errors=\"coerce\")
        if pd.isna(anniversaire_dt):
            anniversaire_dt = pd.Timestamp(\"1997-07-14\")
        anniversaire = st.date_input(\"Anniversaire\", value=anniversaire_dt.date())
        adresses = st.text_area(
            \"Adresses (une par ligne)\",
            value=\"\\n\".join(profile.get(\"adresses\", [])),
        )
        interets = st.text_area(
            \"Centres d'int?rGt (une ligne par ?l?ment)\",
            value=\"\\n\".join(profile.get(\"interets\", [])),
        )
        bio = st.text_area(\"Bio courte\", value=profile.get(\"bio\", \"\"), height=150)
        photo = st.file_uploader(\"Photo de profil (jpg/png)\", type=[\"jpg\", \"jpeg\", \"png\"])
        cv_pdf = st.file_uploader(\"CV (PDF)\", type=[\"pdf\"])
        submitted = st.form_submit_button(\"Enregistrer le profil\")

    if submitted:
        content[\"profile\"] = {
            \"nom\": nom,
            \"headline\": headline,
            \"email\": email,
            \"telephone\": telephone,
            \"linkedin\": linkedin,
            \"anniversaire\": anniversaire.strftime(\"%Y-%m-%d\") if isinstance(anniversaire, date) else anniversaire_dt.strftime(\"%Y-%m-%d\"),
            \"adresses\": [addr.strip() for addr in adresses.splitlines() if addr.strip()],
            \"interets\": [line.strip() for line in interets.splitlines() if line.strip()],
            \"photo\": profile.get(\"photo\", \"assets/profile.jpg\"),
            \"cv_pdf\": profile.get(\"cv_pdf\", \"assets/cv_jean_direl.pdf\"),
            \"bio\": bio,
        }
        if photo is not None:
            PROFILE_IMAGE.write_bytes(photo.read())
        if cv_pdf is not None:
            PROFILE_PDF.write_bytes(cv_pdf.read())
        persist_content(content)
"""

new = """    profile = content.get(\"profile\", {})
    with st.form(\"profile-form\"):
        nom = st.text_input(\"Nom complet\", value=profile.get(\"nom\", \"\"))
        headline = st.text_input(\"Titre / headline\", value=profile.get(\"headline\", \"\"))
        email = st.text_input(\"Email\", value=profile.get(\"email\", \"\"))
        telephone = st.text_input(\"Téléphone\", value=profile.get(\"telephone\", \"\"))
        linkedin = st.text_input(\"Lien LinkedIn\", value=profile.get(\"linkedin\", \"\"))
        anniversaire_str = profile.get(\"anniversaire\", \"1997-07-14\")
        anniversaire_dt = pd.to_datetime(anniversaire_str, errors=\"coerce\")
        if pd.isna(anniversaire_dt):
            anniversaire_dt = pd.Timestamp(\"1997-07-14\")
        anniversaire = st.date_input(\"Anniversaire\", value=anniversaire_dt.date())
        adresses = st.text_area(
            \"Adresses (une par ligne)\",
            value=\"\\n\".join(profile.get(\"adresses\", [])),
        )
        interets = st.text_area(
            \"Centres d'intérêt (une ligne par élément)\",
            value=\"\\n\".join(profile.get(\"interets\", [])),
        )
        bio = st.text_area(\"Bio courte\", value=profile.get(\"bio\", \"\"), height=150)
        photo = st.file_uploader(\"Photo de profil (jpg/png)\", type=[\"jpg\", \"jpeg\", \"png\"])
        cv_pdf = st.file_uploader(\"CV (PDF)\", type=[\"pdf\"])
        submitted = st.form_submit_button(\"Enregistrer le profil\")

    if not submitted:
        return

    updated_profile = {
        \"nom\": nom,
        \"headline\": headline,
        \"email\": email,
        \"telephone\": telephone,
        \"linkedin\": linkedin,
        \"anniversaire\": anniversaire.strftime(\"%Y-%m-%d\")
        if isinstance(anniversaire, date)
        else anniversaire_dt.strftime(\"%Y-%m-%d\"),
        \"adresses\": [addr.strip() for addr in adresses.splitlines() if addr.strip()],
        \"interets\": [line.strip() for line in interets.splitlines() if line.strip()],
        \"photo\": profile.get(\"photo\", \"assets/profile.jpg\"),
        \"cv_pdf\": profile.get(\"cv_pdf\", \"assets/cv_jean_direl.pdf\"),
        \"bio\": bio,
    }

    if photo is not None:
        photo_bytes = photo.getvalue()
        ext = Path(photo.name or \"\").suffix.lower()
        if ext not in {\".jpg\", \".jpeg\", \".png\"}:
            ext = \".jpg\"
        filename = f\"profile-{uuid_str()}\{ext}\"
        destination = UPLOADS_DIR / filename
        destination.write_bytes(photo_bytes)
        PROFILE_IMAGE.write_bytes(photo_bytes)

        old_photo_ref = profile.get(\"photo\", \"")
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
        updated_profile[\"photo\"] = f\"uploads/{filename}\"

    if cv_pdf is not None:
        pdf_bytes = cv_pdf.getvalue()
        PROFILE_PDF.write_bytes(pdf_bytes)
        updated_profile[\"cv_pdf\"] = \"assets/cv_jean_direl.pdf\"

    content[\"profile\"] = updated_profile
    persist_content(content)
"""

if old not in text:
    raise SystemExit("original block not found")

text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
