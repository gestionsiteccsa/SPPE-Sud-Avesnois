---
name: skill-router
description: Orchestrateur principal d’un projet Django OpenCode. Analyse chaque demande utilisateur, choisit uniquement les skills nécessaires, détermine leur ordre de chargement, déclenche feature-design quand une demande métier est incomplète, évite la surcharge de contexte, coordonne les contrôles transversaux et conduit la feature jusqu’à sa Definition of Done. À utiliser comme point d’entrée général pour tout travail de développement sur le projet.
compatibility: opencode
metadata:
  framework: django
  purpose: orchestration
  language: fr
  role: master-router
---

# Skill Router

## 1. Mission

Tu es l’orchestrateur principal des skills du projet.

Tu ne remplaces pas les autres skills.

Tu décides :

- lesquels charger ;
- dans quel ordre ;
- lesquels ignorer ;
- quand poser des questions ;
- quand lancer `feature-design` ;
- quand déclencher les contrôles transversaux ;
- quand une feature est prête à coder ;
- quand elle est réellement terminée.

Ton objectif est de maximiser la pertinence tout en minimisant le bruit contextuel.

---

## 2. Règle absolue

Ne charge jamais tous les skills « au cas où ».

Chaque skill doit être justifié par la demande ou par un impact réel détecté.

---

## 3. Point d’entrée

Pour toute demande de développement :

1. lire `AGENTS.md` ;
2. comprendre l’intention utilisateur ;
3. inspecter le contexte projet nécessaire ;
4. classer la demande ;
5. sélectionner les skills ;
6. déterminer s’il faut `feature-design` ;
7. exécuter le workflow ;
8. terminer par les contrôles adaptés.

---

## 4. Catégories de demandes

Classe d’abord la demande dans une ou plusieurs catégories :

- nouvelle feature ;
- correction bug ;
- refactor ;
- modèle/database ;
- auth ;
- API ;
- formulaire ;
- frontend ;
- Tailwind ;
- JavaScript ;
- upload ;
- admin ;
- email ;
- cache ;
- tâches asynchrones ;
- recherche ;
- SEO ;
- i18n ;
- HTMX ;
- Alpine ;
- import/export ;
- intégration externe ;
- commande management ;
- signal ;
- sécurité ;
- performance ;
- dépendances ;
- docs ;
- déploiement ;
- sauvegarde ;
- opérations ;
- CI/CD.

---

## 5. Quand charger `feature-design`

Charge `feature-design` si la demande :

- ajoute une fonctionnalité métier ;
- ajoute une nouvelle entité ;
- ajoute une relation ;
- modifie un workflow utilisateur ;
- introduit des permissions ;
- introduit un cycle de vie/états ;
- touche plusieurs apps ;
- est ambiguë ;
- risque un refactoring structurel.

Ne le charge pas forcément pour :

- typo ;
- petit style CSS ;
- bug localisé évident ;
- changement de texte ;
- simple correction de test.

---

## 6. Ordre général

Ordre recommandé :

```text
skill-router
→ project-workflow
→ feature-design (si nécessaire)
→ skills métier/techniques
→ skills transversaux
→ django-testing
→ documentation
→ git-quality
```

Adapte selon la tâche.

---

## 7. Skills transversaux

Ces skills ne sont pas toujours nécessaires, mais doivent être envisagés :

- `django-security`
- `django-performance`
- `privacy-rgpd`
- `accessibility`
- `dependency-management`
- `audit-logging`

Ne les charge pas mécaniquement.

---

## 8. Sécurité

Charge `django-security` si la feature touche :

- auth ;
- permission ;
- utilisateur ;
- input utilisateur ;
- upload ;
- HTML dynamique ;
- API ;
- URL externe ;
- secret ;
- fichier ;
- action destructive ;
- webhook ;
- admin ;
- données privées.

Pour une simple modification de texte, inutile.

---

## 9. Performance

Charge `django-performance` si :

- liste ;
- ORM complexe ;
- boucle DB ;
- recherche ;
- cache ;
- export/import ;
- gros volume ;
- agrégation ;
- API list ;
- tâche lourde ;
- upload important.

---

## 10. Privacy

Charge `privacy-rgpd` si :

- donnée personnelle ;
- tracking ;
- cookie ;
- export ;
- logs identifiants ;
- analytics ;
- tiers recevant des données ;
- email marketing ;
- profil utilisateur.

---

## 11. Accessibilité

Charge `accessibility` pour toute feature UI significative, notamment :

- formulaire ;
- modal ;
- menu ;
- dropdown ;
- tableau ;
- interaction JS ;
- composants ;
- navigation.

Pas nécessaire pour une migration DB pure.

---

## 12. Dépendances

Charge `dependency-management` si :

- ajout package ;
- suppression package ;
- upgrade ;
- plugin ;
- service externe nécessitant une lib ;
- nouvelle stack frontend.

---

## 13. Logging/Audit

Charge `audit-logging` si :

- action sensible ;
- administration ;
- export ;
- sécurité ;
- changement de rôles ;
- suppression critique ;
- incident ;
- exigence de traçabilité.

---

## 14. Mapping principal

### Authentification

```text
project-workflow
feature-design si flux nouveau
django-auth
django-security
django-testing
documentation
```

Ajouter :
- `privacy-rgpd` si données perso ;
- `django-email` si activation/reset ;
- `audit-logging` si action sensible.

---

## 15. Modèles / base

```text
project-workflow
feature-design
django-architecture
django-database
django-testing
documentation
```

Ajouter :
- `django-performance` si gros volume/requête ;
- `privacy-rgpd` si données perso.

---

## 16. Formulaire

```text
project-workflow
feature-design si workflow métier
django-forms
frontend-django
accessibility
django-testing
```

Ajouter :
- `django-files-uploads` si fichier ;
- `javascript` si interaction dynamique ;
- `tailwind-css` si Tailwind.

---

## 17. Upload

```text
project-workflow
feature-design si nouveau workflow
django-files-uploads
django-security
privacy-rgpd si données perso
django-testing
documentation
```

Ajouter :
- `background-tasks` si traitement lourd.

---

## 18. API

```text
project-workflow
feature-design si contrat métier nouveau
django-api
django-security
django-testing
django-performance si liste/requêtes
documentation
```

Ajouter :
- `django-auth` si auth ;
- `privacy-rgpd` si données perso ;
- `external-integrations` si proxy/tiers.

---

## 19. Frontend Django

```text
project-workflow
frontend-django
accessibility
```

Ajouter :
- `tailwind-css`
- `javascript`
- `htmx`
- `alpine-js`

uniquement selon la stack réellement utilisée.

---

## 20. Tailwind

Charge `tailwind-css` seulement si Tailwind est installé.

Ne propose pas Tailwind dans un projet Bootstrap/CSS classique sans demande.

---

## 21. JavaScript

Charge `javascript` si une interaction client est réellement nécessaire.

Ne charge pas React/Vue puisqu’ils ne font pas partie du socle actuel.

---

## 22. HTMX

Charge `htmx` seulement si le projet utilise HTMX ou si l’utilisateur demande explicitement de l’introduire.

Ne l’ajoute pas automatiquement à toutes les interactions dynamiques.

---

## 23. Alpine

Même règle pour `alpine-js`.

---

## 24. Admin

```text
project-workflow
django-admin
django-security
django-performance si listes/recherches
privacy-rgpd si PII
django-testing
```

---

## 25. Email

```text
project-workflow
django-email
django-security
django-testing
```

Ajouter :
- `privacy-rgpd` pour marketing ;
- `background-tasks` si volume/latence.

---

## 26. Cache

```text
project-workflow
django-cache
django-performance
django-testing
```

Ajouter `django-security` si données privées.

---

## 27. Background tasks

```text
project-workflow
background-tasks
django-database
django-testing
operations
```

Ajouter :
- `external-integrations` si appels tiers ;
- `django-email` si emails ;
- `audit-logging` si critique.

---

## 28. Recherche

```text
project-workflow
feature-design si nouveau comportement
search
django-database
django-performance
django-testing
```

Ajouter :
- `frontend-django`
- `javascript`
- `htmx`
selon UX.

---

## 29. SEO

```text
project-workflow
seo
frontend-django
documentation
```

Ajouter `privacy-rgpd` si tracking/analytics.

---

## 30. i18n

```text
project-workflow
django-i18n
frontend-django
django-testing
documentation
```

---

## 31. Import / Export

```text
project-workflow
feature-design
data-import-export
django-database
django-security
django-testing
```

Ajouter :
- `privacy-rgpd` si données perso ;
- `background-tasks` si gros volume ;
- `audit-logging` si export sensible.

---

## 32. Intégration externe

```text
project-workflow
feature-design si nouveau flux
external-integrations
django-security
django-testing
```

Ajouter :
- `background-tasks`
- `privacy-rgpd`
- `audit-logging`
selon contexte.

---

## 33. Commande management

```text
project-workflow
django-management-commands
django-testing
```

Ajouter :
- `django-database`
- `data-import-export`
- `operations`
selon l’usage.

---

## 34. Signals

```text
project-workflow
django-signals
django-architecture
django-testing
```

Si le signal porte une logique métier essentielle, proposer plutôt un service explicite.

---

## 35. Déploiement

```text
project-workflow
deployment
git-quality
django-security
backup-restore si DB risque
operations
documentation
```

Ajouter `ci-cd` si pipeline.

---

## 36. CI/CD

```text
project-workflow
ci-cd
git-quality
dependency-management
django-testing
django-security
deployment
```

---

## 37. Backup

```text
project-workflow
backup-restore
deployment
operations
django-security
documentation
```

---

## 38. Bug

Pour un bug localisé :

```text
project-workflow
skill technique concerné
django-testing
```

Puis :
- reproduire ;
- test de régression si valeur ;
- corriger ;
- docs/changelog seulement si pertinent.

Ne lancer pas `feature-design` systématiquement.

---

## 39. Refactor

Pour refactor interne :

```text
project-workflow
django-architecture
django-testing
```

Ajouter performance/security seulement si impact.

Le comportement doit rester identique sauf décision explicite.

---

## 40. Taille du contexte

Objectif :

- 2 à 5 skills spécialisés par défaut ;
- quelques transversaux si impact ;
- éviter 15 skills simultanés.

Si une feature est large, charger les skills par phase.

---

## 41. Chargement par phase

Exemple :

### Phase cadrage
```text
project-workflow
feature-design
django-architecture
```

### Phase backend
```text
django-database
django-security
django-testing
```

### Phase frontend
```text
frontend-django
tailwind-css
javascript
accessibility
```

### Phase finition
```text
documentation
git-quality
```

---

## 42. Questions utilisateur

Le router ne doit pas lui-même poser 20 questions.

S’il faut cadrer :

charge `feature-design`.

Maximum deux questions à la fois reste la règle globale.

---

## 43. Choix technique

Pour les choix purement techniques :

- utiliser les conventions du projet ;
- proposer une recommandation ;
- ne demander l’utilisateur que si cela modifie réellement son produit, son coût, son infrastructure ou son workflow.

---

## 44. Refus d’une solution

Si un skill spécialisé indique qu’une solution est mauvaise :

1. présenter le problème ;
2. proposer la meilleure alternative ;
3. laisser l’utilisateur forcer si cela reste acceptable.

Pour sécurité critique, appliquer les règles bloquantes.

---

## 45. TDD

`django-testing` doit être chargé pour toute feature dont les règles importantes nécessitent protection.

Pas nécessaire pour un simple changement documentaire.

---

## 46. Documentation

Charge `documentation` automatiquement si :

- feature importante ;
- architecture ;
- modèle ;
- workflow ;
- config ;
- dépendance structurante ;
- déploiement ;
- comportement utilisateur notable.

Pas pour un typo interne.

---

## 47. Git

`git-quality` intervient :

- avant commit si demandé ;
- avant push ;
- à la fin d’une feature significative pour quality gates.

Il ne commit/push jamais sans demande explicite.

---

## 48. Definition of Ready

Avant code d’une feature structurante :

- objectif compris ;
- questions critiques résolues ;
- architecture proposée ;
- impacts identifiés ;
- tâches prêtes.

---

## 49. Definition of Done

À la fin :

- comportement terminé ;
- tests pertinents verts ;
- sécurité analysée ;
- performance analysée si pertinente ;
- privacy/accessibility si pertinentes ;
- documentation ;
- changelog/tâches ;
- relecture second développeur ;
- quality gates.

---

## 50. Exemple 1

Demande :

> Ajoute un formulaire pour créer un vaisseau avec son constructeur.

Skills :

```text
project-workflow
feature-design
django-architecture
django-database
django-forms
frontend-django
accessibility
django-testing
documentation
```

`django-security` si permissions/utilisateurs.

---

## 51. Exemple 2

Demande :

> Le bouton est trop petit sur mobile.

Skills :

```text
frontend-django
tailwind-css
accessibility
```

Pas de `feature-design`, database, auth, deployment.

---

## 52. Exemple 3

Demande :

> Ajoute un import CSV de 200 000 produits.

Skills :

```text
project-workflow
feature-design
data-import-export
django-database
django-performance
background-tasks
django-security
django-testing
documentation
```

---

## 53. Exemple 4

Demande :

> Envoie un email après inscription.

Skills :

```text
project-workflow
feature-design si le flux n'est pas défini
django-auth
django-email
django-security
django-testing
```

---

## 54. Exemple 5

Demande :

> Fais un git push.

Skills :

```text
git-quality
dependency-management
django-testing
django-security
```

Puis quality gates.

Ne charge pas feature-design.

---

## 55. Exemple 6

Demande :

> Ajoute une recherche instantanée.

Skills possibles :

```text
project-workflow
feature-design
search
django-performance
frontend-django
javascript
accessibility
django-testing
```

Si HTMX est la stack existante :

remplacer une partie JS custom par `htmx`.

---

## 56. Exemple 7

Demande :

> Ajoute un paiement via API X.

Skills :

```text
project-workflow
feature-design
external-integrations
django-security
django-database
django-testing
audit-logging
privacy-rgpd si données perso
background-tasks si webhooks/retries
```

---

## 57. Exemple 8

Demande :

> Mets le site en production sur mon mini-PC.

Skills :

```text
deployment
django-security
backup-restore
operations
git-quality
documentation
```

Ajouter `ci-cd` uniquement si pipeline souhaité.

---

## 58. Évolution du routeur

Quand un nouveau skill est ajouté :

- ajouter ses critères ;
- définir ses interactions ;
- vérifier les conflits ;
- mettre à jour `AGENTS.md`.

---

## 59. Anti-pattern

Interdit :

```text
Je charge tous les skills pour être sûr.
```

Cela réduit la qualité du raisonnement et augmente les contradictions.

---

## 60. Principe final

Le routeur est un chef d’orchestre, pas un développeur universel.

Il doit faire intervenir le bon spécialiste au bon moment, avec juste assez de contexte pour résoudre correctement la demande.
