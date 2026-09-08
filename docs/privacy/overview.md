# Protection des données personnelles

La page d'information interne est disponible à l'adresse `/protection-des-donnees/` pour les utilisateurs authentifiés. Elle présente les traitements réalisés dans SPPE Sud-Avesnois et utilise une balise `noindex, nofollow`.

Le responsable du traitement retenu est la **Communauté de Communes Sud-Avesnois (CCSA)** ; SPPE Sud-Avesnois est le nom de l'application. La base légale principale est l'exécution d'une mission d'intérêt public. Le point de contact provisoire pour l'exercice des droits est `contact@cc-sudavesnois.fr`.

Cette documentation ne constitue pas une validation juridique. La page, les finalités, la base légale et les durées doivent être validées avant production par le DPO ou le responsable compétent. Les personnes externes figurant dans l'annuaire doivent être informées séparément puisqu'elles n'ont pas accès à la page interne.

## Inventaire synthétique

| Catégorie | Finalité | Accès | Conservation retenue |
|---|---|---|---|
| Coordonnées des structures et responsables | gérer l'annuaire CTG | agents et partenaires CTG habilités, superutilisateurs pour l'administration | révision annuelle, puis rectification ou suppression si la fiche n'est plus utile ou exacte |
| Email et nom des comptes | authentification, habilitations et attribution des actions | utilisateur concerné et superutilisateurs | durée de l'habilitation, puis suppression sous 30 jours |
| Journal d'audit | sécurité, diagnostic et responsabilité des changements | superutilisateurs | 12 mois |
| Fichiers d'import temporaires | mise à jour de l'annuaire | superutilisateur ayant lancé l'import | durée de la requête, sans archivage applicatif |
| Sauvegardes SQLite | continuité et restauration | exploitants autorisés | 6 mois maximum |
| Logs techniques | diagnostic et sécurité | exploitants autorisés | 3 mois maximum |

Les données de démonstration du code courant sont fictives et utilisent le domaine réservé `example.test`. De vraies coordonnées étaient présentes dans un ancien état Git : elles restent potentiellement accessibles dans l'historique et nécessitent une décision coordonnée avant toute réécriture de celui-ci.

## Flux et tiers

- o2switch héberge l'application, SQLite, Redis, SMTP, logs et sauvegardes JetBackup ;
- un stockage externe est recommandé pour une copie chiffrée des sauvegardes ;
- OpenStreetMap reçoit directement du navigateur les requêtes de tuiles cartographiques et les métadonnées réseau associées ;
- la Base Adresse Nationale (`api-adresse.data.gouv.fr`, service public français) reçoit côté serveur l'adresse tapée dans le tableau de bord pour renvoyer latitude/longitude, sans nom, e-mail ni téléphone ; Nominatim/OpenStreetMap n'est interrogé qu'en repli ;
- Chart.js, Leaflet, MarkerCluster, Tailwind et Inter sont servis localement ;
- aucun outil analytics ou publicitaire n'est intégré.

Tout futur service de monitoring, emailing externe, analytics ou stockage constitue un nouveau sous-traitant à documenter avant activation.

## Mesures livrées

- dashboard limité aux superutilisateurs et protection CSRF native ;
- import borné, validé avant écriture et atomique ;
- messages d'import contrôlés sans afficher les exceptions internes ;
- transport JSON sûr et échappement des contenus de la carte ;
- mots de passe validés avec les validateurs Django et stockés par `set_password` ;
- audit de l'ensemble des créations, modifications et suppressions (structures, communes, types, comptes, décisions d'inscription, notifications, sauvegardes) avec attribution de l'acteur et valeurs modifiées, consultable uniquement par les superutilisateurs ;
- sauvegarde cohérente et vérifiable ;
- exemples de configuration dépourvus de secrets réels ;
- Content Security Policy par nonce sur les pages applicatives, sans `unsafe-inline` ni `unsafe-eval` pour les scripts ; l'admin Django reçoit une politique assouplie sur les scripts (templates internes sans nonce) mais conserve les directives de confinement ;
- unicité de l'adresse email appliquée à tous les chemins de création, y compris l'admin Django ;
- rétention du journal d'audit pilotée par la commande `purge_audit_log`.

Les cookies de session et CSRF sont nécessaires à l'authentification et à la sécurité des formulaires. La clé `bddpe-theme`, stockée localement dans le navigateur, conserve uniquement le thème clair ou sombre. Aucun bandeau de consentement n'est requis tant qu'aucun traceur optionnel n'est ajouté.

La rétention de 12 mois du journal d'audit peut être appliquée par la commande `purge_audit_log`, dont la valeur par défaut est de 365 jours. La suppression des comptes sous 30 jours, la rétention des logs pendant 3 mois et la révision annuelle des fiches relèvent également des procédures d'exploitation à formaliser.

## Actions organisationnelles avant mise en ligne

1. faire valider par le DPO ou le responsable compétent la page interne, les finalités, la base légale et les durées retenues ;
2. définir et remettre une information séparée aux personnes externes dont les données figurent dans l'annuaire ;
3. vérifier quelles coordonnées doivent réellement être accessibles aux utilisateurs internes ;
4. formaliser les demandes d'accès, rectification, effacement, limitation et opposition ;
5. appliquer les procédures de départ des agents, de purge des logs et de révision annuelle des fiches ;
6. examiner les contrats et localisations des sous-traitants ;
7. décider du traitement de l'historique Git contenant d'anciennes données réelles.

Une suppression de la base active ne retire pas immédiatement la donnée des sauvegardes. Elle disparaît à l'expiration de leur rétention ; une restauration doit éviter sa réintroduction injustifiée.

Références administratives : [mentions légales de la CCSA](https://cc-sudavesnois.fr/mentions-legales/) et [obligation d'information des personnes selon la CNIL](https://www.cnil.fr/fr/informer-les-personnes).
