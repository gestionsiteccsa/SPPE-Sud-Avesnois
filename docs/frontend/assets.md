# Ressources frontend

Les dépendances visibles en production sont auto-hébergées afin d'éviter les CDN et l'exécution de Tailwind dans le navigateur.

## Source et build

- `static/css/tailwind_input.css` déclare les sources Tailwind ;
- `static/css/tokens.css` et `static/css/base.css` alimentent `app.min.css` ;
- les scripts applicatifs alimentent `static/js/bundle.min.js` ;
- les bibliothèques et la police sont copiées de `node_modules` vers `static/vendor`.

Pour reconstruire exactement les artefacts :

```bash
npm ci
python build_assets.py
```

Le lockfile `package-lock.json` et les versions exactes de `package.json` sont la source de vérité. Après une mise à jour :

```bash
npm audit
python manage.py collectstatic --dry-run --noinput --verbosity 0
python manage.py test
```

Relisez ensuite le diff de `static/`. Les fichiers générés sont versionnés parce que Node.js n'est pas requis sur l'hébergement mutualisé.

## Conventions Tailwind v4

- une variable CSS de taille de texte s'écrit `text-[length:var(--fs-...)]` afin que Tailwind ne l'interprète pas comme une couleur ;
- pour annuler `-translate-x-full` à partir d'un breakpoint, utiliser par exemple `md:translate-x-0` : `transform-none` ne remet pas la propriété CSS `translate` à zéro avec Tailwind v4 ;
- le reset de `base.css` est compilé dans `@layer base` afin que les utilitaires gardent la priorité sur les marges, dimensions, espacements et tailles typographiques ;
- `build_assets.py` vérifie ces invariants après chaque compilation.

## Dépendance externe restante

La carte demande ses tuiles à OpenStreetMap. Conserver l'attribution visible et respecter la politique d'utilisation du fournisseur. Une indisponibilité des tuiles ne doit pas empêcher les listes et fiches de fonctionner.

## Limite de sécurité

Une Content Security Policy par nonce est appliquée aux pages applicatives (scripts strictes via nonce) et à l'admin Django, qui reçoit une politique assouplie sur les scripts (`'unsafe-inline'`) car ses templates internes ne portent pas de nonce.
