# Skill OpenCode — django-project-init

## Rôle

Ce skill initialise ou audite le socle d’un projet Django avant le développement des fonctionnalités.

Il est prévu pour fonctionner avec `project-workflow` comme chef d’orchestre, puis avec des skills plus spécialisés comme `django-security`, `django-testing` ou `django-database`.

## Installation

Copier :

```text
skills/django-project-init/
```

dans le dépôt OpenCode.

Le fichier principal doit être :

```text
skills/django-project-init/SKILL.md
```

## Utilisation

Le skill est pertinent lorsque tu demandes par exemple :

- d’initialiser un nouveau projet Django ;
- de préparer proprement un projet Django existant ;
- d’auditer le socle avant de commencer les features ;
- de mettre en place dev/test/prod ;
- de préparer PostgreSQL ;
- de préparer la qualité, les tests, la documentation et Docker optionnel.

## Philosophie

- bonnes pratiques sans sur-architecture ;
- PostgreSQL privilégié pour les projets destinés à la production ;
- Docker optionnel ;
- environnement classique toujours supporté ;
- secrets strictement hors Git ;
- documentation française ;
- environnements dev/test/prod ;
- questions accessibles à un non-développeur ;
- maximum deux questions à la fois ;
- aucune action Git de commit/push sans demande explicite.
