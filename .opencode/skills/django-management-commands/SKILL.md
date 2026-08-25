---
name: django-management-commands
description: Conception de commandes manage.py sûres, idempotentes, documentées et adaptées à l’exploitation.
compatibility: opencode
metadata:
  framework: django
  language: fr
  workflow-parent: project-workflow
---

# Django Management Commands

## Mission
Créer des commandes `manage.py` pour les opérations explicites, reproductibles et administrables.

## Bons usages
Imports, maintenance, réparation contrôlée, synchronisation, initialisation, purge, rapports et opérations ponctuelles.

## Structure
Utiliser `BaseCommand`, `add_arguments()` et `handle()`. Garder la logique métier dans services/modules réutilisables plutôt que dans une commande gigantesque.

## Sorties
Utiliser `self.stdout` / `self.stderr` et les styles Django plutôt que des `print()` dispersés.

## Idempotence
Une commande d’exploitation doit idéalement pouvoir être relancée sans créer de doublons ou corruption.

## Dry-run
Pour une opération destructive ou massive, proposer `--dry-run` lorsque pertinent.

## Confirmation
Les suppressions/migrations métier dangereuses nécessitent confirmation explicite ou option dédiée. En CI/cron, prévoir un mode non-interactif contrôlé.

## Transactions
Utiliser `transaction.atomic()` pour une unité cohérente, sans enfermer des appels externes lents dans une transaction DB inutilement longue.

## Batch
Pour gros volumes : pagination/iterator/batch, mémoire bornée, progression, reprise éventuelle.

## Sécurité
Ne pas accepter une commande shell construite depuis une entrée non fiable. Ne pas afficher de secrets.

## Environnements
Une commande dangereuse doit pouvoir détecter/protéger la production lorsque nécessaire, mais ne se fie pas uniquement à un nom d’environnement pour l’autorisation.

## Documentation
Documenter objectif, options, exemple, caractère destructif, durée et fréquence si cron.

## Tests
Tester parsing important, dry-run, idempotence et effets métier.
## Questions et coordination
Lis `AGENTS.md`, charge `project-workflow` et `feature-design` si le changement est métier. Pose au maximum deux questions utilisateur à la fois uniquement lorsqu'une décision fonctionnelle est réellement nécessaire. Charge sécurité, tests, performance, privacy, documentation et dépendances selon l'impact.

## Definition of Done
La modification doit avoir passé les contrôles applicables : comportement, erreurs, permissions, sécurité, performance, tests pertinents, documentation et relecture second développeur.

## Principe final
Préférer une solution explicite, observable et maintenable à une automatisation « magique » difficile à diagnostiquer.
