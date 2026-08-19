---
name: audit-logging
description: Traçabilité des actions sensibles, journaux d’audit et logs applicatifs sans fuite de données.
compatibility: opencode
metadata:
  framework: django
  language: fr
  workflow-parent: project-workflow
---

# Audit & Logging

## Mission
Séparer les logs techniques des traces d’audit métier et rendre les incidents compréhensibles sans journaliser des secrets.

## Deux besoins distincts
**Logging technique** : erreurs, warnings, diagnostic, performance.
**Audit métier** : qui a fait quoi, sur quelle ressource, quand, et avec quel résultat.

Ne transforme pas tous les logs en audit et inversement.

## Logging
Utiliser le système `logging` Python/Django. Préférer des loggers par module/app et des niveaux cohérents : DEBUG, INFO, WARNING, ERROR, CRITICAL.

En production, ne pas dépendre de `print()`.

## Données interdites
Ne jamais journaliser volontairement :
- mots de passe ;
- SECRET_KEY ;
- tokens ;
- cookies/session ;
- Authorization headers ;
- clés API ;
- contenu sensible inutile.

Masquer/redacter les champs sensibles.

## PII
Minimiser les données personnelles. Charger `privacy-rgpd` lorsqu’un journal permet d’identifier une personne.

## Correlation
Pour les systèmes où cela apporte une valeur, ajouter un request/correlation ID afin de suivre une requête entre composants.

## Audit
Une entrée d’audit importante peut contenir :
- acteur ;
- action ;
- ressource/type/id ;
- timestamp ;
- résultat ;
- contexte minimal utile.

Éviter de stocker une copie complète avant/après de chaque objet sans besoin.

## Immutabilité
Les utilisateurs ordinaires ne doivent pas pouvoir modifier les traces d’audit. Définir rétention, accès et sauvegarde.

## Actions à auditer
Exemples : permissions/rôles, suppressions sensibles, exports, changements de sécurité, actions administratives, accès à certaines données critiques.

## Erreurs
Une exception inattendue doit être loguée avec contexte technique utile, sans exposer ce contexte à l’utilisateur final.

## Production
Configurer destination, rotation/rétention et collecte selon l’hébergement. Les logs ne doivent pas remplir le disque du serveur.

## Tests
Tester les événements d’audit critiques et surtout l’absence de secrets dans les chemins sensibles. Ne tester pas la bibliothèque logging elle-même.
## Questions et coordination
Lis `AGENTS.md`, charge `project-workflow` et `feature-design` si le changement est métier. Pose au maximum deux questions utilisateur à la fois uniquement lorsqu'une décision fonctionnelle est réellement nécessaire. Charge sécurité, tests, performance, privacy, documentation et dépendances selon l'impact.

## Definition of Done
La modification doit avoir passé les contrôles applicables : comportement, erreurs, permissions, sécurité, performance, tests pertinents, documentation et relecture second développeur.

## Principe final
Préférer une solution explicite, observable et maintenable à une automatisation « magique » difficile à diagnostiquer.
