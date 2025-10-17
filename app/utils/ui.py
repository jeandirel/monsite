from __future__ import annotations

from typing import Iterable, List, Optional

import streamlit as st


def card(
    title: str,
    content: str,
    subtitle: Optional[str] = None,
    footer: Optional[str] = None,
    image: Optional[str] = None,
) -> None:
    body_parts: List[str] = []
    if image:
        body_parts.append(f'<img src="{image}" class="card-image" alt="{title}">')
    body_parts.append(f'<h3>{title}</h3>')
    if subtitle:
        body_parts.append(f'<p class="card-subtitle">{subtitle}</p>')
    body_parts.append(f'<div class="card-body">{content}</div>')
    if footer:
        body_parts.append(f'<div class="card-footer">{footer}</div>')
    html = '<div class="ui-card">' + "".join(body_parts) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def badge(text: str) -> str:
    return f'<span class="ui-badge">{text}</span>'


def tag(text: str) -> str:
    return f'<span class="ui-tag">{text}</span>'


def timeline(items: Iterable[dict]) -> None:
    html_items: List[str] = []
    for item in items:
        title = item.get("title", "")
        subtitle = item.get("subtitle", "")
        period = item.get("period", "")
        details = item.get("details", [])
        detail_html = "".join(f"<li>{point}</li>" for point in details)
        html_items.append(
            "".join(
                [
                    '<div class="timeline-item">',
                    f'<div class="timeline-node"></div>',
                    '<div class="timeline-content">',
                    f"<h4>{title}</h4>",
                    f'<p class="timeline-subtitle">{subtitle}</p>' if subtitle else "",
                    f'<p class="timeline-period">{period}</p>' if period else "",
                    f"<ul>{detail_html}</ul>" if details else "",
                    "</div></div>",
                ]
            )
        )
    html = '<div class="timeline-wrapper">' + "".join(html_items) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def metric(label: str, value: str, help_text: Optional[str] = None) -> None:
    html = (
        '<div class="metric-card">'
        f"<p class='metric-label'>{label}</p>"
        f"<p class='metric-value'>{value}</p>"
    )
    if help_text:
        html += f"<p class='metric-help'>{help_text}</p>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def toolbar_crud(
    add_cb=None,
    export_cb=None,
    import_cb=None,
    add_label: str = "Ajouter",
    export_label: str = "Exporter",
    import_label: str = "Importer",
) -> None:
    cols = st.columns(3)
    if add_cb:
        with cols[0]:
            if st.button(add_label, use_container_width=True):
                add_cb()
    if export_cb:
        with cols[1]:
            if st.button(export_label, use_container_width=True):
                export_cb()
    if import_cb:
        with cols[2]:
            if st.button(import_label, use_container_width=True):
                import_cb()


__all__ = [
    "card",
    "badge",
    "tag",
    "timeline",
    "metric",
    "toolbar_crud",
]
