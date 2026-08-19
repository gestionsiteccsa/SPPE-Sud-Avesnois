---
name: git-quality
description: Pilote la qualité Git et les quality gates d’un projet Django/Python. À utiliser pour pre-commit, lint, formatage, détection de secrets, vérifications Django, migrations, dépendances, préparation de commit et contrôle pré-push. Ne crée jamais de commit ni de push sans demande explicite de l’utilisateur et bloque le push lorsqu’un contrôle critique échoue.
compatibility: opencode
metadata:
  framework: django
  purpose: git-quality-gates
  language: fr
  workflow-parent: project-workflow
---

# Git Quality

## 1. Mission

Tu es responsable de la qualité du dépôt avant commit et push.

Ton objectif est de garantir que le code versionné est :

- formaté ;
- lisible ;
- testable ;
- cohérent ;
- sans secret connu ;
- compatible avec les migrations ;
- conforme aux checks Django ;
- sans vulnérabilité critique connue dans les dépendances ;
- documenté lorsque nécessaire.

Tu ne dois pas créer une bureaucratie qui ralentit inutilement le développement.

---

## 2. Règle Git fondamentale

Ne fais jamais automatiquement :

- `git commit`
- `git push`
- `git rebase`
- `git reset --hard`
- suppression de branche
- force push

sans demande explicite de l’utilisateur.

Tu peux préparer, analyser, corriger et proposer.

---

## 3. Coordination

Avant les quality gates :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. charge si disponibles :
   - `django-testing`
   - `django-security`
   - `django-database`
   - `dependency-management`
   - `documentation`
4. inspecte les outils déjà configurés.

Ne remplace pas un outillage existant sain uniquement pour appliquer une préférence personnelle.

---

## 4. Deux niveaux de contrôle

Sépare :

### Pre-commit

Contrôles rapides.

### Pre-push

Contrôles plus complets.

Le développeur doit pouvoir committer sans attendre plusieurs minutes.

---

## 5. Pre-commit

Le pre-commit doit prioritairement couvrir :

- formatage ;
- lint ;
- syntaxe ;
- whitespace ;
- TOML/YAML/JSON ;
- secrets ;
- gros fichiers accidentels ;
- erreurs simples.

Les tests longs appartiennent au pre-push ou à la CI.

---

## 6. Ruff

Pour Python moderne, Ruff est la valeur par défaut recommandée si aucun outil équivalent n’est déjà imposé.

Il peut couvrir :

- lint ;
- imports ;
- formatage ;
- règles Python.

Évite de cumuler Ruff, Flake8, isort, Black et plusieurs outils qui font la même chose sans besoin.

---

## 7. Ruff lint

Commande typique :

```bash
ruff check .
```

Pour correction automatique :

```bash
ruff check --fix .
```

Ne lance pas `--fix` aveuglément sur un gros changement sans relire le diff.

---

## 8. Ruff format

Commande typique :

```bash
ruff format --check .
```

Pour appliquer :

```bash
ruff format .
```

Le formatage automatique est généralement non controversé, mais relis les changements.

---

## 9. Ordre Ruff + formatter

Si Ruff applique des fixes automatiques, fais généralement :

1. lint/fix ;
2. format.

Cela évite qu’un fix nécessite ensuite un reformatage.

---

## 10. Configuration centralisée

Privilégie `pyproject.toml` lorsque le projet l’utilise déjà.

Évite plusieurs fichiers de configuration contradictoires.

Documente les règles importantes.

---

## 11. Niveau de lint

Active des règles utiles sans transformer le lint en bruit permanent.

Priorité :

- erreurs réelles ;
- imports ;
- code mort ;
- bugs probables ;
- mauvaises pratiques claires.

Les règles purement stylistiques doivent rester raisonnables.

---

## 12. Warnings

Un warning doit être :

- corrigé ;
- ou explicitement ignoré avec justification.

Évite les fichiers contenant de nombreuses suppressions globales.

---

## 13. `noqa`

Un `# noqa` doit être ciblé.

Préfère :

```python
# noqa: F401
```

à une suppression globale sans explication.

Si beaucoup de `noqa` apparaissent, analyse la configuration.

---

## 14. Type checking

Si le projet utilise mypy, pyright ou autre :

intègre-le au quality gate approprié.

Ne rends pas obligatoire un type checker dans un projet existant non préparé sans plan progressif.

---

## 15. Django check

Exécute :

```bash
python manage.py check
```

dans les contrôles courants.

Toute erreur doit bloquer la sortie.

---

## 16. Django deploy check

Avant production ou push vers une branche de release si le workflow le prévoit :

```bash
python manage.py check --deploy --settings=config.settings.prod
```

Adapte le chemin de settings.

Ne l’exécute pas avec de vrais secrets affichés dans les logs.

---

## 17. Migrations non créées

Vérifie les changements de modèles sans migration :

```bash
python manage.py makemigrations --check --dry-run
```

Un échec signifie généralement qu’un modèle a changé sans migration correspondante.

Cela bloque le push si la modification doit être versionnée.

---

## 18. Migrations appliquées

Ne confonds pas :

- migration créée ;
- migration appliquée localement ;
- migration appliquée en staging/prod.

Le dépôt versionne les migrations.

Le déploiement les applique.

---

## 19. Relire les migrations

Toute migration générée doit être relue.

Cherche :

- suppression involontaire ;
- rename mal détecté ;
- default dangereux ;
- contrainte lourde ;
- migration de données incorrecte.

Charge `django-database`.

---

## 20. Conflits de migrations

Si deux branches créent des migrations concurrentes :

analyse avant de créer une merge migration.

Ne génère pas automatiquement une migration de merge sans comprendre les dépendances.

---

## 21. Tests

Au pre-push, exécute la suite adaptée au projet.

Ordre possible :

1. tests ciblés de la feature ;
2. suite complète si temps raisonnable ;
3. tests lents/CI selon workflow.

Ne dis jamais « tous les tests passent » si seule une partie a été exécutée.

---

## 22. Tests rouges

Un test critique rouge bloque le push.

Ne contourne pas un test simplement pour pousser.

Distingue :

- test réellement cassé ;
- test obsolète ;
- comportement produit modifié.

---

## 23. Tests flaky

Un test intermittent doit être traité comme un problème.

Ne relance pas jusqu’à obtenir vert puis pousse sans analyse.

Si un contournement temporaire est nécessaire :

- documente ;
- ajoute tâche ;
- évalue le risque.

---

## 24. Coverage

La couverture peut être contrôlée si configurée.

Ne bloque pas un push uniquement parce qu’un seuil arbitraire élevé n’est pas atteint, sauf règle explicite du projet.

La qualité des tests prime.

---

## 25. Secret scanning

Avant push, analyse les changements pour détecter :

- clés API ;
- tokens ;
- passwords ;
- clés privées ;
- credentials cloud ;
- secrets Django.

Le scanner peut produire des faux positifs.

Analyse avant de contourner.

---

## 26. Secret critique

Si un secret réel est détecté :

- bloque le push ;
- retire le secret ;
- considère-le compromis s’il a déjà été committé ;
- recommande rotation/révocation ;
- inspecte l’historique si nécessaire.

Ne se contente pas de l’ajouter au `.gitignore`.

---

## 27. `.env`

Vérifie :

- `.env` non suivi ;
- `.env.example` suivi ;
- aucune vraie valeur sensible dans l’exemple.

Commande utile :

```bash
git ls-files
```

et inspection ciblée.

---

## 28. `.gitignore`

Audite les exclusions importantes :

- `.env`
- environnements virtuels ;
- caches ;
- media ;
- logs ;
- IDE ;
- builds ;
- coverage ;
- secrets locaux.

N’ignore pas les migrations.

---

## 29. Fichiers volumineux

Bloque ou avertis avant commit si un gros fichier inattendu apparaît :

- dump DB ;
- vidéo ;
- archive ;
- dataset ;
- binaire ;
- model ML.

Détermine s’il doit utiliser Git LFS ou être exclu.

---

## 30. Fichiers générés

Ne versionne pas automatiquement :

- caches ;
- coverage HTML ;
- build temporaire ;
- logs ;
- fichiers runtime.

Versionne uniquement les artefacts nécessaires.

---

## 31. Dépendances

Avant push :

- vérifier nouvelles dépendances ;
- vérifier vulnérabilités connues critiques ;
- vérifier incohérences ;
- vérifier lockfile si présent.

Ne mets pas automatiquement toutes les dépendances à jour.

---

## 32. Update dépendances

Une mise à jour de dépendance doit être une opération consciente.

Après update :

- lint ;
- tests ;
- checks ;
- migration éventuelle ;
- revue changelog upstream si update significative.

---

## 33. Vulnérabilité critique

Si une dépendance contient une vulnérabilité critique exploitable dans le contexte :

- bloque le push ;
- propose version corrigée ou mitigation ;
- documente.

Si non exploitable, explique pourquoi et ajoute éventuellement une tâche.

---

## 34. Lockfile

Si le gestionnaire crée un lockfile :

- versionne-le pour une application déployée ;
- vérifie qu’il correspond aux déclarations.

Ne modifie pas manuellement un lockfile.

---

## 35. Licences

Pour une nouvelle dépendance structurante, vérifier la licence si pertinent.

Une incompatibilité légale sérieuse peut bloquer l’ajout.

---

## 36. Changelog

Avant push, vérifie si le changement significatif nécessite `CHANGELOG.md`.

Ne bloque pas pour un typo interne.

Bloque ou demande correction si une feature importante est documentée comme terminée mais absente du changelog exigé.

---

## 37. PROJECT_TASKS

Vérifie que la feature terminée a son état mis à jour.

Ne force pas une tâche en « Terminé » si la Definition of Done échoue.

---

## 38. Documentation

Pour une feature impactant le comportement :

vérifie la documentation pertinente.

Ne génère pas des changements de docs artificiels.

---

## 39. README

Mets à jour uniquement si :

- installation ;
- config ;
- commandes ;
- dépendances ;
- environnement ;
- workflow ;

ont changé.

---

## 40. Git status

Avant commit/push :

```bash
git status --short
```

Analyse :

- fichiers inattendus ;
- secrets ;
- artefacts ;
- suppressions.

Ne pousse pas un fichier simplement parce qu’il est déjà staged.

---

## 41. Diff

Avant commit/push important :

```bash
git diff
git diff --staged
```

Relis le diff.

Cherche :

- debug ;
- TODO critique ;
- secret ;
- print ;
- code mort ;
- modification accidentelle.

---

## 42. Debug code

Cherche selon stack :

- `print()`
- `breakpoint()`
- `pdb`
- debug toolbar en prod ;
- logs verbeux temporaires.

Un debug accidentel peut bloquer le push.

---

## 43. TODO

Tous les TODO ne sont pas bloquants.

Bloque si le TODO indique :

- sécurité incomplète ;
- validation absente ;
- migration temporaire ;
- comportement incorrect.

Sinon ajoute au suivi si pertinent.

---

## 44. Branches

Respecte la stratégie du projet.

Ne crée pas Git Flow par défaut.

Un projet peut fonctionner correctement avec :

- main + feature branches ;
- trunk-based ;
- autre convention.

Le workflow doit être simple.

---

## 45. Branch naming

Si convention souhaitée :

```text
feature/...
fix/...
refactor/...
```

Ne bloque pas techniquement un projet pour un nom de branche sauf règle explicite.

---

## 46. Commit

Un commit doit représenter une unité cohérente.

Évite :

- feature + refactor sans rapport ;
- dépendance update + changement métier massif ;
- secrets ;
- artefacts.

---

## 47. Commit automatique interdit

Même si tout est vert :

ne fais pas `git commit`.

Informe :

> Les contrôles passent. Le projet est prêt à être commité.

Puis attends la demande.

---

## 48. Message de commit

Tu peux proposer Conventional Commits si le projet adopte cette convention :

```text
feat: add ship manufacturer management
fix: prevent unauthorized profile edits
```

Ne l’impose pas si une convention existe déjà.

---

## 49. Commit amend

Ne fais pas `--amend` sans demande.

Cela réécrit l’historique.

Particulièrement sensible si commit déjà poussé.

---

## 50. Push

Un push doit toujours être explicite.

Quand l’utilisateur dit :

> pousse

commence par les contrôles pré-push.

Ne pousse pas immédiatement.

---

## 51. Pipeline pré-push recommandé

Selon projet :

1. `git status`
2. diff
3. secrets
4. Ruff lint
5. Ruff format check
6. type checking si configuré
7. Django check
8. migration check
9. tests
10. dependency/security audit
11. docs/tasks/changelog
12. second developer review si nécessaire

Puis seulement push.

---

## 52. Contrôles bloquants

Bloque le push en cas de :

- secret réel ;
- tests critiques rouges ;
- erreur lint bloquante ;
- erreur Django check ;
- migration manquante ;
- migration manifestement cassée ;
- vulnérabilité critique exploitable ;
- configuration prod dangereuse ;
- permission critique non corrigée ;
- code syntaxiquement invalide.

---

## 53. Contrôles non bloquants

Peuvent être warnings :

- package légèrement ancien ;
- règle de style mineure ;
- optimisation future ;
- doc secondaire ;
- dette technique faible.

Ne transforme pas chaque warning en blocage.

---

## 54. Forçage

Si l’utilisateur veut forcer malgré un warning :

autorisé.

Si risque critique :

explique fortement le risque.

Ne contourne jamais silencieusement les protections.

---

## 55. Push protection GitHub

Si GitHub push protection est activée :

considère son blocage comme sérieux.

Ne contourne pas un secret détecté sans vérifier qu’il s’agit d’un faux positif ou d’un secret explicitement sûr.

---

## 56. GitHub non obligatoire

Le workflow doit fonctionner même sans GitHub.

Les quality gates sont locaux.

GitHub Actions/Secret Scanning sont des couches supplémentaires.

---

## 57. CI

La CI doit idéalement répéter les contrôles critiques dans un environnement propre.

Ne considère pas pre-commit comme suffisant pour garantir la qualité.

---

## 58. Duplication local/CI

Les mêmes commandes doivent être réutilisables localement et en CI.

Évite deux pipelines divergents.

---

## 59. Makefile / task runner

Si le projet utilise un task runner :

centralise des commandes comme :

```text
lint
format
test
check
prepush
```

Ne crée pas un nouvel outil si des scripts existants suffisent.

---

## 60. Script quality

Un script pré-push peut centraliser les contrôles.

Il doit :

- échouer au premier problème critique ou résumer proprement ;
- retourner un code non zéro ;
- être documenté.

---

## 61. Hooks Git

Pre-commit peut gérer plusieurs stages.

N’utilise pas des hooks locaux non versionnés comme seule garantie.

La configuration doit être dans le dépôt.

---

## 62. Installation hooks

README doit indiquer comment installer les hooks.

Exemple :

```bash
pre-commit install
```

et si pré-push configuré :

```bash
pre-commit install --hook-type pre-push
```

Adapte à la configuration réelle.

---

## 63. Mise à jour hooks

Les hooks ont leurs propres versions.

Mets-les à jour consciemment.

Après update :

- exécute sur tous les fichiers ;
- relis les changements ;
- tests.

---

## 64. Pre-commit autoupdate

`pre-commit autoupdate` peut aider.

Ne l’exécute pas automatiquement avant chaque push.

---

## 65. Secrets faux positifs

Pour un faux positif :

- documente le motif ;
- utilise mécanisme d’allowlist ciblé ;
- ne désactive pas le scanner globalement.

---

## 66. Baseline secret scanner

Si l’outil utilise une baseline :

protège-la.

Une baseline ne doit pas devenir un moyen de cacher de nouveaux secrets.

---

## 67. Checks Python

Selon projet, peuvent inclure :

- compilation ;
- import checks ;
- package build ;
- dependency consistency.

Ne multiplie pas les checks redondants.

---

## 68. `python -m compileall`

Peut détecter certaines erreurs syntaxiques.

Si Ruff/pytest/imports couvrent déjà ce besoin, il n’est pas obligatoire.

---

## 69. Build package

Si le projet produit un package Python :

teste le build.

Pour une application Django classique non distribuée comme package, ce check peut être inutile.

---

## 70. Migrations dans CI

CI devrait exécuter au minimum :

```bash
python manage.py makemigrations --check --dry-run
```

et idéalement appliquer les migrations sur une DB de test propre.

Cela détecte des dépendances/migrations cassées.

---

## 71. PostgreSQL en CI

Si production = PostgreSQL et que des comportements DB spécifiques existent :

CI doit utiliser PostgreSQL pour les tests importants.

Ne valide pas uniquement sous SQLite.

---

## 72. Check production sans vrais secrets

Les settings prod doivent pouvoir être vérifiés avec des valeurs factices sûres.

Ne stocke pas de secrets réels dans CI uniquement pour `check --deploy`.

---

## 73. Variables CI

Utilise les mécanismes secrets du fournisseur CI.

Ne les imprime pas.

---

## 74. Artifacts CI

Ne publie pas :

- `.env`
- dumps DB ;
- logs sensibles ;
- fichiers media privés.

---

## 75. Dependency audit

Utilise l’outil adapté au gestionnaire de dépendances.

Le skill ne doit pas figer un scanner unique.

Critères :

- source fiable ;
- maintenance ;
- sortie exploitable ;
- intégration CI.

---

## 76. Security scanners

Les scanners statiques peuvent aider, mais ne remplacent pas `django-security`.

Un scanner qui ne trouve rien ne prouve pas l’absence de faille métier.

---

## 77. Bandit

Bandit peut être utilisé si le projet le choisit.

Ne l’ajoute pas automatiquement si d’autres outils couvrent déjà le besoin et que le coût dépasse la valeur.

---

## 78. Ruff security rules

Certaines règles Ruff peuvent détecter des patterns risqués.

Elles sont complémentaires.

Ne les traite pas comme audit sécurité complet.

---

## 79. Audit manuel

Le second developer review du `project-workflow` reste obligatoire pour les features importantes.

Les quality gates automatisés ne remplacent pas la compréhension.

---

## 80. Release branch

Si une branche de release existe :

les contrôles peuvent être plus stricts.

Exemple :

- suite complète ;
- deploy check ;
- dependency audit ;
- docs ;
- migration review.

Ne complexifie pas un projet sans release branches.

---

## 81. Tag

Ne crée pas de tag sans demande.

Un tag peut représenter une release.

---

## 82. Version

Si le projet suit SemVer ou autre :

respecte la convention.

Ne bump pas automatiquement la version à chaque push.

---

## 83. Changelog release

Pour une release, vérifie que les changements sont regroupés proprement.

Le changelog de développement peut avoir une section `Non publié`.

---

## 84. Nettoyage branche

Ne supprime pas automatiquement la branche après merge/push.

---

## 85. Force push

`git push --force` est dangereux.

Ne l’utilise jamais par défaut.

Si nécessaire et explicitement demandé, préfère `--force-with-lease` lorsque approprié.

Explique le risque.

---

## 86. Rebase

Ne rebase pas une branche partagée sans accord.

Un rebase local avant publication peut être acceptable si le workflow le prévoit.

---

## 87. Merge conflicts

Résous les conflits en comprenant les deux côtés.

Ne choisis pas systématiquement ours/theirs.

Après résolution :

- tests ;
- migrations ;
- docs ;
- lint.

---

## 88. Migrations + merge conflict

Une migration conflictuelle mérite une analyse spéciale.

Ne renumérote pas mécaniquement sans vérifier les dépendances.

---

## 89. Quality gate adaptatif

Le contrôle doit être proportionné.

Petite correction documentaire :

- pas besoin de lancer toute une suite E2E.

Feature auth :

- sécurité + permissions + tests complets pertinents.

---

## 90. Temps d’exécution

Si pre-push devient trop long :

- profiler ;
- séparer tests lents ;
- paralléliser ;
- déplacer certains checks vers CI.

Ne supprime pas un contrôle critique uniquement pour gagner du temps.

---

## 91. Échec clair

Chaque échec doit expliquer :

- quel contrôle ;
- pourquoi il bloque ;
- comment corriger.

Évite un pipeline de 500 lignes incompréhensible.

---

## 92. Rapport pré-push

Avant push, produire un résumé :

### Passed
- lint
- format
- tests
- migrations

### Warnings
- dependency minor update

### Blocking
- secret detected

Ne pousse que si `Blocking` est vide.

---

## 93. Historique

Ne réécris pas l’historique uniquement pour rendre les commits « plus beaux » sans demande.

La sécurité et la collaboration priment.

---

## 94. Gitignore audit

Lors d’un nouveau type de fichier créé :

analyse s’il doit être versionné.

Exemple :

- uploads : non ;
- migrations : oui ;
- lockfile : généralement oui pour app ;
- `.env.example` : oui.

---

## 95. Fichiers sensibles déjà suivis

Ajouter un fichier au `.gitignore` ne le retire pas du suivi Git.

Si un fichier sensible est déjà tracked :

retire-le de l’index avec la méthode adaptée, sans supprimer la copie locale si nécessaire.

---

## 96. Données de test

Évite de versionner :

- dump production ;
- PII ;
- base locale.

Utilise fixtures fictives.

---

## 97. Generated docs

Si documentation générée est reconstruite automatiquement :

décide si les artefacts construits doivent être versionnés.

Ne versionne pas automatiquement `site/` ou build HTML si la source Markdown suffit.

---

## 98. AGENTS.md

Le fichier AGENTS doit indiquer :

- commandes lint ;
- format ;
- tests ;
- check ;
- pre-push ;
- interdiction commit/push auto.

Maintiens ces commandes réelles.

---

## 99. Documentation qualité

Documente dans README ou docs :

- installation hooks ;
- commandes ;
- règles bloquantes ;
- comment résoudre un échec.

Le workflow doit être compréhensible par quelqu’un qui reprend le projet.

---

## 100. Relecture avant push

Même si tous les outils sont verts :

relis les changements.

Cherche :

- fonctionnalité oubliée ;
- comportement inattendu ;
- commentaire temporaire ;
- secret non détecté ;
- fichier accidentel.

---

## 101. Definition of Done quality

Avant de dire « prêt à pousser », les points applicables doivent être vrais :

- status propre/compris ;
- diff relu ;
- lint vert ;
- format vert ;
- tests pertinents verts ;
- Django check vert ;
- migration check vert ;
- migrations relues ;
- secrets absents ;
- dépendances critiques vérifiées ;
- docs/tasks/changelog à jour ;
- aucun blocker critique.

---

## 102. Principe final

Git n’est pas une poubelle de sauvegarde.

Le dépôt partagé doit rester une version cohérente, testée et compréhensible du projet.

Les contrôles doivent empêcher les erreurs coûteuses sans transformer chaque modification en parcours administratif.
