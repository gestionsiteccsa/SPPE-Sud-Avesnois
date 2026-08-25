# Checklist Auth Django

## Modèle
- [ ] Custom user justifié.
- [ ] Identifiant principal clair.
- [ ] Email/username unicité définie.
- [ ] Profil métier séparé si nécessaire.
- [ ] `AUTH_USER_MODEL` utilisé dans les relations.

## Inscription
- [ ] Mode ouvert/invitation défini.
- [ ] Champs minimisés.
- [ ] Password via API Django.
- [ ] Vérification email décidée.
- [ ] Rate limiting analysé.

## Connexion
- [ ] Backend clair.
- [ ] Enumeration analysée.
- [ ] Compte désactivé refusé.
- [ ] Session configurée.
- [ ] Brute force analysé.

## Reset
- [ ] Mécanisme Django/standard.
- [ ] Token limité.
- [ ] Enumeration maîtrisée.
- [ ] HTTPS/domain correct.

## Permissions
- [ ] Rôles métier clairs.
- [ ] Pas de confusion staff/superuser.
- [ ] Permissions objet.
- [ ] Tests négatifs.

## Compte
- [ ] Changement email sécurisé.
- [ ] Suspension définie.
- [ ] Suppression/anonymisation définie.
- [ ] MFA évaluée si critique.

## Sécurité
- [ ] Aucun password/token loggé.
- [ ] Secrets externes.
- [ ] Actions sensibles auditables.
- [ ] Docs à jour.
