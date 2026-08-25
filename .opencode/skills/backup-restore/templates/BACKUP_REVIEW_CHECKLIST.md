# Checklist Backup

## Périmètre
- [ ] PostgreSQL.
- [ ] Media non régénérables.
- [ ] Rôles/extensions documentés.
- [ ] Autres données critiques identifiées.

## Automatisation
- [ ] Backup quotidien.
- [ ] Job observable.
- [ ] Pas de secret dans script.
- [ ] Pas de jobs concurrents.

## Stockage
- [ ] Permissions strictes.
- [ ] Espace disque surveillé.
- [ ] Copie hors serveur si possible.
- [ ] Chiffrement analysé.
- [ ] Rétention définie.

## Validation
- [ ] Code retour.
- [ ] Archive lisible.
- [ ] Taille cohérente.
- [ ] Checksum.
- [ ] Copie distante vérifiée.

## Restore
- [ ] Runbook documenté.
- [ ] Restore test réussi.
- [ ] Smoke tests après restore.
- [ ] Compatibilité code/schema connue.

## Monitoring
- [ ] Dernier backup réussi connu.
- [ ] Échec signalé.
- [ ] Dernier restore test connu.
