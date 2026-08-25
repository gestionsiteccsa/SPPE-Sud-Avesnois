---
name: django-email
description: Conçoit les emails transactionnels, de sécurité et notifications Django de façon fiable et testable.
compatibility: opencode
metadata:
  framework: django
  purpose: email
  language: fr
  workflow-parent: project-workflow
---

# Django Email

## Mission
Concevoir des emails fiables, sobres et sûrs : transactionnels, notifications, vérification et récupération.

## Types
Distinguer :
- transactionnel ;
- sécurité ;
- notification métier ;
- marketing.
Le marketing relève aussi de `privacy-rgpd`.

## Environnements
- Dev/test : backend console/memory ou capture locale.
- Staging : neutraliser les destinataires réels.
- Prod : provider SMTP/API configuré par secrets.
Ne jamais mettre de credentials dans Git.

## Envoi
Utiliser les APIs Django ou une abstraction simple. Pour beaucoup d'emails ou provider lent, envisager `background-tasks`.

## Templates
Prévoir texte brut + HTML lorsque pertinent. Les templates doivent rester simples, compatibles clients email et accessibles.

## Liens
Les liens d'activation/reset doivent :
- utiliser le bon domaine ;
- HTTPS en production ;
- token temporaire sûr ;
- ne pas exposer de secret dans les logs.

## Idempotence
Un retry ne doit pas produire des effets dangereux ou spammer. Les notifications importantes peuvent avoir une clé/état d'envoi.

## Erreurs
Définir ce qui se passe si l'envoi échoue :
- retry ;
- log ;
- état en attente ;
- action utilisateur.
Ne pas annuler une transaction métier déjà validée uniquement parce qu'un email secondaire échoue, sauf exigence métier.

## Confidentialité
Minimiser le contenu sensible : notifications sur écran verrouillé, forwarding, boîtes partagées.

## Tests
Utiliser le backend de test Django. Vérifier destinataire, type d'email, sujet/éléments métier essentiels et absence d'envoi quand interdit. Ne pas tester SMTP lui-même.

## Questions utilisateur

Quand un choix métier ou UX est réellement nécessaire, pose au maximum deux questions à la fois, en langage accessible, avec une courte explication du pourquoi. Ne demande pas au non-développeur de choisir une technique quand une bonne pratique claire existe.

## Coordination

Lis `AGENTS.md` et charge `project-workflow`. Utilise `feature-design` avant toute évolution métier structurante. Charge les skills transversaux pertinents : `django-security`, `django-testing`, `django-performance`, `privacy-rgpd`, `accessibility`, `documentation`, `dependency-management`.

## Definition of Done

La feature n'est terminée que lorsque les comportements importants, permissions, erreurs, sécurité, tests, documentation et impacts techniques pertinents ont été revus.

## Principe final

Reste proportionné : utilise les abstractions Django et du Web lorsque possible, et n'ajoute pas de complexité sans valeur claire.
