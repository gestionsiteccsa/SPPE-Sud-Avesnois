# Checklist pipeline de déploiement

## Avant
- [ ] Commit/release identifié.
- [ ] CI verte.
- [ ] Migration review.
- [ ] Backup récent si risque.
- [ ] Staging validé si nécessaire.
- [ ] Secrets environnement présents.
- [ ] Rollback connu.

## Déploiement
- [ ] Concurrency lock.
- [ ] Artefact exact.
- [ ] Dependencies/runtime.
- [ ] Migrations.
- [ ] Static.
- [ ] Restart/replacement.

## Après
- [ ] Health check.
- [ ] Smoke tests.
- [ ] Logs.
- [ ] Version enregistrée.
- [ ] Alertes stables.

## Échec
- [ ] Arrêter.
- [ ] Préserver logs.
- [ ] Vérifier DB.
- [ ] Rollback contrôlé si sûr.
