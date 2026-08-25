---
name: django-testing
description: Définit et applique une stratégie de tests Django pragmatique orientée valeur. À utiliser pour toute nouvelle logique métier, bug, permission, migration risquée, intégration ou refactoring significatif. Favorise le TDD lorsqu’il apporte une vraie valeur, pytest/pytest-django si le projet les utilise, tests de permissions négatifs, fixtures petites et composables, paramétrisation, tests de régression et contrôles de migration. Évite les tests triviaux et la course au pourcentage de couverture.
compatibility: opencode
metadata:
  framework: django
  purpose: testing
  language: fr
  workflow-parent: project-workflow
---

# Django Testing

## 1. Mission

Tu es responsable de la stratégie de tests du projet Django.

Ton objectif n’est pas d’écrire le plus grand nombre de tests possible.

Ton objectif est de construire une suite qui :

- protège les comportements importants ;
- détecte les régressions ;
- sécurise les règles métier ;
- vérifie les permissions ;
- permet de refactorer avec confiance ;
- reste lisible ;
- reste rapide à exécuter ;
- reste facile à maintenir.

Principe :

> Un bon test doit réduire un risque réel.

N’écris jamais un test uniquement pour faire augmenter un pourcentage de couverture.

---

## 2. Coordination

Avant d’écrire des tests :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. comprends le comportement attendu ;
4. inspecte les tests existants ;
5. charge si disponibles :
   - `django-architecture`
   - `django-database`
   - `django-security`
   - `django-performance`
   - `django-auth`
   - `django-api`

Respecte le framework de test déjà choisi.

Ne migre pas automatiquement `unittest` vers pytest dans un projet existant sans bénéfice réel.

---

## 3. TDD pragmatique

Le TDD est la stratégie par défaut pour une logique métier nouvelle lorsque cela apporte une vraie valeur.

Cycle :

1. écrire un test décrivant un comportement ;
2. vérifier qu’il échoue pour la bonne raison ;
3. écrire le minimum de code nécessaire ;
4. faire passer le test ;
5. refactorer ;
6. ajouter les cas limites pertinents.

Le test doit décrire le comportement, pas l’implémentation.

---

## 4. Quand le TDD est particulièrement pertinent

Utilise-le en priorité pour :

- règles métier ;
- calculs ;
- permissions ;
- transitions d’état ;
- validations importantes ;
- bugs ;
- régressions ;
- services ;
- contraintes ;
- import/export ;
- logique transactionnelle ;
- API ;
- fonctions ayant plusieurs cas limites.

---

## 5. Quand ne pas forcer un test

Un test automatisé peut être inutile pour :

- texte purement statique ;
- changement visuel sans logique ;
- simple configuration évidente déjà couverte par un outil ;
- wrapper trivial sans comportement ;
- code généré par le framework sans modification.

Si le risque est quasi nul et que le test ne protégerait rien d’utile, ne l’écris pas.

---

## 6. Pyramide de tests pragmatique

Cherche principalement :

### Beaucoup de tests ciblés

- logique métier ;
- services ;
- validators ;
- permissions ;
- QuerySets complexes ;
- serializers/forms importants.

### Tests d’intégration pertinents

- ORM + service ;
- vue + permissions ;
- formulaire + logique ;
- API + base ;
- tâches externes simulées.

### Peu de tests end-to-end

Uniquement pour les parcours critiques ou complexes.

N’essaie pas de tout tester via navigateur.

---

## 7. Test unitaire

Un test unitaire doit cibler une petite responsabilité.

Il doit idéalement :

- être rapide ;
- être déterministe ;
- avoir peu de dépendances ;
- expliquer clairement ce qui casse.

Mais ne crée pas de mocks artificiels partout juste pour appeler un test « unitaire ».

Dans Django, un petit test utilisant la vraie base peut parfois être plus fiable qu’une simulation complexe.

---

## 8. Test d’intégration

Utilise un test d’intégration lorsque le risque se situe entre plusieurs composants :

- modèle + DB ;
- service + transaction ;
- vue + authentification ;
- serializer + modèle ;
- formulaire + validation ;
- commande management + service.

Ce type de test est très utile dans Django.

---

## 9. End-to-end

Utilise un test E2E seulement lorsque :

- le parcours traverse plusieurs couches ;
- le comportement critique dépend du navigateur ;
- JavaScript est essentiel ;
- plusieurs étapes utilisateur sont importantes.

Exemples :

- inscription complète ;
- paiement ;
- workflow multi-écran critique.

Évite de couvrir toutes les pages par E2E.

---

## 10. Tests de sécurité

Toute permission importante doit avoir des tests négatifs.

Minimum selon contexte :

- utilisateur anonyme refusé ;
- utilisateur authentifié sans droit refusé ;
- utilisateur A ne peut pas accéder à la ressource B ;
- rôle insuffisant refusé ;
- propriétaire autorisé ;
- rôle privilégié autorisé si prévu.

Charge `django-security`.

---

## 11. Tests de bug / régression

Lorsqu’un bug est corrigé :

1. reproduis le bug avec un test qui échoue ;
2. corrige ;
3. vérifie que le test passe ;
4. conserve le test.

Le nom doit rappeler le comportement protégé, pas le numéro interne du bug uniquement.

---

## 12. Tester le comportement

Préfère :

```python
def test_archived_ship_is_not_visible_to_public():
    ...
```

à :

```python
def test_filter_called_once():
    ...
```

Ne verrouille pas inutilement la structure interne du code.

Un refactoring valide ne devrait pas casser de nombreux tests sans changement métier.

---

## 13. Organisation des tests

Pour une petite app, ceci peut suffire :

```text
app/
└── tests.py
```

Lorsque les tests grossissent :

```text
app/
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_services.py
    ├── test_views.py
    ├── test_permissions.py
    └── test_selectors.py
```

Découpe selon le comportement réel.

Ne crée pas dix fichiers vides dès le départ.

---

## 14. Nommage des tests

Le nom doit dire ce qui est attendu.

Format utile :

```text
test_<comportement>_<condition>
```

Exemples :

```text
test_user_can_edit_own_profile
test_user_cannot_edit_another_profile
test_order_rejects_negative_quantity
```

Évite :

```text
test_case_1
test_model
test_view
```

---

## 15. Arrange / Act / Assert

Structure mentalement les tests :

- Arrange ;
- Act ;
- Assert.

Tu peux utiliser des commentaires uniquement lorsque le test n’est pas déjà évident.

Évite les tests de 100 lignes mélangeant plusieurs scénarios.

---

## 16. Une intention principale par test

Un test peut contenir plusieurs assertions si elles vérifient le même comportement.

N’impose pas « une assertion par test ».

Mais évite de tester :

- création ;
- modification ;
- suppression ;
- permission ;
- email ;

dans une seule fonction.

---

## 17. pytest

Si le projet utilise pytest :

- utilise des assertions Python simples ;
- utilise fixtures ;
- utilise parametrization ;
- utilise marks avec parcimonie ;
- garde la configuration centralisée.

Pytest est adapté aux petits tests lisibles et aux suites complexes.

---

## 18. pytest-django

Pour un projet Django sous pytest :

utilise `pytest-django`.

Accès DB explicite selon conventions du projet, par exemple :

```python
@pytest.mark.django_db
def test_...():
    ...
```

ou fixture DB adaptée.

Ne rends pas tous les tests dépendants de la DB par défaut si beaucoup n’en ont pas besoin.

---

## 19. Django TestCase

Si le projet utilise le test runner Django :

utilise les classes adaptées :

- `SimpleTestCase` lorsque DB inutile ;
- `TestCase` pour majorité des tests DB ;
- `TransactionTestCase` seulement lorsque le comportement transactionnel réel doit être testé.

Ne choisis pas `TransactionTestCase` partout : il est plus coûteux.

---

## 20. Fixtures pytest

Une fixture doit représenter une petite dépendance compréhensible.

Exemples :

```text
user
admin_user
manufacturer
ship
authenticated_client
```

Évite une fixture globale créant 50 objets pour tous les tests.

---

## 21. Composition des fixtures

Préférer :

```text
user
manufacturer
ship(manufacturer)
```

à une fixture `everything()`.

Les dépendances explicites facilitent la compréhension.

---

## 22. Scope des fixtures

Utilise le scope le plus petit raisonnable.

Le scope `function` est généralement sûr.

N’utilise pas `session` pour accélérer artificiellement des données mutables partagées entre tests.

L’isolation prime.

---

## 23. Factories

Lorsque beaucoup d’objets doivent être créés avec des variations, une factory peut être plus maintenable qu’une fixture statique.

Avant d’ajouter une bibliothèque de factory :

- vérifie qu’elle apporte une vraie valeur ;
- vérifie maintenance ;
- respecte `dependency-management`.

Une fonction/factory maison simple peut suffire.

---

## 24. Données minimales

Crée uniquement les données nécessaires au comportement testé.

Ne construis pas un monde complet pour tester une validation.

Cela :

- accélère ;
- clarifie ;
- réduit le couplage.

---

## 25. Valeurs réalistes

Utilise des valeurs faciles à comprendre.

Préférer :

```text
quantity=2
price=10
```

à des valeurs aléatoires lorsque l’aléatoire n’apporte rien.

Un test doit être reproductible.

---

## 26. Données aléatoires

N’utilise de random que si la propriété testée le nécessite.

Si random :

- seed reproductible ;
- erreur reproductible ;
- plage bornée.

Ne crée pas des tests flaky.

---

## 27. Paramétrisation

Utilise la paramétrisation lorsque plusieurs entrées doivent produire des résultats connus.

Exemple conceptuel :

```python
@pytest.mark.parametrize(
    ("quantity", "valid"),
    [
        (1, True),
        (0, False),
        (-1, False),
    ],
)
```

Évite de copier trois fois le même test.

---

## 28. Cas limites

Pour une règle métier, cherche les frontières.

Exemple :

si maximum = 10 :

- 9 ;
- 10 ;
- 11.

Teste les limites, pas seulement une valeur moyenne.

---

## 29. Exceptions

Si un comportement doit échouer :

teste :

- le type d’erreur ;
- le message uniquement s’il fait partie du contrat ;
- l’absence d’effet secondaire.

Ne teste pas un texte interne susceptible de changer sans importance.

---

## 30. Mocks

Mocke les frontières externes, pas tout le programme.

Bon candidat :

- HTTP externe ;
- email provider ;
- paiement ;
- stockage distant ;
- horloge dans certains cas ;
- tâche externe.

Mauvais candidat :

- ORM entier ;
- chaque méthode interne ;
- objets du domaine seulement pour éviter la DB.

---

## 31. Patch au bon endroit

Lorsque tu patches :

patch l’objet à l’endroit où il est utilisé/importé.

Un mauvais patch peut créer un test qui ne teste rien.

Évite les patchs trop larges.

---

## 32. Vérifier les effets métier, pas les appels internes

Si possible, teste :

```text
la réservation existe
```

plutôt que :

```text
service._private_method called once
```

Les interactions internes ne doivent être testées que si elles constituent réellement le contrat.

---

## 33. Services externes

Les tests ordinaires ne doivent pas dépendre d’Internet.

Utilise :

- mock ;
- fake ;
- sandbox local ;
- fixture HTTP ;
- test contractuel séparé si nécessaire.

Un échec réseau externe ne doit pas rendre la suite de tests métier aléatoire.

---

## 34. Email

Teste :

- qu’un email doit être envoyé ;
- destinataire ;
- sujet/contenu métier essentiel ;
- absence d’envoi lorsque refusé.

Utilise le backend email de test.

Ne teste pas le fonctionnement de SMTP lui-même.

---

## 35. Fichiers

Pour upload :

- fichier temporaire ;
- taille minimale ;
- type attendu ;
- nettoyage après test.

Ne laisse pas de fichiers dans `media/` après les tests.

Utilise un storage/temp directory isolé.

---

## 36. Temps

Les tests basés sur l’heure réelle sont fragiles.

Quand une règle dépend du temps :

- injecte le temps si architecture adaptée ;
- utilise `timezone.now()` ;
- fige l’horloge avec une dépendance maintenue seulement si utile.

Évite `sleep()`.

---

## 37. Timezone

Teste les comportements sensibles aux frontières :

- minuit ;
- changement de jour ;
- fuseaux ;
- DST si métier concerné.

N’écris pas de test timezone complexe pour une feature qui n’en dépend pas.

---

## 38. Transactions

Utilise `TransactionTestCase` ou mécanisme pytest adapté seulement si tu testes réellement :

- commit ;
- rollback ;
- locks ;
- `on_commit`;
- concurrence.

Un test DB standard suffit autrement.

---

## 39. `on_commit`

Si une feature déclenche une action après commit, teste ce comportement avec les outils Django adaptés.

Ne suppose pas qu’un callback `on_commit` s’exécute comme en production dans tous les types de tests sans vérifier le contexte.

---

## 40. Concurrence

Pour une règle réellement concurrente :

- stock ;
- réservation ;
- compteur ;
- unicité de workflow ;

un test séquentiel peut être insuffisant.

Évalue un test dédié utilisant :

- transactions réelles ;
- threads/processus si nécessaire ;
- verrouillage DB.

Ne crée pas de test concurrent complexe si la base garantit déjà l’invariant via une contrainte simple et testée.

---

## 41. Contraintes DB

Teste les contraintes métier critiques.

Exemples :

- unicité ;
- check constraint ;
- suppression protégée ;
- intégrité relationnelle.

Charge `django-database`.

Ne teste pas toutes les contraintes générées automatiquement par Django.

---

## 42. Migrations

Une migration simple générée automatiquement ne nécessite pas toujours un test dédié.

Teste une migration lorsqu’elle :

- transforme des données ;
- renomme/fusionne ;
- change un type risqué ;
- remplit un nouveau champ ;
- ajoute une contrainte après backfill ;
- modifie une grosse table d’une façon complexe.

---

## 43. Tests de migration

Pattern :

1. migrer vers l’état précédent ;
2. insérer des données représentatives ;
3. migrer vers le nouvel état ;
4. vérifier données et contraintes.

Utilise les modèles historiques.

Ne dépends pas du modèle actuel pour vérifier l’ancien schéma.

---

## 44. API

Pour une API, teste en priorité :

- authentification ;
- permissions ;
- validation ;
- status codes ;
- données essentielles ;
- pagination ;
- filtres ;
- erreurs ;
- idempotence si nécessaire.

Ne snapshotte pas d’énormes JSON sans raison.

Charge `django-api`.

---

## 45. Vues HTML

Teste une vue lorsque le comportement a de la valeur :

- permission ;
- redirection métier ;
- formulaire ;
- erreur ;
- contexte important ;
- effet.

Inutile de tester chaque page statique juste pour confirmer `200 OK`.

---

## 46. Templates

Ne teste pas la présence de chaque texte.

Teste uniquement les éléments qui représentent un comportement métier ou une condition importante.

Exemple utile :

- bouton d’administration absent pour utilisateur sans droit.

Mais une permission backend doit toujours être testée séparément ; masquer un bouton n’est pas une sécurité.

---

## 47. Forms

Teste :

- validation métier ;
- normalisation ;
- champs conditionnels ;
- erreurs significatives.

Ne teste pas que `CharField(required=True)` rejette le vide sauf personnalisation ou régression pertinente.

---

## 48. Models

Teste :

- méthodes métier ;
- propriétés calculées ;
- transitions ;
- règles personnalisées ;
- contraintes.

Ne teste pas :

```text
que name est bien sauvegardé dans name
```

sans logique supplémentaire.

---

## 49. QuerySets / selectors

Teste :

- filtre métier ;
- visibilité ;
- ordering métier ;
- annotations ;
- cas de permissions.

Pour les requêtes critiques, teste aussi éventuellement le nombre de requêtes avec `django-performance`.

---

## 50. Admin

Teste l’admin uniquement lorsqu’il contient une logique personnalisée importante :

- permission spéciale ;
- action métier ;
- formulaire custom ;
- restriction queryset.

Ne teste pas l’admin Django standard.

---

## 51. Commands

Une management command métier doit être testée si elle :

- importe ;
- modifie des données ;
- déclenche une opération importante ;
- possède des options.

Teste le comportement, pas seulement la sortie console.

---

## 52. Tâches asynchrones

Teste la fonction métier appelée par la tâche séparément.

Teste la tâche elle-même pour :

- sérialisation paramètres ;
- retry ;
- idempotence ;
- comportement d’échec ;

si c’est pertinent.

Évite de démarrer un vrai worker dans tous les tests.

---

## 53. Celery / queue

Si queue utilisée :

- eager mode avec prudence ;
- tests unitaires sur logique ;
- quelques tests d’intégration queue si réellement nécessaires.

Un mode eager ne reproduit pas toujours tous les comportements d’un worker réel.

Documente la différence.

---

## 54. Cache

Si le cache affecte un comportement :

teste :

- cache miss ;
- cache hit ;
- invalidation.

Ne couple pas chaque test à l’implémentation du cache.

---

## 55. Feature flags

Teste :

- flag off ;
- flag on ;
- permissions si liées.

Évite que les tests dépendent d’un flag global laissé dans un état par un test précédent.

---

## 56. Multilingue

Si i18n métier :

- contenus traduits ;
- locale ;
- fallback ;
- URLs si concernées.

Ne teste pas le framework de traduction lui-même.

---

## 57. Tests rapides

La boucle TDD doit rester rapide.

Permets de lancer :

```text
un test
un fichier
une app
la suite
```

Documente les commandes réelles dans README/AGENTS.

---

## 58. Suite lente

Si certains tests sont réellement lents :

- marque-les ;
- explique pourquoi ;
- exécute-les au bon niveau (pré-push/CI).

Ne cache pas des tests lents nécessaires uniquement pour obtenir une suite rapide.

---

## 59. Marks

Marks possibles :

```text
slow
integration
e2e
security
migration
```

N’en crée pas trop.

Chaque mark doit avoir un usage clair et être enregistré dans la configuration pytest.

---

## 60. Isolation

Chaque test doit pouvoir être lancé seul et dans n’importe quel ordre.

Ne dépends jamais :

- d’un test précédent ;
- d’une donnée créée par un autre test ;
- d’un fichier persistant ;
- d’un état global non restauré.

---

## 61. Flaky tests

Un test intermittent est un bug du système de tests.

Lorsqu’un test flaky apparaît :

- ne fais pas simplement retry indéfiniment ;
- trouve la cause ;
- corrige :
  - temps ;
  - ordre ;
  - réseau ;
  - concurrence ;
  - état partagé.

Un retry temporaire doit être documenté.

---

## 62. Performance des tests

Optimise la suite seulement après identifier les coûts.

Pistes :

- éviter DB inutile ;
- réduire setup ;
- fixtures plus petites ;
- conserver DB de test localement selon outil ;
- paralléliser si suite assez grande ;
- séparer tests lents.

Ne sacrifie pas l’isolation pour quelques secondes.

---

## 63. Base de test

Utilise le même moteur de base que la production lorsque des différences SQL pourraient affecter le comportement.

Pour un projet PostgreSQL réel, privilégie PostgreSQL également dans les tests significatifs.

SQLite peut masquer des différences :

- contraintes ;
- types ;
- locking ;
- SQL ;
- fonctionnalités PostgreSQL.

---

## 64. `--reuse-db`

Avec pytest-django, `--reuse-db` peut accélérer la boucle locale.

Mais si le schéma change :

- recrée la DB lorsque nécessaire ;
- utilise les options adaptées.

Ne rends pas la fiabilité dépendante d’une DB locale périmée.

---

## 65. Tests sans migrations

Une option de test sans migrations peut accélérer certains workflows locaux.

Mais :

- les migrations restent du code ;
- elles doivent être testées ailleurs ;
- les contrôles pré-push/CI doivent vérifier leur cohérence.

Ne masque pas une migration cassée pour gagner du temps.

---

## 66. CI

La CI doit exécuter au minimum selon projet :

- lint ;
- tests ;
- migrations/checks ;
- sécurité pertinente.

Les tests CI doivent partir d’un environnement propre.

Ne considère pas « ça passe chez moi » comme validation finale.

---

## 67. Pré-commit vs pré-push

### Pre-commit

Tests très rapides seulement.

### Pré-push

Suite plus complète.

Ne rends pas chaque commit pénible avec des tests longs.

Le `project-workflow` décide des quality gates.

---

## 68. Coverage

La couverture sert à repérer les zones oubliées.

Elle ne mesure pas la qualité.

N’impose pas un 100%.

Si un seuil est configuré :

- il doit être raisonnable ;
- ne pas pousser à tester du code trivial ;
- pouvoir augmenter progressivement.

---

## 69. Mutation testing

Le mutation testing peut révéler des tests faibles.

Il est optionnel.

Utilise-le uniquement sur :

- logique critique ;
- projet mature ;
- besoin réel.

Ne l’impose pas au socle de tous les projets Django.

---

## 70. Property-based testing

Un outil de property-based testing peut être utile pour :

- parsers ;
- validateurs ;
- calculs ;
- invariants complexes.

Ne l’ajoute pas juste parce qu’il existe.

La dépendance doit être justifiée.

---

## 71. Snapshot testing

Utilise les snapshots avec prudence.

Bon cas :

- structure de sortie stable difficile à vérifier manuellement.

Mauvais cas :

- gros HTML ;
- gros JSON ;
- snapshots acceptés automatiquement sans lecture.

Un snapshot doit détecter un vrai changement, pas créer du bruit.

---

## 72. Golden files

Même principe que snapshots.

Utile pour :

- export ;
- génération ;
- format complexe.

La mise à jour du fichier attendu doit être revue.

---

## 73. Tests de contrat

Si intégration externe critique :

- teste le contrat ;
- schéma ;
- champs obligatoires ;
- erreurs.

Sépare ces tests des tests locaux rapides.

Ils peuvent dépendre d’un sandbox contrôlé.

---

## 74. Tests de performance

Ne transforme pas chaque test en benchmark.

Pour une zone critique :

- nombre de requêtes ;
- taille réponse ;
- temps approximatif sous environnement stable ;
- volume.

Les budgets stricts appartiennent à `django-performance`.

---

## 75. Nombre de requêtes

Pour éviter une régression N+1 sur une feature importante, un test peut utiliser les outils Django pour vérifier un nombre raisonnable de requêtes.

Ne fige pas un nombre exact fragile si plusieurs requêtes équivalentes sont acceptables.

Teste un plafond ou une propriété stable lorsque possible.

---

## 76. Tests de permissions par matrice

Pour plusieurs rôles :

utilise une table/paramétrisation.

Exemple conceptuel :

```text
anonymous -> denied
member -> denied
owner -> allowed
moderator -> allowed
```

C’est plus lisible que quatre blocs dupliqués.

---

## 77. Tests d’états

Pour un workflow :

```text
draft -> published
published -> archived
```

Teste :

- transitions autorisées ;
- transitions interdites ;
- effets associés.

Une machine d’état implicite doit malgré tout être protégée.

---

## 78. Tests d’idempotence

Pour webhook/import/tâche :

exécute l’opération deux fois.

Vérifie qu’elle ne :

- double pas une transaction ;
- crée pas deux objets ;
- envoie pas deux effets interdits.

---

## 79. Tests de sérialisation

Teste uniquement les données faisant partie du contrat public.

Ne bloque pas un refactoring interne en testant chaque champ privé.

---

## 80. Données sensibles dans les tests

N’utilise pas de vraies données personnelles ou secrets.

Les fixtures doivent être fictives.

Ne copie pas un dump production brut pour les tests locaux.

---

## 81. Logs dans les tests

Pour une erreur critique, teste éventuellement qu’un événement est loggé.

Mais ne teste pas tous les textes de logs.

Ne mets jamais un secret fictif dans un test si le pattern pourrait encourager à utiliser des vraies clés.

---

## 82. TDD et design

Si le test est extrêmement difficile à écrire, demande si :

- la responsabilité est trop grosse ;
- les dépendances sont trop couplées ;
- la logique dépend trop du framework ;
- la fonction fait plusieurs choses.

Le test peut signaler un problème d’architecture.

Charge `django-architecture`.

---

## 83. Tests et refactoring

Avant un refactoring significatif :

1. identifier les comportements ;
2. ajouter les tests manquants à forte valeur ;
3. lancer ;
4. refactorer ;
5. relancer.

Ne « corrige » pas simultanément le comportement et l’architecture sans le distinguer.

---

## 84. Bug de test vs bug produit

Lorsqu’un test échoue après changement, ne modifie pas immédiatement le test pour le faire passer.

Décide :

- comportement produit changé intentionnellement ;
- régression ;
- test trop couplé ;
- expectation incorrecte.

Un test rouge est une information.

---

## 85. Tests générés par IA

Ne produis pas des dizaines de tests mécaniques.

Chaque test généré doit être relu mentalement :

- pourrait-il réellement échouer ?
- teste-t-il notre code ?
- protège-t-il un risque ?
- est-il indépendant ?
- sera-t-il compréhensible dans six mois ?

Supprime les tests sans valeur.

---

## 86. Commentaires

Un test doit se comprendre principalement par son nom et ses données.

Commente seulement :

- contexte métier subtil ;
- bug historique non évident ;
- workaround ;
- raison d’un mock inhabituel.

---

## 87. Documentation

Mets à jour la documentation de tests lorsque :

- stratégie change ;
- nouvelle catégorie de test ;
- nouvelle commande ;
- nouveau mark ;
- nouvelle dépendance.

README/AGENTS doivent contenir les commandes réelles.

---

## 88. Rapport de feature

À la fin d’une feature, indique :

- tests ajoutés ;
- comportements couverts ;
- tests exécutés ;
- résultat ;
- éventuels tests non exécutés.

Ne dis jamais « tous les tests passent » si seule une sélection a été exécutée.

---

## 89. Relecture second développeur

Avant Definition of Done :

- test principal présent ?
- cas négatif ?
- cas limite ?
- permission ?
- test trop couplé ?
- fixture trop grosse ?
- mock trompeur ?
- test flaky ?
- duplication ?
- migration risquée couverte ?
- bug protégé contre régression ?

Ajoute uniquement les tests à forte valeur.

---

## 90. Definition of Done testing

Une feature est suffisamment testée lorsque les points applicables sont vrais :

- règle métier importante testée ;
- permissions testées ;
- cas négatifs pertinents testés ;
- cas limites pertinents testés ;
- bug accompagné d’un test de régression ;
- transaction/concurrence testée si critique ;
- migration risquée testée ;
- intégration externe isolée ;
- suite pertinente exécutée ;
- aucun test rouge ;
- tests lisibles et indépendants ;
- documentation mise à jour si nécessaire.

---

## 91. Principe final

La suite de tests doit être un filet de sécurité, pas une deuxième application à maintenir.

Le meilleur test est celui qui :

- échoue lorsqu’un vrai comportement casse ;
- reste vert lors d’un refactoring valide ;
- explique immédiatement le problème ;
- coûte moins à maintenir que le risque qu’il protège.
