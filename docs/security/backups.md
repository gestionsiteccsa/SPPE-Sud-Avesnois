# Sécurité des sauvegardes

## Données protégées

Les sauvegardes SQLite contiennent des données personnelles (comptes collaborateurs, structures, journal d'audit). Elles doivent être traitées avec au moins les mêmes protections que la base active.

## Modèle de menace

- **Accès non autorisé** : seuls les superadmins accèdent à la page Sauvegardes ; aucune sauvegarde n'est jamais servie par HTTP (pas de téléchargement dans le navigateur).
- **Path traversal / symlinks** : les noms de fichiers transitent par l'URL. Toute opération valide le nom contre un motif strict (`bdd-pe-<env>-<horodatage>.sqlite3`), refuse les séparateurs et vérifie que le chemin résolu reste dans le répertoire de sauvegarde. Les liens symboliques et fichiers non réguliers sont ignorés et refusés à la suppression.
- **Remplissage du disque (déni de service)** : l'espace libre est vérifié avant chaque sauvegarde (2× la taille de la base, 50 Mo minimum) ; la création manuelle est limitée en débit (12 requêtes/heure).
- **Concurrence** : un verrou exclusif dans le répertoire de sauvegarde empêche deux créations simultanées (cron + clic manuel, processus Passenger multiples). Un verrou orphelin de plus de 30 minutes est récupéré.
- **Suppression accidentelle** : la rotation automatique ne supprime que les fichiers du motif strict, après une création réussie et vérifiée ; la suppression manuelle passe par une page de confirmation et est consignée dans le journal d'audit.
- **Altération** : chaque sauvegarde est vérifiée à la création (contrôle d'intégrité SQLite + SHA-256) ; la vérification peut être relancée depuis le dashboard.

## Protections applicatives

- Toutes les vues du dashboard « Sauvegardes » exigent un superadmin (GET et POST).
- Toutes les mutations sont en POST, protégées par CSRF natif.
- Les erreurs visibles à l'utilisateur restent génériques ; les détails vont dans les journaux serveur, sans secret ni contenu sensible.
- Les chemins internes ne sont jamais exposés dans les messages.

## Configuration de production

- `BACKUP_DIR` est **obligatoire** en production et doit pointer vers un répertoire privé, distinct de `STATIC_ROOT` et du dossier de la base (le site refuse de démarrer sinon).
- Le répertoire doit rester hors `public_html` et hors de toute racine web ; il n'est jamais servi par HTTP.
- La rotation ne conserve que `BACKUP_RETENTION` copies (7 par défaut).

## Cycle de vie RGPD

Les sauvegardes peuvent contenir des données supprimées du système actif jusqu'à expiration de la rétention. La rétention est bornée (7 copies), la suppression est contrôlée (rotation + page de confirmation) et consignée dans le journal d'audit.
