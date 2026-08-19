---
name: external-integrations
description: Intégrations API tierces et webhooks : timeouts, retries, authentification, idempotence, résilience et sécurité.
compatibility: opencode
metadata:
  framework: django
  language: fr
  workflow-parent: project-workflow
---

# External Integrations

## Mission
Créer une frontière claire entre Django et les services externes.

## Adapter
Encapsuler chaque fournisseur dans un client/service dédié. Le domaine ne doit pas dépendre partout du format JSON du fournisseur.

## Configuration
Base URL, credentials et identifiants viennent de l’environnement/configuration. Aucun secret dans Git.

## Timeouts
Toute requête réseau doit avoir des timeouts explicites adaptés. Une requête web Django ne doit pas pouvoir attendre indéfiniment un tiers.

## Retries
Retry seulement les erreurs transitoires et opérations sûres/idempotentes. Backoff et limite obligatoires.

## Erreurs
Traduire les erreurs fournisseur en exceptions/états applicatifs compréhensibles. Ne pas exposer une réponse brute contenant des informations sensibles.

## Idempotence
Pour créations/paiements/actions critiques, utiliser les mécanismes d’idempotence du fournisseur ou une clé métier locale lorsque disponibles.

## Webhooks
- vérifier signature/authenticité ;
- utiliser le corps brut requis par l’algorithme ;
- rejeter les événements invalides ;
- enregistrer un identifiant d’événement pour éviter les doublons ;
- répondre rapidement ;
- traiter en arrière-plan si long.

## SSRF
Si l’application peut contacter une URL fournie par l’utilisateur, charger `django-security` et appliquer une politique stricte contre SSRF.

## Rate limits
Respecter les quotas, `Retry-After` et backoff. Ne pas créer une boucle de retry agressive.

## Données
Minimiser ce qui est envoyé au tiers. Charger `privacy-rgpd` pour données personnelles.

## Observabilité
Journaliser fournisseur, opération, durée, statut et correlation ID sans token ni payload sensible.

## Tests
Mocker le fournisseur. Tester succès, timeout, 4xx, 5xx, payload invalide, retry, idempotence et signature webhook.
## Questions et coordination
Lis `AGENTS.md`, charge `project-workflow` et `feature-design` si le changement est métier. Pose au maximum deux questions utilisateur à la fois uniquement lorsqu'une décision fonctionnelle est réellement nécessaire. Charge sécurité, tests, performance, privacy, documentation et dépendances selon l'impact.

## Definition of Done
La modification doit avoir passé les contrôles applicables : comportement, erreurs, permissions, sécurité, performance, tests pertinents, documentation et relecture second développeur.

## Principe final
Préférer une solution explicite, observable et maintenable à une automatisation « magique » difficile à diagnostiquer.
