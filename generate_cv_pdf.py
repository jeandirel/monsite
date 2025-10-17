from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from fpdf import FPDF
from fpdf.enums import XPos, YPos


BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "profile_data.json"
OUTPUT_PATH = BASE_DIR / "Jean_Direl_CV.pdf"


ARIAL_REGULAR = r"C:\Windows\Fonts\arial.ttf"
ARIAL_BOLD = r"C:\Windows\Fonts\arialbd.ttf"


@dataclass
class SectionStyle:
    title_font_size: int = 12
    body_font_size: int = 9
    subtitle_font_size: int = 10
    bullet_font_size: int = 9


class CVPDF(FPDF):
    """Helper around FPDF with UTF-8 fonts already registered."""

    def __init__(self) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=False)
        self.add_font("Arial", "", ARIAL_REGULAR)
        self.add_font("Arial", "B", ARIAL_BOLD)
        self.set_margins(15, 15, 15)
        self.section_style = SectionStyle()
        self.column_gap = 8.0
        self.column_width: float | None = None
        self.column_positions: list[float] = []
        self.column_cursor: list[float] = []
        self.current_column = 0

    def line_break(self, height: float = 2.0) -> None:
        """Consistent spacing between blocks."""
        self.ln(height)
        self._reset_x()

    def _available_width(self) -> float:
        return self.w - self.l_margin - self.r_margin

    def _current_x(self) -> float:
        if self.column_width is None:
            return self.l_margin
        return self.column_positions[self.current_column]

    def _reset_x(self) -> None:
        if self.column_width is None:
            self.set_x(self.l_margin)
        else:
            self.set_x(self._current_x())

    def _update_column_y(self) -> None:
        if self.column_width is not None:
            self.column_cursor[self.current_column] = self.get_y()

    def start_two_columns(self, top: float | None = None) -> None:
        """Prepare a two-column layout starting at the provided Y."""
        available_width = self._available_width()
        self.column_width = (available_width - self.column_gap) / 2
        self.column_positions = [
            self.l_margin,
            self.l_margin + self.column_width + self.column_gap,
        ]
        start_y = top if top is not None else self.get_y()
        self.column_cursor = [start_y, start_y]
        self.current_column = 0
        self.set_xy(self.column_positions[0], start_y)

    def set_column(self, index: int) -> None:
        """Switch to the requested column, keeping its own cursor."""
        if self.column_width is None:
            raise RuntimeError("Columns not initialized: call start_two_columns() first.")
        if index not in (0, 1):
            raise ValueError("Column index must be 0 or 1")
        self.current_column = index
        self.set_xy(self.column_positions[index], self.column_cursor[index])

    def section_title(self, title: str) -> None:
        width = self.column_width if self.column_width is not None else self._available_width()
        x = self._current_x()
        y = self.get_y()
        self.set_xy(x, y)
        self.set_fill_color(36, 64, 102)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", self.section_style.title_font_size)
        height = 6.5
        self.cell(width, height, title.upper(), border=0, align="L", fill=True)
        self.set_y(y + height)
        self.set_text_color(55, 55, 55)
        self.line_break(3)
        self._update_column_y()

    def write_body(self, text: str, font_size: int | None = None) -> None:
        self.set_text_color(55, 55, 55)
        size = font_size or self.section_style.body_font_size
        self.set_font("Arial", "", size)
        width = self.column_width if self.column_width is not None else self._available_width()
        self.multi_cell(width, 4.4, text)
        self._update_column_y()
        self._reset_x()

    def write_bullets(self, items: Iterable[str], bullet: str = "•") -> None:
        if not items:
            return
        self.set_text_color(55, 55, 55)
        self.set_font("Arial", "", self.section_style.bullet_font_size)
        width = self.column_width if self.column_width is not None else self._available_width()
        for item in items:
            clean = item.strip()
            if not clean:
                continue
            self.multi_cell(width, 4.2, f"{bullet} {clean}")
            self._reset_x()
        self._update_column_y()


def clean_text(value: str) -> str:
    """Collapsed whitespace and strip artefacts from the JSON source."""
    return " ".join(value.split()).replace("�", "'")


def shorten_text(value: str, max_chars: int) -> str:
    """Shorten text to the closest word boundary within the limit."""
    text = clean_text(value)
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rsplit(" ", 1)[0]
    return truncated.rstrip(",.;:") + "…"


def render_header(pdf: CVPDF, data: dict) -> None:
    about = data["about"]
    contact = data["contact"]

    width = pdf._available_width()
    pdf.set_fill_color(32, 56, 100)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(width, 13, clean_text(about["full_name"]), border=0, align="L", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Arial", "", 12)
    pdf.cell(width, 8, clean_text(about["headline"]), border=0, align="L", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Arial", "", 10)
    pdf.cell(width, 6, clean_text(about["location"]), border=0, align="L", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_fill_color(255, 255, 255)
    pdf.line_break(6)
    pdf.set_text_color(55, 55, 55)

    pdf.start_two_columns(pdf.get_y())

    render_contact(pdf, contact)
    render_skills(pdf, data["skills"])
    render_certifications(pdf, data.get("certifications", []))
    render_interests(pdf, data.get("interests", []))

    pdf.set_column(1)
    render_summary(pdf, data["about"]["summary"])
    render_experience(pdf, data["experience"])
    render_projects(pdf, data.get("projects", []))
    render_education(pdf, data["education"])


def render_contact(pdf: CVPDF, contact: dict) -> None:
    pdf.section_title("Contact")
    pdf.write_body(f"Email : {contact['email']}")
    pdf.write_body(f"Téléphone : {contact['phone']}")
    pdf.write_body(f"LinkedIn : {contact['linkedin']}")
    cities = []
    for addr in contact["address"][:2]:
        part = addr.split(",")[-1].strip()
        if part:
            cities.append(part.replace("76000 ", ""))
    if cities:
        pdf.write_body("Basé : " + " · ".join(cities))
    pdf.write_body(f"Naissance : {contact['birthday']}")
    pdf.line_break(1.0)


def render_summary(pdf: CVPDF, summary: str) -> None:
    pdf.section_title("Profil")
    pdf.write_body(shorten_text(summary, 320))
    pdf.line_break(2)


def render_experience(pdf: CVPDF, experiences: list[dict]) -> None:
    pdf.section_title("Expériences professionnelles")
    main_entries = experiences[:2]
    other_entries = experiences[2:]

    for entry in main_entries:
        title = f"{clean_text(entry['title'])} — {clean_text(entry['company'])}"
        pdf.set_text_color(34, 34, 34)
        pdf.set_font("Arial", "B", pdf.section_style.subtitle_font_size)
        width = pdf.column_width if pdf.column_width is not None else pdf._available_width()
        pdf.multi_cell(width, 4.4, title)
        pdf._reset_x()

        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(90, 90, 90)
        period_line = f"{clean_text(entry['location'])} · {clean_text(entry['period'])}"
        pdf.multi_cell(width, 4.2, period_line)
        pdf._reset_x()

        missions = [clean_text(m) for m in entry.get("missions", [])][:2]
        impacts = [clean_text(i) for i in entry.get("impact", [])][:1]
        summary_parts = missions + impacts
        if summary_parts:
            pdf.write_body(shorten_text(" | ".join(summary_parts), 200))
        pdf.line_break(1.5)

    if other_entries:
        condensed = [
            f"{clean_text(exp['title'])} — {clean_text(exp['company'])} ({clean_text(exp['period'])})"
            for exp in other_entries
        ]
        pdf.write_body(shorten_text("Autres : " + " ; ".join(condensed), 180))
        pdf.line_break(1.0)


def render_education(pdf: CVPDF, education: list[dict]) -> None:
    pdf.section_title("Formation")
    for school in education[:2]:
        heading = f"{clean_text(school['degree'])} — {clean_text(school['institution'])}"
        pdf.set_text_color(34, 34, 34)
        pdf.set_font("Arial", "B", pdf.section_style.subtitle_font_size)
        width = pdf.column_width if pdf.column_width is not None else pdf._available_width()
        pdf.multi_cell(width, 4.4, heading)
        pdf._reset_x()

        pdf.set_font("Arial", "", 10)
        meta = f"{clean_text(school['location'])} | {clean_text(school['period'])}"
        pdf.set_text_color(90, 90, 90)
        pdf.multi_cell(width, 4.0, meta)
        pdf.line_break(1.5)
    pdf.line_break(1.5)


def render_projects(pdf: CVPDF, projects: list[dict]) -> None:
    if not projects:
        return
    pdf.section_title("Projets sélectionnés")
    for project in projects[:1]:
        name_line = f"{clean_text(project['name'])} ({clean_text(project['period'])})"
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(34, 34, 34)
        width = pdf.column_width if pdf.column_width is not None else pdf._available_width()
        pdf.multi_cell(width, 4.4, name_line)
        pdf._reset_x()

        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(90, 90, 90)
        pdf.multi_cell(width, 4.2, shorten_text(project.get("context", ""), 160))
        pdf._reset_x()

        contributions = project.get("contributions", [])
        if contributions:
            pdf.write_body(shorten_text("; ".join(contributions), 200))
        pdf.line_break(2.0)
    pdf.line_break(1.0)


def render_skills(pdf: CVPDF, skills: dict) -> None:
    pdf.section_title("Compétences clés")
    tech = (skills.get("IA & Data", [])[:4] + skills.get("Langages & Frameworks", [])[:3])[:6]
    data_ops = (skills.get("Data Engineering & BI", [])[:3] + skills.get("Ops & Outils", [])[:2])[:5]
    soft = skills.get("Soft skills", [])[:4]

    if tech:
        pdf.write_body("Tech : " + ", ".join(clean_text(item) for item in tech))
    if data_ops:
        pdf.write_body("Data/Ops : " + ", ".join(clean_text(item) for item in data_ops))
    if soft:
        pdf.write_body("Soft : " + ", ".join(clean_text(item) for item in soft))
    pdf.line_break(1.0)


def render_certifications(pdf: CVPDF, certifications: list[dict]) -> None:
    if not certifications:
        return
    pdf.section_title("Certifications")
    width = pdf.column_width if pdf.column_width is not None else pdf._available_width()
    for cert in certifications[:1]:
        period = cert.get("issue_date", "")
        expiry = cert.get("expiry_date")
        timing = clean_text(period)
        if expiry:
            timing += f" → {clean_text(expiry)}"
        line = f"{clean_text(cert['title'])} — {clean_text(cert['provider'])} ({timing})"
        pdf.write_body(shorten_text(line, 180))
    pdf.line_break(1.0)


def render_recommendations(pdf: CVPDF, recommendations: list[dict]) -> None:
    if not recommendations:
        return
    pdf.section_title("Recommandations")
    for ref in recommendations[:1]:
        contact_info = ref.get("contact", {})
        contact_parts: list[str] = []
        if isinstance(contact_info, dict):
            for key in ("telephone", "email"):
                value = contact_info.get(key)
                if value:
                    contact_parts.append(clean_text(value))
        elif isinstance(contact_info, str):
            contact_parts.append(clean_text(contact_info))
        contact_line = " · ".join(contact_parts)
        summary = f"{clean_text(ref['name'])} ({clean_text(ref['role'])}, {clean_text(ref['date'])}) — {contact_line}"
        pdf.write_body(shorten_text(summary, 200))
    pdf.line_break(1.5)


def render_interests(pdf: CVPDF, interests: list[str]) -> None:
    if not interests:
        return
    pdf.section_title("Centres d'intérêt")
    pdf.set_text_color(55, 55, 55)
    pdf.set_font("Arial", "", 11)
    width = pdf.column_width if pdf.column_width is not None else pdf._available_width()
    top_interests = [clean_text(item) for item in interests][:3]
    pdf.multi_cell(width, 4.2, " · ".join(top_interests))
    pdf._reset_x()


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    pdf = CVPDF()
    pdf.add_page()

    render_header(pdf, data)

    pdf.output(str(OUTPUT_PATH))


if __name__ == "__main__":
    main()
