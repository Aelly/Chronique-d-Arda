import re
import sys
from pathlib import Path
from collections import defaultdict

if len(sys.argv) != 2:
    print("Usage: python detect_doublons_links.py <fichier.md | dossier>")
    sys.exit(1)

path = Path(sys.argv[1])

if not path.exists():
    print("Fichier ou dossier introuvable.")
    sys.exit(1)

def analyze_file(file_path: Path):
    links_lines = defaultdict(list)
    in_sources_section = False
    in_personnages_section = False

    with file_path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            stripped = line.strip()

            # --- Gestion des titres H2 ---
            if stripped.startswith("## "):
                if stripped == "## Sources":
                    in_sources_section = True
                    in_personnages_section = False
                    continue
                elif stripped == "## Personnages notables":
                    in_personnages_section = True
                    continue
                else:
                    # Tout autre H2 termine la section "Personnages notables"
                    in_personnages_section = False

            # Ignorer tout ce qui est après ## Sources
            if in_sources_section:
                continue

            # Ignorer la section Personnages notables
            if in_personnages_section:
                continue

            # Ignorer les blocs de citation
            if stripped.startswith(">"):
                continue

            # Match [[Note]] ou [[Note|alias]]
            matches = re.findall(r"\[\[([^\]|]+)", line)
            for match in matches:
                links_lines[match].append(line_number)

    return {k: v for k, v in links_lines.items() if len(v) > 1}

# Déterminer les fichiers à analyser
if path.is_file():
    md_files = [path]
else:
    md_files = list(path.rglob("*.md"))

if not md_files:
    print("Aucun fichier .md trouvé.")
    sys.exit(0)

found_any = False

for md_file in sorted(md_files):
    duplicates = analyze_file(md_file)

    if duplicates:
        found_any = True
        print(f"\n📄 {md_file}")
        for note, lines in sorted(duplicates.items()):
            lignes = ", ".join(map(str, lines))
            print(f"  - {note} → {len(lines)} occurrences (lignes {lignes})")

if not found_any:
    print("✅ Aucun doublon de lien détecté dans les fichiers analysés.")
