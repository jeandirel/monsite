from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image, ImageDraw, ImageFont
import streamlit as st

from .storage import (
    ASSETS_DIR,
    DATA_DIR,
    UPLOADS_DIR,
    ensure_dirs,
    load_json,
    now_iso,
    save_json,
)

CONTENT_FILE = DATA_DIR / "content.json"
MESSAGES_FILE = DATA_DIR / "messages.json"
PROFILE_IMAGE = ASSETS_DIR / "profile.jpg"
PROFILE_PDF = ASSETS_DIR / "cv_jean_direl.pdf"
CUSTOM_CSS = (Path(__file__).resolve().parent.parent / "styles" / "custom.css")


def ensure_initialized() -> None:
    ensure_dirs()
    ensure_assets()
    ensure_content_file()
    ensure_messages_file()


def ensure_content_file() -> None:
    if CONTENT_FILE.exists():
        return
    from app.data.seed_content import get_seed_content  # type: ignore

    content = get_seed_content()
    save_json(CONTENT_FILE, content)


def ensure_messages_file() -> None:
    if MESSAGES_FILE.exists():
        return
    save_json(MESSAGES_FILE, [])


def ensure_assets() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    gitkeep = UPLOADS_DIR / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")
    if not PROFILE_IMAGE.exists():
        create_placeholder_image(PROFILE_IMAGE)
    if not PROFILE_PDF.exists():
        create_placeholder_pdf(PROFILE_PDF)


def create_placeholder_image(path: Path) -> None:
    size = (640, 640)
    background = (15, 23, 42)
    accent = (56, 189, 248)
    image = Image.new("RGB", size, background)
    draw = ImageDraw.Draw(image)
    initials = "JD"
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), initials, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
    draw.text(position, initials, font=font, fill=accent)
    image.save(path, format="JPEG", quality=92)


def create_placeholder_pdf(path: Path) -> None:
    stream = "BT /F1 24 Tf 72 750 Td (CV placeholder - Remplacez ce fichier) Tj ET"
    stream_length = len(stream.encode("latin-1"))
    pdf_content = "\n".join(
        [
            "%PDF-1.4",
            "1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj",
            "2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj",
            "3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 595 842]/Resources<</Font<</F1 5 0 R>>>>/Contents 4 0 R>>endobj",
            f"4 0 obj<</Length {stream_length}>>stream",
            stream,
            "endstream endobj",
            "5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj",
            "trailer<</Root 1 0 R>>",
            "%%EOF",
        ]
    )
    path.write_text(pdf_content, encoding="latin-1")


@st.cache_data(show_spinner=False)
def load_content() -> Dict[str, Any]:
    ensure_initialized()
    data = load_json(CONTENT_FILE)
    if not isinstance(data, dict):
        raise ValueError("Le fichier content.json est corrompu ou vide.")
    return data


def save_content(data: Dict[str, Any]) -> None:
    save_json(CONTENT_FILE, data)
    load_content.clear()


@st.cache_data(show_spinner=False)
def load_messages() -> List[Dict[str, Any]]:
    ensure_initialized()
    data = load_json(MESSAGES_FILE)
    if data is None:
        return []
    if not isinstance(data, list):
        raise ValueError("Le fichier messages.json est corrompu.")
    return data


def save_messages(messages: List[Dict[str, Any]]) -> None:
    save_json(MESSAGES_FILE, messages)
    load_messages.clear()


def append_message(message: Dict[str, Any]) -> None:
    messages = load_messages()
    message.setdefault("created_at", now_iso())
    messages.append(message)
    save_messages(messages)


def inject_custom_css() -> None:
    if CUSTOM_CSS.exists():
        css = CUSTOM_CSS.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


__all__ = [
    "load_content",
    "save_content",
    "load_messages",
    "save_messages",
    "append_message",
    "ensure_initialized",
    "inject_custom_css",
    "PROFILE_IMAGE",
    "PROFILE_PDF",
]
