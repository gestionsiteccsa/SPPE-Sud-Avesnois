---
name: search
description: Conçoit la recherche et les filtres d’un projet Django, de l’ORM simple au full-text PostgreSQL.
compatibility: opencode
metadata:
  framework: django
  purpose: search
  language: fr
  workflow-parent: project-workflow
---

# Search

## Mission
Concevoir une recherche utile, pertinente et proportionnée au volume du projet.

## Commencer simple
Pour petit volume :
- filtres ORM ;
- `icontains` ciblé ;
- PostgreSQL si déjà utilisé.
Ne pas ajouter Elasticsearch/OpenSearch par réflexe.

## Champs
Définir explicitement ce qui est recherchable. Éviter de chercher dans des données privées ou champs internes sans besoin.

## PostgreSQL
Selon le besoin :
- index B-tree ;
- trigrammes ;
- full-text search ;
- GIN/GiST.
Analyser `EXPLAIN` pour les requêtes significatives.

## Pertinence
Décider si la recherche doit être :
- correspondance simple ;
- préfixe ;
- fuzzy ;
- full-text ;
- pondérée.
Ne pas prétendre à une pertinence « intelligente » sans règle.

## Filtres
Les filtres doivent être combinables, partageables via query params lorsque pertinent, et bornés.

## Pagination
Toute recherche potentiellement volumineuse doit être paginée. Ordre stable.

## Sécurité
Appliquer d'abord le scope de visibilité/tenant/permission, puis la recherche. Une recherche ne doit jamais révéler l'existence d'une ressource privée.

## UX
État vide, correction, filtres actifs, réinitialisation, loading si recherche dynamique. Charger `javascript` si instantanée.

## Tests
Pertinence métier, permissions, filtres, limites, caractères spéciaux, accents si pertinents, et nombre de requêtes pour endpoint critique.

## Questions utilisateur

Quand un choix métier ou UX est réellement nécessaire, pose au maximum deux questions à la fois, en langage accessible, avec une courte explication du pourquoi. Ne demande pas au non-développeur de choisir une technique quand une bonne pratique claire existe.

## Coordination

Lis `AGENTS.md` et charge `project-workflow`. Utilise `feature-design` avant toute évolution métier structurante. Charge les skills transversaux pertinents : `django-security`, `django-testing`, `django-performance`, `privacy-rgpd`, `accessibility`, `documentation`, `dependency-management`.

## Definition of Done

La feature n'est terminée que lorsque les comportements importants, permissions, erreurs, sécurité, tests, documentation et impacts techniques pertinents ont été revus.

## Principe final

Reste proportionné : utilise les abstractions Django et du Web lorsque possible, et n'ajoute pas de complexité sans valeur claire.
