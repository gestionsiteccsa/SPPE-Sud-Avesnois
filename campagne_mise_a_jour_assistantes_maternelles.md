# Campagne annuelle de mise à jour des fiches des assistantes maternelles

## 1. Objectif

Mettre en place un système simple permettant, une fois par an, de demander aux assistantes maternelles de vérifier les informations enregistrées dans le portail interne, sans leur imposer la création d'un compte utilisateur.

Le principe central est le suivant :

- une campagne de vérification est créée dans l'administration ;
- une période d'ouverture est définie, par exemple du 1er janvier au 1er février ;
- un lien individuel et temporaire est généré pour chaque fiche concernée ;
- le lien permet uniquement de consulter la fiche associée et de proposer des modifications ;
- aucune modification n'est appliquée directement ;
- toute proposition doit être validée par un agent ou par la structure responsable ;
- les personnes peuvent également confirmer que leurs informations sont toujours correctes.

---

## 2. Fonctionnement général recommandé

### Étape 1 — Création d'une campagne

Dans l'administration, ajouter une rubrique du type **Campagnes de mise à jour**.

Une campagne contient au minimum :

- un nom, par exemple `Campagne annuelle 2027` ;
- une date de début ;
- une date de fin ;
- un statut : brouillon, programmée, en cours, clôturée ;
- éventuellement un message d'introduction personnalisé ;
- la liste des fiches concernées ;
- les structures ou territoires concernés si la campagne ne porte pas sur toute la base.

Exemple :

- Début : 01/01/2027
- Fin : 01/02/2027
- Population : toutes les assistantes maternelles actives

### Étape 2 — Génération des accès individuels

Lors du lancement de la campagne, le système génère automatiquement un accès unique pour chaque fiche.

Exemple conceptuel :

`https://portail.exemple.fr/verification/7cf1a8e3d9...`

Le lien ne doit pas contenir directement l'identifiant numérique de la fiche, par exemple `/assistante/428/`.

Il vaut mieux utiliser un **jeton aléatoire long et non prédictible**.

Chaque jeton est associé à :

- la campagne ;
- la fiche concernée ;
- sa date de création ;
- sa date d'expiration ;
- son statut ;
- éventuellement le nombre d'ouvertures ;
- la date de première et dernière consultation.

### Étape 3 — Envoi du lien

Si une adresse e-mail est disponible, un message est envoyé automatiquement avec :

- le motif de la campagne ;
- la période pendant laquelle la vérification est possible ;
- le lien personnel ;
- une indication claire expliquant qu'aucun compte n'est nécessaire ;
- une consigne indiquant de ne pas transmettre le lien à une autre personne.

### Étape 4 — Consultation de la fiche

La personne clique sur son lien et voit uniquement la fiche qui lui correspond.

Elle peut ensuite choisir :

1. **Mes informations sont correctes**
2. **Je souhaite signaler une modification**
3. **Je n'exerce plus cette activité**
4. **Cette fiche ne me concerne pas**
5. éventuellement **Je souhaite être recontactée**

### Étape 5 — Proposition de modification

Si la personne choisit de modifier sa fiche, le formulaire affiche les informations actuelles.

Elle modifie uniquement les champs nécessaires.

Exemples :

- téléphone ;
- e-mail ;
- adresse professionnelle ou d'accueil ;
- commune ;
- nombre de places ;
- disponibilité ;
- informations complémentaires ;
- statut d'activité.

Les nouvelles valeurs sont enregistrées dans une demande séparée et **ne remplacent jamais directement les données officielles**.

### Étape 6 — Validation interne

Dans l'administration, une file de validation affiche les demandes reçues.

Pour chaque champ modifié :

| Champ | Valeur actuelle | Valeur proposée |
|---|---|---|
| Téléphone | 06 12 34 56 78 | 06 98 76 54 32 |
| E-mail | ancien@example.fr | nouveau@example.fr |
| Commune | Fourmies | Fourmies |

L'agent peut :

- accepter toute la demande ;
- accepter seulement certains champs ;
- refuser la demande ;
- ajouter un commentaire interne ;
- contacter la personne avant validation.

Une fois validées, les informations approuvées sont copiées dans la fiche officielle.

---

## 3. Ne pas utiliser l'identifiant de base directement dans l'URL

Même si l'idée d'un « ID unique » est correcte fonctionnellement, il ne faut pas exposer un identifiant séquentiel du type :

`/verification/1254/`

car quelqu'un pourrait tester :

- `/verification/1255/`
- `/verification/1256/`
- etc.

Utiliser à la place un jeton aléatoire robuste, par exemple généré avec `secrets.token_urlsafe()` côté Python.

Exemple :

`/verification/Gru9QxXj5H8fzx7tsVtYyAj6Z.../`

Le jeton peut être stocké sous forme hachée en base de données pour limiter les conséquences d'une fuite de base.

---

## 4. Durée de validité

Le lien doit être utilisable uniquement pendant la période de campagne.

Exemple :

- campagne : 01/01/2027 → 01/02/2027 ;
- le lien est considéré comme invalide avant le 1er janvier ;
- il est automatiquement refusé après le 1er février.

Il est conseillé de conserver le jeton en base après expiration, mais en statut expiré, afin de garder l'historique.

### Cas à prévoir

- campagne prolongée de quelques jours ;
- lien révoqué manuellement ;
- nouveau lien généré ;
- e-mail erroné ;
- personne indiquant que la fiche n'est pas la sienne ;
- campagne clôturée avant la date prévue.

---

## 5. Que faire lorsqu'aucune adresse e-mail n'est renseignée ?

C'est le principal cas alternatif à prévoir.

### Solution A — Courrier papier avec code personnel

Un courrier est généré contenant :

- l'adresse générale du portail ;
- un code individuel ;
- éventuellement un QR Code.

Exemple :

`https://portail.exemple.fr/verification`

Code : `AM-7FH4-9K2M`

La personne saisit son code et accède à sa fiche.

**Avantages :**

- fonctionne sans e-mail ;
- facile à expliquer ;
- le même mécanisme de validation est conservé.

**Inconvénient :** coût et gestion des courriers.

### Solution B — QR Code individuel sur le courrier

Le courrier contient un QR Code correspondant au lien personnel.

La personne scanne le QR Code avec son téléphone et accède directement à sa fiche.

Le code texte reste affiché sous le QR Code pour les personnes qui ne souhaitent pas le scanner.

C'est probablement la meilleure solution papier.

### Solution C — Envoi par SMS

Si un numéro de téléphone mobile est disponible, le lien peut être envoyé par SMS.

**Avantages :** rapide et simple pour l'utilisateur.

**Inconvénients :**

- coût d'un prestataire SMS ;
- nécessité de vérifier la qualité des numéros ;
- gestion du consentement et des règles de communication applicables.

### Solution D — Transmission par la structure référente

Le portail peut générer une liste des personnes sans e-mail, avec un courrier ou une fiche individuelle imprimable.

La structure référente peut ensuite :

- remettre le document en main propre ;
- envoyer le courrier ;
- téléphoner à la personne ;
- transmettre le code selon la procédure interne définie.

### Solution E — Mise à jour assistée par téléphone

Pour une personne sans e-mail ou peu à l'aise avec le numérique :

- elle contacte la structure ;
- l'agent ouvre sa fiche ;
- l'agent saisit la demande de modification au nom de la personne ;
- la demande conserve une trace du canal utilisé : `téléphone`.

Il est préférable de conserver le même workflow de validation, même lorsque la demande est saisie par un agent.

### Solution F — Mise à jour lors d'un rendez-vous physique

Même principe, mais avec le canal `accueil physique`.

La fiche peut comporter :

- date de vérification ;
- agent ayant réalisé la vérification ;
- canal : accueil physique.

### Solution G — Accès de secours par informations personnelles

Possible, mais moins recommandé.

Exemple :

- nom ;
- prénom ;
- commune ;
- date de naissance ou autre donnée de contrôle.

Cette approche augmente le risque qu'une tierce personne accède à une fiche.

Elle ne devrait être utilisée qu'en dernier recours et uniquement avec des informations suffisamment discriminantes.

---

## 6. Stratégie recommandée pour les personnes sans e-mail

Prévoir plusieurs canaux selon les informations disponibles :

1. **E-mail présent** → envoi du lien personnel par e-mail.
2. **Pas d'e-mail mais mobile présent** → éventuellement SMS.
3. **Ni e-mail ni SMS exploitable** → courrier avec QR Code + code texte.
4. **Personne en difficulté numérique** → vérification assistée par téléphone ou en accueil.

Dans l'administration, afficher le canal utilisé pour chaque fiche.

Exemple :

| Personne | E-mail | Téléphone | Canal prévu | Statut |
|---|---|---|---|---|
| Mme A | oui | oui | E-mail | Envoyé |
| Mme B | non | oui | SMS | Envoyé |
| Mme C | non | non | Courrier | À imprimer |
| Mme D | oui | oui | E-mail | Vérifié |

---

## 7. Tableau de bord de campagne

La rubrique administration devrait présenter immédiatement :

- nombre total de fiches concernées ;
- nombre d'e-mails envoyés ;
- nombre d'e-mails en erreur ;
- nombre de fiches sans e-mail ;
- nombre de liens ouverts ;
- nombre de fiches confirmées sans modification ;
- nombre de demandes de modification ;
- nombre de demandes en attente ;
- nombre de demandes acceptées ;
- nombre de demandes refusées ;
- nombre de personnes n'ayant pas encore répondu.

Exemple :

```text
Campagne 2027

Fiches concernées                 418
E-mails envoyés                   362
Sans adresse e-mail                56
Liens consultés                   291
Informations confirmées           214
Demandes de modification           77
Demandes en attente                14
Aucune réponse                    127
```

---

## 8. Relances

Ajouter une fonction de relance est fortement recommandé.

Par exemple :

- premier envoi le 1er janvier ;
- première relance le 15 janvier ;
- dernière relance quelques jours avant la fermeture.

Le système ne doit relancer que les personnes qui n'ont pas encore répondu.

Prévoir dans l'administration un bouton :

**Relancer les personnes n'ayant pas répondu**

Il peut afficher un récapitulatif avant envoi.

---

## 9. Confirmation explicite même lorsqu'il n'y a aucun changement

Ne pas considérer qu'une absence de demande signifie que les informations sont correctes.

La personne doit explicitement cliquer sur :

**Je confirme que mes informations sont toujours correctes.**

Enregistrer ensuite :

- date de vérification ;
- campagne ;
- méthode de vérification ;
- statut `confirmé sans modification`.

Cela permet de distinguer :

- une fiche réellement vérifiée ;
- une personne qui n'a simplement jamais répondu.

---

## 10. Historique

Conserver un historique complet est important.

Pour chaque fiche :

- campagne 2025 : vérifiée sans changement ;
- campagne 2026 : téléphone modifié ;
- campagne 2027 : aucune réponse ;
- campagne 2028 : adresse modifiée.

Pour chaque modification :

- ancienne valeur ;
- nouvelle valeur ;
- date de la demande ;
- auteur de la demande ou canal ;
- agent ayant validé ;
- date de validation ;
- décision.

---

## 11. Attribution de la validation

Il est préférable de ne pas dépendre uniquement de la personne qui a créé la fiche.

Une fiche devrait être rattachée à une **structure responsable** ou un **service responsable**.

Exemple :

```text
Assistante maternelle
    ↓
RPE / structure responsable
    ↓
Agents habilités
    ↓
Validation des demandes
```

Cela évite qu'une demande soit bloquée lorsqu'un agent change de poste, est absent ou quitte la structure.

Il reste possible d'enregistrer :

- créateur initial de la fiche ;
- dernier agent ayant modifié la fiche ;
- agent ayant validé la dernière demande.

---

## 12. Sécurité

### Principes essentiels

- ne jamais exposer l'identifiant interne de la fiche comme mécanisme d'authentification ;
- utiliser un jeton cryptographiquement aléatoire ;
- limiter la validité du jeton à la campagne ;
- ne permettre l'accès qu'à une seule fiche ;
- ne jamais permettre une modification directe des données officielles ;
- protéger les formulaires contre les attaques CSRF ;
- limiter le nombre de tentatives sur les pages de saisie de code ;
- journaliser les opérations importantes ;
- utiliser HTTPS ;
- éviter d'inscrire le jeton dans des journaux applicatifs inutilement ;
- ne pas intégrer de données personnelles dans l'URL.

### Lien après validation

Plusieurs choix sont possibles :

#### Option 1 — Le lien reste utilisable jusqu'à la fin de la campagne

La personne peut revenir voir ce qu'elle a envoyé.

#### Option 2 — Le lien devient lecture seule après soumission

Recommandé.

La personne voit :

`Votre demande a été transmise le 12/01/2027 et est en attente de validation.`

#### Option 3 — Le lien est désactivé après soumission

Plus strict, mais moins pratique si la personne souhaite vérifier ce qu'elle a envoyé.

Le meilleur compromis est généralement l'option 2.

---

## 13. Protection contre le transfert accidentel du lien

Un lien personnel agit comme une clé d'accès.

Si la personne transfère son e-mail, le destinataire pourrait théoriquement ouvrir sa fiche.

Plusieurs niveaux sont possibles.

### Niveau simple

Lien personnel seul.

Suffisant pour des données peu sensibles si les risques ont été évalués.

### Niveau intermédiaire

Lien personnel + demande d'une information déjà connue, par exemple les quatre derniers chiffres du téléphone.

### Niveau renforcé

Lien personnel + code envoyé par e-mail ou SMS.

Cela augmente cependant la complexité pour les utilisateurs.

Le niveau doit être choisi en fonction de la nature exacte des informations visibles sur la fiche.

---

## 14. Gestion des e-mails invalides

Prévoir explicitement le traitement des échecs d'envoi.

Dans l'administration :

```text
E-mail envoyé              351
Adresse invalide             7
Message non distribué         4
Pas d'adresse e-mail         56
```

Pour les échecs :

- basculer vers SMS si autorisé et disponible ;
- sinon générer un courrier ;
- signaler la fiche dans une liste `Action nécessaire`.

---

## 15. Export et impression pour le courrier

Prévoir une fonction :

**Générer les courriers pour les personnes sans e-mail**

Le système peut produire un PDF contenant un courrier par personne avec :

- identité ;
- texte explicatif ;
- période de campagne ;
- QR Code ;
- code manuel ;
- coordonnées de la structure à contacter en cas de difficulté.

Cela évite de préparer manuellement les courriers.

---

## 16. États recommandés

Pour chaque participation :

```text
NON_CONTACTÉ
ENVOI_PROGRAMMÉ
ENVOYÉ
ERREUR_ENVOI
CONSULTÉ
CONFIRMÉ_SANS_MODIFICATION
MODIFICATION_SOUMISE
EN_ATTENTE_VALIDATION
VALIDÉ
REFUSÉ
EXPIRÉ
```

Pour une campagne :

```text
BROUILLON
PROGRAMMÉE
EN_COURS
CLÔTURÉE
ARCHIVÉE
```

---

## 17. Modèle de données possible pour Django

Architecture indicative :

### `UpdateCampaign`

- `name`
- `starts_at`
- `ends_at`
- `status`
- `created_by`
- `created_at`
- `message`

### `VerificationInvitation`

- `campaign`
- `person` ou `structure`
- `token_hash`
- `expires_at`
- `delivery_channel`
- `sent_at`
- `opened_at`
- `completed_at`
- `status`

### `UpdateRequest`

- `invitation`
- `submitted_at`
- `status`
- `reviewed_by`
- `reviewed_at`
- `review_comment`

### `UpdateRequestField`

- `request`
- `field_name`
- `old_value`
- `new_value`
- `decision`

Cette séparation permet d'accepter certains champs et d'en refuser d'autres.

---

## 18. Interface administration recommandée

### Page Campagnes

```text
Campagne annuelle 2027
01/01/2027 → 01/02/2027

[Préparer la campagne]
[Lancer les envois]
[Relancer les non-répondants]
[Générer les courriers]
[Clôturer la campagne]
```

### Résumé

```text
418 fiches
362 e-mails disponibles
56 sans e-mail
291 réponses
77 modifications
14 validations en attente
```

### Filtres

- tout ;
- sans réponse ;
- sans e-mail ;
- erreur d'envoi ;
- modification demandée ;
- validation en attente ;
- vérifié sans modification ;
- expiré.

---

## 19. Interface côté assistante maternelle

Éviter une interface trop administrative.

### Écran 1

```text
Vérification de vos informations

Dans le cadre de notre mise à jour annuelle, merci de vérifier les informations ci-dessous.

Cette vérification est disponible jusqu'au 1er février 2027.
```

### Écran 2

Afficher la fiche actuelle.

Puis :

- **Tout est correct**
- **Modifier certaines informations**

### Écran 3 — Modification

Afficher les champs avec leur valeur actuelle et permettre la modification.

### Écran 4 — Vérification finale

Résumé :

```text
Téléphone
06 12 34 56 78
→ 06 98 76 54 32

E-mail
aucune modification
```

Bouton :

**Envoyer ma demande**

### Écran 5

```text
Merci.

Votre demande a bien été transmise.
Les modifications seront appliquées après vérification par notre service.
```

---

## 20. Cas particuliers à prévoir

### Personne ne travaillant plus

Bouton :

**Je n'exerce plus comme assistante maternelle**

Cela crée une demande de changement de statut, pas une suppression immédiate.

### Mauvaise fiche

Bouton :

**Cette fiche ne me concerne pas**

La fiche passe dans une file de vérification interne.

### Décès ou situation particulière signalée par un tiers

Ne pas modifier automatiquement la fiche. Créer une alerte nécessitant une vérification interne.

### Plusieurs fiches pour une même personne

Éviter d'envoyer plusieurs accès sans explication. Le système peut regrouper les fiches dans une invitation lorsque cela correspond au modèle métier.

### Adresse e-mail partagée

Plusieurs invitations peuvent être envoyées à la même adresse, chacune avec son propre lien.

### Modification de l'e-mail pendant la campagne

Une nouvelle adresse proposée ne doit pas automatiquement devenir l'adresse de sécurité du lien courant avant validation.

---

## 21. RGPD et minimisation des données

La page publique obtenue via le lien doit afficher uniquement les informations nécessaires à la vérification.

Éviter d'afficher des données internes telles que :

- commentaires agents ;
- historique administratif ;
- identifiants internes ;
- notes de service ;
- informations non nécessaires à la personne.

Prévoir également un texte précisant :

- pourquoi les données sont demandées ;
- qui les traite ;
- la finalité de la mise à jour ;
- les modalités d'exercice des droits ;
- la durée de conservation pertinente.

Le contenu exact devra être adapté au registre de traitement et à la politique de confidentialité de l'organisme.

---

## 22. Automatisation de la campagne

Une amélioration future pourrait permettre :

1. création de la campagne ;
2. sélection de la population ;
3. aperçu avant lancement ;
4. génération automatique des invitations ;
5. envoi à la date de début ;
6. relances automatiques ;
7. fermeture automatique à la date de fin ;
8. rapport de fin de campagne.

Pour la première version, un déclenchement manuel depuis l'administration est toutefois plus simple et plus sûr.

---

## 23. Rapport de fin de campagne

Lors de la clôture, produire un bilan :

```text
Campagne annuelle 2027

Population totale : 418
Réponses : 332
Taux de réponse : 79,4 %
Confirmations sans changement : 245
Demandes de modification : 87
Modifications validées : 79
Modifications refusées : 5
Encore en attente : 3
Sans réponse : 86
```

Possibilité d'export CSV ou Excel pour les agents.

---

## 24. Version minimale recommandée pour une première mise en production

Pour éviter de développer trop de fonctionnalités immédiatement :

### V1

- création d'une campagne ;
- dates de début et de fin ;
- génération des jetons ;
- envoi par e-mail ;
- liste des personnes sans e-mail ;
- page individuelle de vérification ;
- confirmation « tout est correct » ;
- formulaire de modification ;
- validation administrative ;
- historique ;
- tableau de bord simple ;
- génération d'un courrier avec QR Code pour les personnes sans e-mail.

### V2

- relances automatiques ;
- SMS ;
- validation champ par champ ;
- statistiques avancées ;
- exports ;
- génération en masse des courriers PDF ;
- automatisation complète des dates.

---

## 25. Architecture fonctionnelle finale recommandée

```text
                      ADMINISTRATION
                            │
                            ▼
                 Création d'une campagne
                  01/01/2027 → 01/02/2027
                            │
                            ▼
                Sélection des fiches actives
                            │
                            ▼
                 Génération des invitations
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
           E-mail          SMS          Courrier
          + lien          + lien        + QR/code
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                  Consultation de la fiche
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
          Tout est correct       Modification
                 │                     │
                 ▼                     ▼
             Confirmation        Demande enregistrée
                                       │
                                       ▼
                              Validation interne
                                       │
                              ┌────────┴────────┐
                              ▼                 ▼
                           Acceptée          Refusée
                              │
                              ▼
                        Fiche officielle
```

---

## 26. Recommandation générale

La meilleure approche est une **campagne annuelle contrôlée**, fondée sur des liens individuels temporaires plutôt qu'une ouverture publique de l'annuaire.

Le système recommandé est :

**Campagne → invitation individuelle → consultation de la fiche → confirmation ou proposition → validation humaine → historique.**

Pour les personnes ne disposant pas d'adresse e-mail, le meilleur mécanisme de secours est :

**courrier individuel avec QR Code + code texte**, complété si nécessaire par une procédure de mise à jour assistée par téléphone ou en accueil.

Ce modèle conserve une expérience très simple pour les assistantes maternelles tout en évitant la création de centaines de comptes et en maintenant le contrôle des données par les agents habilités.
