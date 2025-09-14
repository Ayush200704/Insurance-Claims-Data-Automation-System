# PostgreSQL Setup Guide

## Option 1: Install PostgreSQL on Windows

### Download and Install
1. Go to https://www.postgresql.org/download/windows/
2. Download PostgreSQL installer
3. Run the installer with these settings:
   - Username: `postgres`
   - Password: `Ayush200704@`
   - Port: `5432`
   - Database: `insurance_claims`

### Start PostgreSQL Service
```bash
# Start PostgreSQL service
net start postgresql-x64-15

# Or through Services.msc
# Search for "Services" in Start menu
# Find "postgresql-x64-15" and start it
```

### Create Database
```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Create database
CREATE DATABASE insurance_claims;

# Exit
\q
```

## Option 2: Use Docker PostgreSQL

```bash
# Run PostgreSQL in Docker
docker run --name postgres-insurance \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=Ayush200704@ \
  -e POSTGRES_DB=insurance_claims \
  -p 5432:5432 \
  -d postgres:15
```

## Option 3: Use SQLite (Easiest)

Just use the current SQLite configuration - no installation needed!

```python
database_url: str = "sqlite:///./insurance_claims.db"
```

## Test Connection

```python
# Test database connection
python -c "
from app.core.database import engine
try:
    with engine.connect() as conn:
        print('✅ Database connection successful!')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

