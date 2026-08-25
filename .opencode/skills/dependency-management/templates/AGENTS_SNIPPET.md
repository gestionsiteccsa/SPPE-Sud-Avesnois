## Dependency Management

- Charger `dependency-management` lors de tout ajout, suppression ou mise à jour de package.
- Respecter le gestionnaire déjà choisi par le projet.
- Ne pas ajouter une dépendance si Django/Python répond déjà proprement au besoin.
- Vérifier maintenance, compatibilité, sécurité et impact avant une dépendance structurante.
- Maintenir manifestes et lockfiles cohérents.
- Avant push/release, analyser les vulnérabilités connues.
- Une simple nouvelle version disponible ne bloque pas un push.
- Une vulnérabilité critique applicable, une résolution cassée ou un lock incohérent peut le bloquer.
