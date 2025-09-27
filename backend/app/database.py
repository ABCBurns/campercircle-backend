from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    # "DATABASE_URL", "postgresql://camper:camperpass@db:5432/camperdb"
    "DATABASE_URL",
    "postgresql+psycopg2://camper:camper123@db:5432/camper",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -----------------------------------------------------------------------------
# Create tables
# -----------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# -----------------------------------------------------------------------------
# Conditionally create GIST index
# -----------------------------------------------------------------------------
# Check if index idx_users_locations exists if not then create it.
# It creates a GIST index on User.location in the users table.
# GIST index ensures ST_DWithin and ST_Distance queries scale.
with engine.begin() as conn:
    conn.execute(
        text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relname = 'idx_users_location'
            ) THEN
                CREATE INDEX idx_users_location ON users USING gist (location);
            END IF;
        END$$;
    """)
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
