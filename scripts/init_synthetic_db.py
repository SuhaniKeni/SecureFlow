import os
from secureflow.db.database import init_db, SessionLocal, engine
from secureflow.db.synthetic_generator import generate_synthetic_database

def main():
    print("=== Initializing SecureFlow Synthetic Database (Stage 5.3) ===")
    from secureflow.db.models import Base
    Base.metadata.drop_all(bind=engine)
    init_db(engine)
    
    session = SessionLocal()
    try:
        generate_synthetic_database(session, seed=42)
    finally:
        session.close()
        
    print("=== Database Setup & Synthetic Seeding Complete ===")

if __name__ == "__main__":
    main()
