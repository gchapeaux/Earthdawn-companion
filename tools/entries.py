"""Split an OCRed rules chapter into entries with a Step/Action/Strain header.

Talents and skills share the same layout:

    Air Dance
    Step: Rank+DEX   Action: Free
    Strain: 2        Skill Use: No        (talents)
    Strain: 0        Cost: Novice         (skills)
    <description paragraphs>
"""
import json
import re
from pathlib import Path

from ocr_text import load_pages, to_paragraphs

ATTRS = {"DEX", "STR", "TOU", "PER", "WIL", "CHA"}
NOTE = r"\s*(?P<{0}>\(see text\))?"
STEP = re.compile(r"^Step:\s*(?P<step>Rank(?:\s*\+\s*[A-Za-z]{3})?(?:\s*\+\s*\d+)?|NA)\s*"
                  r"(?:Action:\s*(?P<action>\w+)" + NOTE.format("actionNote") + r")?\s*$")
ACTION = re.compile(r"^Action:\s*(?P<action>\w+)" + NOTE.format("actionNote") + r"\s*$")
STRAIN = re.compile(r"^Strain:\s*(?P<strain>\d+)" + NOTE.format("strainNote") +
                    r"\s*(?:(?:Skill Use|Cost):\s*(?P<rest>.*))?$")
SKILL_USE = re.compile(r"^Skill Use:\s*(?P<rest>.*)$")
COST = re.compile(r"^Cost:\s*(?P<rest>.*)$")
SPACES = re.compile(r"\s+")
TIERS = {"Novice", "Journeyman", "Warden", "Master"}


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower().replace("'", "")).strip("-")


def parse_step(text):
    text = SPACES.sub("", text).upper()
    if text in ("NA", ""):
        return None
    m = re.fullmatch(r"RANK(?:\+([A-Z]{3}))?(?:\+(\d+))?", text)
    if not m or (m.group(1) and m.group(1) not in ATTRS):
        raise ValueError(f"unknown step formula: {text}")
    return {"attribute": m.group(1), "bonus": int(m.group(2) or 0)}


def parse_skill_use(text):
    m = re.match(r"(Yes|No)\s*(?:\((\w+)\))?", (text or "").strip())
    if not m:
        return None
    return {"allowed": m.group(1) == "Yes", "tier": m.group(2) if m.group(2) in TIERS else None,
            "note": "see text" if "see text" in text else None}


def parse_cost(text):
    tier = (text or "").strip().split(" ")[0]
    return tier if tier in TIERS else None


def read_lines(ocr_dir):
    lines = []  # (book_page, line)
    for page, page_lines in load_pages(ocr_dir):
        lines += [(page, l) for l in page_lines]
    return lines


def extract_entries(lines):
    starts = [i for i, (_, l) in enumerate(lines) if STEP.match(l.strip())]
    entries = []
    for n, i in enumerate(starts):
        # The name is the closest non-blank line above the Step: line.
        j = i - 1
        while not lines[j][1].strip():
            j -= 1
        name, page = lines[j][1].strip(), lines[j][0]
        m = STEP.match(lines[i][1].strip())
        entry = {"id": slug(name), "name": name, "step": parse_step(m.group("step")),
                 "action": m.group("action"), "actionNote": "see text" if m.group("actionNote") else None,
                 "strain": None, "strainNote": None, "page": page}
        header = {}
        k = i + 1
        while k < len(lines):
            l = lines[k][1].strip()
            if not l:
                k += 1
                continue
            sm, um, cm, am = STRAIN.match(l), SKILL_USE.match(l), COST.match(l), ACTION.match(l)
            if sm:
                entry["strain"] = int(sm.group("strain"))
                entry["strainNote"] = "see text" if sm.group("strainNote") else None
                if sm.group("rest"):
                    header["Cost" if "Cost:" in l else "Skill Use"] = sm.group("rest")
            elif um:
                header["Skill Use"] = um.group("rest")
            elif cm:
                header["Cost"] = cm.group("rest")
            elif am and not entry["action"]:
                entry["action"] = am.group("action")
                entry["actionNote"] = "see text" if am.group("actionNote") else None
            else:
                break
            k += 1
        # The description runs until the next entry's name line.
        end = len(lines)
        if n + 1 < len(starts):
            end = starts[n + 1] - 1
            while not lines[end][1].strip():
                end -= 1
        body = lines[k:end]
        if not entry["action"]:
            # Two-column layout: the Action: line can land further down the page.
            for offset, (_, l) in enumerate(body[:40]):
                am = ACTION.match(l.strip())
                if am:
                    entry["action"] = am.group("action")
                    del body[offset]
                    break
        entry["_header"] = header
        entry["description"] = to_paragraphs([l for _, l in body])
        entries.append(entry)
    return entries


def apply_overrides(entries, overrides_file):
    overrides = json.loads(Path(overrides_file).read_text(encoding="utf-8"))
    entries.extend(overrides.get("_add", []))
    entries.sort(key=lambda e: e["name"])
    by_id = {e["id"]: e for e in entries}
    for entry_id, fix in overrides.items():
        if entry_id.startswith("_"):
            continue
        entry = by_id[entry_id]
        paragraphs = entry["description"]
        # Apply from the end so earlier indexes stay valid.
        for r in sorted(fix.get("replace", []), key=lambda r: r["from"], reverse=True):
            paragraphs[r["from"]:r["to"]] = r["with"]
        if "replaceFromText" in fix:
            start = next(i for i, p in enumerate(paragraphs) if p.startswith(fix["replaceFromText"]))
            paragraphs[start:] = fix["with"]
        if "dropFromText" in fix:
            start = next(i for i, p in enumerate(paragraphs) if p.startswith(fix["dropFromText"]))
            del paragraphs[start:]
        entry.update(fix.get("set", {}))
        if "tables" in fix:
            entry["tables"] = fix["tables"]


def mark_headings(paragraphs):
    """Short title-like paragraphs ("Dialects", "Finding Food") become "## " headings."""
    out = []
    for p in paragraphs:
        if len(p) < 40 and not re.search(r"[.!?:,;)\"]$", p) and p[:1].isupper() and not p.startswith("## "):
            p = "## " + p
        out.append(p)
    return out
