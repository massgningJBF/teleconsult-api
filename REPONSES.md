# Réponses aux questions de réflexion — Étapes 0 et 1

## Étape 0 — Choix du sujet

### Question 1

Nous avons retenu le **Sujet D — API de téléconsultation** (médecins, patients,
créneaux, rendez-vous). Ce choix est motivé par la richesse des règles métier à
modéliser autour de la **ressource centrale `Slot`/`Appointment`** : contrairement à
un simple CRUD, la réservation d'un créneau est une opération concurrente et
stateful (un créneau ne peut être réservé qu'une fois, ce qui impose de gérer un
conflit `409`), ce qui oblige à réfléchir sérieusement à l'intégrité des données
plutôt qu'à de la simple validation de champs. Les règles de **contrôle d'accès par
rôle** (`doctor` crée des créneaux, `patient` les réserve, chacun ne voit que ce qui
le concerne) donnent un cas d'usage concret et réaliste pour l'autorisation, plus
intéressant qu'une simple distinction lecture/écriture. Enfin, la règle
**temporelle** de l'annulation (impossible à moins de 24h du rendez-vous) introduit
une logique métier dépendant du temps réel, qu'on ne retrouve pas dans un CRUD
classique et qui nous a semblé pédagogiquement plus stimulante à implémenter et à
tester correctement.

## Étape 1 — Concevoir le contrat avant le code

### Question 2 — Tableau des ressources

| Ressource | URL collection | URL élément | Méthodes | Code succès |
|---|---|---|---|---|
| Auth | `/api/v1/auth/register` | — | `POST` | `201` |
| Auth | `/api/v1/auth/login` | — | `POST` | `200` |
| Auth | `/api/v1/auth/refresh` | — | `POST` | `200` |
| Auth | `/api/v1/auth/me` | — | `GET` | `200` |
| Doctor | `/api/v1/doctors/` | `/api/v1/doctors/<id>` | `GET` | `200` |
| Slot | `/api/v1/slots/` | — | `GET`, `POST` | `200` / `201` |
| Appointment | `/api/v1/appointments/` | — | `GET`, `POST` | `200` / `201` |
| Appointment | — | `/api/v1/appointments/<id>/cancel` | `POST` | `200` |

**Écarts au CRUD standard, justifiés :**
- Pas de `PUT`/`DELETE` sur `Doctor`/`Patient` : ces profils sont créés
  automatiquement via `/auth/register` et ne sont pas éditables dans ce périmètre —
  ajouter leur édition n'apportait pas de valeur pédagogique supplémentaire par
  rapport au temps disponible.
- Pas de `DELETE` sur `Appointment` : on annule (changement de `status`, via
  `POST .../cancel`) plutôt que de supprimer, car l'historique des rendez-vous
  annulés doit rester consultable (traçabilité métier).
- `POST /appointments/<id>/cancel` plutôt qu'un `PATCH` générique sur le statut :
  l'annulation a une règle métier propre (fenêtre de 24h) qui justifie une route
  dédiée plutôt qu'une mise à jour de champ arbitraire.
- Pas de `DELETE` sur `Slot` : un créneau déjà réservé ne doit pas pouvoir
  disparaître silencieusement sous un rendez-vous existant ; ce n'était pas prioritaire
  vu le temps imparti.

### Question 3 — Les trois codes d'erreur les plus fréquents

| Code | Situation métier concrète |
|---|---|
| `401 Unauthorized` | Un patient tente de réserver un créneau (`POST /appointments/`) sans envoyer de jeton JWT, ou avec un jeton expiré. |
| `403 Forbidden` | Un compte `patient` tente de créer un créneau (`POST /slots/`), une action réservée aux `doctor` ; ou un patient tente d'annuler un rendez-vous à moins de 24h de l'heure du rendez-vous. |
| `409 Conflict` | Un patient tente de réserver un créneau déjà réservé par quelqu'un d'autre (`is_available = false`). |

*(Le `422` — validation, ex. durée de créneau hors des bornes 15-120 min — est
également fréquent mais nous avons choisi de documenter les trois qui reflètent le
mieux la logique métier propre au sujet plutôt que la validation générique.)*

### Question 4 — Schémas JSON

**Réponse d'erreur unique (implémentée dans `app/errors.py`) :**
```json
{
  "error": "conflict",
  "message": "ce creneau n'est plus disponible"
}
```
Pour les erreurs de validation (`422`), `message` est un objet détaillant le champ
fautif :
```json
{
  "error": "validation_error",
  "message": {
    "end_time": ["la duree du creneau doit etre comprise entre 15 et 120 minutes"]
  }
}
```

**Réponse de collection paginée (implémentée sur `GET /slots/`) :**
```json
{
  "items": [
    {
      "id": 1,
      "doctor_id": 1,
      "start_time": "2026-10-01T10:00:00",
      "end_time": "2026-10-01T10:30:00",
      "is_available": true
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 10,
    "pages": 3,
    "total": 27
  }
}
```

### Question 5 — Modèle de données et stratégie de chargement

**Entités et cardinalités :**
- `User (1) — (1) Doctor` : un compte utilisateur de rôle `doctor` possède exactement
  un profil `Doctor` (clé étrangère `doctor.user_id`, unique).
- `User (1) — (1) Patient` : idem pour le rôle `patient` (`patient.user_id`, unique).
- `Doctor (1) — (N) Slot` : un médecin propose plusieurs créneaux (`slot.doctor_id`).
- `Slot (1) — (0..1) Appointment` : un créneau porte au plus un rendez-vous
  (`appointment.slot_id`, unique — garantit qu'un créneau ne peut être réservé
  qu'une seule fois au niveau base de données, pas seulement au niveau applicatif).
- `Patient (1) — (N) Appointment` : un patient peut avoir plusieurs rendez-vous
  (`appointment.patient_id`).

**Stratégie de chargement, relation par relation :**
- `User → Doctor/Patient` : chargement **lazy** (par défaut SQLAlchemy). On ne
  charge le profil que lorsqu'on en a explicitement besoin (ex. dans
  `auth_service` après authentification) ; l'exposer en eager sur chaque lecture de
  `User` serait un coût inutile, ce chemin n'étant pas sur la voie chaude de l'API.
- `Doctor → Slot` : lazy. `GET /slots/` interroge directement la table `Slot` avec un
  filtre `doctor_id`, sans jamais traverser l'objet `Doctor` — le lazy loading par
  défaut n'est donc jamais sollicité sur ce chemin.
- `Slot → Appointment` : lazy. Peu consulté dans ce sens (on part plutôt de
  `Appointment` vers `Slot`).
- `Patient → Appointment` : chargement **explicite** via une requête filtrée
  (`Appointment.query.filter_by(patient_id=...)`) plutôt que la relation
  SQLAlchemy — équivalent fonctionnellement à du lazy loading contrôlé.
- `Appointment → Slot`, pour la liste des rendez-vous d'un **médecin**
  (`list_appointments_for_doctor`) : nous utilisons un **join explicite** entre
  `Appointment` et `Slot` (`Appointment.query.join(Slot, ...)`) — c'est le seul
  endroit où un chargement de type "eager" est justifié, car sans lui on devrait
  d'abord charger tous les créneaux du médecin puis, pour chacun, requêter les
  rendez-vous associés (N+1 requêtes). Le join ramène tout en une seule requête SQL.
