## CI/CD

- Charger `ci-cd` pour toute création ou modification de pipeline.
- Réutiliser les mêmes commandes que les quality gates locaux.
- Les jobs de test ne doivent jamais recevoir les secrets production.
- Utiliser PostgreSQL en CI lorsque le comportement production en dépend.
- Toute livraison production doit avoir health check et rollback.
- Les migrations risquées nécessitent revue et backup gate.
- Ne pas automatiser un déploiement production non maîtrisé.
- Les fichiers de CI sont du code sensible et doivent être relus.
