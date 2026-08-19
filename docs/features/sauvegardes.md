# Sauvegardes de la base

La page **Sauvegardes** du tableau de bord (réservée aux superadmins) permet de créer, vérifier et supprimer les copies SQLite, et de suivre la sauvegarde automatique.

## Sauvegarde manuelle

Le bouton « Sauvegarder maintenant » crée une copie cohérente de la base (API de sauvegarde SQLite), la vérifie (contrôle d'intégrité) et calcule son SHA-256. La création et la suppression sont consignées dans le journal d'audit.

## Sauvegarde automatique

La sauvegarde quotidienne est déclenchée par une tâche planifiée chez l'hébergeur (cron) :

```bash
python manage.py backup_sqlite
```

La commande utilise le répertoire `BACKUP_DIR`, vérifie la copie créée et applique la rotation (`BACKUP_RETENTION`, 7 copies par défaut). Un répertoire et un nombre de copies peuvent être passés explicitement :

```bash
python manage.py backup_sqlite /chemin/vers/backups --keep 7
```

La page Sauvegardes indique la fraîcheur de la dernière copie (alerte si plus de 26 h) et rappelle la ligne cron.

## Liste et vérification

Le tableau liste les copies (nom, date, taille, statut). Chaque ligne propose :

- **Vérifier** : relance le contrôle d'intégrité et recalcule l'empreinte ;
- **Supprimer** : page de confirmation, puis suppression consignée dans le journal.

L'état « vérifiée » est conservé dans un catalogue JSON du répertoire (`bddpe-backups.json`), mis à jour à la création et à la vérification.

## Sécurité

Voir [Sécurité des sauvegardes](../security/backups.md).
