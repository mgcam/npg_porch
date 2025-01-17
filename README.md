# FastAPI Server for Pipeline Orchestration Project

## Requirements

Python >= 3.7
sqlite3 >= 3.9

## Installation & Usage

To run the server, please execute the following from the root directory:

```bash
bash
pip3 install -e .
cd server
export DB_URL=postgresql+asyncpg://npg_rw:$PASS@npg_porch_db:$PORT/$DATABASE
export DB_SCHEMA='non_default'
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

and open your browser at `http://localhost:8080` to see links to the docs.

## Testing

Use `pytest` from the package root

Individual tests are run in the form `pytest server/tests/init_test.py`

### Fixtures

Fixtures reside under `server/tests/fixtures` and are registered in `server/tests/conftest.py`
They can also be listed by invoking `pytest --fixtures`

Any fixtures that are not imported in conftest.py will not be detected.

## Deployment of schema from ORM

Create a schema on a postgres server:

```bash
psql --host=npg_porch_db --port=$PORT --username=npg_admin --password -d postgres

CREATE SCHEMA npg_porch
```

Then run a script that deploys the ORM to this schema

```bash
DB=npg_porch
export DB_URL=postgresql+psycopg2://npg_admin:$PASS@npg_porch_db:$PORT/$DB
server/deploy_schema.py

psql --host=npg_porch_db --port=$PORT --username=npg_admin --password -d $DB
```

Permissions must be granted to the npg_rw and npg_ro users to the newly created schema

```sql
GRANT USAGE ON SCHEMA npg_porch TO npgtest_ro, npgtest_rw;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA npg_porch TO npgtest_rw;
GRANT SELECT ON ALL TABLES IN SCHEMA npg_porch TO npgtest_ro;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA npg_porch TO npgtest_rw;
```

Note that granting usage on sequences is required to allow autoincrement columns to work during an insert. This is a trick of newer Postgres versions.
