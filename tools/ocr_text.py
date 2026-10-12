"""Shared helpers to load and clean the OCR text of the rulebook PDFs.

The PDFs were produced with "Microsoft Print to PDF": part of their text is drawn as
vector shapes, so text extraction misses it. Pages are rendered and OCRed instead:

    pdftoppm -r 300 -gray -png Talents.pdf ocr/talents/p
    OMP_THREAD_LIMIT=1 tesseract ocr/talents/p-01.png ocr/talents/p-01.png.ocr -l eng
"""
import re
from collections import Counter
from pathlib import Path

FOOTER = re.compile(r"^\s*(GE:?\s*\d{1,3}|\d{1,3}\s*GE:?|[^\w]*(?:\w\s+)?\d{1,3}(?:\s+\W*\w?)?\W*|EARTHDAWN|E ?A ?R ?T ?H ?D ?A ?W ?N)\s*$")
PAGE_NUMBER = re.compile(r"^(?=.{2,10}$)\D*?(\d{2,3})\D*$")

FIXES = [
    ("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
    ("ﬁ", "fi"), ("ﬂ", "fl"), ("—", "—"),
]


# Words the OCR glued together or misread, found by checking against a dictionary.
WORD_FIXES = {
    "anumber": "a number", "orkawrysmile": "ork a wry smile", "halfhour": "half hour",
    "agaist": "against", "maintainted": "maintained", "ona": "on a", "ina": "in a",
    "untilheimproves": "until he improves", "mustbeused": "must be used", "Itis": "It is",
}


def fix_words(text):
    text = re.sub(r"(?<=[.,;:!?\"]) +[=|~_] +", " ", text)  # stray marks between words
    return re.sub(r"[A-Za-z]+", lambda m: WORD_FIXES.get(m.group(0), m.group(0)), text)


def is_noise(line, vocabulary):
    """OCR garbage from illustrations ("SAF "if er A ; at iy ty", ". a ~ a a ~").

    Lines holding digits are kept (stat blocks, table rows). Other lines are dropped
    when most of their words are neither common in the chapter nor word-shaped.
    """
    line = line.strip()
    if not line or re.search(r"\d", line):
        return False
    visible = line.replace(" ", "")
    if sum(c.isalpha() for c in visible) < 0.4 * len(visible):
        return True
    words = re.findall(r"[A-Za-z]+", line)
    real = sum(vocabulary.get(w.lower(), 0) >= 3
               or (len(w) >= 4 and re.search(r"[aeiouy]", w.lower()) and (w.islower() or w.istitle()))
               for w in words)
    return real < 0.5 * len(words)


def load_pages(ocr_dir):
    """Return [(book_page, [lines])] for every OCRed page, in order."""
    files = sorted(Path(ocr_dir).glob("p-*.png.ocr.txt"),
                   key=lambda p: int(re.search(r"p-(\d+)", p.name).group(1)))
    texts = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        for a, b in FIXES:
            text = text.replace(a, b)
        texts.append(text)
    vocabulary = Counter(w.lower() for t in texts for w in re.findall(r"[A-Za-z]+", t))
    pages, offsets = [], Counter()
    for index, text in enumerate(texts, start=1):
        lines = text.splitlines()
        # Footers carry the book page number ("GE 123", "& 191"); keep the usual offset.
        for line in lines[-6:]:
            m = PAGE_NUMBER.match(line)
            if m:
                offsets[int(m.group(1)) - index] += 1
        pages.append((index, [l.rstrip() for l in lines if not FOOTER.match(l) and not is_noise(l, vocabulary)]))
    offset = offsets.most_common(1)[0][0] if offsets else 0
    return [(offset + i, lines) for i, lines in pages]


def to_paragraphs(lines):
    """Join OCR lines into paragraphs, undoing end-of-line hyphenation."""
    paragraphs, current = [], ""
    for raw in lines:
        line = raw.strip()
        if not line:
            # Tesseract leaves a blank line between paragraphs, but also at page breaks:
            # only close the paragraph if it ends a sentence or is a short heading.
            if current and (re.search(r"[.!?:)\"]$", current) or len(current) < 40):
                paragraphs.append(current)
                current = ""
            continue
        if not current:
            current = line
        elif current.endswith("-") and line[:1].islower():
            current = current[:-1] + line
        elif current.endswith("-") and not current.endswith(" -"):
            current += line  # "Low-" + "Light Vision"
        else:
            current += " " + line
        # A short line ending a sentence closes the paragraph.
        if len(line) < 70 and re.search(r"[.!?:)\"]$", line):
            paragraphs.append(current)
            current = ""
    if current:
        paragraphs.append(current)
    return [fix_words(p) for p in paragraphs]
