# Checklist API Django

## Contrat
- [ ] Endpoint et méthode cohérents.
- [ ] Status codes corrects.
- [ ] Champs exposés minimisés.
- [ ] Champs système read-only.
- [ ] Erreurs structurées.

## Auth / permissions
- [ ] Authentication adaptée.
- [ ] Permissions explicites.
- [ ] QuerySet scoped.
- [ ] Permission objet.
- [ ] Create permissions.
- [ ] Tests négatifs.

## Données
- [ ] Serializer validation.
- [ ] Logique métier non dupliquée.
- [ ] Nested writes maîtrisées.
- [ ] Concurrence/idempotence analysées.

## Performance
- [ ] Pagination.
- [ ] Limite maximale.
- [ ] Pas de N+1.
- [ ] Filtres/orderings bornés.
- [ ] Gros exports traités correctement.

## Sécurité
- [ ] CORS si nécessaire seulement.
- [ ] CSRF si session auth.
- [ ] Pas de données sensibles.
- [ ] Upload/SSRF analysés si concernés.
- [ ] Throttling analysé.

## Évolution
- [ ] Versioning analysé.
- [ ] Dépréciation documentée si nécessaire.
- [ ] OpenAPI/docs à jour.

## Tests
- [ ] Auth.
- [ ] Permissions.
- [ ] Validation.
- [ ] Pagination.
- [ ] Champs sensibles.
- [ ] Idempotence si critique.
