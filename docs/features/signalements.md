# Signalements (bug tracker intégré)

Un bouton fixe en bas à droite du site (pages publiques comme tableau de bord)
permet aux **utilisateurs connectés** d'ouvrir une modale et d'envoyer un
signalement : bug, suggestion ou autre remarque.

## Parcours

1. L'utilisateur clique l'icône « Signaler un bug ou une remarque ».
2. La modale (`<dialog>` natif) s'ouvre avec le focus sur le message.
3. Le champ **« Page concernée » (facultatif) est pré-rempli** avec la page courante
   (`window.location.pathname`), mais reste **modifiable librement**
   (saisie + suggestions des grandes sections).
4. Envoi en `fetch` JSON avec CSRF ; sans JavaScript, le formulaire POST
   classique vers `/feedback/signaler/` fonctionne aussi (repli + page
   `feedback/form.html` en cas d'erreur).
5. Message de succès, fermeture de la modale, retour du focus au bouton.

## Données

Modèle `feedback.FeedbackReport` :

- `user` (compte auteur, `SET_NULL` pour garder l'historique) ;
- `type` : bug / suggestion / autre ;
- `message` : 10 à 2000 caractères, texte brut ;
- `page_declaree` : page indiquée par l'utilisateur (modifiable, facultative) ;
- `page_auto` : page déduite côté serveur (en-tête `Referer` même hôte,
  repli sur le contexte envoyé par le JS) — jamais acceptée aveuglément ;
- `url_name`, `user_agent` (tronqué à 500) ;
- `statut` : nouveau → en cours → résolu ;
- `traite_par`, `commentaire_interne`, `created_at`, `updated_at`.

## Notifications

À chaque signalement, un email texte est envoyé aux adresses actives de
`DestinataireNotification` (même table que les inscriptions, To/CCI
respectés), avec repli sur les superadmins si aucune adresse active.
Un échec SMTP est journalisé mais **ne fait jamais perdre le signalement**.

## Administration

- Admin Django (`Signalements`) : liste par date, filtres statut/type,
  recherche message/pages/email, actions « Marquer en cours / résolu ».
- Limitation de débit : 10 envois / heure / utilisateur (`django_ratelimit`,
  clé `user`, `block=True`).
- Accès `POST` réservé aux connectés (`LoginRequiredMixin`) ; les anonymes
  sont redirigés vers la connexion.

## Accessibilité

- `<dialog>` natif : ESC, clic backdrop, retour focus, `aria-labelledby` /
  `aria-describedby`, zone de statut `aria-live="polite"`.
- Cible tactile 52 px, tokens de contraste existants, bouton masqué à
  l'impression (`print.css`).
- Test manuel recommandé : clavier seul, zoom 200 %, lecteur d'écran,
  envoi sans JavaScript.

## Données personnelles

Données minimales : compte auteur, message libre, URL visitée, navigateur.
Ne pas y saisir de mot de passe. Conservation recommandée : 24 mois, puis
suppression via l'admin (à valider avec le responsable de traitement).
