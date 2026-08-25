---
name: django-forms
description: Conçoit et audite les formulaires Django, ModelForms, validations, formsets, erreurs, UX et sécurité.
compatibility: opencode
metadata:
  framework: django
  purpose: forms
  language: fr
  workflow-parent: project-workflow
---

# Django Forms

## Mission
Concevoir les formulaires Django comme une frontière de validation fiable et une interface utilisateur claire.

## Choix Form / ModelForm
- `ModelForm` quand un formulaire édite naturellement un modèle.
- `Form` pour recherche, filtres, workflows multi-modèles ou actions.
- Ne jamais utiliser `fields = "__all__"` sur un modèle contenant des champs système, propriétaires, permissions ou statuts protégés.
- Les valeurs `owner`, `created_by`, rôle, statut protégé et données calculées sont déterminées côté serveur.

## Validation
- Utiliser les validateurs de champs pour les contraintes locales.
- `clean_<field>()` pour une règle centrée sur un champ.
- `clean()` pour cohérence multi-champs.
- La règle métier réutilisable doit vivre dans un service/domaine commun plutôt que dans trois formulaires.
- Ne pas faire confiance à la validation JavaScript.

## Erreurs et UX
- Messages compréhensibles et proches des champs.
- Résumé d'erreurs pour les formulaires complexes.
- Conserver les données saisies après erreur.
- Labels visibles, help text utile, autocomplete et types HTML appropriés.
- Ne pas utiliser le placeholder comme label.

## Formsets
Utiliser formsets/inlines pour plusieurs formulaires similaires. Pour les formsets dynamiques, préserver management form, index, suppression, limites et validation serveur.

## Uploads
Pour un champ fichier, charger `django-files-uploads`. Le formulaire ne constitue jamais à lui seul la sécurité de fichier.

## Transactions
Si un submit crée/modifie plusieurs objets liés, utiliser une opération métier transactionnelle lorsque nécessaire. Les effets externes sont déclenchés après commit quand approprié.

## Sécurité
CSRF obligatoire pour POST avec session. Aucun champ caché contrôlé par le client ne doit devenir une permission.

## Tests
Tester les validations métier, cas limites, droits, erreurs et transactions. Ne pas tester que `CharField(required=True)` refuse le vide sans personnalisation.

## Questions utilisateur

Quand un choix métier ou UX est réellement nécessaire, pose au maximum deux questions à la fois, en langage accessible, avec une courte explication du pourquoi. Ne demande pas au non-développeur de choisir une technique quand une bonne pratique claire existe.

## Coordination

Lis `AGENTS.md` et charge `project-workflow`. Utilise `feature-design` avant toute évolution métier structurante. Charge les skills transversaux pertinents : `django-security`, `django-testing`, `django-performance`, `privacy-rgpd`, `accessibility`, `documentation`, `dependency-management`.

## Definition of Done

La feature n'est terminée que lorsque les comportements importants, permissions, erreurs, sécurité, tests, documentation et impacts techniques pertinents ont été revus.

## Principe final

Reste proportionné : utilise les abstractions Django et du Web lorsque possible, et n'ajoute pas de complexité sans valeur claire.
