---
name: django-admin
description: Conçoit un Django Admin sûr, performant et limité aux usages internes pertinents.
compatibility: opencode
metadata:
  framework: django
  purpose: admin
  language: fr
  workflow-parent: project-workflow
---

# Django Admin

## Mission
Utiliser l'admin Django comme outil interne d'administration, pas comme frontend métier par défaut.

## Accès
- `is_staff` signifie accès admin, pas rôle métier générique.
- Permissions minimales.
- Comptes individuels.
- MFA fortement recommandé pour les comptes privilégiés si le projet le permet.
- Ne jamais rendre l'admin public sans protections adaptées.

## Querysets
Surcharger `get_queryset()` pour limiter les objets visibles selon droits/organisation. Les permissions objet doivent être respectées.

## Formulaires admin
- Exclure les champs sensibles non modifiables.
- `readonly_fields` pour données système.
- Custom forms pour règles spécifiques.
- Ne pas permettre la modification d'owner/statut critique simplement parce qu'un champ existe.

## Performance
Analyser :
- `list_display` relationnel ;
- `list_select_related` ;
- `search_fields` ;
- filtres ;
- autocomplete ;
- gros COUNT ;
- actions massives.
Charger `django-performance`.

## Actions admin
Toute action destructive ou métier importante doit :
- vérifier les permissions ;
- fonctionner transactionnellement si nécessaire ;
- présenter une confirmation si impact fort ;
- produire un audit si pertinent.

## Recherche
Éviter des `search_fields` sur de gros champs non indexés ou des données privées sans besoin.

## PII
Limiter les colonnes, exports, filtres et recherches sur données personnelles. Charger `privacy-rgpd`.

## Tests
Tester uniquement les customisations significatives : permissions, queryset, actions, formulaires et comportements métier.

## Questions utilisateur

Quand un choix métier ou UX est réellement nécessaire, pose au maximum deux questions à la fois, en langage accessible, avec une courte explication du pourquoi. Ne demande pas au non-développeur de choisir une technique quand une bonne pratique claire existe.

## Coordination

Lis `AGENTS.md` et charge `project-workflow`. Utilise `feature-design` avant toute évolution métier structurante. Charge les skills transversaux pertinents : `django-security`, `django-testing`, `django-performance`, `privacy-rgpd`, `accessibility`, `documentation`, `dependency-management`.

## Definition of Done

La feature n'est terminée que lorsque les comportements importants, permissions, erreurs, sécurité, tests, documentation et impacts techniques pertinents ont été revus.

## Principe final

Reste proportionné : utilise les abstractions Django et du Web lorsque possible, et n'ajoute pas de complexité sans valeur claire.
