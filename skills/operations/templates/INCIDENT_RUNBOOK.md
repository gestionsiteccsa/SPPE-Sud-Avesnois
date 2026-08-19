# Runbook Incident

## Symptôme

Décrire ce qui est observé.

## Impact

- Utilisateurs concernés :
- Fonctionnalités :
- Données en risque :

## Vérifications

1. Health check
2. Services
3. Logs
4. Disque
5. Mémoire
6. PostgreSQL
7. Réseau/TLS

## Actions sûres

- ...

## Actions à risque

N’exécuter qu’après validation :
- restauration ;
- suppression ;
- rollback DB ;
- reboot ;
- purge.

## Validation

- [ ] Service accessible.
- [ ] Health check OK.
- [ ] Logs stables.
- [ ] Données cohérentes.

## Postmortem

- Cause :
- Détection :
- Correction :
- Prévention :
