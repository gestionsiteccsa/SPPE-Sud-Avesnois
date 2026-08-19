# Déploiement sur o2switch

Cette procédure cible une application Python cPanel/Passenger sous Python 3.13. Elle suppose un faible trafic, peu d'écritures simultanées et SQLite conservé hors du répertoire public.

## 1. Préparer une release

Sur un poste de développement avec Python 3.13 et Node.js 22 :

```bash
python -m pip install --requirement requirements.txt
npm ci
python build_assets.py
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --dry-run --noinput --verbosity 0
python manage.py test
python -m pip check
npm audit
```

Le build frontend doit laisser `git diff -- static` vide pour une release déjà versionnée. Identifiez le commit à déployer et disposez d'une sauvegarde vérifiée avant toute migration.

## 2. Créer l'application cPanel

Dans « Setup Python App » :

1. choisir Python 3.13 ;
2. placer la racine applicative hors de `public_html` ;
3. sélectionner le domaine ou sous-domaine HTTPS ;
4. utiliser `passenger_wsgi.py` comme fichier de démarrage ;
5. utiliser `application` comme callable WSGI ;
6. conserver le chemin de l'environnement virtuel indiqué par cPanel.

Le fichier `passenger_wsgi.py` expose déjà `app.wsgi.application`. Les détails d'écran peuvent évoluer : se référer à la [documentation Python officielle o2switch](https://faq.o2switch.fr/cpanel/logiciels/hebergement-python-multi-version/) et aux [versions disponibles](https://faq.o2switch.fr/guides/langages-supportes-php-node-ruby-python/).

## 3. Installer l'application

Activez l'environnement virtuel fourni par cPanel, placez-vous dans la racine applicative, puis exécutez :

```bash
python -m pip install --requirement requirements.txt
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
```

Node.js n'est pas nécessaire sur o2switch : `static/css`, `static/js` et `static/vendor` contiennent les artefacts construits. `collectstatic` les rassemble dans `STATIC_ROOT`.

Configurez le domaine pour servir le contenu de `STATIC_ROOT` sous `/static/`, via le mécanisme cPanel adapté au domaine. Ne rendez ni la base SQLite, ni les sauvegardes, ni `.env` accessibles par HTTP.

## 4. Variables cPanel

Définissez les variables dans l'interface de l'application Python, jamais dans Git :

| Variable | Production |
|---|---|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `False` |
| `SECRET_KEY` | valeur aléatoire forte et unique |
| `ALLOWED_HOSTS` | domaines explicites, séparés par des virgules |
| `CSRF_TRUSTED_ORIGINS` | origines HTTPS complètes |
| `DATABASE_PATH` | chemin absolu privé et persistant |
| `BACKUP_DIR` | chemin absolu privé, hors `public_html` et distinct de `STATIC_ROOT` (obligatoire) |
| `BACKUP_RETENTION` | nombre de sauvegardes conservées (défaut `7`) |
| `STATIC_ROOT` | chemin absolu destiné aux statiques collectés |
| `REDIS_URL` | URL/socket de l'instance Redis privée |
| `EMAIL_*` | compte SMTP transactionnel o2switch |
| `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL` | expéditeurs du domaine |
| `LOG_LEVEL` | `INFO` |

La production refuse de démarrer si `DEBUG=True`, si les hôtes restent locaux, si les origines CSRF sont absentes, si le SMTP choisi n'a pas d'hôte ou si Redis n'est pas configuré. Activez l'[instance Redis privée o2switch](https://faq.o2switch.fr/cpanel/o2switch/redis/) et ne publiez jamais son secret.

Le répertoire contenant `DATABASE_PATH` doit être inscriptible par l'utilisateur Passenger. Il doit rester persistant lorsque le code applicatif est remplacé. Idem pour `BACKUP_DIR` : il ne doit jamais être placé sous `public_html` ni sous `STATIC_ROOT`.

Planifiez la sauvegarde quotidienne avec un cron cPanel (même utilisateur que l'application, sortie consignée et alerte sur code retour non nul) :

```bash
cd /chemin/application && python manage.py backup_sqlite
```

## 5. HTTPS et HSTS

Validez d'abord le certificat, les redirections et tous les sous-domaines. La valeur initiale `SECURE_HSTS_SECONDS=3600` est volontairement progressive. N'activez `SECURE_HSTS_INCLUDE_SUBDOMAINS` puis `SECURE_HSTS_PRELOAD` qu'après validation de l'ensemble du domaine ; ces options sont difficiles à annuler côté navigateur.

## 6. Redémarrage et smoke tests

Redémarrez l'application depuis cPanel, puis vérifiez :

- `/health/` renvoie uniquement `{"status":"ok"}` en HTTPS ;
- accueil, liste, détail, filtres, pagination et carte après connexion d'un compte validé ;
- redirection vers la connexion (`?next=`) pour un visiteur non authentifié sur l'accueil, la liste, le détail ou la carte ;
- absence de 404 sur CSS, JS, SVG et polices ;
- refus du dashboard pour un visiteur et un utilisateur non superutilisateur ;
- connexion, déconnexion et email de réinitialisation ;
- création, modification et suppression avec journal d'audit ;
- échec atomique d'un petit import invalide ;
- limitation de connexion commune via Redis ;
- sauvegarde post-déploiement créée et vérifiée.

## 7. Retour arrière

Un retour arrière du code n'est pas une restauration de base.

1. suspendre le déploiement et préserver les logs ;
2. identifier la release précédente ;
3. déterminer si la migration est rétrocompatible ;
4. remettre le code et les statiques précédents ;
5. ne restaurer SQLite qu'après décision humaine explicite ;
6. redémarrer Passenger et refaire les smoke tests.

Ne tentez pas d'inverser automatiquement une migration qui a supprimé ou transformé des données. Suivez le [runbook de restauration](backup-restore.md).
