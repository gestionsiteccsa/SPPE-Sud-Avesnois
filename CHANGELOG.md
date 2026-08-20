# Changelog

## Non publié

### Ajouté

- manifeste Python 3.13 reproductible et lockfile npm ;
- configuration Passenger/WSGI, endpoint `/health/` et CI Python 3.13 ;
- commandes de sauvegarde et de vérification SQLite ;
- tests automatisés des imports, comptes, audits, carte, contraintes et sauvegardes ;
- documentation de déploiement, exploitation, frontend et données personnelles ;
- Content Security Policy par nonce (`app.csp`) appliquée aux pages applicatives ;
- chemin d'accès à l'admin Django personnalisable (`ADMIN_URL`) ;
- commande `purge_audit_log` pour appliquer la rétention du journal d'audit ;
- tests des vues publiques (accueil) et du modèle Commune ;
- index SQLite sur `date_mise_a_jour`, `date_mise_a_jour_monenfant` et `(afficher, date_mise_a_jour)` ;
- tests des vues publiques (liste, filtres, détail, carte), du CRUD communes/types, de la suppression groupée, de l'accès au dashboard, de la limitation de connexion et des en-têtes de sécurité.
- page interne authentifiée « Protection des données », non indexable, avec les informations CCSA, les durées de conservation, les droits et les destinataires.
- limitation de débit de la connexion à l'admin Django (par IP et compte) ;
- Content Security Policy appliquée à l'admin Django via une politique assouplie sur les scripts uniquement ;
- blocage de l'indexation par les moteurs de recherche (`robots.txt`, en-tête `X-Robots-Tag` et balise méta `noindex, nofollow`).
- inscription en libre accès des collaborateurs (`/inscription/`, limitée en débit) avec demande en attente de validation par un superadmin, email de notification aux superadmins et emails de décision au collaborateur ;
- file « Demandes d'inscription » dans le tableau de bord avec compteur des demandes en attente et actions Valider / Refuser ;
- association des communes aux collaborateurs depuis la fiche utilisateur (`UserCommune`), colonne « Communes liées » dans la liste des comptes ;
- espace collaborateur : ajout, modification et suppression des structures limités aux communes liées (liste, formulaire et suppression groupée restreints côté serveur), navigation adaptée au rôle et redirection après connexion ;
- paramètre d'environnement `SITE_URL` pour les liens contenus dans les emails.
- lint Python Ruff (`ruff check .`, règles E4/E7/E9/F) ajouté à la CI et aux contrôles locaux, avec dépendances de développement dans `requirements-dev.txt` et configuration `pyproject.toml` ;
- imports inutilisés retirés (`communes/views.py`, `home/admin.py`, `home/models.py`, `structures/views/__init__.py`) et variable morte supprimée dans `dashboard_tags.py`.
- page « Notifications » dans le tableau de bord pour configurer les destinataires des demandes d'inscription : activation et copie cachée (CCI) réglables par adresse, ajout et suppression d'adresses ; en l'absence d'adresse active, les superadmins restent prévenus automatiquement ;
- modèle `DestinataireNotification` administrable dans l'admin Django ;
- email de réinitialisation de mot de passe personnalisé (sujet et contenu en français, lien valable 3 h) ;
- page « Sauvegardes » dans le tableau de bord (superadmins) : sauvegarde manuelle en un clic, vérification d'intégrité et SHA-256, suppression avec confirmation, suivi de fraîcheur (alerte au-delà de 26 h) et rappel de la tâche cron ;
- sauvegardes automatiques sécurisées : répertoire `BACKUP_DIR` (obligatoire en production, distinct de la base et des statiques), rotation `BACKUP_RETENTION` (7 copies par défaut, appliquée après création réussie), verrou anti-concurrence avec récupération des verrous orphelins, vérification d'espace disque avant écriture, validation stricte des noms (anti path traversal, refus des liens symboliques), journal d'audit des créations et suppressions ;
- journal d'activité étendu à l'ensemble des ajouts, modifications et suppressions : communes, types, comptes utilisateurs (avec communes liées), décisions d'inscription, configuration des notifications et changements de mot de passe (jamais le mot de passe lui-même), en plus des structures, des imports, des suppressions groupées et des sauvegardes ;
- page « Journal » enrichie de filtres par action, objet et utilisateur, et d'un libellé lisible pour les actions spéciales (mot de passe modifié, objet créé ou supprimé) ; l'accès reste réservé aux superadmins.
- page « Mon profil » dans le tableau de bord (tous les comptes connectés) pour modifier le prénom, le nom et l'adresse email ; le changement d'email est confirmé par le mot de passe actuel, reste unique et est tracé dans le journal d'audit.
- WhiteNoise (`whitenoise.middleware.WhiteNoiseMiddleware` + `CompressedStaticFilesStorage`) pour servir `/static/` depuis `STATIC_ROOT` en production, sans configuration Apache/Passenger dédiée.

### Modifié

- page « Notifications » réorganisée avec une synthèse de l’envoi, des réglages plus explicites et adaptés au mobile, la conservation des choix après erreur et une confirmation avant le retrait d’une adresse ;
- site fermé : l'accueil, la liste, le détail et la carte des structures exigent désormais la connexion (les pages de connexion, d'inscription et de réinitialisation du mot de passe restent publiques) ;
- périmètre des collaborateurs appliqué aux pages du site (accueil, liste, détail, carte) : seuls les structures et communes liées au compte sont visibles, y compris dans les filtres et les compteurs ; les superadmins conservent l'accès à l'ensemble ;
- menu du tableau de bord limité aux superadmins pour les sections Utilisateurs, Demandes d'inscription, Notifications et Sauvegardes (les liens Notifications et Sauvegardes étaient visibles par tous les comptes connectés).
- tableau de bord enrichi avec les capacités par type et commune, les jours d’ouverture, la fraîcheur des données source et la complétude des fiches ; les statistiques d’offre se limitent aux structures visibles et les répartitions longues sont regroupées sous « Autres » ;
- accueil du tableau de bord recentré sur les actions, les indicateurs utiles et les dernières modifications, avec les trois graphiques de suivi conservés et leurs alternatives textuelles accessibles ;
- gestion des communes et des types améliorée avec recherche, états vides, tableaux adaptés au mobile et confirmations après les opérations ;
- liste des structures du tableau de bord réorganisée pour clarifier la recherche, le tri, les résultats, les actions groupées et la consultation sur mobile ;
- changement de mot de passe rendu plus clair et accessible, avec aide visible, erreurs regroupées, affichage des champs fonctionnel et confirmation après enregistrement ;
- page d'accueil simplifiée autour de la recherche et reformulée pour les professionnel·les qui alimentent l'annuaire et orientent les familles ;
- ressources frontend auto-hébergées et Tailwind construit avant déploiement ;
- configuration de production validée par variables d'environnement, Redis partagé, SMTP et logs ;
- import CSV/XLSX borné, validé et transactionnel ;
- création des comptes avec confirmation et validation du mot de passe ;
- journal d'audit avec valeurs réellement modifiées et acteur correct ;
- journal d'audit étendu aux communes et aux types via des signaux génériques (même mécanisme `from_db` que les structures, sans requête supplémentaire à la modification) ;
- données de démonstration remplacées par des exemples fictifs ;
- journal d'audit optimisé : l'état antérieur est capturé au chargement (`from_db`) au lieu d'une requête supplémentaire à chaque écriture ;
- statistiques publiques et du tableau de bord partagées via un service commun ;
- tableau de bord optimisé : compteurs agrégés et répartition mensuelle en une seule requête groupée (au lieu d'une vingtaine de requêtes) ;
- réglages de sécurité définis inconditionnellement pour rester testables et surchargeables ;
- connexion à l'admin Django restreinte par une limite de débit partagée avec Redis en production.

### Corrigé

- comptage des structures par commune et par type regroupé dans les requêtes de liste afin d’éliminer les requêtes répétées pour chaque ligne ;
- confirmations de suppression des structures rendues explicites et comptage des suppressions groupées limité aux structures réellement supprimées ;
- compatibilité Tailwind v4 des tokens typographiques, de l'ordre des couches CSS et du positionnement de la navigation sur écran large ;
- unicité de l'adresse email appliquée au formulaire d'admin Django ;
- limitation de connexion ciblée par adresse IP et compte pour ne pas bloquer toute une IP partagée ;
- délai de validité des liens de réinitialisation ramené de 24 h à 3 h ;
- template de formulaire public redondant et inutilisé supprimé ;
- envoi réel de l'email de réinitialisation de mot de passe (templates de sujet et de contenu manquants : la demande affichait une erreur serveur).

### Sécurité

- transport des données cartographiques par `json_script` et échappement du HTML dynamique ;
- protection du dernier superutilisateur actif ;
- échec fermé de l'authentification si des emails dupliqués existent ;
- contraintes de cohérence et de valeurs positives ajoutées à SQLite ;
- CSP stricte `script-src 'self' 'nonce-…'` sans `unsafe-inline` ni `unsafe-eval` ;
- rétention du journal d'audit désormais pilotée par une commande dédiée.
