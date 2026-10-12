# Transcription des règles

Scripts qui produisent les fichiers de `data/` à partir des PDF du *Player's Guide* 4e.
Les PDF et les sorties OCR ne sont **pas** versionnés (droits d'auteur) : garde-les en
dehors du dépôt.

## Prérequis

```bash
sudo apt-get install -y poppler-utils tesseract-ocr wamerican   # wamerican : contrôle des mots
```

## 1. OCR

Le texte extractible des PDF est incomplet (formules `Step:` et titres dessinés en
vectoriel), d'où l'OCR. `OMP_THREAD_LIMIT=1` évite que les processus Tesseract parallèles
se marchent dessus.

```bash
OCR=~/earthdawn-ocr        # hors du dépôt
for pair in talents:Talents skills:Skills disc:Disciplines races:Concepts_and_Races; do
  mkdir -p $OCR/${pair%%:*}
  pdftoppm -r 300 -gray -png "${pair#*:}.pdf" $OCR/${pair%%:*}/p
done
ls $OCR/*/p-*.png | OMP_THREAD_LIMIT=1 xargs -P 4 -I{} tesseract {} {}.ocr -l eng
```

## 2. Extraction (dans cet ordre)

```bash
python3 tools/extract_talents.py     $OCR/talents data/talents.json
python3 tools/extract_skills.py      $OCR/skills  data/skills.json        # lit talents.json
python3 tools/extract_disciplines.py $OCR/disc    data/talents.json data/disciplines.json
python3 tools/extract_races.py       $OCR/races   data/races.json         # complète races.json
python3 tools/validate_data.py
```

`data/step-dice.json`, `data/attribute-table.json` et la base de `data/races.json`
(moyennes, attributs de départ) viennent de la table des dés et de la fiche de création :
ils ont été saisis à la main.

## Corrections manuelles

`tools/overrides/*.json` contient les corrections faites en relisant les pages : tableaux
et encadrés sur deux colonnes, textes autour des illustrations, fiches fusionnées par
l'OCR. Les index de `replace` portent sur les paragraphes bruts de l'OCR.

Pour corriger une erreur trouvée en jeu : ajoute une entrée dans l'override du fichier
concerné, relance l'extraction puis `validate_data.py`.

| Fichier | Rôle |
|---|---|
| `ocr_text.py` | Chargement des pages OCR, numéros de page, filtre du bruit, paragraphes, mots recollés |
| `entries.py` | Découpage des fiches au format Step/Action/Strain (talents et compétences) |
| `extract_*.py` | Un script par fichier de données |
| `validate_data.py` | Contrôles de cohérence (sort en erreur si un contrôle échoue) |
