## Backup & Restore

- Charger `backup-restore` pour les sauvegardes, restaurations et opérations de récupération.
- Production doit disposer d’une sauvegarde quotidienne de PostgreSQL et des media non régénérables.
- Une copie uniquement sur le disque de production n’est pas suffisante à long terme.
- Une sauvegarde n’est pas considérée fiable tant qu’une restauration n’a pas été testée.
- Avant une migration destructive ou à fort risque, vérifier un backup récent et exploitable.
- Une restauration en production ne doit jamais être déclenchée automatiquement ou sans accord explicite.
