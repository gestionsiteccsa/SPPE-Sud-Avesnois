# Supervision et incidents

## Supervision minimale

- sonder `/health/` et une page publique depuis l'extérieur ;
- alerter sur indisponibilité, hausse des erreurs 500 et certificat proche de l'expiration ;
- consulter les logs Passenger/Django au niveau `INFO` ou supérieur ;
- surveiller espace disque, CPU, mémoire, I/O et taille de SQLite ;
- vérifier chaque jour l'âge de la dernière sauvegarde valide ;
- rechercher les occurrences de `database is locked`.

Les logs vont vers la sortie standard afin d'être collectés par Passenger/cPanel. Configurez leur rotation côté hébergement. Ils ne doivent contenir ni mot de passe, ni token, ni contenu complet d'import. Une solution de suivi d'erreurs externe est optionnelle pour ce volume et doit être revue sous l'angle RGPD avant activation.

## Incident : site indisponible

1. tester le domaine et `/health/` depuis l'extérieur ;
2. vérifier certificat, DNS et statut de l'application cPanel ;
3. lire les dernières erreurs Passenger/Django ;
4. contrôler les quotas CPU, mémoire, I/O et disque ;
5. redémarrer une fois l'application seulement si les logs permettent une hypothèse ;
6. revenir à la release précédente si l'incident suit un déploiement.

## Incident : `database is locked`

1. noter heure, fréquence, URL et opération administrative concernée ;
2. rechercher un import ou plusieurs écritures simultanées ;
3. éviter les relances répétées qui augmentent la contention ;
4. vérifier qu'aucune copie naïve ou tâche longue ne bloque la base ;
5. conserver les preuves et stabiliser les écritures.

Une occurrence isolée peut être opérationnelle. Des occurrences répétées, plusieurs rédacteurs réguliers, des imports fréquents, des workers d'écriture ou plusieurs instances applicatives déclenchent une étude de migration vers MariaDB.

## Incident : sauvegarde en échec

Ne supprimez aucune ancienne copie. Vérifiez le chemin, les droits, l'espace disponible et le message de la commande. Relancez une seule sauvegarde après correction, vérifiez-la, copiez-la hors du compte puis consignez l'incident.

## Entretien périodique

- hebdomadaire : erreurs applicatives, espace et sauvegardes ;
- mensuel : dépendances de sécurité, capacité et purge du journal d'audit ;
- trimestriel : restauration testée et revue du runbook ;
- avant chaque déploiement : sauvegarde valide, quality gates et procédure de rollback.

## Purge du journal d'audit

Le journal d'audit conserve d'anciennes valeurs potentiellement personnelles. Appliquez la rétention validée avec le responsable du traitement, par exemple tous les mois via un cron :

```bash
python manage.py purge_audit_log --older-than-days 365 --dry-run
python manage.py purge_audit_log --older-than-days 365
```

L'option `--dry-run` affiche le nombre d'entrées concernées sans rien supprimer. Adaptez la durée à la politique de conservation retenue.
