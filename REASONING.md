# Splitwisely Reasoning

## Features I Built

- Django server-rendered frontend with a responsive trip dashboard.
- SQLite persistence for users, trips, members, invitations, and expenses.
- Email-based signup and login, with compatibility for existing username-based accounts.
- Multiple trips/groups with an account-scoped trip switcher.
- Automatic membership: the account creating a trip becomes its owner and first member.
- Email invitations with pending, accepted, and declined states.
- A visible invitation section showing who invited the user and which group they were invited to.
- Accepting an invitation creates the recipient's membership and exposes that group's expenses and balances.
- Expense creation, editing, and deletion within the selected trip.
- Participant-specific expense splits, so optional activities and excluded items are handled fairly.
- Search and category filtering for reconstructing what happened during the trip.
- Per-member paid, owed, and net balances.
- Settlement calculation that matches debtors to creditors to reduce the number of transfers.
- CSRF-protected forms and login-required trip and expense actions.
- Automated Django tests for login, signup, trip ownership, invitation state changes, authorization boundaries, participant-specific balances, and settlement output.

## Inferred Features

The prompt strongly implied that the app needed more than a final arithmetic result. I inferred and implemented:

- A searchable expense history, because the group needs to recover the context of a vague day-two charge.
- Notes, day labels, categories, and payer information, because those details make old expenses understandable.
- A participant picker per expense, because equal splitting is not always fair.
- Separate trip ownership and membership, because a user should see their own groups and accepted invitations rather than every trip in the database.
- An invitation inbox, because adding somebody to a group should be an explicit action that they can accept or decline.

## Key Decisions & Trade-offs

### Django templates instead of React

The final frontend uses Django templates and standard POST forms. This keeps authentication, CSRF protection, redirects, and database writes in one server-side application. The earlier Vite/React client remains in `frontend/` as reference, but it is not part of the current run path.

### SQLite for persistence

SQLite keeps local setup small and makes the project immediately runnable without a separate database service. A production deployment would likely use PostgreSQL, especially for concurrent writes, backups, and stronger operational guarantees.

### Django's built-in User model

The app uses Django's built-in authentication and password hashing instead of introducing a custom user model late in the project. Email is the user-facing identity, while the email-or-username backend preserves compatibility with accounts created before email login was added. The database username is set to the email for new accounts, which keeps Django's standard login view usable without exposing a separate username concept.

### Invitation by email

Invitations are stored as database records instead of immediately creating a member. If the recipient already has an account, the invitation points to that user. If they sign up later with the invited email, the pending invitation is linked to the new account. Membership is created only after acceptance, and the recipient can explicitly decline the request.

### Tests use an isolated database

The test suite runs with Django's temporary in-memory database, so authentication, trip ownership, invitation acceptance, and expense calculations can be verified without changing the developer's local SQLite data. Run it with `python3 manage.py test trip` from `backend/`.

### In-memory settlement calculation

Expenses and participants are stored in SQLite, while balances and settlement transfers are calculated from the current trip records when requested. This avoids stale derived totals and keeps the source of truth clear. The current greedy creditor/debtor matching minimizes transfers for the normal group-expense case.

## How I Handled The Twist

The central twist is that the group does not always split expenses evenly. Each expense stores its own participant set. The calculation divides only by that set, so scuba is shared by the divers and Priya is excluded from the beer-related dinner cost. The same participant-aware records drive balances and the final settle-up list, so the UI and arithmetic use one consistent source of truth.

The social twist is handled through invitations rather than silently adding people. A recipient can see the inviter and destination group, then accept or decline. Once accepted, that account can see the group's history, add expenses using its members, and participate in the settlement.

## What I Would Do With More Time

- Send real invitation emails with signed, expiring invite links.
- Add user profile names and avatars separate from login email.
- Add per-person custom shares or percentages for mixed meals.
- Persist settlement payment completion and show an audit trail.
- Expand the existing automated tests to cover real email delivery and concurrent invitation updates.
- Add PostgreSQL configuration, environment-based secrets, and production deployment settings.
- Add pagination and indexes for large trips.
- Add import/export for group-chat receipts and CSV backups.