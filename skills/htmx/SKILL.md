---
name: htmx
description: Encadre l’usage de HTMX avec Django pour des interactions serveur dynamiques sans SPA.
compatibility: opencode
metadata:
  framework: django
  purpose: htmx
  language: fr
  workflow-parent: project-workflow
---

# HTMX

## Mission
Ajouter des interactions serveur dynamiques à Django avec HTMX sans transformer le projet en SPA.

## Quand utiliser
Pertinent pour :
- formulaires partiels ;
- filtres ;
- pagination dynamique ;
- modales ;
- mise à jour d'un fragment ;
- actions simples.
Pas nécessaire pour une page statique.

## Serveur d'abord
La logique reste dans Django. HTMX demande un fragment HTML et remplace une zone du DOM.

## Partials
Séparer proprement les fragments réutilisables sans dupliquer la page entière. Une vue peut rendre page complète ou partial selon convention claire.

## URLs et méthodes
Utiliser les méthodes HTTP adaptées. CSRF obligatoire pour les mutations avec session Django.

## History
Si une interaction modifie un état de navigation utile, utiliser push-url/history de façon cohérente. Le bouton retour doit fonctionner.

## Target/swap
Choisir explicitement `hx-target` et `hx-swap`. Éviter de remplacer de grands morceaux de page sans besoin.

## Erreurs
Gérer 4xx/5xx, validation formulaire, messages et focus. Ne laisser pas une zone vide silencieusement.

## Accessibilité
Après swap significatif : focus, annonces et ordre DOM. Le HTML rendu doit rester sémantique.

## Sécurité
Le client peut modifier les attributs HTMX. Toutes permissions et validations restent serveur.

## Performance
HTMX ne corrige pas un endpoint lent. Paginer et optimiser ORM.

## JavaScript
Utiliser du JS custom uniquement quand HTMX/HTML ne suffit pas. Ne multiplier pas HTMX + Alpine + scripts pour le même composant sans raison.

## Tests
Tester les vues/partials comme des réponses HTTP normales ; tests navigateur seulement pour les interactions complexes.

## Questions utilisateur

Quand un choix métier ou UX est réellement nécessaire, pose au maximum deux questions à la fois, en langage accessible, avec une courte explication du pourquoi. Ne demande pas au non-développeur de choisir une technique quand une bonne pratique claire existe.

## Coordination

Lis `AGENTS.md` et charge `project-workflow`. Utilise `feature-design` avant toute évolution métier structurante. Charge les skills transversaux pertinents : `django-security`, `django-testing`, `django-performance`, `privacy-rgpd`, `accessibility`, `documentation`, `dependency-management`.

## Definition of Done

La feature n'est terminée que lorsque les comportements importants, permissions, erreurs, sécurité, tests, documentation et impacts techniques pertinents ont été revus.

## Principe final

Reste proportionné : utilise les abstractions Django et du Web lorsque possible, et n'ajoute pas de complexité sans valeur claire.
