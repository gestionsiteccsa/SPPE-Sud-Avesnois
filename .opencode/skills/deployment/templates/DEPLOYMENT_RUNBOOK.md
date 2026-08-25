# Runbook de déploiement

## Avant

- [ ] Branche/commit correct.
- [ ] Quality gates verts.
- [ ] Tests pertinents verts.
- [ ] Migrations relues.
- [ ] Backup récent si changement DB risqué.
- [ ] `check --deploy`.
- [ ] Plan de rollback identifié.

## Déploiement

- [ ] Installer la release.
- [ ] Installer dépendances verrouillées.
- [ ] Appliquer migrations.
- [ ] Collecter static.
- [ ] Redémarrer/remplacer le service.
- [ ] Vérifier service.

## Après

- [ ] Health check.
- [ ] Page principale.
- [ ] Login si applicable.
- [ ] DB.
- [ ] Static.
- [ ] HTTPS.
- [ ] Logs.
- [ ] Version déployée enregistrée.

## Rollback

- [ ] Identifier release précédente.
- [ ] Vérifier compatibilité DB.
- [ ] Restaurer code/image.
- [ ] Redémarrer.
- [ ] Health check.
- [ ] Smoke tests.
