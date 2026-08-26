# perform alembic migrations

1. Create migration

```bash
uv run alembic revision --autogenerate -m "description"
```

2. Upgrade

```bash
uv run alembic upgrade head
```

3. Downgrade

```bash
uv run alembic downgrade -1
```
