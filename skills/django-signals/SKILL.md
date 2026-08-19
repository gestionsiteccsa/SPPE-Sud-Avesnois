---
name: django-signals
description: Usage discipliné des signaux Django afin d’éviter les effets de bord cachés et les architectures difficiles à maintenir.
compatibility: opencode
metadata:
  framework: django
  language: fr
  workflow-parent: project-workflow
---

# Django Signals

## Mission
Utiliser les signaux uniquement pour du découplage réellement utile.

## Règle principale
Ne mets pas la logique métier centrale dans `post_save` simplement pour éviter d’appeler explicitement un service.

Une action essentielle doit être visible dans le workflow.

## Bons usages
- invalidation/cache découplée ;
- intégration d’une app réutilisable ;
- instrumentation/audit ciblé ;
- réaction réellement transversale.

## Mauvais usages
- créer automatiquement une chaîne d’objets métier complexe ;
- envoyer plusieurs emails ;
- appels API externes ;
- modifier le même modèle en boucle ;
- remplacer un service métier.

## Transactions
`post_save` peut s’exécuter avant le commit final. Pour un effet externe dépendant de la transaction, utiliser `transaction.on_commit()` lorsque pertinent.

## Récursion
Prévenir les boucles save → signal → save.

## Bulk operations
Ne suppose pas que `bulk_create`, `bulk_update` ou `QuerySet.update()` déclenchent les mêmes signaux qu’un `save()` individuel.

## Registration
Enregistrer les receivers de façon claire et éviter les doubles registrations.

## Performance
Un signal s’exécute implicitement. Une requête supplémentaire dans un receiver peut devenir un N+1 invisible.

## Tests
Tester l’effet métier observable. Si le signal est important, tester qu’il se déclenche dans les chemins réellement supportés.

## Documentation
Tout signal non trivial doit être documenté car son effet n’est pas visible au point d’appel.
## Questions et coordination
Lis `AGENTS.md`, charge `project-workflow` et `feature-design` si le changement est métier. Pose au maximum deux questions utilisateur à la fois uniquement lorsqu'une décision fonctionnelle est réellement nécessaire. Charge sécurité, tests, performance, privacy, documentation et dépendances selon l'impact.

## Definition of Done
La modification doit avoir passé les contrôles applicables : comportement, erreurs, permissions, sécurité, performance, tests pertinents, documentation et relecture second développeur.

## Principe final
Préférer une solution explicite, observable et maintenable à une automatisation « magique » difficile à diagnostiquer.
