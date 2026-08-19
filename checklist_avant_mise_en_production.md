# 🚀 CHECKLIST AVANT MISE EN PRODUCTION

> À effectuer sur la **préproduction/staging**, puis vérifier les points concernés une dernière fois en production.

## 🔐 1. Secrets & configuration

- [ ] Aucun secret présent dans le dépôt Git
- [ ] Aucun secret présent dans le frontend
- [ ] `.env` exclu de Git
- [ ] Variables d'environnement de production configurées
- [ ] Clés API de production correctement configurées
- [ ] Clés API limitées aux permissions nécessaires
- [ ] Mots de passe de développement supprimés
- [ ] Comptes de test supprimés ou désactivés
- [ ] Données de test supprimées
- [ ] Configuration DEV impossible à utiliser accidentellement
- [ ] `DEBUG` désactivé
- [ ] Stack traces masquées
- [ ] Logs DEBUG désactivés
- [ ] Aucun `console.log` sensible
- [ ] Aucun endpoint/debug toolbar de développement accessible
- [ ] Configuration production vérifiée manuellement

## 🌐 2. Domaine, DNS & HTTPS

- [ ] Domaine définitif configuré
- [ ] DNS correctement configurés
- [ ] HTTPS fonctionnel
- [ ] Certificat TLS valide
- [ ] Renouvellement automatique du certificat configuré
- [ ] HTTP redirigé vers HTTPS
- [ ] `www` / sans `www` géré correctement
- [ ] Domaine canonique défini
- [ ] Aucun mixed content HTTP/HTTPS
- [ ] HSTS configuré si approprié
- [ ] Sous-domaines nécessaires vérifiés
- [ ] Anciennes URLs correctement redirigées si nécessaire

## 🛡️ 3. Sécurité HTTP

- [ ] `Content-Security-Policy` vérifiée
- [ ] Protection contre le clickjacking
- [ ] `X-Content-Type-Options` configuré
- [ ] `Referrer-Policy` configurée
- [ ] `Permissions-Policy` configurée
- [ ] Cookies `Secure`
- [ ] Cookies `HttpOnly`
- [ ] `SameSite` correctement configuré
- [ ] CORS limité aux domaines nécessaires
- [ ] CSRF actif
- [ ] Aucune information inutile sur le serveur exposée

## 🔑 4. Connexion & comptes

Tester réellement :

- [ ] Création de compte
- [ ] Connexion
- [ ] Déconnexion
- [ ] Mauvais mot de passe
- [ ] Adresse e-mail inexistante
- [ ] Compte désactivé
- [ ] Vérification d'adresse e-mail
- [ ] Mot de passe oublié
- [ ] Réinitialisation du mot de passe
- [ ] Changement du mot de passe
- [ ] Changement d'adresse e-mail
- [ ] Suppression du compte
- [ ] Expiration des sessions
- [ ] Anciennes sessions correctement invalidées
- [ ] Rate limiting sur la connexion
- [ ] Rate limiting sur la récupération du mot de passe
- [ ] Protection contre le brute-force
- [ ] Protection contre l'énumération des comptes
- [ ] 2FA/MFA testé si disponible

## 👮 5. Permissions

Tester avec **chaque rôle existant** :

- [ ] Visiteur
- [ ] Utilisateur
- [ ] Modérateur si présent
- [ ] Administrateur
- [ ] Autres rôles métier

Vérifier :

- [ ] Pages privées réellement inaccessibles
- [ ] Routes privées protégées côté serveur
- [ ] APIs privées protégées
- [ ] Un utilisateur ne peut pas consulter les données d'un autre
- [ ] Un utilisateur ne peut pas modifier les données d'un autre
- [ ] Un utilisateur ne peut pas supprimer les données d'un autre
- [ ] Modification manuelle d'un ID dans une URL testée
- [ ] Modification d'un ID dans une requête API testée
- [ ] Escalade de privilèges impossible
- [ ] Administration inaccessible sans autorisation
- [ ] Actions sensibles contrôlées côté serveur

## 🧨 6. Tests de sécurité

- [ ] Injection SQL testée
- [ ] XSS testée
- [ ] CSRF testée
- [ ] IDOR/BOLA testé
- [ ] Path traversal testé si pertinent
- [ ] Open redirect testé
- [ ] SSRF testé si pertinent
- [ ] Injection de commandes testée si pertinent
- [ ] Manipulation des paramètres testée
- [ ] Requêtes volontairement invalides testées
- [ ] Payloads très volumineux testés
- [ ] Endpoints sensibles recensés
- [ ] Routes inutilisées supprimées
- [ ] Scan de sécurité effectué
- [ ] Vulnérabilités critiques corrigées
- [ ] Vulnérabilités importantes analysées

## 📁 7. Upload de fichiers

Si le site permet les uploads :

- [ ] Taille maximale testée
- [ ] Extensions autorisées vérifiées
- [ ] Type MIME contrôlé
- [ ] Fichier avec fausse extension testé
- [ ] Fichier exécutable refusé
- [ ] Nom de fichier dangereux testé
- [ ] Path traversal testé
- [ ] Fichier trop volumineux refusé proprement
- [ ] Fichiers privés réellement privés
- [ ] Téléchargement soumis aux permissions
- [ ] Suppression des fichiers fonctionnelle
- [ ] Stockage disponible suffisant

## 🗄️ 8. Base de données

- [ ] Base de production créée
- [ ] Identifiants différents de DEV
- [ ] Base non exposée publiquement
- [ ] Permissions DB minimales
- [ ] Toutes les migrations appliquées
- [ ] Aucune migration manquante
- [ ] Contraintes DB vérifiées
- [ ] Index importants présents
- [ ] Données de test absentes
- [ ] Comptes administrateurs contrôlés
- [ ] Encodage UTF-8 correct
- [ ] Accents testés
- [ ] Emojis testés si acceptés
- [ ] Fuseau horaire vérifié
- [ ] Dates/heures vérifiées

## 💾 9. Sauvegardes

**Point bloquant pour une mise en production.**

- [ ] Sauvegarde automatique activée
- [ ] Base de données sauvegardée
- [ ] Fichiers utilisateurs sauvegardés
- [ ] Sauvegarde quotidienne vérifiée
- [ ] Plusieurs générations conservées
- [ ] Sauvegarde externe au serveur principal
- [ ] Sauvegardes protégées
- [ ] Sauvegardes chiffrées si nécessaire
- [ ] Échec de sauvegarde déclenche une alerte

### Test indispensable

- [ ] Une sauvegarde a réellement été restaurée
- [ ] Base restaurée correctement
- [ ] Fichiers restaurés correctement
- [ ] Application fonctionnelle après restauration
- [ ] Temps approximatif de restauration connu
- [ ] Procédure documentée

## 🇪🇺 10. RGPD

- [ ] Données personnelles collectées inventoriées
- [ ] Chaque donnée collectée est réellement nécessaire
- [ ] Base légale définie
- [ ] Mentions d'information présentes
- [ ] Politique de confidentialité disponible
- [ ] Mentions légales disponibles
- [ ] Durées de conservation définies
- [ ] Suppression des données prévue
- [ ] Export des données possible lorsque nécessaire
- [ ] Rectification possible
- [ ] Suppression de compte fonctionnelle
- [ ] Demande d'effacement testée
- [ ] Consentements enregistrés lorsque nécessaires
- [ ] Consentements révocables
- [ ] Sous-traitants identifiés
- [ ] Services externes vérifiés
- [ ] Données transmises hors UE identifiées
- [ ] Logs vérifiés pour éviter les données personnelles inutiles
- [ ] Procédure de violation de données définie

## 🍪 11. Cookies & traceurs

- [ ] Inventaire des cookies effectué
- [ ] Cookies nécessaires identifiés
- [ ] Cookies facultatifs identifiés
- [ ] Aucun cookie facultatif avant consentement
- [ ] Bouton « Accepter » fonctionnel
- [ ] Bouton « Refuser » fonctionnel
- [ ] Refuser aussi facilement qu'accepter
- [ ] Choix personnalisé fonctionnel
- [ ] Retrait du consentement possible
- [ ] Choix conservé correctement
- [ ] Analytics vérifié
- [ ] Pixels publicitaires vérifiés
- [ ] Contenus externes vérifiés
- [ ] Réseaux sociaux vérifiés
- [ ] Cookies réellement supprimés/bloqués après refus lorsque nécessaire

## ♿ 12. Accessibilité RGAA / WCAG

Tester réellement :

- [ ] Site entièrement navigable au clavier
- [ ] Ordre du focus cohérent
- [ ] Focus visible
- [ ] Aucun piège clavier
- [ ] Contrastes vérifiés
- [ ] Zoom 200 % testé
- [ ] Affichage mobile testé
- [ ] Lecteur d'écran testé
- [ ] Formulaires accessibles
- [ ] Labels présents
- [ ] Messages d'erreur accessibles
- [ ] Images avec alternatives appropriées
- [ ] Images décoratives ignorées
- [ ] Titres correctement hiérarchisés
- [ ] HTML sémantique
- [ ] Liens compréhensibles hors contexte lorsque requis
- [ ] Modales accessibles
- [ ] Menus accessibles
- [ ] Composants dynamiques accessibles
- [ ] ARIA correctement utilisée
- [ ] Animations désactivables lorsque nécessaire
- [ ] Documents PDF accessibles lorsque nécessaire
- [ ] Audit automatique effectué
- [ ] Contrôle manuel effectué
- [ ] Déclaration d'accessibilité préparée lorsque applicable

## 📱 13. Responsive & navigateurs

Tester au minimum :

- [ ] Petit smartphone
- [ ] Grand smartphone
- [ ] Tablette
- [ ] Ordinateur portable
- [ ] Grand écran

Navigateurs :

- [ ] Chrome
- [ ] Firefox
- [ ] Edge
- [ ] Safari lorsque pertinent

Vérifier :

- [ ] Aucun débordement horizontal
- [ ] Menus fonctionnels
- [ ] Modales fonctionnelles
- [ ] Formulaires utilisables
- [ ] Boutons suffisamment grands sur mobile
- [ ] Clavier mobile ne bloque pas les formulaires
- [ ] Orientation portrait
- [ ] Orientation paysage

## 🧪 14. Tests fonctionnels

Effectuer **un parcours complet comme un vrai utilisateur** :

- [ ] Arrivée sur le site
- [ ] Navigation
- [ ] Recherche
- [ ] Inscription
- [ ] Confirmation e-mail
- [ ] Connexion
- [ ] Fonctionnalités principales
- [ ] Modification du profil
- [ ] Déconnexion

Puis tester :

- [ ] Champs vides
- [ ] Valeurs incorrectes
- [ ] Valeurs extrêmement longues
- [ ] Caractères spéciaux
- [ ] Accents
- [ ] Emojis si acceptés
- [ ] Double clic
- [ ] Double envoi de formulaire
- [ ] Retour navigateur
- [ ] Rafraîchissement de page
- [ ] Session expirée
- [ ] Connexion lente
- [ ] Perte de connexion pendant une action

## ✉️ 15. E-mails

- [ ] Confirmation d'inscription reçue
- [ ] Mot de passe oublié reçu
- [ ] Notifications reçues
- [ ] Expéditeur correct
- [ ] Domaine d'envoi correct
- [ ] SPF valide
- [ ] DKIM valide
- [ ] DMARC configuré
- [ ] Liens fonctionnels
- [ ] Liens utilisant le domaine de production
- [ ] Aucun lien vers localhost/staging
- [ ] Affichage mobile correct
- [ ] Test Gmail
- [ ] Test Outlook
- [ ] Dossier spam vérifié
- [ ] Aucun secret/donnée inutile dans les e-mails

## ⚡ 16. Performances

- [ ] Page d'accueil testée
- [ ] Pages principales testées
- [ ] Pages lourdes identifiées
- [ ] Core Web Vitals contrôlés
- [ ] Images optimisées
- [ ] Images correctement dimensionnées
- [ ] Cache configuré
- [ ] Compression activée
- [ ] Requêtes DB excessives recherchées
- [ ] N+1 recherchés
- [ ] Pages avec beaucoup de données paginées
- [ ] APIs testées
- [ ] Temps de réponse acceptable
- [ ] Test avec connexion mobile/lente
- [ ] Test de charge réalisé si audience importante prévue

## 🔍 17. SEO

Pour les pages publiques :

- [ ] `<title>` présent
- [ ] Meta description
- [ ] H1 correct
- [ ] Structure H1/H2/H3 cohérente
- [ ] URLs propres
- [ ] Canonical correcte
- [ ] `robots.txt`
- [ ] Sitemap XML
- [ ] Sitemap accessible
- [ ] Pages privées exclues de l'indexation
- [ ] Staging interdit aux moteurs de recherche
- [ ] Production autorisée à l'indexation lorsque souhaité
- [ ] Open Graph configuré
- [ ] Image de partage correcte
- [ ] Favicon présent
- [ ] Page 404 correcte

## 📊 18. Logs & monitoring

- [ ] Monitoring disponible
- [ ] Site surveillé 24/7
- [ ] Erreurs HTTP surveillées
- [ ] Exceptions applicatives surveillées
- [ ] CPU surveillé
- [ ] RAM surveillée
- [ ] Disque surveillé
- [ ] Base de données surveillée
- [ ] Temps de réponse surveillé
- [ ] Certificat HTTPS surveillé
- [ ] Sauvegardes surveillées
- [ ] E-mails critiques surveillés si nécessaire
- [ ] Alertes configurées
- [ ] Test d'une alerte réellement effectué
- [ ] Logs accessibles en cas d'incident
- [ ] Rotation des logs configurée
- [ ] Disque protégé contre le remplissage par les logs

## 📦 19. Dépendances

- [ ] Dépendances scannées
- [ ] Vulnérabilités connues contrôlées
- [ ] Aucune vulnérabilité critique non traitée
- [ ] Dépendances obsolètes identifiées
- [ ] Dépendances abandonnées identifiées
- [ ] Versions de production verrouillées
- [ ] Packages DEV absents de production lorsque pertinent
- [ ] Licences problématiques vérifiées

## 🖥️ 20. Serveur

- [ ] OS à jour
- [ ] Correctifs de sécurité installés
- [ ] Services inutiles désactivés
- [ ] Ports inutiles fermés
- [ ] Pare-feu configuré
- [ ] SSH sécurisé
- [ ] Connexion SSH par clé privilégiée
- [ ] Connexion root distante désactivée lorsque possible
- [ ] Protection brute-force SSH
- [ ] Utilisateurs système contrôlés
- [ ] Permissions fichiers contrôlées
- [ ] Répertoires sensibles inaccessibles depuis le Web
- [ ] `.env` inaccessible depuis le Web
- [ ] `.git` inaccessible depuis le Web
- [ ] Fichiers de sauvegarde inaccessibles depuis le Web
- [ ] Espace disque suffisant
- [ ] Heure/NTP correctement configuré
- [ ] Redémarrage automatique des services critiques prévu
- [ ] Redémarrage complet du serveur testé

## 🔥 21. Pare-feu & exposition réseau

- [ ] Inventaire des ports ouverts
- [ ] Seuls les ports nécessaires sont exposés
- [ ] Base de données non exposée publiquement
- [ ] Redis/cache non exposé publiquement
- [ ] Interfaces d'administration protégées
- [ ] Interfaces Docker/containers non exposées
- [ ] Services internes accessibles uniquement depuis le réseau nécessaire
- [ ] Rate limiting au niveau proxy lorsque pertinent

## 🚨 22. Gestion des pannes

Simuler autant que possible :

- [ ] Application arrêtée
- [ ] Base indisponible
- [ ] Service externe indisponible
- [ ] API externe en timeout
- [ ] E-mail indisponible
- [ ] Stockage indisponible
- [ ] Disque presque plein
- [ ] Erreur 500
- [ ] Redémarrage serveur

Vérifier :

- [ ] Pas de perte de données évitable
- [ ] Message utilisateur propre
- [ ] Erreur journalisée
- [ ] Administrateur alerté lorsque nécessaire
- [ ] Application récupère correctement après rétablissement

## ↩️ 23. Rollback

Avant le lancement :

- [ ] Version actuellement déployée identifiable
- [ ] Version précédente disponible
- [ ] Procédure de rollback documentée
- [ ] Rollback applicatif possible
- [ ] Impact des migrations DB connu
- [ ] Sauvegarde disponible avant migration destructive
- [ ] Personne responsable du rollback identifiée
- [ ] Procédure déjà testée

## 📚 24. Documentation d'exploitation

- [ ] Procédure de déploiement
- [ ] Procédure de mise à jour
- [ ] Procédure de sauvegarde
- [ ] Procédure de restauration
- [ ] Procédure de rollback
- [ ] Procédure de renouvellement des secrets
- [ ] Procédure en cas de panne
- [ ] Procédure en cas de compromission
- [ ] Architecture du serveur documentée
- [ ] Services utilisés documentés
- [ ] Fournisseurs externes documentés
- [ ] Variables d'environnement documentées sans leurs valeurs secrètes

## ⚖️ 25. Pages légales

Selon le projet :

- [ ] Mentions légales
- [ ] Politique de confidentialité
- [ ] Gestion des cookies
- [ ] CGU
- [ ] CGV si nécessaire
- [ ] Informations éditeur
- [ ] Informations hébergeur
- [ ] Contact
- [ ] Médiateur de la consommation si applicable
- [ ] Informations relatives aux données personnelles
- [ ] Déclaration d'accessibilité si applicable

## 🔴 26. BLOQUANTS ABSOLUS

**🚫 NE PAS METTRE EN PRODUCTION si :**

- [ ] `DEBUG` est encore actif
- [ ] Un secret est présent dans Git
- [ ] Une vulnérabilité critique connue n'est pas traitée
- [ ] Une faille d'authentification est connue
- [ ] Une faille de permissions est connue
- [ ] HTTPS n'est pas opérationnel
- [ ] Des données personnelles sont publiquement accessibles
- [ ] La base de données est inutilement exposée à Internet
- [ ] Des migrations nécessaires sont absentes
- [ ] Les sauvegardes ne fonctionnent pas
- [ ] Aucune restauration n'a été testée
- [ ] Un parcours métier critique est cassé
- [ ] Les obligations RGPD essentielles ne sont pas satisfaites
- [ ] Un problème d'accessibilité bloquant connu empêche l'accès à une fonctionnalité essentielle

## 🟠 27. À CORRIGER RAPIDEMENT

Peuvent éventuellement ne pas bloquer le lancement selon leur gravité :

- [ ] Petites anomalies responsive
- [ ] Problèmes SEO secondaires
- [ ] Optimisations d'images
- [ ] Performance d'une page secondaire
- [ ] Dette technique mineure
- [ ] Documentation interne secondaire
- [ ] Warning non critique d'une dépendance
- [ ] Petites améliorations UX

Tout élément accepté doit être ajouté au suivi des tâches avec une priorité et une justification.

## 🟢 28. GO / NO-GO FINAL

### Sécurité
- [ ] **GO**

### Fonctionnel
- [ ] **GO**

### Base de données
- [ ] **GO**

### Sauvegarde/restauration
- [ ] **GO**

### RGPD
- [ ] **GO**

### RGAA/WCAG
- [ ] **GO**

### Serveur/infrastructure
- [ ] **GO**

### Performances
- [ ] **GO**

### Monitoring
- [ ] **GO**

### Documentation
- [ ] **GO**

## 🚀 DÉCISION

- [ ] **GO — Mise en production autorisée**
- [ ] **NO-GO — Mise en production bloquée**

**Version :**

**Date :**

**Responsable du contrôle :**

**Problèmes non bloquants acceptés :**

**Rollback prévu vers :**

**Sauvegarde pré-déploiement vérifiée :**
