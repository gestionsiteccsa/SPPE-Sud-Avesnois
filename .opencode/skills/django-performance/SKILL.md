---
name: django-performance
description: Analyse et optimise les performances d’un projet Django sans optimisation prématurée. À utiliser lorsqu’une feature manipule des listes, relations, volumes importants, requêtes complexes, cache, exports, imports ou traitements coûteux, ou lorsqu’une lenteur est observée. Détecte N+1, requêtes inutiles, mauvais chargements ORM, pagination absente, index pertinents, cache mal conçu et traitements trop lourds, puis mesure avant d’optimiser.
compatibility: opencode
metadata:
  framework: django
  purpose: performance
  language: fr
  workflow-parent: project-workflow
---

# Django Performance

## 1. Mission

Tu es responsable de la performance applicative du projet Django.

Ton objectif est de :

- détecter les problèmes réels ou très probables ;
- mesurer avant d’optimiser ;
- réduire les requêtes inutiles ;
- éviter les N+1 ;
- contrôler les volumes chargés ;
- utiliser les index de façon pertinente ;
- introduire le cache uniquement lorsqu’il apporte une valeur réelle ;
- préserver la lisibilité et la maintenabilité.

Principe :

> N’optimise pas ce qui n’est pas un problème, mais ne laisse pas une feature manifestement coûteuse entrer en production sans analyse.

---

## 2. Coordination

Avant une optimisation :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. inspecte la feature et les requêtes ;
4. charge si disponibles :
   - `django-architecture`
   - `django-database`
   - `django-testing`
   - `django-security`
   - `django-api`

Ne modifie pas le schéma ou l’architecture sans coordination avec les skills concernés.

---

## 3. Quand analyser la performance

Analyse systématiquement lorsqu’une feature :

- affiche une liste ;
- traverse plusieurs relations ;
- effectue des agrégations ;
- exporte beaucoup de données ;
- importe beaucoup de lignes ;
- lance des boucles sur QuerySets ;
- sert une API paginée ;
- génère des fichiers ;
- effectue du reporting ;
- utilise du cache ;
- appelle plusieurs services externes ;
- exécute des tâches longues.

Pour une petite vue simple, ne crée pas un audit lourd.

---

## 4. Mesurer avant d’optimiser

Avant une optimisation non évidente, mesure.

Outils possibles selon environnement :

- nombre de requêtes ;
- durée des requêtes ;
- Django Debug Toolbar en local si déjà adaptée au projet ;
- logs SQL ciblés ;
- `QuerySet.explain()` ;
- `EXPLAIN` PostgreSQL ;
- profiling Python ;
- métriques applicatives.

Ne garde pas un logging SQL verbeux en production sans raison.

---

## 5. N+1

Le N+1 est un risque majeur dans Django.

Exemple conceptuel :

```python
for ship in Ship.objects.all():
    print(ship.manufacturer.name)
```

Si `manufacturer` n’est pas préchargé, une requête supplémentaire peut être faite par ligne.

Détecte ce pattern dans :

- vues ;
- serializers ;
- templates ;
- admin ;
- exports ;
- tâches.

---

## 6. `select_related`

Utilise `select_related()` pour les relations simples basées sur jointure, notamment :

- `ForeignKey`
- `OneToOneField`

Quand plusieurs relations sont toujours nécessaires, charge-les en une requête lorsque cela reste raisonnable.

Ne fais pas `select_related()` sur tout « au cas où ».

---

## 7. `prefetch_related`

Utilise `prefetch_related()` pour :

- many-to-many ;
- relations inverses ;
- ensembles multiples ;
- préchargements personnalisés.

Comprends que cela déclenche des requêtes supplémentaires mais évite une requête par objet.

Utilise `Prefetch` si :

- filtre spécifique ;
- queryset optimisé ;
- destination personnalisée.

---

## 8. Ne pas précharger inutilement

Un prefetch massif peut être pire qu’un N+1 léger sur une petite page.

Analyse :

- taille de page ;
- cardinalité ;
- mémoire ;
- champs réellement utilisés.

Ne précharge pas des milliers d’objets liés inutiles.

---

## 9. QuerySets paresseux

Comprends l’évaluation paresseuse des QuerySets.

Évite les évaluations répétées inutiles :

```python
if queryset:
    ...
for item in queryset:
    ...
```

Selon le besoin, réutilise le cache du QuerySet ou utilise la méthode adaptée.

---

## 10. `exists()`

Utilise `exists()` lorsque tu as seulement besoin de savoir si au moins une ligne existe et que le QuerySet ne sera pas ensuite entièrement consommé.

Ne l’utilise pas mécaniquement si le QuerySet sera immédiatement évalué : cela peut ajouter une requête.

---

## 11. `count()`

Utilise `count()` pour compter côté DB lorsque tu n’as pas besoin de charger les objets.

Si les objets sont déjà chargés, `len()` peut éviter une nouvelle requête.

Choisis selon le contexte.

---

## 12. `values()` et `values_list()`

Quand tu n’as besoin que de quelques champs :

- `values()`
- `values_list()`

peuvent éviter de construire des modèles complets.

Ne les utilise pas si cela rend le code métier illisible ou si les méthodes du modèle sont nécessaires.

---

## 13. `only()` et `defer()`

Utilise-les avec prudence.

Ils peuvent réduire les données transférées mais provoquer des requêtes différées supplémentaires si un champ est ensuite accédé.

Ne les introduis pas sans mesure.

---

## 14. Agrégations

Préférer les agrégations SQL lorsque la base peut faire efficacement :

- count ;
- sum ;
- avg ;
- min/max ;
- annotations.

Évite :

```python
sum(obj.amount for obj in queryset)
```

si la base peut retourner directement l’agrégat sans charger toutes les lignes.

---

## 15. Annotations

Utilise `annotate()` lorsque le calcul appartient naturellement à la requête.

Attention aux jointures qui multiplient les lignes et faussent certains agrégats.

Teste le SQL/résultat sur les cas complexes.

---

## 16. Sous-requêtes

`Subquery`, `Exists`, `OuterRef` peuvent remplacer certains traitements Python ou requêtes répétées.

Mais une requête SQL très complexe n’est pas automatiquement plus rapide.

Mesure avec `explain()` lorsque nécessaire.

---

## 17. Boucles et requêtes

Pendant une revue, cherche explicitement :

```text
for / while
  -> appel ORM
```

Ce pattern mérite une analyse.

Solutions possibles :

- prefetch ;
- bulk ;
- annotation ;
- requête groupée ;
- dictionnaire préchargé.

---

## 18. Bulk operations

Pour beaucoup d’écritures :

- `bulk_create`
- `bulk_update`
- `QuerySet.update`

peuvent réduire fortement le coût.

Mais vérifie les conséquences :

- `save()` ;
- signaux ;
- validation ;
- logique métier.

Charge `django-database`.

---

## 19. Pagination obligatoire selon volume

Toute liste potentiellement importante doit avoir une stratégie de pagination ou de limitation.

Django fournit `Paginator`.

Ne renvoie pas 50 000 objets simplement parce que la base peut les retourner.

Pour une API, charge `django-api`.

---

## 20. Taille de page

Choisis une taille raisonnable selon :

- poids de chaque objet ;
- relations ;
- interface ;
- latence.

Évite les valeurs énormes.

Autoriser l’utilisateur à choisir la taille doit avoir une limite maximale.

---

## 21. Pagination par offset

La pagination classique basée sur offset convient à beaucoup de cas.

Sur des volumes très importants ou des pages très profondes, elle peut devenir coûteuse.

Analyse alors une pagination de type cursor/keyset si l’usage le justifie.

Ne complexifie pas un projet normal inutilement.

---

## 22. Ordering stable

Une pagination doit utiliser un ordre stable.

Si le champ de tri n’est pas unique, ajoute un tie-breaker stable lorsque nécessaire.

Exemple :

```text
created_at, id
```

Cela évite les doublons/manques entre pages.

---

## 23. Index

Avant d’ajouter un index :

- identifier la requête ;
- identifier les filtres ;
- identifier l’ordre ;
- vérifier la sélectivité ;
- vérifier les indexes existants.

Charge `django-database`.

Un index non utilisé coûte quand même sur les écritures.

---

## 24. Index et ForeignKey

Les ForeignKey sont généralement indexées automatiquement par Django.

Ne duplique pas un index sans vérifier.

Les indexes composites peuvent être nécessaires pour des filtres multi-colonnes fréquents.

---

## 25. `QuerySet.explain()`

Utilise `explain()` pour comprendre le plan lorsque :

- requête lente ;
- gros volume ;
- index incertain ;
- agrégation complexe.

Ne prétends pas comprendre un plan sans analyser :

- scan ;
- rows ;
- index ;
- join ;
- sort.

---

## 26. PostgreSQL

Pour PostgreSQL, pense notamment à :

- B-tree ;
- indexes composites ;
- indexes partiels ;
- GIN/GiST selon type de recherche ;
- trigrammes ;
- full-text.

Seulement lorsque le besoin le justifie.

---

## 27. Cache : règle générale

Le cache n’est pas le premier réflexe.

Ordre recommandé :

1. supprimer les requêtes inutiles ;
2. optimiser le SQL ;
3. paginer ;
4. corriger le schéma/index si besoin ;
5. seulement ensuite envisager le cache.

Le cache ajoute :

- invalidation ;
- cohérence ;
- mémoire ;
- complexité.

---

## 28. Niveaux de cache Django

Django permet plusieurs granularités :

- cache site ;
- cache vue ;
- fragment de template ;
- cache bas niveau.

Choisis le niveau le plus petit qui résout le problème.

Ne cache pas tout le site si une seule requête est coûteuse.

---

## 29. Cache de données

Le cache bas niveau est pertinent pour :

- calcul cher ;
- agrégat ;
- réponse externe ;
- données rarement modifiées.

Une clé de cache doit être :

- stable ;
- namespacée ;
- suffisamment spécifique.

---

## 30. Invalidation

Avant de créer un cache, réponds :

> Comment sait-on qu’il n’est plus valide ?

Stratégies :

- TTL ;
- invalidation explicite ;
- version de clé ;
- événement.

Si aucune stratégie d’invalidation fiable n’existe, reconsidère le cache.

---

## 31. Cache stampede

Pour une donnée très demandée et coûteuse à recalculer, plusieurs expirations simultanées peuvent provoquer une surcharge.

Si le risque existe, analyse :

- verrou ;
- stale-while-revalidate ;
- jitter de TTL ;
- préchauffage.

Ne complexifie pas un trafic faible.

---

## 32. Cache et sécurité

Ne mets pas en cache une réponse privée sous une clé partagée.

Analyse :

- utilisateur ;
- permissions ;
- langue ;
- headers ;
- tenant ;
- rôle.

Une fuite de cache est une fuite de données.

Charge `django-security`.

---

## 33. Cache local mémoire

Le cache local mémoire n’est pas un bon choix de partage entre plusieurs processus.

Ne suppose pas qu’une valeur écrite par un worker sera visible par tous.

Pour production multi-process, utilise une solution adaptée si un cache partagé est nécessaire.

---

## 34. Sessions et cache

Si les sessions utilisent le cache :

analyse persistance et éviction.

Une perte de cache peut déconnecter les utilisateurs selon backend.

Ne modifie pas le backend de session uniquement pour gagner quelques millisecondes sans comprendre les conséquences.

---

## 35. Templates

Cherche dans les templates :

- relation accédée dans boucle ;
- méthodes/propriétés déclenchant ORM ;
- inclusion répétée coûteuse.

Les données doivent être préparées efficacement avant rendu.

Évite les requêtes cachées dans les propriétés appelées des centaines de fois.

---

## 36. Properties de modèle

Une propriété qui fait une requête DB peut être dangereuse dans une boucle.

Documente ou refactore si nécessaire.

Une propriété semble souvent « gratuite » pour le lecteur du code.

---

## 37. Serializers API

Les serializers peuvent masquer des N+1 via :

- relations imbriquées ;
- `SerializerMethodField` ;
- méthodes ;
- properties.

Charge les relations dans le queryset de la vue/service.

Teste les nombres de requêtes sur les endpoints critiques.

---

## 38. Admin Django

Les pages admin peuvent devenir lentes avec :

- `list_display` relationnel ;
- filtres ;
- search_fields ;
- facettes ;
- gros `COUNT(*)`.

Utilise :

- `list_select_related` ;
- `get_queryset()` ;
- indexes adaptés ;
- pagination raisonnable.

N’optimise l’admin que si son usage le nécessite.

---

## 39. Recherche

Une recherche `icontains` sur plusieurs gros champs peut devenir coûteuse.

Selon besoin :

- indexes adaptés ;
- trigram ;
- full-text PostgreSQL ;
- moteur externe si vraiment nécessaire.

Ne déploie pas Elasticsearch/OpenSearch pour une petite recherche sans mesure.

---

## 40. Exports

Pour un export volumineux :

- éviter de charger tout en mémoire ;
- utiliser iterator/streaming lorsque adapté ;
- limiter champs ;
- batch ;
- tâche async si long.

Documente les limites.

---

## 41. Imports

Pour imports volumineux :

- batch ;
- transactions raisonnables ;
- bulk ;
- validation groupée ;
- éviter une requête par ligne.

Charge `django-database`.

---

## 42. `iterator()`

Pour parcourir un gros QuerySet une seule fois, `iterator()` peut réduire le cache mémoire du QuerySet.

Analyse son interaction avec prefetch selon version Django.

Ne l’utilise pas pour une liste normale de 20 objets.

---

## 43. Mémoire

Une feature peut être lente parce qu’elle charge trop de données, même avec peu de requêtes.

Cherche :

- QuerySet transformé en list énorme ;
- dictionnaires massifs ;
- fichiers lus entièrement ;
- images ;
- exports.

Traite par streaming/batch lorsque pertinent.

---

## 44. CPU

Pour traitements CPU lourds :

- génération ;
- image ;
- compression ;
- calcul ;

ne bloque pas inutilement une requête web.

Analyse une tâche asynchrone.

Ne mets pas du calcul CPU lourd en cache sans corriger le workflow si le temps de réponse reste inacceptable au premier appel.

---

## 45. I/O réseau

Pour appels externes :

- timeout ;
- réutilisation client/connexion selon bibliothèque ;
- retries raisonnables ;
- async/tâche si pertinent ;
- cache si données répétitives et stables.

N’effectue pas dix appels séquentiels si une API batch existe.

---

## 46. Timeouts

Toute intégration externe doit avoir un timeout.

Une requête sans timeout peut bloquer un worker indéfiniment.

Charge `django-security` pour SSRF et réseau non fiable.

---

## 47. Compression

La compression HTTP peut réduire la bande passante mais coûte CPU.

Selon architecture, elle peut être gérée par :

- reverse proxy ;
- CDN ;
- Django.

Évite de compresser deux fois.

Documente la couche responsable.

---

## 48. Static files

En production, ne sers généralement pas les static lourds via la logique Django applicative si une couche dédiée est disponible.

Le choix dépend du déploiement.

Charge `deployment`.

---

## 49. Media

Même principe pour gros médias.

Une application Django ne doit pas devenir un serveur de fichiers inefficace sans raison.

Pour fichiers privés, combine contrôle d’accès et mécanisme de délégation adapté.

---

## 50. Middleware

Chaque middleware s’exécute sur beaucoup de requêtes.

N’ajoute pas un middleware pour une logique spécifique à une seule feature.

Mesure les middlewares coûteux.

---

## 51. Context processors

Un context processor s’exécute pour de nombreux templates.

Évite qu’il lance plusieurs requêtes complexes à chaque page.

Préférer :

- données réellement globales ;
- cache ;
- injection explicite selon contexte.

---

## 52. Template tags

Un tag custom peut cacher une requête DB.

Évite les tags exécutant une requête par occurrence.

Prépare les données en amont.

---

## 53. Signaux

Un signal peut ajouter un coût invisible à chaque sauvegarde.

Analyse :

- requêtes ;
- appels réseau ;
- traitements.

Ne lance pas un traitement lourd synchronement via signal si la latence est importante.

---

## 54. `save()` / `delete()`

Une surcharge de `save()` exécutant beaucoup de logique peut dégrader chaque écriture.

Place les workflows coûteux dans des services explicites.

Charge `django-architecture`.

---

## 55. Validation

Une validation peut déclencher des requêtes.

Évite une requête par élément dans un formset/import.

Précharge ou valide en lot lorsque pertinent.

---

## 56. Transactions

Les longues transactions peuvent :

- garder des locks ;
- augmenter contention ;
- ralentir d’autres requêtes.

Garde-les courtes.

Charge `django-database`.

---

## 57. Concurrence

Une optimisation qui supprime une transaction/lock peut introduire une corruption.

L’intégrité prime sur quelques millisecondes.

Mesure avant de réduire une garantie.

---

## 58. Async Django

N’utilise pas async comme solution générale de performance.

Async est utile surtout pour certaines charges I/O et intégrations compatibles.

L’ORM et les dépendances doivent être utilisés selon leurs capacités réelles de la version Django.

Ne transforme pas une vue simple en async sans bénéfice.

---

## 59. Nombre de workers

Le dimensionnement serveur dépend de :

- CPU ;
- mémoire ;
- I/O ;
- type de serveur ;
- trafic.

Ce skill ne doit pas inventer un nombre universel.

Charge `deployment`/`operations`.

---

## 60. Tests de performance

Pour une feature sensible, ajoute un test lorsque cela protège un risque réel.

Exemples :

- nombre maximal de requêtes ;
- pagination présente ;
- endpoint ne charge pas toutes les lignes.

Ne crée pas des benchmarks fragiles basés sur des millisecondes dans la CI ordinaire.

---

## 61. `assertNumQueries`

Django fournit des outils pour compter les requêtes.

Utilise-les pour protéger un N+1 connu.

Évite de figer un nombre exact lorsque le contrat permet de légères variations.

Exemple :

- tester que 100 objets ne provoquent pas 101 requêtes.

---

## 62. Dataset représentatif

Un N+1 peut être invisible avec un seul objet.

Pour un test de requêtes, utilise plusieurs éléments liés.

Ne crée pas 100 000 objets si 5 suffisent à révéler le pattern.

---

## 63. Baseline

Pour une optimisation importante, documente si possible :

- avant ;
- après ;
- nombre de requêtes ;
- plan/index ;
- impact.

Ne revendique pas « 10x plus rapide » sans mesure.

---

## 64. Budget de performance

Pour une feature critique, un budget peut être défini :

- nombre de requêtes ;
- taille page ;
- temps max approximatif ;
- mémoire.

Ne crée pas de budgets artificiels pour toutes les pages.

---

## 65. Observabilité

En production, les vraies performances nécessitent des métriques.

Selon infrastructure :

- temps réponse ;
- taux erreur ;
- slow queries ;
- CPU/mémoire ;
- queue ;
- cache hit rate.

Ce skill doit préparer le code pour être observable, sans imposer un fournisseur.

---

## 66. Logging performance

Ne log pas chaque requête SQL en production.

Utilise plutôt :

- slow query logging ;
- APM ;
- métriques ciblées.

Évite de créer un problème d’I/O en voulant diagnostiquer la performance.

---

## 67. Cache hit rate

Si un cache important est introduit, mesure si possible son utilité.

Un cache avec très faible hit rate et forte complexité peut être supprimé.

---

## 68. Dépendances performance

N’ajoute pas Redis, Celery, Elasticsearch ou autre composant uniquement par réflexe.

Chaque infrastructure supplémentaire ajoute :

- maintenance ;
- sécurité ;
- backup ;
- supervision ;
- coût.

Ajoute-la lorsque le besoin est réel.

---

## 69. Optimisation prématurée

Signes :

- index avant requête ;
- cache avant mesure ;
- Redis pour 20 utilisateurs ;
- async partout ;
- architecture distribuée sans trafic ;
- réplication DB avant nécessité.

Refuse poliment ces choix s’ils ajoutent plus de risques que de valeur.

---

## 70. Sous-optimisation évidente

À l’inverse, signale immédiatement :

- N+1 évident ;
- liste non paginée illimitée ;
- boucle avec `.save()` sur milliers de lignes ;
- chargement de fichier géant en mémoire ;
- API externe appelée dans chaque itération ;
- agrégation Python de millions de lignes.

Ces problèmes sont suffisamment prévisibles pour être corrigés sans attendre la production.

---

## 71. Refactoring performance

Une optimisation doit préserver le comportement.

Avant :

- tests métier ;
- mesure.

Après :

- tests métier ;
- mesure.

Ne change pas simultanément le comportement fonctionnel sans le signaler.

---

## 72. Documentation

Pour une optimisation structurante, mets à jour :

- documentation feature ;
- `docs/architecture/decisions.md` si nécessaire ;
- `CHANGELOG.md` si impact notable ;
- documentation infrastructure si cache/service ajouté.

Documente surtout le **pourquoi**.

---

## 73. Relecture performance

Avant Definition of Done, cherche :

- N+1 ;
- requête dans boucle ;
- liste illimitée ;
- prefetch excessif ;
- champs inutiles ;
- agrégation Python ;
- index manquant probable ;
- cache incohérent ;
- traitement synchrone lourd ;
- appel réseau répétitif ;
- transaction trop longue.

Ne corrige que ce qui est pertinent.

---

## 74. Definition of Done performance

Une feature est suffisamment analysée lorsque les points applicables sont vrais :

- volume probable compris ;
- requêtes principales identifiées ;
- N+1 absent ou justifié ;
- pagination/limites présentes ;
- indexes analysés si nécessaire ;
- traitement lourd géré correctement ;
- cache uniquement si justifié ;
- mesure effectuée pour optimisation non évidente ;
- tests de régression perf ajoutés si forte valeur ;
- documentation mise à jour si architecture modifiée.

---

## 75. Principe final

La performance n’est pas « faire le moins de requêtes possible ».

Une bonne solution équilibre :

- temps de réponse ;
- mémoire ;
- coût DB ;
- complexité ;
- cohérence ;
- maintenabilité ;
- capacité à évoluer.

Optimise d’abord les gros multiplicateurs : N+1, volumes non bornés, requêtes mal indexées et traitements répétés.
