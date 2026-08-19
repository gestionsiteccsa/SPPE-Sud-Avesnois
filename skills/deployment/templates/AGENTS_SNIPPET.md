## Déploiement

- Charger `deployment` pour staging, production, Docker, systemd, reverse proxy, HTTPS et release.
- Docker doit rester optionnel si le projet supporte aussi un déploiement classique.
- Ne jamais utiliser `runserver` en production.
- Ne jamais déployer avec `DEBUG=True`.
- Avant production : quality gates, migrations relues, backup si nécessaire, `check --deploy`, plan de rollback.
- Après déploiement : health check, smoke tests et vérification des logs.
- Aucune opération destructive de production sans accord explicite.
