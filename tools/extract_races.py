"""Add rules text from the Races chapter OCR to data/races.json.

Usage: python3 tools/extract_races.py <ocr/races dir> data/races.json

races.json starts from the character creation sheet (averages, starting attributes);
this adds the chapter page and the full text of each racial ability.
"""
import json
import re
import sys
from pathlib import Path

from ocr_text import load_pages, to_paragraphs

HEADINGS = {"DWARFS": "dwarf", "ELVES": "elf", "HUMANS": "human", "OBSIDIMEN": "obsidiman",
            "ORKS": "ork", "TROLLS": "troll", "TSKRANG": "tskrang", "WINDLINGS": "windling"}
LABEL = re.compile(r"^(?P<label>[A-Z][A-Za-z' -]{2,40}?):\s*(?P<text>.*)$")
TALENT_REFS = {"Versatility": "versatility", "Astral Sight": "astral-sight"}
# Numeric effects the app applies to the character sheet.
EFFECTS = {
    ("dwarf", "Strong Back"): [{"stat": "carryingCapacityStrength", "bonus": 2}],
    ("obsidiman", "Increased Wound Threshold"): [{"stat": "woundThreshold", "bonus": 3}],
    ("obsidiman", "Natural Armor"): [{"stat": "physicalArmor", "bonus": 3}],
    ("windling", "Increased Physical Defense"): [{"stat": "physicalDefense", "bonus": 2}],
}


def key(line):
    return re.sub(r"[^A-Z]", "", line.upper()) if line.strip().isupper() else None


def main(ocr_dir, races_path):
    lines = [(page, l) for page, page_lines in load_pages(ocr_dir) for l in page_lines]
    starts = [(i, HEADINGS[key(l)]) for i, (_, l) in enumerate(lines) if key(l) in HEADINGS]
    data = json.loads(Path(races_path).read_text(encoding="utf-8"))
    races = {r["id"]: r for r in data["races"]}

    for n, (i, race_id) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        section = lines[i + 1:end]
        texts = [l for _, l in section]
        game = next(k for k, l in enumerate(texts) if l.strip() == "Game Information")
        abilities_at = next(k for k, l in enumerate(texts) if l.strip() == "Racial Abilities")
        race = races[race_id]
        race["page"] = lines[i][0]
        # The flavour text before "Game Information" wraps around illustrations and comes out
        # of the OCR too noisy to keep; the app only needs the game information.
        race.pop("description", None)

        abilities = []
        for paragraph in to_paragraphs(texts[abilities_at + 1:]):
            m = LABEL.match(paragraph)
            if m:
                abilities.append({"name": m.group("label"), "text": m.group("text")})
            elif abilities:
                abilities[-1]["text"] += "\n" + paragraph
        for a in abilities:
            if a["name"] in TALENT_REFS:
                a["talentRef"] = TALENT_REFS[a["name"]]
            if (race_id, a["name"]) in EFFECTS:
                a["effects"] = EFFECTS[(race_id, a["name"])]
        race["abilities"] = abilities

    overrides = json.loads((Path(__file__).parent / "overrides" / "races.json").read_text(encoding="utf-8"))
    for race_id, fixes in overrides.items():
        if race_id.startswith("_"):
            continue
        for name, text in fixes.get("abilities", {}).items():
            next(a for a in races[race_id]["abilities"] if a["name"] == name)["text"] = text

    data["source"] = ("Earthdawn 4e Player's Guide - Races chapter, and K. Scott's Earthdawn 4E "
                      "character creation sheet v0.3 (averages)")
    data.pop("notes", None)
    Path(races_path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(starts)} races updated in {races_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
