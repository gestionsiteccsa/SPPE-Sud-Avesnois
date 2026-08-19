# SPPE Sud-Avesnois — annuaire des structures petite enfance

Application Django proposant un annuaire public, des filtres, une carte et un tableau de bord réservé aux superutilisateurs. La cible de production est un hébergement mutualisé o2switch sous Python 3.13, Django 6.0 et SQLite pour un faible volume d'écritures.

## Fonctions principales

- consultation, recherche, filtres, pagination et fiches détaillées ;
- carte Leaflet alimentée par les structures géolocalisées ;
- connexion par email et réinitialisation du mot de passe ;
- inscription des collaborateurs via le lien `/inscription/`, validée par un superadmin (email de notification), puis gestion des structures des communes qui leur sont liées ;
- CRUD des structures, communes, types et comptes dans le dashboard ;
- import CSV/XLSX transactionnel et journal d'audit ;
- sauvegarde SQLite cohérente et contrôle d'intégrité.

## Prérequis

- Python 3.13 ;
- Node.js 22 et npm uniquement pour reconstruire les ressources frontend ;
- Redis en production pour une limitation de connexion commune aux processus Passenger.

Les fichiers CSS, JavaScript, polices et bibliothèques frontend construits sont versionnés. Node.js n'est donc pas nécessaire sur le serveur si ces fichiers ont été générés et vérifiés avant le déploiement.

## Installation locale

```bash
python -m venv env
```

Activation sous Windows PowerShell :

```powershell
.\env\Scripts\Activate.ps1
```

Activation sous Linux ou macOS :

```bash
source env/bin/activate
```

Puis :

```bash
python -m pip install --requirement requirements.txt
npm ci
python build_assets.py
cp .env.example .env  # Linux/macOS ; sous Windows : Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Pour le développement (Ruff inclus) : `python -m pip install --requirement requirements-dev.txt`.

`seed_data` charge cinq structures entièrement fictives. Remplacez uniquement les valeurs locales nécessaires dans `.env` ; ce fichier ne doit jamais être versionné. Les chemins relatifs de l'exemple sont réservés au développement ; la production utilise des chemins absolus privés.

## Contrôles qualité

```bash
python build_assets.py
ruff check .
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --dry-run --noinput --verbosity 0
python manage.py test
python -m pip check
npm audit
```

Les dépendances de développement (dont Ruff) sont installées via `requirements-dev.txt`. La CI répète le build et les contrôles critiques sous Python 3.13. Aucun commit ou push n'est automatisé par le projet.

## Import et sauvegarde

```bash
python manage.py import_excel chemin/structures.xlsx
python manage.py backup_sqlite chemin/prive/backups
python manage.py verify_sqlite_backup chemin/prive/backups/sauvegarde.sqlite3
python manage.py purge_audit_log --older-than-days 365 --dry-run
```

L'option `--ecraser` de l'import remplace les structures seulement si le fichier entier est valide. Une sauvegarde ne doit jamais être stockée dans le répertoire public du domaine. Le journal d'audit est conservé par défaut un an ; ajustez la rétention avec `purge_audit_log` (planifiez-la en production).

L'admin Django n'est plus exposé à `/admin/` : le chemin par défaut est `gestion-interne/`, à personnaliser dans l'environnement via `ADMIN_URL`.

## Documentation

- [Index de la documentation](docs/index.md)
- [Déploiement o2switch](docs/operations/deployment-o2switch.md)
- [Sauvegarde et restauration](docs/operations/backup-restore.md)
- [Supervision et incidents](docs/operations/runbook.md)
- [Données personnelles et RGPD](docs/privacy/overview.md)
- [Audit initial et état des remédiations](AUDIT_O2SWITCH.md)
- [Tâches restant à traiter](PROJECT_TASKS.md)

## Limites connues

SQLite convient au petit service prévu, avec peu d'écritures simultanées. Des erreurs `database is locked`, plusieurs administrateurs actifs, des imports fréquents, des écritures en arrière-plan ou plusieurs instances applicatives imposent de réévaluer une migration vers MariaDB.

Les tuiles de la carte restent chargées depuis OpenStreetMap. Les autres dépendances frontend et la police Inter sont hébergées localement.
