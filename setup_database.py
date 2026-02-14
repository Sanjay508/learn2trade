# setup_database.py
import psycopg2
import os
import urllib.parse

def setup_database():
    """Create all database tables"""
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    # Fix for postgres:// vs postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    try:
        # Parse the URL
        result = urllib.parse.urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=result.hostname,
            port=result.port or 5432,
            database=result.path[1:],
            user=result.username,
            password=result.password
        )
        cur = conn.cursor()
        print("✅ Connected to database")
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(256) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
        """)
        print("✅ users table created")
        
        # Create portfolios table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                cash DECIMAL(15,2) DEFAULT 100000.00,
                total_value DECIMAL(15,2) DEFAULT 100000.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ portfolios table created")
        
        # Create holdings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS holdings (
                id SERIAL PRIMARY KEY,
                portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
                symbol VARCHAR(20) NOT NULL,
                company_name VARCHAR(200),
                shares INTEGER NOT NULL,
                avg_price DECIMAL(15,2) NOT NULL,
                total_invested DECIMAL(15,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ holdings table created")
        
        # Create orders table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
                symbol VARCHAR(20) NOT NULL,
                company_name VARCHAR(200),
                action VARCHAR(10) NOT NULL,
                shares INTEGER NOT NULL,
                price DECIMAL(15,2) NOT NULL,
                total DECIMAL(15,2) NOT NULL,
                profit_loss DECIMAL(15,2),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ orders table created")
        
        # Create watchlists table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS watchlists (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                symbol VARCHAR(20) NOT NULL,
                company_name VARCHAR(200),
                notes TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, symbol)
            );
        """)
        print("✅ watchlists table created")
        
        # Create learning_progress table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS learning_progress (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                course_category VARCHAR(100) NOT NULL,
                lesson_name VARCHAR(200) NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_category, lesson_name)
            );
        """)
        print("✅ learning_progress table created")
        
        # Commit all changes
        conn.commit()
        
        # Verify tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        print("\n📋 Tables in database:")
        for table in tables:
            print(f"   - {table[0]}")
        
        cur.close()
        conn.close()
        print("\n🎉 Database setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

if __name__ == "__main__":
    setup_database()