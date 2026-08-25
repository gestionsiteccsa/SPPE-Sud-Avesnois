# AGENTS.md — OpenCode Django

## Rôle général

Ce projet utilise un ensemble de skills spécialisés sous :

```text
skills/
```

Le point d’entrée principal est :

```text
skill-router
```

Pour toute demande de développement, commencer par appliquer les règles du routeur afin de charger uniquement les skills nécessaires.

---

## Principes globaux

1. Ne jamais charger tous les skills par défaut.
2. Utiliser `feature-design` avant une feature métier structurante.
3. Poser au maximum deux questions utilisateur à la fois.
4. Les questions doivent être compréhensibles par un non-développeur.
5. Expliquer brièvement pourquoi une question est importante.
6. Proposer une recommandation concrète.
7. Respecter l’architecture existante avant d’en proposer une nouvelle.
8. Éviter le refactoring prévisible sans surarchitecturer.
9. Appliquer des tests pertinents, pas une couverture artificielle.
10. Sécurité par défaut.
11. Documentation française maintenue automatiquement.
12. Contrôle des performances lorsqu’il existe un vrai risque.
13. Aucun secret dans Git.
14. Aucun commit ou push sans demande explicite.
15. Docker reste optionnel si le projet supporte les deux méthodes.
16. Production, test et développement restent séparés.
17. Toute feature importante se termine par une relecture « second développeur ».

---

## Workflow d’une feature

```text
Demande
→ skill-router
→ feature-design si nécessaire
→ contrat de feature
→ tâches
→ tests pertinents / TDD pragmatique
→ implémentation
→ sécurité / performance / privacy / accessibilité selon impact
→ second developer review
→ documentation
→ changelog / tâches
→ quality gates
→ terminé
```

---

## Skills principaux

### Orchestration
- `skill-router`
- `project-workflow`
- `feature-design`

### Architecture / backend
- `django-project-init`
- `django-architecture`
- `django-database`
- `django-forms`
- `django-signals`
- `django-management-commands`

### Auth / sécurité / données
- `django-auth`
- `django-security`
- `privacy-rgpd`
- `audit-logging`

### API / intégrations / données externes
- `django-api`
- `external-integrations`
- `data-import-export`

### Frontend
- `frontend-django`
- `tailwind-css`
- `javascript`
- `htmx`
- `alpine-js`
- `accessibility`

### Fonctionnalités Django
- `django-admin`
- `django-email`
- `django-files-uploads`
- `django-cache`
- `background-tasks`
- `search`
- `seo`
- `django-i18n`

### Qualité
- `django-testing`
- `django-performance`
- `dependency-management`
- `git-quality`
- `documentation`

### Production
- `deployment`
- `backup-restore`
- `operations`
- `ci-cd`

---

## Git

Ne jamais exécuter automatiquement :

```text
git commit
git push
git rebase
git reset --hard
git push --force
```

sans demande explicite.

Quand un push est demandé, exécuter d’abord les quality gates définis par `git-quality`.

---

## Documentation

La documentation est écrite en français.

Elle est mise à jour automatiquement lorsqu’une feature importante change :

- comportement ;
- architecture ;
- modèle ;
- permissions ;
- configuration ;
- déploiement ;
- dépendance structurante.

---

## Questions utilisateur

Quand une décision structurante manque :

- maximum deux questions ;
- pas de jargon inutile ;
- une recommandation ;
- expliquer le pourquoi.

Exemple :

> Un vaisseau peut-il avoir un seul constructeur ou plusieurs ?  
> Je recommande un seul constructeur si chaque modèle appartient à une marque précise, car cela simplifie les relations et les filtres.

Pas :

> ForeignKey ou ManyToMany ?

---

## Sécurité

Les problèmes critiques peuvent bloquer :

- secret exposé ;
- permission manquante ;
- fuite de données ;
- migration manifestement dangereuse ;
- vulnérabilité critique applicable.

Les warnings mineurs ne doivent pas bloquer automatiquement.

---

## Definition of Done globale

Une feature importante est terminée quand les points applicables sont satisfaits :

- besoin couvert ;
- architecture cohérente ;
- tests pertinents ;
- sécurité ;
- performance ;
- privacy ;
- accessibilité ;
- migrations ;
- documentation ;
- changelog/tâches ;
- dépendances ;
- second developer review ;
- quality gates.
