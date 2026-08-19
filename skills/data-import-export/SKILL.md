---
name: data-import-export
description: Imports et exports de données Django robustes : validation, gros volumes, reprise, sécurité, confidentialité et formats.
compatibility: opencode
metadata:
  framework: django
  language: fr
  workflow-parent: project-workflow
---

# Data Import / Export

## Mission
Importer et exporter sans corruption, fuite de données ni consommation mémoire incontrôlée.

## Formats
CSV convient souvent aux tableaux. XLSX peut être utile pour utilisateurs métier. JSON pour échanges structurés. Choisir selon le besoin, pas selon préférence technique.

## Import : pipeline
1. réception ;
2. validation fichier ;
3. parsing ;
4. normalisation ;
5. validation métier ;
6. preview/dry-run si utile ;
7. écriture ;
8. rapport.

Ne mélange pas parsing et écriture ligne par ligne sans stratégie d’erreur.

## Mapping
Définir colonnes obligatoires, optionnelles, types, valeurs autorisées, encodage et comportement des champs inconnus.

## Doublons
Définir explicitement : ignorer, mettre à jour, erreur ou fusionner. Utiliser une clé métier stable.

## Atomicité
Pour petit import, transaction globale possible. Pour gros import, batches et stratégie de reprise peuvent être préférables.

## Gros volumes
Streaming/chunks, mémoire bornée, bulk operations quand sûres, tâche asynchrone si long.

## Rapport
Retourner lignes réussies, erreurs avec numéro de ligne et raison, sans exposer inutilement des données sensibles.

## Export
Appliquer exactement les permissions et scopes de visibilité. Un export est une surface d’exfiltration.

## CSV injection
Pour exports destinés aux tableurs, traiter les cellules commençant par caractères de formule dangereux selon la politique du projet.

## Confidentialité
Pour exports contenant des données personnelles : minimisation, audit, expiration du fichier, accès contrôlé. Charger `privacy-rgpd`.

## Tests
Encodage, colonnes manquantes, types invalides, doublons, gros fichier raisonnable, permission, CSV injection et reprise.
## Questions et coordination
Lis `AGENTS.md`, charge `project-workflow` et `feature-design` si le changement est métier. Pose au maximum deux questions utilisateur à la fois uniquement lorsqu'une décision fonctionnelle est réellement nécessaire. Charge sécurité, tests, performance, privacy, documentation et dépendances selon l'impact.

## Definition of Done
La modification doit avoir passé les contrôles applicables : comportement, erreurs, permissions, sécurité, performance, tests pertinents, documentation et relecture second développeur.

## Principe final
Préférer une solution explicite, observable et maintenable à une automatisation « magique » difficile à diagnostiquer.
