# Audit du projet SPPE Sud-Avesnois pour un hébergement o2switch mutualisé

**Date de l'audit :** 17 août 2026  
**Périmètre :** code, configuration, dépendances, sécurité, données, performances et exploitabilité  
**Cible retenue :** Python 3.13, Django 6.0, SQLite, faible trafic/démonstration  
**Verdict au moment de l'audit :** **non prêt pour une mise en ligne publique en l'état**

> Mise à jour de remédiation du 17 août 2026 : les corrections automatisables P0/P1 ont été implémentées. Le projet est désormais techniquement préparé pour une recette o2switch, mais la mise en ligne reste conditionnée à la configuration réelle de cPanel, Redis, SMTP, HTTPS, sauvegarde externe et supervision. Le détail des actions humaines restantes se trouve dans `PROJECT_TASKS.md`.

## État des remédiations

| Domaine | État | Résultat |
|---|---|---|
| Python et dépendances | Corrigé | `.python-version`, `requirements.txt`, `package-lock.json` et CI Python 3.13 |
| Statiques et frontend | Corrigé | `STATIC_ROOT`, build reproductible, artefacts versionnés, dépendances auto-hébergées |
| Passenger/WSGI | Corrigé côté dépôt | `passenger_wsgi.py` et runbook ; création cPanel à réaliser |
| Tests | Corrigé | couverture des flux critiques ajoutée et suite verte |
| Import | Corrigé | validation avant écriture, transaction atomique, date monenfant.fr correcte |
| Audit | Corrigé | modifications et acteur de suppression enregistrés |
| Comptes | Corrigé avec limite documentée | validation Django, confirmation, dernier superutilisateur protégé, backend fermé sur doublon ; unicité DB globale reportée à un éventuel modèle utilisateur personnalisé |
| Données de démonstration | Partiel | données courantes fictives ; ancien historique Git à traiter par décision coordonnée |
| Rate limiting | Corrigé côté dépôt | Redis partagé obligatoire en production, aucun contrôle Django masqué ; instance o2switch à configurer |
| SMTP, logs, sauvegarde, supervision | Partiel | configuration, commandes et runbooks livrés ; services et alertes à activer chez l'hébergeur |
| CSP | Planifié | CDN retirés ; extraction des derniers scripts/styles inline suivie en P2 |

Les constats qui suivent restent le relevé historique de l'état audité et expliquent les décisions prises. Ils ne doivent pas être lus comme l'état actuel du code.

## 1. Résumé exécutif

SPPE Sud-Avesnois est une application Django compacte et lisible qui fournit un annuaire public de structures petite enfance, une carte, des filtres et un tableau de bord réservé aux superutilisateurs. Les vues publiques principales sont paginées ou correctement bornées, les relations courantes sont préchargées et les protections natives Django (CSRF, sessions, validation des mots de passe, variables d'environnement) sont en grande partie présentes.

L'application peut être hébergée chez o2switch avec Django 6.0, mais l'environnement de production doit utiliser **Python 3.13** : l'environnement local utilise Python 3.14, qui n'est pas proposé dans la documentation o2switch consultée. Django 6.0 prend officiellement en charge Python 3.12, 3.13 et 3.14, donc aucune rétrogradation de Django n'est nécessaire.

Les principaux obstacles ne viennent pas de l'architecture métier, mais de la préparation à la production : les dépendances Python ne sont pas déclarées dans un manifeste, la collecte des fichiers statiques échoue, les ressources compilées nécessaires ne sont pas versionnées, aucun test n'est découvert et aucune procédure Passenger, sauvegarde ou retour arrière n'existe. Plusieurs défauts applicatifs importants ont également été confirmés dans l'import, le journal d'audit et la création des utilisateurs.

SQLite reste acceptable pour la cible faible trafic choisie, à condition de limiter les écritures concurrentes, de rendre les imports atomiques et de mettre en place une sauvegarde cohérente avec restauration testée. MariaDB devra être envisagée si les écritures, les administrateurs simultanés ou les erreurs de verrouillage augmentent.

## 2. Périmètre et méthode

L'audit porte sur l'état local du dépôt au 17 août 2026. Il s'agit d'une analyse statique complétée par les contrôles Django et Python disponibles. Aucun code applicatif, schéma ou contenu de base n'a été modifié.

Deux fichiers comportaient déjà des modifications locales au début de l'audit :

- `structures/templates/structures/structure_map.html` ;
- `structures/views/__init__.py`.

Ils ont été analysés dans leur état local actuel. Leur provenance et leur intention ne sont pas déduites par cet audit.

### Limites

- Aucun environnement Python 3.13 n'était disponible localement : la compatibilité 3.13 est documentée, mais n'a pas encore fait l'objet d'un smoke test réel.
- Aucun test de charge, test navigateur ou audit dynamique de sécurité n'a été exécuté.
- `npm ls --depth=0` n'a pas pu être exploité, car l'installation locale de npm est incomplète. Ce résultat ne prouve pas un défaut des paquets du projet.
- L'audit RGPD est technique et organisationnel ; il ne remplace pas la validation d'un DPO ou d'un juriste.

## 3. Vue d'ensemble du projet

### Fonctionnalités observées

- annuaire public avec recherche et filtres ;
- fiche détaillée d'une structure ;
- carte Leaflet/OpenStreetMap ;
- authentification par adresse email et réinitialisation du mot de passe ;
- tableau de bord réservé aux superutilisateurs ;
- gestion des structures, communes, types et utilisateurs ;
- import CSV/XLSX ;
- journal d'activité ;
- opérations groupées de suppression.

### Architecture

| Composant | Responsabilité principale |
|---|---|
| `app` | settings, routes racine, WSGI et ASGI |
| `home` | page d'accueil et statistiques publiques |
| `communes` | modèle et administration des communes |
| `structures` | cœur métier, vues publiques, dashboard, import et audit |
| `authentication` | connexion par email et déconnexion |
| `templates` / `static` | interface publique et dashboard |

Le projet contient 227 fichiers suivis par Git, environ 2 313 lignes Python et 3 837 lignes de templates HTML. La base locale observée contient 37 structures, 7 communes, 3 types, 1 utilisateur et aucun enregistrement de journal d'audit.

### Dépendances installées localement

| Dépendance | Version observée |
|---|---:|
| Python | 3.14.6 |
| Django | 6.0.7 |
| django-ratelimit | 4.1.0 |
| openpyxl | 3.1.5 |
| python-decouple | 3.8 |
| asgiref | 3.12.1 |
| sqlparse | 0.5.5 |

Le frontend déclare Tailwind CSS et son CLI en version `^4.3.3` dans `package.json`.

## 4. Résultats des vérifications

| Vérification | Résultat | Interprétation |
|---|---|---|
| `python manage.py check` | Réussi, 2 contrôles masqués | Aucun problème Django standard hors contrôles volontairement ignorés |
| `python manage.py check --deploy` | 6 avertissements | Configuration locale en `DEBUG=True`, secret local faible et sécurités HTTPS inactives dans ce mode |
| `python manage.py test` | 0 test découvert | Aucun filet de régression automatisé |
| `makemigrations --check --dry-run` | Aucun changement | Modèles et migrations sont synchronisés |
| `pip check` | Réussi | Pas de dépendance Python cassée dans l'environnement local |
| `compileall` | Réussi | Les modules Python analysés se compilent |
| `collectstatic --dry-run --noinput` | Échec | `STATIC_ROOT` n'est pas défini |
| `npm ls --depth=0` | Non concluant | npm local ne trouve pas son propre module CLI |

Les six avertissements de `check --deploy` ne prouvent pas que la future production utilisera ces valeurs : la commande a lu le fichier `.env` local. Ils démontrent cependant qu'il n'existe pas encore de configuration de production distincte et testable. Le contrôle devra être relancé avec les vraies variables de production, sans jamais afficher leurs valeurs.

## 5. Points positifs confirmés

- `SECRET_KEY`, `DEBUG` et `ALLOWED_HOSTS` sont lus depuis l'environnement ; `.env` est ignoré par Git.
- `DEBUG` vaut `False` par défaut si la variable est absente.
- `SecurityMiddleware`, la protection CSRF, les sessions, l'authentification et la protection anti-clickjacking sont actives.
- Les formulaires POST observés contiennent un jeton CSRF et la déconnexion exige POST.
- Le dashboard est protégé par un contrôle `is_superuser` côté serveur.
- La liste publique et la liste des structures du dashboard sont paginées.
- Les vues de liste, détail et carte utilisent `select_related("type", "commune")`, ce qui évite les N+1 évidents sur ces relations.
- Les recherches passent par l'ORM Django ; aucun SQL brut construit depuis une saisie n'a été observé.
- Les migrations sont présentes et synchronisées avec les modèles.
- L'import impose une taille maximale de 10 Mo et une liste d'extensions autorisées.
- Les mots de passe sont enregistrés avec `set_password()` et non en clair.
- Les dépendances Python actuellement installées sont cohérentes selon `pip check`.

## 6. Constats bloquants avant mise en ligne

### B1 — Installation Python non reproductible

**Preuve.** Le README demande `pip install -r requirements.txt`, mais le dépôt ne contient ni `requirements.txt`, ni `pyproject.toml`, ni lockfile Python.

**Impact.** o2switch ne peut pas reconstruire de façon fiable l'environnement. Une installation manuelle risque de récupérer des versions différentes de celles auditées.

**Action requise.** Ajouter une source de dépendances versionnée et compatible Python 3.13. Les versions directes doivent être épinglées ou verrouillées selon l'outil choisi. Tester l'installation dans un environnement Python 3.13 vierge.

### B2 — Chaîne de fichiers statiques inutilisable depuis Git

**Preuves.** `collectstatic --dry-run` échoue faute de `STATIC_ROOT`. `static/css/app.min.css` et `static/js/bundle.min.js` existent localement mais sont ignorés par Git alors que les templates les référencent. `static/css/tailwind.css` est absent, et le fichier d'entrée attendu par `build_assets.py`, `static/css/tailwind_input.css`, n'est pas présent dans le dépôt observé.

**Impact.** Un déploiement construit depuis Git peut servir des pages sans le design attendu ou échouer lors de la préparation des statiques.

**Action requise.** Définir une stratégie unique : sources frontend versionnées, build reproductible, artefacts inclus dans l'artefact de release, puis `collectstatic` vers un `STATIC_ROOT` persistant et servi par la configuration o2switch. Ne pas dépendre du CDN Tailwind de développement en production.

### B3 — Données personnelles réelles dans les données de démonstration

**Preuve.** `structures/management/commands/seed_data.py` est suivi par Git et contient des noms, adresses, emails et numéros de téléphone permettant d'identifier des personnes physiques.

**Impact.** Ces données sont copiées avec chaque clone et peuvent rester dans l'historique Git même après suppression du fichier courant. Des coordonnées professionnelles peuvent rester des données personnelles au sens du RGPD.

**Action requise.** Remplacer les données par un jeu entièrement fictif, documenter la provenance et la finalité des vraies données de production, puis évaluer si l'historique Git a été partagé. Si nécessaire, planifier un nettoyage d'historique et traiter les anciennes données comme potentiellement exposées. Une validation DPO/juridique est recommandée avant publication de données nominatives.

### B4 — L'import peut supprimer la base puis laisser un état partiel

**Preuve.** Dans `DashboardImportView.post()`, l'option « écraser » supprime toutes les structures avant le bloc `try`. L'import suivant n'est pas entouré d'une transaction atomique et crée les objets ligne par ligne.

**Impact.** Une erreur de décodage, un classeur invalide, une valeur inattendue ou une interruption Passenger peut laisser la table vide ou partiellement remplie. Le risque est amplifié avec SQLite et un hébergement mutualisé où les requêtes longues peuvent être interrompues.

**Action requise.** Valider le fichier avant toute suppression, exécuter suppression et import dans une transaction unique, présenter un bilan des lignes rejetées et conserver les données précédentes si l'import échoue. Effectuer une sauvegarde cohérente avant tout import destructif.

### B5 — Absence totale de tests automatisés

**Preuve.** Django découvre zéro test, bien que trois modules `tests.py` existent.

**Impact.** Les flux critiques — permissions, import destructif, création d'utilisateur, audit, visibilité publique et authentification — peuvent régresser sans détection.

**Action requise.** Ajouter avant mise en ligne un socle ciblé couvrant au minimum : refus d'accès au dashboard, création et modification d'une structure, import réussi/échoué/atomique, création d'utilisateur avec validation du mot de passe, journal d'audit, visibilité `afficher=False` et pages publiques principales.

## 7. Constats importants

### I1 — Version Python locale absente d'o2switch

Le projet est développé sous Python 3.14.6. La documentation o2switch consultée annonce des exécutables jusqu'à Python 3.13, tandis que Django 6.0 accepte officiellement Python 3.12 à 3.14.

**Recommandation.** Épingler Python 3.13 pour le déploiement et pour au moins un environnement de test local ou CI. Il s'agit d'un écart d'environnement, pas d'une incompatibilité connue de Django.

### I2 — Aucune procédure Passenger/WSGI

`app/wsgi.py` existe et expose bien `application`, mais aucun runbook n'indique la racine de l'application, le fichier de démarrage, les variables, l'installation, les migrations, les statiques, le redémarrage ou les smoke tests.

**Recommandation.** Documenter l'utilisation de « Setup Python App » avec Python 3.13, `app/wsgi.py` comme fichier de démarrage et `application` comme point d'entrée. Conserver le code et la base persistante hors d'un répertoire web publiquement listable.

### I3 — La date monenfant.fr importée est perdue

`_create_structure()` passe la date importée à `date_mise_a_jour`, champ `auto_now=True`, au lieu de `date_mise_a_jour_monenfant`. Django remplace cette valeur lors de l'enregistrement.

**Impact.** L'indicateur de fraîcheur monenfant.fr ne reflète pas le fichier importé.

**Recommandation.** Affecter la date au bon champ et couvrir les formats acceptés, les dates invalides et l'absence de date par des tests.

### I4 — Le journal d'audit n'enregistre pas les modifications

Le signal `post_save` relit la structure après sa sauvegarde. L'« ancienne » ligne est donc déjà identique à la nouvelle, ce qui produit aucun changement et empêche la création du journal de modification.

Par ailleurs, `DashboardStructureDeleteView` surcharge `delete()`, mais le POST de `DeleteView` appelle directement `form_valid()` puis `self.object.delete()` avec Django 6.0. L'utilisateur n'est donc pas attaché à l'objet lors d'une suppression normale et le journal reçoit `user=None`.

**Recommandation.** Capturer l'état précédent avant l'écriture ou centraliser la mutation dans un service explicite et transactionnel. Affecter l'acteur dans le chemin POST réellement exécuté. Définir une rétention pour les journaux, car `changes` peut contenir d'anciennes données personnelles.

### I5 — Création d'utilisateur fragile et mots de passe insuffisamment validés

Le champ `password` est écrit manuellement dans le template mais n'appartient pas au `ModelForm`. Si sa valeur manque, `form.add_error("password", ...)` cible un champ inexistant et peut provoquer une erreur serveur. Lorsqu'il est fourni, `set_password()` le chiffre correctement, mais les validateurs configurés dans `AUTH_PASSWORD_VALIDATORS` ne sont pas appelés.

**Recommandation.** Utiliser un formulaire dédié basé sur les mécanismes Django de création d'utilisateur, avec confirmation et validation du mot de passe. Empêcher la suppression ou la désactivation accidentelle du dernier superutilisateur actif.

### I6 — L'authentification par email suppose une unicité non garantie

`EmailBackend` utilise `.get(email=username)` alors que le modèle utilisateur Django par défaut ne garantit pas l'unicité de l'email. Des doublons créés par un autre chemin, notamment l'admin Django, provoqueraient `MultipleObjectsReturned` et une erreur de connexion.

**Recommandation.** Garantir l'unicité normalisée de l'email au niveau du modèle et de la base, ou adopter un modèle utilisateur personnalisé avant que la base ne devienne difficile à migrer.

### I7 — Limitation de débit locale à chaque processus

Les caches `default` et `ratelimit` utilisent `LocMemCache`. Chaque processus Passenger maintient son propre compteur : la limite de 10 connexions par minute n'est donc pas globale. Les contrôles `django_ratelimit.E003` et `django_ratelimit.W001` sont masqués.

**Recommandation.** Utiliser l'instance Redis privée proposée par o2switch comme cache partagé, réactiver les contrôles et tester le comportement en cas d'indisponibilité. Étendre une protection proportionnée au mot de passe oublié avant d'activer le SMTP.

### I8 — Risque XSS dans la carte et HTML marqué sûr

La carte injecte `structures_json` avec `|safe`, puis construit des fragments via concaténation HTML. Certains champs sont échappés en Python, mais `code_postal` ne l'est pas. Un classeur importé est une source externe et ne doit pas être considéré comme fiable uniquement parce que l'import est réservé à un superutilisateur.

**Recommandation.** Utiliser `json_script` pour transporter les données et construire les éléments avec des APIs DOM sûres ou échapper chaque valeur dans son contexte. Réexaminer également les usages de `mark_safe()` dans les liens de tri.

### I9 — Dépendances frontend tierces en production

Les pages chargent Tailwind depuis `cdn.tailwindcss.com`, Inter depuis Google Fonts, Leaflet depuis unpkg, Chart.js depuis jsDelivr et les tuiles depuis OpenStreetMap. Les scripts n'utilisent pas d'intégrité SRI et les connexions transmettent au minimum des métadonnées réseau aux tiers.

**Recommandation.** Compiler Tailwind, héberger localement les bibliothèques et la police lorsque les licences le permettent, puis préparer une Content Security Policy. Pour les tuiles cartographiques, documenter le fournisseur, sa politique d'usage et l'information des visiteurs ; ne pas mettre en place un proxy de tuiles sans vérifier les conditions du service.

### I10 — SMTP, logs et supervision non préparés

Le backend email par défaut écrit dans la console. En production, le mot de passe oublié ne remettra donc pas réellement l'email à l'utilisateur tant que le SMTP n'est pas configuré. Aucune configuration applicative de logs, rotation, alerte ou health check n'est présente.

**Recommandation.** Configurer un compte SMTP transactionnel par variables d'environnement, tester les URLs HTTPS des emails et empêcher les secrets/tokens d'apparaître dans les logs. Définir le fichier de log Passenger, une rotation, une vérification HTTP et une alerte simple d'indisponibilité.

### I11 — Effet de bord pendant la validation du formulaire Structure

`StructureForm.clean()` crée immédiatement un nouveau `TypeStructure` avec `get_or_create()`. Si un autre champ rend ensuite le formulaire invalide, ce type peut rester en base sans structure associée.

**Recommandation.** Différer la création jusqu'à la sauvegarde réussie, dans la même transaction que la structure.

## 8. Améliorations recommandées

- Séparer explicitement les configurations développement, test et production, ou fournir au minimum un module de production contrôlable indépendamment du `.env` local.
- Ajouter un `.env.example` sans secret, décrivant toutes les variables obligatoires.
- Régler `LANGUAGE_CODE` et `TIME_ZONE` selon l'usage français réel ; conserver UTC en stockage reste approprié.
- Déployer HSTS progressivement. La configuration actuelle active directement un an, les sous-domaines et le préchargement lorsque `DEBUG=False`, ce qui est risqué avant validation HTTPS de tous les sous-domaines.
- Ne pas afficher directement le texte brut d'une exception d'import, même au dashboard ; journaliser le détail et présenter un message contrôlé.
- Fermer explicitement les classeurs `openpyxl` et éviter de convertir un grand classeur complet en liste en mémoire.
- Ajouter des contraintes métier cohérentes : âge minimum inférieur ou égal à l'âge maximum, places disponibles inférieures ou égales à la capacité, états de disponibilité non contradictoires.
- Versionner `package-lock.json` ou adopter une autre source de vérité unique pour les dépendances Node.
- Ajouter une CI légère sous Python 3.13 : installation vierge, checks, migrations, tests et build des statiques.
- Ajouter des annotations de type aux fonctions publiques et nettoyer les imports inutilisés, sans lancer un refactoring global uniquement stylistique.

## 9. Performance et choix SQLite

### État actuel

Aucun problème N+1 critique n'a été validé sur les vues publiques inspectées. La liste publique est paginée à 20 éléments et précharge `type` et `commune`. La page d'accueil borne les structures récentes à trois. Le dashboard est une zone froide réservée au superutilisateur.

La carte charge toutes les structures géolocalisées dans une seule réponse. Avec 37 structures, cela reste raisonnable. Ce point devient conditionnellement problématique si le nombre de marqueurs atteint plusieurs milliers : taille HTML/JSON, mémoire du worker et performances du navigateur augmenteraient ensemble.

### Garde-fous obligatoires pour SQLite

- Conserver le fichier SQLite sur un stockage persistant et inscriptible, distinct des artefacts de release si une stratégie de releases est adoptée.
- Éviter les imports ou traitements longs dans une requête web ; à court terme, les rendre atomiques et bornés.
- Limiter le nombre d'administrateurs effectuant des écritures simultanées.
- Surveiller les erreurs `database is locked`, les temps de réponse et les redémarrages Passenger.
- Ne pas copier naïvement le fichier pendant une écriture pour fabriquer une sauvegarde.
- Tester la restauration avec la même version applicative et les migrations attendues.

### Seuils de réévaluation vers MariaDB

Déclencher une étude de migration si l'un des événements suivants apparaît :

- erreurs de verrouillage SQLite répétées ;
- plusieurs administrateurs écrivent simultanément de façon régulière ;
- imports fréquents ou volumineux ;
- besoin de workers/tâches écrivant en parallèle ;
- indisponibilité acceptable très courte ou restauration plus industrialisée ;
- croissance importante du volume et des filtres ;
- besoin de déployer plusieurs instances applicatives.

Sur o2switch, MariaDB/MySQL est mieux intégré à cPanel que PostgreSQL. La documentation o2switch avertit que sa version PostgreSQL est ancienne et susceptible d'être retirée ; PostgreSQL n'est donc pas recommandé pour cette cible précise malgré la recommandation générale de Django.

## 10. Sauvegarde et restauration SQLite

JetBackup fournit des sauvegardes régulières des fichiers o2switch, mais o2switch précise que ces archives ne remplacent pas une politique propre. Pour SQLite, une simple copie du fichier à un instant arbitraire n'est pas une preuve de cohérence.

### Politique proposée pour la démonstration

- **RPO proposé :** 24 heures au maximum de données perdues.
- **RTO proposé :** restauration manuelle dans la demi-journée.
- sauvegarde quotidienne cohérente via l'API de sauvegarde SQLite ou une procédure mettant les écritures en pause ;
- conservation d'au moins 7 quotidiennes et 4 hebdomadaires, à ajuster au volume ;
- une copie hors du compte o2switch, chiffrée si elle contient des données personnelles ;
- vérification de présence, taille et checksum ;
- alerte si la dernière sauvegarde réussie dépasse 26 heures ;
- test de restauration initial, après changement de stratégie, puis au moins trimestriel pour ce niveau de criticité.

Ces valeurs sont des objectifs proposés et doivent être validées par le responsable du service.

### Test de restauration minimal

1. Préparer un répertoire et une base temporaires hors production.
2. Restaurer la copie SQLite sans écraser la production.
3. Utiliser le code correspondant à la date de la sauvegarde.
4. Exécuter les migrations nécessaires, puis `manage.py check`.
5. Vérifier les nombres d'objets attendus et quelques enregistrements représentatifs.
6. Tester accueil, liste, détail, connexion et lecture du dashboard.
7. Neutraliser tout envoi d'email externe dans l'environnement de test.
8. Consigner la date, le résultat, le checksum et la durée ; supprimer ensuite les données temporaires.

### Restauration après incident

1. Limiter ou arrêter les écritures via l'application Passenger.
2. Conserver une copie de l'état défaillant pour analyse lorsque possible.
3. Choisir explicitement la sauvegarde et la version de code compatibles.
4. Restaurer dans une cible contrôlée, jamais par une commande supposant implicitement la production.
5. Exécuter checks et smoke tests.
6. Redémarrer Passenger et surveiller les logs.
7. Invalider les sessions ou secrets si l'incident était lié à la sécurité.

## 11. Feuille de route priorisée

### P0 — Avant toute mise en ligne publique

- [ ] Remplacer les données personnelles de `seed_data.py` par des données fictives et évaluer l'historique Git.
- [ ] Créer un manifeste Python reproductible pour Python 3.13 et valider une installation vierge.
- [ ] Réparer la chaîne frontend, définir `STATIC_ROOT` et valider `collectstatic` depuis un clone propre.
- [ ] Créer une configuration de production documentée : `DEBUG=False`, secret fort, hôtes explicites, HTTPS, cookies et origines CSRF.
- [ ] Rendre l'import atomique, valider avant suppression et corriger `date_mise_a_jour_monenfant`.
- [ ] Corriger la création des utilisateurs, l'unicité de l'email et la validation des mots de passe.
- [ ] Corriger le journal d'audit des modifications et suppressions.
- [ ] Ajouter les tests de sécurité et d'intégrité listés en B5.
- [ ] Définir, automatiser et tester une sauvegarde/restauration SQLite.
- [ ] Écrire et tester le runbook Passenger/WSGI et le retour arrière.

### P1 — Premières semaines d'exploitation

- [ ] Activer Redis o2switch comme cache partagé et retirer les contrôles `django-ratelimit` masqués.
- [ ] Configurer SMTP, logs, rotation, health check et alerte d'indisponibilité.
- [ ] Supprimer les constructions HTML risquées de la carte et ajouter les tests XSS pertinents.
- [ ] Auto-héberger les dépendances frontend possibles et préparer une CSP compatible.
- [ ] Documenter finalités, accès, rétention, sous-traitants et mentions de confidentialité ; faire valider les aspects juridiques.
- [ ] Mettre en place une CI Python 3.13 incluant tests et build des statiques.

### P2 — Maintenabilité et évolution

- [ ] Séparer clairement les settings développement/test/production.
- [ ] Renforcer les contraintes métier et la validation des imports.
- [ ] Ajouter une stratégie de monitoring des performances et des erreurs SQLite.
- [ ] Réexaminer MariaDB selon les seuils définis plus haut.
- [ ] Améliorer progressivement typage, journalisation et découpage du module dashboard.

## 12. Checklist de déploiement o2switch

Cette checklist décrit la cible, pas l'état actuellement disponible. Les éléments P0 doivent être corrigés avant de l'exécuter.

### Avant le déploiement

- [ ] Partir d'un commit identifié et d'un arbre Git sans modifications inexpliquées.
- [ ] Vérifier qu'aucun secret ni donnée personnelle de démonstration ne part dans l'artefact.
- [ ] Installer et tester localement sous Python 3.13 depuis le manifeste versionné.
- [ ] Construire les ressources frontend de manière reproductible.
- [ ] Exécuter checks, migrations en mode vérification, tests et `collectstatic` de validation.
- [ ] Vérifier une sauvegarde cohérente récente et une procédure de restauration déjà testée.
- [ ] Préparer une procédure de rollback du code ; ne pas confondre rollback du code et rollback de la base.

### Création de l'application cPanel

- [ ] Créer l'application dans « Setup Python App » avec Python 3.13.
- [ ] Définir la racine de l'application dans un répertoire non destiné à exposer directement les sources.
- [ ] Configurer `app/wsgi.py` comme fichier de démarrage et `application` comme point d'entrée.
- [ ] Activer l'environnement virtuel fourni par cPanel.
- [ ] Installer uniquement les dépendances du manifeste versionné.
- [ ] Définir un chemin de log Passenger accessible et soumis à rotation.

### Variables de production

- [ ] `SECRET_KEY` : valeur forte, unique et non versionnée.
- [ ] `DEBUG=False`.
- [ ] `ALLOWED_HOSTS` : domaine(s) explicite(s), jamais `*`.
- [ ] Origines CSRF HTTPS explicites si la configuration finale les nécessite.
- [ ] Paramètres SMTP et adresse d'expéditeur.
- [ ] Chemin persistant du fichier SQLite si le code est adapté pour le configurer.
- [ ] Paramètres Redis distincts et secret stocké uniquement dans l'environnement.
- [ ] Aucune vraie valeur secrète dans le README, les commandes copiées ou les logs.

### Initialisation

- [ ] Exécuter `python manage.py check` avec les variables de production.
- [ ] Exécuter `python manage.py check --deploy` et analyser chaque avertissement.
- [ ] Exécuter `python manage.py migrate` après sauvegarde et revue des migrations.
- [ ] Exécuter `python manage.py collectstatic --noinput` vers `STATIC_ROOT`.
- [ ] Créer un compte administrateur individuel avec un mot de passe robuste ; ne pas partager le compte.
- [ ] Configurer le domaine et le certificat HTTPS o2switch.
- [ ] Tester la détection HTTPS derrière Passenger avant d'activer HSTS progressivement.
- [ ] Redémarrer l'application depuis cPanel.

### Smoke tests après déploiement

- [ ] Accueil, liste, filtres, pagination, détail et carte répondent en HTTPS.
- [ ] CSS, JavaScript, SVG et polices sont servis sans erreur 404.
- [ ] Une structure masquée n'est pas accessible publiquement.
- [ ] Connexion, déconnexion POST et reset du mot de passe fonctionnent.
- [ ] Un utilisateur anonyme et un utilisateur non superuser ne peuvent pas accéder au dashboard.
- [ ] Création, modification et suppression d'une structure produisent les journaux attendus.
- [ ] Un petit import non destructif réussit ; un import invalide ne modifie aucune donnée.
- [ ] Le cache Redis et la limitation de débit sont partagés entre processus.
- [ ] Les logs ne contiennent ni secret, ni mot de passe, ni token de réinitialisation.
- [ ] La sauvegarde post-déploiement est créée et vérifiée.

### Retour arrière

- [ ] Arrêter le déploiement si installation, migration, statiques ou smoke tests échouent.
- [ ] Conserver les logs et l'identifiant de la release en échec.
- [ ] Revenir à la release précédente identifiée.
- [ ] Ne restaurer la base que si la migration ou les données l'exigent et après décision humaine explicite.
- [ ] Relancer Passenger, refaire les smoke tests et surveiller les erreurs.

## 13. Références officielles

- [Déployer une application Python sur o2switch](https://faq.o2switch.fr/cpanel/logiciels/hebergement-python-multi-version/)
- [Versions de Python disponibles chez o2switch](https://faq.o2switch.fr/guides/langages-supportes-php-node-ruby-python/)
- [Bases de données proposées par o2switch](https://faq.o2switch.fr/cpanel/bases-de-donnees/)
- [Avertissement o2switch relatif à PostgreSQL](https://faq.o2switch.fr/cpanel/bases-de-donnees/postgresql/)
- [Instance Redis privée o2switch](https://faq.o2switch.fr/cpanel/o2switch/redis/)
- [Restauration avec JetBackup](https://faq.o2switch.fr/cpanel/fichiers/sauvegarde-jetbackup/)
- [Suivi CPU, mémoire et I/O o2switch](https://faq.o2switch.fr/cpanel/mesures/suivi-usage-ressources/)
- [Compatibilité Python de Django 6.0](https://docs.djangoproject.com/fr/6.0/faq/install/)
- [Checklist de déploiement Django](https://docs.djangoproject.com/fr/6.0/howto/deployment/checklist/)

## 14. Conclusion

Le projet est suffisamment simple pour une première exploitation o2switch en Python 3.13 avec SQLite, et son architecture publique ne présente pas de défaut de performance majeur à son volume actuel. La mise en ligne doit toutefois attendre la résolution des P0 : reproductibilité des dépendances, statiques, retrait des données personnelles du dépôt, intégrité de l'import, correction des comptes et de l'audit, tests minimaux et sauvegarde restaurable.

Après ces corrections, l'offre mutualisée o2switch est cohérente avec l'usage faible/démonstration retenu. Le premier signal de croissance à surveiller n'est pas le nombre de lectures publiques, mais la concurrence des écritures administratives et les erreurs de verrouillage SQLite.
