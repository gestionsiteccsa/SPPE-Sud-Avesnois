# Checklist de revue des tests Django

## Valeur
- [ ] Chaque test protège un comportement réel.
- [ ] Pas de test trivial du framework.
- [ ] Pas de test ajouté uniquement pour coverage.

## Métier
- [ ] Règles importantes couvertes.
- [ ] Cas limites pertinents.
- [ ] Erreurs attendues.

## Sécurité
- [ ] Anonyme refusé si nécessaire.
- [ ] Mauvais utilisateur refusé.
- [ ] Mauvais rôle refusé.
- [ ] Propriétaire/bon rôle autorisé.

## Données
- [ ] Contraintes importantes testées.
- [ ] Transaction/concurrence si critique.
- [ ] Migration risquée testée.

## Qualité
- [ ] Tests indépendants.
- [ ] Pas de dépendance à l’ordre.
- [ ] Pas de réseau réel.
- [ ] Fixtures petites.
- [ ] Pas de mocks inutiles.
- [ ] Pas de flaky test connu.

## Performance
- [ ] Suite ciblée rapide.
- [ ] Tests lents identifiés.
- [ ] N+1 critique protégé si pertinent.

## Fin
- [ ] Tests réellement exécutés.
- [ ] Résultat documenté.
