## Initialisation et workflow Django

- Pour une nouvelle feature, une évolution métier, un bug significatif ou un refactoring : charger `project-workflow`.
- Pour initialiser ou auditer le socle Django : charger `django-project-init`.
- Charger ensuite les skills spécialisés pertinents selon la tâche.
- Ne pas modifier une décision d’architecture structurante sans vérifier la documentation dans `docs/architecture/`.
- Ne jamais créer de commit ou effectuer de push sans demande explicite de l’utilisateur.
- Avant un push demandé, exécuter les quality gates définis par le projet et bloquer en cas d’échec critique.
