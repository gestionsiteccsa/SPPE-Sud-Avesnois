## API Django

- Charger `django-api` uniquement si le projet expose réellement une API.
- La logique métier doit rester partagée avec les autres points d’entrée et ne pas être dupliquée dans les serializers/views.
- Les QuerySets doivent être filtrés selon les permissions avant sérialisation.
- Ne jamais exposer automatiquement tous les champs sensibles d’un modèle.
- Toute liste potentiellement volumineuse doit être paginée.
- `AllowAny` doit être explicitement justifié.
- Les APIs publiques/partenaires doivent documenter leur contrat et leur stratégie de compatibilité.
