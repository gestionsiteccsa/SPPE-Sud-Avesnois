# Changelog

## Non publié

### Modifié

- campagnes : le lancement, la relance, le passage en réel et la génération des courriers créent ou mettent à jour les invitations **en une seule opération groupée** (`bulk_create`/`bulk_update`) au lieu d'une écriture par fiche — une campagne de 200 fiches passe d'environ 1 600 à moins de 10 requêtes ; chaque opération consigne désormais **une entrée résumée** dans le journal d'audit (action « groupée ») au lieu d'une entrée par invitation.
- campagnes : le compteur d'ouvertures de la page publique est incrémenté directement en base (`F()` + mise à jour ciblée), supprimant toute perte d'incrément en cas d'ouvertures simultanées et les entrées d'audit associées ; la transition vers « consulté » reste appliquée.
- file de validation : liste paginée (25 demandes par page) au lieu du chargement intégral de l'historique ; les compteurs affichés par catégorie restent globaux grâce à un comptage SQL dédié.
- import CSV/XLSX avec option « remplacer » : la suppression préalable des fiches n'écrit plus une entrée d'audit par fiche (signaux suspendus pendant l'opération) ; une entrée résumée « Remplacement des données » est ajoutée, et les fiches créées restent journalisées individuellement.
- décision d'une demande d'inscription : écritures et entrée de journal regroupées dans une transaction unique ; l'e-mail de décision part après le commit (un incident SMTP ne laisse plus d'état incohérent ni de journal manquant).
- admin Django : pages liste des invitations, demandes de mise à jour et structures optimisées (`select_related` sur campagne/fiche/type/commune/relecteur), supprimant jusqu'à ~400 requêtes par page.
- formulaire de structure : le contrôle anti-doublon dans une commune charge uniquement les colonnes utiles (nom/prénom) au lieu d'instancier toutes les fiches de la commune.
- import CSV/XLSX optimisé : l'audit par structure créée est conservé mais les performances sont améliorées. Les types et communes sont résolus via un cache en mémoire (au lieu d'une requête par ligne), les doublons (y compris intra-fichier, insensibles à la casse et aux accents) sont détectés par une requête unique par commune et les fiches sont créées par lots (`bulk_create`) ; les contraintes restent validées pendant la préparation et toute violation de contrainte est signalée proprement.
- campagnes : les envois d'e-mails (lancement, relance, passage en réel) sont désormais effectués hors de la transaction de base de données afin de ne pas maintenir une transaction ouverte pendant toute la durée des envois ; le statut « erreur d'envoi » reste conservé par fiche. Le lancement est refusé si la date du jour est hors de la période de la campagne.
- file de validation : le sélecteur « Fiche concernée » de la saisie assistée est borné aux 500 invitations les plus récentes (message indiquant le nombre total), la validation serveur restant complète.
- menu du tableau de bord : le lien « File de validation » est désormais visible pour les collaborateurs actifs (l'accès leur était déjà ouvert), seul « Campagnes » reste réservé aux superadmins.
- détail d'une campagne : indication du nombre total de fiches correspondant au filtre lorsqu'il dépasse les 200 affichées ; requête de préchargement inutile supprimée.
- page publique de vérification : confirmation avant l'envoi d'une demande « arrêt d'activité » ou « fiche ne me concerne pas » (actions définitives).
- page d'import : la colonne « Tranche d'âge » est documentée comme obligatoire (« non renseigné » accepté) et le message d'erreur est adapté au contexte d'import.
- journal d'audit : les champs proposés lors d'une demande de modification sont désormais journalisés explicitement (création par lots ne déclenchant pas les signaux).
- fiches existantes sans tranche d'âge : migration de données les marquant « âge non renseigné » pour rester modifiables.

### Corrigé

- tableau de bord : la liste des structures et l'accueil sont désormais bornés aux communes liées du collaborateur (comme la création, la modification et la suppression), ce qui supprime l'exposition des fiches hors périmètre et des statistiques territoriales complètes.
- annuaire et tableau de bord : les filtres `commune` / `type` et l'action groupée ignorent les valeurs non numériques (un paramètre `?commune=abc` ne provoque plus d'erreur 500).
- file de validation : le compteur « + N autre(s) champ(s) » utilise désormais la relation préchargée au lieu d'un `COUNT` par demande affichée.
- build frontend : le JavaScript est réellement minifié via esbuild (`bundle.min.js` passe d'environ 13,8 à 6,6 Ko) ; le sélecteur d'horaires est compilé en `timeslider.min.js` / `timeslider.min.css` servis par le formulaire, esbuild ayant été ajouté aux dépendances de développement.
- tests : l'assertion des en-têtes de sécurité production ne dépend plus des options HSTS locales de l'environnement.
- formulaire de fiche : la valeur « 0 » des champs numériques (âge minimum, places disponibles, nombre de places total, nombre de professionnel·les) disparaissait à l'affichage en modification à cause du filtre `default` qui efface toute valeur falsy ; remplacé par `default_if_none`.
- formulaire de fiche : la case « Afficher sur le site » apparaissait cochée même pour une fiche masquée (`False|default:True`), risquant de republier involontairement une fiche masquée lors d'une simple modification ; l'état réel de la fiche est désormais respecté.

### Ajouté

- signalements : bouton fixe « Signaler un bug » sur tout le site (utilisateurs connectés) ouvrant une modale accessible (`<dialog>`, page pré-remplie modifiable, envoi JSON avec repli sans JS) ; stockage en base (`feedback.FeedbackReport`, statuts nouveau/en cours/résolu), email aux `DestinataireNotification` actifs et administration Django dédiée.
- signalements : email de notification mis en page (pastille couleur par type, tableau auteur/pages/message, bouton vers l'admin) avec version texte conservée.
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
- index SQLite sur `timestamp` du journal d'activité (tri décroissant permanent et filtre de purge sans scan complet).
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
- pages d'erreur personnalisées aux couleurs du site : 404 (page introuvable), 403 (accès refusé), 400 (requête invalide) et 500 (erreur interne, page autonome pour rester affichable même en cas de panne).
- campagnes de mise à jour annuelle des assistantes maternelles : création et lancement d'une campagne (dates, statuts brouillon/en cours/clôturée/archivée), invitation par fiche avec jeton personnel aléatoire stocké haché (jamais d'identifiant de fiche dans l'URL), envoi du lien par e-mail ou courrier imprimable avec code, page publique de vérification sans compte (`/verification/<jeton>/`, CSRF, limitation de débit, lecture seule après soumission), confirmation ou proposition de modification sans application directe, file de validation champ par champ (superadmins et collaborateurs limités à leurs communes), saisie assistée par un agent (téléphone ou accueil), relance des non-répondants, clôture avec passage en « expiré », résumé et statistiques de campagne, journalisation dans l'audit.
- mode test des campagnes : adresses e-mail de test saisies par campagne (2-3, validées), lancement et relance envoyés uniquement à ces adresses (sujet préfixé `[TEST]`, aucune adresse réelle jamais utilisée), bandeau « Mode test » dans le tableau de bord et bouton « Passer en réel » (jetons régénérés, envois aux vraies adresses, invitations courrier repassées en « non contacté ») ; bouton « Lancer en mode test » avec saisie des adresses directement sur la page d'une campagne en brouillon.
- carte des structures : sélecteur de fond « Plan » (OpenStreetMap, par défaut) / « Satellite » (Esri World Imagery) avec attributions conservées et politique CSP étendue aux tuiles Esri.
- carte des structures : filtre par disponibilité (« Tout », « Disponible », « Complet », « Non communiqué ») appliqué instantanément aux marqueurs, avec annonce du nombre affiché et bouton « Recentrer » adapté au filtre actif.
- géocodage des adresses : Base Adresse Nationale en premier puis Nominatim en repli, aide à la saisie dans le formulaire (suggestions + mini-carte OpenStreetMap de contrôle, boutons « Re-vérifier » / « Effacer »), proxy dashboard `/tableau-de-bord/adresses/suggestions/` limité en débit, commande `geocode_structures` avec filtre latitude/longitude manquante et export `--export-ko` des introuvables.

### Modifié

- page « File de validation » des campagnes repensée : toutes les demandes soumises affichées par défaut et regroupées en sections par catégorie (modification, arrêt d'activité, fiche ne me concerne pas, confirmations), filtres par catégorie, statut, campagne et recherche par nom, tableau avec comparatif « Avant → Après » par champ modifié, statuts en badges et informations de traitement (date, agent, commentaire) ;

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
- affichage des erreurs de validation du formulaire de structure : résumé global en tête de formulaire et messages sous les champs concernés (auparavant, seules les erreurs du champ « nom » étaient visibles) ;
- formulaire de fiche : bloc « Accueil spécifique » en colonne de droite sous « Tranche d'âge » ; « Adresse & Contact » en pleine largeur avec « Capacité d'accueil » et « Informations de gestion » côte à côte en dessous.
- conservation de la commune et du type sélectionnés après une erreur de validation du formulaire de structure.
- formulaire de fiche : emails minuscules sans espaces superflus ; téléphones français validés et normalisés au format national (`01 23 45 67 89`, `+33`/`0033` acceptés).
- build des ressources : un échec d'esbuild affiche désormais son message d'erreur (plus de log aveugle en CI) avec un contrôle préalable du binaire dans le workflow qualité.
- build des ressources : le lanceur esbuild détecte si `bin/esbuild` est le shim JS ou le binaire natif installé par le postinstall (exécution directe dans ce cas), corrigeant l'échec CI `SyntaxError: Invalid or unexpected token` sur le fichier ELF.
- build des ressources : sorties strictement reproductibles entre Windows et Linux (normalisation LF des copies vendor, stdin binaire pour esbuild, écritures LF, `.gitattributes`), corrigeant l'échec CI `git diff --exit-code -- static` sur `leaflet.css` (CRLF livré par npm) et les `min.js`.
- CI : variable `BACKUP_DIR` fournie au contrôle `check --deploy` (exigée en production depuis la fonction sauvegardes).
- fiche structure : l'adresse n'affiche plus le code postal et la commune en double lorsque l'adresse saisie les contient déjà (comparaison insensible à la casse et aux accents) ; le bloc adresse est masqué s'il est vide.
- formulaire de fiche : placement manuel du point sur la carte (« Placer le point manuellement », marqueur déplaçable ou clic) avec adresse tapée conservée telle quelle ; le point manuel survit à la frappe, seuls suggestion, « Re-vérifier » ou « Effacer » le remplacent.
- formulaire de fiche : mini-carte d'adresse avec fonds « Plan » / « Satellite » (comme la page carte) et hauteur doublée pour viser juste.
- tests : le test de limitation de connexion fige l'horloge vue par django-ratelimit (fenêtres ancrées au temps réel, échec aléatoire si la boucle chevauchait une frontière de minute sur runner chargé).

### Sécurité

- transport des données cartographiques par `json_script` et échappement du HTML dynamique ;
- protection du dernier superutilisateur actif ;
- échec fermé de l'authentification si des emails dupliqués existent ;
- contraintes de cohérence et de valeurs positives ajoutées à SQLite ;
- CSP stricte `script-src 'self' 'nonce-…'` sans `unsafe-inline` ni `unsafe-eval` ;
- rétention du journal d'audit désormais pilotée par une commande dédiée.
