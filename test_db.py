import psycopg2
import sys

# Test PostgreSQL connection
db_url = "postgresql://xgenai_db_user:F6x7ohdE2KZ5LMHPfJzQ9muaDkTJY2eC@dpg-d4laq0je5dus73fm14c0-a.oregon-postgres.render.com:5432/xgenai_db?sslmode=require"

try:
    print("Testing PostgreSQL connection...")
    print(f"URL: {db_url[:50]}...")
    
    conn = psycopg2.connect(db_url)
    print("✅ Connection successful!")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
    # Test if users table exists
    cur.execute("SELECT to_regclass('public.users');")
    result = cur.fetchone()[0]
    if result:
        print("✅ Users table exists")
        
        # Count users
        cur.execute("SELECT COUNT(*) FROM users;")
        count = cur.fetchone()[0]
        print(f"Total users: {count}")
    else:
        print("⚠️ Users table does NOT exist - need to create it")
    
    conn.close()
    print("✅ Test complete!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
