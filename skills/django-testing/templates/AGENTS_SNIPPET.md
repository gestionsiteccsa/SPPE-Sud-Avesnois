## Tests Django

- Charger `django-testing` pour toute nouvelle logique métier, bug, permission, migration risquée ou refactoring significatif.
- Appliquer un TDD pragmatique : test d’abord lorsqu’il protège un comportement réel.
- Ne pas écrire de tests triviaux uniquement pour augmenter la couverture.
- Toute permission importante doit avoir un test négatif.
- Toute correction de bug doit recevoir un test de régression lorsque reproductible.
- Les tests doivent être indépendants et déterministes.
- Ne jamais affirmer que toute la suite passe si seule une partie a été exécutée.
