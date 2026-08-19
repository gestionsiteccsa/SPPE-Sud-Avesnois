---
name: django-i18n
description: Conçoit l’internationalisation Django : langues, traductions, formats, URLs, dates et fuseaux horaires.
compatibility: opencode
metadata:
  framework: django
  purpose: i18n
  language: fr
  workflow-parent: project-workflow
---

# Django i18n / l10n

## Mission
Gérer proprement langues, traductions, formats locaux et fuseaux horaires.

## Django i18n
Utiliser les mécanismes Django :
- gettext ;
- `{% trans %}` ;
- catalogues ;
- LocaleMiddleware si nécessaire.
Ne concaténer pas des fragments de phrases traduites de façon fragile.

## Langue
Définir langues supportées, langue par défaut et stratégie :
- préférence utilisateur ;
- session/cookie ;
- URL ;
- header navigateur.

## URLs
N'utiliser des URLs préfixées par langue que si cela apporte une vraie valeur au produit/SEO.

## Formats
Dates, nombres et devises doivent suivre la locale d'affichage sans modifier les valeurs stockées.

## Timezone
Stocker des instants de façon cohérente et afficher dans la timezone prévue. Pour une app multi-zone, définir clairement la timezone utilisateur.

## Textes UI
Prévoir l'allongement des traductions. Ne coder pas des conteneurs fixes basés sur le français.

## Pluriels
Utiliser les mécanismes de pluralisation, pas des `s` concaténés.

## JavaScript
Si le JS contient du texte utilisateur, utiliser la stratégie i18n du projet plutôt que dupliquer un second catalogue incohérent.

## Emails
Traduire selon la langue du destinataire si le métier le nécessite.

## Tests
Tester changement de langue, formats et frontières timezone seulement là où c'est métier.

## Questions utilisateur

Quand un choix métier ou UX est réellement nécessaire, pose au maximum deux questions à la fois, en langage accessible, avec une courte explication du pourquoi. Ne demande pas au non-développeur de choisir une technique quand une bonne pratique claire existe.

## Coordination

Lis `AGENTS.md` et charge `project-workflow`. Utilise `feature-design` avant toute évolution métier structurante. Charge les skills transversaux pertinents : `django-security`, `django-testing`, `django-performance`, `privacy-rgpd`, `accessibility`, `documentation`, `dependency-management`.

## Definition of Done

La feature n'est terminée que lorsque les comportements importants, permissions, erreurs, sécurité, tests, documentation et impacts techniques pertinents ont été revus.

## Principe final

Reste proportionné : utilise les abstractions Django et du Web lorsque possible, et n'ajoute pas de complexité sans valeur claire.
