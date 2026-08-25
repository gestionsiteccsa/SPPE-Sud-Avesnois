# Références d’architecture Django — base 2026-08-15

Ce document sert de contexte. Lorsqu’une décision dépend d’une version précise, vérifier la documentation officielle de la version réellement utilisée.

## Applications Django

La documentation officielle décrit une application Django comme un package Python destiné à fournir un ensemble de fonctionnalités et pouvant contenir modèles, vues, templates, URLs, fichiers statiques, etc.

Conséquence retenue : une app doit représenter une responsabilité/capacité cohérente, pas simplement une table.

## Modèles

La documentation officielle présente un modèle comme la source définitive d’information sur les données qu’il représente.

Conséquence retenue : ne pas vider artificiellement les modèles de tout comportement uniquement pour appliquer une architecture en couches.

## Managers / QuerySets

Les Managers constituent l’interface des opérations de requête des modèles.

Conséquence retenue : utiliser Managers/QuerySets pour la logique de lecture et de requête réutilisable avant d’introduire une couche de repository générique.

## Transactions

`transaction.atomic()` permet de garantir l’atomicité d’un bloc de base de données.

Conséquence retenue : les services d’écriture multi-entités doivent identifier clairement leurs frontières transactionnelles.

## Signaux

Django fournit un dispatcher de signaux pour notifier des receivers découplés.

Conséquence retenue : les signaux sont utiles pour des réactions découplées, mais le cœur obligatoire d’un workflow doit rester explicite lorsque cela améliore la traçabilité.

## Templates par application

La documentation/tutoriel Django recommande de placer les templates propres à une application dans son répertoire de templates afin de faciliter notamment la réutilisabilité.

## Reusable apps

Django documente explicitement la création d’applications réutilisables.

Conséquence retenue : conserver autant que possible des frontières d’app claires et éviter les dépendances inutiles au projet global.
