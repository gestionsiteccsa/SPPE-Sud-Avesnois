# Checklist Performance Django

## ORM
- [ ] Pas de requête dans une boucle sans justification.
- [ ] `select_related` analysé.
- [ ] `prefetch_related` analysé.
- [ ] Pas de prefetch massif inutile.
- [ ] Agrégations DB utilisées lorsque pertinent.
- [ ] Pas de chargement de champs/objets inutiles important.

## Volume
- [ ] Pagination/limite.
- [ ] Taille de page bornée.
- [ ] Export/import par batch si nécessaire.
- [ ] Pas de gros fichier chargé entièrement sans besoin.

## Database
- [ ] Index analysés.
- [ ] QuerySet.explain si requête réellement problématique.
- [ ] Pas de dénormalisation prématurée.

## Cache
- [ ] Cache réellement justifié.
- [ ] Invalidation définie.
- [ ] Clé tenant/user/permissions correcte.
- [ ] Aucun risque de fuite de données.

## Traitement
- [ ] Pas de CPU lourd dans requête web si évitable.
- [ ] Appels externes avec timeout.
- [ ] Appels répétitifs batchés/cachés si pertinent.
- [ ] Transactions courtes.

## Tests
- [ ] Test de N+1 si risque critique.
- [ ] Dataset suffisant pour révéler le problème.
- [ ] Mesure avant/après si optimisation notable.

## Documentation
- [ ] Décision perf structurante documentée.
