# Earthdawn Companion — Cahier des charges

> Version 0.4 — 2026-10-12
> Les points marqués **[À CONFIRMER]** attendent encore une décision.

## 1. Contexte et objectif

Je joue à **Earthdawn 4e édition (FASA, livres en anglais)** avec un carnet papier et le
*Player's Guide*. Pendant les parties, retrouver un talent, son attribut, son action, sa
fatigue et les dés à lancer demande de feuilleter le livre et de faire des calculs.

**Objectif :** une application Android qui sert de :
1. **Banque de talents et de compétences** consultable rapidement, hors ligne.
2. **Fiche de personnage simplifiée** : je saisis mes attributs et mes rangs, l'app me dit
   quel Step et quels dés lancer.

L'app sera partagée avec les autres joueurs du groupe : **toutes les disciplines** du
*Player's Guide* doivent donc être prises en charge, pas seulement la mienne
(Weaponsmith, cercle 2).

## 2. Utilisateurs et contexte d'usage

- Les joueurs du groupe, sur smartphone **Android**, autour de la table, souvent d'une
  seule main.
- Consultations courtes et fréquentes : « Je lance quoi pour Forge Weapon ? »
- Pas de connexion garantie → **fonctionnement 100 % hors ligne**.
- **Les dés sont lancés à la main** : l'app indique les dés, elle ne les lance pas.

## 3. Périmètre fonctionnel

### 3.1 V1 — MVP

#### F1. Banque de talents
- Liste des ~150 talents du *Player's Guide* (chapitre Talents).
- Fiche détaillée de chaque talent :
  - Nom
  - **Step** : formule (`Rank+DEX`, `Rank+PER`, `Rank` seul, `NA`…)
  - **Action** : Standard / Simple / Free / Sustained / NA
  - **Strain** (fatigue)
  - **Skill Use** : Oui/Non + palier (Novice / Journeyman / Warden / Master)
  - Description (règles), avec la note sur la version non magique le cas échéant
  - **Disciplines qui y ont accès** et à quel cercle ou palier (déduit des données
    des disciplines)
  - Page du livre
- Recherche par nom (tolérante : « forge » → Forge Weapon, Forge Armor).
- Filtres : discipline, attribut lié, type d'action, strain > 0, utilisable comme
  compétence.

#### F2. Banque de compétences
- Compétences du chapitre Skills (~24 entrées propres), classées par type :
  **Artisan, General, Knowledge, Language**.
- Les talents marqués `Skill Use: Yes` sont aussi trouvables comme compétences, avec un
  lien vers la fiche du talent.
- Même fiche et mêmes filtres que les talents, plus un filtre par type de compétence.

#### F3. Banque de disciplines
- Les 15 disciplines du *Player's Guide*, avec pour chacune :
  - Important Attributes, Karma Ritual, Artisan Skills, Half-Magic
  - Talent Options du palier Initiate
  - Par cercle (1 à 8) : Durability, talents de discipline, talent gratuit éventuel et
    capacités (karma, bonus de défense, armure mystique, pouvoirs spéciaux)
  - Talent Options du palier Journeyman
- Depuis la fiche d'une discipline, on ouvre directement la fiche de ses talents.

#### F3 bis. Banque de races
- Les 8 races : maturité, espérance de vie, taille, poids, mouvement, modificateur de
  karma, attributs de départ et capacités raciales (`data/races.json`).

#### F4. Favoris
- Une étoile sur chaque fiche pour l'ajouter ou la retirer des favoris.
- Un onglet « Favoris » accessible en un geste.

#### F5. Mon personnage (un seul personnage en V1)
- Saisie : nom, **race**, **discipline**, **cercle**.
- La race ajoute automatiquement ses **capacités raciales** : Heat Sight, Low-Light
  Vision, Versatility, Astral Sight, Flight, Gahad, Tail Combat, Living Armor… Les
  bonus chiffrés (+2 Physical Defense du windling, +3 Wound Threshold et +3 Physical
  Armor de l'obsidiman, +2 STR pour la charge du nain) sont appliqués aux
  caractéristiques. Les talents raciaux (ex. Astral Sight) sont ajoutés avec
  `source: racial`, donc sans karma.
- Saisie des **6 attributs** (DEX, STR, TOU, PER, WIL, CHA), puis calcul automatique
  depuis la table des attributs (§4) :
  - l'Attribute Step de chaque attribut ;
  - les caractéristiques dérivées, en lecture seule : défenses physique, mystique et
    sociale, charge, seuils d'inconscience, de mort et de blessure, tests de
    récupération, armure mystique.
- Quand on choisit la discipline et le cercle, l'app **propose les talents de
  discipline** auxquels le personnage a accès et ajoute ceux qu'on coche.
- Ajout libre de talents (Talent Options, Versatility…) et de compétences depuis la
  banque, avec leur **rang** (0–15).
- Pour chaque talent ou compétence possédé :
  **Step final = Attribute Step + Rang** (ou `Rang` seul selon la formule),
  converti en **dés** avec la *Step/Action Dice Table* (ex. Step 9 → D8+D6).
- Indicateur karma : peut-on dépenser du karma sur ce talent ? (oui pour un talent de la
  discipline du personnage, non pour une compétence, un talent racial ou un talent
  appris par Versatility)
- Rappel des capacités de discipline acquises, par exemple Weaponsmith C1 :
  « Karma sur les tests de fabrication ou de réparation ».
- Ajustement manuel optionnel du Step (bonus ou malus d'objet, de sort, de blessure).

#### F6. Hors ligne et sauvegarde
- Les données de règles sont **intégrées à l'application**.
- Le personnage est sauvegardé localement sur le téléphone.
- **Export/import** du personnage en fichier JSON, via le menu « Partager » d'Android
  (sauvegarde, changement de téléphone, envoi au MJ).

### 3.2 V2 — Évolutions envisagées
- **Suivi en partie** : dégâts actuels, blessures, points de karma, fatigue cumulée.
- **Points de Légende** : coût du rang suivant selon le cercle ou le palier.
- **Assistant de création de personnage** : race, 25 points d'attributs, valeurs
  raciales, 8 rangs de talents, compétences de départ (données déjà présentes sur la
  fiche de création).
- Plusieurs personnages.
- Sorts, équipement, notes de session.
- Lanceur de dés (dés explosifs, karma), seulement si le besoin apparaît.
- Interface en français (les textes de règles restent en anglais).

### 3.3 Hors périmètre
- Outils pour le MJ (créatures, rencontres).
- Synchronisation en ligne et comptes utilisateurs.
- Publication publique sur un store.

## 4. Règles de calcul

- **Talent ou Skill Step** = Rang + Attribute Step indiqué par la formule `Step:`.
  Exemple du livre : PER Step 6 + Spellcasting rang 3 → Step 9 → **D8+D6**.
- **Attribute Step et caractéristiques dérivées** : `data/attribute-table.json`
  (valeurs d'attribut 1 à 30), transcrit depuis la fiche de création 4e de K. Scott.

  | Colonne | Attribut source |
  |---|---|
  | Defense | DEX (physique), PER (mystique), CHA (sociale) |
  | Carry | STR |
  | Uncon, Death, Wound, Recov | TOU |
  | Mystic Armor | WIL |

  Les lignes 28 à 30 (défense 16 trois fois, charge 530 deux fois) sont conformes : peu
  de valeurs changent sur les derniers niveaux.
- **Step/Action Dice Table** : `data/step-dice.json` (Steps 1 à 40).
- Les bonus de discipline (Durability, défenses par cercle) s'ajoutent aux
  caractéristiques dérivées.

Ces tables sont des **fichiers de données**, pas du code en dur.

## 5. Données

### 5.1 Sources
| Fichier | Contenu | Pages du livre |
|---|---|---|
| `Talents.pdf` | *Player's Guide* 4e, chapitre Talents | 119–181 |
| `Skills.pdf` | *Player's Guide* 4e, chapitre Skills | 183–201 |
| `Disciplines.pdf` | *Player's Guide* 4e, chapitre Disciplines (15 disciplines, cercles 1–8) | 79–118 |
| `Concepts_and_Races.pdf` | *Player's Guide* 4e, chapitres Concepts et Races | 31–56 |
| Image | Step/Action Dice Table | — |
| Image | Fiche de création 4e (table des attributs, races) | — |

Les PDF **ne sont pas** versionnés dans le dépôt.

### 5.2 Transcription en JSON ✅

Toutes les données de règles sont transcrites en fichiers JSON dans `data/`, puis
intégrées à l'app. L'app ne lit jamais les PDF.

| Fichier | Contenu |
|---|---|
| `data/talents.json` | 149 talents |
| `data/skills.json` | 23 compétences, liste des compétences par défaut, table « Talents Available as Skills » |
| `data/disciplines.json` | 15 disciplines × 8 cercles, talents optionnels Novice et Journeyman |
| `data/races.json` | 8 races, attributs de départ, capacités raciales (texte complet + effets chiffrés) |
| `data/step-dice.json` | Step → dés, Steps 1 à 40 |
| `data/attribute-table.json` | Valeur d'attribut → Step et caractéristiques dérivées, valeurs 1 à 30 |

Les PDF ont été produits par « Microsoft Print to PDF » et une partie du texte y est
dessinée en formes vectorielles : les formules `Step:`, certains titres et les lignes
contenant des ligatures (`fl`, `fi`) sont absents du texte extractible. La chaîne de
transcription (`tools/`, voir `tools/README.md`) est donc :

1. rendu des pages en image (300 dpi) puis **OCR** (Tesseract) ;
2. découpage automatique en fiches (talents, compétences, disciplines, races) ;
3. **corrections manuelles** versionnées dans `tools/overrides/*.json`, faites en lisant
   les pages concernées : encadrés et tableaux sur deux colonnes, textes autour des
   illustrations (une vingtaine de fiches) ;
4. **script de validation** `tools/validate_data.py` :
   - chaque talent cité par une discipline (cercles, options, talents gratuits) existe ;
   - chaque fiche a un Step valide, une action, un strain, une page ;
   - le palier « Skill Use » de chaque talent concorde avec la table « Talents Available
     as Skills » du chapitre Skills (contrôle croisé entre deux chapitres) ;
   - chaque discipline a 8 cercles, 5 talents au cercle 1 puis 1 par cercle, Thread
     Weaving au cercle 1 ;
   - les tables Step → dés et attributs sont complètes ;
   - avertissement sur les paragraphes qui ne finissent pas une phrase et les caractères
     suspects.

État : **0 erreur**, 1 avertissement attendu (bloc de statistiques de Spirit Mount).
Les textes d'ambiance des races sont omis (trop bruités par les illustrations, inutiles
pour l'app).

### 5.3 Modèle de données

Les descriptions sont des listes de paragraphes ; un paragraphe qui commence par `## `
est un intertitre. Les tableaux des fiches sont structurés dans `tables`.

```jsonc
// data/talents.json → { "talents": [ … ] }
{
  "id": "forge-weapon",
  "name": "Forge Weapon",
  "step": { "attribute": "PER", "bonus": 0 },  // Step = Rang + attribut + bonus ; attribute null si "Rank" seul ; step null si NA
  "action": "Sustained",                        // Standard | Simple | Free | Sustained | NA
  "actionNote": null,                           // "see text" quand le livre renvoie au texte
  "strain": 0,
  "strainNote": null,
  "skillUse": { "allowed": false, "tier": null, "note": null },  // tier : Novice | Journeyman | Warden | Master
  "nonMagicalNote": null,                       // différences de la version compétence
  "page": 148,
  "description": [ "The adept performs a ritual…", "## Dialects", "…" ],
  "tables": [ { "title": "…", "columns": ["…"], "rows": [["…"]], "footnote": "…" } ]  // optionnel
}

// data/skills.json → { "defaultSkills": [ids], "talentsAsSkills": { "Novice": [noms], "Journeyman": [noms] }, "skills": [ … ] }
{
  "id": "craft-armor", "name": "Craft Armor",
  "step": { "attribute": "PER", "bonus": 0 }, "action": "Sustained", "strain": 0,
  "cost": "Novice",                             // palier de coût en Points de Légende
  "skillType": "General",                       // Artisan | General | Knowledge | Language
  "usableAsArtisan": true,
  "default": false,                             // utilisable sans rang (Default Skill Table)
  "page": 194, "description": [ "…" ]
}

// data/disciplines.json → { "disciplines": [ … ] }
{
  "id": "weaponsmith", "name": "Weaponsmith",
  "description": "…", "importantAttributes": ["PER", "WIL", "CHA"],
  "karmaRitual": "…", "artisanSkills": ["Rune Carving", "Wood Carving"], "halfMagic": "…",
  "durability": 5,                              // ajouté à chaque cercle
  "notes": [ { "name": "Mount", "text": "…" } ],  // optionnel (Beastmaster, Cavalryman)
  "talentOptions": {
    "Novice":     [ { "ref": "avoid-blow", "name": "Avoid Blow" }, … ],
    "Journeyman": [ { "ref": "battle-shout", "name": "Battle Shout" }, … ]
  },
  "circles": [
    {
      "circle": 1,
      "freeTalents": [ { "ref": "craftsman", "name": "Craftsman", "kind": "skill", "note": "…" } ],
      "disciplineTalents": [ { "ref": "forge-weapon", "name": "Forge Weapon" },
                             { "ref": "thread-weaving", "name": "Thread Weaving", "variant": "Thread Smithing" } ],
      "abilities": [ { "type": "karma", "name": "Karma", "text": "The adept can spend a Karma Point on any test to craft or repair an item." } ]
    },
    {
      "circle": 2,
      "disciplineTalents": [ { "ref": "conversation", "name": "Conversation" } ],
      "abilities": [ { "type": "defense", "name": "Defense", "defense": "mystic", "bonus": 1, "text": "…" } ]
    }
  ]
}
// Types de capacités : karma, defense (+defense, bonus), recovery, initiative, mystic-armor (+bonus),
// free-talent (amélioration de matrice), et capacités nommées (traveling-smithy, collaborate…).

// data/races.json → { "races": [ … ] }
{
  "id": "windling", "name": "Windling", "page": 53,
  "maturity": "30", "lifespan": "170", "height": "18\"", "weight": 13,
  "movement": { "ground": 6, "flight": 16 }, "karmaModifier": 6,
  "startingAttributes": { "DEX": 11, "STR": 4, "TOU": 8, "PER": 11, "WIL": 10, "CHA": 12 },
  "abilities": [
    { "name": "Astral Sight", "talentRef": "astral-sight", "text": "…" },
    { "name": "Increased Physical Defense", "effects": [ { "stat": "physicalDefense", "bonus": 2 } ], "text": "…" }
  ]
}

// data/step-dice.json         → { "steps": [ { "step": 9, "dice": "D8+D6" }, … ] }
// data/attribute-table.json   → { "values": [ { "value": 12, "step": 5, "defense": 7, … } ] }

// Personnage (stockage local + export)
{
  "schemaVersion": 1,
  "name": "…", "race": "…", "discipline": "weaponsmith", "circle": 2,
  "attributes": { "DEX": 0, "STR": 0, "TOU": 0, "PER": 0, "WIL": 0, "CHA": 0 },
  "abilities": [ { "ref": "forge-weapon", "kind": "talent", "rank": 3, "source": "discipline", "modifier": 0 } ],
  "favorites": [ "forge-weapon", "melee-weapons" ]
}
```

`source` vaut `discipline`, `option`, `versatility`, `racial` ou `skill`. C'est ce
champ qui détermine si le karma est possible.

## 6. Interface (mobile)

Navigation par barre d'onglets en bas de l'écran :

| Onglet | Contenu |
|---|---|
| ⭐ **Favoris** | Écran d'accueil : mes favoris avec leur Step et leurs dés, en grand |
| 🧙 **Personnage** | Attributs, caractéristiques, mes talents et compétences avec rang, Step et dés |
| 📖 **Banque** | Recherche et filtres dans les talents, compétences et disciplines |
| ⚙️ **Réglages** | Export/import, thème clair ou sombre, à propos |

Principes :
- Le Step et les dés sont toujours visibles sans ouvrir la fiche.
- Modifier un rang se fait directement dans la liste avec des boutons − et +.
- Thème sombre par défaut (parties en soirée), texte lisible.
- Gros boutons, utilisables d'une main.

## 7. Choix techniques

### 7.1 Plateforme : .NET MAUI (Android)

Décision : **.NET MAUI**, ciblant **Android** en V1, plutôt qu'une PWA.

| | .NET MAUI | PWA |
|---|---|---|
| Maîtrise de la techno | ✅ utilisée au travail | à apprendre ou à réapprendre |
| Hors ligne | ✅ natif | via service worker |
| Données protégées par le droit d'auteur | ✅ intégrées à l'APK, rien n'est publié | ❌ demande un hébergement à accès restreint |
| Distribution Android | APK à envoyer, ou test fermé Play Console (25 $ une fois) | un lien |
| iPhone | ❌ Mac + compte Apple Developer (99 $/an) | ✅ |
| Build depuis une session Claude (Linux) | Android : oui (workload `maui-android`). Test sur ton téléphone. | oui |

**iPhone : hors périmètre pour le moment.** Pour garder une porte de sortie, la logique
métier et les données vivent dans une **bibliothèque .NET indépendante de MAUI** : une
version web Blazor pourra la réutiliser si besoin.

**Distribution : APK** envoyé directement aux joueurs (installation depuis une source
inconnue à autoriser sur Android). La CI produit l'APK signé en artefact téléchargeable.
La clé de signature est conservée hors du dépôt (secret GitHub Actions), car Android
refuse une mise à jour signée avec une autre clé.

### 7.2 Architecture

```
src/
  EarthdawnCompanion.Core/       // .NET class library : modèles, calcul Step→dés, chargement JSON, règles karma
  EarthdawnCompanion.App/        // .NET MAUI : vues XAML, ViewModels (CommunityToolkit.Mvvm), Shell + onglets
tests/
  EarthdawnCompanion.Core.Tests/ // xUnit : calculs, tables, validation des données
data/                            // JSON de règles (embarqués en ressources)
tools/                           // scripts de transcription et de validation
```

- Version .NET : LTS en cours (à fixer au démarrage du code).
- MVVM avec **CommunityToolkit.Mvvm**, navigation **Shell** avec `TabBar`.
- Données de règles : JSON en **ressources embarquées**, chargées au démarrage.
- Personnage : fichier JSON dans `FileSystem.AppDataDirectory`. Pas besoin de SQLite
  pour un seul personnage.
- Export/import : `Share` et `FilePicker` de MAUI Essentials.
- CI GitHub Actions : tests de `Core` + validation des données, et si possible build de
  l'APK en artefact téléchargeable.

## 8. Droits d'auteur et confidentialité

Les textes d'Earthdawn sont protégés (FASA). L'app est **à usage privé du groupe** :
- dépôt GitHub **privé** ;
- PDF sources non versionnés ;
- APK partagé uniquement au sein du groupe, pas de publication publique.

## 9. Décisions prises

| Sujet | Décision |
|---|---|
| Édition | Earthdawn 4e (FASA), textes en anglais |
| Plateforme | .NET MAUI, Android uniquement ; iPhone mis de côté |
| Distribution | APK partagé directement au groupe |
| Personnages | Un seul en V1 |
| Lanceur de dés | Non en V1, les dés sont lancés à la main |
| Disciplines | Toutes, pas seulement Weaponsmith |
| Races et talents raciaux | Inclus en V1 |
| Table des attributs, lignes 28–30 | Conformes au livre |

## 10. Plan de réalisation

1. ✅ Cahier des charges v0.3, tables Step→dés, attributs et races en JSON.
2. ✅ **Données** : transcription de `talents.json`, `skills.json`, `disciplines.json` et
   des capacités raciales, script de validation. Relecture humaine au fil de l'usage.
3. **Squelette** : solution .NET (Core + App + Tests), CI, chargement des données.
4. **Banque** : listes, recherche, filtres, fiches, favoris.
5. **Personnage** : attributs, discipline et cercle, talents, calcul Step → dés,
   export/import.
6. Installation sur ton téléphone, test en partie, ajustements.
7. V2 selon les retours.
