# Tâches projet

Les protections applicatives automatisables de l'audit sont livrées. Les tâches suivantes nécessitent une décision humaine, un compte externe ou une évolution d'architecture.

## P0 — Avant mise en ligne

- [ ] Faire créer et tester l'application Python 3.13 dans cPanel o2switch.
- [ ] Configurer les variables de production, Redis privé, SMTP, domaine, HTTPS et service des statiques.
- [ ] Exécuter le déploiement, les migrations, la sauvegarde initiale et tous les smoke tests documentés.
- [ ] Créer une copie de sauvegarde chiffrée hors du compte o2switch et réaliser un test de restauration consigné.
- [ ] Décider avec les responsables concernés du traitement de l'historique Git contenant d'anciennes données personnelles ; toute réécriture implique coordination et rotation des clones.
- [ ] Faire valider par le responsable de traitement/DPO la page interne « Protection des données », les finalités, la base légale et les durées retenues.
- [ ] Informer les personnes externes dont les coordonnées figurent dans l'annuaire (désormais privé) des accès autorisés et de leurs droits sur ces données.

## P1 — Premières semaines

- [ ] Configurer une sonde externe sur `/health/`, les alertes, la rotation des logs et la surveillance des sauvegardes.
- [ ] Surveiller et consigner les erreurs `database is locked`, la taille de SQLite et la concurrence des écritures.
- [ ] Tester la limitation de connexion entre plusieurs processus Passenger et la panne Redis contrôlée.
- [ ] Valider la durée de rétention du journal d'audit et planifier la commande `purge_audit_log` (cron) ; définir la rétention des logs.
- [ ] Formaliser la suppression des comptes sous 30 jours après la fin d'une habilitation et la révision annuelle des fiches de l'annuaire.

## P2 — Évolution

- [ ] Personnaliser `ADMIN_URL` en production et vérifier l'accès restreint de l'admin Django.
- [ ] Étudier un modèle utilisateur personnalisé si l'email doit devenir une identité unique garantie par la base dans tous les chemins d'administration.
- [ ] Migrer vers MariaDB si les verrouillages se répètent, si plusieurs personnes écrivent régulièrement, si les imports deviennent fréquents, si des tâches écrivent en parallèle ou si plusieurs instances sont nécessaires.
- [ ] Ajouter un suivi d'erreurs externe uniquement après revue des données transmises et de la sous-traitance.

La Content Security Policy par nonce est déjà appliquée aux pages applicatives et à l'admin (politique assouplie sur les scripts pour les templates internes de Django), avec une limitation de débit sur la connexion à l'admin. L'indexation par les moteurs de recherche est bloquée sur tout le site (robots.txt, X-Robots-Tag, méta noindex). Les index SQLite sur les dates et la visibilité, l'optimisation du tableau de bord (agrégats groupés) et les tests des vues publiques, du CRUD, de la limitation de connexion et des en-têtes de sécurité sont livrés. La mise en place de tuiles cartographiques alternatives au fournisseur OpenStreetMap n'est pas prévue à ce stade.

Le flux d'inscription des collaborateurs (demande en attente, validation par un superadmin, communes liées via la fiche utilisateur, gestion des structures bornée aux communes liées) est livré avec ses tests. Les destinataires des notifications de demandes d'inscription sont configurables dans le tableau de bord (« Notifications », activation et CCI par adresse) avec repli sur les superadmins si aucune adresse active ; l'email de réinitialisation de mot de passe est opérationnel. Reste à décider le moment où les communes sont attribuées aux nouveaux collaborateurs validés et à communiquer le lien `/inscription/` aux personnes habilitées.

Le système de sauvegarde est livré : page « Sauvegardes » du tableau de bord (création manuelle, vérification, suppression avec confirmation, suivi de fraîcheur), commande `backup_sqlite` avec rotation `BACKUP_RETENTION` et verrou anti-concurrence, `BACKUP_DIR` obligatoire en production. Reste à configurer la tâche cron cPanel (documentée dans `docs/operations/deployment-o2switch.md`), à valider l'horaire et à planifier le test de restauration initial puis trimestriel.

La page « Mon profil » du tableau de bord est livrée avec ses tests : les comptes connectés peuvent modifier leur prénom, leur nom et leur adresse email (confirmation par mot de passe actuel, unicité de l'email, journal d'audit).

Le système de campagnes de mise à jour annuelle des assistantes maternelles est livré (app `campagnes`, documentation `docs/features/campagnes.md`) : campagne avec période et statuts, invitations à jeton haché, page publique de vérification sans compte, file de validation champ par champ, saisie assistée, relance et courriers imprimables, statistiques et journalisation. Un mode test permet de lancer une campagne vers 2-3 adresses de test (aucun e-mail réel) puis de « Passer en réel » (jetons régénérés). Reste à définir l'organisation pratique des courriers papier (impression, affranchissement, remise en main propre) et à décider si la V2 (relances automatiques, SMS, QR code, PDF) est souhaitée. À noter : la campagne n'envoie des e-mails qu'à l'action « Lancer les envois », « Relancer » ou « Passer en réel », jamais automatiquement.
