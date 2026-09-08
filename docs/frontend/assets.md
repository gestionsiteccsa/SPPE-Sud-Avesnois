# Ressources frontend

Les dépendances visibles en production sont auto-hébergées afin d'éviter les CDN et l'exécution de Tailwind dans le navigateur. En production, les fichiers de `STATIC_ROOT` sont servis par WhiteNoise (`whitenoise.middleware.WhiteNoiseMiddleware`) sous `/static/`, sans configuration Apache/Passenger dédiée.

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

En cas d'échec d'esbuild, `build_assets.py` affiche le message d'erreur du binaire (commande, code et `stderr`) au lieu d'une erreur nue. Le lanceur détecte automatiquement si `bin/esbuild` est le shim JS (via `node`) ou le binaire natif installé par le postinstall (exécution directe) ; vérifiez d'abord que `node_modules/esbuild/bin/esbuild --version` répond (sinon, relancer `npm ci`).

Reproductibilité Windows/Linux : les copies vendor texte sont normalisées en LF, esbuild reçoit son entrée en binaire et les artefacts sont écrits en LF ; `.gitattributes` (`* text=auto`) fige cette convention. Le contrôle CI `git diff --exit-code -- static` exige un rebuild strictement identique.

## Conventions Tailwind v4

- une variable CSS de taille de texte s'écrit `text-[length:var(--fs-...)]` afin que Tailwind ne l'interprète pas comme une couleur ;
- pour annuler `-translate-x-full` à partir d'un breakpoint, utiliser par exemple `md:translate-x-0` : `transform-none` ne remet pas la propriété CSS `translate` à zéro avec Tailwind v4 ;
- le reset de `base.css` est compilé dans `@layer base` afin que les utilitaires gardent la priorité sur les marges, dimensions, espacements et tailles typographiques ;
- `build_assets.py` vérifie ces invariants après chaque compilation.

## Dépendance externe restante

La carte propose deux fonds via le sélecteur en haut à droite : « Plan » (OpenStreetMap, affiché par défaut) et « Satellite » (Esri World Imagery). Conserver les attributions visibles et respecter la politique d'utilisation de chaque fournisseur. Une indisponibilité des tuiles ne doit pas empêcher les listes et fiches de fonctionner.

## Limite de sécurité

Une Content Security Policy par nonce est appliquée aux pages applicatives (scripts strictes via nonce) et à l'admin Django, qui reçoit une politique assouplie sur les scripts (`'unsafe-inline'`) car ses templates internes ne portent pas de nonce.
