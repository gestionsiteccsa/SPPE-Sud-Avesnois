---
name: django-files-uploads
description: Sécurise les uploads, fichiers, images, téléchargements et stockages media dans Django.
compatibility: opencode
metadata:
  framework: django
  purpose: files-uploads
  language: fr
  workflow-parent: project-workflow
---

# Django Files & Uploads

## Mission
Gérer les uploads comme une surface de sécurité et de stockage à part entière.

## Principes
- `MEDIA_ROOT`/storage utilisateur est distinct de `STATIC_ROOT`.
- Ne jamais faire confiance au nom, extension, MIME déclaré ou contenu fourni par le client.
- Générer des noms de fichiers sûrs et éviter l'utilisation directe d'un nom utilisateur comme chemin.
- Aucun chemin utilisateur ne doit permettre une sortie du répertoire prévu.

## Validation
Définir selon le besoin :
- taille maximale ;
- extensions autorisées si pertinentes ;
- MIME réel si vérifiable ;
- dimensions d'image ;
- format ;
- nombre de fichiers ;
- quotas.
La validation doit être serveur.

## Images
- Décoder/re-encoder si nécessaire pour éliminer contenu inattendu.
- Analyser métadonnées EXIF, notamment géolocalisation, avec `privacy-rgpd`.
- Limiter dimensions et mémoire consommée.
- Se méfier des decompression bombs.

## Documents
PDF, Office, archives et formats complexes sont potentiellement actifs. Si le risque le justifie, isoler analyse/antivirus/sandbox plutôt que faire confiance à l'extension.

## Stockage
Choisir filesystem local, stockage objet ou service dédié selon le déploiement. Les fichiers privés nécessitent autorisation avant service, URL temporaire ou délégation contrôlée.

## Téléchargement
- `Content-Disposition` approprié.
- Type de contenu maîtrisé.
- Éviter l'exécution inline de contenu utilisateur potentiellement actif.
- Permissions objet systématiques pour fichiers privés.

## Nettoyage
Définir le cycle de vie des fichiers : remplacement, suppression modèle, fichiers orphelins, backups, rétention.

## Performance
Ne pas charger un gros fichier entièrement en mémoire si streaming/chunks suffisent. Les traitements lourds peuvent aller en tâche asynchrone.

## Tests
Tester taille, type, permission, path traversal, nom hostile, fichier vide, stockage temporaire et nettoyage.

## Questions utilisateur

Quand un choix métier ou UX est réellement nécessaire, pose au maximum deux questions à la fois, en langage accessible, avec une courte explication du pourquoi. Ne demande pas au non-développeur de choisir une technique quand une bonne pratique claire existe.

## Coordination

Lis `AGENTS.md` et charge `project-workflow`. Utilise `feature-design` avant toute évolution métier structurante. Charge les skills transversaux pertinents : `django-security`, `django-testing`, `django-performance`, `privacy-rgpd`, `accessibility`, `documentation`, `dependency-management`.

## Definition of Done

La feature n'est terminée que lorsque les comportements importants, permissions, erreurs, sécurité, tests, documentation et impacts techniques pertinents ont été revus.

## Principe final

Reste proportionné : utilise les abstractions Django et du Web lorsque possible, et n'ajoute pas de complexité sans valeur claire.
