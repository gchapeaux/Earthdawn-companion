# Earthdawn Companion — Cahier des charges

> Version 0.1 (brouillon) — 2026-10-12
> Statut : en cours de rédaction, les points marqués **[À CONFIRMER]** attendent une réponse.

## 1. Contexte et objectif

Je joue à **Earthdawn 4e édition (FASA, livres en anglais)** avec un carnet papier et le
*Player's Guide*. Pendant les parties, retrouver un talent, son attribut, son action, sa
fatigue et le dé à lancer demande de feuilleter le livre et de faire des calculs.

**Objectif :** une application sur téléphone qui sert de :
1. **Banque de talents et de compétences** consultable rapidement, hors ligne.
2. **Fiche de personnage simplifiée** : je saisis mes attributs et mes rangs, l'app me dit
   quel Step et quels dés lancer.

Usage strictement personnel (voir §8).

## 2. Utilisateur et contexte d'usage

- Un joueur, sur smartphone, autour de la table, souvent d'une seule main.
- Consultations courtes et fréquentes : « Je lance quoi pour Air Dance ? »
- Pas de connexion garantie → **fonctionnement 100 % hors ligne**.

## 3. Périmètre fonctionnel

### 3.1 V1 — MVP

#### F1. Banque de talents
- Liste des ~150 talents du *Player's Guide* (chapitre Talents).
- Fiche détaillée de chaque talent :
  - Nom
  - **Step** : formule (`Rank+DEX`, `Rank+PER`, `Rank` seul, `NA`…)
  - **Action** : Standard / Simple / Free / Sustained / NA
  - **Strain** (fatigue) : nombre
  - **Skill Use** : Oui/Non + palier (Novice / Journeyman / Warden / Master)
  - Description (règles), avec la note sur la version non magique le cas échéant
  - Page du livre
- Recherche par nom (tolérante : « air d » → Air Dance, Air Sailing…).
- Filtres : attribut lié, type d'action, strain > 0, utilisable comme compétence.

#### F2. Banque de compétences
- Compétences du chapitre Skills (~24 entrées propres), classées par type :
  **Artisan, General, Knowledge, Language**.
- Les talents marqués `Skill Use: Yes` sont aussi trouvables comme compétences, avec
  un lien vers la fiche du talent.
- Même fiche et mêmes filtres que les talents, plus un filtre par type de compétence.

#### F3. Favoris
- Une étoile sur chaque fiche pour l'ajouter ou la retirer des favoris.
- Un onglet « Favoris » accessible en un geste depuis l'écran d'accueil.

#### F4. Mon personnage
- Saisie : nom, race, discipline, cercle.
- Saisie des **6 attributs** (DEX, STR, TOU, PER, WIL, CHA) → calcul automatique de
  l'**Attribute Step** de chacun (table du livre).
- Ajout de talents et de compétences depuis la banque, avec leur **rang** (0–15).
- Pour chaque talent ou compétence possédé :
  **Step final = Attribute Step + Rang** (ou `Rang` seul selon la formule),
  converti en **dés** avec la *Step/Dice Table* (ex. Step 9 → D8+D6).
- Indication visuelle : talent de discipline (karma possible) ou compétence (pas de karma).
- Ajustement manuel optionnel du Step (bonus ou malus d'objet, de sort, de blessure).

#### F5. Hors ligne et sauvegarde
- Toutes les données (banque + personnage) sont stockées sur le téléphone.
- **Export/import** du personnage en fichier JSON (sauvegarde ou changement de téléphone).

### 3.2 V2 — Évolutions envisagées
- **Lanceur de dés** : on touche un talent et l'app lance les bons dés, avec les dés
  explosifs (on relance un dé qui fait son maximum), le dé de karma en option et la règle
  du 1.
- **Suivi en partie** : dégâts actuels, blessures, seuils d'inconscience et de mort,
  points de karma, fatigue cumulée sur le combat.
- **Points de Légende** : coût du rang suivant selon le cercle ou le palier.
- **Filtre par discipline et cercle** : nécessite les listes de talents du chapitre
  Disciplines (non fourni pour l'instant).
- Sorts, équipement, notes de session.
- Plusieurs personnages.
- Option d'interface en français (les textes de règles restent en anglais).

### 3.3 Hors périmètre
- Outils pour le MJ (créatures, rencontres).
- Synchronisation en ligne et comptes utilisateurs.
- Publication sur un store.

## 4. Règles de calcul (à vérifier contre le livre)

- **Talent Step** = Rang + Attribute Step indiqué par la formule `Step:` du talent.
  Exemple du livre : PER Step 6 + Spellcasting rang 3 → Step 9 → **D8+D6**.
- **Skill Step** : même principe.
- **Attribute Step** : dépend de la valeur de l'attribut, d'après la table du *Player's
  Guide*. **[À CONFIRMER : me fournir la page de la table Attribut → Step.]**
- **Step/Dice Table** : correspondance Step → dés, à saisir depuis le livre.
  **[À CONFIRMER : me fournir la page de la table, au moins jusqu'au Step 30.]**

Ces deux tables seront des **fichiers de données**, pas du code en dur, pour pouvoir les
corriger facilement.

## 5. Données

### 5.1 Source
- `Talents.pdf` (*Player's Guide* 4e, chapitre Talents, 63 pages)
- `Skills.pdf` (*Player's Guide* 4e, chapitre Skills, 19 pages)

### 5.2 Extraction : point d'attention
Le PDF a été produit par « Microsoft Print to PDF ». Sa couche texte est **incomplète** :
- les formules `Step:` (ex. `Rank+DEX`) n'apparaissent pas dans le texte extrait ;
- les lignes qui contiennent des ligatures (`fl`, `fi`…) sont parfois perdues.

L'extraction se fera donc en combinant le texte extrait et la **lecture des pages
rendues en image**, avec une relecture. Prévoir un écran ou un fichier pour signaler et
corriger les erreurs de saisie.

### 5.3 Modèle de données (proposition)

```jsonc
// talents.json
{
  "id": "air-dance",
  "name": "Air Dance",
  "kind": "talent",
  "step": { "attribute": "DEX", "rank": true },   // attribute: null si "Rank" seul ; step: null si NA
  "action": "Free",                                // Standard | Simple | Free | Sustained | NA
  "strain": 2,
  "skillUse": { "allowed": false, "tier": null },  // tier: Novice | Journeyman | Warden | Master
  "description": "…",
  "nonMagicalNote": null,
  "page": 124
}

// skills.json
{
  "id": "craft-armor",
  "name": "Craft Armor",
  "kind": "skill",
  "skillType": "Artisan",                          // Artisan | General | Knowledge | Language
  "step": { "attribute": "PER", "rank": true },
  "action": "Sustained",
  "strain": 0,
  "description": "…",
  "page": 0
}

// character (stockage local)
{
  "name": "…", "race": "…", "discipline": "…", "circle": 1,
  "attributes": { "DEX": 0, "STR": 0, "TOU": 0, "PER": 0, "WIL": 0, "CHA": 0 },
  "abilities": [ { "ref": "air-dance", "rank": 3, "modifier": 0 } ],
  "favorites": [ "air-dance", "avoid-blow" ]
}
```

## 6. Interface (mobile d'abord)

Navigation par barre d'onglets en bas de l'écran :

| Onglet | Contenu |
|---|---|
| ⭐ **Favoris** | Écran d'accueil : mes favoris avec leur Step et leurs dés, en grand |
| 🧙 **Personnage** | Attributs + liste de mes talents et compétences avec leur rang, leur Step et leurs dés |
| 📖 **Banque** | Recherche et filtres sur tous les talents et compétences |
| ⚙️ **Réglages** | Export/import, thème clair ou sombre |

Principes :
- Le Step et les dés sont toujours visibles sans ouvrir la fiche.
- Modifier un rang se fait directement dans la liste avec des boutons − et +.
- Thème sombre par défaut (parties en soirée), texte lisible.
- Gros boutons, utilisables d'une main.

## 7. Choix techniques (proposition)

- **PWA** (Progressive Web App) :
  - installable sur l'écran d'accueil, sur Android comme sur iOS ;
  - hors ligne grâce à un service worker ;
  - pas de store ni de compte développeur.
- Pile envisagée : **Vite + TypeScript + framework léger (Svelte ou React)**, stockage
  local via **IndexedDB**.
- Données de règles en **JSON** dans le dépôt (`data/`).
- Hébergement de l'app : voir §8. **[À CONFIRMER]**

## 8. Droits d'auteur et confidentialité

Les textes d'Earthdawn sont protégés (FASA). L'app est **à usage personnel** :
- dépôt GitHub **privé** ;
- les PDF sources **ne sont pas** versionnés dans le dépôt ;
- hébergement non public : GitHub Pages est public même pour un dépôt privé, selon le
  plan GitHub. Options : hébergement avec accès restreint, ou les données de règles
  sont importées sur le téléphone depuis un fichier et ne sont jamais publiées.
  **[À CONFIRMER]**

## 9. Questions ouvertes

1. Un seul personnage, ou plusieurs ?
2. Le lanceur de dés en V1 ou en V2 ?
3. Téléphone Android ou iPhone ?
4. Discipline, race et cercle de ton personnage (pour tester avec de vraies données) ?
5. Peux-tu fournir les pages du *Player's Guide* avec :
   - la table Attribut → Step,
   - la *Step/Dice Table*,
   - la liste des talents de ta discipline (chapitre Disciplines) ?
6. Hébergement : quelle option du §8 te convient ?

## 10. Plan de réalisation (proposition)

1. **Données** : extraire talents et compétences en JSON, puis relecture.
2. **Squelette PWA** : navigation, banque consultable hors ligne.
3. **Favoris + personnage** : calcul Step → dés.
4. **Export/import**, installation sur le téléphone, tests en partie.
5. V2 selon les retours.
