"""Build data/skills.json from the OCR of the Skills chapter.

Usage: python3 tools/extract_skills.py <ocr/skills dir> data/skills.json
"""
import json
import sys
from pathlib import Path

from entries import apply_overrides, extract_entries, mark_headings, parse_cost, read_lines

LANGUAGE_SKILLS = {"read-write-language", "speak-language"}
ARTISAN_ONLY = {"artisan", "artist"}
KNOWLEDGE_SKILLS = {"knowledge"}
# Default Skill Table (p.184). Most of these are talents usable as skills (see talents.json).
DEFAULT_SKILLS = {
    "animal-handling", "avoid-blow", "awareness", "bribery", "climbing", "conversation",
    "distract", "etiquette", "flirting", "haggle", "melee-weapons", "missile-weapons",
    "research", "resist-taunt", "seduction", "slough-blame", "swimming", "throwing-weapons",
    "tracking", "unarmed-combat", "wilderness-survival",
}


def talents_as_skills(lines, talent_names):
    """Read the "Talents Available as Skills" table (p.185), laid out in three columns."""
    texts = [l.strip() for _, l in lines]
    start = texts.index("Talents Available as Skills")
    tiers, tier = {}, None
    names = sorted(talent_names, key=len, reverse=True)
    for line in texts[start + 1:]:
        if line in ("Novice Skills", "Journeyman Skills"):
            tier = line.split()[0]
            tiers[tier] = []
            continue
        if line.isupper() and len(line) > 3:  # next section heading
            break
        while tier and line:
            name = next((n for n in names if line.startswith(n)), None)
            if not name:
                break
            tiers[tier].append(name)
            line = line[len(name):].strip()
    return {t: sorted(v) for t, v in tiers.items()}


def main(ocr_dir, out_path):
    lines = read_lines(ocr_dir)
    talents_path = Path(out_path).with_name("talents.json")
    talent_names = [t["name"] for t in json.loads(talents_path.read_text(encoding="utf-8"))["talents"]]
    skills = extract_entries(lines)
    for s in skills:
        s["cost"] = parse_cost(s.pop("_header").get("Cost"))
        s["skillType"] = ("Language" if s["id"] in LANGUAGE_SKILLS else
                          "Knowledge" if s["id"] in KNOWLEDGE_SKILLS else
                          "Artisan" if s["id"] in ARTISAN_ONLY else "General")
        s["usableAsArtisan"] = any("used as an Artisan skill" in p for p in s["description"])
    apply_overrides(skills, Path(__file__).parent / "overrides" / "skills.json")
    for s in skills:
        s["default"] = s["id"] in DEFAULT_SKILLS
        s["description"] = mark_headings(s["description"])

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"source": "Earthdawn 4e Player's Guide - Skills chapter",
                   "defaultSkills": sorted(DEFAULT_SKILLS),
                   "talentsAsSkills": talents_as_skills(lines, talent_names),
                   "skills": skills}, f, indent=2, ensure_ascii=False)
    print(f"{len(skills)} skills written to {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
