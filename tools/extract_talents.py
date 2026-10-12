"""Build data/talents.json from the OCR of the Talents chapter.

Usage: python3 tools/extract_talents.py <ocr/talents dir> data/talents.json
"""
import json
import sys
from pathlib import Path

from entries import apply_overrides, extract_entries, mark_headings, parse_skill_use, read_lines


def main(ocr_dir, out_path):
    talents = extract_entries(read_lines(ocr_dir))
    for t in talents:
        header = t.pop("_header")
        t["skillUse"] = parse_skill_use(header.get("Skill Use"))
        notes = [p for p in t["description"] if p.startswith("Skill Use:")]
        t["description"] = [p for p in t["description"] if p not in notes]
        t["nonMagicalNote"] = " ".join(p[len("Skill Use:"):].strip() for p in notes) or None
    apply_overrides(talents, Path(__file__).parent / "overrides" / "talents.json")
    for t in talents:
        t["description"] = mark_headings(t["description"])

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"source": "Earthdawn 4e Player's Guide - Talents chapter",
                   "talents": talents}, f, indent=2, ensure_ascii=False)
    print(f"{len(talents)} talents written to {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
