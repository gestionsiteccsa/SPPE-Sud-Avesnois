# Checklist de revue Database

## Modèle
- [ ] Les entités et relations représentent le métier.
- [ ] Optionalité explicite.
- [ ] Unicités métier identifiées.
- [ ] `on_delete` justifié.
- [ ] Pas de JSON utilisé pour cacher une relation importante.

## Intégrité
- [ ] Contraintes DB pertinentes.
- [ ] Validation applicative pertinente.
- [ ] Concurrence analysée.
- [ ] Pas de compteur critique non atomique.

## Migration
- [ ] Migration générée.
- [ ] Migration relue.
- [ ] Pas d’opération destructive inattendue.
- [ ] Données existantes prises en compte.
- [ ] Reverse défini lorsque réaliste.
- [ ] Locks/volume analysés si nécessaire.

## Performance
- [ ] Index justifiés par des requêtes réelles.
- [ ] Index composites/conditionnels analysés si nécessaire.
- [ ] Aucune dénormalisation prématurée.

## Tests
- [ ] Contraintes testées.
- [ ] Suppressions importantes testées.
- [ ] Migration de données testée si risquée.
- [ ] Transactions/concurrence testées si critiques.

## Documentation
- [ ] Documentation modèles mise à jour.
- [ ] Diagrammes à jour.
- [ ] Décision structurante documentée.
