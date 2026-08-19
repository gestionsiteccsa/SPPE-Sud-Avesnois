# Runbook de restauration

## Avant

- [ ] Identifier l’incident.
- [ ] Choisir le backup cible.
- [ ] Vérifier timestamp, taille et checksum.
- [ ] Vérifier la version PostgreSQL.
- [ ] Vérifier la release applicative correspondante.
- [ ] Identifier rôles/extensions nécessaires.
- [ ] Stopper ou limiter les écritures si restauration production.

## Test préalable

- [ ] Créer une base temporaire.
- [ ] Restaurer avec `pg_restore`.
- [ ] Lancer les checks Django.
- [ ] Vérifier des données représentatives.
- [ ] Exécuter les smoke tests.
- [ ] Vérifier les media si concernés.

## Production

- [ ] Accord explicite.
- [ ] Conserver l’état actuel si utile.
- [ ] Restaurer base.
- [ ] Restaurer media.
- [ ] Appliquer les migrations nécessaires.
- [ ] Démarrer l’application.
- [ ] Health check.
- [ ] Smoke tests.
- [ ] Vérifier logs.

## Après

- [ ] Réouvrir le trafic.
- [ ] Documenter l’incident.
- [ ] Révoquer/rotater secrets ou sessions si nécessaire.
- [ ] Vérifier que les backups suivants fonctionnent.
