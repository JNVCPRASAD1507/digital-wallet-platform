# Digital Wallet & Transaction Processing Platform

This repository is a production-oriented FastAPI starting implementation for the supplied hiring assignment.

## Folder structure

```text
digital-wallet-platform/
├── app/
│   ├── api/
│   │   ├── router.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── wallets.py
│   │       ├── money.py
│   │       ├── transactions.py
│   │       ├── notifications.py
│   │       ├── admin.py
│   │       └── dashboard.py
│   ├── core/
│   ├── dependencies/
│   ├── models/
│   ├── schemas/
│   └── services/
├── alembic/
├── docs/
├── postman/
└── tests/
```

## Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Swagger: `http://localhost:8000/docs`

## Important design

- PostgreSQL is the source of truth.
- Money uses `Decimal`/`NUMERIC(20,2)`, not floating point.
- Deposit/withdrawal/transfer operations run inside one database transaction.
- Wallet rows are locked with `SELECT ... FOR UPDATE`.
- Two-wallet transfers lock rows in deterministic UUID order to reduce deadlocks.
- Idempotency is enforced by a unique `(user_id, key, operation)` constraint.
- Ledger rows are append-only from the API perspective.
- Wallet ownership and role checks are enforced before financial mutations.
