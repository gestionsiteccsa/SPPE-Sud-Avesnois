---
name: seo
description: Conçoit le SEO technique des pages publiques Django : metadata, sitemap, robots, canonical, partage et données structurées.
compatibility: opencode
metadata:
  framework: django
  purpose: seo
  language: fr
  workflow-parent: project-workflow
---

# SEO Django

## Mission
Optimiser l'indexation uniquement pour les pages qui doivent réellement être publiques et découvrables.

## Métadonnées
Chaque page indexable significative :
- title unique ;
- meta description utile ;
- canonical si nécessaire ;
- robots cohérent.

## Headings
Un H1 clair et hiérarchie logique. Le SEO ne justifie pas un HTML non sémantique.

## URLs
Lisibles, stables et cohérentes. Les slugs sont utiles quand ils améliorent l'URL, mais l'identifiant technique reste distinct si nécessaire.

## Sitemap
Utiliser le framework sitemap Django si le projet a assez de pages publiques. Exclure pages privées, temporaires ou inutiles.

## robots.txt
Utiliser pour guider les robots, pas pour protéger des données. Une URL privée doit être protégée par permissions.

## Canonical
Éviter le contenu dupliqué avec query params, variantes ou routes multiples quand pertinent.

## Open Graph
Ajouter Open Graph/Twitter Cards si partage social utile. Ne pas créer de métadonnées sans contenu réel.

## Données structurées
Schema.org uniquement pour un type réellement applicable et conforme au contenu visible.

## Performance
Core Web Vitals et poids frontend peuvent influencer l'expérience et le référencement. Charger `django-performance`.

## Privacy
Ne rendre indexable aucune page contenant des données personnelles privées.

## Tests
Vérifier tags/robots/sitemap/canonical sur pages clés. Ne snapshotter pas tout le `<head>` si fragile.

## Questions utilisateur

Quand un choix métier ou UX est réellement nécessaire, pose au maximum deux questions à la fois, en langage accessible, avec une courte explication du pourquoi. Ne demande pas au non-développeur de choisir une technique quand une bonne pratique claire existe.

## Coordination

Lis `AGENTS.md` et charge `project-workflow`. Utilise `feature-design` avant toute évolution métier structurante. Charge les skills transversaux pertinents : `django-security`, `django-testing`, `django-performance`, `privacy-rgpd`, `accessibility`, `documentation`, `dependency-management`.

## Definition of Done

La feature n'est terminée que lorsque les comportements importants, permissions, erreurs, sécurité, tests, documentation et impacts techniques pertinents ont été revus.

## Principe final

Reste proportionné : utilise les abstractions Django et du Web lorsque possible, et n'ajoute pas de complexité sans valeur claire.
