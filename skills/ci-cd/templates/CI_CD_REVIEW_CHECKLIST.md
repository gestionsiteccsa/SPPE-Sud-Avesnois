# Checklist CI/CD

## CI
- [ ] Install propre.
- [ ] Runtime épinglé.
- [ ] PostgreSQL pertinent.
- [ ] Lint.
- [ ] Format check.
- [ ] Django check.
- [ ] Migration check.
- [ ] Migrate sur DB propre.
- [ ] Tests.
- [ ] Audit sécurité.
- [ ] Aucun secret prod.

## CD
- [ ] Trigger explicite.
- [ ] Environnements séparés.
- [ ] Artefact identifiable.
- [ ] Staging.
- [ ] Production protégée.
- [ ] Migration review.
- [ ] Backup gate si risque.
- [ ] Health check.
- [ ] Smoke tests.
- [ ] Rollback.

## Sécurité pipeline
- [ ] Permissions minimales.
- [ ] Secrets store.
- [ ] Actions/plugins épinglés.
- [ ] SSH host key vérifiée.
- [ ] Deploy user limité.

## Documentation
- [ ] Triggers.
- [ ] Jobs.
- [ ] Secrets attendus.
- [ ] Déploiement.
- [ ] Rollback.
