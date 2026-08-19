# Checklist Frontend Django

## Structure
- [ ] HTML sémantique.
- [ ] Titre principal clair.
- [ ] Hiérarchie des headings.
- [ ] Navigation cohérente.

## Formulaires
- [ ] Labels associés.
- [ ] Champs requis identifiables.
- [ ] Help text pertinent.
- [ ] Erreurs par champ.
- [ ] Erreurs globales si nécessaire.
- [ ] CSRF.
- [ ] Validation serveur.

## Accessibilité
- [ ] Navigation clavier.
- [ ] Focus visible.
- [ ] Ordre de focus logique.
- [ ] Images alt.
- [ ] Boutons/liens sémantiques.
- [ ] ARIA seulement si nécessaire.
- [ ] Information non dépendante uniquement de couleur.

## Responsive
- [ ] Mobile.
- [ ] Intermédiaire.
- [ ] Desktop.
- [ ] Tables/menus utilisables.

## JavaScript
- [ ] JS réellement nécessaire.
- [ ] Pas de données utilisateur injectées dangereusement.
- [ ] États loading/error.
- [ ] Double soumission gérée.
- [ ] Fallback/progressive enhancement analysé.

## Static
- [ ] `{% static %}` utilisé.
- [ ] Assets namespacés si app.
- [ ] Media séparés.
- [ ] Pas de fichier utilisateur dans static.

## Performance
- [ ] Pas de JS/CSS disproportionné.
- [ ] Images raisonnables.
- [ ] Pas de N+1 caché dans template.

## Sécurité
- [ ] Permissions backend.
- [ ] Pas de `safe` non justifié.
- [ ] Redirects contrôlés.
- [ ] Uploads traités par security skill.

## Documentation
- [ ] Composant important documenté.
- [ ] Décision framework documentée.
