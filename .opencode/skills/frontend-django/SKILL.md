---
name: frontend-django
description: Conçoit et maintient le frontend server-rendered d’un projet Django avec templates, formulaires, composants réutilisables, static files et JavaScript léger. À utiliser pour pages HTML, formulaires, navigation, composants UI, assets, progressive enhancement, accessibilité et UX. Privilégie HTML natif, Django Forms, composants simples et JavaScript uniquement lorsqu’il apporte une vraie valeur, sans imposer React ou une SPA.
compatibility: opencode
metadata:
  framework: django
  purpose: frontend
  rendering: server-side
  language: fr
  workflow-parent: project-workflow
---

# Frontend Django

## 1. Mission

Tu es responsable du frontend rendu par Django.

Ton objectif est de produire une interface :

- claire ;
- cohérente ;
- accessible ;
- progressive ;
- responsive ;
- maintenable ;
- sécurisée ;
- simple à faire évoluer ;
- compatible avec les fonctionnalités Django ;
- utilisable même si JavaScript échoue lorsque cela est raisonnable.

Principe :

> HTML natif et Django d’abord. JavaScript lorsque l’interaction le justifie. Framework frontend lourd uniquement lorsqu’un besoin réel l’impose.

---

## 2. Coordination

Avant une modification significative :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. inspecte les templates, CSS, JS et forms existants ;
4. respecte le design et les conventions déjà validés ;
5. charge si disponibles :
   - `django-architecture`
   - `django-security`
   - `django-testing`
   - `django-performance`
   - `django-auth`
   - `accessibility`
   - `documentation`

Ne change pas de framework CSS ou de stratégie frontend sans raison importante.

---

## 3. Questions de cadrage

Pose au maximum **2 questions à la fois**.

Pose uniquement des questions qui changent réellement l’expérience ou l’architecture.

Exemples :

- Cette action doit-elle fonctionner sans JavaScript ?
- Faut-il permettre l’édition directement dans la liste ou via une page dédiée ?
- Le public utilise-t-il principalement mobile, desktop ou les deux ?
- Cette information est-elle publique ou dépend-elle de l’utilisateur ?

Explique brièvement pourquoi la question compte.

Ne demande pas au non-développeur de choisir entre des techniques HTML équivalentes si une bonne pratique claire existe.

---

## 4. Progressive enhancement

Le comportement de base doit fonctionner avec HTML et requêtes HTTP classiques lorsque cela est raisonnable.

JavaScript améliore ensuite :

- feedback immédiat ;
- modales ;
- filtres dynamiques ;
- autocomplétion ;
- interactions partielles ;
- drag-and-drop ;
- rafraîchissement ciblé.

Ne transforme pas un formulaire simple en application JavaScript complexe.

---

## 5. Templates Django

Utilise le moteur de templates Django pour :

- structure HTML ;
- affichage conditionnel ;
- boucles simples ;
- liens ;
- composants/includes ;
- traduction ;
- static assets.

Évite de mettre dans les templates :

- requêtes DB ;
- règles métier complexes ;
- calculs importants ;
- permissions uniquement visuelles ;
- transformation lourde.

Prépare les données dans les couches Python appropriées.

---

## 6. Héritage de templates

Utilise l’héritage pour les layouts communs.

Structure typique :

```text
templates/
├── base.html
├── components/
├── partials/
└── pages/
```

ou templates par app lorsque cela correspond mieux au projet.

Évite plusieurs layouts presque identiques copiés-collés.

---

## 7. Blocks

Les blocks doivent avoir un rôle clair :

```text
title
content
extra_css
extra_js
```

Ne crée pas des dizaines de blocks ultra-spécifiques rendant le layout impossible à comprendre.

---

## 8. Includes

Utilise `{% include %}` pour un fragment visuel réutilisable.

Bon cas :

- message d’alerte ;
- carte ;
- pagination ;
- champ de formulaire ;
- navigation secondaire.

Mauvais cas :

- fragment contenant beaucoup de logique métier ;
- include utilisé seulement pour réduire artificiellement un fichier de dix lignes.

---

## 9. Composants frontend

Crée un composant lorsqu’un motif :

- apparaît plusieurs fois ;
- possède une structure stable ;
- nécessite plusieurs états ;
- doit rester visuellement cohérent.

Exemples :

- badge ;
- card ;
- modal ;
- table ;
- empty state ;
- pagination ;
- breadcrumb.

Ne construis pas un design system complet avant d’avoir plusieurs besoins réels.

---

## 10. Custom template tags

Utilise des template tags/filters custom uniquement lorsqu’ils représentent une logique de présentation réutilisable.

Ils ne doivent pas cacher :

- requêtes DB répétées ;
- permissions ;
- workflow métier ;
- appels externes.

Une fonction Python normale dans la bonne couche est souvent préférable.

---

## 11. Context processors

Un context processor convient aux données réellement nécessaires sur de nombreuses pages :

- identité utilisateur ;
- configuration globale non sensible ;
- navigation globale simple.

Évite qu’il exécute des requêtes coûteuses ou fournisse des données spécifiques à une seule page.

---

## 12. HTML sémantique

Utilise les éléments natifs selon leur sens :

- `header`
- `nav`
- `main`
- `section`
- `article`
- `aside`
- `footer`
- `button`
- `form`
- `label`
- `table`

Évite les `div` cliquables quand un `button` ou un lien suffit.

HTML natif apporte comportement clavier, sémantique et accessibilité gratuitement.

---

## 13. Boutons et liens

Utilise :

- `<a>` pour naviguer ;
- `<button>` pour agir.

Ne crée pas un lien qui supprime un objet.

Ne crée pas un bouton qui simule une navigation sans raison.

---

## 14. Formulaires Django

Privilégie les `Form` et `ModelForm` Django pour :

- validation serveur ;
- normalisation ;
- affichage des erreurs ;
- widgets ;
- champs.

Une validation JavaScript peut améliorer l’UX mais ne remplace jamais la validation serveur.

---

## 15. ModelForm

Utilise `ModelForm` lorsque le formulaire représente naturellement un modèle.

Déclare explicitement les champs éditables lorsque des champs sensibles existent.

Évite `fields = "__all__"` sur un modèle contenant :

- propriétaire ;
- permissions ;
- statut interne ;
- flags administratifs.

---

## 16. Form simple

Utilise `forms.Form` pour :

- recherche ;
- filtres ;
- contact ;
- action non directement liée à un modèle ;
- workflow multi-modèles.

Ne crée pas un modèle juste pour avoir un ModelForm.

---

## 17. Labels

Chaque champ doit avoir un label compréhensible.

Le placeholder ne remplace pas le label.

Les labels doivent être correctement associés aux contrôles.

Préférer le mécanisme Django générant les IDs/labels correctement.

---

## 18. Help text

Utilise `help_text` pour les informations nécessaires à la saisie.

Ne surcharge pas chaque champ de texte inutile.

Une instruction doit être proche du champ qu’elle concerne.

---

## 19. Erreurs de formulaire

Affiche :

- erreurs globales ;
- erreurs par champ ;
- message compréhensible ;
- état visuel non dépendant uniquement de la couleur.

Après soumission invalide, l’utilisateur doit comprendre :

- ce qui est incorrect ;
- où ;
- comment le corriger.

---

## 20. Focus après erreur

Pour les formulaires complexes, analyse le placement du focus :

- résumé d’erreurs ;
- premier champ invalide ;
- titre de confirmation.

Ne déplace pas le focus de façon surprenante.

---

## 21. Champs requis

Indique clairement les champs requis.

Ne suppose pas que `*` est compris sans explication lorsque le formulaire est important.

Les attributs HTML et validation Django doivent rester cohérents.

---

## 22. Autocomplete

Utilise l’attribut HTML `autocomplete` approprié pour les champs standard :

- name ;
- email ;
- current-password ;
- new-password ;
- address ;
- etc.

Ne désactive pas `autocomplete` sur les mots de passe uniquement par réflexe.

---

## 23. Input types

Utilise les types HTML adaptés :

- email ;
- url ;
- number ;
- date ;
- search ;
- password.

Mais garde la validation Django comme source fiable côté serveur.

---

## 24. Groupes de champs

Pour radio/checkboxes ou groupes logiques, utilise :

- `fieldset`
- `legend`

lorsque pertinent.

Cela améliore compréhension et accessibilité.

---

## 25. Formsets

Utilise les formsets Django lorsque plusieurs formulaires similaires doivent être édités ensemble.

N’utilise pas un formset pour masquer un workflow métier complexe qui serait plus clair avec plusieurs étapes.

---

## 26. Formsets dynamiques

Si JavaScript ajoute/supprime des lignes :

- respecte management form ;
- indexes ;
- validation ;
- suppression ;
- accessibilité ;
- fonctionnement serveur final.

Teste les cas limites.

---

## 27. POST/Redirect/GET

Après une soumission réussie, utilise généralement une redirection.

Cela évite les resoumissions involontaires lors du rafraîchissement.

Ne rends pas une page de succès dépendante d’un POST persistant sans raison.

---

## 28. Messages Django

Utilise le messages framework pour les feedbacks transitoires :

- succès ;
- erreur non liée au formulaire ;
- avertissement ;
- information.

Ne l’utilise pas pour stocker des informations métier durables.

---

## 29. Feedback utilisateur

Toute action doit donner un retour approprié.

Exemples :

- création réussie ;
- suppression ;
- sauvegarde ;
- chargement ;
- erreur.

Évite les actions silencieuses.

---

## 30. Confirmation destructive

Pour suppression ou action irréversible :

- page de confirmation ou modal accessible ;
- nom de l’objet ;
- conséquence claire.

Ne repose pas uniquement sur `window.confirm()` si l’action est importante.

---

## 31. Navigation

La navigation doit être :

- prévisible ;
- cohérente ;
- accessible clavier ;
- liée à la structure du site.

Indique l’état actif lorsque cela aide.

---

## 32. Breadcrumbs

Utilise un breadcrumb pour les hiérarchies profondes.

Ne l’ajoute pas sur une application très simple où il n’apporte rien.

Structure sémantique correcte.

---

## 33. Titres de page

Chaque page doit avoir :

- `<title>` pertinent ;
- un titre principal clair ;
- hiérarchie de headings cohérente.

Évite les sauts de niveaux sans raison.

---

## 34. Empty states

Une liste vide doit expliquer la situation.

Bon empty state :

- « Aucun vaisseau enregistré »
- action de création si autorisée.

Évite une table vide sans explication.

---

## 35. États de chargement

Pour une interaction JavaScript :

- afficher un état de chargement si la durée peut être perceptible ;
- empêcher les doubles soumissions ;
- restaurer l’état en cas d’erreur.

Ne bloque pas toute la page pour une petite opération locale.

---

## 36. Double soumission

Pour un formulaire sensible :

- désactivation temporaire du bouton côté UI ;
- idempotence côté serveur lorsque critique.

Le JavaScript seul ne protège pas contre double requête.

---

## 37. JavaScript

Ajoute JavaScript lorsqu’il améliore réellement l’expérience.

Préférer :

- petit module ;
- responsabilité claire ;
- DOM natif lorsque suffisant.

Ne crée pas un bundle complexe pour trois interactions.

---

## 38. Modules JavaScript

Organise le JS par fonctionnalité/composant.

Évite :

```text
app.js
```

de 5 000 lignes.

Mais n’éclate pas non plus chaque événement en fichier séparé.

Même principe de cohésion que pour Python.

---

## 39. JavaScript inline

Évite le JS inline répété dans les templates.

Préférer des fichiers static versionnés.

Les données nécessaires peuvent être exposées via :

- `data-*` ;
- JSON sûr ;
- contexte limité.

Ne concatène pas des données utilisateur dans du JavaScript brut.

---

## 40. `json_script`

Pour transmettre des données JSON vers JavaScript, utilise les mécanismes sûrs de Django adaptés plutôt qu’une interpolation directe dans `<script>`.

Charge `django-security`.

---

## 41. Événements

Utilise des listeners plutôt que `onclick` inline lorsque cela améliore la structure.

Les composants doivent être initialisables de façon claire.

---

## 42. Dépendances JavaScript

Avant d’ajouter une bibliothèque :

- besoin réel ;
- taille ;
- maintenance ;
- sécurité ;
- accessibilité ;
- compatibilité.

Ne charge pas une librairie entière pour une fonction triviale disponible nativement.

---

## 43. HTMX / Alpine / autres

Ces outils peuvent être utiles mais ne sont jamais imposés par ce skill.

Si le projet adopte un outil :

- décision documentée ;
- conventions ;
- tests ;
- accessibilité ;
- fallback selon besoin.

Ne mélange pas plusieurs micro-frameworks pour résoudre les mêmes problèmes.

---

## 44. React/Vue

Si le frontend devient une vraie SPA ou possède une complexité suffisante, charge le skill spécialisé React/Vue.

Ne mélange pas les responsabilités de ce skill avec une architecture SPA.

Django peut rester backend/API.

---

## 45. CSS

Utilise le système CSS déjà choisi :

- CSS natif ;
- Tailwind ;
- Bootstrap ;
- autre.

Ne migre pas de framework visuel pendant une feature sans justification.

---

## 46. Organisation CSS

Évite un unique fichier de milliers de lignes si le projet grandit.

Organise selon :

- composants ;
- layout ;
- pages ;
- utilities ;

en fonction de l’outil choisi.

Ne duplique pas des styles de composants.

---

## 47. Variables/design tokens

Pour un projet avec identité visuelle stable, centralise :

- couleurs ;
- spacing ;
- radius ;
- typographie ;

via le mécanisme du framework choisi.

Ne crée pas un design system abstrait pour deux pages.

---

## 48. Responsive

Chaque feature frontend doit être testée mentalement et si possible réellement sur :

- petit mobile ;
- largeur intermédiaire ;
- desktop.

Évite les largeurs fixes qui cassent sur petit écran.

---

## 49. Mobile first

Une approche mobile-first peut être utile, mais ne l’impose pas si le design existant utilise une autre stratégie cohérente.

Le résultat doit fonctionner à toutes les tailles cibles.

---

## 50. Tables

Les tables servent aux données tabulaires.

Utilise :

- `caption` lorsque utile ;
- headers ;
- scope ;
- structure sémantique.

Pour mobile :

- scroll horizontal maîtrisé ;
- vue alternative seulement si nécessaire.

Ne transforme pas une vraie table en dizaines de divs uniquement pour le style.

---

## 51. Images

Chaque image informative doit avoir un texte alternatif pertinent.

Image décorative :

```text
alt=""
```

Ne répète pas le texte adjacent dans l’alt sans valeur.

---

## 52. Icônes

Une icône seule utilisée comme bouton doit avoir un nom accessible.

Si le bouton a un texte visible suffisant, évite un aria-label contradictoire.

---

## 53. ARIA

Règle :

> No ARIA is better than bad ARIA.

Utilise HTML natif quand possible.

ARIA complète une sémantique manquante ; elle ne répare pas automatiquement un mauvais composant.

Pour widgets complexes, suivre les patterns WAI-ARIA pertinents.

---

## 54. Clavier

Toute fonction interactive doit être utilisable au clavier.

Vérifie notamment :

- Tab ;
- Shift+Tab ;
- Enter ;
- Space ;
- Escape selon composant ;
- flèches pour widgets appropriés.

Ne retire jamais l’indicateur de focus sans remplacement visible.

---

## 55. Focus visible

Le focus clavier doit être clairement visible.

Évite :

```css
outline: none;
```

sans alternative.

---

## 56. Ordre de focus

L’ordre DOM doit généralement correspondre à l’ordre visuel.

Évite `tabindex` positif pour réorganiser artificiellement la navigation.

---

## 57. Modales

Une modal doit gérer :

- focus initial ;
- focus contenu ;
- Escape ;
- retour du focus au déclencheur ;
- arrière-plan non interactif selon pattern ;
- nom accessible.

Pour une simple confirmation, une page dédiée peut parfois être plus simple et robuste.

---

## 58. Menus custom

N’implémente pas un widget ARIA complexe si un simple groupe de liens suffit.

Un « menu » de navigation de site n’a pas forcément besoin du pattern `menubar`.

Utilise les patterns ARIA seulement quand le comportement correspond réellement au widget.

---

## 59. Couleurs

Ne communique pas une information uniquement par couleur.

Exemple :

- erreur rouge + texte/iconographie ;
- succès vert + message.

Le skill accessibilité peut définir les exigences détaillées de contraste.

---

## 60. Motion

Respecte la préférence utilisateur `prefers-reduced-motion` pour animations importantes.

Évite les animations qui bloquent l’usage ou provoquent des mouvements excessifs.

---

## 61. Langue

Définis la langue du document :

```html
<html lang="fr">
```

ou dynamique selon i18n.

Les changements de langue importants doivent être balisés si nécessaire.

---

## 62. I18n

Si le projet est multilingue :

- utilise `{% trans %}` / mécanismes Django ;
- évite le texte métier enfoui dans JS ;
- prévois les textes plus longs ;
- ne concatène pas des fragments traduits de façon fragile.

---

## 63. Dates/nombres

Affiche selon locale et contexte.

Ne modifie pas la valeur stockée uniquement pour la présentation.

---

## 64. Fuseaux horaires

L’interface doit distinguer si nécessaire :

- heure locale ;
- timezone projet ;
- instant UTC.

Ne montre pas une heure ambiguë pour une action métier critique.

---

## 65. Static files

Utilise `django.contrib.staticfiles`.

Sépare les assets applicatifs des médias utilisateurs.

Ne place jamais un upload utilisateur dans `static/`.

---

## 66. Namespacing static

Pour assets d’app :

```text
app/static/app/...
```

permet d’éviter les collisions.

Utilise `{% static %}` plutôt que des chemins codés en dur.

---

## 67. Collectstatic

En production, les fichiers static sont collectés et servis par la stratégie de déploiement.

Ce skill ne doit pas faire de Django un serveur static de production par défaut.

Charge `deployment`.

---

## 68. Cache busting

Une stratégie de static fingerprintés/manifest peut être utilisée en production lorsque configurée.

Ne versionne pas les noms manuellement dans les templates.

---

## 69. Media

Les media sont les fichiers utilisateurs.

Le frontend doit utiliser les URLs de storage fournies par Django.

Ne construit pas un chemin disque.

Pour fichiers privés, ne suppose pas qu’une URL publique est acceptable.

---

## 70. Sécurité template

Django auto-échappera généralement les variables.

Ne désactive pas cette protection pour « faire fonctionner » du HTML utilisateur.

Évalue précisément :

- `safe`
- `mark_safe`
- HTML riche.

Charge `django-security`.

---

## 71. CSRF dans les formulaires

Pour toute soumission POST Django avec session :

```django
{% csrf_token %}
```

Ne désactive pas CSRF pour résoudre un problème frontend.

Pour JS/AJAX, utilise la stratégie Django documentée.

---

## 72. Permission UI

L’interface peut masquer une action non autorisée.

Mais le backend doit toujours vérifier la permission.

Le frontend n’est jamais la barrière de sécurité.

---

## 73. Formulaires conditionnels

Si un champ apparaît avec JavaScript :

le serveur doit gérer correctement :

- champ absent ;
- champ présent ;
- valeur falsifiée.

Ne lie pas l’intégrité au DOM.

---

## 74. Pagination UI

Une pagination doit être :

- compréhensible ;
- accessible ;
- conserver les filtres pertinents ;
- ne pas générer des centaines de liens.

Pour gros volumes, adapter l’affichage.

---

## 75. Filtres

Un filtre doit :

- avoir un label ;
- conserver son état ;
- être réinitialisable ;
- produire une URL partageable lorsque pertinent.

Préférer query params pour recherches/filtres GET.

---

## 76. Recherche

Une recherche est généralement un GET.

L’URL peut contenir les critères non sensibles.

Ne place pas des données confidentielles dans la query string.

---

## 77. Tri

Indique clairement le tri actif.

Pour table :

- nom du champ ;
- direction.

Utilise une sémantique accessible lorsque le tri est interactif.

---

## 78. Actions en masse

Pour sélection multiple :

- checkbox avec label ;
- action claire ;
- confirmation destructive ;
- permission serveur ;
- nombre d’éléments sélectionnés.

Ne déclenche pas une action irréversible par simple changement de select.

---

## 79. Notifications toast

Les toasts ne doivent pas être le seul endroit contenant une information critique.

Pour les lecteurs d’écran, utiliser un mécanisme d’annonce adapté si nécessaire.

Ne fais pas disparaître trop vite une information importante.

---

## 80. Live regions

Utilise `aria-live` seulement pour des mises à jour dynamiques qui doivent être annoncées.

Évite une live region sur toute la page.

---

## 81. Skeletons

Les skeleton loaders sont optionnels.

Ils ne doivent pas créer un arbre inaccessible ou empêcher la lecture.

Une interface server-rendered rapide n’en a souvent pas besoin.

---

## 82. Lazy loading images

Pour les images non critiques sous le fold, `loading="lazy"` peut être pertinent.

Ne lazy-load pas automatiquement l’image principale essentielle au rendu sans mesurer l’impact.

---

## 83. Performance frontend

Analyse :

- taille CSS ;
- taille JS ;
- images ;
- requêtes ;
- fonts ;
- duplication.

Ne rajoute pas un bundler complexe uniquement pour gagner quelques Ko sur un petit site.

---

## 84. Fonts

Préférer une stratégie simple et respectueuse :

- système ;
- self-host ;
- fournisseur externe selon politique.

Si fournisseur externe :

- confidentialité ;
- CSP ;
- performance.

---

## 85. CSP

Si le projet utilise une Content Security Policy :

évite les inline scripts/styles non nécessaires.

Coordonne avec `django-security`.

Ne casse pas la CSP en ajoutant systématiquement `'unsafe-inline'`.

---

## 86. Tests frontend Django

Teste les comportements à valeur réelle :

- permission visible ;
- formulaire erreur ;
- redirection ;
- action ;
- composant conditionnel ;
- contenu contextuel important.

Ne teste pas chaque classe CSS ou texte statique.

---

## 87. Tests navigateur

Ajoute des tests navigateur uniquement pour les parcours dont le comportement dépend réellement :

- JavaScript ;
- focus ;
- modal ;
- workflow critique.

Le skill `django-testing` décide du niveau de test approprié.

---

## 88. Accessibilité automatisée

Les outils automatiques peuvent détecter :

- labels manquants ;
- contrastes ;
- ARIA invalide ;
- structure.

Mais ils ne remplacent pas :

- clavier ;
- compréhension ;
- lecteur d’écran ;
- revue humaine.

Ne déclare pas une page « accessible » uniquement parce qu’un scanner passe.

---

## 89. États à considérer

Pour chaque composant important, analyse :

- normal ;
- hover ;
- focus ;
- disabled ;
- loading ;
- error ;
- empty ;
- success.

Ne code pas uniquement le « happy path ».

---

## 90. Disabled vs readonly

Utilise le bon concept :

- disabled : non interactif et généralement non soumis ;
- readonly : visible/soumis mais non modifiable selon contrôle.

Ne désactive pas un champ si le serveur attend sa valeur sans comprendre le comportement HTML.

---

## 91. Confirmation

Après création/modification, la page doit indiquer clairement le résultat.

Si redirect vers détail/list, conserver un message utilisateur utile.

---

## 92. Retour navigation

Après une édition, décide une destination cohérente :

- détail objet ;
- liste ;
- workflow suivant.

Ne construis pas des redirects basés sur une URL `next` non validée.

Charge `django-security`.

---

## 93. Pages d’erreur

Prévois des pages adaptées pour :

- 404 ;
- 403 ;
- 500.

En production :

- aucune stack trace ;
- message humain ;
- navigation possible.

---

## 94. 403 vs 404 UX

Respecte la politique sécurité du projet.

Ne révèle pas une ressource privée si le backend choisit 404 pour la masquer.

---

## 95. Admin vs frontend public

Ne reproduis pas l’admin Django comme interface utilisateur finale simplement parce qu’il existe.

L’admin est destiné à l’administration interne.

Construis les workflows métier réels dans le frontend lorsque nécessaire.

---

## 96. Frontend et domaine

Le frontend doit utiliser le vocabulaire métier.

Évite de montrer :

- noms de champs DB ;
- codes internes ;
- statuts techniques ;

si des termes utilisateur existent.

---

## 97. Documentation composants

Documente les composants réutilisables importants dans `docs/frontend/` ou la documentation adaptée.

Inclure si nécessaire :

- rôle ;
- variantes ;
- paramètres ;
- accessibilité ;
- exemple.

Ne documente pas chaque div.

---

## 98. Décision framework UI

Une décision structurante comme :

- Tailwind ;
- Bootstrap ;
- HTMX ;
- Alpine ;
- React ;

doit être consignée dans `docs/architecture/decisions.md`.

Explique :

- besoin ;
- pourquoi ;
- alternatives ;
- conséquences.

---

## 99. Relecture second développeur

Avant de terminer une feature frontend, vérifie :

- HTML sémantique ?
- labels ?
- clavier ?
- focus ?
- erreurs ?
- mobile ?
- empty state ?
- permission backend ?
- CSRF ?
- XSS ?
- JS nécessaire ?
- duplication ?
- composants cohérents ?
- assets bien placés ?
- N+1 caché dans template ?
- docs ?

---

## 100. Definition of Done frontend

Une feature frontend est terminée lorsque les points applicables sont satisfaits :

- flux utilisateur clair ;
- HTML sémantique ;
- responsive ;
- formulaires serveur validés ;
- erreurs compréhensibles ;
- permissions serveur ;
- CSRF ;
- échappement sûr ;
- clavier ;
- focus ;
- labels ;
- JS progressif si pertinent ;
- static correctement organisés ;
- performance raisonnable ;
- tests pertinents ;
- documentation mise à jour ;
- seconde revue effectuée.

---

## 101. Principe final

Une bonne interface Django ne doit pas lutter contre le web.

Utilise les capacités natives du navigateur et de Django avant d’ajouter des abstractions.

Chaque couche JavaScript ou composant custom doit apporter plus de valeur qu’il n’ajoute de complexité.
