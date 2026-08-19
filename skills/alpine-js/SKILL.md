---
name: alpine-js
description: Encadre Alpine.js pour les petits états et interactions locales d’un frontend Django.
compatibility: opencode
metadata:
  framework: django
  purpose: alpine-js
  language: fr
  workflow-parent: project-workflow
---

# Alpine.js

## Mission
Utiliser Alpine.js pour de petits états et interactions locales lorsque le projet l'a choisi, sans construire une SPA cachée.

## Bons usages
- dropdown ;
- modal simple ;
- onglets ;
- toggle ;
- état d'un composant ;
- petites transitions.

## Mauvais usages
- logique métier ;
- gros store global ;
- client API complexe ;
- routing SPA ;
- duplication de Django.

## État
Garder `x-data` local au composant. Utiliser un store global uniquement pour un besoin réellement global.

## Sécurité
`x-html` est sensible comme `innerHTML`. Ne jamais y injecter du contenu utilisateur non maîtrisé. Préférer `x-text`.

## CSP
Si le projet utilise une CSP stricte, choisir la stratégie/build Alpine compatible. Ne désactiver pas la CSP par facilité.

## Accessibilité
Les éléments interactifs restent des boutons/liens natifs. Maintenir `aria-expanded`, focus, Escape, navigation clavier selon le composant.

## Django
Les données métier restent serveur. Les petites valeurs initiales peuvent venir de `data-*` ou JSON sûr.

## HTMX
HTMX gère les échanges serveur ; Alpine peut gérer l'état local. Éviter qu'ils pilotent tous deux le même état sans convention.

## Dépendance
Ne l'ajouter que si plusieurs interactions locales profitent de sa simplicité. Pour un simple toggle, JS natif peut suffire.

## Tests
Tester les composants à forte valeur et les interactions accessibles. Ne tester pas Alpine lui-même.

## Questions utilisateur

Quand un choix métier ou UX est réellement nécessaire, pose au maximum deux questions à la fois, en langage accessible, avec une courte explication du pourquoi. Ne demande pas au non-développeur de choisir une technique quand une bonne pratique claire existe.

## Coordination

Lis `AGENTS.md` et charge `project-workflow`. Utilise `feature-design` avant toute évolution métier structurante. Charge les skills transversaux pertinents : `django-security`, `django-testing`, `django-performance`, `privacy-rgpd`, `accessibility`, `documentation`, `dependency-management`.

## Definition of Done

La feature n'est terminée que lorsque les comportements importants, permissions, erreurs, sécurité, tests, documentation et impacts techniques pertinents ont été revus.

## Principe final

Reste proportionné : utilise les abstractions Django et du Web lorsque possible, et n'ajoute pas de complexité sans valeur claire.
