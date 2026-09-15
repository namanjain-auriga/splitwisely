# Splitwisely

Splitwisely is a Django template app for tracking shared trip expenses, handling participant-specific splits, and reducing the final balance to the fewest payments.

The frontend is now rendered with Django templates in `backend/trip/templates/`.

## How To Run

From the repository root:

```bash
cd /workspaces/splitwisely/backend
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:5173
```

Open [http://localhost:5173/signup/](http://localhost:5173/signup/) and register with an email address. Then log in, create a trip, and invite friends by account email. An invitation remains pending until the recipient accepts it; only accepted members can see that group's expenses and balances.

The app uses SQLite at `backend/splitwisely.sqlite3`. Django templates and static assets are under `backend/trip/`. The old Vite client remains in `frontend/` for reference, but is not required to run the current app.

## Run Tests

```bash
cd /workspaces/splitwisely/backend
python3 manage.py test trip
```

The test suite uses an isolated in-memory database and covers authentication, account-scoped trips, automatic owner membership, invitation acceptance and decline, participant-specific expense balances, and settlement minimization.

## Main Routes

- `/signup/` — create an account
- `/login/` — log in with email or legacy username
- `/` — current trip dashboard
- `/trips/new/` — create a trip/group
- `/trips/<id>/members/add/` — invite a member by email
- `/invitations/<id>/accept/` — accept a pending group invitation
- `/invitations/<id>/decline/` — decline a pending group invitation
- `/settle-up/` — view the minimized settlement plan

## Database And Migrations

The current schema includes Django users, trips, members, expenses, and invitations. After pulling schema changes, run:

```bash
cd /workspaces/splitwisely/backend
python3 manage.py migrate
```
