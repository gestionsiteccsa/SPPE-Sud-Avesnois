# Campagnes de mise à jour des assistantes maternelles

Le tableau de bord propose une section **Campagnes** (réservée aux superadmins) pour organiser la vérification annuelle des fiches des assistantes maternelles **sans création de compte utilisateur**.

## Principe

1. Une campagne est créée avec un nom, une date de début, une date de fin et un message d'introduction.
2. Au lancement, le système crée une **invitation par fiche** (type « Assistante maternelle » et fiche affichée sur le site) avec un **jeton personnel aléatoire** (`secrets.token_urlsafe`, stocké haché en base — jamais l'identifiant de la fiche).
3. Les personnes disposant d'une adresse e-mail reçoivent un lien personnel ; les autres passent par courrier (code imprimable) ou par **saisie assistée par un agent** (téléphone ou accueil).
4. La page publique `/verification/<jeton>/` affiche uniquement la fiche concernée et propose : tout est correct, proposer une modification, ne plus exercer, fiche ne me concerne pas.
5. **Aucune modification n'est appliquée directement** : chaque proposition crée une demande traitée dans la **File de validation** (acceptation champ par champ ou refus, avec commentaire interne).
6. La campagne est clôturée manuellement ; les fiches sans réponse passent en « expiré ».

## Cycle de vie

Une campagne passe par les statuts **brouillon → en cours → clôturée → archivée**. Les liens ne sont utilisables que pendant la période et tant que la campagne est en cours ; après soumission, le lien reste consultable en lecture seule (option retenue : l'invitation n'accepte qu'une seule réponse).

## Invitations et statuts

Chaque invitation suit un statut : non contacté, envoi programmé, envoyé, erreur d'envoi, consulté, confirmé sans modification, en attente de validation, validé, refusé, expiré. Les canaux possibles : e-mail, courrier, téléphone, accueil physique.

## Actions du tableau de bord

- **Lancer les envois** (brouillon → en cours) : invitations + jetons + envoi des e-mails ;
- **Relancer les personnes n'ayant pas répondu** : nouveau jeton par invitation, e-mail renvoyé ou courrier régénéré ;
- **Générer les courriers** : page imprimable avec le code personnel par personne sans e-mail (le jeton n'est produit qu'à l'impression) ;
- **Clôturer la campagne** : les sans-réponse passent en « expiré ».

La page de détail présente le résumé (fiches concernées, e-mails envoyés, erreurs, sans e-mail, réponses, taux de réponse, validations en attente, sans réponse) et une liste filtrable des fiches.

## Mode test

Pour tester une campagne sans envoyer d'e-mails aux personnes :

1. cocher **« Mode test (aucun e-mail réel envoyé) »** et saisir **2-3 adresses e-mail de test** (séparées par des virgules) dans le formulaire de création ;
2. **« Lancer en mode test »** (bouton disponible sur la page de la campagne en brouillon, avec saisie des adresses directement sur la page) : toutes les invitations sont créées normalement, mais **chaque e-mail part uniquement aux adresses de test** (sujet préfixé `[TEST]`), y compris pour les fiches prévues en courrier, afin de pouvoir tester toutes les fiches ;
3. un bandeau orange « Mode test » s'affiche sur la page de la campagne et le bouton **« Passer en réel »** apparaît ;
4. « Passer en réel » : les jetons sont **régénérés** (les liens de test deviennent invalides), les e-mails partent aux **vraies adresses** et les invitations courrier repassent en « non contacté » (courrier à imprimer).

Garantie : en mode test, l'adresse réelle d'une fiche n'est jamais utilisée comme destinataire. Les adresses de test reçoivent des liens vers de vraies fiches : à réserver à des adresses internes.

## File de validation

Accessible aux superadmins et aux collaborateurs actifs (limités à leurs communes liées). La page affiche **toutes les demandes soumises**, regroupées en sections par catégorie : proposition de modification, arrêt d'activité, fiche ne me concerne pas, confirmations sans modification — chacune avec son compteur.

Des filtres permettent de cibler : catégorie, statut (en attente / acceptée / refusée), campagne et recherche par nom. La liste est **paginée** (25 demandes par page, les compteurs de chaque catégorie restant globaux). Le tableau présente pour chaque demande : la personne (nom, commune, campagne), le canal, la date de soumission, le **comparatif Avant → Après** par champ modifié (ex. `Téléphone : 06 12 34 56 78 → 06 98 76 54 32`), le statut et le traitement (date, agent, commentaire).

Pour les demandes en attente, la zone de traitement s'affiche sous la ligne : valeur actuelle et valeur proposée par champ ; l'agent peut :

- accepter tous les champs ;
- accepter seulement certains champs ;
- refuser la demande ;
- ajouter un commentaire interne.

Les champs acceptés sont copiés sur la fiche officielle, dans une transaction, avec traçage dans le journal d'audit. Les champs modifiables sont : téléphone, e-mail, adresse, commune, places disponibles et informations complémentaires. Les confirmations sans modification n'attendent aucune validation : elles apparaissent directement avec le badge « Confirmé sans modification ».

## Saisie assistée

La file de validation contient un formulaire « Saisir une demande au nom d'une personne » pour les personnes sans e-mail ou peu à l'aise avec le numérique : l'agent choisit la fiche, le type de demande et le canal (téléphone ou accueil) ; le workflow de validation est identique.

## Sécurité

- jeton aléatoire long, stocké **haché** (SHA-256), jamais d'identifiant de fiche dans l'URL ;
- validité limitée à la période de la campagne, refus automatique après clôture ;
- un seul accès : le jeton ouvre uniquement la fiche associée ;
- aucune modification directe des données officielles depuis la page publique ;
- CSRF sur les formulaires et limitation de débit sur la soumission (20/h par IP) ;
- la page publique n'affiche que les données utiles à la vérification (aucun commentaire agent ni historique).

## Modèles

- `UpdateCampaign` : campagne (nom, dates, statut, message) ;
- `VerificationInvitation` : invitation par fiche (jeton haché, expiration, statut, canal, consultations) ;
- `UpdateRequest` : demande (confirmation, modification, arrêt d'activité, fiche incorrecte) ;
- `UpdateRequestField` : champ proposé avec décision par champ.

L'ensemble est journalisé dans l'audit (création, modification, suppression et décisions de validation). Les opérations groupées de campagne (lancement, relance, passage en réel, génération des courriers) consignent **une entrée résumée** plutôt qu'une entrée par fiche ; les ouvertures de la page publique (compteur « consulté ») ne sont pas journalisées individuellement.

## Limites de la V1

- population fixe : toutes les assistantes maternelles affichées ;
- pas de relances automatiques, de SMS ni de QR code (courrier avec code texte imprimable) ;
- envois synchrones : adapté au volume actuel (~quelques dizaines de fiches) ;
- mode test : les adresses de test sont saisies par campagne ; après « Passer en réel », les liens envoyés en test sont invalidés.