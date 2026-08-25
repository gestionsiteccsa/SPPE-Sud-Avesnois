---
name: background-tasks
description: Conçoit les tâches asynchrones et périodiques Django : idempotence, retries, transactions, workers et observabilité.
compatibility: opencode
metadata:
  framework: django
  purpose: background-tasks
  language: fr
  workflow-parent: project-workflow
---

# Background Tasks

## Mission
Déplacer hors requête web les traitements longs, retryables ou différés quand cela apporte une vraie valeur.

## Quand
Pertinent pour :
- emails volumineux ;
- imports/exports ;
- génération fichiers ;
- traitement image ;
- appels externes lents ;
- rapports ;
- tâches périodiques.
Pas pour une opération de quelques millisecondes.

## Choix outil
Évaluer d'abord les mécanismes disponibles dans la version Django et l'infrastructure. Celery/RQ/autre seulement si le besoin dépasse la solution simple.

## Idempotence
Une tâche peut être exécutée plusieurs fois. Concevoir pour éviter doublons :
- clé métier ;
- contrainte DB ;
- statut ;
- transaction.

## Arguments
Passer des IDs simples, pas des objets ORM sérialisés complets. Recharger l'état dans la tâche.

## Transactions
Planifier après commit si la tâche dépend de données qui viennent d'être écrites.

## Retries
Retry uniquement sur erreurs transitoires. Backoff, limite et distinction erreur permanente/transitoire.

## Dead letter / échecs
Prévoir logs, statut, alerte et reprise manuelle pour les tâches importantes.

## Tâches périodiques
Un seul scheduler logique. Documenter fréquence, timezone, verrou et comportement si une exécution précédente continue.

## Sécurité
Ne pas mettre de secret dans payload/log. Ne pas exécuter une commande construite depuis des données utilisateur.

## Observabilité
Durée, backlog, erreurs, retries, dernière exécution, worker vivant.

## Tests
Tester fonction métier séparément, idempotence, retry et erreur. Ne pas démarrer un vrai worker dans toute la suite.

## Questions utilisateur

Quand un choix métier ou UX est réellement nécessaire, pose au maximum deux questions à la fois, en langage accessible, avec une courte explication du pourquoi. Ne demande pas au non-développeur de choisir une technique quand une bonne pratique claire existe.

## Coordination

Lis `AGENTS.md` et charge `project-workflow`. Utilise `feature-design` avant toute évolution métier structurante. Charge les skills transversaux pertinents : `django-security`, `django-testing`, `django-performance`, `privacy-rgpd`, `accessibility`, `documentation`, `dependency-management`.

## Definition of Done

La feature n'est terminée que lorsque les comportements importants, permissions, erreurs, sécurité, tests, documentation et impacts techniques pertinents ont été revus.

## Principe final

Reste proportionné : utilise les abstractions Django et du Web lorsque possible, et n'ajoute pas de complexité sans valeur claire.
