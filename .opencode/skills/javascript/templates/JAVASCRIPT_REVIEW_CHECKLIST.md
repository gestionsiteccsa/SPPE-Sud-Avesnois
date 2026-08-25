# Checklist JavaScript

## Nécessité
- [ ] JavaScript apporte une vraie valeur.
- [ ] Progressive enhancement analysé.
- [ ] Pas de framework/bundler inutile.

## Structure
- [ ] Modules ES.
- [ ] Responsabilités cohérentes.
- [ ] Pas de global inutile.
- [ ] Hooks DOM stables (`data-*` si pertinent).

## Sécurité
- [ ] Pas de `eval`.
- [ ] Pas de `innerHTML` non maîtrisé.
- [ ] CSRF.
- [ ] URLs contrôlées.
- [ ] Pas de secret dans storage navigateur.

## Fetch
- [ ] `response.ok`.
- [ ] Erreurs réseau.
- [ ] Parsing correct.
- [ ] Abort/timeout si pertinent.
- [ ] Double soumission gérée.

## UX
- [ ] Loading.
- [ ] Success.
- [ ] Error.
- [ ] Focus.
- [ ] Clavier.
- [ ] Reduced motion si animation.

## Performance
- [ ] Pas de listeners inutiles.
- [ ] Pas de polling excessif.
- [ ] Pas de dépendance lourde injustifiée.
- [ ] Page-specific loading si utile.

## Projet
- [ ] Static Django.
- [ ] Tests pertinents.
- [ ] Debug retiré.
- [ ] Documentation si nécessaire.
