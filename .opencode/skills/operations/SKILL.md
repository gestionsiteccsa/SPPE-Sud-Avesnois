---
name: operations
description: Exploite et supervise un projet Django en production. À utiliser pour logs, monitoring, health checks, alertes, incidents, espace disque, disponibilité, workers, tâches planifiées, maintenance, runbooks, observabilité et diagnostic. Ne dépend d’aucun fournisseur précis et s’adapte à une petite production sur mini-PC comme à une infrastructure plus mature.
compatibility: opencode
metadata:
  framework: django
  purpose: operations
  language: fr
  workflow-parent: project-workflow
---

# Operations Django

## 1. Mission

Tu es responsable de l’exploitation du projet une fois déployé.

Ton objectif est que le service soit :

- observable ;
- diagnostiquable ;
- maintenable ;
- surveillé ;
- récupérable ;
- prévisible en cas d’incident ;
- exploitable par quelqu’un d’autre que son auteur.

Tu dois éviter deux extrêmes :

- aucune supervision ;
- une stack d’observabilité disproportionnée pour un petit projet.

---

## 2. Coordination

Avant toute décision :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. charge si disponibles :
   - `deployment`
   - `backup-restore`
   - `django-security`
   - `django-performance`
   - `documentation`
4. inspecte l’infrastructure réelle.

Ne suppose pas Kubernetes, Prometheus ou Grafana sans besoin.

---

## 3. Questions

Pose au maximum 2 questions à la fois si une décision d’exploitation dépend vraiment du contexte.

Exemples :

- Le serveur sera-t-il accessible 24/7 ?
- Souhaites-tu recevoir des alertes par email, messagerie ou autre canal ?

Si le besoin n’est pas défini, propose une solution minimale viable.

---

## 4. Observabilité minimale

Pour une petite production sérieuse, surveille au minimum :

- disponibilité HTTP ;
- erreurs applicatives ;
- espace disque ;
- mémoire ;
- CPU ;
- PostgreSQL ;
- backups ;
- certificats TLS ;
- état des services.

---

## 5. Logs Django

Configure des logs suffisamment utiles pour diagnostiquer :

- erreurs ;
- warnings ;
- événements opérationnels importants.

Évite un niveau DEBUG en production en permanence.

---

## 6. Logs sensibles

Ne log jamais :

- passwords ;
- tokens ;
- clés API ;
- cookies de session ;
- headers Authorization ;
- contenu sensible inutile.

Charge `django-security`.

---

## 7. Structure des logs

Préfère des logs structurés et cohérents lorsque cela apporte une vraie valeur.

Exemples de champs :

- timestamp ;
- niveau ;
- logger ;
- message ;
- request id ;
- user id non sensible si pertinent ;
- path ;
- status.

Ne sur-structure pas un petit projet si journald suffit.

---

## 8. Request ID

Un identifiant de requête peut aider à suivre une erreur à travers :

- reverse proxy ;
- Django ;
- workers ;
- services externes.

Ajoute-le lorsque le projet devient assez complexe pour en tirer bénéfice.

---

## 9. Rotation des logs

Les logs ne doivent jamais remplir le disque.

Utilise :

- journald ;
- logrotate ;
- mécanisme plateforme.

Définis une rétention raisonnable.

---

## 10. Journald

Sur Linux/systemd, journald peut suffire à un petit projet.

Documente :

```bash
journalctl -u <service>
```

et les commandes utiles.

---

## 11. Health check

Prévois un endpoint ou mécanisme simple.

Exemple :

```text
/health/
```

Réponse minimale :

- application vivante ;
- pas de détail sensible.

---

## 12. Readiness

Si nécessaire, distingue :

- liveness ;
- readiness.

Une readiness peut vérifier :

- DB accessible ;
- dépendance critique disponible.

Ne surcharge pas le health check public avec des tests coûteux.

---

## 13. Health check privé

Pour contrôles plus détaillés, utilise un endpoint interne/protégé ou un outil d’exploitation.

Ne révèle pas publiquement :

- versions ;
- hôtes DB ;
- détails d’erreurs ;
- architecture interne.

---

## 14. Monitoring externe

Surveille l’application depuis l’extérieur si possible.

Un serveur peut croire qu’il fonctionne alors que :

- DNS cassé ;
- certificat expiré ;
- reverse proxy arrêté ;
- route réseau inaccessible.

---

## 15. Uptime

Pour petit projet, une simple sonde HTTP périodique peut suffire.

Pour projet critique, ajoute :

- multi-région ;
- métriques ;
- SLO/SLA.

Ne complexifie pas prématurément.

---

## 16. Alertes

Une alerte doit être :

- actionnable ;
- pertinente ;
- peu bruyante.

Évite d’alerter sur chaque warning.

---

## 17. Niveaux d’alerte

Exemple :

### Critique
- site inaccessible ;
- DB inaccessible ;
- disque presque plein ;
- backup en échec prolongé ;
- certificat sur le point d’expirer.

### Warning
- mémoire élevée ;
- erreurs en hausse ;
- backup distant retardé.

---

## 18. Alert fatigue

Si trop d’alertes sont ignorées, le système est mal conçu.

Réduis le bruit.

Une alerte doit généralement impliquer une action humaine possible.

---

## 19. CPU

Surveille les pics prolongés.

Un pic court n’est pas forcément un problème.

Analyse :

- requête lente ;
- boucle ;
- image/PDF ;
- worker ;
- attaque ;
- index manquant.

---

## 20. Mémoire

Sur mini-PC, la mémoire est critique.

Surveille :

- consommation Django ;
- PostgreSQL ;
- workers ;
- Docker ;
- cache.

Évite un nombre de workers dépassant la RAM disponible.

---

## 21. Swap

La swap peut éviter certains crashs mais ne corrige pas un manque structurel de RAM.

Une application qui swap continuellement sera lente.

---

## 22. Disque

Surveille :

- espace libre ;
- inodes ;
- logs ;
- backups ;
- media ;
- Docker images ;
- PostgreSQL.

Une alerte disque est critique.

---

## 23. Seuil disque

Définis des seuils raisonnables.

Exemple :

- warning < 20 % libre ;
- critique < 10 % libre.

Adapte à la taille/rapidité de croissance.

---

## 24. Docker disk usage

Si Docker :

surveille :

- images anciennes ;
- containers ;
- volumes ;
- build cache.

Ne lance jamais automatiquement un `docker system prune -a --volumes` en production.

---

## 25. PostgreSQL

Surveille :

- disponibilité ;
- connexions ;
- taille DB ;
- locks ;
- requêtes lentes ;
- espace ;
- backups.

Pour petit projet, une supervision simple suffit.

---

## 26. Connexions DB

Une mauvaise configuration de workers peut épuiser les connexions PostgreSQL.

Analyse :

- processus web ;
- workers async ;
- pool ;
- tâches.

Ne monte pas `max_connections` aveuglément.

---

## 27. Slow queries

Active une stratégie de détection des requêtes lentes si nécessaire.

Utilise PostgreSQL/logging/APM selon infrastructure.

Ne log pas toutes les requêtes en production en permanence.

---

## 28. Locks

Un lock long peut bloquer le site.

Analyse particulièrement après :

- migration ;
- import ;
- transaction longue.

Charge `django-database`.

---

## 29. Taille DB

Surveille la croissance.

Une croissance anormale peut venir de :

- logs stockés en DB ;
- historique infini ;
- sessions ;
- données temporaires ;
- pièces jointes mal stockées.

---

## 30. Sessions

Si sessions DB, planifie le nettoyage des sessions expirées.

Django fournit des mécanismes adaptés.

Documente la tâche planifiée.

---

## 31. Cache

Si Redis/memcached :

surveille :

- mémoire ;
- disponibilité ;
- évictions ;
- hit rate ;
- connexions.

Ne fais pas du cache une dépendance critique sans comprendre le fallback.

---

## 32. Workers

Si Celery/RQ/queue :

surveille :

- process vivant ;
- backlog ;
- erreurs ;
- retries ;
- tâches bloquées ;
- durée.

---

## 33. Queue length

Une file qui grandit continuellement signale :

- workers insuffisants ;
- tâche trop lente ;
- erreur ;
- pic de charge.

Ne résous pas uniquement en ajoutant des workers sans analyser la cause.

---

## 34. Scheduler

Si tâches périodiques :

surveille que le scheduler est unique lorsqu’il doit l’être.

Évite deux schedulers lançant la même tâche.

---

## 35. Cron/systemd timers

Toutes les tâches planifiées importantes doivent être documentées.

Inclure :

- fréquence ;
- utilisateur ;
- commande ;
- logs ;
- impact.

---

## 36. Tâches critiques

Exemples :

- backups ;
- purge ;
- imports ;
- renouvellement ;
- rapports.

Une tâche critique doit avoir :

- statut ;
- alerte en cas d’échec ;
- runbook si nécessaire.

---

## 37. Certificats TLS

Surveille la date d’expiration.

Ne découvre pas le problème le jour où HTTPS casse.

Automatise le renouvellement et teste-le.

---

## 38. DNS

Un incident DNS peut rendre le site inaccessible sans panne serveur.

Documente :

- fournisseur ;
- zone ;
- TTL ;
- responsables.

Ne stocke pas les credentials DNS dans le wiki.

---

## 39. Reverse proxy

Surveille :

- service actif ;
- erreurs 5xx ;
- certificats ;
- espace logs.

Un 502/504 peut venir de Django, du proxy ou du réseau local.

---

## 40. Codes HTTP

Observe les tendances :

- 2xx ;
- 4xx ;
- 5xx.

Une hausse 500 est critique.

Une hausse 404 peut indiquer mauvais lien ou scan hostile.

---

## 41. Taux d’erreur

Ne regarde pas seulement le nombre brut.

Une hausse proportionnelle au trafic peut être normale.

Utilise taux/ratio si métriques disponibles.

---

## 42. Temps de réponse

Surveille :

- médiane ;
- p95 ;
- p99 si projet assez important.

Pour petit site, temps moyen + logs lents peuvent suffire.

---

## 43. SLO

N’introduis pas des SLO formels sans besoin.

Pour un service métier critique, ils peuvent devenir utiles.

---

## 44. Maintenance

Documente les opérations régulières :

- mises à jour OS ;
- dépendances ;
- backups ;
- certificats ;
- nettoyage ;
- tests restore ;
- rotation secrets.

---

## 45. Patch Tuesday / calendrier fixe

Ne lie pas le projet à un jour précis universel.

Crée un rythme de maintenance adapté.

---

## 46. Mise à jour OS

Avant mise à jour majeure :

- backup ;
- espace ;
- compatibilité ;
- fenêtre ;
- reboot possible.

Ne mélange pas update OS et release applicative importante si cela complique le diagnostic.

---

## 47. Mise à jour dépendances

Charge `git-quality`.

Évalue :

- sécurité ;
- changelog ;
- compatibilité ;
- tests.

---

## 48. Redémarrage

Après reboot serveur, vérifier que démarrent automatiquement :

- DB ;
- web ;
- workers ;
- proxy ;
- backup timers ;
- monitoring.

---

## 49. Test reboot

Pour un nouveau serveur, un reboot contrôlé est un bon test d’exploitation.

Ne le fais pas sans accord explicite.

---

## 50. Incident

Quand un incident arrive :

1. préserver les données ;
2. évaluer impact ;
3. stabiliser ;
4. diagnostiquer ;
5. restaurer service ;
6. analyser cause ;
7. documenter ;
8. prévenir récidive.

---

## 51. Priorité incident

Ordre général :

1. sécurité / intégrité ;
2. disponibilité ;
3. performance ;
4. confort.

Ne sacrifie pas les données pour rétablir vite.

---

## 52. Runbook incident

Structure :

```text
Symptôme
Impact
Vérifications
Actions sûres
Escalade
Rollback/restore
Validation
```

---

## 53. Incident DB indisponible

Vérifie :

- service ;
- disque ;
- connexions ;
- logs ;
- réseau ;
- credentials ;
- locks.

Ne redémarre pas PostgreSQL aveuglément sans regarder les logs.

---

## 54. Incident 502

Vérifie :

- process Django ;
- socket/port ;
- proxy ;
- logs ;
- timeout ;
- RAM.

---

## 55. Incident disque plein

Actions :

- identifier source ;
- préserver DB ;
- arrêter croissance ;
- nettoyer éléments sûrs ;
- agrandir stockage si nécessaire.

Ne supprime jamais des backups ou volumes au hasard.

---

## 56. Incident mémoire

Vérifie :

- OOM killer ;
- nombre workers ;
- leak ;
- tâche lourde ;
- cache ;
- DB.

---

## 57. Incident certificat

Vérifie :

- renouvellement ;
- DNS ;
- port 80/443 ;
- permissions ;
- logs ACME.

---

## 58. Incident backup

Charge `backup-restore`.

Ne purge pas les anciennes sauvegardes tant que la nouvelle stratégie échoue.

---

## 59. Incident sécurité

Charge `django-security`.

Préserve :

- logs ;
- état ;
- preuves utiles.

Ne supprime pas immédiatement tous les logs.

---

## 60. Postmortem

Après incident important, documente :

- chronologie ;
- impact ;
- cause ;
- détection ;
- résolution ;
- actions préventives.

Sans recherche de culpable.

---

## 61. Action items

Chaque action postmortem doit devenir :

- tâche ;
- priorité ;
- propriétaire si workflow humain ;
- critère de fin.

---

## 62. Monitoring utilisateur

Si possible, surveille une vraie action utilisateur critique, pas seulement `/health/`.

Exemple :

- page publique ;
- endpoint lecture simple.

N’utilise pas un compte admin pour un monitoring externe si inutile.

---

## 63. Synthetic checks

Des tests synthétiques peuvent vérifier :

- login ;
- recherche ;
- page critique.

N’en ajoute pas trop.

---

## 64. Error tracking

Un outil dédié peut centraliser :

- stack traces ;
- fréquence ;
- contexte.

Choisis un fournisseur seulement si utile.

Ne log pas de PII excessive.

---

## 65. APM

APM est utile pour projet plus complexe.

Permet :

- traces ;
- DB ;
- appels externes ;
- transactions.

Ne l’impose pas à un petit projet.

---

## 66. Metrics

Métriques utiles :

- requests ;
- latency ;
- errors ;
- queue ;
- DB ;
- backups ;
- resources.

Commence petit.

---

## 67. Prometheus/Grafana

Bon choix pour infrastructure auto-hébergée plus mature.

Mais ajoute :

- maintenance ;
- stockage ;
- sécurité.

Ne les installe pas automatiquement.

---

## 68. Mini-PC

Pour un mini-PC :

priorités :

- disque ;
- température si matériel pertinent ;
- RAM ;
- reboot ;
- alimentation ;
- réseau ;
- backups hors machine.

---

## 69. UPS

Pour un serveur maison, un onduleur peut améliorer la résilience.

Ce n’est pas une exigence logicielle, mais documente comme recommandation infrastructure si disponibilité importante.

---

## 70. Réseau domestique

Si hébergé à domicile :

analyse :

- IP publique ;
- CGNAT ;
- box ;
- redirections ;
- DNS dynamique ;
- firewall ;
- coupures ISP.

Le skill deployment doit traiter la configuration.

---

## 71. Internet coupé

Un serveur maison peut rester sain mais inaccessible.

Monitoring externe permet de détecter cela.

---

## 72. Électricité

Une coupure peut corrompre ou interrompre.

PostgreSQL est conçu pour la récupération crash, mais backups restent nécessaires.

---

## 73. Température

Sur matériel compact, température élevée peut réduire performance/stabilité.

Utilise outils système si pertinent.

Ne transforme pas operations en monitoring hardware complet sans besoin.

---

## 74. SMART disque

Sur serveur local, SMART peut aider à détecter une dégradation disque.

Si disponible, surveille les erreurs critiques.

Un SMART « OK » ne remplace pas les backups.

---

## 75. RAID

RAID améliore disponibilité mais n’est pas un backup.

Ne confonds jamais les deux.

---

## 76. Snapshot

Snapshots peuvent aider aux restores rapides.

Mais ils ne remplacent pas une copie hors serveur.

---

## 77. Nettoyage

Planifie prudemment :

- sessions expirées ;
- vieux backups selon politique ;
- logs ;
- fichiers temporaires ;
- caches ;
- Docker images.

Toute purge doit avoir une cible claire.

---

## 78. Media orphelins

Ne supprime pas automatiquement les fichiers media non référencés sans procédure fiable.

Une relation absente peut être un bug ou une restauration partielle.

---

## 79. DB maintenance

PostgreSQL gère VACUUM automatiquement via autovacuum.

Ne lance pas des maintenances agressives sans comprendre.

Surveille plutôt si autovacuum est en difficulté.

---

## 80. Migrations production

Après migration :

- vérifier durée ;
- erreurs ;
- locks ;
- espace ;
- application.

Documente les incidents.

---

## 81. Feature flags

Pour rollout risqué, un feature flag peut aider.

Mais ajoute complexité.

Utilise seulement pour besoin réel.

---

## 82. Rollback feature

Un rollback applicatif doit être distinct d’un rollback DB.

Documente les dépendances.

---

## 83. Configuration drift

Le serveur ne doit pas dériver silencieusement.

Versionne autant que possible :

- services ;
- proxy config ;
- scripts ;
- timers.

Ne modifie pas manuellement sans documenter.

---

## 84. Infrastructure as Code

Pour une infrastructure mature, IaC peut devenir pertinent.

Ne l’impose pas à un premier mini-PC.

---

## 85. Inventaire

Documente :

- serveur ;
- OS ;
- domaine ;
- services ;
- ports ;
- emplacement backups ;
- dépendances externes.

Pas de secrets.

---

## 86. Versions

Conserve une manière simple de connaître :

- commit déployé ;
- Django ;
- Python ;
- PostgreSQL.

Ne les expose pas publiquement sans besoin.

---

## 87. Capacity planning

Surveille la tendance avant saturation :

- DB ;
- media ;
- backups ;
- RAM ;
- CPU.

Un problème prévisible doit devenir une tâche avant panne.

---

## 88. Seuils dynamiques

Au début, des seuils statiques simples suffisent.

Avec historique, adapte selon tendances.

---

## 89. Tâches automatiques dangereuses

Ne crée jamais une tâche automatique qui :

- redémarre continuellement ;
- supprime massivement ;
- restaure prod ;
- prune volumes ;
- force migrations.

Les actions destructrices nécessitent contrôle.

---

## 90. Auto-restart

Un restart automatique sur crash est généralement utile.

Mais une boucle de crash doit alerter.

Ne masque pas un bug avec `Restart=always` sans visibilité.

---

## 91. Restart storm

Si service redémarre sans cesse :

- logs ;
- backoff ;
- limite ;
- alerte.

---

## 92. Maintenance page

Prévois une page de maintenance seulement si les opérations nécessitent une indisponibilité visible.

Ne la rends pas permanente par défaut.

---

## 93. Documentation

Maintiens :

```text
docs/operations/
├── overview.md
├── monitoring.md
├── incidents.md
├── maintenance.md
└── runbooks/
```

Adapte à la taille réelle du projet.

---

## 94. Runbooks utiles

Exemples :

- site down ;
- DB down ;
- disque plein ;
- backup failed ;
- restore ;
- certificat expiré ;
- worker bloqué.

---

## 95. Tableau de bord minimal

Même sans Grafana, une page/commande interne ou doc peut résumer :

- services ;
- disque ;
- dernier backup ;
- certificat ;
- version.

Ne crée pas un dashboard custom si les outils système suffisent.

---

## 96. Contrôle périodique

Au minimum périodiquement :

- backup restore test ;
- espace ;
- certificats ;
- dépendances sécurité ;
- OS ;
- logs d’erreur ;
- documentation runbook.

---

## 97. Definition of Done operations

L’exploitation est prête lorsque :

- services supervisés ;
- logs accessibles ;
- rotation ;
- health check ;
- monitoring externe si possible ;
- alertes critiques ;
- disque surveillé ;
- backups surveillés ;
- TLS surveillé ;
- runbooks incidents ;
- tâches planifiées documentées ;
- restart après reboot validé ;
- documentation à jour.

---

## 98. Relecture second développeur

Vérifie :

- qu’est-ce qui casse sans alerte ?
- que se passe-t-il si disque plein ?
- si DB s’arrête ?
- si certificat expire ?
- si backup échoue ?
- si worker meurt ?
- si serveur reboot ?
- si Internet tombe ?

Ajoute seulement les protections pertinentes.

---

## 99. Principe final

Une production n’est pas « terminée » quand la page s’affiche.

Elle est exploitable lorsque quelqu’un peut savoir qu’elle fonctionne, comprendre pourquoi elle ne fonctionne plus, et réagir sans improviser.
