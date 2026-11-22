"""Editorial and language checks for published case-study copy."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=[
    ROOT/"README.md",ROOT/"docs"/"README.es.md",
    ROOT/"docs"/"methodology.md",ROOT/"docs"/"methodology.es.md",
    ROOT/"app.py"
]

def test_public_copy_avoids_long_dashes():
    for path in PUBLIC:
        text=path.read_text(encoding="utf-8")
        assert "\u2014" not in text, f"Long dash found in {path}"
        assert "\u2013" not in text, f"Medium dash found in {path}"

def test_readme_languages_share_verified_metrics():
    english=(ROOT/"README.md").read_text(encoding="utf-8")
    spanish=(ROOT/"docs"/"README.es.md").read_text(encoding="utf-8")
    for figure in ("33.73","27.45","27.63","18.6","22.22","93.59"):
        assert figure in english and figure in spanish,figure
    assert "docs/README.es.md" in english
    assert "../README.md" in spanish

def test_cutoff_explained_in_both_languages():
    english=(ROOT/"README.md").read_text(encoding="utf-8")
    spanish=(ROOT/"docs"/"README.es.md").read_text(encoding="utf-8")
    for item in ("W43","W44","W47"):
        assert item in english and item in spanish
