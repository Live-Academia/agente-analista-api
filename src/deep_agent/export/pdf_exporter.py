"""Converte relatorios Markdown em PDF usando fpdf2 (puro Python, sem dependencias nativas)."""
from __future__ import annotations

import re


def markdown_to_pdf(markdown_text: str, title: str = "Relatorio Deep Agent") -> bytes:
    """Converte texto Markdown para bytes de PDF prontos para download.

    Suporta: H1/H2/H3, listas com marcador, listas numeradas, negrito inline,
    italico inline, codigo inline e paragrafos normais.
    Caracteres nao-Latin1 sao substituidos para compatibilidade com a fonte built-in.
    """
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    def _clean(text: str) -> str:
        """Remove markdown inline e converte para Latin-1 safe."""
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"\*(.*?)\*", r"\1", text)
        text = re.sub(r"`(.*?)`", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # links
        # Substituir caracteres comuns fora do Latin-1
        replacements = {
            "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
            "\u2013": "-", "\u2014": "--", "\u2026": "...",
            "\u00e3": "a", "\u00e9": "e", "\u00ea": "e", "\u00e0": "a",
            "\u00e7": "c", "\u00f5": "o", "\u00fa": "u", "\u00ed": "i",
            "\u00f3": "o", "\u00e2": "a", "\u00f4": "o", "\u00e1": "a",
            "\u00c3": "A", "\u00c9": "E", "\u00c7": "C", "\u00d5": "O",
            "\u00da": "U", "\u00cd": "I", "\u00d3": "O", "\u00c2": "A",
            "\u00c1": "A", "\u00d4": "O", "\u00ca": "E",
        }
        for orig, repl in replacements.items():
            text = text.replace(orig, repl)
        # Remover qualquer caracter restante fora do Latin-1
        text = text.encode("latin-1", errors="replace").decode("latin-1")
        return text

    lines = markdown_text.split("\n")
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if not line:
            pdf.ln(3)
            i += 1
            continue

        # H1
        if line.startswith("# ") and not line.startswith("## "):
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 11, _clean(line[2:]))
            pdf.ln(2)
            # Linha separadora
            pdf.set_draw_color(180, 180, 180)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(50, 50, 50)

        # H2
        elif line.startswith("## ") and not line.startswith("### "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(60, 60, 60)
            pdf.multi_cell(0, 9, _clean(line[3:]))
            pdf.ln(1)
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(50, 50, 50)

        # H3
        elif line.startswith("### "):
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 8, _clean(line[4:]))
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(50, 50, 50)

        # Linha horizontal
        elif line.startswith("---") or line.startswith("***"):
            pdf.set_draw_color(200, 200, 200)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
            pdf.ln(4)

        # Lista com marcador
        elif line.startswith("- ") or line.startswith("* "):
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(50, 50, 50)
            text = _clean(line[2:])
            # Identacao com bullet
            x_orig = pdf.get_x()
            pdf.set_x(x_orig + 5)
            pdf.multi_cell(0, 6, f"• {text}")
            pdf.set_x(x_orig)

        # Lista numerada
        elif re.match(r"^\d+\.\s", line):
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(50, 50, 50)
            text = _clean(line)
            x_orig = pdf.get_x()
            pdf.set_x(x_orig + 5)
            pdf.multi_cell(0, 6, text)
            pdf.set_x(x_orig)

        # Bloco de codigo (```)
        elif line.startswith("```"):
            pdf.set_font("Courier", size=9)
            pdf.set_fill_color(240, 240, 240)
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_line = lines[i].rstrip()
                if code_line:
                    safe = code_line.encode("latin-1", errors="replace").decode("latin-1")
                    pdf.multi_cell(0, 5, safe, fill=True)
                else:
                    pdf.ln(2)
                i += 1
            pdf.set_font("Helvetica", size=11)
            pdf.ln(2)

        # Paragrafo normal
        else:
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 6, _clean(line))

        i += 1

    return bytes(pdf.output())
