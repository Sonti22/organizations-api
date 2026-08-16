# Configuration

The **organizations‑api** service relies on a few environment variables that are loaded via `pydantic-settings`. Proper configuration is required for the application to start and connect to the PostgreSQL database.

## Required variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Full SQLAlchemy async URL used by the application. It must include the driver (`postgresql+asyncpg`), user, password, host, port and database name. | `postgresql+asyncpg://postgres:postgres@localhost:5432/organizations` |
| `POSTGRES_USER` | (Optional) Username for the Postgres container. Defaults to `postgres` if not set. |
| `POSTGRES_PASSWORD` | (Optional) Password for the Postgres container. Defaults to `postgres` if not set. |
| `POSTGRES_DB` | (Optional) Database name for the Postgres container. Defaults to `organizations` if not set. |

The `DATABASE_URL` is the only variable directly consumed by the FastAPI application (see `app.core.config`). The other variables are used by the Docker Compose file to initialise the Postgres container.

## Loading the configuration

The project uses **pydantic‑settings**. When the application starts, the `Settings` class (defined in `app.core.config`) reads the environment variables automatically. No additional code changes are required – just ensure the variables are present in your environment or in a `.env` file that is loaded by Docker Compose.

## Example `.env`

```dotenv
# Database connection for the API
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/organizations

# Optional Postgres container variables (used by docker‑compose)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=organizations
```

Place this file at the project root and reference it in `docker-compose.yml` (already configured).

---

*This documentation file does not affect the runtime behaviour of the application but greatly improves developer experience and reduces configuration‑related errors.*