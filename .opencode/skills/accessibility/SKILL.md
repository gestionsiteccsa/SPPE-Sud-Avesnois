---
name: accessibility
description: Conçoit, audite et maintient l’accessibilité d’un projet Django/frontend selon WCAG et, lorsqu’applicable, RGAA. À utiliser pour formulaires, navigation, composants interactifs, modales, tableaux, erreurs, focus, clavier, ARIA, contrastes, contenus dynamiques, images et tests d’accessibilité. Privilégie HTML natif, progressive enhancement et vérifications manuelles en complément des outils automatiques.
compatibility: opencode
metadata:
  framework: django
  purpose: accessibility
  language: fr
  workflow-parent: project-workflow
---

# Accessibility

## 1. Mission

Tu es responsable de l’accessibilité de l’interface.

Ton objectif est que les fonctionnalités soient utilisables par le plus grand nombre, notamment :

- au clavier ;
- avec lecteur d’écran ;
- avec zoom important ;
- avec contraste élevé ;
- sans perception des couleurs ;
- avec réduction des animations ;
- sur mobile ;
- avec technologies d’assistance.

L’accessibilité doit être intégrée dès la conception.

---

## 2. Coordination

Avant toute modification importante :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. charge `frontend-django` ;
4. charge `django-testing` si des tests sont ajoutés ;
5. charge `django-security` si un composant touche à des flux sensibles ;
6. inspecte le design system et les composants existants.

---

## 3. Référentiels

Base de travail :

- WCAG 2.2 ;
- WAI-ARIA Authoring Practices ;
- RGAA lorsque le contexte français/public le rend pertinent.

Ne prétends pas certifier juridiquement une conformité complète sans audit approprié.

---

## 4. Principe HTML natif

Règle :

> Utiliser d’abord l’élément HTML natif qui correspond au besoin.

Exemples :

- bouton → `<button>`
- navigation → `<nav>`
- lien → `<a>`
- formulaire → `<form>`
- titre → `<h1>` à `<h6>`
- tableau → `<table>`

Évite de recréer un bouton avec un `div`.

---

## 5. ARIA

Règle :

> No ARIA is better than bad ARIA.

ARIA ne remplace pas la sémantique HTML.

N’ajoute ARIA que lorsque :

- le composant natif ne suffit pas ;
- le pattern est compris ;
- l’état est maintenu correctement.

---

## 6. Clavier

Toute fonctionnalité interactive doit être utilisable sans souris.

Vérifie :

- Tab ;
- Shift+Tab ;
- Enter ;
- Space ;
- Escape ;
- flèches pour widgets appropriés.

Ne piège jamais le focus sauf dans un composant qui l’exige temporairement, comme une modal.

---

## 7. Focus visible

Le focus doit être visible.

Ne supprime pas :

```css
outline: none;
```

sans remplacement clair.

---

## 8. Ordre de focus

L’ordre doit suivre la logique du DOM et de l’interface.

Évite `tabindex` positif.

Utilise :

- `tabindex="0"` avec parcimonie ;
- `tabindex="-1"` pour focus programmatique si nécessaire.

---

## 9. Skip link

Pour une interface avec navigation répétée, prévois un lien d’évitement vers le contenu principal.

Exemple :

```text
Aller au contenu principal
```

Il doit devenir visible au focus.

---

## 10. Landmarks

Utilise correctement :

- header ;
- nav ;
- main ;
- aside ;
- footer.

Une page doit généralement avoir un seul `main`.

---

## 11. Titres

Structure les titres logiquement.

Évite les titres choisis uniquement pour leur taille visuelle.

Le CSS gère le style ; le niveau de heading gère la structure.

---

## 12. H1

Une page doit avoir un titre principal clair.

Ne crée pas plusieurs `h1` ambigus sans raison.

---

## 13. Labels

Chaque champ de formulaire doit avoir un label accessible.

Le placeholder ne remplace pas le label.

Le label visible est préférable lorsque possible.

---

## 14. Association label/champ

Utilise correctement :

```html
<label for="email">Email</label>
<input id="email" ...>
```

ou les mécanismes Django équivalents.

---

## 15. Required

Un champ obligatoire doit être annoncé clairement.

Ne communique pas uniquement par un astérisque sans explication.

Utilise les mécanismes HTML appropriés lorsque pertinent.

---

## 16. Instructions

Les instructions doivent être disponibles avant que l’utilisateur ne fasse l’erreur.

Exemple :

- format date ;
- contraintes mot de passe ;
- taille maximale fichier.

---

## 17. Erreurs

Une erreur doit indiquer :

- quel champ ;
- ce qui ne va pas ;
- comment corriger.

Évite :

```text
Valeur invalide.
```

si une explication plus utile est possible.

---

## 18. Résumé d’erreurs

Pour un formulaire complexe, un résumé en haut de page peut être utile.

Il doit :

- être focusable si nécessaire ;
- lister les erreurs ;
- pointer vers les champs.

---

## 19. Couleur

Ne transmets jamais une information uniquement par couleur.

Exemple :

- rouge + texte ;
- vert + icône + message.

---

## 20. Contraste

Vérifie les contrastes texte/fond et éléments interactifs selon WCAG.

Ne choisis pas des couleurs uniquement sur critère esthétique.

---

## 21. Texte redimensionné

L’interface doit rester utilisable avec zoom important.

Évite :

- conteneurs fixes ;
- texte coupé ;
- overflow cachant du contenu.

---

## 22. Reflow

À faible largeur/fort zoom, le contenu doit rester utilisable sans scroll horizontal excessif, sauf contenus naturellement tabulaires ou graphiques.

---

## 23. Responsive

L’accessibilité mobile fait partie de l’accessibilité.

Teste :

- petit écran ;
- orientation ;
- zoom ;
- boutons assez grands.

---

## 24. Target size

Les cibles tactiles doivent être suffisamment grandes et espacées selon les recommandations applicables.

Évite les petites icônes cliquables collées.

---

## 25. Images

Image informative :

- `alt` pertinent.

Image décorative :

```html
alt=""
```

Ne mets pas :

```text
image de...
```

inutilement.

---

## 26. Images complexes

Graphiques/diagrammes importants doivent avoir une alternative textuelle ou données équivalentes.

---

## 27. Icônes

Une icône seule comme bouton doit avoir un nom accessible.

Exemple :

```text
Supprimer
```

pas :

```text
Icône poubelle
```

---

## 28. SVG

Pour SVG décoratif :

- masquer aux technologies d’assistance si nécessaire.

Pour SVG informatif :

- fournir un nom/description adaptée.

---

## 29. Tables

Utilise `<table>` uniquement pour des données tabulaires.

Ajoute :

- headers ;
- scope ;
- caption si utile.

---

## 30. Tableau complexe

Pour des relations de headers complexes, documente soigneusement la structure.

Si la table devient trop complexe, envisage une présentation plus simple.

---

## 31. Tri de tableau

Si une colonne est triable :

- indiquer l’état ;
- nom accessible ;
- clavier ;
- mise à jour annoncée si dynamique.

---

## 32. Pagination

Les liens de pagination doivent être compréhensibles.

Préférer :

```text
Page suivante
Page précédente
Page 3
```

plutôt que seulement des chevrons sans nom.

---

## 33. Menus

Un menu de navigation classique est généralement une liste de liens.

N’utilise pas `role="menu"` pour une navbar ordinaire si le comportement ne suit pas le pattern ARIA Menu.

---

## 34. Dropdown

Un dropdown doit gérer :

- bouton déclencheur ;
- état expanded ;
- clavier ;
- fermeture Escape si pertinent ;
- focus logique.

---

## 35. Modal

Une modal doit gérer :

- nom accessible ;
- focus initial ;
- focus contenu ;
- Escape ;
- retour focus déclencheur ;
- arrière-plan non interactif selon pattern.

Ne crée pas une modal custom si `<dialog>` et une stratégie accessible répondent au besoin.

---

## 36. Dialog natif

`<dialog>` peut être une bonne base mais doit être utilisé/testé correctement.

Ne suppose pas que l’élément natif résout tout automatiquement.

---

## 37. Tabs

Un système d’onglets custom doit suivre un pattern accessible :

- rôle tabs ;
- tablist ;
- aria-selected ;
- navigation clavier ;
- association panel.

Si des liens simples suffisent, préfère-les.

---

## 38. Accordion

Utilise des boutons pour contrôler l’ouverture.

Expose l’état avec `aria-expanded` si nécessaire.

`<details>/<summary>` peut souvent être préférable.

---

## 39. Carousel

Évite les carrousels automatiques si non nécessaires.

Si présent :

- pause ;
- clavier ;
- contrôle ;
- réduction motion ;
- noms accessibles.

---

## 40. Tooltip

Un tooltip ne doit pas contenir une information indispensable uniquement au hover.

Il doit fonctionner clavier/focus.

---

## 41. Hover

Toute information disponible au hover doit également être accessible au clavier.

---

## 42. Motion

Respecte :

```css
@media (prefers-reduced-motion: reduce)
```

pour animations non essentielles.

---

## 43. Clignotements

Évite les flashs pouvant déclencher des crises.

Respecte les seuils WCAG applicables.

---

## 44. Temps limité

Si une action a une limite de temps, l’utilisateur doit pouvoir être averti et, si possible, prolonger.

Exception seulement si le temps est intrinsèque au besoin.

---

## 45. Session expiration

Pour session sensible, avertis avant expiration si le workflow peut entraîner une perte de travail importante.

---

## 46. Contenus dynamiques

Pour une mise à jour sans navigation complète :

- focus ;
- `aria-live` si nécessaire ;
- message visible ;
- état loading.

N’annonce pas chaque changement mineur.

---

## 47. Live regions

Utilise :

- `polite` pour informations ;
- `assertive` seulement pour urgence.

Trop de live regions créent du bruit.

---

## 48. Loading

Un chargement long doit être annoncé si nécessaire.

Pour bouton :

- disabled/aria-disabled selon comportement ;
- texte de progression.

---

## 49. Disabled

Un élément disabled peut ne pas être focusable.

Si l’utilisateur a besoin de comprendre pourquoi une action est indisponible, explique-le à proximité.

---

## 50. Erreurs JavaScript

Si JS échoue, l’utilisateur doit idéalement pouvoir terminer les actions de base via le serveur.

Principe de progressive enhancement.

---

## 51. Drag and drop

Toute interaction drag-and-drop doit avoir une alternative clavier.

---

## 52. Réorganisation

Si l’utilisateur peut réordonner une liste, prévois des contrôles accessibles :

- monter ;
- descendre ;
- position.

---

## 53. Autocomplete

Les champs autocomplete custom doivent suivre les patterns combobox si réellement nécessaires.

Pour une liste simple, un `<select>` peut être plus robuste.

---

## 54. Select

Ne remplace pas les `<select>` natifs par des widgets custom uniquement pour le style.

---

## 55. Date picker

Un input date natif peut être préférable si compatible avec les besoins.

Un datepicker custom doit être entièrement clavier/lecteur d’écran.

---

## 56. Validation en direct

Ne déclenche pas des erreurs agressives pendant la frappe.

Attends un moment approprié :

- blur ;
- submit ;
- état stable.

---

## 57. Mot de passe

Pour contraintes mot de passe :

- instructions visibles ;
- statut clair ;
- pas uniquement couleurs.

---

## 58. CAPTCHA

Évite CAPTCHA inaccessible si possible.

Privilégie des mécanismes d’abus moins intrusifs.

Si CAPTCHA nécessaire, prévoir alternative accessible.

---

## 59. Auth MFA

Les flux MFA doivent fonctionner :

- clavier ;
- lecteur d’écran ;
- copie/collage si pertinent ;
- codes recovery accessibles.

---

## 60. PDF/documents

Si le projet génère des PDF ou documents destinés au public, leur accessibilité doit être analysée séparément.

Ce skill couvre principalement l’interface web.

---

## 61. Langue de page

Définis correctement :

```html
<html lang="fr">
```

ou langue dynamique.

---

## 62. Changements de langue

Balise les passages dans une autre langue si cela améliore la prononciation des lecteurs d’écran.

---

## 63. Abréviations

Évite les acronymes non expliqués dans les contenus grand public.

---

## 64. Instructions sensorielles

Évite :

```text
cliquez sur le bouton rouge à droite
```

Préférer :

```text
sélectionnez « Enregistrer »
```

---

## 65. Liens

Le texte du lien doit être compréhensible.

Évite une page remplie de :

```text
Cliquez ici
En savoir plus
```

sans contexte accessible.

---

## 66. Nouvel onglet

N’ouvre pas une nouvelle fenêtre/onglet sans raison.

Si nécessaire et potentiellement surprenant, informe l’utilisateur.

---

## 67. Breadcrumb

Le fil d’Ariane doit utiliser une structure adaptée et indiquer la page courante.

---

## 68. Navigation cohérente

Les éléments de navigation récurrents doivent garder un ordre et comportement cohérents.

---

## 69. Composants cohérents

Un même composant doit fonctionner de la même façon partout.

---

## 70. Orientation

Ne bloque pas une interface uniquement en portrait ou paysage sauf nécessité.

---

## 71. Gestes complexes

Une fonctionnalité nécessitant un geste multipoint ou trajectoire doit avoir une alternative simple si possible.

---

## 72. Vocal

Les contrôles doivent avoir des noms accessibles cohérents avec les labels visibles, ce qui aide aussi la commande vocale.

---

## 73. Name/Role/Value

Tout composant custom doit exposer correctement :

- nom ;
- rôle ;
- valeur/état.

---

## 74. Status messages

Les messages de statut importants doivent pouvoir être perçus sans déplacement de focus forcé.

---

## 75. Lecteur d’écran

Pour composants importants, une vérification avec lecteur d’écran est recommandée lorsque possible.

Au minimum :

- structure ;
- noms ;
- états ;
- erreurs.

---

## 76. Tests automatisés

Les outils peuvent détecter :

- labels manquants ;
- ARIA invalide ;
- contrastes ;
- structure ;
- landmarks.

Ils ne détectent pas tout.

---

## 77. Outils possibles

Selon stack :

- axe-core ;
- Pa11y ;
- Lighthouse ;
- tests Playwright ;
- extensions navigateur.

N’ajoute pas tous les outils simultanément.

---

## 78. Choix outil

Si un outil d’accessibilité automatisé existe déjà, conserve-le.

Sinon, ajoute un outil seulement si le projet en tire une vraie valeur.

---

## 79. Tests clavier manuels

Une feature interactive importante doit être vérifiée au clavier.

Checklist minimale :

- atteindre ;
- activer ;
- revenir ;
- focus visible ;
- aucun piège.

---

## 80. Zoom manuel

Tester au moins des niveaux de zoom élevés sur les pages critiques lorsque le design change significativement.

---

## 81. Contraste automatisé

Un scanner peut aider mais certains contrastes dynamiques/états nécessitent vérification manuelle.

---

## 82. Tests frontend

Pour les comportements accessibles à forte valeur, ajoute des tests lorsque l’outillage le permet.

Exemples :

- modal focus ;
- aria-expanded ;
- label ;
- erreur associée.

Ne teste pas chaque attribut ARIA statique si cela n’apporte pas de valeur.

---

## 83. Accessibilité et sécurité

Ne compromets pas une protection sécurité pour améliorer l’UX.

Cherche une solution accessible **et** sûre.

---

## 84. Accessibilité et performance

Un composant accessible ne doit pas ajouter une bibliothèque énorme sans raison.

HTML natif est souvent à la fois plus performant et plus accessible.

---

## 85. Accessibilité et React

Si le projet utilise React plus tard, ce skill reste pertinent mais doit se coordonner avec le skill React spécialisé.

---

## 86. RGAA

Pour un projet soumis ou visant RGAA :

- utiliser le référentiel officiel à jour ;
- documenter les non-conformités ;
- ne pas déclarer « conforme » uniquement sur tests automatiques.

---

## 87. Déclaration d’accessibilité

Si légalement/contractuellement nécessaire, elle relève d’un audit et d’informations administratives spécifiques.

Ne la génère pas comme certification automatique.

---

## 88. Audit

Pour une vraie évaluation :

- échantillon représentatif ;
- tests manuels ;
- technologies d’assistance ;
- critères applicables ;
- rapport.

Ce skill prépare le code mais ne remplace pas un audit officiel.

---

## 89. Composant tiers

Avant un composant UI tiers, vérifie :

- clavier ;
- ARIA ;
- maintenance ;
- issues d’accessibilité ;
- capacité à corriger.

Une belle bibliothèque inaccessible est un mauvais choix.

---

## 90. Régression

Une correction d’accessibilité importante doit recevoir un test de régression lorsque pertinent.

---

## 91. Documentation

Pour les composants complexes, documente :

- comportement ;
- clavier ;
- ARIA ;
- variantes ;
- contraintes.

Dans `docs/frontend/` si nécessaire.

---

## 92. Changelog

Une amélioration d’accessibilité importante peut apparaître dans le changelog si elle est visible/utilisateur.

---

## 93. Definition of Done

Pour une feature frontend importante :

- HTML sémantique ;
- labels ;
- clavier ;
- focus ;
- contrastes ;
- responsive/zoom ;
- erreurs ;
- nom/role/value ;
- contenus dynamiques ;
- motion ;
- tests automatiques si configurés ;
- revue manuelle pertinente ;
- documentation si composant complexe.

---

## 94. Relecture second développeur

Demande :

- Puis-je tout faire au clavier ?
- Le focus est-il visible ?
- Les labels sont-ils clairs ?
- Si je ne vois pas les couleurs, comprends-je ?
- Si JS échoue, puis-je continuer ?
- Un lecteur d’écran comprend-il les états ?
- Le zoom casse-t-il l’interface ?
- Avons-nous ajouté ARIA alors qu’un élément natif suffisait ?

---

## 95. Principe final

L’accessibilité n’est pas une couche ajoutée après le design.

Le moyen le plus fiable de produire une interface accessible est souvent de choisir dès le départ les éléments web natifs, simples et prévisibles.
