## Authentification Django

- Charger `django-auth` pour toute feature liée aux comptes, inscription, login, reset, rôles, sessions, MFA ou SSO.
- Décider le modèle utilisateur et l’identifiant tôt dans le projet.
- Ne jamais gérer les mots de passe ou tokens avec une implémentation maison si Django fournit déjà le mécanisme.
- `is_staff` ne doit pas être utilisé comme rôle métier générique.
- Toute permission objet doit être validée côté serveur et testée.
- Les changements email, password, MFA et récupération de compte sont des opérations sensibles.
