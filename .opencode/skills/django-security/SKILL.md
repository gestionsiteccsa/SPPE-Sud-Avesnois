---
name: django-security
description: Audite, conçoit et renforce la sécurité d’un projet Django. À utiliser pour toute feature exposant des données, authentification, permissions, formulaires, API, uploads, URLs distantes, sessions, cookies, secrets, logs ou configuration de production. Vérifie systématiquement les risques pertinents, privilégie les protections natives Django, applique une approche secure-by-default et bloque les opérations Git de sortie lorsqu’un risque critique connu subsiste.
compatibility: opencode
metadata:
  framework: django
  purpose: security
  language: fr
  workflow-parent: project-workflow
---

# Django Security

## 1. Mission

Tu es responsable de la sécurité applicative du projet Django.

Ta mission est de réduire les risques sans rendre le projet inutilisable ou inutilement complexe.

Principes :

- secure by default ;
- moindre privilège ;
- deny by default lorsque pertinent ;
- validation côté serveur ;
- secrets hors code ;
- permissions explicites ;
- protections Django natives conservées ;
- dépendances minimales ;
- erreurs non bavardes en production ;
- sécurité vérifiée à chaque feature selon son contexte.

La sécurité n’est pas une étape finale.

Elle fait partie de la conception.

---

## 2. Coordination

Avant une analyse importante :

1. lis `AGENTS.md` ;
2. charge `project-workflow` ;
3. inspecte la feature et son flux ;
4. lis les décisions d’architecture concernées ;
5. charge si disponibles :
   - `django-architecture`
   - `django-database`
   - `django-auth`
   - `django-api`
   - `django-testing`
   - `dependency-management`
   - `deployment`

Ne duplique pas un contrôle déjà fourni de manière plus spécialisée, mais vérifie que les responsabilités sont couvertes.

---

## 3. Modèle de menace léger

Pour toute feature non triviale, demande silencieusement :

- qui peut appeler cette feature ?
- quelles données reçoit-elle ?
- quelles données expose-t-elle ?
- quelles actions peut-elle déclencher ?
- peut-elle agir sur un objet appartenant à quelqu’un d’autre ?
- peut-elle lire un fichier ?
- peut-elle écrire un fichier ?
- peut-elle appeler une URL externe ?
- peut-elle exécuter une commande ?
- peut-elle modifier des privilèges ?
- que se passe-t-il si l’utilisateur ment sur toutes les entrées ?

Ne transforme pas cette analyse en questionnaire utilisateur sauf si une décision métier manque.

---

## 4. Questions utilisateur

Pose au maximum 2 questions à la fois.

Pose uniquement des questions métier ou de risque réellement structurantes.

Exemple :

> Un membre peut-il modifier uniquement ses propres objets, ou ceux de son organisation également ?  
> **Pourquoi :** cela détermine la règle d’autorisation. Vérifier seulement que l’utilisateur est connecté ne suffit pas.

Ne demande pas :

> Faut-il protéger contre SQL injection ?

La réponse est toujours oui.

---

## 5. Authentification vs autorisation

Ne confonds jamais :

- **authentification** : qui est l’utilisateur ;
- **autorisation** : ce qu’il a le droit de faire.

`login_required` ne suffit pas à protéger un objet.

Pour toute action sur une ressource :

1. vérifier l’identité ;
2. vérifier le droit d’action ;
3. vérifier l’accès à l’objet précis ;
4. filtrer les QuerySets si nécessaire ;
5. tester le refus.

---

## 6. Contrôle d’accès objet par objet

Préviens les failles IDOR/BOLA.

Danger :

```text
/object/123/edit/
```

Un utilisateur ne doit jamais obtenir l’accès uniquement parce qu’il connaît un identifiant.

Préférer une sélection déjà limitée :

```python
get_object_or_404(
    queryset_visible_par(request.user),
    pk=pk,
)
```

ou une vérification explicite de permission.

Teste au minimum :

- propriétaire autorisé ;
- autre utilisateur refusé ;
- administrateur/rôle autorisé si prévu.

---

## 7. Moindre privilège

Chaque acteur ne reçoit que les permissions nécessaires.

Évite :

- tout utilisateur `staff` pour simplifier ;
- permissions globales lorsque l’accès doit être scoped ;
- clés API excessivement puissantes ;
- comptes DB superuser pour l’application.

Les comptes de service doivent avoir des droits limités.

---

## 8. Superuser et staff

Ne confonds pas :

- utilisateur authentifié ;
- staff ;
- superuser ;
- rôle métier.

N’utilise pas `is_staff` comme système complet de rôles métier sauf cas réellement simple.

Les privilèges d’administration doivent être rares.

---

## 9. Méthodes HTTP

Les requêtes sûres (`GET`, `HEAD`, etc.) ne doivent pas modifier l’état.

Toute action ayant un effet doit utiliser une méthode appropriée.

Ne crée pas :

```text
GET /delete/123/
```

Utilise POST/DELETE selon l’interface et protège correctement la requête.

La protection CSRF repose aussi sur cette séparation. Django recommande que GET et les méthodes sûres restent sans effet de bord. 

---

## 10. CSRF

Conserve `CsrfViewMiddleware` sauf architecture explicitement compatible avec une autre stratégie sûre.

Pour les formulaires Django :

- utilise `{% csrf_token %}` ;
- ne désactive pas CSRF pour résoudre une erreur ;
- configure `CSRF_TRUSTED_ORIGINS` uniquement avec les origines réellement nécessaires.

Pour AJAX :

- utilise la méthode recommandée par Django ;
- ne rends pas le cookie/token publiquement plus accessible sans raison.

Toute exemption `csrf_exempt` doit être :

- rare ;
- justifiée ;
- documentée ;
- revue.

---

## 11. XSS

Les templates Django auto-échappent normalement les variables.

Ne contourne pas cette protection sans raison.

Points sensibles :

- `safe` ;
- `mark_safe()` ;
- HTML utilisateur ;
- rich text ;
- JavaScript inline ;
- insertion dans des attributs/URLs ;
- contenu généré par un éditeur WYSIWYG.

Toute donnée HTML fournie par un utilisateur doit être :

- refusée ;
- ou nettoyée avec une stratégie explicitement conçue.

Ne crée pas un sanitizer maison.

---

## 12. SQL injection

Privilégie l’ORM Django.

Pour SQL brut :

- paramètres séparés ;
- jamais de concaténation avec entrée utilisateur ;
- jamais d’interpolation de noms SQL depuis une saisie non validée ;
- tests ;
- justification.

Exemple dangereux conceptuel :

```python
cursor.execute("SELECT ... WHERE name = '" + user_value + "'")
```

N’écris jamais ce type de requête.

---

## 13. Command injection

Évite les commandes shell lorsque Python ou une bibliothèque permet la même opération.

Si un processus externe est indispensable :

- ne passe pas par `shell=True` sauf nécessité démontrée ;
- arguments séparés ;
- allowlist ;
- aucune concaténation d’entrée utilisateur ;
- permissions système minimales ;
- timeout ;
- gestion d’erreur.

---

## 14. Path traversal

Toute opération sur un chemin provenant d’une saisie externe est sensible.

Ne concatène pas naïvement :

```text
uploads/ + user_filename
```

Empêche :

- `../`
- chemins absolus ;
- séparateurs inattendus ;
- symlinks abusifs selon contexte.

Utilise l’API de stockage Django lorsque possible.

---

## 15. Uploads

Tout fichier utilisateur est non fiable.

Analyse :

- taille ;
- extension ;
- type MIME ;
- contenu réel si pertinent ;
- nom ;
- destination ;
- permission ;
- stockage ;
- exposition web ;
- antivirus/scanner si niveau de risque suffisant.

Ne fais jamais confiance au seul `Content-Type` envoyé par le client.

---

## 16. Types de fichiers

Si la feature n’a besoin que d’images, n’accepte pas arbitrairement tout type.

Utilise une allowlist.

Exemple :

- jpeg ;
- png ;
- webp.

Pour documents :

- liste de formats explicitement autorisés.

Évite les exécutables et formats actifs lorsque non nécessaires.

---

## 17. Taille des fichiers

Définis des limites :

- taille par fichier ;
- nombre ;
- éventuellement quota utilisateur.

Protège :

- mémoire ;
- disque ;
- temps CPU ;
- bande passante.

Une limite frontend n’est pas une limite de sécurité.

Applique le contrôle côté serveur et éventuellement au reverse proxy.

---

## 18. Noms de fichiers

Ne conserve pas aveuglément un nom utilisateur comme nom physique final.

Utilise :

- nom généré ;
- UUID ;
- stratégie sûre du storage.

Le nom original peut être conservé comme métadonnée si nécessaire.

---

## 19. Stockage des uploads

Idéalement, les uploads ne doivent pas être exécutables par le serveur web.

Sépare :

- code applicatif ;
- static ;
- media utilisateur.

Selon le risque, héberge les fichiers utilisateurs :

- sur un domaine séparé ;
- dans un stockage objet ;
- avec headers adaptés.

La configuration exacte dépend du déploiement.

---

## 20. Téléchargements

Pour une ressource privée :

- vérifie l’autorisation avant de servir le fichier ;
- ne donne pas simplement une URL publique prédictible.

Utilise selon infrastructure :

- réponse applicative ;
- URL temporaire signée ;
- mécanisme interne du reverse proxy.

Ne laisse pas Django streamer de très gros fichiers si une infrastructure dédiée est disponible.

---

## 21. SSRF

Toute feature qui récupère une URL fournie ou influencée par l’utilisateur est à haut risque.

Exemples :

- importer une image par URL ;
- webhook test ;
- aperçu de lien ;
- scanner de site ;
- PDF depuis URL.

Risques :

- localhost ;
- réseau interne ;
- metadata cloud ;
- services administratifs ;
- redirections.

---

## 22. Protection SSRF

Lorsque possible :

- allowlist de domaines ;
- protocoles autorisés (`https`) ;
- résolution DNS contrôlée ;
- refus IP privées/loopback/link-local ;
- refus des schémas non HTTP(S) ;
- timeout ;
- limite taille ;
- redirections contrôlées ;
- client HTTP sans accès implicite à des credentials.

Ne crée pas un « fetch URL universel ».

---

## 23. Open redirects

Pour tout paramètre `next`, `redirect`, `return_to` :

- valide qu’il pointe vers une destination sûre ;
- utilise les helpers Django adaptés ;
- n’effectue pas une redirection vers une URL utilisateur arbitraire.

---

## 24. Host header

Ne construis pas des URLs ou décisions de sécurité en lisant directement un Host non validé.

Configure `ALLOWED_HOSTS`.

Utilise les APIs Django adaptées.

N’utilise pas `ALLOWED_HOSTS = ["*"]` en production par défaut.

---

## 25. CORS

CORS n’est pas un mécanisme d’authentification.

N’autorise pas toutes les origines par confort.

Si CORS est nécessaire :

- origines explicites ;
- méthodes nécessaires ;
- headers nécessaires ;
- credentials seulement si nécessaires.

Charge `django-api` pour une API.

---

## 26. Cookies

En production HTTPS, évalue et configure :

- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`
- `SESSION_COOKIE_HTTPONLY`
- `SESSION_COOKIE_SAMESITE`
- équivalents appropriés.

Ne désactive pas HttpOnly pour rendre une session accessible au JavaScript.

Le paramétrage SameSite dépend du besoin réel d’intégration cross-site.

---

## 27. Sessions

Utilise le système de session Django correctement.

Analyse :

- durée ;
- expiration ;
- logout ;
- rotation ;
- stockage ;
- sensibilité du poste partagé.

Pour action très sensible, une réauthentification peut être nécessaire.

Ne stocke pas de données secrètes inutiles dans la session.

---

## 28. Mots de passe

Utilise exclusivement le framework d’authentification et de hashage Django.

Jamais :

- mot de passe en clair ;
- chiffrement réversible ;
- MD5/SHA maison ;
- log du mot de passe.

Applique les validateurs de mot de passe adaptés au projet.

Ne force pas des règles arbitraires incompatibles avec les recommandations actuelles sans besoin.

---

## 29. Login brute force

Django ne fournit pas nécessairement une protection complète contre toutes les tentatives abusives pour chaque architecture.

Analyse les besoins de :

- rate limiting ;
- lockout progressif ;
- délai ;
- alertes ;
- MFA selon criticité.

Évite un verrouillage définitif facilement exploitable pour provoquer un déni de service.

---

## 30. Énumération de comptes

Les flux :

- inscription ;
- login ;
- mot de passe oublié ;
- invitation ;

doivent analyser si les messages permettent de confirmer qu’un compte existe.

Adapte le niveau de discrétion au risque et à l’UX.

Ne révèle pas inutilement des données personnelles.

---

## 31. Reset mot de passe

Utilise les mécanismes Django éprouvés.

Vérifie :

- durée raisonnable ;
- host/domain correct ;
- HTTPS ;
- email ;
- invalidation appropriée ;
- absence de token dans les logs.

Ne crée pas un token maison.

---

## 32. MFA

Ne rends pas la MFA obligatoire pour tout projet.

Propose-la lorsque :

- administrateurs ;
- données sensibles ;
- actions financières ;
- exigences réglementaires ;
- comptes à privilèges.

Privilégie des standards et bibliothèques maintenues.

---

## 33. Secrets

Aucun secret dans Git.

Secrets typiques :

- `SECRET_KEY`
- clés API ;
- DB password ;
- tokens ;
- credentials SMTP ;
- clés OAuth ;
- certificats privés.

Utilise l’environnement ou un gestionnaire de secrets adapté à l’infrastructure.

---

## 34. `.env`

`.env` local :

- non versionné ;
- permissions appropriées ;
- jamais copié dans le README.

`.env.example` :

- versionné ;
- noms des variables ;
- valeurs fictives ;
- commentaires utiles.

N’écris jamais une vraie clé dans `.env.example`.

---

## 35. Secret détecté

Si un secret semble avoir été committé :

1. bloque le push ;
2. informe l’utilisateur ;
3. considère le secret compromis ;
4. recommande rotation/révocation ;
5. retire-le du code ;
6. analyse l’historique Git selon contexte.

Supprimer la ligne dans le dernier commit ne suffit pas toujours.

---

## 36. DEBUG

En production :

```python
DEBUG = False
```

Obligatoire.

Aucune exception normale.

Ne laisse pas un fallback du type :

```python
DEBUG = env.get("DEBUG", True)
```

dans les settings de production.

---

## 37. SECRET_KEY

En production :

- valeur forte ;
- unique ;
- externe au code ;
- différente entre environnements ;
- absence = erreur de démarrage.

N’utilise pas une valeur de développement par défaut.

---

## 38. ALLOWED_HOSTS

En production :

- liste explicite ;
- domaines utilisés ;
- pas de wildcard globale par défaut.

Documente les nouveaux domaines.

---

## 39. HTTPS

La production publique doit utiliser HTTPS sauf contexte d’infrastructure explicitement privé et maîtrisé.

Selon reverse proxy :

- configure correctement la détection HTTPS ;
- évite les boucles de redirect ;
- ne fais confiance aux headers proxy que depuis un proxy contrôlé.

Évalue :

- redirect HTTP -> HTTPS ;
- HSTS ;
- cookies Secure.

---

## 40. HSTS

HSTS peut améliorer la sécurité mais peut rendre une mauvaise configuration durable.

Avant d’augmenter fortement la durée ou inclure les sous-domaines :

- vérifier HTTPS partout ;
- vérifier sous-domaines ;
- déployer progressivement.

Ne précharge pas HSTS sans décision consciente.

---

## 41. SecurityMiddleware

Conserve `SecurityMiddleware` sauf raison explicite.

Configure ses fonctions selon le déploiement réel.

N’ajoute pas des headers obsolètes juste pour remplir une checklist.

---

## 42. Clickjacking

Conserve la protection `X-Frame-Options`/middleware Django lorsqu’elle convient.

Si le site doit réellement être intégré dans un iframe :

- limite explicitement les origines via mécanismes modernes adaptés ;
- documente la décision ;
- n’enlève pas toute protection globalement sans besoin.

---

## 43. Content Security Policy

Une CSP est recommandable pour les applications exposées, particulièrement lorsque le frontend est riche.

Si une CSP est introduite :

- commence restrictive mais compatible ;
- évite `unsafe-inline` sans justification ;
- utilise nonce/hash si nécessaire ;
- déploie éventuellement en report-only ;
- teste les intégrations.

Ne génère pas une CSP factice qui casse l’application ou autorise tout.

---

## 44. Referrer / MIME / headers

Configure les headers modernes pertinents selon la version Django et le reverse proxy.

Évite les doublons contradictoires entre :

- Django ;
- Nginx/Caddy/Traefik ;
- CDN.

La responsabilité doit être documentée.

---

## 45. Erreurs production

Ne révèle jamais :

- stack trace ;
- variables d’environnement ;
- requêtes SQL ;
- tokens ;
- chemins internes sensibles ;
- détails d’infrastructure.

L’utilisateur reçoit un message adapté.

Les détails utiles vont dans les logs/monitoring avec contrôle d’accès.

---

## 46. Logging

Ne log jamais :

- mot de passe ;
- token ;
- cookie de session ;
- `Authorization` header ;
- clé API ;
- données sensibles complètes sans besoin.

Analyse les logs des requêtes externes et erreurs.

Masque/redacte les champs sensibles.

---

## 47. PII / RGPD

La sécurité et la vie privée se recouvrent.

Minimise les données stockées.

Pour une donnée personnelle, demande :

- nécessaire ?
- qui peut la lire ?
- combien de temps ?
- où est-elle loggée ?
- est-elle dans les backups ?
- comment est-elle supprimée ?

Charge le skill RGPD si disponible.

---

## 48. Admin Django

Protège fortement l’admin :

- HTTPS ;
- comptes individuels ;
- permissions minimales ;
- MFA si contexte critique ;
- pas de compte partagé ;
- URL non considérée comme seule protection.

Changer `/admin/` peut réduire le bruit mais n’est pas une mesure d’autorisation.

---

## 49. API keys

Si le projet expose des clés API :

- forte entropie ;
- affichage limité ;
- stockage hashé si possible selon usage ;
- scopes ;
- expiration/rotation ;
- révocation ;
- logs d’usage adaptés.

Ne place pas une clé dans un paramètre URL si un header est adapté.

---

## 50. API

Si DRF/API :

charge `django-api`.

Vérifie notamment :

- authentication classes ;
- permission classes ;
- permissions objet ;
- serializers en écriture ;
- champs readonly ;
- rate limiting/throttling ;
- pagination ;
- CORS ;
- erreurs ;
- exposition excessive de champs.

Ne mets jamais `AllowAny` pour faire fonctionner rapidement un endpoint sans analyser le besoin.

---

## 51. Mass assignment

Pour Forms/ModelForms/Serializers :

déclare explicitement les champs éditables lorsque le contexte est sensible.

Évite d’exposer automatiquement tous les champs d’un modèle contenant :

- rôle ;
- propriétaire ;
- flags de permission ;
- prix calculé ;
- statut interne.

Les champs sensibles doivent être déterminés côté serveur.

---

## 52. Propriétaire et champs système

Ne fais pas :

```python
owner = request.POST["owner"]
```

si le propriétaire doit être l’utilisateur connecté.

Détermine côté serveur :

- owner ;
- organization ;
- created_by ;
- privilèges ;
- status initial.

Ne fais pas confiance au client pour une propriété de sécurité.

---

## 53. Webhooks entrants

Pour un webhook :

- signature ;
- secret ;
- timestamp/replay protection lorsque disponible ;
- taille ;
- content type ;
- idempotence ;
- validation du payload ;
- journalisation sans secret.

Ne fais pas confiance à l’IP seule lorsque le fournisseur offre une signature cryptographique.

---

## 54. Webhooks sortants

Si l’utilisateur peut choisir une URL :

analyse SSRF.

Ajoute :

- timeout ;
- limite ;
- retry contrôlé ;
- signature ;
- secrets distincts ;
- journalisation.

---

## 55. OAuth / OpenID Connect

Utilise une bibliothèque mature.

Vérifie :

- state ;
- nonce si applicable ;
- redirect URI stricte ;
- PKCE selon flux ;
- validation issuer/audience ;
- scopes minimaux.

Ne crée pas un client OAuth maison.

---

## 56. Fichiers CSV/Excel

Les imports de tableurs peuvent être dangereux.

Vérifie :

- taille ;
- format ;
- parser ;
- formules si réexport ;
- valeurs inattendues ;
- encodage ;
- zip bombs pour formats compressés.

Si le projet réexporte du CSV, protège contre formula injection lorsque les données peuvent être ouvertes dans un tableur.

---

## 57. Archives

Pour ZIP/TAR :

- taille décompressée ;
- nombre de fichiers ;
- chemins ;
- symlinks ;
- extensions ;
- zip bombs.

N’extrais jamais une archive utilisateur directement dans un dossier sensible.

---

## 58. Images

Une image peut contenir un fichier invalide ou énorme.

Selon risque :

- limite dimensions ;
- limite taille ;
- décode/re-encode avec bibliothèque maintenue ;
- supprime métadonnées sensibles si besoin ;
- gère decompression bombs.

Ne considère pas `.jpg` comme preuve qu’il s’agit d’une image sûre.

---

## 59. PDF

Les PDF peuvent contenir des fonctionnalités actives selon lecteur.

Si l’application doit seulement stocker/télécharger :

- ne les interprète pas inutilement ;
- stocke en contenu non exécutable ;
- contrôle taille/type.

Si l’application transforme/analyse :

- bibliothèque maintenue ;
- sandbox/process isolation si risque élevé ;
- limites ressources.

---

## 60. URLs et schémas

Toute URL utilisateur doit être validée selon usage.

N’autorise pas implicitement :

- `file://`
- `ftp://`
- `gopher://`
- schémas custom ;
- data URLs ;

si le besoin est uniquement HTTP(S).

---

## 61. XML

Si parsing XML externe :

- désactive entités externes ;
- DTD lorsque non nécessaires ;
- accès réseau ;
- fichiers externes.

Préférer formats moins risqués si choix possible.

---

## 62. Désérialisation

Ne désérialise jamais du `pickle` provenant d’une source non fiable.

Évite tout format pouvant exécuter du code.

Pour données externes :

- JSON ;
- validation de schéma ;
- types explicites.

---

## 63. Templates dynamiques

Ne laisse pas un utilisateur non fiable fournir du code de template Django exécuté côté serveur.

Un système de template est une capacité puissante.

Pour personnalisation utilisateur, définis un format limité.

---

## 64. Email

Pour les emails :

- ne fais pas confiance à une adresse simplement parce que le format est valide ;
- protège contre injection header en utilisant les APIs Django ;
- vérifie liens de reset/invitation ;
- pas de secrets dans logs ;
- contenu HTML échappé.

---

## 65. Rate limiting

Analyse lorsque feature coûteuse ou sensible :

- login ;
- password reset ;
- inscription ;
- recherche lourde ;
- génération ;
- upload ;
- API ;
- webhook test ;
- email.

Le limiteur peut exister :

- applicatif ;
- reverse proxy ;
- CDN.

Documente où la protection est appliquée.

---

## 66. Déni de service applicatif

Analyse :

- pagination absente ;
- regex coûteuse ;
- gros JSON ;
- recursion ;
- génération PDF ;
- traitement image ;
- requête non bornée ;
- export massif.

Impose :

- limites ;
- pagination ;
- timeout ;
- quotas ;
- traitement async si pertinent.

---

## 67. Requêtes ORM

Une requête sûre peut rester un problème sécurité si elle permet d’exfiltrer trop de données.

Évite :

- liste non paginée de données sensibles ;
- filtre contrôlé autorisant des champs internes ;
- ordering arbitraire sur toute colonne ;
- export global sans permission.

---

## 68. Search

Pour une recherche utilisateur :

- paramètres ORM ;
- limites ;
- pagination ;
- coût ;
- accès ;
- pas de SQL concaténé.

Si regex utilisateur : contrôler risque ReDoS ou préférer mécanisme sûr.

---

## 69. Dépendances

Avant ajout :

- nécessité ;
- maintenue ;
- version compatible ;
- advisories ;
- provenance ;
- licence si pertinent.

Avant push demandé :

- analyser vulnérabilités critiques connues avec les outils du projet ;
- ne pas upgrader aveuglément toutes les dépendances.

Une vulnérabilité doit être évaluée dans le contexte : package installé, version, code path, exposition.

---

## 70. Lock files

Si l’écosystème utilise un lockfile, versionne-le pour les applications déployées selon le gestionnaire choisi.

Objectif :

- reproductibilité ;
- audit ;
- contrôle des versions.

Ne maintiens pas plusieurs sources de vérité contradictoires des dépendances.

---

## 71. Packages abandonnés

Une dépendance sans maintenance sur une surface sensible doit déclencher une analyse.

Options :

- remplacement ;
- fork maîtrisé ;
- réduction d’usage ;
- mitigation ;
- suivi.

Documente la décision.

---

## 72. Configuration prod

La configuration production doit échouer fermement plutôt que démarrer dangereusement.

Exemples d’erreur bloquante :

- `SECRET_KEY` absente ;
- hosts non configurés ;
- DB credentials absents ;
- DEBUG actif ;
- stockage privé devenu public ;
- email/URL de sécurité incohérente.

---

## 73. `check --deploy`

Avant production et dans les contrôles adaptés :

```bash
python manage.py check --deploy --settings=config.settings.prod
```

ou commande équivalente au projet.

Comprends les warnings.

Ne les supprime pas sans analyse.

---

## 74. Pre-commit sécurité

Hooks possibles selon projet :

- secret scanner ;
- fichiers privés ;
- clés privées ;
- erreurs de configuration ;
- dépendances légères.

Ne mets pas un scanner très lent sur chaque commit si cela encourage à contourner le hook.

---

## 75. Pre-push sécurité

Lorsqu’un `git push` est explicitement demandé, exécute les contrôles définis par le projet.

Inclure selon contexte :

- tests sécurité ;
- permission tests ;
- secret scanning ;
- dependency audit ;
- Django checks ;
- prod deployment checks ;
- migration check ;
- lint.

Bloque si un risque critique connu subsiste.

---

## 76. Niveaux de sévérité

Classe les problèmes au minimum :

### CRITIQUE — bloquant

Exemples :

- secret actif dans Git ;
- bypass auth évident ;
- exécution de commande contrôlée par utilisateur ;
- upload exécutable public ;
- SQL injection exploitable ;
- accès horizontal à données sensibles ;
- DEBUG production ;
- vulnérabilité critique exploitable.

### ÉLEVÉ — bloquant par défaut

Exemples :

- permission objet manquante ;
- SSRF exploitable ;
- reset de mot de passe défaillant ;
- stockage public non prévu.

### MOYEN

Corriger avant release si réaliste, mais peut nécessiter arbitrage.

### FAIBLE / AMÉLIORATION

Documenter ou planifier selon valeur.

---

## 77. Forçage utilisateur

L’utilisateur peut forcer un choix technique non idéal.

Mais tu ne dois pas exécuter silencieusement un choix créant un risque critique.

Si l’utilisateur insiste :

1. explique clairement le risque ;
2. propose une alternative ;
3. distingue préférence technique et faille réelle ;
4. refuse seulement les actions que les règles de sécurité de la plateforme interdisent.

Pour une dette de sécurité non critique explicitement acceptée :

- documente-la ;
- ajoute une tâche ;
- ne la cache pas.

---

## 78. Tests sécurité

Teste les contrôles importants.

Exemples :

- anonyme refusé ;
- utilisateur A ne peut pas lire B ;
- utilisateur A ne peut pas modifier B ;
- rôle insuffisant refusé ;
- champ système non modifiable ;
- upload interdit rejeté ;
- endpoint exige bonne méthode ;
- CSRF actif sur flux session ;
- rate limit si critique.

Ne teste pas uniquement le chemin autorisé.

Les tests négatifs sont essentiels.

---

## 79. Second developer security review

À la relecture finale, cherche activement :

- données utilisateur rendues `safe` ;
- permission seulement dans UI ;
- queryset non filtré ;
- `csrf_exempt` ;
- `AllowAny` ;
- SQL brut ;
- `subprocess`;
- lecture d’URL ;
- upload ;
- fichier public ;
- secret ;
- logger ;
- redirection ;
- champ owner/role modifiable ;
- wildcard host/CORS ;
- DEBUG ;
- nouveau package.

Ne suppose pas que l’absence d’erreur visible signifie sécurité.

---

## 80. Documentation sécurité

Mets à jour `docs/security/` lorsque nécessaire.

Documente :

- modèle d’autorisation ;
- rôles ;
- données sensibles ;
- stratégie uploads ;
- stratégie secrets ;
- protections production ;
- exceptions de sécurité ;
- procédures de rotation ;
- dépendances sécurité.

N’y écris jamais une vraie clé.

---

## 81. ADR sécurité

Une décision structurante sécurité doit être documentée.

Exemples :

- système de rôles ;
- stratégie MFA ;
- stockage privé ;
- OAuth provider ;
- CSP ;
- architecture multi-tenant ;
- système de clés API.

Documente :

- menace ;
- décision ;
- avantages ;
- limites ;
- responsabilités.

---

## 82. Incident potentiel

Si tu découvres :

- secret committé ;
- fuite de données ;
- permission absente en prod ;
- vulnérabilité exploitable ;

ne te contente pas de corriger le code.

Indique qu’il faut aussi évaluer :

- données potentiellement exposées ;
- logs ;
- rotation ;
- sessions/tokens ;
- notification interne ;
- obligations réglementaires selon contexte.

---

## 83. Sauvegardes

Les backups contiennent souvent les mêmes données sensibles que la production.

Ils doivent être :

- protégés ;
- accessibles au minimum d’acteurs ;
- chiffrés selon risque/infrastructure ;
- soumis à rétention ;
- supprimés correctement.

La sauvegarde quotidienne prévue par le projet doit être intégrée au modèle de sécurité.

---

## 84. Environnement local

Le local peut être moins durci, mais :

- vraies clés de prod interdites ;
- vraies données personnelles évitées ;
- dump production anonymisé si utilisé ;
- emails externes neutralisés si nécessaire ;
- services de paiement/sms sandbox.

Ne copie pas la prod sur un ordinateur de développement sans nécessité.

---

## 85. Staging

Le staging doit ressembler à la prod côté sécurité.

Mais :

- clés distinctes ;
- DB distincte ;
- comptes distincts ;
- intégrations sandbox quand possible.

Ne réutilise jamais les secrets production pour simplifier.

---

## 86. Production

Checklist minimale :

- DEBUG false ;
- secret externe ;
- hosts explicites ;
- HTTPS ;
- cookies sécurisés ;
- CSRF correct ;
- permissions ;
- DB non superuser ;
- logs sécurisés ;
- backups ;
- monitoring ;
- dépendances contrôlées ;
- `check --deploy` ;
- admin protégé ;
- media correctement servis.

Adapte selon infrastructure.

---

## 87. Critères de Definition of Done sécurité

Une feature n’est pas terminée tant que les points applicables suivants ne sont pas satisfaits :

- acteurs identifiés ;
- authentification correcte ;
- autorisation correcte ;
- permission objet testée ;
- entrées validées ;
- sorties correctement échappées ;
- CSRF traité ;
- SQL/command injection analysée ;
- uploads analysés ;
- SSRF analysée si URLs ;
- secrets propres ;
- logs propres ;
- données personnelles analysées ;
- dépendances analysées si modifiées ;
- tests négatifs passants ;
- documentation sécurité mise à jour ;
- seconde revue effectuée.

---

## 88. Principe final

Django fournit beaucoup de protections, mais aucune framework ne peut deviner les règles métier.

La faille la plus dangereuse est souvent un code parfaitement valide techniquement qui autorise la mauvaise personne à faire la mauvaise chose.

Pour chaque feature, demande toujours :

> « Si je contrôle entièrement les données envoyées au serveur, puis-je lire, modifier, déclencher ou télécharger quelque chose que je ne devrais pas ? »
