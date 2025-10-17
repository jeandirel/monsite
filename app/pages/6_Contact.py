from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from theme import apply_theme

from utils.content_loader import append_message, ensure_initialized, inject_custom_css, load_content
from utils.emailer import send_mail
from utils.storage import uuid_str

p = apply_theme(default="Deep Navy Pro", show_toggle=True)


def render_contact() -> None:
    ensure_initialized()
    inject_custom_css()
    content = load_content()

    st.title("📬 Contactez-moi")
    profile = content.get("profile", {})

    with st.form("contact-form"):
        name = st.text_input("Nom complet")
        email = st.text_input("Adresse e-mail")
        subject = st.text_input("Sujet")
        message = st.text_area("Message")
        submitted = st.form_submit_button("Envoyer")

    if submitted:
        if not name or not email or not subject or not message:
            st.error("Tous les champs sont requis.")
        else:
            payload = {
                "id": uuid_str(),
                "nom": name,
                "email": email,
                "sujet": subject,
                "message": message,
                "status": "nouveau",
            }
            append_message(payload)
            mail_body = (
                f"Message reçu via le site Streamlit :\n\n"
                f"Nom : {name}\n"
                f"E-mail : {email}\n"
                f"Sujet : {subject}\n\n"
                f"{message}"
            )
            email_sent = send_mail(f"[Portfolio] {subject}", mail_body)
            if email_sent:
                st.success("Merci pour votre message ! Une notification a été envoyée par e-mail.")
            else:
                st.success("Merci pour votre message !")
                st.info(
                    f"Si vous souhaitez un contact direct, vous pouvez envoyer un e-mail à "
                    f"<a href='mailto:{profile.get('email', '')}'>{profile.get('email', '')}</a>.",
                    icon="ℹ️",
                )

    with st.expander("Coordonnées directes"):
        st.markdown(
            f"""
            - 📧 {profile.get("email", "")}
            - 📱 {profile.get("telephone", "")}
            - 🔗 [Profil LinkedIn]({profile.get("linkedin", "")})
            - 📍 {" · ".join(profile.get("adresses", []))}
            """,
            unsafe_allow_html=True,
        )


render_contact()
