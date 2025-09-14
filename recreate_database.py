"""
Recreate database with correct schema
"""
import os
from app.core.database import Base, engine

def recreate_database():
    """Recreate database with correct schema"""
    print("🗑️ Dropping existing database...")
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped")
    
    # Create all tables with new schema
    print("🔨 Creating new database schema...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database recreated with correct schema")
    
    print("🎉 Database recreation completed!")

if __name__ == "__main__":
    recreate_database()

