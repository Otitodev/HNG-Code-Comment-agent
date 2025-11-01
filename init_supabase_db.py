#!/usr/bin/env python3
"""
Initialize Supabase database with required tables
Run this script after setting up your Supabase credentials
"""
import asyncio
import os
from sqlalchemy import text
from app.db import engine, Base
from app.models import DailyTip, CodeRequest, UserLanguagePreference

async def init_database():
    """Initialize the database with all tables"""
    try:
        print("🚀 Initializing Supabase database...")
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully!")
        
        # Test the connection and show table info
        async with engine.connect() as conn:
            print("\n🔍 Verifying tables...")
            
            # Check if we're using PostgreSQL or SQLite
            db_url = str(engine.url)
            is_postgresql = 'postgresql' in db_url
            
            if is_postgresql:
                # PostgreSQL queries
                result = await conn.execute(
                    text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_type = 'BASE TABLE'
                        ORDER BY table_name
                    """)
                )
            else:
                # SQLite queries
                result = await conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                )
            
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Created tables: {', '.join(tables)}")
            
            # Show table structures
            for table in tables:
                if is_postgresql:
                    result = await conn.execute(
                        text(f"""
                            SELECT column_name, data_type, is_nullable
                            FROM information_schema.columns 
                            WHERE table_name = '{table}' 
                            AND table_schema = 'public'
                            ORDER BY ordinal_position
                        """)
                    )
                    columns = result.fetchall()
                    print(f"\n📊 Table '{table}':")
                    for col in columns:
                        nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                        print(f"   - {col[0]}: {col[1]} ({nullable})")
                else:
                    result = await conn.execute(
                        text(f"PRAGMA table_info({table})")
                    )
                    columns = result.fetchall()
                    print(f"\n📊 Table '{table}':")
                    for col in columns:
                        nullable = "NULL" if col[3] == 0 else "NOT NULL"
                        print(f"   - {col[1]}: {col[2]} ({nullable})")
        
        print("\n🎉 Supabase database initialization completed!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("❌ DATABASE_URL not set in environment variables")
        print("Please update your .env file with Supabase credentials")
        exit(1)
    
    if "supabase.co" not in os.getenv("DATABASE_URL", ""):
        print("⚠️  Warning: DATABASE_URL doesn't appear to be a Supabase URL")
        print("Make sure you're using the correct Supabase database connection string")
    
    asyncio.run(init_database())