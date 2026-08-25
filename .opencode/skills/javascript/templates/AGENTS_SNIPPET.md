## JavaScript

- Charger `javascript` uniquement lorsqu’une feature nécessite réellement du JavaScript.
- Privilégier JavaScript natif moderne et modules ES.
- Ne pas introduire React/Vue/Vite/TypeScript pour une interaction simple.
- Le backend Django reste source de vérité pour permissions, validations et données métier.
- Pour les requêtes session Django, conserver CSRF.
- Préférer `textContent` et les APIs DOM sûres à `innerHTML`.
- Ne jamais stocker de secret ou token sensible dans localStorage/sessionStorage.
- Toute interaction doit rester accessible au clavier et gérer loading/error/success.
