---
name: tailwind-css
description: Conçoit, organise et audite l’usage de Tailwind CSS dans un projet Django. À utiliser pour intégration Tailwind, classes utilitaires, design tokens, responsive, dark mode, composants visuels, détection des sources, build CSS, réduction des duplications, accessibilité et performance. S’intègre avec frontend-django et accessibility sans imposer Tailwind aux projets qui ne l’utilisent pas.
compatibility: opencode
metadata:
  framework: django
  css-framework: tailwindcss
  purpose: styling
  language: fr
  workflow-parent: project-workflow
---

# Tailwind CSS

## 1. Mission

Tu es responsable de l’usage propre, cohérent et maintenable de Tailwind CSS.

Ton objectif est de produire un frontend :

- lisible ;
- responsive ;
- cohérent visuellement ;
- accessible ;
- performant ;
- sans duplication excessive ;
- sans classes dynamiques impossibles à détecter ;
- sans surcouche CSS inutile.

Tailwind est un outil, pas une architecture.

---

## 2. Coordination

Avant toute modification :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. charge `frontend-django` ;
4. charge `accessibility` pour toute feature UI significative ;
5. charge `javascript` si l’interaction en nécessite ;
6. inspecte la version Tailwind et la stratégie de build existante.

Ne migre pas Tailwind v3 → v4 ou inversement sans décision explicite.

---

## 3. Vérifier la version

La configuration Tailwind dépend fortement de sa version.

Avant de modifier :

- package manifest ;
- lockfile ;
- fichier CSS d’entrée ;
- build command ;
- éventuel config JS ;
- intégration Vite/PostCSS/CLI.

Ne suppose pas qu’un tutoriel v3 correspond à un projet v4.

---

## 4. Tailwind v4

Pour un projet Tailwind v4, privilégie les mécanismes v4 :

- `@import "tailwindcss";`
- theme variables via `@theme`
- détection des classes par scanning des sources
- directives CSS modernes de Tailwind v4.

N’introduis pas automatiquement un vieux `tailwind.config.js` v3 si le projet n’en a pas besoin.

---

## 5. Tailwind v3

Si le projet est réellement en v3 :

respecte sa configuration existante.

Ne mélange pas syntaxe/configuration v4.

---

## 6. Installation

Choisis la méthode adaptée :

- Tailwind CLI ;
- PostCSS ;
- Vite ;
- intégration déjà présente.

Pour un Django server-rendered simple, Tailwind CLI peut être suffisant.

Ne rajoute pas Vite uniquement pour compiler Tailwind si aucun besoin frontend supplémentaire ne le justifie.

---

## 7. Node optionnel

La documentation Tailwind prévoit également un CLI standalone.

Si le projet cherche à éviter Node et que le workflow choisi le permet proprement, cette option peut être étudiée.

Ne crée pas une stack npm entière par réflexe.

---

## 8. Build

Le projet doit définir clairement :

### Développement

Compilation/watch.

### Production

Compilation minifiée/optimisée selon outil.

Documente les commandes réelles dans README/AGENTS.

---

## 9. Fichier d’entrée CSS

Utilise un point d’entrée clair.

Exemple :

```text
assets/css/app.css
```

ou convention déjà existante.

Évite plusieurs fichiers Tailwind racines sans raison.

---

## 10. Fichier généré

Le CSS généré doit être placé selon la stratégie static du projet.

Exemple :

```text
static/css/app.css
```

La décision de versionner ou non le CSS compilé dépend du pipeline.

Documente-la.

---

## 11. Source scanning

Tailwind génère les styles en détectant les classes utilisées dans les fichiers source.

Vérifie que les templates Django et fichiers JS pertinents sont détectés.

Une classe absente des sources détectées peut disparaître du build.

---

## 12. Classes dynamiques

Évite de construire des noms de classes arbitrairement :

```django
bg-{{ color }}-500
```

Tailwind peut ne pas détecter ce type de chaîne.

Préférer une table explicite :

```python
COLOR_CLASSES = {
    "success": "bg-green-600",
    "danger": "bg-red-600",
}
```

ou mapping côté template/JS approprié.

---

## 13. Pourquoi

Tailwind scanne les sources comme du texte.

Il ne comprend pas nécessairement la construction dynamique d’un nom de classe.

Les classes doivent apparaître sous une forme détectable.

---

## 14. Source explicite

Si certains fichiers nécessaires ne sont pas détectés automatiquement, configure les sources via les mécanismes adaptés à la version Tailwind.

Ne scanne pas tout le disque ou `node_modules`.

---

## 15. Packages externes

Si des templates/classes proviennent d’un package non détecté, ajoute explicitement la source selon les mécanismes Tailwind adaptés.

Ne safelist pas des milliers de classes par facilité.

---

## 16. Safelist

Une safelist doit être ciblée.

Bon usage :

- classes réellement générées par données contrôlées ;
- contenu provenant d’un système externe connu.

Mauvais usage :

- toute la palette ;
- toutes les tailles ;
- toutes les variantes.

---

## 17. Utility-first

Utilise les utilities directement lorsque cela reste lisible.

Évite de recréer systématiquement :

```css
.my-margin { ... }
.my-flex { ... }
```

qui reproduisent les utilities Tailwind.

---

## 18. Longues listes de classes

Une liste de classes longue n’est pas automatiquement mauvaise.

Mais si la même combinaison se répète de nombreuses fois, crée un composant/template réutilisable.

Ne remplace pas toutes les listes longues par du CSS custom.

---

## 19. Composants

La réutilisation doit prioritairement passer par :

- includes Django ;
- composants template ;
- macros/outillage existant ;
- fonctions frontend si pertinentes.

Tailwind recommande souvent de réutiliser via les composants de ton framework plutôt qu’en créant une classe CSS pour chaque motif.

---

## 20. `@apply`

Utilise `@apply` avec parcimonie.

Pertinent pour :

- styles difficiles à factoriser autrement ;
- intégration avec HTML tiers ;
- petite abstraction stable.

Mauvais usage :

reconstruire Bootstrap avec 200 classes `.btn-*`, `.card-*`, etc.

---

## 21. Classes sémantiques custom

Du CSS custom est acceptable lorsque :

- un composant externe impose une classe ;
- une règle CSS complexe est plus lisible ;
- un effet n’est pas pratique en utilities.

Ne transforme pas Tailwind en interdiction du CSS.

---

## 22. Design tokens

Centralise les décisions visuelles importantes :

- couleurs ;
- fonts ;
- spacing custom ;
- breakpoints custom ;
- shadows ;
- radius.

Avec Tailwind v4, privilégie les theme variables via `@theme` lorsque approprié.

---

## 23. Couleurs

Ne multiplie pas les couleurs arbitraires.

Définis une palette cohérente :

- primary ;
- neutral ;
- success ;
- warning ;
- danger.

Le nom exact dépend de la stratégie du projet.

---

## 24. Arbitrary values

Les valeurs arbitraires sont utiles :

```text
w-[37rem]
```

mais deviennent problématiques si elles sont partout.

Si une valeur se répète ou correspond à un token de design, ajoute-la au thème plutôt que la répéter.

---

## 25. Arbitrary properties

Même règle.

Utilise-les pour un besoin ponctuel, pas comme système principal.

---

## 26. Spacing

Préférer l’échelle Tailwind cohérente.

Évite :

```text
mt-[13px]
mb-[17px]
```

partout sans raison.

---

## 27. Typography

Définis une hiérarchie :

- titres ;
- body ;
- small ;
- labels.

Ne choisit pas taille/poids arbitrairement composant par composant.

---

## 28. Fonts

Si une font custom est réellement utilisée, configure-la dans le thème.

Analyse :

- performance ;
- fallback ;
- privacy ;
- chargement.

---

## 29. Responsive

Tailwind applique des variants responsive sur les utilities.

Conçois d’abord la mise en page petite largeur puis enrichis si cette stratégie correspond au projet.

---

## 30. Breakpoints

Utilise les breakpoints par défaut sauf besoin réel.

Ne crée pas un breakpoint différent pour chaque écran observé.

---

## 31. Mobile

Vérifie notamment :

- navigation ;
- formulaires ;
- cartes ;
- tables ;
- modales ;
- boutons.

Ne résous pas le mobile uniquement avec `hidden md:block`.

---

## 32. Containers

Utilise des largeurs/max-width cohérentes.

Évite des pages ayant chacune leur propre valeur arbitraire.

---

## 33. Grid vs flex

Utilise :

- flex pour axe principal simple ;
- grid pour dispositions bidimensionnelles.

Ne force pas grid ou flex par style personnel.

---

## 34. Dark mode

Ne crée un dark mode que si le projet le souhaite.

Tailwind supporte la variante `dark:` et permet de personnaliser la stratégie.

---

## 35. Dark mode système

Le comportement par défaut/choisi peut suivre `prefers-color-scheme`.

Si le projet veut un toggle manuel, implémente la stratégie documentée pour la version Tailwind.

---

## 36. Toggle 3 états

Si demandé :

```text
clair
sombre
système
```

peut être plus complet qu’un simple booléen.

Mais ne le complique pas si deux états suffisent.

---

## 37. Flash de thème

Si thème persistant côté navigateur, évite un flash clair/sombre au chargement si cela est visible.

Coordonne avec `javascript` et CSP.

---

## 38. Color scheme

Pour les contrôles natifs, utilise le `color-scheme` approprié lorsque nécessaire afin que les champs navigateur correspondent au thème.

---

## 39. Accessibilité couleurs

Toute couleur choisie doit respecter le contraste approprié.

Charge `accessibility`.

Ne suppose pas que toutes les couleurs Tailwind passent automatiquement selon taille/fond.

---

## 40. Focus

Chaque composant interactif doit avoir un style `focus-visible` perceptible.

Ne supprime pas les outlines sans alternative.

---

## 41. Hover

Ne conçois pas un état uniquement au hover.

Le clavier doit avoir un état focus équivalent.

---

## 42. Disabled

Les éléments désactivés doivent rester compréhensibles.

Évite un contraste tellement faible qu’ils deviennent invisibles.

---

## 43. États

Pour un composant important, définir :

- default ;
- hover ;
- focus ;
- active ;
- disabled ;
- error ;
- loading si pertinent.

---

## 44. Forms

Tailwind ne remplace pas la sémantique des formulaires.

Les classes servent au visuel.

Les labels, erreurs, `required` et validation restent gérés avec Django/HTML.

---

## 45. Form styles

Si le projet utilise un plugin officiel ou styles custom pour forms, garde une stratégie cohérente.

N’ajoute pas un plugin uniquement parce qu’un formulaire paraît brut si quelques utilities suffisent.

---

## 46. Typography plugin

Le plugin Typography peut être pertinent pour du contenu riche/Markdown.

Ne le charge pas pour du texte ordinaire.

---

## 47. Plugins

Avant tout plugin :

- officiel/maintenu ?
- nécessaire ?
- compatible version ?
- impact build ?
- alternative simple ?

---

## 48. Classes conditionnelles Django

Pour conditionner une classe :

```django
class="... {% if active %}bg-blue-600{% else %}bg-gray-100{% endif %}"
```

est acceptable si les classes complètes apparaissent dans le source.

---

## 49. Mapping Python

Pour plusieurs variantes, un mapping central peut être plus lisible.

Exemple conceptuel :

```python
BADGE_VARIANTS = {
    "success": "...",
    "warning": "...",
}
```

Ne mélange pas une logique métier complexe avec les classes.

---

## 50. Template filters pour classes

Évite de cacher toutes les classes dans des template filters opaques.

La structure visuelle doit rester retrouvable.

---

## 51. Component variants

Pour un composant réutilisable, documente les variantes supportées.

Exemple :

```text
button:
- primary
- secondary
- danger
```

Évite 20 variantes combinatoires.

---

## 52. Duplication

Cherche les combinaisons identiques répétées.

Si elles représentent le même composant, factorise le composant.

Si elles ne sont identiques que par hasard, ne crée pas une abstraction artificielle.

---

## 53. Class ordering

Si le projet utilise un formatter/plugin officiel adapté à Tailwind, il peut aider à standardiser l’ordre des classes.

Ne l’ajoute pas si cela impose une stack disproportionnée.

---

## 54. Prettier

Un plugin Prettier Tailwind peut être pertinent dans un projet utilisant déjà Prettier/Node.

Ne rajoute pas Prettier uniquement pour réordonner les classes d’un petit projet Django.

---

## 55. Lisibilité

Pour une classe énorme, structure le template plutôt que de concaténer du code illisible.

Ne coupe pas des attributs d’une manière incompatible avec le formatter/projet.

---

## 56. CSS custom global

Garde le CSS global minimal :

- imports ;
- theme ;
- base custom nécessaire ;
- composants exceptionnels.

Évite un `app.css` de milliers de lignes contournant Tailwind.

---

## 57. Preflight

Tailwind inclut des styles de base.

Comprends leur effet avant d’ajouter un gros reset CSS externe.

Ne combine pas plusieurs resets sans raison.

---

## 58. Contenu tiers

Pour HTML provenant d’un éditeur ou Markdown, les utilities ne peuvent pas forcément être ajoutées directement à chaque balise.

Le plugin Typography ou styles ciblés peuvent être pertinents.

---

## 59. Dynamic HTML

Si du HTML est généré depuis DB, ne génère pas arbitrairement des classes Tailwind à partir de données utilisateurs.

Cela peut créer sécurité, maintenance et build imprévisible.

---

## 60. XSS

Tailwind ne change rien aux règles XSS.

N’utilise pas `safe` pour permettre des classes/HTML utilisateur sans validation.

Charge `django-security`.

---

## 61. Content Security Policy

Tailwind compilé en CSS statique fonctionne bien avec CSP restrictive.

Évite d’introduire des styles inline dynamiques sans raison.

---

## 62. Performance

Tailwind génère le CSS correspondant aux classes détectées dans les sources.

Vérifie que la configuration ne force pas une génération énorme inutile.

---

## 63. CSS final

Sur une feature importante, vérifie raisonnablement :

- taille ;
- duplication ;
- présence des classes ;
- absence d’une safelist gigantesque.

Ne définis pas un seuil universel.

---

## 64. Watch development

Le watcher doit surveiller uniquement les sources utiles et se relancer facilement.

Documente la commande.

---

## 65. Build production

Le build doit être reproductible depuis une installation propre.

Il doit être exécuté par CI/CD ou procédure de déploiement.

---

## 66. `collectstatic`

Le CSS compilé doit rejoindre la stratégie Django static avant `collectstatic` selon architecture.

Coordonne avec `deployment`.

---

## 67. Pipeline

Si Node/CLI Tailwind fait partie du build :

CI doit compiler le CSS.

Ne dépends pas d’un fichier généré uniquement sur la machine d’un développeur sans politique claire.

---

## 68. Versionner le CSS compilé

Décide selon workflow :

### Possible
Si le serveur ne possède aucun outil de build frontend.

### Non nécessaire
Si CI construit l’artefact.

Documente une seule stratégie.

---

## 69. Sourcemaps

Utilise-les en développement si utiles.

En production, analyse si elles doivent être publiées.

Ne publie pas des sources sensibles.

---

## 70. Dev vs prod

Les styles visuels doivent être identiques.

Le build production ne doit pas faire disparaître des classes présentes en dev.

Les classes dynamiques non détectées sont un risque majeur à tester.

---

## 71. Tests visuels

N’impose pas des snapshots visuels pour toutes les pages.

Pour composants critiques/design system mature, cela peut devenir pertinent.

---

## 72. Tests navigateur

Pour responsive/interactions importantes, utilise les tests frontend si le projet en a.

Tailwind lui-même n’a pas besoin d’être testé.

Teste le comportement de l’interface.

---

## 73. Accessibilité automatisée

Une UI Tailwind doit toujours passer par les mêmes contrôles accessibilité que n’importe quel CSS.

Les utilities n’offrent aucune conformité automatique.

---

## 74. Responsive test

Pour une feature de layout :

- mobile ;
- tablette/intermédiaire ;
- desktop.

Ne valide pas seulement la capture desktop.

---

## 75. Dark test

Si dark mode actif :

vérifie les composants nouveaux en clair et sombre.

Évite les textes devenant illisibles parce qu’une seule couleur a été adaptée.

---

## 76. Design consistency

Avant d’inventer une nouvelle combinaison :

cherche si le projet possède déjà :

- bouton ;
- card ;
- input ;
- badge ;
- alert.

Réutilise.

---

## 77. Design debt

Si trois implémentations différentes du même bouton existent, crée une tâche/refactor ciblé.

Ne refactore pas tout le design lors d’une petite feature sans besoin.

---

## 78. Naming

Les noms de composants doivent refléter le rôle :

```text
button
alert
badge
card
```

Pas une couleur spécifique :

```text
blue-box
```

---

## 79. Semantic variants

Préférer :

```text
danger
success
warning
```

à :

```text
red
green
orange
```

quand la couleur représente un sens.

---

## 80. Pas de logique métier couleur

Le backend peut exposer un état métier.

Le frontend mappe cet état vers une variante visuelle.

Ne stocke pas `"bg-red-500"` dans la base comme règle métier.

---

## 81. Composants Django

Une structure possible :

```text
templates/components/
├── button.html
├── badge.html
├── alert.html
└── card.html
```

Uniquement quand réellement réutilisés.

---

## 82. Macros/composants tiers

Si le projet adopte une bibliothèque de composants templates, ce choix doit être documenté.

N’ajoute pas une dépendance pour éviter un simple `{% include %}`.

---

## 83. Tailwind Plus

Les composants commerciaux/officiels peuvent servir de référence si le projet dispose des droits/licences appropriés.

Ne copie pas du contenu payant auquel l’utilisateur n’a pas accès.

---

## 84. UI kits tiers

Analyse :

- licence ;
- accessibilité ;
- version Tailwind ;
- dépendances JS ;
- maintenance.

Ne mélange pas plusieurs UI kits incohérents.

---

## 85. Headless components

Peuvent être utiles pour interactions complexes.

Mais pour Django sans framework JS lourd, un composant natif accessible est souvent préférable.

---

## 86. Z-index

Évite des valeurs arbitraires croissantes :

```text
z-[99999]
```

Définis une échelle cohérente si plusieurs couches existent.

---

## 87. Position fixed/sticky

Teste sur mobile et zoom.

Un header fixe ne doit pas masquer le contenu ou le focus.

---

## 88. Overflow

Attention à :

- tableaux ;
- modales ;
- menus ;
- code.

Ne cache pas du contenu critique par `overflow-hidden`.

---

## 89. `sr-only`

Utilise les utilities d’écran-reader pour du texte utile uniquement aux technologies d’assistance lorsque pertinent.

Ne masque pas avec `sr-only` un contenu que tout le monde devrait voir.

---

## 90. `hidden`

`hidden` retire le contenu de l’affichage et généralement de l’accessibilité.

Ne l’utilise pas pour cacher visuellement un label qui doit rester accessible ; utilise la stratégie adaptée.

---

## 91. Print

Si le projet doit imprimer des pages, utilise les variants/styles print si nécessaire.

Ne l’ajoute pas par défaut.

---

## 92. RTL

Si langues RTL prévues, analyse direction et utilities.

Ne prépare pas toute une architecture RTL sans besoin.

---

## 93. Internationalisation

Les textes traduits peuvent être plus longs.

Évite les tailles fixes fragiles.

---

## 94. Documentation

Pour une convention Tailwind structurante, mets à jour :

```text
docs/frontend/tailwind.md
```

ou page équivalente.

Inclure :

- version ;
- build ;
- thème ;
- composants ;
- dark mode ;
- conventions ;
- commandes.

---

## 95. AGENTS

Documente les commandes réelles :

```text
tailwind-dev
tailwind-build
```

ou équivalents.

---

## 96. Quality gate

Avant push si Tailwind est modifié de manière significative :

- build CSS réussi ;
- classes présentes ;
- lint/format si configuré ;
- responsive vérifié ;
- accessibilité pertinente ;
- aucun asset inattendu.

---

## 97. Relecture second développeur

Demande :

- La classe sera-t-elle détectée au build ?
- Avons-nous créé une valeur arbitraire récurrente ?
- Un composant existe-t-il déjà ?
- Le responsive fonctionne-t-il ?
- Le focus est-il visible ?
- Dark mode si utilisé ?
- Avons-nous ajouté un plugin/dépendance inutile ?
- Le CSS custom contourne-t-il Tailwind ?

---

## 98. Definition of Done

Une feature Tailwind est terminée lorsque les points applicables sont satisfaits :

- build fonctionne ;
- sources détectées ;
- pas de classe dynamique fragile ;
- design cohérent ;
- responsive ;
- accessibilité ;
- états interactifs ;
- duplication raisonnable ;
- thème utilisé correctement ;
- dark mode validé si actif ;
- pipeline/docs à jour.

---

## 99. Principe final

Tailwind doit réduire le coût de création et de maintenance du CSS.

S’il aboutit à des templates impossibles à lire, des centaines de valeurs arbitraires ou un énorme fichier `@apply`, le projet utilise l’outil contre sa philosophie.
