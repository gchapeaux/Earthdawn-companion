"""Build data/disciplines.json from the OCR of the Disciplines chapter.

Usage: python3 tools/extract_disciplines.py <ocr/disc dir> data/talents.json data/disciplines.json

Circle headings are partly drawn as vector shapes and missing from the OCR, so circles
are counted instead: First Circle grants five "Discipline Talents:", then every later
circle ends with exactly one "Discipline Talent:" line.
"""
import json
import re
import sys
from pathlib import Path

from entries import slug
from ocr_text import fix_words, load_pages

DISCIPLINES = ["Air Sailor", "Archer", "Beastmaster", "Cavalryman", "Elementalist", "Illusionist",
               "Nethermancer", "Scout", "Sky Raider", "Swordmaster", "Thief", "Troubadour",
               "Warrior", "Weaponsmith", "Wizard"]
ATTRIBUTES = {"Dexterity": "DEX", "Strength": "STR", "Toughness": "TOU",
              "Perception": "PER", "Willpower": "WIL", "Charisma": "CHA"}
LABEL = re.compile(r"^(?P<label>[A-Z][A-Za-z', _-]{2,40}?)\s*:\s*(?P<text>.*)$")
GLUED_HEADING = re.compile(r"\s+(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth)\s+Circ\S*$")
DURABILITY = re.compile(r"^Durability\s+(\d+)\s*$")
CIRCLE_HEADING = re.compile(r"^(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)\s+Circle\s*$")
DEFENSE = re.compile(r"adds \+(\d+) to his (Physical|Mystic|Social) Defense")
BONUS = re.compile(r"adds \+(\d+) to his")


def join(lines):
    text = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if text.endswith("-") and line[:1].islower():
            text = text[:-1] + line
        else:
            text = (text + " " + line).strip()
    return fix_words(re.sub(r"\s+", " ", text))


def split_list(text):
    """'Avoid Blow, Thread Weaving (Air Weaving), Wind Catcher' -> refs."""
    refs = []
    text = GLUED_HEADING.sub("", text.strip())
    for item in re.split(r",\s*", text.rstrip(".")):
        item = item.strip()
        if not item:
            continue
        m = re.match(r"^(.*?)\s*[(\[](.*)[)\]]$", item)
        name, variant = (m.group(1), m.group(2)) if m else (item, None)
        refs.append({"ref": slug(name), "name": name, **({"variant": variant} if variant else {})})
    return refs


def labeled_blocks(lines):
    """Group lines into (label, text) blocks; unlabeled lines continue the previous block."""
    blocks = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if CIRCLE_HEADING.match(s) or s == "Talents and Abilities":
            blocks.append((s, ""))
            continue
        d = DURABILITY.match(s)
        if d:
            blocks.append(("Durability", d.group(1)))
            continue
        m = LABEL.match(s)
        if m:
            blocks.append((m.group("label").replace(" _ ", " ").replace("_", "").strip(), [m.group("text")]))
        elif blocks and isinstance(blocks[-1][1], list):
            blocks[-1][1].append(s)
        else:
            blocks.append(("", [s]))
    return [(label, join(text) if isinstance(text, list) else text) for label, text in blocks]


def ability(label, text):
    entry = {"type": label.lower().replace(" ", "-"), "name": label, "text": text}
    if label == "Defense":
        m = DEFENSE.search(text)
        if m:
            entry.update({"defense": m.group(2).lower(), "bonus": int(m.group(1))})
    elif label in ("Initiative", "Mystic Armor", "Recovery"):
        m = BONUS.search(text)
        entry["bonus"] = int(m.group(1)) if m else 1
    return entry


def parse_discipline(name, lines):
    text = [l for l in lines[1:]]
    marker = next(i for i, l in enumerate(text) if l.strip() == "Talents and Abilities")
    intro, rest = text[:marker], text[marker + 1:]

    # Intro: flavour text, then labeled fields.
    first_label = next((i for i, l in enumerate(intro) if l.strip().startswith("Important")),
                       next(i for i, l in enumerate(intro) if l.strip().startswith("Karma")))
    d = {"id": slug(name), "name": name, "description": join(intro[:first_label])}
    for label, value in labeled_blocks(intro[first_label:]):
        key = label.lower().replace("-", "").replace(" ", "")
        if key.startswith("important"):
            d["importantAttributes"] = [a for w, a in ATTRIBUTES.items() if w in value]
        elif key.startswith("karma"):
            d["karmaRitual"] = value
        elif key.startswith("artisan"):
            d["artisanSkills"] = [s.strip() for s in value.rstrip(".").split(",")]
        elif key.startswith("halfmagic"):
            d["halfMagic"] = value
        elif label in ("Note", "Mount"):
            d.setdefault("notes", []).append({"name": label, "text": value})
        elif "Important Attri" in value:
            d["importantAttributes"] = [a for w, a in ATTRIBUTES.items() if w in value]
        else:
            d.setdefault("_unparsed", []).append([label, value])

    d["talentOptions"] = {}
    d["circles"] = []
    circle = {"circle": 1, "disciplineTalents": [], "abilities": []}
    for label, value in labeled_blocks(rest):
        if not label or CIRCLE_HEADING.match(label):
            if value:
                d.setdefault("_unparsed", []).append([label, value])
            continue
        value = GLUED_HEADING.sub("", value)
        if label.endswith("Talent Options"):
            tier = label.split()[0]
            # The book calls the first pool "Novice" (and once "Initiate").
            d["talentOptions"]["Novice" if tier == "Initiate" else tier] = split_list(value)
        elif label == "Discipline Talents":
            circle["disciplineTalents"] = split_list(value)
            d["circles"].append(circle)
            circle = {"circle": len(d["circles"]) + 1, "disciplineTalents": [], "abilities": []}
        elif label == "Discipline Talent":
            circle["disciplineTalents"] = split_list(value)
            d["circles"].append(circle)
            circle = {"circle": len(d["circles"]) + 1, "disciplineTalents": [], "abilities": []}
        elif label == "Durability":
            d["durability"] = int(value)
        elif label == "Free Talent":
            m = re.match(r"^([A-Z][A-Za-z ]+?)(?:\.\s+(.*))?$", value)
            if m and m.group(1).strip() in TALENT_NAMES | SKILL_NAMES:
                talent = {"ref": slug(m.group(1)), "name": m.group(1).strip()}
                if m.group(1).strip() not in TALENT_NAMES:
                    # Troubadour's Entertainer, Weaponsmith's Craftsman: a talent version of a skill.
                    talent["kind"] = "skill"
                if m.group(2):
                    talent["note"] = m.group(2)
                circle.setdefault("freeTalents", []).append(talent)
            else:
                circle["abilities"].append(ability(label, value))
        else:
            circle["abilities"].append(ability(label, value))
    return d


TALENT_NAMES = set()
SKILL_NAMES = set()


def main(ocr_dir, talents_path, out_path):
    TALENT_NAMES.update(t["name"] for t in json.load(open(talents_path, encoding="utf-8"))["talents"])
    skills_path = Path(talents_path).with_name("skills.json")
    SKILL_NAMES.update(s["name"] for s in json.load(open(skills_path, encoding="utf-8"))["skills"])
    lines = [l for _, page in load_pages(ocr_dir) for l in page]
    def key(text):
        return re.sub(r"\s+", "", text).upper()

    keys = {key(n): n for n in DISCIPLINES}
    starts = [i for i, l in enumerate(lines) if l.strip().isupper() and key(l) in keys]
    disciplines = []
    for n, i in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        name = keys[key(lines[i])]
        disciplines.append(parse_discipline(name, lines[i:end]))

    overrides = json.loads((Path(__file__).parent / "overrides" / "disciplines.json").read_text(encoding="utf-8"))
    by_id = {d["id"]: d for d in disciplines}
    for disc_id, fix in overrides.items():
        if not disc_id.startswith("_"):
            by_id[disc_id].update(fix)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"source": "Earthdawn 4e Player's Guide - Disciplines chapter",
                   "disciplines": disciplines}, f, indent=2, ensure_ascii=False)
    print(f"{len(disciplines)} disciplines written to {out_path}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
