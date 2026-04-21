from app.core.database import Base, engine
from app.scripts.seed import seed_db


def set_up():
    # Create database tables if absent.
    Base.metadata.create_all(bind=engine)

    # Seed data to the database.
    seed_db()

if __name__ == "__main__":
    set_up()
