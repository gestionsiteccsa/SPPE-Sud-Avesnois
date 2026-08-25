---
name: backup-restore
description: Conçoit, automatise, documente et vérifie la stratégie de sauvegarde et restauration d’un projet Django, principalement PostgreSQL + media utilisateurs. À utiliser pour sauvegardes quotidiennes, rétention, copie hors serveur, chiffrement, vérification d’intégrité, tests de restauration, restauration après incident et préparation avant migration/déploiement risqué. Une sauvegarde n’est jamais considérée fiable tant qu’une restauration n’a pas été testée.
compatibility: opencode
metadata:
  framework: django
  datastore: postgresql
  purpose: backup-restore
  language: fr
  workflow-parent: project-workflow
---

# Backup & Restore Django

## 1. Mission

Tu es responsable de la résilience des données du projet.

Ton objectif est que le projet puisse réellement récupérer après :

- erreur humaine ;
- migration incorrecte ;
- suppression accidentelle ;
- panne disque ;
- corruption ;
- serveur perdu ;
- ransomware ;
- erreur de déploiement.

Une sauvegarde qui existe mais qui n’a jamais été restaurée n’est pas une garantie.

---

## 2. Politique par défaut

Pour ce projet, la politique par défaut est :

- sauvegarde **quotidienne** ;
- base PostgreSQL ;
- fichiers media utilisateurs si présents ;
- plusieurs générations conservées ;
- au moins une copie hors de la machine de production lorsque possible ;
- accès aux backups limité ;
- chiffrement lorsque les données le justifient ;
- vérification automatique ;
- restauration testée périodiquement.

Adapte la rétention au volume et à l’infrastructure.

---

## 3. Coordination

Avant configuration :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. charge :
   - `django-database`
   - `django-security`
   - `deployment`
   - `documentation`
4. inspecte :
   - base PostgreSQL ;
   - media ;
   - Docker ou non ;
   - espace disque ;
   - stockage externe possible ;
   - données sensibles.

---

## 4. Questions

Pose au maximum **2 questions à la fois** si une décision ne peut pas être déduite.

Exemples :

- Existe-t-il un stockage externe disponible pour une seconde copie ?
- Combien de jours de rétention souhaites-tu conserver si le volume devient important ?

Si l’utilisateur ne sait pas, propose une valeur par défaut raisonnable.

---

## 5. Ce qu’il faut sauvegarder

Analyse :

### Base de données

Toujours pour une application persistante.

### Media utilisateurs

Si les fichiers ne peuvent pas être régénérés.

### Configuration critique

Pas les secrets en clair dans un backup non sécurisé.

### Autres données

- fichiers générés uniques ;
- index externes non reconstruisibles ;
- uploads ;
- certificats si nécessaire ;
- files de queue uniquement si architecture l’exige.

Ne sauvegarde pas les caches reconstruisibles sans raison.

---

## 6. Code source

Git est la source du code.

Ne traite pas le backup serveur comme la seule copie du code.

Le dépôt distant doit exister indépendamment du serveur de production.

---

## 7. PostgreSQL : stratégie standard

Pour un projet Django classique, `pg_dump` est une bonne base de sauvegarde logique.

Format custom recommandé dans beaucoup de cas :

```bash
pg_dump -Fc ...
```

Avantages :

- archive compacte ;
- restaurable avec `pg_restore` ;
- restauration sélective ;
- portable entre architectures.

Adapte à la version PostgreSQL réelle.

---

## 8. Version pg_dump

Utilise un client `pg_dump` compatible avec le serveur.

Ne suppose pas que n’importe quelle vieille version peut dumper un serveur plus récent.

Documente les versions.

---

## 9. Dump logique

Un dump logique contient le schéma et/ou les données.

Il est pratique pour :

- petite/moyenne base ;
- migration ;
- récupération ;
- transfert.

Pour une base très volumineuse ou RPO serré, analyse PITR/backup physique.

---

## 10. `pg_dumpall`

`pg_dumpall` peut sauvegarder :

- plusieurs bases ;
- rôles ;
- tablespaces selon usage.

Mais il n’est pas nécessaire pour chaque projet Django mono-base.

Si les rôles PostgreSQL doivent être restaurés, prévois leur sauvegarde séparée ou procédure d’infrastructure.

---

## 11. Rôles PostgreSQL

Une restauration de DB n’est pas complète si l’environnement dépend de rôles absents.

Documente :

- user applicatif ;
- owner ;
- extensions ;
- permissions.

Ne stocke pas les mots de passe des rôles dans la documentation.

---

## 12. Extensions PostgreSQL

Si le projet utilise :

- pg_trgm ;
- uuid ;
- PostGIS ;
- autres extensions ;

documente leur installation.

La restauration peut échouer si l’extension n’existe pas sur la cible.

---

## 13. Media

Sauvegarde `MEDIA_ROOT` ou stockage objet selon architecture.

Ne mélange pas :

- static collectés ;
- media utilisateurs.

Les static peuvent généralement être régénérés depuis le code.

---

## 14. Backup media cohérent

Si les références DB et fichiers media doivent rester cohérentes, définis le niveau de cohérence nécessaire.

Pour beaucoup de sites, un léger décalage quotidien est acceptable.

Pour des documents critiques, une stratégie plus cohérente peut être requise.

---

## 15. Stockage externe

Une copie uniquement sur le même disque que la production ne protège pas contre la panne disque.

Prévois si possible :

- NAS ;
- autre serveur ;
- stockage objet ;
- disque externe déconnectable ;
- cloud backup.

---

## 16. Principe 3-2-1

Comme objectif de maturité, considère :

- 3 copies ;
- 2 supports différents ;
- 1 copie hors site.

Ce n’est pas une obligation immédiate pour un petit projet, mais une bonne cible.

---

## 17. Ransomware

Un backup toujours monté en écriture peut être détruit en même temps que la production.

Lorsque possible, utilise :

- versioning ;
- immutabilité ;
- compte backup distinct ;
- stockage non monté en permanence ;
- permissions limitées.

---

## 18. Compte de backup

Le processus de backup doit avoir les permissions nécessaires, mais pas davantage.

Le stockage destination ne doit pas être accessible à tous les utilisateurs système.

---

## 19. Secrets

Ne place pas le mot de passe DB dans le script.

Utilise :

- variables d’environnement ;
- `.pgpass` correctement protégé ;
- secret manager ;
- mécanisme Docker secret si retenu.

---

## 20. `.pgpass`

Si utilisé :

- permissions strictes ;
- utilisateur système dédié ;
- fichier non versionné.

Ne l’inclus jamais dans les backups publics.

---

## 21. Chiffrement

Si les backups contiennent des données personnelles ou sensibles, chiffre-les au repos lorsque la couche de stockage ne fournit pas déjà une protection suffisante.

Utilise des outils éprouvés.

Ne crée pas un chiffrement maison.

---

## 22. Clé de chiffrement

La clé ne doit pas être stockée uniquement avec le backup chiffré.

Sinon la perte/compromission touche les deux.

Prévoyez :

- stockage distinct ;
- rotation ;
- récupération ;
- accès limité.

---

## 23. Chiffrement en transit

Lors d’une copie vers stockage distant, utilise un protocole chiffré :

- SSH/SFTP ;
- HTTPS/TLS ;
- outil de backup sécurisé.

Évite FTP en clair.

---

## 24. Compression

Le format custom de PostgreSQL gère déjà des capacités adaptées selon options/version.

Ne recompresse pas automatiquement plusieurs fois.

Pour media, compression dépend du type de fichiers.

---

## 25. Nommage

Nom de backup explicite :

```text
project-db-2026-08-15T020000Z.dump
```

ou équivalent.

Inclure :

- projet ;
- type ;
- date/heure ;
- éventuellement environnement.

Ne mets pas de secret dans le nom.

---

## 26. UTC

Pour les noms et logs automatiques, UTC est souvent préférable.

Affiche éventuellement l’heure locale dans la documentation humaine.

---

## 27. Répertoire local

Exemple :

```text
/var/backups/myproject/
├── database/
└── media/
```

Permissions strictes.

Ne stocke pas dans le repository Git.

---

## 28. Rétention

Définis une politique claire.

Valeur de départ possible :

- 7 sauvegardes quotidiennes ;
- 4 hebdomadaires ;
- 6 mensuelles.

C’est un exemple, pas une règle universelle.

Adapte au stockage et à la criticité.

---

## 29. Suppression automatique

La rotation doit supprimer uniquement les backups ciblés.

Un script de purge doit être extrêmement prudent.

Évite les glob patterns dangereux et `rm -rf` non bornés.

---

## 30. Backups avant déploiement

Une sauvegarde quotidienne ne remplace pas forcément un backup pré-déploiement.

Avant une migration risquée :

- vérifie un backup récent ;
- ou crée un snapshot/dump spécifique.

---

## 31. Backup avant suppression

Toute opération destructrice importante doit évaluer un backup préalable.

Cela ne signifie pas qu’il faut sauvegarder avant chaque petite suppression utilisateur.

---

## 32. Automatisation

Sur Linux sans Docker :

- systemd timer recommandé ;
- cron acceptable si bien documenté.

Préférer une configuration versionnable et observable.

---

## 33. systemd timer

Avantages :

- logs journald ;
- état ;
- calendrier ;
- erreurs visibles.

Un template est fourni.

---

## 34. Cron

Si cron est retenu :

- utilisateur dédié ;
- PATH explicite ;
- logs ;
- erreurs ;
- environnement.

Ne suppose pas que cron possède le même environnement que ton shell.

---

## 35. Docker

Si PostgreSQL est dans Docker :

tu peux exécuter `pg_dump` :

- depuis le container ;
- depuis un container client ;
- depuis l’hôte.

La méthode doit être documentée et testée.

---

## 36. Ne pas sauvegarder le volume brut à chaud aveuglément

Copier directement les fichiers d’un volume PostgreSQL en fonctionnement n’est pas équivalent à un backup valide, sauf stratégie physique PostgreSQL correctement conçue.

Pour un projet standard, préfère `pg_dump`.

---

## 37. Backup physique

Pour gros besoins :

- `pg_basebackup` ;
- snapshots cohérents ;
- continuous archiving.

Ces stratégies nécessitent une expertise supplémentaire.

Ne les impose pas au petit projet.

---

## 38. PITR

Point-In-Time Recovery permet de restaurer à un instant précis via base backup + WAL.

Pertinent si :

- forte criticité ;
- RPO faible ;
- beaucoup de changements entre backups.

Complexité supérieure.

Documente avant adoption.

---

## 39. RPO

Définis le Recovery Point Objective si le projet devient critique.

Question :

> Combien de données au maximum peut-on perdre ?

Avec backup quotidien uniquement, on peut perdre potentiellement jusqu’à environ une journée de modifications.

Ne cache pas cette réalité.

---

## 40. RTO

Recovery Time Objective :

> Combien de temps peut-on rester indisponible ?

Un petit projet peut accepter une restauration manuelle plus longue.

Un service critique peut nécessiter automatisation/réplication.

---

## 41. Backup réussi

Un script qui termine sans erreur ne prouve pas que le dump est valide.

Vérifie :

- fichier existe ;
- taille non anormale ;
- code retour ;
- archive lisible ;
- stockage externe réussi.

---

## 42. Taille minimum

Une vérification de taille peut détecter un dump vide/anormal.

Ne fixe pas un seuil universel.

Compare éventuellement aux backups précédents.

---

## 43. `pg_restore --list`

Pour une archive custom, utilise une inspection type :

```bash
pg_restore --list backup.dump
```

pour vérifier que l’archive est lisible.

Cela ne remplace pas une restauration complète.

---

## 44. Checksum

Calcule un checksum pour détecter une corruption/transfert incorrect.

Exemple :

```text
SHA-256
```

Stocke le checksum avec le backup ou dans un catalogue fiable.

---

## 45. Vérification après copie

Après upload distant :

- vérifier présence ;
- taille ;
- checksum si outil le permet.

Ne supprime pas immédiatement la copie locale avant confirmation du transfert.

---

## 46. Monitoring

Une sauvegarde qui échoue silencieusement est dangereuse.

Prévois :

- logs ;
- statut ;
- notification en cas d’échec ;
- contrôle du dernier backup réussi.

---

## 47. Pas de notification de succès obligatoire

Une notification quotidienne « succès » peut devenir du bruit.

Préférer :

- alerte sur échec ;
- rapport périodique ;
- dashboard/état si disponible.

---

## 48. Âge du dernier backup

Un health check opérationnel peut surveiller :

```text
dernier backup réussi < 26h
```

si backup quotidien.

Ne mélange pas ce contrôle avec le health endpoint public Django.

---

## 49. Test de restauration

Une restauration doit être testée périodiquement.

Minimum recommandé pour un petit projet sérieux :

- test après mise en place ;
- test après changement majeur de stratégie ;
- test périodique.

La fréquence exacte dépend de la criticité.

---

## 50. Environnement de restauration

Ne teste pas en écrasant la production.

Utilise :

- base temporaire ;
- staging ;
- VM/container dédié ;
- machine de test.

---

## 51. Test DB

Procédure type :

1. créer base vide ;
2. restaurer archive ;
3. lancer checks ;
4. vérifier tables/données ;
5. démarrer application avec cette DB si possible ;
6. exécuter smoke tests.

---

## 52. `pg_restore`

Pour archive custom :

```bash
pg_restore ...
```

La base cible doit être préparée selon la procédure choisie.

Documente propriétaire/rôles/extensions.

---

## 53. `--clean`

L’option de nettoyage peut supprimer des objets existants.

Ne l’utilise pas sur une base non dédiée sans comprendre son impact.

---

## 54. `--create`

Peut être utile selon procédure, mais nécessite les permissions adaptées.

Ne l’emploie pas mécaniquement.

---

## 55. Owner

Lors de restauration vers un environnement différent, les owners peuvent poser problème.

Analyse :

- `--no-owner` ;
- rôle cible ;
- permissions.

Ne corrige pas avec un superuser permanent.

---

## 56. Restore media

Restaure les media dans un emplacement temporaire/staging.

Vérifie :

- nombre approximatif ;
- fichiers critiques ;
- permissions ;
- liens DB.

---

## 57. Smoke tests après restore

Teste :

- démarrage Django ;
- login ;
- lecture d’un objet ;
- lecture d’un media ;
- feature critique.

Cela prouve davantage qu’un simple `pg_restore` vert.

---

## 58. Restauration partielle

`pg_restore` peut permettre des restaurations sélectives avec les formats adaptés.

Mais une restauration partielle peut casser les relations.

Utilise seulement avec compréhension du schéma.

---

## 59. Restauration production

Avant restore production :

1. identifier incident ;
2. arrêter/limiter les écritures ;
3. sauvegarder l’état courant si utile ;
4. choisir point de restauration ;
5. valider conséquences ;
6. restaurer ;
7. migrations si nécessaires ;
8. health/smoke ;
9. réouvrir trafic.

---

## 60. Ne pas écraser immédiatement

Même une base corrompue peut contenir des données utiles pour investigation/récupération.

Lorsque possible, conserve une copie avant remplacement.

---

## 61. Compatibilité code/DB

Une vieille sauvegarde peut correspondre à un ancien schéma.

Après restauration, il peut être nécessaire de :

- déployer le code correspondant ;
- puis appliquer les migrations.

Documente le lien entre release et backup.

---

## 62. Metadata backup

Conserve idéalement avec le backup :

- timestamp ;
- environnement ;
- version PostgreSQL ;
- commit/release applicative ;
- méthode ;
- statut ;
- checksum.

Pas de secret.

---

## 63. Catalogue

Un fichier catalogue ou logs peuvent permettre de savoir quels backups existent.

Évite de dépendre uniquement du nom des fichiers.

---

## 64. DB + media synchronisés

Pour une restauration complète, sélectionne des backups proches dans le temps.

Documente si les deux ne sont pas atomiquement synchronisés.

---

## 65. Sauvegardes Django sessions

Si sessions DB :

elles sont incluses dans la DB.

Après restauration, de vieilles sessions pourraient redevenir présentes.

Selon incident, envisage de purger/invalider les sessions.

---

## 66. Tokens

Même problème pour certains tokens persistants.

Après incident sécurité, restaurer une DB peut réintroduire :

- tokens ;
- clés API DB ;
- sessions.

Charge `django-security`.

---

## 67. Secrets après restore

Les secrets d’environnement ne doivent pas provenir automatiquement d’un vieux backup si cela réintroduit une clé compromise.

La restauration des données et la gestion des secrets sont distinctes.

---

## 68. RGPD

Les backups peuvent contenir des données supprimées du système actif.

Documente :

- rétention ;
- accès ;
- cycle de suppression ;
- politique de restauration.

Ne promets pas une suppression instantanée de toutes les copies si la stratégie backup ne le permet pas.

---

## 69. Données personnelles

Les backups doivent avoir au moins les mêmes protections que les données actives.

Souvent plus strictes, car ils contiennent un snapshot massif.

---

## 70. Logs backup

Ne log pas :

- password DB ;
- secrets ;
- contenu sensible.

Log utile :

- début ;
- fin ;
- taille ;
- destination ;
- checksum ;
- erreur.

---

## 71. Espace disque

Avant dump :

- vérifier espace disponible.

Un backup qui remplit le disque peut mettre la production en panne.

---

## 72. Temp files

Si le workflow crée des fichiers temporaires :

- emplacement ;
- permissions ;
- nettoyage après succès/échec.

Ne laisse pas des dumps sensibles dans `/tmp` sans protection.

---

## 73. Concurrence de backups

Empêche deux jobs backup quotidiens de s’exécuter simultanément si le précédent dure encore.

Utilise :

- systemd ;
- lockfile sûr ;
- outil backup.

---

## 74. Timeout

Un backup anormalement long doit pouvoir être détecté.

Ne tue pas arbitrairement un dump normal sur une grosse base sans métriques.

---

## 75. Ressources

Le dump peut consommer :

- CPU ;
- I/O ;
- réseau.

Planifie à une heure creuse si nécessaire.

---

## 76. Horaire

Pour un backup quotidien, choisis une heure stable adaptée au trafic.

Le skill ne doit pas inventer l’heure sans contexte lors du déploiement final.

---

## 77. Sauvegarde staging

Staging peut nécessiter ses propres backups si des données de test importantes existent.

Mais la priorité est production.

Ne mélange pas les archives staging/prod.

---

## 78. Noms d’environnement

Toujours inclure clairement :

```text
prod
staging
```

dans répertoire ou metadata.

Évite les restaurations croisées accidentelles.

---

## 79. Test sur staging

Une bonne stratégie est de restaurer périodiquement un backup prod dans un environnement isolé/anonymisé selon politique.

Attention aux données personnelles et emails externes.

---

## 80. Neutralisation staging

Après restore prod vers test/staging :

- emails ;
- SMS ;
- paiements ;
- webhooks ;
- tâches externes ;

doivent être neutralisés avant ouverture.

---

## 81. Anonymisation

Si les données production sont utilisées hors production, anonymise lorsque possible.

Ne considère pas un réseau interne comme protection suffisante.

---

## 82. Backup cloud

Si stockage cloud :

- chiffrement ;
- versioning ;
- lifecycle ;
- permissions IAM ;
- MFA/admin ;
- logs d’accès.

Ne rends pas un bucket public.

---

## 83. Backup NAS

Si NAS :

- compte dédié ;
- permissions ;
- snapshots si disponibles ;
- protection ransomware ;
- capacité.

---

## 84. Disque USB

Pour petit serveur, un disque externe peut être une seconde copie utile.

Mais un disque toujours branché reste vulnérable à certains incidents.

Rotation/déconnexion est plus résiliente.

---

## 85. Validation périodique

Crée un rapport simple :

```text
Dernier backup DB : OK
Dernier backup media : OK
Copie distante : OK
Dernier restore test : date
```

Ne considère pas uniquement la présence du fichier.

---

## 86. Documentation

Maintiens :

```text
docs/operations/backup-restore.md
```

avec :

- quoi sauvegarder ;
- fréquence ;
- rétention ;
- destination ;
- chiffrement ;
- automatisation ;
- vérification ;
- restauration ;
- test restore ;
- incident.

---

## 87. Runbook restore

La documentation doit être assez précise pour qu’un autre opérateur puisse restaurer.

Mais ne mets pas de secrets.

---

## 88. Script backup

Le script doit :

- `set -e` ou gestion robuste équivalente ;
- validation des variables ;
- permissions ;
- code retour ;
- logs ;
- cleanup ;
- vérification archive ;
- rotation prudente.

Ne crée pas un script shell dangereux avec des chemins non validés.

---

## 89. Script restore

Un script restore est plus dangereux.

Par défaut, il doit cibler une base explicitement définie.

Il ne doit jamais supposer « production ».

Exiger confirmation ou variable explicite pour opération destructive.

---

## 90. Dry-run

Quand possible, propose une phase d’inspection avant restauration :

- liste archive ;
- cible ;
- taille ;
- metadata.

---

## 91. Automatisation restore

Ne restaure jamais automatiquement la production après détection d’un incident.

La restauration production nécessite une décision humaine explicite.

---

## 92. Test automatique restore

En revanche, un restore dans une base temporaire peut être automatisé périodiquement.

Très utile pour prouver la validité des backups.

---

## 93. Nettoyage DB test

Après restore test :

- supprimer la DB temporaire ;
- supprimer media temporaires ;
- conserver rapport ;
- ne conserver aucune donnée prod inutile.

---

## 94. Quality gate déploiement

Avant une migration risquée, `deployment` doit vérifier le statut backup.

Si aucun backup exploitable récent :

bloquer l’opération selon criticité.

---

## 95. Échec backup

Si le backup quotidien échoue :

- conserver ancien backup ;
- alerter ;
- ne pas purger les anciennes générations ;
- diagnostiquer avant la prochaine rotation.

---

## 96. Échec transfert distant

Si dump local réussi mais copie distante échoue :

- conserver copie locale ;
- alerter ;
- réessayer selon politique.

---

## 97. Échec de rotation

Une rotation qui échoue ne doit pas rendre le backup courant invalide.

Log et alerte.

---

## 98. Restore test échoué

Considère cela comme problème important.

Un backup non restaurable doit être traité avant de continuer à faire confiance à la stratégie.

---

## 99. Definition of Done backup

La stratégie est considérée prête lorsque :

- DB sauvegardée quotidiennement ;
- media couverts si nécessaires ;
- rétention définie ;
- stockage protégé ;
- copie hors serveur si possible ;
- secret hors script ;
- chiffrement analysé ;
- job automatique ;
- erreurs visibles ;
- archive vérifiée ;
- restauration documentée ;
- restauration testée avec succès ;
- monitoring du dernier backup ;
- documentation à jour.

---

## 100. Principe final

Le vrai produit d’un système de backup n’est pas le fichier `.dump`.

Le vrai produit est la capacité démontrée à remettre le service en état avec des données acceptables après un incident.
