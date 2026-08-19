## Données Django

- Charger `django-database` pour toute modification significative des modèles, relations, contraintes, migrations, indexes ou transactions.
- PostgreSQL est la cible privilégiée lorsqu’un vrai environnement de production est prévu.
- Toute règle d’intégrité critique pouvant être garantie par la base doit être évaluée comme contrainte DB.
- Relire toute migration générée avant de la considérer valide.
- Ne pas modifier une migration déjà appliquée sur un environnement partagé sans stratégie explicite.
- Les migrations destructives ou massives nécessitent une analyse d’impact et, si pertinent, une sauvegarde préalable.
