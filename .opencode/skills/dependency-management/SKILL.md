---
name: dependency-management
description: Gère les dépendances Python/Django et, si présent, JavaScript/Node d’un projet : ajout, suppression, verrouillage, mises à jour, vulnérabilités, compatibilité, licences, dépendances abandonnées et contrôles avant commit/push/release. À utiliser dès qu’une bibliothèque est ajoutée ou modifiée et lors des revues périodiques de dépendances.
compatibility: opencode
metadata:
  framework: django
  purpose: dependency-management
  language: fr
  workflow-parent: project-workflow
---

# Dependency Management

## 1. Mission

Tu dois maintenir les dépendances du projet :

- nécessaires ;
- maintenues ;
- compatibles ;
- reproductibles ;
- sûres ;
- documentées lorsqu’elles structurent le projet.

Une dépendance est du code tiers auquel le projet accorde sa confiance.

N’ajoute donc jamais une bibliothèque uniquement pour économiser quelques lignes triviales.

---

## 2. Coordination

Avant toute modification :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. charge selon le contexte :
   - `django-security`
   - `git-quality`
   - `django-testing`
   - `deployment`
   - `documentation`
4. identifie le gestionnaire de dépendances réellement utilisé.

Ne mélange pas plusieurs gestionnaires sans raison.

---

## 3. Gestionnaire existant

Respecte le projet.

Exemples Python :

- `pyproject.toml` ;
- `requirements*.txt` ;
- Poetry ;
- uv ;
- pip-tools ;
- autre outil déjà retenu.

Exemples frontend :

- npm ;
- pnpm ;
- yarn.

Ne migre pas de gestionnaire uniquement par préférence personnelle.

---

## 4. Questions

Pose au maximum 2 questions si une décision métier/technique importante manque.

Pour une simple dépendance, ne transforme pas l’ajout en interrogatoire.

Explique en langage accessible pourquoi un choix a un impact.

---

## 5. Avant d’ajouter une dépendance

Demande-toi :

1. le besoin existe-t-il vraiment ?
2. Django/Python sait-il déjà le faire ?
3. la dépendance est-elle maintenue ?
4. est-elle compatible avec les versions du projet ?
5. quel est son impact sécurité ?
6. quelle est sa profondeur transitive ?
7. est-elle structurante ou facilement remplaçable ?

---

## 6. Standard library first

Si la bibliothèque standard Python répond proprement au besoin, préfère-la généralement.

Mais ne réimplémente pas une fonctionnalité complexe de sécurité ou protocole pour éviter une dépendance reconnue.

---

## 7. Django first

Avant un package Django tiers, vérifie si Django fournit déjà une solution adaptée.

Exemples :

- auth ;
- sessions ;
- cache ;
- email ;
- validation ;
- sécurité ;
- pagination ;
- formulaires.

---

## 8. Évaluation d’un package

Avant une dépendance importante, analyse :

- documentation ;
- maintenance récente ;
- compatibilité ;
- communauté ;
- historique de sécurité ;
- fréquence de release ;
- licence ;
- dépendances transitives ;
- qualité des tests si visible.

Ne juge pas uniquement au nombre d’étoiles GitHub.

---

## 9. Package abandonné

Évite une nouvelle dépendance manifestement abandonnée si une alternative maintenue existe.

Pour une dépendance existante abandonnée :

- ne la supprime pas brutalement ;
- évalue le risque ;
- crée une tâche de remplacement si nécessaire.

---

## 10. Typosquatting

Vérifie soigneusement le nom exact d’un package avant installation.

Ne devine jamais le nom PyPI/npm.

Une faute peut installer un package malveillant.

---

## 11. Source

Utilise les registres et sources approuvés par le projet.

Ne récupère pas arbitrairement une archive depuis un site inconnu.

---

## 12. Git dependency

Une dépendance directement depuis Git doit être exceptionnelle.

Si nécessaire :

- dépôt de confiance ;
- commit/tag précis ;
- raison documentée.

Évite une branche mouvante comme `main`.

---

## 13. Versioning

Les environnements doivent pouvoir reproduire le même ensemble de dépendances.

Le niveau de verrouillage dépend du gestionnaire retenu.

Ne laisse pas la production résoudre librement des versions différentes de celles testées.

---

## 14. Versions flottantes

Évite les dépendances totalement non bornées pour un déploiement reproductible.

Mais ne fixe pas artificiellement chaque contrainte dans les métadonnées d’une bibliothèque réutilisable comme dans une application.

Ce skill cible principalement une application Django.

---

## 15. Lock file

Si le gestionnaire fournit un lockfile pour application :

- versionne-le ;
- mets-le à jour avec l’outil prévu ;
- ne l’édite pas manuellement sauf cas documenté.

---

## 16. Hashes

Lorsque le workflow Python retenu supporte proprement des hashes verrouillés, ils peuvent renforcer la reproductibilité/intégrité.

Ne les ajoute pas avec une procédure que l’équipe ne peut pas maintenir.

---

## 17. Dépendances directes/transitives

Distingue :

- dépendance choisie par le projet ;
- dépendance installée indirectement.

Ne modifie pas arbitrairement une transitive sans comprendre la chaîne.

---

## 18. Ajout

Après ajout :

1. fichier manifeste mis à jour ;
2. lock/résolution mis à jour ;
3. installation propre ;
4. tests pertinents ;
5. audit sécurité ;
6. documentation si structurante.

---

## 19. Suppression

Quand une dépendance n’est plus utilisée :

- retirer imports ;
- retirer configuration ;
- retirer package ;
- régénérer lock ;
- tester ;
- vérifier documentation.

Évite les dépendances mortes.

---

## 20. Mise à jour

Une mise à jour n’est pas uniquement :

```text
prendre la dernière version
```

Analyse :

- changelog ;
- breaking changes ;
- migration guide ;
- sécurité ;
- Python/Django supportés.

---

## 21. Patch

Les mises à jour patch sont généralement moins risquées, mais pas automatiquement sans risque.

Exécute les tests pertinents.

---

## 22. Minor

Une version mineure peut introduire :

- nouvelles fonctionnalités ;
- dépréciations ;
- changements comportementaux.

Lis les notes si dépendance importante.

---

## 23. Major

Une mise à jour majeure nécessite une revue explicite.

Ne la mélange pas à une feature métier sans raison.

---

## 24. Django

Avant upgrade Django :

- release notes ;
- versions Python ;
- dépréciations ;
- dépendances compatibles ;
- tests ;
- settings ;
- middleware ;
- DB ;
- templates.

Traite cela comme une évolution technique dédiée.

---

## 25. Python

Avant changement de version Python :

- Django compatible ;
- packages compatibles ;
- image Docker/serveur ;
- CI ;
- staging ;
- production.

---

## 26. PostgreSQL

Le client/driver Python et la version PostgreSQL doivent rester cohérents avec la politique du projet.

Une mise à jour DB majeure relève aussi de `deployment` et `backup-restore`.

---

## 27. Frontend

Si Node existe, applique les mêmes principes :

- lockfile ;
- dépendances minimales ;
- audit ;
- compatibilité ;
- build reproductible.

Ne crée pas une stack Node pour un projet Django qui n’en a pas besoin.

---

## 28. Dev dependencies

Sépare autant que le gestionnaire le permet :

- runtime ;
- développement ;
- test ;
- lint ;
- documentation.

La production ne doit pas forcément installer les outils de développement.

---

## 29. Sécurité

Avant release/push lorsque pertinent, vérifie les vulnérabilités connues.

Pour Python, utilise un outil adapté à l’écosystème du projet, par exemple `pip-audit` si retenu.

Pour npm, utilise les mécanismes adaptés à npm et analyse les résultats.

---

## 30. Audit ≠ vérité absolue

Un audit de dépendances peut produire :

- vrais risques ;
- faux positifs ;
- vulnérabilités non exploitables dans le contexte ;
- absence de correctif.

Analyse, ne masque pas.

---

## 31. Vulnérabilité critique

Si une vulnérabilité critique/haute est réellement applicable au projet et qu’un correctif raisonnable existe :

le push/release doit être bloqué jusqu’à correction ou décision explicitement documentée.

---

## 32. Exception sécurité

Une exception doit documenter :

- package ;
- vulnérabilité ;
- contexte ;
- pourquoi non exploitable/acceptée ;
- mitigation ;
- date de réévaluation.

Ne crée pas un ignore permanent sans justification.

---

## 33. Secret scanners

La gestion des dépendances ne remplace pas la détection de secrets.

Charge `git-quality` / `django-security`.

---

## 34. Supply chain

Réduis la surface de chaîne d’approvisionnement :

- peu de dépendances ;
- sources fiables ;
- lock ;
- revue des changements importants ;
- CI reproductible.

---

## 35. Scripts d’installation

Certaines dépendances npm/Python peuvent exécuter du code pendant installation/build.

Sois particulièrement prudent avec une dépendance inconnue.

---

## 36. Licence

Pour dépendance structurante, vérifie que sa licence est compatible avec le projet.

Ne donne pas de conclusion juridique définitive si le cas est complexe.

Signale le besoin de validation.

---

## 37. Package privé

Pour package privé :

- registry sécurisé ;
- token hors Git ;
- accès minimal ;
- documentation d’installation sans secret.

---

## 38. Environnements

Dev/test/staging/prod doivent utiliser un ensemble de runtime cohérent.

Les différences doivent être intentionnelles, pas accidentelles.

---

## 39. Production

N’exécute pas une mise à jour générale non testée directement en production.

La production installe l’état validé.

---

## 40. Staging

Pour changement de dépendance structurant :

teste en staging lorsque le risque le justifie.

---

## 41. Clean install

Périodiquement et avant release importante, vérifie qu’une installation depuis zéro fonctionne avec les fichiers versionnés.

Cela détecte les dépendances « présentes uniquement sur ma machine ».

---

## 42. Imports fantômes

Une dépendance peut fonctionner localement car installée globalement sans être déclarée.

Un environnement propre doit le détecter.

---

## 43. Dépendance inutilisée

Quand possible, identifie les packages devenus inutiles.

Ne supprime pas automatiquement uniquement sur analyse statique : Django peut charger dynamiquement des composants.

---

## 44. Requirements par environnement

Si le projet utilise des requirements séparés, conserve une hiérarchie claire.

Exemple :

```text
requirements/
├── base.txt
├── dev.txt
├── test.txt
└── prod.txt
```

Mais n’impose pas ce modèle si `pyproject.toml` gère déjà proprement les groupes.

---

## 45. Duplication

Évite de maintenir manuellement la même version dans de nombreux fichiers si l’outil permet une source unique.

---

## 46. Contraintes

Utilise des contraintes lorsque cela résout un vrai problème de compatibilité.

Documente les pins temporaires inhabituels.

---

## 47. Pin temporaire

Exemple :

```text
package<3
```

doit idéalement avoir une raison et une tâche de réévaluation si le blocage est temporaire.

---

## 48. Dépréciations

Les warnings de dépréciation sont une dette future.

Lors d’une mise à jour, analyse-les et crée des tâches pertinentes.

Ne laisse pas tout s’accumuler jusqu’au prochain major.

---

## 49. Tests

Après modification de dépendance :

- tests ciblés ;
- tests d’intégration si nécessaire ;
- suite complète selon impact.

Charge `django-testing`.

---

## 50. Performance

Une dépendance peut dégrader :

- démarrage ;
- mémoire ;
- requêtes ;
- taille frontend.

Pour dépendance structurante, charge `django-performance`.

---

## 51. Documentation

Documente une dépendance si elle affecte l’architecture ou l’exploitation.

Pas besoin d’une page wiki pour chaque petit package.

---

## 52. ADR

Une dépendance majeure peut mériter un ADR.

Exemples :

- Celery ;
- DRF ;
- Channels ;
- moteur de recherche ;
- stockage objet.

---

## 53. Changelog

Une mise à jour purement interne mineure ne nécessite pas forcément une entrée utilisateur.

Une évolution ayant impact notable doit apparaître selon la politique du projet.

---

## 54. PROJECT_TASKS

Crée une tâche si :

- migration future nécessaire ;
- package abandonné ;
- pin temporaire ;
- vulnérabilité acceptée temporairement ;
- major upgrade différé.

---

## 55. Avant commit

Contrôle :

- manifestes cohérents ;
- lock à jour ;
- aucun secret ;
- tests pertinents ;
- format/lint selon workflow.

Le commit reste demandé par l’utilisateur selon la politique globale.

---

## 56. Avant push

Le push est un quality gate.

Vérifie notamment :

- état Git ;
- tests critiques ;
- dépendances déclarées ;
- audit sécurité ;
- migrations ;
- secrets ;
- documentation nécessaire.

---

## 57. Vérifier les mises à jour avant push

Ne bloque pas un push uniquement parce qu’une nouvelle version non critique existe.

Ce serait trop agressif.

Signale les mises à jour disponibles selon politique.

Bloque pour :

- vulnérabilité critique applicable ;
- dépendance cassée ;
- incompatibilité ;
- lock incohérent.

---

## 58. Pourquoi

« Une mise à jour existe » n’est pas synonyme de « le projet est vulnérable ».

Mettre à jour juste avant chaque push peut introduire des régressions.

Les upgrades doivent être contrôlés et testés.

---

## 59. Release

Avant release :

- installation reproductible ;
- audits ;
- tests ;
- staging selon risque ;
- notes de migration ;
- rollback si dépendance structurante.

---

## 60. Dépendance native

Certaines bibliothèques nécessitent :

- paquets OS ;
- compilateur ;
- bibliothèques C ;
- runtime externe.

Documente-les dans `deployment`.

---

## 61. Docker

Les dépendances OS de l’image doivent être minimales.

Ne laisse pas les outils de build dans l’image runtime si multi-stage permet de les retirer raisonnablement.

---

## 62. Images de base

Une image Docker est aussi une dépendance.

Épingle raisonnablement la version et surveille les mises à jour sécurité.

---

## 63. Actions CI

Les actions/plugins de CI sont également du code tiers.

Épingle selon les bonnes pratiques de la plateforme.

Ne les considère pas comme hors périmètre supply-chain.

---

## 64. CDN frontend

Une bibliothèque chargée depuis un CDN est une dépendance externe.

Analyse :

- disponibilité ;
- confidentialité ;
- CSP ;
- intégrité ;
- version.

Préférer self-hosting si le contexte sécurité/RGPD le justifie.

---

## 65. SRI

Pour ressources externes statiques compatibles, Subresource Integrity peut être pertinente.

Charge `django-security`.

---

## 66. Auto-update bots

Dependabot/Renovate ou équivalent peuvent proposer les mises à jour.

Ils ne doivent pas fusionner aveuglément les changements importants sans tests.

---

## 67. Automatisation progressive

Pour un petit projet :

1. audit manuel/scripté ;
2. CI ;
3. bot de mise à jour éventuellement.

Ne complexifie pas dès le premier jour.

---

## 68. Fréquence revue

En plus des changements de feature, prévois une revue périodique des dépendances.

La fréquence dépend de la criticité.

Les alertes de sécurité importantes ne doivent pas attendre la revue périodique.

---

## 69. EOL

Surveille les versions en fin de support :

- Python ;
- Django ;
- PostgreSQL ;
- Node si présent.

Planifie leur upgrade avant urgence.

---

## 70. Django LTS

Une version LTS peut être pertinente pour certains projets recherchant stabilité/support long.

Ne force pas LTS si le projet a une stratégie différente et maîtrisée.

---

## 71. Compatibilité navigateur

Les dépendances frontend peuvent avoir un impact navigateur.

Charge `frontend-django` si pertinent.

---

## 72. Paquet sécurité

Pour auth, crypto, JWT, OAuth, parsing complexe :

préfère une solution reconnue et maintenue plutôt qu’une implémentation maison.

---

## 73. JWT

N’ajoute pas JWT parce que c’est populaire.

Si les sessions Django répondent au besoin, elles peuvent être plus simples.

Charge `django-auth` / `django-api`.

---

## 74. Celery

N’ajoute pas Celery pour une tâche périodique triviale si un timer suffit.

Une dépendance architecturale doit résoudre un besoin réel.

---

## 75. Redis

N’ajoute pas Redis « au cas où ».

Il ajoute un service à exploiter.

Charge `django-performance` si le cache devient nécessaire.

---

## 76. DRF

N’ajoute pas Django REST Framework si le projet n’a pas de vraie API nécessitant son niveau de fonctionnalités.

Charge `django-api`.

---

## 77. Pillow

Une bibliothèque d’image peut être justifiée si traitement d’images nécessaire.

Analyse ses dépendances système et sécurité des fichiers uploadés.

---

## 78. Bibliothèques d’upload

Ne fais pas confiance à une extension de fichier uniquement parce qu’une bibliothèque la reconnaît.

Charge `django-security`.

---

## 79. Package de debug

Django Debug Toolbar et équivalents sont dev-only.

Ne les active pas en production.

---

## 80. Profiler

Même règle : environnement de développement/staging contrôlé.

---

## 81. Test packages

Factory/test helpers restent dev/test sauf besoin runtime réel.

---

## 82. Version source

Pour chaque incident lié à une dépendance, être capable d’identifier la version installée.

Le lock et la release doivent permettre cela.

---

## 83. SBOM

Pour projet à exigences élevées, une Software Bill of Materials peut devenir pertinente.

Ne l’impose pas à tous les petits projets.

---

## 84. Reproductibilité

Un nouveau développeur ou serveur doit pouvoir reconstruire l’environnement sans deviner quels packages installer.

---

## 85. README

Le README doit expliquer la commande officielle d’installation des dépendances.

Une seule procédure principale claire.

---

## 86. Documentation environnement

Si dev et prod installent des groupes différents, explique-le.

---

## 87. Contrôle d’impact

Pour toute dépendance structurante, évalue :

- architecture ;
- sécurité ;
- performance ;
- DB ;
- frontend ;
- déploiement ;
- opérations ;
- tests ;
- documentation.

---

## 88. Refus technique

Refuse/propose une alternative si l’utilisateur demande une dépendance :

- dangereuse ;
- abandonnée ;
- incompatible ;
- disproportionnée.

Explique simplement.

L’utilisateur peut imposer son choix sauf blocage de sécurité critique défini par le workflow.

---

## 89. Relecture second développeur

Avant validation :

- Avons-nous vraiment besoin du package ?
- Est-il maintenu ?
- La version est-elle contrôlée ?
- Est-il compatible ?
- Le lock est-il à jour ?
- Introduit-il un service ?
- Une vulnérabilité connue s’applique-t-elle ?
- Peut-on reconstruire l’environnement ?
- La doc doit-elle changer ?

---

## 90. Definition of Done

Une modification de dépendance est terminée lorsque :

- besoin justifié ;
- source vérifiée ;
- version compatible ;
- manifeste mis à jour ;
- lock/résolution cohérent ;
- installation propre possible ;
- tests pertinents verts ;
- audit sécurité analysé ;
- production reproductible ;
- docs/ADR/tâches mis à jour si nécessaire.

---

## 91. Principe final

Le meilleur graphe de dépendances n’est pas celui qui contient les outils les plus modernes.

C’est le plus petit ensemble de composants maintenus qui répond proprement aux besoins du projet et que l’équipe peut tester, mettre à jour et exploiter.
