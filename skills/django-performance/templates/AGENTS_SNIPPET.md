## Performance Django

- Charger `django-performance` pour toute feature manipulant listes, relations, gros volumes, agrégations, exports/imports, cache ou traitement coûteux.
- Mesurer avant toute optimisation non évidente.
- Chercher systématiquement les N+1 dans les boucles, templates, serializers et exports.
- Toute liste potentiellement volumineuse doit être paginée ou explicitement bornée.
- Le cache n’est utilisé qu’après analyse des requêtes et de l’invalidation.
- Ne pas ajouter Redis/Celery/moteur de recherche uniquement « pour la scalabilité » sans besoin réel.
