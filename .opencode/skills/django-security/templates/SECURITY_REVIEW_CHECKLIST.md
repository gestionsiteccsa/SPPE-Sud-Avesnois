# Security Review Checklist

## Accès
- [ ] Authentification requise si nécessaire.
- [ ] Autorisation explicite.
- [ ] Permission objet.
- [ ] Tests utilisateur non propriétaire.
- [ ] Moindre privilège.

## Entrées / sorties
- [ ] Validation serveur.
- [ ] Pas de `safe`/`mark_safe` dangereux.
- [ ] ORM paramétré.
- [ ] Pas de shell non maîtrisé.
- [ ] Redirect contrôlé.

## Web
- [ ] Méthodes GET sans effets.
- [ ] CSRF.
- [ ] CORS minimal.
- [ ] Host validation.
- [ ] Cookies prod sécurisés.
- [ ] HTTPS/HSTS analysés.

## Fichiers
- [ ] Allowlist.
- [ ] Taille.
- [ ] Nom sûr.
- [ ] Stockage non exécutable.
- [ ] Permission de téléchargement.
- [ ] Archives/images/PDF analysés si pertinents.

## Réseau
- [ ] SSRF analysée.
- [ ] Protocoles limités.
- [ ] IP internes bloquées si nécessaire.
- [ ] Timeout.
- [ ] Redirections contrôlées.

## Secrets
- [ ] Aucun secret Git.
- [ ] `.env.example` propre.
- [ ] Secret scanner passé si configuré.

## Données
- [ ] Logs sans secret.
- [ ] PII minimisées.
- [ ] Champs système déterminés serveur.

## Production
- [ ] DEBUG false.
- [ ] ALLOWED_HOSTS explicite.
- [ ] `check --deploy`.
- [ ] Backups protégés.
- [ ] Admin protégé.

## Dépendances
- [ ] Nouvelles dépendances évaluées.
- [ ] Vulnérabilités critiques analysées.

## Tests
- [ ] Tests négatifs.
- [ ] Permissions.
- [ ] Security-specific tests pertinents.
