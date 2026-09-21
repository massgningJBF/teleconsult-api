# Checklist avant mise en production

- [ ] secrets via variables d'environnement, jamais dans le depot
- [ ] DEBUG = False en production
- [ ] base derriere plusieurs workers Gunicorn
- [ ] rate limiting actif sur /api/v1/auth/login
- [ ] CORS restreint aux origines connues (actuellement `*`, a restreindre avant prod)
- [ ] en-tetes de securite presents
- [ ] erreurs JSON uniformes, pas de stacktrace exposee
- [ ] healthcheck /health verifiant la base
- [ ] suite pytest verte en CI avant tout deploiement
- [ ] migrations Alembic a jour (`flask db upgrade`) avant chaque deploiement
- [ ] JWT_SECRET_KEY different de SECRET_KEY et suffisamment long
- [ ] limite de debit globale (200/h) adaptee au trafic reel avant prod
- [ ] sauvegarde reguliere du fichier de base de donnees / volume Docker
- [ ] revue des roles: seul un compte "doctor" peut creer des creneaux
