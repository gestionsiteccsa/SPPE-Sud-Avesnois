## Operations

- Charger `operations` pour monitoring, logs, alertes, incidents, maintenance et exploitation production.
- Toute production doit avoir au minimum : health check, logs, surveillance disque, backups, TLS et état des services.
- Les alertes doivent être actionnables et peu bruyantes.
- Ne jamais masquer un incident par des redémarrages automatiques infinis.
- Toute tâche planifiée critique doit être documentée et observable.
- Les opérations destructrices restent soumises à accord explicite.
