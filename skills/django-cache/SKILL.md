---
name: django-cache
description: Conçoit et audite le cache Django, son invalidation, ses clés, sa sécurité et son impact performance.
compatibility: opencode
metadata:
  framework: django
  purpose: cache
  language: fr
  workflow-parent: project-workflow
---

# Django Cache

## Mission
Utiliser le cache uniquement lorsqu'il résout un problème mesuré ou très probable.

## Ordre
Avant le cache :
1. corriger N+1 ;
2. optimiser requête ;
3. paginer ;
4. indexer si pertinent ;
5. seulement ensuite cacher.

## Niveaux
Django permet cache site, vue, fragment template et bas niveau. Choisir le niveau le plus petit efficace.

## Clés
Une clé doit inclure tout ce qui influence la valeur :
- objet/version ;
- utilisateur ou tenant si privé ;
- langue ;
- permissions ;
- paramètres pertinents.

## Invalidation
Avant d'implémenter, répondre : « quand et comment cette valeur devient-elle obsolète ? »
Stratégies : TTL, invalidation explicite, version de clé, événements.

## Sécurité
Ne jamais partager un cache contenant des données privées entre utilisateurs/tenants. Une fuite de cache est une fuite de données.

## Redis/Memcached
N'ajouter un service externe que si le besoin le justifie. Le cache local mémoire n'est pas partagé entre processus.

## Stampede
Pour donnée très coûteuse et très demandée : lock, jitter, stale-while-revalidate ou préchauffage si nécessaire. Pas de complexité pour faible trafic.

## Sessions
Si le cache sert aux sessions, comprendre l'impact des évictions et pertes de cache.

## Tests
Tester miss, hit, invalidation et isolation utilisateur/tenant quand le cache fait partie du comportement important.

## Questions utilisateur

Quand un choix métier ou UX est réellement nécessaire, pose au maximum deux questions à la fois, en langage accessible, avec une courte explication du pourquoi. Ne demande pas au non-développeur de choisir une technique quand une bonne pratique claire existe.

## Coordination

Lis `AGENTS.md` et charge `project-workflow`. Utilise `feature-design` avant toute évolution métier structurante. Charge les skills transversaux pertinents : `django-security`, `django-testing`, `django-performance`, `privacy-rgpd`, `accessibility`, `documentation`, `dependency-management`.

## Definition of Done

La feature n'est terminée que lorsque les comportements importants, permissions, erreurs, sécurité, tests, documentation et impacts techniques pertinents ont été revus.

## Principe final

Reste proportionné : utilise les abstractions Django et du Web lorsque possible, et n'ajoute pas de complexité sans valeur claire.
