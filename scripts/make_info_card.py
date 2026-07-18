from __future__ import annotations

import html
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


ROWS = [
    ("Name", "Shubh Srivastava"),
    ("Role", "Computer Science Student"),
    ("Focus", "Algorithms, security, ML, systems"),
    ("Stack", "C++ / Python / JavaScript / SQL / React"),
    ("Interests", "Blockchain, ZK proofs, cryptography"),
    ("Style", "Clean, optimized, scalable code"),
    ("GitHub", "github.com/shubh-srivastava"),
]


def svg_escape(value: str) -> str:
    return html.escape(value, quote=True)


def main() -> None:
    static = os.getenv("STATIC") == "1"
    width = 490
    height = 350
    left = 34
    top = 78
    row_h = 34

    lines = []
    for idx, (key, value) in enumerate(ROWS):
        y = top + idx * row_h
        delay = 0 if static else 0.25 + idx * 0.11
        anim = ""
        if not static:
            anim = (
                f'<animate attributeName="opacity" values="0;1" dur="0.32s" begin="{delay:.2f}s" fill="freeze" />'
                f'<animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" dur="0.32s" begin="{delay:.2f}s" fill="freeze" />'
            )
        opacity = "1" if static else "0"
        lines.append(
            f'<g opacity="{opacity}">{anim}'
            f'<text x="{left}" y="{y}" fill="#7ee787" class="key">{svg_escape(key)}</text>'
            f'<text x="{left + 112}" y="{y}" fill="#c9d1d9" class="value">{svg_escape(value)}</text>'
            "</g>"
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Shubh Srivastava profile information">
  <title>Shubh Srivastava profile information</title>
  <style>
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    .key {{ font: 600 15px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    .value {{ font: 500 15px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  </style>
  <rect width="100%" height="100%" rx="12" fill="#0d1117" />
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="11" fill="none" stroke="#30363d" />
  <circle cx="28" cy="26" r="6" fill="#ff5f56" />
  <circle cx="48" cy="26" r="6" fill="#ffbd2e" />
  <circle cx="68" cy="26" r="6" fill="#27c93f" />
  <text x="34" y="55" fill="#8b949e" class="mono" font-size="14">shubh@github:~$ whoami</text>
  <g class="mono">
    {''.join(lines)}
  </g>
  <text x="34" y="322" fill="#8b949e" class="mono" font-size="13">Building reliable software from first principles.</text>
</svg>
"""
    (ROOT / "info-card.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
