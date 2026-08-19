# Notifications et emails

## Demande d'inscription

Quand un visiteur remplit le formulaire d'inscription (`/inscription/`), un email de notification est envoyé aux adresses configurées dans le tableau de bord, page **Notifications** (réservée aux superadmins).

### Configuration

- chaque adresse peut être **active** (« Recevoir les notifications ») ou non ;
- chaque adresse active peut être placée **en copie cachée (CCI)** ; les autres reçoivent l'email en destinataire principal ;
- si aucune adresse n'est active, les superadmins ayant une adresse email sont prévenus automatiquement (filet de sécurité).

La page affiche une synthèse du nombre d'adresses actives, principales et en CCI. Les préférences sont enregistrées en une fois pour toutes les adresses configurées, et le retrait d'une adresse demande une confirmation explicite.

Le modèle `DestinataireNotification` est également administrable dans l'admin Django.

## Décision d'inscription

- validation : email au collaborateur avec confirmation d'accès ;
- refus : email d'information au collaborateur.

## Mot de passe oublié

Le formulaire `/mot-de-passe-oublie/` envoie un email contenant un lien de réinitialisation valable **3 heures**. Les templates sont `templates/registration/password_reset_email.html` et `password_reset_subject.txt`. L'envoi est limité en débit (10 demandes par heure et par adresse IP).

## Réglage SMTP

Les paramètres SMTP sont fournis par variables d'environnement (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`, `SITE_URL`), voir `.env.example`. En développement, l'email backend console affiche les messages dans les logs.
