# Sauvegarde et restauration SQLite

L'objectif proposé pour ce petit service est une perte maximale de 24 heures de données (RPO) et une restauration manuelle dans la demi-journée (RTO). Ces objectifs doivent être validés par le responsable du service.

## Politique recommandée

- une sauvegarde cohérente quotidienne par la commande Django ;
- 7 copies quotidiennes, 4 hebdomadaires et 6 mensuelles ;
- une copie chiffrée hors du compte o2switch ;
- contrôle d'intégrité et checksum à chaque création ;
- alerte si aucune sauvegarde valide n'a moins de 26 heures ;
- test de restauration initial puis trimestriel.

[JetBackup](https://faq.o2switch.fr/cpanel/fichiers/sauvegarde-jetbackup/) est une couche complémentaire. Il ne remplace ni la copie externe, ni le contrôle de cohérence SQLite, ni le test de restauration.

## Créer et vérifier

Utilisez un répertoire privé distinct de la base active. En production, définissez `BACKUP_DIR` (obligatoire) et `BACKUP_RETENTION` ; en local, les valeurs par défaut sont `backups/` et 7.

```bash
python manage.py backup_sqlite
python manage.py verify_sqlite_backup backups/bdd-pe-prod-AAAAMMJJTHHMMSSffffffZ.sqlite3
```

Le répertoire et le nombre de copies conservées peuvent être passés explicitement :

```bash
python manage.py backup_sqlite /home/compte/private-backups/bdd-pe --keep 7
```

La commande utilise l'API de sauvegarde SQLite pendant que l'application fonctionne, écrit d'abord un fichier partiel, exécute `PRAGMA integrity_check`, puis publie atomiquement la copie et affiche son SHA-256. Elle applique ensuite la rotation : seules les `BACKUP_RETENTION` copies les plus récentes sont conservées, et uniquement après une création réussie.

Le tableau de bord (page « Sauvegardes », superadmins) propose une sauvegarde manuelle en un clic, la vérification d'une copie, sa suppression avec confirmation, et l'état de fraîcheur de la dernière sauvegarde (alerte au-delà de 26 h). Les créations et suppressions manuelles sont consignées dans le journal d'audit.

Configurez la tâche cron sous le même utilisateur que l'application :

```bash
cd /chemin/application && python manage.py backup_sqlite
```

Consignez sa sortie dans un fichier soumis à rotation et alertez sur tout code retour non nul. La rotation intégrée remplace le script de purge séparé précédemment recommandé ; elle reste bornée au motif `bdd-pe-*.sqlite3` du répertoire configuré.

## Test de restauration sans risque

1. choisir une sauvegarde et noter son SHA-256 ;
2. préparer un répertoire temporaire privé, jamais le chemin de production ;
3. vérifier la copie avec `verify_sqlite_backup` ;
4. déployer le code correspondant à la sauvegarde ;
5. définir `DATABASE_PATH` vers la copie temporaire et neutraliser le SMTP externe ;
6. exécuter `check`, `migrate --plan`, puis les migrations nécessaires sur cette copie ;
7. tester accueil, liste, détail, connexion et lecture du dashboard ;
8. comparer quelques comptes et structures attendus ;
9. consigner date, durée, résultat et opérateur ;
10. supprimer la copie temporaire selon la politique de données.

## Restauration après incident

1. mettre l'application en maintenance ou arrêter les écritures ;
2. conserver une copie de la base défaillante si cela reste sûr ;
3. choisir explicitement la sauvegarde et la release compatibles ;
4. restaurer d'abord dans une cible de contrôle ;
5. vérifier intégrité et parcours critiques ;
6. remplacer la base de production seulement après validation humaine ;
7. redémarrer Passenger, surveiller les logs et créer une nouvelle sauvegarde.

Les suppressions de données personnelles peuvent subsister jusqu'à expiration des sauvegardes. Une restauration doit éviter de réintroduire volontairement des données déjà supprimées, sauf nécessité d'incident documentée.
