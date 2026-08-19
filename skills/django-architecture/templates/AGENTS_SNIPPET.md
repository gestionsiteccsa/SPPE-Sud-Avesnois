## Architecture Django

- Pour toute décision de découpage ou de placement de logique Django, charger `django-architecture`.
- Le skill `project-workflow` reste responsable du cadrage global de la feature.
- Ne créer une nouvelle app Django que pour une responsabilité métier cohérente.
- Utiliser d’abord les mécanismes Django natifs ; ajouter services/selectors/couches supplémentaires seulement lorsqu’ils apportent une valeur réelle.
- Éviter à la fois les fichiers monolithiques et les micro-fichiers artificiels.
- Documenter les décisions structurantes dans `docs/architecture/decisions.md`.
