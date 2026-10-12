"""Check that the rules data in data/ is complete and consistent.

Usage: python3 tools/validate_data.py [data dir]
Exits with status 1 when an error is found; warnings point at entries to proofread.
"""
import json
import re
import sys
from pathlib import Path

ACTIONS = {"Standard", "Simple", "Free", "Sustained", "NA"}
ATTRIBUTES = {"DEX", "STR", "TOU", "PER", "WIL", "CHA"}
TIERS = {"Novice", "Journeyman", "Warden", "Master"}


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, where, message):
        self.errors.append(f"{where}: {message}")

    def warn(self, where, message):
        self.warnings.append(f"{where}: {message}")


def check_entry(r, where, e):
    step = e.get("step")
    if step is not None and (set(step) != {"attribute", "bonus"} or
                             (step["attribute"] is not None and step["attribute"] not in ATTRIBUTES)):
        r.error(where, f"bad step {step}")
    if e.get("action") not in ACTIONS:
        r.error(where, f"bad action {e.get('action')!r}")
    if not isinstance(e.get("strain"), int):
        r.error(where, f"missing strain")
    if not isinstance(e.get("page"), int):
        r.error(where, "missing page")
    if not e.get("description"):
        r.error(where, "empty description")
        return
    for p in e["description"]:
        if not p.startswith("## ") and not re.search(r"[.!?:)\"]$", p):
            r.warn(where, f"paragraph does not end a sentence: ...{p[-50:]!r}")
        if re.search(r"[|~@{}\\]", p):
            r.warn(where, f"suspicious characters: {p[:60]!r}")
    for t in e.get("tables", []):
        if any(len(row) != len(t["columns"]) for row in t["rows"]):
            r.error(where, f"table {t['title']!r} has rows of the wrong width")


def main(data_dir):
    data = Path(data_dir)
    load = lambda name: json.loads((data / name).read_text(encoding="utf-8"))
    r = Report()

    talents = load("talents.json")["talents"]
    skills_file = load("skills.json")
    skills = skills_file["skills"]
    disciplines = load("disciplines.json")["disciplines"]
    races = load("races.json")["races"]
    step_dice = load("step-dice.json")["steps"]
    attribute_table = load("attribute-table.json")["values"]

    talent_ids = {t["id"]: t for t in talents}
    skill_ids = {s["id"]: s for s in skills}
    for collection, name in ((talents, "talent"), (skills, "skill"), (disciplines, "discipline"), (races, "race")):
        ids = [e["id"] for e in collection]
        for dup in {i for i in ids if ids.count(i) > 1}:
            r.error(name, f"duplicate id {dup}")

    for t in talents:
        where = f"talent {t['name']}"
        check_entry(r, where, t)
        su = t.get("skillUse")
        if not su or su["allowed"] is None:
            r.error(where, "missing Skill Use")
        elif su["allowed"] and su["tier"] not in TIERS:
            r.error(where, f"skill use without tier: {su}")

    for s in skills:
        where = f"skill {s['name']}"
        check_entry(r, where, s)
        if s.get("cost") not in TIERS:
            r.error(where, f"bad cost {s.get('cost')!r}")
        if s.get("skillType") not in {"Artisan", "General", "Knowledge", "Language"}:
            r.error(where, f"bad skill type {s.get('skillType')!r}")

    # The Skills chapter table and each talent's "Skill Use" line must agree.
    book = {name: tier for tier, names in skills_file["talentsAsSkills"].items() for name in names}
    for t in talents:
        su = t.get("skillUse") or {}
        listed = book.get(t["name"])
        if su.get("allowed") and listed != su.get("tier"):
            r.error(f"talent {t['name']}", f"Skill Use {su.get('tier')} but Skills chapter lists {listed}")
        if listed and not su.get("allowed"):
            r.error(f"talent {t['name']}", f"Skills chapter lists it as a {listed} skill but Skill Use is No")
    for ref in skills_file["defaultSkills"]:
        if ref not in talent_ids and ref not in skill_ids:
            r.error("default skills", f"unknown {ref}")

    for d in disciplines:
        where = f"discipline {d['name']}"
        for field in ("description", "importantAttributes", "karmaRitual", "artisanSkills", "halfMagic", "durability"):
            if not d.get(field):
                r.error(where, f"missing {field}")
        if set(d.get("importantAttributes", [])) - ATTRIBUTES:
            r.error(where, "bad important attributes")
        if [c["circle"] for c in d["circles"]] != list(range(1, 9)):
            r.error(where, f"circles {[c['circle'] for c in d['circles']]}, expected 1-8")
        if set(d["talentOptions"]) != {"Novice", "Journeyman"}:
            r.error(where, f"talent option tiers {sorted(d['talentOptions'])}")
        for tier, options in d["talentOptions"].items():
            if len(options) != 10:
                r.warn(where, f"{len(options)} {tier} talent options (usually 10)")
        refs = [(f"{tier} option", o) for tier, opts in d["talentOptions"].items() for o in opts]
        for c in d["circles"]:
            expected = 5 if c["circle"] == 1 else 1
            if len(c["disciplineTalents"]) != expected:
                r.error(where, f"circle {c['circle']} has {len(c['disciplineTalents'])} discipline talents")
            refs += [(f"circle {c['circle']}", x) for x in c["disciplineTalents"]]
            refs += [(f"circle {c['circle']} free", x) for x in c.get("freeTalents", [])]
            for a in c["abilities"]:
                if a["type"] == "defense" and "bonus" not in a:
                    r.error(where, f"circle {c['circle']}: unparsed defense bonus {a['text']!r}")
        for label, ref in refs:
            known = skill_ids if ref.get("kind") == "skill" else talent_ids
            if ref["ref"] not in known:
                r.error(where, f"{label}: unknown talent {ref['name']!r}")
        if "Thread Weaving" not in [x["name"] for x in d["circles"][0]["disciplineTalents"]]:
            r.error(where, "no Thread Weaving at First Circle")

    for race in races:
        where = f"race {race['name']}"
        if set(race["startingAttributes"]) != ATTRIBUTES:
            r.error(where, "starting attributes incomplete")
        if not race.get("abilities") or not all(a.get("text") for a in race["abilities"]):
            r.error(where, "racial abilities without rules text")
        for a in race.get("abilities", []):
            if a.get("talentRef") and a["talentRef"] not in talent_ids:
                r.error(where, f"unknown talent {a['talentRef']}")

    if [s["step"] for s in step_dice] != list(range(1, 41)):
        r.error("step-dice", "steps must be 1-40")
    for s in step_dice:
        if not re.fullmatch(r"(\d?D(4|6|8|10|12|20))(\+\d?D(4|6|8|10|12|20))*([+-]\d)?", s["dice"]):
            r.error("step-dice", f"step {s['step']}: bad dice {s['dice']!r}")
    if [v["value"] for v in attribute_table] != list(range(1, 31)):
        r.error("attribute-table", "values must be 1-30")
    steps = [v["step"] for v in attribute_table]
    if steps != sorted(steps):
        r.error("attribute-table", "steps must not decrease")

    for w in r.warnings:
        print("warning:", w)
    for e in r.errors:
        print("ERROR:", e)
    print(f"{len(talents)} talents, {len(skills)} skills, {len(disciplines)} disciplines, "
          f"{len(races)} races: {len(r.errors)} errors, {len(r.warnings)} warnings")
    return 1 if r.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent.parent / "data"))
