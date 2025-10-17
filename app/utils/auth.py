from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import bcrypt
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


@dataclass
class Credentials:
    email: str
    password_hash: str


def get_admin_credentials() -> Optional[Credentials]:
    try:
        auth_section = st.secrets.get("auth", {})
    except StreamlitSecretNotFoundError:
        auth_section = {}
    email = auth_section.get("admin_email")
    password_hash = auth_section.get("admin_password_hash")
    if not email or not password_hash:
        return None
    return Credentials(email=email, password_hash=password_hash)


def hash_password(plain_text: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_text.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_text: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain_text.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def logout() -> None:
    st.session_state.pop("auth_user", None)


def login_form() -> bool:
    credentials = get_admin_credentials()
    if credentials is None:
        st.warning(
            "Configuration d'authentification absente. "
            "Veuillez renseigner `.streamlit/secrets.toml`."
        )
        return False

    if "auth_user" in st.session_state:
        return True

    with st.form("admin-login-form", clear_on_submit=False):
        st.write("### Connexion administrateur")
        email = st.text_input("E-mail", placeholder="admin@site.local")
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter")

    if submit:
        if email.strip().lower() != credentials.email.lower():
            st.error("Identifiants invalides.")
            return False
        if not verify_password(password, credentials.password_hash):
            st.error("Identifiants invalides.")
            return False
        st.session_state["auth_user"] = credentials.email
        st.success("Connexion reussie.")
        return True
    return False


def is_authenticated() -> bool:
    return "auth_user" in st.session_state


if __name__ == "__main__":
    import getpass

    plain = getpass.getpass("Saisissez le mot de passe a hacher: ")
    print(hash_password(plain))
