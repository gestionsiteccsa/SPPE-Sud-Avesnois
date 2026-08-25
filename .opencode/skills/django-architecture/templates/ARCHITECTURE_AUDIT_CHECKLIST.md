# Checklist d’audit d’architecture Django

## Apps
- [ ] Chaque app a une responsabilité explicable en une phrase.
- [ ] Pas d’app par modèle sans raison métier.
- [ ] Pas d’app `core` devenue fourre-tout.
- [ ] Pas de dépendances circulaires non justifiées.

## Modèles
- [ ] Les modèles contiennent les comportements intrinsèques pertinents.
- [ ] Aucun God Model évident.
- [ ] Les invariants importants sont protégés au niveau adapté.

## Vues
- [ ] Les vues restent des points d’entrée.
- [ ] Pas de logique métier longue dupliquée.
- [ ] Permissions clairement identifiables.

## Requêtes
- [ ] QuerySets/Managers utilisés pour les lectures réutilisables.
- [ ] Selectors uniquement si la complexité le justifie.

## Services
- [ ] Chaque service orchestre une vraie opération métier.
- [ ] Pas de wrapper inutile.
- [ ] Transactions clairement définies.

## Signaux
- [ ] Pas de workflow métier principal caché dans des signaux.
- [ ] Les signaux importants sont documentés.

## Fichiers
- [ ] Aucun fichier monolithique difficile à parcourir.
- [ ] Pas de fragmentation excessive.

## Documentation
- [ ] Overview à jour.
- [ ] ADR/decisions à jour si nécessaire.
- [ ] Diagrammes cohérents avec le code réel.
