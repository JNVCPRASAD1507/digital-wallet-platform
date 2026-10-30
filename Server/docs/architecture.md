# Architecture

Routes are intentionally thin. Authentication/authorization is handled by dependencies. Financial
business rules are in service modules. SQLAlchemy models represent the database.

## Concurrency

A transfer locks both wallet rows before reading balances. The locks are acquired in deterministic
UUID order. Therefore two concurrent requests cannot both read the same old sender balance and
successfully spend it.

## Idempotency

Critical mutation endpoints require `Idempotency-Key`. A unique database constraint prevents duplicate
financial operations for the same user/key/operation.

## Ledger

Every balance-changing operation inserts a transaction ledger record containing balance-before and
balance-after values. No normal endpoint updates or deletes ledger rows.

## Error contract

Domain failures use:

```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "Insufficient wallet balance"
  }
}
```
