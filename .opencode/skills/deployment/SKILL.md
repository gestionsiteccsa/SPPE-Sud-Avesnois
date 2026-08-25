---
name: deployment
description: Conçoit, documente et sécurise le déploiement d’un projet Django en staging et production, avec ou sans Docker. À utiliser pour serveur Linux, reverse proxy, serveur WSGI/ASGI, HTTPS, variables d’environnement, PostgreSQL, static/media, migrations, services systemd, Docker Compose, health checks, rollback, déploiement reproductible et contrôles post-déploiement. N’effectue aucune opération destructive de production sans accord explicite.
compatibility: opencode
metadata:
  framework: django
  purpose: deployment
  language: fr
  workflow-parent: project-workflow
---

# Deployment Django

## 1. Mission

Tu es responsable d’un déploiement Django :

- reproductible ;
- sécurisé ;
- documenté ;
- observable ;
- réversible ;
- aussi proche que possible entre staging et production ;
- utilisable avec Docker ou sans Docker.

Le projet ne doit jamais dépendre obligatoirement de Docker si le projet a décidé de supporter les deux modes.

---

## 2. Principe fondamental

Ne « copie pas simplement le projet sur le serveur ».

Un déploiement doit définir explicitement :

- version du code ;
- runtime Python ;
- dépendances ;
- settings ;
- variables d’environnement ;
- base de données ;
- migrations ;
- static/media ;
- serveur applicatif ;
- reverse proxy ;
- HTTPS ;
- logs ;
- sauvegardes ;
- health checks ;
- rollback.

---

## 3. Questions de cadrage

Pose au maximum **2 questions à la fois**.

Exemples :

- Le serveur cible est-il déjà connu ?
- Souhaites-tu déployer cette première version avec Docker ou sans Docker ?

Explique pourquoi cela change la procédure.

Si une bonne pratique peut être décidée sans l’utilisateur, décide-la et explique-la.

---

## 4. Coordination

Avant toute opération :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. charge :
   - `django-security`
   - `git-quality`
   - `django-database`
   - `documentation`
4. charge `backup-restore` s’il existe ;
5. inspecte les settings dev/test/staging/prod ;
6. identifie le serveur WSGI ou ASGI retenu ;
7. identifie PostgreSQL et services externes.

---

## 5. Environnements

Le projet doit distinguer clairement :

```text
dev
test
staging
prod
```

Le déploiement ne doit jamais dépendre d’un `DEBUG=True` accidentel.

---

## 6. Parité

Cherche une forte parité entre local, staging et production :

- même moteur DB lorsque raisonnable ;
- mêmes versions majeures ;
- mêmes services structurants ;
- configuration par environnement ;
- même processus applicatif autant que possible.

Le local peut conserver des outils de développement supplémentaires.

---

## 7. Settings

Structure typique :

```text
config/settings/
├── base.py
├── dev.py
├── test.py
├── staging.py
└── prod.py
```

Adapte au projet existant.

Ne réorganise pas automatiquement des settings déjà propres.

---

## 8. Secrets

Aucun secret dans Git.

Production utilise des variables d’environnement ou un secret manager adapté.

Ne place jamais dans :

- Dockerfile ;
- compose versionné ;
- README ;
- service systemd ;
- commande shell historique ;

un vrai secret si une méthode plus sûre existe.

---

## 9. `.env`

Un `.env` production peut être utilisé sur un petit serveur si :

- non versionné ;
- permissions filesystem strictes ;
- sauvegarde sécurisée ;
- accès limité.

Pour infrastructure plus mature, préférer un secret manager.

---

## 10. DEBUG

Production :

```text
DEBUG=False
```

Toujours.

Un déploiement avec `DEBUG=True` est bloquant.

---

## 11. ALLOWED_HOSTS

Configure explicitement les domaines/hôtes attendus.

Ne mets pas :

```text
ALLOWED_HOSTS = ["*"]
```

en production sans justification architecturale très particulière.

---

## 12. CSRF trusted origins

Configure les origines HTTPS nécessaires.

Ne désactive pas CSRF pour résoudre un problème de proxy.

---

## 13. Proxy headers

Si reverse proxy :

configure correctement la détection HTTPS et les headers proxy selon l’architecture.

N’accepte pas aveuglément des headers de proxy depuis Internet si Django est directement exposé.

---

## 14. Django non exposé directement

En production standard :

```text
Internet
   |
Reverse proxy
   |
WSGI/ASGI server
   |
Django
```

Le serveur de développement Django n’est pas un serveur de production.

---

## 15. `runserver`

Ne déploie jamais avec :

```bash
python manage.py runserver
```

Django indique explicitement que `runserver` n’est pas conçu pour la production.

---

## 16. WSGI vs ASGI

Choisis selon les besoins.

WSGI :
- application principalement synchrone ;
- stack classique.

ASGI :
- async ;
- WebSockets ;
- connexions longues ;
- certains workloads modernes.

Ne choisis pas ASGI uniquement parce qu’il est plus récent.

---

## 17. Serveur applicatif

Utilise un serveur de production adapté à l’interface retenue.

Exemples possibles selon projet :

- Gunicorn ;
- Uvicorn ;
- Daphne ;
- autre serveur maintenu compatible.

Ne fige pas un serveur universel dans ce skill.

---

## 18. Reverse proxy

Nginx, Caddy ou équivalent peut gérer :

- TLS ;
- compression ;
- static ;
- limites ;
- proxy ;
- headers.

Choisis selon l’infrastructure réelle.

---

## 19. HTTPS

Production doit utiliser HTTPS.

Automatise le renouvellement du certificat.

Teste le renouvellement et documente la procédure.

---

## 20. HTTP

Redirige HTTP vers HTTPS lorsque le site doit être uniquement sécurisé.

Attention aux health checks internes et architecture proxy.

---

## 21. HSTS

Active HSTS uniquement après validation HTTPS complète.

Commence prudemment.

Ne précharge pas un domaine sans comprendre les conséquences.

---

## 22. Cookies

En production HTTPS :

analyse et configure :

- Secure ;
- HttpOnly ;
- SameSite ;
- CSRF cookie ;
- session cookie.

Charge `django-security`.

---

## 23. PostgreSQL

Pour une application de production structurée, PostgreSQL est généralement la base recommandée si c’est le moteur choisi par le projet.

Ne bascule pas silencieusement SQLite → PostgreSQL au moment du déploiement sans tests.

---

## 24. Base distante

La DB ne doit pas être exposée publiquement sans nécessité.

Préférer :

- localhost ;
- réseau privé ;
- firewall ;
- réseau Docker privé.

---

## 25. Compte DB

Django doit utiliser un compte DB dédié avec permissions nécessaires, pas un superuser PostgreSQL.

---

## 26. Migrations

Une release contenant des migrations doit prévoir :

1. backup si risque ;
2. validation migrations ;
3. application contrôlée ;
4. vérification ;
5. stratégie rollback.

Ne lance pas automatiquement des migrations destructrices sur production.

---

## 27. `migrate`

Commande standard :

```bash
python manage.py migrate
```

Mais avant production, inspecte les migrations nouvelles.

---

## 28. Migrations destructrices

Pour :

- suppression colonne ;
- changement de type risqué ;
- grosse migration de données ;
- contrainte lourde ;

prépare un plan spécifique.

Une migration Django valide syntaxiquement n’est pas forcément sûre en production.

---

## 29. Expand/contract

Pour changements DB sensibles avec déploiement sans interruption :

1. ajouter structure compatible ;
2. déployer code compatible ;
3. migrer données ;
4. basculer ;
5. supprimer ancien champ dans une release ultérieure.

Utilise seulement lorsque nécessaire.

---

## 30. Static files

Production doit exécuter la stratégie prévue pour :

```bash
python manage.py collectstatic
```

Ne sers pas les static avec `runserver`.

---

## 31. Static via reverse proxy

Sur un petit serveur, reverse proxy peut servir le répertoire collecté.

Une solution comme WhiteNoise peut aussi être retenue selon architecture.

Documente le choix.

---

## 32. Media

Les uploads utilisateurs sont différents des static.

Ils nécessitent :

- stockage ;
- permissions ;
- sauvegarde ;
- taille ;
- sécurité ;
- stratégie de service.

Ne les écrase pas lors d’un nouveau déploiement.

---

## 33. Media privé

Un fichier privé ne doit pas devenir public simplement parce qu’il existe dans `MEDIA_ROOT`.

Charge `django-security`.

---

## 34. Utilisateur système

Exécute l’application avec un utilisateur dédié non root.

Ne lance pas le processus Django en root.

---

## 35. Permissions filesystem

Le processus doit avoir uniquement les permissions nécessaires.

Évite :

```bash
chmod -R 777
```

---

## 36. Répertoire release

Une stratégie sans Docker peut utiliser :

```text
/srv/myproject/
├── releases/
├── current -> releases/...
├── shared/
│   ├── media/
│   └── env/
```

Cette structure facilite rollback.

Elle n’est pas obligatoire pour un très petit projet, mais le déploiement doit rester reproductible.

---

## 37. Virtualenv

Sans Docker, utilise un environnement Python isolé.

Ne pip-installe pas l’application dans le Python système sans stratégie claire.

---

## 38. Python

Épingle la version Python supportée.

Staging et prod doivent utiliser la même version majeure/mineure lorsque possible.

---

## 39. Dépendances

Installe depuis les fichiers versionnés/lockés du projet.

Ne fais pas :

```bash
pip install -U ...
```

arbitrairement pendant une release.

---

## 40. systemd

Sans Docker, systemd est une bonne option sur Linux pour gérer le processus.

Le service doit définir :

- utilisateur ;
- working directory ;
- environnement ;
- commande ;
- restart policy ;
- logs.

Ne mets pas les secrets directement dans un fichier world-readable.

---

## 41. Exemple systemd

Le template fourni par ce skill doit rester un exemple avec placeholders.

Ne copie pas un chemin fictif en production sans adaptation.

---

## 42. Restart

Un restart doit être contrôlé.

Après restart :

- statut service ;
- logs ;
- health check ;
- test HTTP.

Ne considère pas `systemctl restart` réussi comme preuve que l’application fonctionne.

---

## 43. Logs

Les logs doivent permettre de diagnostiquer :

- erreurs Django ;
- erreurs serveur ;
- reverse proxy ;
- déploiement.

Ils ne doivent pas contenir :

- passwords ;
- tokens ;
- données sensibles inutiles.

---

## 44. Rotation logs

Configure une rotation ou utilise journald/plateforme.

Évite qu’un disque se remplisse à cause des logs.

---

## 45. Health check

Prévois un endpoint ou mécanisme simple.

Exemple :

```text
/health/
```

Il doit vérifier au minimum que l’application répond.

Un health check profond peut vérifier DB/services, mais attention à son coût et à ce qu’il révèle.

---

## 46. Liveness vs readiness

Si infrastructure avancée :

- liveness : processus vivant ;
- readiness : prêt à recevoir trafic.

Pour un petit serveur, un seul endpoint simple peut suffire.

---

## 47. Endpoint health

Ne révèle pas :

- version détaillée des composants ;
- credentials ;
- stack trace ;
- config interne.

---

## 48. Smoke tests

Après déploiement, teste quelques parcours critiques :

- page d’accueil ;
- login si applicable ;
- endpoint principal ;
- DB ;
- static ;
- media selon besoin.

---

## 49. Déploiement atomique

Évite une période où moitié des fichiers sont ancienne version et moitié nouvelle.

Une stratégie release + symlink ou image Docker immuable aide.

---

## 50. Rollback

Chaque procédure de déploiement doit expliquer comment revenir à la release précédente.

Rollback code n’implique pas automatiquement rollback DB.

---

## 51. Rollback DB

Les migrations DB peuvent rendre le rollback complexe.

Avant migration destructive, définis explicitement la stratégie.

Ne lance pas automatiquement `migrate app old_number` sur prod.

---

## 52. Sauvegarde avant release

Pour une migration risquée :

déclenche ou vérifie un backup récent.

Charge `backup-restore`.

---

## 53. Docker optionnel

Le dépôt peut contenir :

- `Dockerfile`
- `compose.yml`
- `.dockerignore`

tout en supportant un déploiement classique.

La présence de Docker ne rend pas Docker obligatoire.

---

## 54. Dockerfile

Un Dockerfile production doit viser :

- image maintenue ;
- version épinglée raisonnablement ;
- utilisateur non root ;
- dépendances minimales ;
- build reproductible ;
- pas de secret.

---

## 55. Multi-stage build

Utilise multi-stage si cela réduit réellement l’image ou sépare build/runtime.

Ne complexifie pas une petite image Python sans bénéfice.

---

## 56. `.dockerignore`

Exclure :

- `.git`
- `.env`
- venv ;
- caches ;
- media locaux ;
- logs ;
- tests artefacts ;
- secrets.

N’exclus pas les fichiers nécessaires au build.

---

## 57. Docker Compose

Compose peut orchestrer local/staging/petit serveur :

- web ;
- postgres ;
- redis ;
- worker ;
- reverse proxy.

Ne crée pas 12 services si le projet n’en utilise que 2.

---

## 58. Compose production

Si Compose en production :

- volumes persistants ;
- restart policies ;
- secrets/env ;
- health checks ;
- réseaux ;
- backups ;
- versions.

Ne traite pas `docker compose up` comme stratégie complète.

---

## 59. Volumes

Les données persistantes doivent survivre au remplacement du conteneur :

- PostgreSQL ;
- media ;
- autres données.

Ne stocke pas les données importantes uniquement dans la couche writable d’un container.

---

## 60. Docker DB

Ne supprime jamais un volume DB lors d’un simple redéploiement.

Commandes avec `-v` nécessitent une vigilance particulière.

---

## 61. Build vs pull

Définis si le serveur :

- build localement ;
- pull une image construite en CI.

Pour un petit serveur, build local peut être acceptable.

Pour workflow mature, image construite/testée en CI est préférable.

---

## 62. Image tags

Évite `latest` comme seule référence de rollback.

Utilise un tag/version/commit identifiable.

---

## 63. Staging

Staging doit permettre de valider :

- migrations ;
- configuration ;
- static ;
- intégrations ;
- comportement production-like.

Il ne doit pas utiliser les données réelles de production sans politique explicite.

---

## 64. Données staging

Préférer données fictives/anonymisées.

Ne clone pas une base production contenant des données personnelles sur staging sans nécessité et protections.

---

## 65. Staging protégé

Un staging exposé à Internet peut nécessiter :

- authentification ;
- firewall ;
- robots interdits ;
- données fictives.

---

## 66. Production

Production doit être la configuration la plus stricte.

Aucun outil de debug ou profiler exposé.

---

## 67. `check --deploy`

Avant release production :

```bash
python manage.py check --deploy --settings=<settings-prod>
```

Utilise des variables adaptées.

Un warning critique doit être analysé.

---

## 68. Quality gate

Avant déploiement :

charge `git-quality`.

La release doit partir d’un état Git identifié et validé.

Ne déploie pas des modifications locales non comprises.

---

## 69. Commit déployé

Enregistre l’identifiant du commit/release déployé.

Cela facilite :

- diagnostic ;
- rollback ;
- audit.

---

## 70. Git sur serveur

Deux stratégies possibles :

- clone/pull contrôlé ;
- artefact/image déployé.

Pour une petite installation, Git sur serveur est acceptable.

Pour maturité supérieure, artefact immuable est préférable.

---

## 71. `git pull` aveugle

Ne fais pas simplement :

```bash
git pull && restart
```

sans :

- contrôle branche ;
- dépendances ;
- migrations ;
- static ;
- health check ;
- rollback.

---

## 72. CI/CD

Automatise progressivement.

Une première version peut avoir un script documenté.

Plus tard :

- CI tests ;
- build ;
- deploy staging ;
- validation ;
- prod.

N’automatise pas une mauvaise procédure.

---

## 73. Déploiement manuel reproductible

Même manuel, le déploiement doit suivre une checklist ou script.

Deux déploiements identiques doivent suivre les mêmes étapes.

---

## 74. Script deploy

Un script peut :

- vérifier Git ;
- installer dépendances ;
- migrate ;
- collectstatic ;
- restart ;
- health check.

Les étapes dangereuses doivent être clairement identifiées.

---

## 75. Pas de secret dans script

Les scripts lisent les secrets depuis l’environnement.

---

## 76. Maintenance mode

Pour migration longue ou incompatible, un mode maintenance peut être nécessaire.

Ne l’active pas systématiquement pour chaque release.

---

## 77. Zero downtime

Ne promet pas zéro downtime sans architecture adaptée.

Sur petit serveur, quelques secondes contrôlées peuvent être acceptables.

---

## 78. Reverse proxy timeout

Adapte les timeouts aux besoins.

Ne masque pas une opération applicative mal conçue en mettant un timeout de 30 minutes.

---

## 79. Upload size

Définis les limites cohérentes :

- proxy ;
- Django ;
- application.

Sinon une limite Nginx peut contredire le formulaire.

---

## 80. Firewall

Expose uniquement les ports nécessaires.

Typiquement :

- SSH ;
- HTTP ;
- HTTPS.

PostgreSQL/Redis ne devraient généralement pas être publics.

---

## 81. SSH

Pour administration :

- clés SSH ;
- utilisateur non root ;
- permissions ;
- fail2ban ou équivalent selon exposition ;
- mises à jour.

La configuration système détaillée peut être séparée dans un skill infrastructure.

---

## 82. OS updates

Le serveur doit recevoir des mises à jour de sécurité.

Ne mets pas à jour aveuglément le système au milieu d’un déploiement applicatif.

---

## 83. Reboot

Si mise à jour nécessite reboot :

planifie et vérifie que les services redémarrent automatiquement.

---

## 84. Horloge

Serveur synchronisé via NTP.

Important pour :

- TLS ;
- sessions ;
- logs ;
- tâches ;
- tokens.

---

## 85. DNS

Avant production :

- domaine ;
- records ;
- TTL ;
- certificat ;
- redirection.

Ne modifie pas DNS sans demande explicite.

---

## 86. Email

Si le projet envoie des emails :

staging ne doit pas accidentellement envoyer de vrais emails aux utilisateurs production.

Utilise backend de test ou destinataires contrôlés.

---

## 87. Services externes

Pour chaque intégration :

- clé par environnement ;
- endpoint staging si disponible ;
- timeout ;
- retry ;
- observabilité.

Ne réutilise pas systématiquement les credentials prod en staging.

---

## 88. Tâches async

Si Celery/RQ/etc. :

déployer aussi :

- worker ;
- scheduler si nécessaire ;
- broker ;
- monitoring ;
- restart.

Ne déploie pas uniquement le web.

---

## 89. Cron

Les tâches planifiées doivent être versionnées/documentées autant que possible.

Évite un cron créé manuellement puis oublié.

---

## 90. Une seule exécution

Pour tâches planifiées critiques en environnement multi-instance, éviter les doublons.

Le mécanisme dépend de l’architecture.

---

## 91. Observabilité minimale

Au minimum :

- logs ;
- disponibilité ;
- espace disque ;
- DB ;
- sauvegardes.

Pour projet plus important :

- métriques ;
- traces ;
- alerting.

---

## 92. Espace disque

Sur mini-PC, surveille particulièrement :

- logs ;
- backups ;
- Docker images ;
- PostgreSQL ;
- media.

Un disque plein peut arrêter l’application.

---

## 93. Monitoring backup

Une sauvegarde non vérifiée n’est pas suffisante.

Le skill `backup-restore` doit prévoir contrôle et restauration testée.

---

## 94. Déploiement sans Docker

Procédure type :

1. préparer serveur ;
2. utilisateur applicatif ;
3. code/release ;
4. virtualenv ;
5. dépendances ;
6. env ;
7. DB ;
8. migrate ;
9. collectstatic ;
10. systemd ;
11. reverse proxy ;
12. TLS ;
13. health/smoke tests.

Documente chaque étape.

---

## 95. Déploiement Docker

Procédure type :

1. préparer serveur ;
2. Docker/Compose ;
3. env/secrets ;
4. volumes ;
5. build/pull ;
6. DB ;
7. migrations ;
8. static ;
9. services ;
10. reverse proxy/TLS ;
11. health/smoke tests.

---

## 96. Choix Docker

Si l’utilisateur ne connaît pas Docker :

ne le force pas.

Tu peux maintenir les fichiers Docker comme option future.

La procédure sans Docker doit rester pleinement fonctionnelle.

---

## 97. Documentation

Maintiens :

```text
docs/operations/deployment.md
```

avec :

- prérequis ;
- staging ;
- prod ;
- Docker ;
- sans Docker ;
- rollback ;
- dépannage ;
- vérifications.

---

## 98. Runbook release

Crée une checklist reproductible :

```text
Avant
Déploiement
Après
Rollback
```

Elle doit pouvoir être suivie par quelqu’un d’autre.

---

## 99. Relecture second développeur

Avant une mise en production, vérifie :

- DEBUG ?
- secrets ?
- hosts ?
- HTTPS ?
- cookies ?
- migrations ?
- backup ?
- static ?
- media ?
- service non-root ?
- DB exposée ?
- firewall ?
- logs ?
- health ?
- rollback ?
- version Git ?
- documentation ?

---

## 100. Definition of Done déploiement

Un déploiement est réussi seulement si :

- processus actif ;
- health check OK ;
- page principale OK ;
- DB OK ;
- migrations OK ;
- static OK ;
- HTTPS OK ;
- logs sans erreur critique ;
- version déployée connue ;
- backup/rollback cohérents ;
- documentation à jour.

---

## 101. Incident pendant déploiement

Si un contrôle critique échoue :

- arrête ;
- conserve les logs ;
- ne poursuis pas « pour voir » ;
- évalue rollback ;
- protège les données.

---

## 102. Principe final

Un bon déploiement n’est pas celui qui fonctionne une fois.

C’est celui qui peut être reproduit, compris, vérifié et annulé proprement.
