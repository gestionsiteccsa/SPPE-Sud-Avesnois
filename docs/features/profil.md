# Mon profil

Chaque compte connecté au tableau de bord dispose d'une page **Mon profil** (`/dashboard/profil/`, lien « Mon profil » dans le menu latéral).

## Champs modifiables

- **Prénom** ;
- **Nom** ;
- **Adresse email** : sert d'identifiant de connexion, elle doit rester unique (le nom d'utilisateur est synchronisé avec l'email).

## Sécurité

Le changement d'adresse email est confirmé par la saisie du **mot de passe actuel** ; une adresse déjà utilisée par un autre compte est refusée. Toute modification est tracée dans le journal d'audit (page « Journal », réservée aux superadmins) avec les anciennes et nouvelles valeurs.