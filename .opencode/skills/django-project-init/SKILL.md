---
name: django-project-init
description: Initialise ou audite le socle d’un projet Django avant le développement des features. À utiliser au démarrage d’un projet Django, lors de la reprise d’un projet existant, ou lorsque le socle doit être normalisé. Met en place une architecture simple et évolutive, PostgreSQL, environnements dev/test/prod, gestion stricte des secrets, qualité de code, tests pragmatiques, documentation française, Docker optionnel et fichiers de gouvernance. Se coordonne avec le skill project-workflow et les skills Django spécialisés.
compatibility: opencode
metadata:
  framework: django
  purpose: project-foundation
  language: fr
  workflow-parent: project-workflow
---

# Django Project Init

## 1. Mission

Tu construis ou audites le **socle technique d’un projet Django**.

Ton objectif est d’obtenir un projet :

- simple à comprendre ;
- propre à maintenir ;
- sécurisé dès le départ ;
- facilement testable ;
- prêt à évoluer ;
- aussi proche que raisonnablement possible entre local, staging et production ;
- documenté en français ;
- utilisable avec ou sans Docker ;
- compatible avec les autres skills du projet.

Tu ne dois pas sur-architecturer un petit projet.

Tu dois néanmoins anticiper les décisions qui deviennent coûteuses à changer plus tard, comme :

- modèle utilisateur ;
- stratégie de settings ;
- base de données ;
- secrets ;
- conventions de projet ;
- structure des apps ;
- stockage des médias ;
- dépendances structurantes.

---

## 2. Coordination avec les autres règles

Avant toute action :

1. Lis `AGENTS.md`.
2. Charge `project-workflow` s’il est disponible.
3. Charge les skills spécialisés utiles s’ils existent :
   - `django-architecture`
   - `django-database`
   - `django-security`
   - `django-testing`
   - `git-quality`
   - `documentation`
   - `deployment`
4. Inspecte le projet existant avant de créer ou remplacer quoi que ce soit.

En cas de conflit :

1. sécurité et intégrité des données ;
2. règles explicites du dépôt ;
3. décisions d’architecture déjà validées ;
4. bonnes pratiques Django actuelles ;
5. simplicité et maintenabilité.

Ne duplique pas dans ce skill les détails qui appartiennent à un skill spécialisé quand celui-ci est disponible.

---

## 3. Projet neuf ou projet existant

Détermine d’abord si tu es dans l’un des cas suivants.

### Projet neuf

Tu peux proposer et créer le socle complet.

### Projet existant

Ne réinitialise jamais aveuglément le projet.

Commence par un audit rapide :

- version Python ;
- version Django ;
- gestionnaire de dépendances ;
- base de données ;
- structure des settings ;
- modèle utilisateur ;
- apps existantes ;
- tests ;
- lint/formatage ;
- variables d’environnement ;
- `.gitignore` ;
- Docker ;
- documentation ;
- Git ;
- CI éventuelle.

Ensuite classe chaque élément :

- **Conserver**
- **Améliorer**
- **À décider**
- **Risque critique**

Privilégie une évolution progressive.

---

## 4. Questions initiales

L’utilisateur peut être non-développeur.

Pose **au maximum 2 questions à la fois** et uniquement si la réponse change réellement le socle.

Explique brièvement pourquoi la question est importante.

### Questions structurantes possibles

Selon ce qui n’est pas déjà connu :

- Le projet a-t-il besoin de comptes utilisateurs ?
- L’authentification utilisera-t-elle probablement l’email, un username ou une autre identité ?
- Une API ou un frontend React/Vue est-il prévu ?
- Des fichiers utilisateurs seront-ils envoyés ?
- Le projet sera-t-il multilingue ?
- Existe-t-il déjà une base de données ou des données à préserver ?
- Le projet doit-il fonctionner sans Docker ?
- Y a-t-il des contraintes d’hébergement connues ?

Ne demande pas à l’utilisateur de choisir :

- l’emplacement d’un fichier standard ;
- une option de lint évidente ;
- un mécanisme de sécurité Django standard ;
- une convention technique sans impact métier notable.

Choisis la bonne pratique et explique-la.

---

## 5. Version Python et Django

### Règle

Ne fige pas dans ce skill un numéro de version éternel.

Lors de l’initialisation :

1. détermine la version Django réellement installée si le projet existe ;
2. si le projet est neuf, vérifie les versions Django officiellement supportées lorsque l’accès aux sources officielles est disponible ;
3. n’utilise jamais une branche Django non supportée pour un nouveau projet ;
4. privilégie :
   - la **LTS actuelle** lorsque la stabilité et la durée de support priment ;
   - la **dernière stable** lorsque ses nouveautés sont utiles et que sa durée de support convient ;
5. utilise une version Python officiellement prise en charge par la version Django choisie ;
6. documente le choix dans `docs/architecture/decisions.md`.

Pour les correctifs de sécurité/patch releases d’une même série, préfère la dernière version de patch compatible.

Ne fais pas une montée de version majeure ou mineure d’un projet existant sans analyser les incompatibilités et sans tests.

---

## 6. Base de données

### Valeur par défaut recommandée

Pour un vrai projet destiné à staging/production, privilégie **PostgreSQL** dès le développement local lorsque c’est raisonnable.

Objectif : réduire les différences de comportement entre local et production.

SQLite reste acceptable pour :

- prototype jetable ;
- démonstration très simple ;
- cas explicitement assumé.

Mais ne l’utilise pas comme solution locale par défaut si la production utilisera PostgreSQL et que le projet comporte des relations ou requêtes métier importantes.

Utilise un pilote PostgreSQL moderne et officiellement compatible avec la version Django/Python retenue.

Ne mets aucun identifiant de base de données dans le code.

---

## 7. Structure de projet recommandée

Ne crée pas une architecture complexe sans besoin.

Pour un projet classique, une base saine peut ressembler à :

```text
project/
├── manage.py
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── PROJECT_TASKS.md
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── urls.py
│   ├── wsgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── dev.py
│       ├── test.py
│       └── prod.py
├── apps/
├── templates/
├── static/
├── media/              # local uniquement ; contenu non versionné
├── tests/ ou tests par app
└── docs/
```

Adapte cette structure au projet existant.

### Apps Django

Crée une app pour une **responsabilité métier cohérente**, pas pour chaque modèle.

Évite :

- une app gigantesque contenant tout le domaine ;
- une app par table ;
- des apps purement artificielles sans frontière métier.

Le découpage détaillé appartient à `django-architecture` lorsqu’il existe.

---

## 8. Settings : base / dev / test / prod

Utilise des settings séparés avec une base commune.

### `base.py`

Contient uniquement ce qui est réellement commun :

- `INSTALLED_APPS`
- middleware commun ;
- templates ;
- i18n ;
- configuration générale ;
- modèle utilisateur ;
- paramètres de base de données construits à partir de variables d’environnement ;
- static/media communs ;
- logging de base si nécessaire.

### `dev.py`

Peut activer :

- `DEBUG = True` ;
- outils de développement ;
- logs plus détaillés ;
- email backend local ;
- valeurs pratiques uniquement adaptées au local.

### `test.py`

Doit fournir :

- environnement déterministe ;
- paramètres adaptés aux tests ;
- services externes neutralisés ou simulés lorsque pertinent ;
- hashers/optimisations de test uniquement si cela ne masque pas un comportement à tester.

### `prod.py`

Doit :

- définir `DEBUG = False` ;
- exiger les secrets nécessaires ;
- exiger des hôtes autorisés explicites ;
- activer les protections de production pertinentes ;
- échouer clairement si une variable critique manque ;
- ne contenir aucun fallback dangereux.

### Sélection

Utilise le mécanisme standard `DJANGO_SETTINGS_MODULE`.

Exemples conceptuels :

```text
config.settings.dev
config.settings.test
config.settings.prod
```

Le README doit expliquer comment chaque environnement le sélectionne.

La production ne doit jamais dépendre d’un réglage local implicite.

---

## 9. Variables d’environnement et secrets

Politique stricte.

### Obligatoire

- aucun secret en dur ;
- aucun `.env` réel dans Git ;
- `.env.example` versionné ;
- noms de variables explicites ;
- valeurs critiques obligatoires en production ;
- erreur explicite si une variable critique manque.

Variables typiques :

```text
DJANGO_SETTINGS_MODULE
DJANGO_SECRET_KEY
DJANGO_ALLOWED_HOSTS
DATABASE_URL ou paramètres DB séparés
DJANGO_CSRF_TRUSTED_ORIGINS
```

N’ajoute pas une bibliothèque de gestion d’environnement uniquement par habitude.

Si la bibliothèque standard et la configuration du projet suffisent proprement, reste simple.

Si une dépendance dédiée apporte une vraie valeur au projet, analyse-la comme toute dépendance externe.

### `.env.example`

Ne contient :

- aucune vraie clé ;
- aucun vrai mot de passe ;
- aucun token ;
- aucune URL privée contenant des identifiants.

Utilise des valeurs factices clairement identifiables.

---

## 10. Modèle utilisateur

C’est une décision structurante.

Si le projet a ou aura probablement des utilisateurs authentifiés, évalue le modèle utilisateur **avant les premières migrations métier**.

Changer `AUTH_USER_MODEL` au milieu d’un projet est complexe.

### Règle de conception

Ne crée pas un custom user inutilement sophistiqué.

Si un modèle personnalisé est justifié dès le départ :

- pars d’une abstraction Django adaptée ;
- garde le modèle d’identité aussi simple que possible ;
- place les données spécifiques à un domaine dans des modèles liés lorsque cela réduit le couplage ;
- référence toujours l’utilisateur via `settings.AUTH_USER_MODEL` dans les relations de modèles ;
- utilise `get_user_model()` dans le code exécuté dynamiquement.

Avant de décider email vs username, utilise le questionnement du `project-workflow`.

Documente la décision.

---

## 11. Static et media

Distingue clairement :

- **static** : assets de l’application ;
- **media** : fichiers envoyés ou générés pour les utilisateurs.

Ne versionne pas les médias utilisateurs.

Le stockage de production dépendra de l’infrastructure et du skill de déploiement.

Ne suppose pas qu’un stockage local permanent convient à toutes les productions.

---

## 12. Dépendances

Pour chaque dépendance ajoutée :

1. justifie son besoin ;
2. vérifie qu’elle est maintenue ;
3. vérifie la compatibilité Python/Django ;
4. vérifie la sécurité connue si possible ;
5. évite les doublons de fonctionnalité ;
6. documente les dépendances structurantes.

Regroupe la configuration Python moderne dans `pyproject.toml` lorsque cela est compatible avec l’outillage choisi.

Ne change pas le gestionnaire de dépendances d’un projet existant sans raison.

---

## 13. Qualité de code

Pour un projet Python/Django moderne, configure un socle de qualité simple.

### Ruff

Ruff peut assurer :

- lint ;
- formatage ;
- imports ;
- nombreuses vérifications Python.

Utilise une configuration raisonnable et progressive.

N’active pas des centaines de règles agressives sans vérifier leur utilité.

Ne transforme pas le lint en obstacle permanent au développement.

### Type checking

Le typage statique est utile mais ne doit pas être imposé aveuglément si le projet n’en a pas besoin ou n’est pas prêt.

Si le projet utilise déjà un type checker, conserve-le et configure-le proprement.

---

## 14. Tests

Initialise un framework de tests cohérent avec le projet.

Si `pytest` est choisi :

- structure claire ;
- configuration centralisée ;
- intégration Django appropriée ;
- fixtures compréhensibles ;
- pas de fixtures globales gigantesques.

Applique le TDD pragmatique du skill `project-workflow`.

Le socle doit permettre de lancer facilement :

- les tests complets ;
- un fichier ;
- une classe ;
- un test précis.

Documente les commandes dans le README et `AGENTS.md`.

---

## 15. Pre-commit

Configure `pre-commit` si cela correspond au workflow choisi.

Les hooks rapides peuvent inclure :

- Ruff lint ;
- Ruff format ;
- détection de fins de ligne/espaces ;
- validation YAML/TOML ;
- détection de gros fichiers accidentels ;
- détection de secrets si un outil adapté est retenu.

Ne fais pas tourner une suite de tests de plusieurs minutes à chaque commit.

Les contrôles lourds appartiennent plutôt au pré-push ou à la CI.

---

## 16. Gitignore

Crée ou audite un `.gitignore` adapté au projet.

Inclure selon le contexte :

- environnements virtuels ;
- caches Python ;
- caches de test ;
- caches lint/type checking ;
- `.env` et variantes privées ;
- logs ;
- base SQLite locale si non destinée à être versionnée ;
- médias locaux ;
- fichiers IDE ;
- fichiers OS ;
- builds ;
- couverture ;
- secrets/certificats locaux.

N’ignore pas `.env.example`.

N’ignore pas les migrations Django.

N’ignore pas un fichier important simplement parce qu’il change souvent.

---

## 17. Docker optionnel

Le projet doit pouvoir fonctionner **sans Docker** sauf demande contraire explicite.

Si les fichiers Docker sont souhaités, prépare-les comme une voie alternative.

Configuration typique :

- `Dockerfile`
- `compose.yaml`
- `.dockerignore`

Objectifs :

- environnement reproductible ;
- PostgreSQL local facile ;
- mêmes variables d’environnement ;
- versions explicites ;
- installation déterministe.

Le README doit proposer deux parcours :

### Sans Docker

- environnement virtuel ;
- installation des dépendances ;
- PostgreSQL ;
- variables ;
- migrations ;
- lancement.

### Avec Docker

- configuration ;
- build ;
- démarrage ;
- migrations ;
- logs ;
- arrêt.

Docker ne doit pas modifier la logique métier.

---

## 18. Sécurité du socle

Applique les bonnes pratiques Django actuelles et charge `django-security` s’il existe.

Au minimum :

- secrets hors dépôt ;
- `DEBUG=False` en production ;
- `ALLOWED_HOSTS` explicite ;
- protections CSRF conservées ;
- middleware de sécurité conservé ;
- cookies sécurisés en production lorsque HTTPS est utilisé ;
- HTTPS/redirect/HSTS évalués selon l’infrastructure ;
- pas d’exposition de stack trace en production ;
- pas de permissivité CORS inutile ;
- pas de wildcard dangereuse par défaut ;
- uploads non exécutables ;
- logs sans secrets.

Avant production, `manage.py check --deploy` ou l’équivalent adapté au projet doit faire partie des contrôles.

---

## 19. Documentation initiale obligatoire

La documentation est en français sauf demande contraire.

Initialise ou complète :

```text
README.md
PROJECT_TASKS.md
CHANGELOG.md
docs/
├── index.md
├── architecture/
│   ├── overview.md
│   └── decisions.md
├── features/
├── models/
├── security/
├── workflows/
└── glossary.md
```

Ne remplis pas artificiellement des dizaines de pages vides.

Crée les sections utiles au socle puis laisse les features enrichir le wiki.

### README minimum

Doit expliquer :

- rôle du projet ;
- prérequis ;
- version Python/Django ;
- installation sans Docker ;
- installation avec Docker si disponible ;
- configuration `.env` ;
- dev/test/prod ;
- base de données ;
- migrations ;
- lancement ;
- tests ;
- lint/formatage ;
- documentation ;
- règles Git essentielles ;
- emplacement des logs si pertinent.

---

## 20. AGENTS.md

Si `AGENTS.md` existe, conserve son contenu pertinent.

Ajoute ou vérifie une section expliquant :

- commandes réelles du projet ;
- skill `project-workflow` à utiliser pour les features ;
- skill `django-project-init` pour les audits/init du socle ;
- skills Django spécialisés disponibles ;
- environnement par défaut pour le local ;
- commande de test ;
- commande lint/format ;
- interdiction de commit/push sans demande explicite.

Ne copie pas tout le contenu des skills dans `AGENTS.md`.

---

## 21. PROJECT_TASKS et CHANGELOG

Si les fichiers n’existent pas, initialise-les avec les conventions du `project-workflow`.

Pendant l’init, les tâches possibles peuvent inclure :

- choix utilisateur/auth ;
- installation PostgreSQL ;
- settings ;
- tests ;
- pre-commit ;
- documentation ;
- Docker optionnel ;
- premier audit sécurité.

Ne marque pas une tâche terminée si elle ne l’est pas réellement.

---

## 22. Sauvegardes

Le socle doit être compatible avec une stratégie de sauvegarde.

La mise en œuvre dépend de l’infrastructure, mais documente dès maintenant que la production devra prévoir :

- sauvegarde quotidienne de la base ;
- sauvegarde quotidienne des médias si nécessaires ;
- rétention ;
- stockage séparé lorsque possible ;
- procédure de restauration ;
- test de restauration.

Ne crée pas de script de backup dépendant d’une infrastructure inconnue.

---

## 23. Contrôle de parité des environnements

Cherche la parité raisonnable entre local, staging et production.

### À garder similaire autant que possible

- moteur de base de données ;
- version de Python ;
- version de Django ;
- dépendances ;
- comportement des migrations ;
- configuration via environnement ;
- services structurants.

### Différences légitimes

- DEBUG ;
- outils de debug ;
- volume de logs ;
- endpoints de services externes ;
- secrets ;
- stockage ;
- cache ;
- email ;
- monitoring.

Documente les différences voulues.

---

## 24. Audit après initialisation

Après création ou normalisation du socle, effectue une deuxième relecture.

Vérifie :

- projet démarre ;
- settings dev fonctionnent ;
- settings test fonctionnent ;
- settings prod chargent sans fallback dangereux avec des variables factices adaptées ;
- migrations cohérentes ;
- tests lancés ;
- Ruff lancé ;
- pre-commit valide sa configuration si présent ;
- `.env` non suivi ;
- `.env.example` présent ;
- `.gitignore` pertinent ;
- aucun secret évident ;
- documentation lisible ;
- Docker optionnel cohérent s’il existe.

Ne prétends jamais qu’une commande a réussi sans l’avoir exécutée.

---

## 25. Definition of Done de l’initialisation

Le socle est considéré prêt lorsque les points applicables sont vrais :

- version Python supportée ;
- version Django supportée ;
- base de données choisie et documentée ;
- settings dev/test/prod séparés ;
- secrets externalisés ;
- `.env.example` présent ;
- `.gitignore` propre ;
- architecture de projet compréhensible ;
- modèle utilisateur décidé avant qu’il devienne coûteux à changer ;
- qualité/lint configurés ;
- tests exécutables ;
- pre-commit configuré si retenu ;
- README français exploitable ;
- documentation initiale présente ;
- fichiers de gouvernance présents ;
- Docker optionnel fonctionnel s’il est créé ;
- aucun contrôle critique rouge ;
- seconde relecture terminée.

Si un élément structurant est encore indécis, indique clairement que l’initialisation n’est pas totalement terminée.

---

## 26. Sortie finale

À la fin, résume :

### Socle créé ou conservé
Les principaux choix.

### Décisions à retenir
Exemples : PostgreSQL, custom user, settings, Docker.

### Commandes utiles
Seulement les commandes réellement valides pour ce dépôt.

### Vérifications exécutées
Avec leur résultat réel.

### Points restant à traiter
Uniquement ce qui est réellement en attente.

---

## 27. Principe anti-refactoring inutile

Avant chaque choix structurant, demande :

> Ce choix est-il simple aujourd’hui, cohérent avec Django, et suffisamment flexible pour les évolutions raisonnablement prévisibles ?

Évite les deux extrêmes :

- tout mettre dans un seul fichier/app parce que « c’est plus rapide » ;
- construire une architecture de grande entreprise pour une application encore simple.

Commence simple, avec de bonnes frontières, puis fais évoluer seulement lorsque le besoin apparaît.
