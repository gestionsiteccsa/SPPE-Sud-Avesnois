## Sécurité Django

- Charger `django-security` pour toute feature exposant des données, permissions, authentification, formulaire, API, upload, URL externe ou configuration production.
- La sécurité est secure-by-default et applique le moindre privilège.
- Toute action sur une ressource doit vérifier l’accès à l’objet, pas uniquement l’authentification.
- Aucun secret ne doit être versionné.
- Ne jamais désactiver CSRF, protections XSS ou middleware de sécurité uniquement pour contourner un problème de développement.
- Les risques CRITIQUES et ÉLEVÉS connus bloquent le push par défaut.
- Les tests de permission doivent inclure des chemins négatifs.
