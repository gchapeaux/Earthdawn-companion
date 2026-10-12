# Earthdawn Companion — Cahier des charges

> Version 0.2 — 2026-10-12
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

#### F4. Favoris
- Une étoile sur chaque fiche pour l'ajouter ou la retirer des favoris.
- Un onglet « Favoris » accessible en un geste.

#### F5. Mon personnage (un seul personnage en V1)
- Saisie : nom, race, **discipline**, **cercle**.
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

  ⚠️ Les lignes 28 à 30 de la fiche semblent contenir des coquilles : défense 16 trois
  fois et charge 530 deux fois. **[À VÉRIFIER dans le livre]**
- **Step/Action Dice Table** : `data/step-dice.json` (Steps 1 à 40).
- Les bonus de discipline (Durability, défenses par cercle) s'ajoutent aux
  caractéristiques dérivées.

Ces tables sont des **fichiers de données**, pas du code en dur.

## 5. Données

### 5.1 Sources
| Fichier | Contenu | Pages |
|---|---|---|
| `Talents.pdf` | *Player's Guide* 4e, chapitre Talents | 63 |
| `Skills.pdf` | *Player's Guide* 4e, chapitre Skills | 19 |
| `Disciplines.pdf` | *Player's Guide* 4e, chapitre Disciplines (15 disciplines, cercles 1–8) | 40 |
| Image | Step/Action Dice Table | — |
| Image | Fiche de création 4e (table des attributs, races) | — |

Les PDF **ne sont pas** versionnés dans le dépôt.

### 5.2 Transcription en JSON
Toutes les données de règles sont transcrites **une fois** en fichiers JSON dans
`data/`, puis intégrées à l'app. L'app ne lit jamais les PDF.

Points d'attention : les PDF ont été produits par « Microsoft Print to PDF » et leur
couche texte est **incomplète** :
- les formules `Step:` (ex. `Rank+DEX`) et certains intertitres (« Initiate Talent
  Options ») manquent dans le texte extrait ;
- les lignes qui contiennent des ligatures (`fl`, `fi`…) sont parfois perdues.

Méthode de transcription :
1. extraction du texte ;
2. lecture des pages rendues en image pour combler les trous ;
3. **script de validation** :
   - chaque talent cité par une discipline existe dans `talents.json` ;
   - chaque talent a une formule de Step, une action et un strain ;
   - aucune description ne se termine en milieu de phrase ;
4. relecture humaine ciblée : liste des fiches signalées par le script.

### 5.3 Modèle de données

```jsonc
// data/talents.json
{
  "id": "forge-weapon",
  "name": "Forge Weapon",
  "step": { "attribute": "PER", "rank": true },   // attribute: null si "Rank" seul ; step: null si NA
  "action": "Sustained",                           // Standard | Simple | Free | Sustained | NA
  "strain": 0,
  "skillUse": { "allowed": true, "tier": "Journeyman" },
  "description": "…",
  "nonMagicalNote": null,
  "page": 0
}

// data/skills.json
{
  "id": "craft-armor",
  "name": "Craft Armor",
  "skillType": "Artisan",                          // Artisan | General | Knowledge | Language
  "step": { "attribute": "PER", "rank": true },
  "action": "Sustained",
  "strain": 0,
  "description": "…",
  "page": 0
}

// data/disciplines.json
{
  "id": "weaponsmith",
  "name": "Weaponsmith",
  "importantAttributes": ["CHA", "PER", "WIL"],
  "karmaRitual": "…",
  "artisanSkills": ["Rune Carving", "Wood Carving"],
  "halfMagic": "…",
  "talentOptions": {
    "Initiate":   ["avoid-blow", "awareness", "danger-sense", "…"],
    "Journeyman": ["battle-shout", "diplomacy", "…"]
  },
  "circles": [
    {
      "circle": 1,
      "durability": 5,
      "freeTalent": { "ref": "craftsman", "note": "…" },
      "disciplineTalents": ["forge-weapon", "item-history", "melee-weapons",
                            "steel-thought", { "ref": "thread-weaving", "variant": "Thread Smithing" }],
      "abilities": [ { "type": "karma", "text": "Karma on any test to craft or repair an item" } ]
    },
    {
      "circle": 2,
      "disciplineTalents": ["conversation"],
      "abilities": [ { "type": "defense", "defense": "mystic", "bonus": 1 } ]
    }
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

Le seul vrai inconvénient de MAUI est l'iPhone. Pour garder une porte de sortie, la
logique métier et les données vivent dans une **bibliothèque .NET indépendante de
MAUI** : si un joueur a un iPhone un jour, une version web Blazor pourra la réutiliser.
**[À CONFIRMER : aucun joueur du groupe n'a d'iPhone ?]**

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

## 9. Questions ouvertes

1. Un joueur du groupe a-t-il un iPhone ? (impact sur §7.1)
2. Distribution : APK envoyé directement, ou test fermé Play Console ?
3. Vérifier les lignes 28–30 de la table des attributs dans le livre.
4. Les talents raciaux (ex. Astral Sight du windling) et les règles de race sont-ils
   utiles en V1 ?

## 10. Plan de réalisation

1. ✅ Cahier des charges v0.2, tables Step→dés et attributs en JSON.
2. **Données** : transcription de `talents.json`, `skills.json` et `disciplines.json`,
   script de validation, relecture.
3. **Squelette** : solution .NET (Core + App + Tests), CI, chargement des données.
4. **Banque** : listes, recherche, filtres, fiches, favoris.
5. **Personnage** : attributs, discipline et cercle, talents, calcul Step → dés,
   export/import.
6. Installation sur ton téléphone, test en partie, ajustements.
7. V2 selon les retours.
