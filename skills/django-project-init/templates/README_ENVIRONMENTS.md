# Environnements Django

Le projet utilise quatre fichiers de settings :

- `base.py` : valeurs communes ;
- `dev.py` : développement local ;
- `test.py` : tests automatisés ;
- `prod.py` : production.

La sélection se fait avec `DJANGO_SETTINGS_MODULE`.

## Local

```text
DJANGO_SETTINGS_MODULE=config.settings.dev
```

Le debug peut être actif et les outils de développement sont autorisés.

## Test

```text
DJANGO_SETTINGS_MODULE=config.settings.test
```

L’environnement doit être déterministe et isoler autant que possible les services externes.

## Production

```text
DJANGO_SETTINGS_MODULE=config.settings.prod
```

`DEBUG` doit être désactivé. Les secrets, hôtes autorisés et autres paramètres critiques doivent être fournis explicitement par l’environnement.

La production ne doit jamais utiliser silencieusement les settings de développement.
