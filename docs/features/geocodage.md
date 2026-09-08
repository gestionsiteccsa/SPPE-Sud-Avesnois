# Géocodage des adresses et carte

Les fiches de structures avec une adresse sont placées automatiquement sur la carte OpenStreetMap du site. Aucune clé Google ni compte externe n'est nécessaire.

## Principe

1. Dans le tableau de bord, pendant la frappe de l'adresse, le formulaire propose jusqu'à 5 suggestions de la **Base Adresse Nationale** (service public français gratuit).
2. Choisir une suggestion remplit les coordonnées cachées (`latitude` / `longitude`) et affiche un point de contrôle sur une mini-carte OpenStreetMap.
3. Sans JavaScript ou sans suggestion choisie, les coordonnées sont calculées automatiquement côté serveur à l'enregistrement.
4. La carte publique (`/carte/`) affiche uniquement les fiches avec coordonnées et `Afficher sur le site` coché, via Leaflet servi localement.

## Ordre des services

1. **BAN** `api-adresse.data.gouv.fr` en premier (meilleure pour les adresses françaises, score minimum 0,5).
2. **Nominatim / OpenStreetMap** en repli si la BAN ne trouve rien.
3. Si aucun service ne trouve l'adresse, la fiche reste enregistrée sans coordonnées et n'apparaît pas sur la carte.

Les coordonnées déjà renseignées à la main ne sont jamais écrasées automatiquement. Le bouton **« Re-vérifier l'adresse sur la carte »** relance les suggestions, **« Effacer les coordonnées »** force un nouveau calcul à l'enregistrement.

## Rattrapage des fiches existantes

```bash
python manage.py geocode_structures --dry-run
python manage.py backup_sqlite backups/
python manage.py geocode_structures --export-ko geocodage-echecs-AAAA-MM-JJ.csv
```

- `--dry-run` compte et affiche sans rien enregistrer.
- Sans option, seules les fiches avec latitude ou longitude manquante sont complétées.
- `--export-ko fichier.csv` exporte les adresses introuvables (`;` séparateur) pour correction manuelle : faute de frappe, hameau, rue récente.
- Faire une sauvegarde avant le batch réel, comme pour un import.

## Confidentialité et limites

- Seule l'adresse tapée dans le dashboard est envoyée à la BAN, sans nom ni e-mail ni téléphone. Voir `privacy/overview.md`.
- Les suggestions passent par le serveur Django (`/dashboard/adresses/suggestions/`), limité à 60 requêtes/minute par utilisateur et réservé aux comptes autorisés. Aucun appel direct du navigateur vers un tiers, la Content Security Policy reste `connect-src 'self'`.
- La BAN ne connaît pas toujours les lieux-dits et les voies très récentes : corriger ces cas à la main après l'export des introuvables.
