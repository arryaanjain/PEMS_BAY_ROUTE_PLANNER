"""Small helper to create database tables declared in models.

Run this once after you configure DATABASE_URL to create tables:
    python create_tables.py
"""
from app.database import engine, Base
from app import models


def main():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done")


if __name__ == "__main__":
    main()
