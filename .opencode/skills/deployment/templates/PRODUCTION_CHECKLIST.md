# Checklist Production

## Django
- [ ] DEBUG=False.
- [ ] SECRET_KEY externe.
- [ ] ALLOWED_HOSTS correct.
- [ ] CSRF trusted origins correctes.
- [ ] `check --deploy`.

## Serveur
- [ ] Processus non-root.
- [ ] WSGI/ASGI production.
- [ ] Reverse proxy.
- [ ] HTTPS.
- [ ] Firewall.
- [ ] Logs/rotation.

## Données
- [ ] PostgreSQL non public.
- [ ] Compte DB dédié.
- [ ] Migrations relues.
- [ ] Backup.
- [ ] Media persistants.

## Release
- [ ] Commit identifié.
- [ ] Dépendances verrouillées.
- [ ] Static collectés.
- [ ] Health check.
- [ ] Smoke tests.
- [ ] Rollback documenté.

## Docker si utilisé
- [ ] Pas de secret dans image.
- [ ] Utilisateur non-root.
- [ ] Volumes persistants.
- [ ] Tags identifiables.
- [ ] Health checks.
