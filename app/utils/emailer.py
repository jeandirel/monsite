from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Optional

import streamlit as st


def _smtp_config() -> Optional[dict]:
    smtp_secrets = st.secrets.get("smtp", {})
    host = smtp_secrets.get("host")
    user = smtp_secrets.get("user")
    password = smtp_secrets.get("password")
    to_addr = smtp_secrets.get("to")
    port = smtp_secrets.get("port", 587)
    if not host or not user or not password or not to_addr:
        return None
    return {"host": host, "user": user, "password": password, "to": to_addr, "port": port}


def send_mail(subject: str, body: str, to: Optional[str] = None) -> bool:
    config = _smtp_config()
    if not config:
        return False

    recipient = to or config["to"]
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config["user"]
    message["To"] = recipient
    message.set_content(body)

    try:
        with smtplib.SMTP(config["host"], config["port"]) as server:
            server.starttls()
            server.login(config["user"], config["password"])
            server.send_message(message)
        return True
    except Exception:
        return False


__all__ = ["send_mail"]
