## Tailwind CSS

- Charger `tailwind-css` uniquement si le projet utilise Tailwind.
- Toujours vérifier la version Tailwind avant de modifier sa configuration.
- Pour Tailwind v4, privilégier les mécanismes v4 plutôt que des recettes v3 obsolètes.
- Éviter les noms de classes construits dynamiquement qui ne peuvent pas être détectés au build.
- Réutiliser les composants Django plutôt que dupliquer de longues combinaisons de classes.
- Les valeurs arbitraires doivent rester ponctuelles.
- Toute feature UI doit rester responsive et accessible.
- Ne pas ajouter Vite/PostCSS/Node si le pipeline existant n’en a pas besoin.
