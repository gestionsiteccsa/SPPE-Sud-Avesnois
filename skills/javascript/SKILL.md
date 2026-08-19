---
name: javascript
description: Conçoit, organise, sécurise et teste le JavaScript moderne d’un projet Django server-rendered. À utiliser pour modules ES, DOM, événements, fetch, async/await, formulaires dynamiques, CSRF, interactions accessibles, gestion des erreurs, performance, stockage navigateur et organisation des fichiers. Privilégie JavaScript natif et progressif, sans imposer React, Vue ou un bundler lourd.
compatibility: opencode
metadata:
  framework: django
  language: javascript
  purpose: frontend-interactivity
  workflow-parent: project-workflow
---

# JavaScript

## 1. Mission

Tu es responsable du JavaScript navigateur du projet.

Ton objectif est d’ajouter uniquement l’interactivité réellement utile, avec un code :

- lisible ;
- modulaire ;
- sécurisé ;
- accessible ;
- testable ;
- performant ;
- compatible avec Django ;
- facile à supprimer ou remplacer.

Principe :

> Si HTML, CSS et Django suffisent, ne rajoute pas JavaScript.

---

## 2. Coordination

Avant toute modification :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. charge `frontend-django` ;
4. charge `accessibility` pour toute interaction UI ;
5. charge `django-security` pour fetch, stockage, HTML dynamique ou données utilisateur ;
6. charge `django-testing` si des tests sont pertinents ;
7. charge `tailwind-css` si Tailwind est utilisé.

Ne transforme pas le frontend Django en SPA par accumulation progressive de scripts.

---

## 3. Questions

Pose au maximum 2 questions lorsque le comportement utilisateur n’est pas clair.

Exemples :

- Cette action doit-elle fonctionner sans JavaScript ?
- Souhaites-tu une mise à jour instantanée sans rechargement de page ?

Explique le compromis.

Ne demande pas au non-développeur de choisir entre `addEventListener` et attribut inline : décide selon les bonnes pratiques.

---

## 4. Progressive enhancement

Le JavaScript améliore une interface fonctionnelle lorsque raisonnable.

Exemples :

- confirmation ;
- autocomplétion ;
- filtre instantané ;
- modal ;
- mise à jour partielle ;
- preview ;
- compteur ;
- drag-and-drop.

Le backend reste source de vérité.

---

## 5. Pas de logique métier critique uniquement côté client

Le JavaScript ne décide jamais seul :

- permissions ;
- prix final ;
- propriétaire ;
- statut protégé ;
- validation critique ;
- quota ;
- rôle.

Le serveur recalcule et valide.

---

## 6. Modules ES

Privilégie les modules ES modernes.

Exemple :

```html
<script type="module" src="..."></script>
```

Puis :

```javascript
import { initModal } from "./modal.js";
```

Évite un énorme namespace global.

---

## 7. Un module = une responsabilité cohérente

Exemples :

```text
static/js/
├── app.js
├── components/
│   ├── modal.js
│   ├── dropdown.js
│   └── toast.js
├── features/
│   ├── ship-form.js
│   └── search.js
└── utils/
    └── http.js
```

Adapte à la taille réelle.

Ne crée pas 40 fichiers pour trois interactions simples.

---

## 8. `app.js`

Le point d’entrée doit surtout initialiser les modules.

Évite un `app.js` de plusieurs milliers de lignes.

---

## 9. Fonctions

Une fonction doit faire une chose compréhensible.

Si une fonction :

- lit le DOM ;
- appelle une API ;
- transforme des données ;
- affiche une modal ;
- gère trois erreurs ;

elle mérite probablement d’être découpée.

---

## 10. Variables

Utilise `const` par défaut.

Utilise `let` si réassignation nécessaire.

Évite `var`.

---

## 11. Strict mode

Les modules ES sont stricts par défaut.

Ne rajoute pas une configuration artificielle si les modules sont déjà utilisés.

---

## 12. Nommage

Utilise des noms orientés intention :

```javascript
submitProfileForm()
fetchShips()
closeModal()
```

Évite :

```javascript
doStuff()
handle2()
dataThing()
```

---

## 13. Événements

Utilise `addEventListener()`.

Évite les attributs HTML inline :

```html
onclick="..."
```

sauf contexte particulier explicitement justifié.

---

## 14. Event delegation

Pour une liste dynamique ou beaucoup d’éléments similaires, la délégation peut être pertinente.

Ne l’utilise pas partout par réflexe.

---

## 15. `DOMContentLoaded`

Avec les modules placés correctement, tu n’as pas toujours besoin d’attendre `DOMContentLoaded`.

Comprends le chargement réel du script avant d’ajouter des wrappers inutiles.

---

## 16. Sélecteurs DOM

Préférer des hooks stables pour le JavaScript :

```text
data-js="modal"
data-action="delete"
```

plutôt que dépendre de classes purement visuelles Tailwind.

---

## 17. Pourquoi

Une classe CSS peut changer pour le design.

Un attribut `data-*` peut représenter explicitement un comportement.

Cela réduit le couplage JS/CSS.

---

## 18. IDs

Utilise un ID lorsqu’il identifie réellement un élément unique.

N’invente pas un ID pour chaque élément uniquement pour sélectionner en JS.

---

## 19. `data-*`

Utilise les attributs data pour de petites métadonnées :

- identifiant ;
- URL ;
- état ;
- config simple.

Ne stocke pas un gros objet métier complet dans le DOM sans besoin.

---

## 20. JSON depuis Django

Pour transmettre une structure JSON depuis un template Django, utilise une méthode sûre telle que `json_script` lorsque adaptée.

Évite :

```django
<script>
  const data = {{ object_json|safe }};
</script>
```

---

## 21. Texte utilisateur

Pour insérer du texte :

```javascript
element.textContent = value;
```

plutôt que `innerHTML`.

---

## 22. `innerHTML`

Considère `innerHTML` comme sensible.

Utilise-le uniquement lorsque :

- HTML réellement nécessaire ;
- contenu maîtrisé/nettoyé ;
- stratégie XSS comprise.

Charge `django-security`.

---

## 23. DOM XSS

Ne construis pas du HTML avec des données utilisateur via concaténation.

Danger :

```javascript
target.innerHTML = `<div>${userValue}</div>`;
```

Préférer création DOM :

```javascript
const div = document.createElement("div");
div.textContent = userValue;
```

---

## 24. `insertAdjacentHTML`

Même niveau de prudence que `innerHTML`.

---

## 25. `eval`

N’utilise jamais `eval()` pour des données externes.

Évite également :

- `new Function()`
- chaînes exécutées comme code.

---

## 26. URLs

Toute URL construite à partir de données externes doit être validée.

Attention :

- `javascript:`
- `data:`
- redirections ;
- URLs tierces.

---

## 27. `fetch`

Utilise Fetch API pour les requêtes HTTP modernes lorsqu’une requête JavaScript est nécessaire.

Ne remplace pas un formulaire HTML normal par `fetch()` sans bénéfice utilisateur.

---

## 28. Wrapper HTTP

Si plusieurs features utilisent `fetch`, crée éventuellement un petit helper.

Exemple :

```text
requestJSON()
postJSON()
```

Ne crée pas un client API de 500 lignes pour deux endpoints.

---

## 29. Status HTTP

`fetch()` ne rejette pas automatiquement la Promise pour tous les statuts HTTP d’erreur.

Vérifie :

```javascript
if (!response.ok) {
    ...
}
```

Ne traite pas `404` ou `500` comme succès.

---

## 30. Parsing

Ne suppose pas toujours JSON.

Vérifie le contrat :

- JSON ;
- HTML ;
- blob ;
- texte.

---

## 31. Timeout

Fetch ne fournit pas un timeout simple historique comme certaines bibliothèques.

Utilise `AbortController` lorsqu’un timeout ou annulation est nécessaire.

---

## 32. Abort

Annule une requête obsolète lorsque pertinent :

- recherche instantanée ;
- navigation ;
- autocomplete.

Cela évite des réponses arrivant dans le mauvais ordre.

---

## 33. Race conditions frontend

Pour une recherche dynamique :

```text
requête A
requête B
réponse B
réponse A
```

ne doit pas permettre à A d’écraser le résultat plus récent B.

Utilise abort ou version de requête.

---

## 34. Async/await

Privilégie `async`/`await` lorsque cela améliore la lecture des Promises.

N’oublie pas `try/catch` aux frontières où une erreur doit être gérée.

---

## 35. Erreur réseau

Distingue :

- réseau indisponible ;
- timeout ;
- réponse HTTP d’erreur ;
- JSON invalide ;
- erreur métier.

L’utilisateur n’a pas besoin d’un message technique brut.

---

## 36. Messages d’erreur

Affiche une erreur compréhensible :

```text
Impossible d’enregistrer pour le moment.
```

et logue les détails appropriés si nécessaire.

Ne montre pas une stack trace JavaScript à l’utilisateur.

---

## 37. Finally

Utilise `finally` pour restaurer les états :

- bouton ;
- spinner ;
- disabled.

Cela évite une interface bloquée après erreur.

---

## 38. CSRF Django

Pour des requêtes unsafe utilisant l’authentification par session Django :

- conserve la protection CSRF ;
- envoie le token selon la méthode documentée par Django ;
- utilise les bonnes méthodes HTTP.

Ne mets pas `csrf_exempt` pour simplifier `fetch`.

---

## 39. Token CSRF

Selon configuration, le token peut venir :

- du cookie ;
- d’un élément DOM rendu ;
- de la stratégie Django définie.

Utilise une méthode cohérente avec `CSRF_USE_SESSIONS` et `CSRF_COOKIE_HTTPONLY`.

Ne suppose pas toujours que le cookie est lisible.

---

## 40. Exemple helper CSRF

Un helper peut centraliser :

- headers ;
- credentials ;
- JSON ;
- erreurs.

Il doit rester petit et testé.

---

## 41. Credentials

Pour same-origin/session :

utilise la politique de credentials cohérente avec le navigateur/Django.

Ne force pas des credentials cross-origin sans besoin.

---

## 42. CORS

Ne tente pas de corriger une erreur CORS uniquement en JavaScript.

CORS est une politique serveur/navigateur.

Charge `django-security` / `django-api`.

---

## 43. FormData

Pour soumettre un formulaire, `FormData` peut être utile, notamment uploads.

Ne fixe pas manuellement un header multipart avec boundary incorrect.

Laisse le navigateur gérer le `Content-Type` lorsqu’approprié.

---

## 44. JSON

Pour API JSON :

- `JSON.stringify()` ;
- header approprié ;
- validation serveur.

Ne sérialise pas un objet DOM entier.

---

## 45. Double soumission

Lors d’un submit async :

- désactiver temporairement l’action si pertinent ;
- état loading ;
- backend idempotent si critique.

Le bouton désactivé seul n’est pas une garantie.

---

## 46. Loading

Un état loading doit être :

- visible ;
- compréhensible ;
- accessible si nécessaire.

Ne remplace pas le label par un spinner sans nom.

---

## 47. Optimistic UI

Utilise une mise à jour optimiste seulement lorsque :

- l’action échoue rarement ;
- rollback UI simple ;
- bénéfice réel.

Pour une suppression critique, attendre le serveur peut être plus clair.

---

## 48. Debounce

Pertinent pour :

- recherche ;
- resize ;
- input dynamique.

N’ajoute pas debounce sur chaque événement.

---

## 49. Throttle

Pertinent pour certains événements fréquents :

- scroll ;
- pointermove.

Ne micro-optimise pas sans besoin.

---

## 50. Performance DOM

Évite :

- reflows répétés ;
- lectures/écritures alternées massives ;
- création DOM gigantesque.

Pour une petite page, reste simple.

---

## 51. Event listeners

Évite d’attacher des centaines de listeners lorsque la délégation est plus simple.

Mais la simplicité reste prioritaire.

---

## 52. Memory leaks

Sur des composants dynamiques, nettoie :

- timers ;
- observers ;
- listeners ;
- subscriptions ;

si leur cycle de vie l’exige.

---

## 53. Timers

Évite les `setInterval()` permanents sans raison.

Pour polling, définis :

- fréquence ;
- arrêt ;
- visibilité page ;
- erreurs.

---

## 54. Polling

Si la donnée doit se mettre à jour rarement, un refresh manuel ou server-rendered peut suffire.

N’introduis pas WebSockets pour éviter un polling de 30 secondes sur un petit besoin.

---

## 55. WebSockets

Si vraiment nécessaires, cette décision relève d’une architecture ASGI/Channels ou autre.

Ne les implémente pas dans ce skill seul.

---

## 56. DOM observers

`MutationObserver`, `ResizeObserver`, `IntersectionObserver` sont utiles dans certains cas.

Ne les utilise pas lorsqu’un événement natif simple suffit.

---

## 57. Lazy loading

Pour fonctionnalités ou modules lourds, dynamic import peut être pertinent.

Ne complexifie pas trois petits scripts.

---

## 58. Dynamic import

Exemple :

```javascript
const module = await import("./heavy-feature.js");
```

Utilise seulement pour un vrai bénéfice.

---

## 59. Browser support

Cible les navigateurs définis par le projet.

Ne transpile pas automatiquement du JavaScript moderne pour des navigateurs non supportés.

---

## 60. Polyfills

Ajoute seulement ceux réellement nécessaires.

Chaque polyfill est une dépendance/code supplémentaire.

---

## 61. Bundler

N’ajoute pas Vite/Webpack/Rollup uniquement parce que le projet a du JavaScript.

Les modules ES natifs peuvent suffire.

---

## 62. Quand un bundler devient pertinent

Exemples :

- React/Vue ;
- TypeScript ;
- gros graphe JS ;
- asset pipeline complexe ;
- npm packages front nombreux ;
- optimisation build nécessaire.

Documente la décision.

---

## 63. TypeScript

Ne convertis pas un petit JS Django en TypeScript automatiquement.

TypeScript devient pertinent si :

- frontend conséquent ;
- objets complexes ;
- API publique importante ;
- équipe habituée.

---

## 64. npm

N’ajoute npm que si une dépendance/build frontend le nécessite.

Le JavaScript natif n’en dépend pas.

---

## 65. Dépendances JS

Avant un package :

- besoin réel ;
- taille ;
- maintenance ;
- sécurité ;
- licence ;
- browser support.

Charge `dependency-management`.

---

## 66. Lodash

N’ajoute pas une grosse bibliothèque utilitaire pour une fonction native simple.

---

## 67. Axios

Fetch natif suffit souvent.

N’ajoute Axios que si ses fonctionnalités apportent une vraie valeur au projet.

---

## 68. jQuery

N’introduis pas jQuery dans un nouveau code moderne sauf contrainte existante forte.

Si un projet historique l’utilise, ne réécris pas tout sans raison.

---

## 69. Frameworks

React, Vue, Svelte ne relèvent pas de ce skill.

Si la complexité le justifie, charge le skill spécialisé.

---

## 70. Alpine / HTMX

Ils peuvent compléter Django avec moins de JS custom.

Ne les ajoute pas à une feature sans décision.

---

## 71. localStorage

Considère que JavaScript peut lire `localStorage`.

N’y stocke pas :

- session ;
- token sensible ;
- secret.

Charge `django-security`.

---

## 72. sessionStorage

Même prudence.

Sa durée plus courte ne le rend pas sûr contre XSS.

---

## 73. Cookies JS

Ne rends pas les cookies de session accessibles au JavaScript.

Les cookies sensibles doivent rester HttpOnly lorsque possible.

---

## 74. Préférences

`localStorage` peut être adapté pour des préférences non sensibles :

- thème ;
- vue grille/liste.

Documente si cela devient un vrai stockage utilisateur.

---

## 75. Privacy

Toute persistance/analytics côté navigateur doit être analysée avec `privacy-rgpd`.

---

## 76. URLSearchParams

Utilise pour manipuler proprement les query params.

Évite de concaténer des URLs à la main.

---

## 77. History API

Pour améliorer filtres/navigation sans reload, utilise-la avec prudence.

Le bouton retour du navigateur doit rester cohérent.

---

## 78. Accessibility

Toute interaction JavaScript doit avoir :

- clavier ;
- focus ;
- nom accessible ;
- état ;
- feedback.

Charge `accessibility`.

---

## 79. Focus

Après une action dynamique importante, décide explicitement où le focus doit aller.

Exemples :

- modal ouverte ;
- modal fermée ;
- erreur ;
- contenu ajouté.

Ne déplace pas le focus pour des changements mineurs.

---

## 80. Modal

Ne code pas une modal en JS en ignorant :

- focus trap ;
- Escape ;
- retour focus ;
- arrière-plan ;
- nom accessible.

Utilise HTML natif/pattern éprouvé.

---

## 81. Dropdown

Expose l’état avec `aria-expanded` si pertinent.

Le bouton doit rester un vrai bouton.

---

## 82. Tabs

Respecte le pattern clavier si ce sont réellement des tabs.

Sinon, des liens peuvent suffire.

---

## 83. Live region

Pour un résultat dynamique important :

utilise `aria-live` avec parcimonie.

---

## 84. Animations

Respecte `prefers-reduced-motion`.

JavaScript doit aussi tenir compte des utilisateurs réduisant les animations si une animation est déclenchée par script.

---

## 85. Pointer

Ne dépend pas uniquement de mouse events.

Utilise click/pointer events selon le besoin afin de supporter tactile/clavier.

---

## 86. Keyboard events

Ne simule pas tous les clicks via `keydown` si le contrôle natif le fait déjà.

Un `<button>` activé par Enter/Space fonctionne nativement.

---

## 87. Tests

Teste le JavaScript lorsqu’il contient un comportement qui peut régresser.

Exemples :

- transformation pure ;
- composant dynamique ;
- validation UI complexe ;
- gestion d’état ;
- requête HTTP helper.

---

## 88. Tests navigateur

Pour interactions DOM importantes, Playwright ou autre outil navigateur peut être pertinent si le projet l’utilise.

Ne l’ajoute pas pour un simple toggle.

---

## 89. Tests unitaires JS

Si aucun environnement Node n’existe et que le JS reste minuscule, ne crée pas tout un runner uniquement pour tester deux lignes.

Le test Django/navigateur peut parfois suffire.

---

## 90. Test fetch

Ne fais pas dépendre les tests de services externes.

Mock/fake les frontières.

---

## 91. ESLint

Si le projet dispose déjà d’ESLint, respecte-le.

Ne l’ajoute pas automatiquement à un très petit JS moderne si la valeur ne justifie pas la stack Node.

---

## 92. Formatter

Même principe avec Prettier.

Si déjà présent, utilise-le.

Sinon, n’ajoute pas une dépendance uniquement pour formater 50 lignes.

---

## 93. JSDoc

Utilise JSDoc pour :

- contrats non évidents ;
- objets structurés ;
- fonctions publiques complexes.

Ne documente pas :

```javascript
/** Adds two numbers */
function add(a, b)
```

si évident.

---

## 94. Comments

Explique le pourquoi, pas la syntaxe.

---

## 95. Debug

Avant push, retire :

- `console.log` temporaires ;
- breakpoints ;
- mocks ;
- alert debug.

Un `console.error` ou logging intentionnel peut rester si la stratégie le prévoit.

---

## 96. Source maps

Si bundler présent, décide si elles doivent être publiques en prod.

Ne révèle pas inutilement des sources internes.

---

## 97. Error tracking

Si un outil de suivi frontend est utilisé :

- filtre données personnelles ;
- secrets ;
- contenu formulaire.

Charge `privacy-rgpd`.

---

## 98. CSP

Le JS en fichiers/modules facilite une CSP stricte.

Évite les scripts inline si le projet utilise une CSP.

Charge `django-security`.

---

## 99. Nonce

Si un script inline est réellement nécessaire avec CSP, utilise la stratégie du projet.

Ne rajoute pas `'unsafe-inline'` par facilité.

---

## 100. Dynamic script injection

N’injecte pas arbitrairement des scripts externes à partir d’une URL utilisateur.

---

## 101. Third-party scripts

Toute intégration tierce doit être revue :

- sécurité ;
- privacy ;
- performance ;
- CSP.

---

## 102. DOM clobbering

Évite de dépendre de propriétés globales créées implicitement depuis des IDs/names HTML.

Sélectionne explicitement les éléments.

---

## 103. Prototype pollution

Ne fusionne pas aveuglément des objets externes dans des objets sensibles.

Utilise des structures explicites.

---

## 104. JSON parsing

`JSON.parse()` n’exécute pas du code, mais la donnée reste non fiable.

Valide sa structure avant usage critique.

---

## 105. Validation client

La validation client sert à l’UX.

Le serveur valide toujours.

---

## 106. Form validation API

Les APIs natives :

- `checkValidity()`
- `reportValidity()`
- contraintes HTML

peuvent suffire pour beaucoup de besoins.

Ne réimplémente pas toutes les validations.

---

## 107. Custom validation

Pour règle spécifique, garde la même règle côté serveur.

La version client n’est qu’une aide.

---

## 108. File preview

Pour preview d’un upload :

- taille ;
- type ;
- object URL ;
- révocation URL si nécessaire.

Cela ne valide pas le fichier côté serveur.

---

## 109. Object URLs

Si `URL.createObjectURL()` est utilisé, pense à `URL.revokeObjectURL()` lorsque le cycle de vie l’exige.

---

## 110. Clipboard

L’accès clipboard doit être déclenché par une action utilisateur et fournir un feedback.

Prévois un fallback raisonnable.

---

## 111. Notifications browser

Ne demande pas la permission notifications au chargement initial sans contexte.

Demande-la après une action/intention claire.

---

## 112. Geolocation

Même règle.

Ne demande pas une donnée sensible avant qu’elle soit nécessaire.

Charge `privacy-rgpd`.

---

## 113. Service workers

Ne crée pas un PWA/service worker sans besoin.

Un cache offline mal conçu peut servir des données obsolètes ou privées.

---

## 114. Offline

Si un mode offline est demandé, il mérite une conception séparée :

- cache ;
- sync ;
- conflit ;
- sécurité ;
- privacy.

---

## 115. `defer` / modules

Les modules sont différés par défaut dans leur chargement/exécution classique.

Comprends ce comportement avant d’ajouter `defer` partout.

---

## 116. Script placement

Utilise la stratégie cohérente du projet :

- modules dans head ;
- ou fin de body.

Ne duplique pas le même script sur plusieurs templates.

---

## 117. Static files Django

Place les scripts dans la stratégie `static` du projet.

Utilise `{% static %}`.

Ne mets pas du JS applicatif dans `MEDIA_ROOT`.

---

## 118. Cache busting

Laisse la stratégie Django/static pipeline gérer les fichiers fingerprintés si configurée.

Ne rajoute pas `?v=123` manuellement partout.

---

## 119. Page-specific JS

Ne charge pas un module lourd sur toutes les pages si une seule feature l’utilise.

Un import conditionnel/page-specific peut être approprié.

---

## 120. Initialisation

Un module doit tolérer l’absence du composant si chargé globalement, ou être chargé uniquement sur les pages concernées.

Évite :

```javascript
document.querySelector(...).addEventListener(...)
```

sans vérifier l’existence lorsque le script peut être global.

---

## 121. Data attributes pour init

Exemple :

```html
<div data-js="ship-search"></div>
```

Le module recherche ce hook et s’initialise seulement s’il existe.

---

## 122. Multiple instances

Un composant réutilisable doit fonctionner avec plusieurs instances sur la même page.

N’utilise pas un ID global si la feature peut apparaître plusieurs fois.

---

## 123. Custom events

Des `CustomEvent` peuvent découpler des composants simples.

Ne crée pas un event bus global complexe pour un petit projet.

---

## 124. State

Garde l’état local au composant lorsque possible.

Ne crée pas un store global sans besoin.

---

## 125. State URL

Les filtres/recherches partageables peuvent avoir leur état dans l’URL plutôt que dans un store.

---

## 126. State server

Les données métier restent sur le serveur.

Le navigateur peut avoir une copie temporaire pour l’interface.

---

## 127. No magic

Évite les scripts qui modifient le DOM globalement selon des conventions implicites difficiles à retrouver.

Les hooks et initialisations doivent être explicites.

---

## 128. Refactoring

Si plusieurs features copient le même helper :

factorise seulement lorsque le contrat commun est clair.

---

## 129. Relecture second développeur

Avant de terminer une feature JS, vérifie :

- JavaScript réellement nécessaire ?
- Backend toujours source de vérité ?
- Module assez petit ?
- Pas de global ?
- Pas de XSS DOM ?
- Fetch vérifie `response.ok` ?
- CSRF correct ?
- Erreurs gérées ?
- Double submit ?
- Clavier/focus ?
- localStorage contient-il quelque chose de sensible ?
- dépendance externe nécessaire ?
- comportement sans JS acceptable ?
- tests pertinents ?

---

## 130. Definition of Done

Une feature JavaScript est terminée lorsque les points applicables sont vrais :

- progressive enhancement analysé ;
- code modulaire ;
- erreurs réseau/HTTP gérées ;
- CSRF correct ;
- aucune injection DOM dangereuse ;
- validation serveur conservée ;
- accessibilité ;
- loading/error/success ;
- aucun debug temporaire ;
- dépendances justifiées ;
- performance raisonnable ;
- tests pertinents ;
- documentation mise à jour si architecture/usage change.

---

## 131. Principe final

Le meilleur JavaScript dans un projet Django est celui qui ajoute une interaction claire sans retirer les qualités natives du web.

Ajoute du JavaScript pour améliorer une expérience, pas pour recréer inutilement ce que le navigateur et Django savent déjà faire.
