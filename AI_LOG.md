# AI Conversation Log

This file records the user requests and assistant responses from the Splitwisely implementation conversation. System and developer instructions, credentials, and raw tool internals are intentionally excluded.

---

## 1. Fullstack Application

**User prompt**

> Six friends are going to Goa for four days. Over the trip the money flies around: someone books the cab, someone pays for a big group dinner, someone covers the stay, someone grabs chai and snacks at 2am. Usually they just split things evenly — but not always: only four of them went scuba diving, and Priya, who doesn’t drink, shouldn’t have to chip in for the beer run. By the last evening nobody can remember who paid for what; there’s a vague feeling that someone’s owed a lot and someone’s gotten off lightly. They keep asking ‘wait, what was that big one on day two?’ and scrolling back through a messy group chat to find it. What they really want at the end is dead simple: who owes whom, and the fewest payments to square up.
>
> Build something so the group can settle up fairly at the end of the trip.
>
> The group talks about spending with lots of context clues, so make expenses easy to add, find, and understand.
>
> Build a fullstack application using Python and React.

**Assistant response**

Built the initial fullstack Splitwisely application with a FastAPI backend and React/Vite frontend. It included seeded Goa expenses, participant-specific splits, search/filtering, balances, and minimized settlement transfers.

The API included expense creation and settlement calculation. The frontend included a trip dashboard, expense history, search, filtering, balance cards, and a settle-up view.

Validation passed with Python compilation, API settlement assertions, and `npm run build`.

---

## 2. Run Instructions

**User prompt**

> steps to run

**Assistant response**

Install dependencies and start two processes:

```bash
npm install
python3 -m pip install -r backend/requirements.txt
```

Backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

Frontend:

```bash
npm run dev
```

Open `http://localhost:5173`.

---

## 3. Uvicorn Exit Code 137

**User prompt**

The Uvicorn process started, served `/api/overview`, then exited with code `137` after reload activity.

**Assistant response**

Exit code `137` indicates the container killed Uvicorn, likely because `--reload` created an extra watcher process and caused memory pressure. The recommended command was:

```bash
uvicorn backend.main:app --port 8000
```

The `404` responses for `/` and `/favicon.ico` were identified as harmless because the API did not define those routes.

---

## 4. Frontend Blank or Unavailable

**User prompt**

> i am not able to view anything on the frontend

**Assistant response**

The Vite server had stopped or moved from port `5173` to `5174` because the original port was occupied. The frontend and backend ports were checked, CORS was updated to allow `5174`, and the frontend was restarted.

The frontend was verified at:

```text
http://localhost:5174
```

The backend was verified at:

```text
http://localhost:8000
```

---

## 5. Open the Frontend

**User prompt**

> open the front end and show me

**Assistant response**

Opened the running frontend at:

```text
http://localhost:5173
```

---

## 6. Blank Page and HTML Entrypoint

**User prompt**

> it doesnot show any thing on that no html nothing

**Assistant response**

The Vite entrypoint was replaced with a complete HTML document containing a doctype, viewport metadata, title, React root, and module script. Vite was restarted on port `5173`, and the served HTML plus backend API were verified.

The frontend URL was:

```text
http://localhost:5173/
```

---

## 7. Dedicated Frontend Folder

**User prompt**

> make a new frontend with a dedicated frontend folder and also install all the dependencies it requires; use vite react for the frontend

**Assistant response**

The React/Vite project was moved into `frontend/` with its own:

- `package.json`
- `package-lock.json`
- `vite.config.js`
- `index.html`
- `src/main.jsx`
- `src/styles.css`

Dependencies were installed with `npm install` inside `frontend/`, and `npm run build` passed.

---

## 8. Replace React with Django Templates

**User prompt**

> use django template instead of react for frontend

**Assistant response**

The frontend was converted to Django templates. Added Django project files under `backend/`, including `manage.py`, settings, URLs, views, templates, static CSS, add/edit expense pages, and a settle-up page.

The run command became:

```bash
cd backend
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:5173
```

Django checks and template rendering passed.

---

## 9. Database, Multiple Trips, Groups, and Members

**User prompt**

> use a database to store the details and expenses
>
> also maintain multiple trips and make an option to add a new trip/group then add expenses to that group and also add/invite new members to that group

**Assistant response**

Added SQLite-backed Django models for:

- Trips
- Members
- Expenses

Added multiple trip switching, new trip creation, member invitation screens, trip-specific expenses, trip-specific participants, balances, and settlements.

The SQLite database is stored at:

```text
backend/splitwisely.sqlite3
```

Migrations were created and applied, and database workflow checks passed.

---

## 10. User Accounts and Automatic Group Membership

**User prompt**

> maintain my account and add a signup and login and maintain the user account and auto add the user while creating the group

**Assistant response**

Added Django authentication with signup, login, logout, password hashing, protected trip actions, trip ownership, and automatic membership for the account creating a trip.

The creator becomes both the trip owner and first member. The signup entrypoint is:

```text
http://localhost:5173/signup/
```

---

## 11. Email Accounts, Account-Scoped Trips, and Invitations

**User prompt**

> also maintain the users using their mail ids and maintain their expenses and trips
>
> suppose i have some trips/groups and i login to some other account then show me trips and expenses for that account
>
> also maintain this when i add some user to a group then maintain that expenses also
>
> also add a feature to accept the group joining request in a new section if added by some user that you are added by whom and to which group

**Assistant response**

Added email-first accounts and account-scoped access. Users see only trips they own or have accepted membership in. Expenses and balances remain attached to their trip.

Invitations are stored with:

- Inviter
- Recipient email/user
- Destination trip
- Pending, accepted, or declined status

The invitation section shows who invited the user and which group they were invited to. Accepting creates trip membership; declining does not. Pending invitations are linked automatically when a new account signs up with the invited email.

The complete invitation lifecycle and account isolation were tested successfully.

---

## 12. README and Reasoning Documents

**User prompt**

> README.md — how to run (template in the scoring section).
>
> REASONING.md — Features I built (incl. the ones inferred), Key decisions & trade-offs, How I handled the twist, What I’d do with more time.
>
> make these files

**Assistant response**

Created:

- `README.md` with Django setup, migration, run, route, and test instructions.
- `REASONING.md` with implemented features, inferred features, architecture decisions, trade-offs, twist handling, and future work.

---

## 13. Automated Test Cases

**User prompt**

> make some test cases

**Assistant response**

Added `backend/trip/tests.py` with 9 Django tests covering:

- Email and username authentication
- Login protection
- Signup account creation
- Automatic trip owner membership
- Invitation acceptance
- Invitation decline
- Account-scoped trip visibility
- Participant-specific expense balance calculation
- Settlement minimization

The missing `backend/trip/__init__.py` package marker was also added. The suite passed:

```text
Ran 9 tests
OK
```

---

## 14. Documentation Refresh

**User prompt**

> also update readme and reasoning.md

**Assistant response**

Updated both documents to include:

- Email-based account behavior
- Pending invitation lifecycle
- Accept/decline invitation routes
- Database migration instructions
- Isolated test database behavior
- Current automated test coverage
- Updated authentication and invitation trade-offs

---

## 15. Current Export Request

**User prompt**

> AI_LOG.md — their prompts and the AI’s responses, exported. This is how we tell who directed the AI versus who pasted its output unchecked.
>
> make a AI_LOG.md file and add all the conversations my prompts and your responses in that file

**Assistant response**

Created this chronological `AI_LOG.md` transcript containing the user prompts and assistant responses from the conversation. System/developer instructions and raw tool internals were excluded so the file focuses on the direction given by the user and the resulting AI work.
