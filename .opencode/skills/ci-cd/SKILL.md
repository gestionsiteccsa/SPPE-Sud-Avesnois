---
name: ci-cd
description: Conçoit, documente et maintient une CI/CD sûre pour un projet Django. À utiliser pour pipelines de lint, tests, checks Django, migrations, audits sécurité, build, artefacts, staging et production. Réutilise les mêmes commandes que le workflow local, privilégie les sources officielles, isole les secrets, utilise PostgreSQL lorsque pertinent, bloque la livraison sur les échecs critiques et n’automatise pas un déploiement production dangereux.
compatibility: opencode
metadata:
  framework: django
  purpose: ci-cd
  language: fr
  workflow-parent: project-workflow
---

# CI/CD Django

## 1. Mission

Tu es responsable de l’automatisation fiable des contrôles et livraisons du projet.

Ton objectif est que chaque changement puisse être :

- vérifié ;
- testé ;
- construit ;
- livré ;
- audité ;
- reproduit.

La CI/CD doit refléter le workflow local.

Elle ne doit pas être une deuxième logique différente.

---

## 2. Coordination

Avant création/modification d’un pipeline :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. charge :
   - `git-quality`
   - `django-testing`
   - `django-security`
   - `django-database`
   - `dependency-management`
   - `deployment`
4. charge `backup-restore` si production/migrations sensibles ;
5. inspecte le fournisseur CI réellement utilisé.

Ne suppose pas GitHub Actions si le projet utilise GitLab CI, Forgejo, Gitea ou autre.

---

## 3. Principe de parité

Les commandes CI doivent être les mêmes que celles qu’un développeur peut lancer localement autant que possible.

Exemples :

```text
lint
format-check
test
django-check
migration-check
security-audit
```

Évite les scripts CI qui n’existent nulle part ailleurs.

---

## 4. Questions

Pose au maximum 2 questions si le fournisseur ou la stratégie de déploiement ne peut pas être déduite.

Exemples :

- Le dépôt est-il hébergé sur GitHub, GitLab ou ailleurs ?
- Veux-tu que la production soit déployée automatiquement après validation, ou déclenchée manuellement ?

Explique pourquoi le choix change la sécurité du pipeline.

---

## 5. Étapes CI minimales

Pour un projet Django standard, la CI doit généralement vérifier :

1. checkout ;
2. runtime Python ;
3. dépendances ;
4. lint ;
5. format check ;
6. Django check ;
7. migrations ;
8. tests ;
9. sécurité/dépendances selon configuration.

---

## 6. PostgreSQL en CI

Si la production utilise PostgreSQL et que le projet dépend de son comportement :

utilise PostgreSQL dans la CI pour les tests importants.

Ne valide pas uniquement avec SQLite si cela peut masquer :

- contraintes ;
- types ;
- locks ;
- requêtes spécifiques ;
- extensions.

---

## 7. Version PostgreSQL

La version CI doit être cohérente avec staging/production autant que possible.

Ne teste pas sur une version arbitrairement très différente.

---

## 8. Python

Épingle une version cohérente avec le projet.

Si une matrice de compatibilité est réellement utile, ajoute-la.

Une application interne n’a pas besoin de tester dix versions Python.

---

## 9. Django

Pour une application, teste la version réellement verrouillée.

Ne teste pas automatiquement plusieurs versions Django comme une bibliothèque générique sauf besoin.

---

## 10. Installation propre

La CI doit partir d’un environnement propre.

Cela détecte :

- dépendance non déclarée ;
- fichier local manquant ;
- cache trompeur ;
- configuration implicite.

---

## 11. Cache CI

Le cache peut accélérer :

- packages ;
- outils ;
- build.

Mais il ne doit pas compromettre la reproductibilité.

Clé de cache basée sur les fichiers de dépendances lorsque pertinent.

---

## 12. Ruff

Exécute la commande réelle du projet.

Exemples :

```bash
ruff check .
ruff format --check .
```

Ne modifie pas automatiquement le code dans la CI principale.

La CI vérifie ; le développeur corrige.

---

## 13. Type checking

Si configuré :

exécute le type checker.

Ne l’ajoute pas automatiquement uniquement parce qu’une CI existe.

---

## 14. Django check

Exécute :

```bash
python manage.py check
```

ou équivalent avec les settings de test.

Toute erreur bloque.

---

## 15. Migration check

Exécute :

```bash
python manage.py makemigrations --check --dry-run
```

afin de détecter des changements de modèle non migrés.

---

## 16. Application migrations

Sur la DB CI propre :

```bash
python manage.py migrate
```

permet aussi de vérifier que l’historique est applicable.

---

## 17. Tests

Exécute la suite adaptée.

Si suite longue :

- tests rapides PR ;
- suite complète branche principale/release ;
- tests lents séparés.

Ne retire pas les tests critiques pour accélérer.

---

## 18. Parallelisation

Parallélise seulement si :

- suite assez grande ;
- tests isolés ;
- DB supporte ;
- gain réel.

Ne crée pas de complexité pour 30 secondes.

---

## 19. Coverage

Si coverage configurée :

publie éventuellement un rapport.

Ne fait pas du 100 % une condition universelle.

---

## 20. Tests de migration

Les migrations risquées peuvent avoir des jobs dédiés.

Ne les exécute pas uniquement sur une DB SQLite simplifiée.

---

## 21. Security audit

Selon outils choisis :

- dependency audit ;
- secret scan ;
- static analysis ;
- Django deploy checks selon stage.

La CI complète mais ne remplace pas la revue `django-security`.

---

## 22. Secret scanning

Scanne :

- commit ;
- diff ;
- dépôt selon outil.

Un secret réel bloque immédiatement.

---

## 23. Secrets CI

Utilise le store de secrets du fournisseur.

Jamais :

- dans YAML ;
- dans Dockerfile ;
- dans logs ;
- dans artifact.

---

## 24. Principe secrets

Les secrets CI doivent être :

- minimaux ;
- scoped ;
- séparés par environnement ;
- rotatables.

Le job de test n’a pas besoin des credentials production.

---

## 25. Pull requests

Une PR doit pouvoir être testée sans donner accès aux secrets production.

Attention aux workflows provenant de forks.

---

## 26. Environments

Sépare au minimum lorsque possible :

```text
test
staging
production
```

Avec secrets et protections distincts.

---

## 27. Staging

Staging peut être déployé automatiquement depuis :

- branche principale ;
- tag ;
- branche dédiée ;

selon workflow.

Le choix doit être documenté.

---

## 28. Production

La production ne doit pas être déployée automatiquement depuis n’importe quelle branche.

Définis une source de release explicite.

---

## 29. Déploiement manuel

Pour un projet sensible ou petit serveur maison, un job production déclenché manuellement peut être le meilleur compromis.

Il permet :

- contrôle ;
- simplicité ;
- logs ;
- reproductibilité.

---

## 30. Approval

Si la plateforme supporte les environnements protégés, exige une approbation pour production lorsque pertinent.

---

## 31. Production automatique

Un déploiement automatique après merge peut être acceptable si :

- tests robustes ;
- migrations sûres ;
- rollback ;
- monitoring ;
- équipe habituée.

Ne l’impose pas au départ.

---

## 32. Build once

Stratégie mature :

> construire une fois, promouvoir le même artefact.

Exemple :

- image Docker construite en CI ;
- testée ;
- déployée en staging ;
- même digest promu en prod.

Cela réduit les différences.

---

## 33. Build sur serveur

Pour petit projet, le serveur peut construire/installler.

C’est acceptable si :

- procédure reproductible ;
- versions verrouillées ;
- logs ;
- rollback.

---

## 34. Artefacts

Artefacts possibles :

- package ;
- image ;
- coverage ;
- rapports de tests ;
- SBOM si utilisé.

Ne publie pas d’artefacts sensibles.

---

## 35. Docker build

Si Docker :

- build ;
- scan si outil choisi ;
- tag immutable ;
- pas de secret ;
- user non-root ;
- tests.

---

## 36. Tags Docker

Utilise au moins une référence identifiable :

- commit SHA ;
- version ;
- tag release.

`latest` peut exister mais ne doit pas être la seule référence.

---

## 37. Registry

Les credentials registry sont des secrets.

Scopes minimaux :

- push pour job build ;
- pull pour serveur.

---

## 38. Deploy sans Docker

Pipeline peut :

- transférer artefact ;
- SSH contrôlé ;
- exécuter script versionné ;
- restart systemd.

Ne colle pas 100 commandes shell inline si un script de déploiement versionné est plus lisible.

---

## 39. SSH

Clé CI dédiée.

Pas de clé personnelle de développeur.

Permissions limitées.

---

## 40. Host key

Ne désactive pas aveuglément la vérification SSH host key.

Utilise `known_hosts` ou mécanisme sécurisé.

---

## 41. Deploy user

Utilisateur de déploiement dédié avec permissions minimales.

Il ne doit pas devenir root permanent sans nécessité.

---

## 42. Sudo

Si sudo est nécessaire :

autorise uniquement les commandes requises lorsque possible.

Exemple :

- restart du service ciblé.

---

## 43. Migrations production

Les migrations sont une étape explicite.

Ne lance pas des migrations destructrices automatiquement sans plan.

---

## 44. Analyse migration

Avant production :

- migration check ;
- revue ;
- staging ;
- backup si risque ;
- compatibilité rollback.

---

## 45. Backup gate

Pour une release avec migration risquée :

vérifie la présence d’un backup récent ou déclenche un backup contrôlé selon le workflow.

---

## 46. Collectstatic

Intègre `collectstatic` selon le mode de déploiement.

Ordre exact dépend de l’architecture.

---

## 47. Restart

Après installation :

- restart/reload ;
- état service ;
- logs ;
- health check.

---

## 48. Health check

Le pipeline ne doit pas considérer la commande de déploiement comme preuve de succès.

Il doit vérifier le service.

---

## 49. Smoke tests

Après staging/prod :

- page principale ;
- endpoint santé ;
- connexion DB ;
- feature critique simple.

Ne fais pas un E2E de 30 minutes comme unique health check.

---

## 50. Rollback

Le pipeline doit documenter ou fournir un mécanisme de rollback.

Il doit savoir quelle release précédente est restaurable.

---

## 51. Rollback automatique

Un rollback automatique peut être dangereux si la DB a migré.

Ne l’active pas sans stratégie claire.

---

## 52. Rollback manuel

Pour un premier projet, un rollback manuel guidé peut être plus sûr.

---

## 53. Déploiement atomique

Si possible, évite une copie progressive de fichiers servis en direct.

Utilise :

- image ;
- release directory ;
- symlink ;
- mécanisme plateforme.

---

## 54. Concurrence de déploiement

Empêche deux déploiements production simultanés.

Utilise les mécanismes de concurrency/lock du fournisseur.

---

## 55. Annulation

Si un nouveau commit arrive, tu peux annuler un déploiement staging obsolète.

Pour production, ne tue pas brutalement une migration en cours.

---

## 56. Timeout CI

Chaque job doit avoir un timeout raisonnable.

Évite les jobs bloqués indéfiniment.

---

## 57. Retry

Ne retry pas automatiquement un test logique rouge.

Retry peut être approprié pour :

- téléchargement réseau ;
- service temporairement indisponible ;

avec limite.

---

## 58. Flaky

Un retry automatique massif masque les flaky tests.

Charge `django-testing`.

---

## 59. Logs CI

Les logs doivent être suffisants pour comprendre l’échec.

Masque les secrets.

---

## 60. Debug CI

N’active pas un shell distant/debug interactif sur un job contenant des secrets production sans contrôle.

---

## 61. Notifications

Notifie surtout :

- pipeline main cassé ;
- staging/prod échoué ;
- sécurité ;
- déploiement prod réussi/échoué selon besoin.

Évite le bruit sur chaque job vert.

---

## 62. Branch protection

Si la plateforme supporte :

- checks obligatoires ;
- PR review ;
- protection main ;
- interdiction force push.

Recommandé pour projets collaboratifs/importants.

---

## 63. Solo project

Même seul, protéger main peut éviter des erreurs, mais ne crée pas de lourdeur excessive.

---

## 64. Required checks

Les checks bloquants doivent correspondre aux quality gates critiques :

- lint ;
- tests ;
- migrations ;
- sécurité essentielle.

---

## 65. Docs

Si MkDocs :

un job peut exécuter :

```bash
mkdocs build --strict
```

si le projet l’a configuré.

---

## 66. Deploy docs

La documentation peut être publiée séparément.

Ne publie pas de documentation interne contenant des informations sensibles sur un site public.

---

## 67. Frontend build

Si Node/Tailwind/build :

- installer lock ;
- build ;
- tests ;
- artefacts.

Ne laisse pas la prod télécharger des versions différentes à chaque build.

---

## 68. npm

Utilise installation reproductible adaptée au lockfile, par exemple `npm ci` lorsque npm est le gestionnaire retenu.

---

## 69. Python install

Utilise la commande officielle du projet.

N’utilise pas un `pip install` improvisé si uv/Poetry/pip-tools est retenu.

---

## 70. Matrix

Une matrix est utile pour une bibliothèque.

Pour une app Django, elle est souvent inutile au-delà des services réellement déployés.

---

## 71. Services CI

Les services peuvent inclure :

- PostgreSQL ;
- Redis si réellement utilisé.

Ne démarre pas des services inutiles.

---

## 72. Fixtures CI

Les tests créent leurs propres données.

Ne branche jamais la CI de test sur la DB staging/prod.

---

## 73. Emails

Les tests CI n’envoient pas de vrais emails.

---

## 74. External APIs

Mock/fake/sandbox.

Aucun test PR ne doit déclencher paiement/SMS réel.

---

## 75. Scheduled CI

Un job planifié peut périodiquement vérifier :

- dépendances ;
- sécurité ;
- tests complets ;
- restauration test selon infrastructure.

Ne duplique pas une automation externe si inutile.

---

## 76. Dependency updates

Les bots peuvent ouvrir des PR.

Chaque PR suit les mêmes tests.

Ne merge pas automatiquement les majors.

---

## 77. Security patches

Pour patch critique :

pipeline accéléré possible, mais toujours tests minimaux essentiels.

Urgence ne signifie pas aucun test.

---

## 78. SBOM

Optionnel pour maturité/exigences.

Génère depuis l’artefact réel.

Ne l’impose pas à tous les projets.

---

## 79. Provenance

Pour projets à exigences fortes, signing/provenance des artefacts peut être ajouté.

Pas nécessaire au socle minimal.

---

## 80. Actions/plugins tiers

Les actions CI sont des dépendances.

Privilégie sources maintenues/officielles.

Épingle versions de manière sûre.

---

## 81. Pin par SHA

Pour environnement à forte exigence, épingler une action tierce à un commit SHA réduit certains risques supply-chain.

Conserve une méthode de mise à jour.

---

## 82. Permissions pipeline

Sur plateformes supportant permissions de token :

accorde uniquement ce qui est nécessaire.

Un job de test en lecture ne doit pas avoir droit de déployer.

---

## 83. OIDC cloud

Pour cloud supportant OIDC, préfère des credentials temporaires à une clé cloud longue durée si l’architecture le permet.

---

## 84. Secrets environnement

Production doit avoir ses propres secrets.

Ne réutilise pas ceux de staging.

---

## 85. Environment URL

Si plateforme le permet, expose l’URL staging/prod dans le résumé de déploiement.

Pas de token dans URL.

---

## 86. Changelog release

Une release peut générer/préparer des notes depuis `CHANGELOG.md`.

Le changelog reste source humaine validée.

---

## 87. Tags Git

Ne crée un tag/release que si le workflow le prévoit.

Ne tag pas automatiquement chaque merge.

---

## 88. Versioning

Si version applicative :

injecte-la dans l’artefact/logs de façon reproductible.

Exemple : tag/commit.

---

## 89. Migrations sans downtime

Pour une prod active, coordonne expand/contract si nécessaire.

Le CI/CD ne peut pas rendre automatiquement une migration incompatible sûre.

---

## 90. Feature flags

Un pipeline peut déployer code désactivé derrière flag pour réduire le risque.

Seulement si le projet utilise réellement les flags.

---

## 91. Maintenance window

Pour migration lourde, le pipeline doit permettre un déploiement manuel en fenêtre de maintenance.

---

## 92. Production database clone

Ne clone pas automatiquement la prod vers CI.

Données personnelles interdites par défaut.

---

## 93. Staging refresh

Si besoin de données réalistes :

anonymisation + procédure contrôlée.

Charge `privacy-rgpd`.

---

## 94. Incident pipeline

Si production deploy échoue :

- arrêter les étapes suivantes ;
- préserver logs ;
- vérifier état ;
- ne pas relancer aveuglément ;
- rollback selon plan.

---

## 95. Pipeline cassé

Ne contourne pas durablement un check obligatoire.

Corrige la cause ou documente une exception temporaire.

---

## 96. CI as code

Versionne les fichiers pipeline.

Toute modification de CI est une modification de code sensible.

---

## 97. Review CI

Une modification donnant plus de permissions/secrets doit être revue attentivement.

---

## 98. Documentation

Maintiens :

```text
docs/operations/ci-cd.md
```

avec :

- triggers ;
- jobs ;
- secrets ;
- staging ;
- production ;
- rollback ;
- dépannage.

---

## 99. AGENTS

Documente les commandes locales équivalentes aux jobs CI.

---

## 100. Definition of Done CI

Une CI est prête lorsque :

- install propre ;
- lint ;
- format check ;
- Django check ;
- migration check ;
- migrations applicables ;
- tests ;
- PostgreSQL si pertinent ;
- sécurité ;
- secrets protégés ;
- logs lisibles ;
- triggers corrects ;
- documentation.

---

## 101. Definition of Done CD

Une CD est prête lorsque :

- source release explicite ;
- staging validé ;
- secrets séparés ;
- migration strategy ;
- backup gate si risque ;
- artefact identifiable ;
- concurrency contrôlée ;
- health check ;
- smoke tests ;
- rollback ;
- logs ;
- production protégée.

---

## 102. Principe final

La CI/CD ne doit pas automatiser aveuglément.

Elle doit automatiser une procédure déjà sûre, reproductible et comprise.

Automatiser une mauvaise procédure ne la rend pas meilleure : cela permet seulement de faire l’erreur plus vite.
