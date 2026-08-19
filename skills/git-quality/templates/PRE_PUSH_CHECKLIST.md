# Checklist pré-push

## Git
- [ ] `git status` compris.
- [ ] Diff relu.
- [ ] Aucun fichier accidentel.
- [ ] Aucun debug temporaire.

## Quality
- [ ] Ruff lint.
- [ ] Ruff format check.
- [ ] Type checker si configuré.
- [ ] Django check.

## Database
- [ ] `makemigrations --check --dry-run`.
- [ ] Migrations relues.
- [ ] Pas de migration destructive inattendue.

## Tests
- [ ] Tests ciblés.
- [ ] Suite appropriée.
- [ ] Aucun test critique rouge.

## Security
- [ ] Secret scan.
- [ ] `.env` non tracked.
- [ ] Dependency audit.
- [ ] Prod check si pertinent.

## Project
- [ ] PROJECT_TASKS à jour.
- [ ] CHANGELOG à jour si nécessaire.
- [ ] Documentation à jour.
- [ ] README à jour si nécessaire.

## Décision
- [ ] Aucun blocker.
- [ ] Push explicitement demandé.
