# Téléconsultation API

API REST Flask pour une plateforme de prise de rendez-vous médicaux (projet final —
Conception d'API REST avec Flask, Sujet D).

## Domaine

- **Doctor** : profil médecin (nom, spécialité, email), lié à un `User` de rôle `doctor`.
- **Patient** : profil patient (nom, email, date de naissance), lié à un `User` de rôle `patient`.
- **Slot** : créneau proposé par un médecin (`start_time`, `end_time`, `is_available`).
- **Appointment** : réservation d'un créneau par un patient (`reason`, `status`).

Règles métier implémentées :
- un créneau déjà réservé ne peut pas l'être une seconde fois → `409`
- l'annulation n'est possible que jusqu'à 24h avant le rendez-vous → `403` sinon
- un patient ne voit que ses propres rendez-vous ; un médecin voit tous les siens avec les
  infos du patient
- `start_time < end_time` et durée du créneau comprise entre 15 et 120 minutes → `422` sinon
- seul un compte `doctor` peut créer un créneau (`403` pour un `patient`)

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # puis éditez les secrets
export FLASK_APP=run.py
flask db upgrade        # crée les tables via Alembic
python run.py            # démarre sur http://localhost:5000
```

## Lancer les tests

```bash
pytest -v --cov=app --cov-report=term-missing
```

10 tests, couverture ≈ 84 % (objectif du cours : ≥ 70 %).

## Documentation

Une fois le serveur lancé : `http://localhost:5000/docs` (Swagger UI),
spec brute sur `/openapi.json`.

## Déploiement Docker

```bash
docker compose up --build
curl http://localhost:8000/health
```

## Parcours de démonstration

```bash
# 1. Inscription d'un médecin et d'un patient
curl -X POST localhost:5000/api/v1/auth/register -H "Content-Type: application/json" \
  -d '{"email":"doc@ex.com","password":"secret123","role":"doctor","name":"Dr House","specialty":"Diagnostic"}'
curl -X POST localhost:5000/api/v1/auth/register -H "Content-Type: application/json" \
  -d '{"email":"pat@ex.com","password":"secret123","role":"patient","name":"Alice"}'

# 2. Connexion (récupérer les tokens)
DOC_TOKEN=$(curl -s -X POST localhost:5000/api/v1/auth/login -H "Content-Type: application/json" \
  -d '{"email":"doc@ex.com","password":"secret123"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
PAT_TOKEN=$(curl -s -X POST localhost:5000/api/v1/auth/login -H "Content-Type: application/json" \
  -d '{"email":"pat@ex.com","password":"secret123"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 3. Le médecin crée un créneau
curl -X POST localhost:5000/api/v1/slots/ -H "Authorization: Bearer $DOC_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"start_time":"2026-10-01T10:00:00","end_time":"2026-10-01T10:30:00"}'

# 4. Le patient réserve (adapter slot_id)
curl -X POST localhost:5000/api/v1/appointments/ -H "Authorization: Bearer $PAT_TOKEN" \
  -H "Content-Type: application/json" -d '{"slot_id":1,"reason":"consultation"}'

# 5. Le patient voit ses rendez-vous
curl localhost:5000/api/v1/appointments/ -H "Authorization: Bearer $PAT_TOKEN"

# 6. Healthcheck
curl -i localhost:5000/health
```

## Ce qui reste à personnaliser avant le rendu

- adapter `CHECKLIST.md` (5 items propres au projet, comme demandé au TP 12)
- restreindre `CORS` aux origines réelles en prod (actuellement `*`)
- ajouter les réponses écrites aux questions de réflexion des étapes 0 et 1 de l'énoncé
- éventuellement : endpoint `/metrics`, versionnement `/api/v2` (bonus)
