#!/usr/bin/env python3
"""
Genera visual_notes.html automáticamente a partir de:
- visual_notes.template.html  -> plantilla base
- visual_notes.json           -> datos de grupos e imágenes

USO BÁSICO:
    python3 generate_visual_notes.py \
      --template visual_notes.template.html \
      --data visual_notes.json \
      --output visual_notes.html

QUÉ HACE:
1. Lee la plantilla HTML.
2. Busca el marcador {{AUTO_GENERATED_VISUAL_ARCHIVE}}.
3. Construye el archivo visual desde el JSON.
4. Inserta ese bloque en la plantilla.
5. Guarda el HTML final.

PARA QUÉ SIRVE:
- Evitar editar visual_notes.html a mano cada vez.
- Mantener orden y consistencia.
- Actualizar captions, grupos y archivos desde un solo lugar.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from urllib.parse import quote


def escape_attr(value: str) -> str:
    """Escapa texto para atributos HTML."""
    return html.escape(value, quote=True)


SAFE_PATH_CHARS = "/._-:()"


def path_href(base: str, filename: str) -> str:
    """
    Convierte un nombre de archivo a una ruta apta para href/src.
    - conserva slash, punto, guion, guion bajo, dos puntos y paréntesis
    - convierte espacios a %20
    """
    return f"{base.rstrip('/')}/{quote(filename, safe=SAFE_PATH_CHARS)}"


def build_card(full_base: str, thumbs_base: str, item: dict) -> str:
    """Construye una tarjeta individual de la grilla."""
    file_name = item["file"]
    full_path = path_href(full_base, file_name)
    thumb_path = path_href(thumbs_base, file_name)
    alt_en = escape_attr(item["alt_en"])
    caption_en = html.escape(item["caption_en"])
    caption_es = html.escape(item["caption_es"])

    return f'''          <figure class="visual-note-card">
            <a href="{full_path}" target="_blank" rel="noopener noreferrer">
              <img src="{thumb_path}" alt="{alt_en}">
            </a>
            <figcaption>
              <span class="lang lang-en" lang="en">{caption_en}</span>
              <span class="lang lang-es" lang="es">{caption_es}</span>
            </figcaption>
          </figure>'''


def build_group(full_base: str, thumbs_base: str, group: dict) -> str:
    """Construye una subsección visible por lugar."""
    group_en = html.escape(group["group_en"])
    group_es = html.escape(group["group_es"])
    comment = group.get("group_comment", "")
    comment_block = ""
    if comment:
        comment_block = f"\n          <!-- {html.escape(comment)} -->"

    cards = "\n\n".join(build_card(full_base, thumbs_base, item) for item in group["items"])

    return f'''        <div class="visual-archive-group">
          <h3 class="projects-subtitle">
            <span class="lang lang-en" lang="en">{group_en}</span>
            <span class="lang lang-es" lang="es">{group_es}</span>
          </h3>{comment_block}

          <div class="visual-notes-grid">
{cards}
          </div>
        </div>'''


def generate_archive_block(data: dict) -> str:
    """Construye el bloque completo que reemplaza el marcador de la plantilla."""
    full_base = data["paths"]["full_base"]
    thumbs_base = data["paths"]["thumbs_base"]
    groups = data["groups"]

    return "\n\n".join(build_group(full_base, thumbs_base, group) for group in groups)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate visual_notes.html from template + JSON data.")
    parser.add_argument("--template", required=True, help="Path to visual_notes.template.html")
    parser.add_argument("--data", required=True, help="Path to visual_notes.json")
    parser.add_argument("--output", required=True, help="Path to output visual_notes.html")
    args = parser.parse_args()

    template_path = Path(args.template)
    data_path = Path(args.data)
    output_path = Path(args.output)

    template = template_path.read_text(encoding="utf-8")
    data = json.loads(data_path.read_text(encoding="utf-8"))

    marker = "{{AUTO_GENERATED_VISUAL_ARCHIVE}}"
    if marker not in template:
        raise ValueError(f"Marker {marker!r} not found in template.")

    archive_html = generate_archive_block(data)
    final_html = template.replace(marker, archive_html)

    output_path.write_text(final_html, encoding="utf-8")
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
