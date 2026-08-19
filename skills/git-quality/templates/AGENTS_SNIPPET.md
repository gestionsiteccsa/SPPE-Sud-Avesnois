## Git et quality gates

- Charger `git-quality` pour les opérations de qualité, pre-commit, préparation de commit et demande de push.
- Ne jamais exécuter `git commit` ou `git push` sans demande explicite de l’utilisateur.
- Avant tout push demandé, exécuter les quality gates définis par le projet.
- Bloquer le push si un secret, un test critique rouge, une migration manquante/cassée, une erreur Django critique ou une vulnérabilité exploitable critique subsiste.
- Les warnings mineurs doivent être signalés sans bloquer automatiquement.
- Les dépendances ne sont jamais toutes mises à jour automatiquement avant un push.
