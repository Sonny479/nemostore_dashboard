import sqlite3
import os

def verify_data(db_path):
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 전체 개수 확인
        cursor.execute("SELECT count(*) FROM items")
        count = cursor.fetchone()[0]
        print(f"Total records in 'items' table: {count}")
        
        # 지역별 개수 확인
        print("\n--- Records by Region ---")
        cursor.execute("SELECT region, count(*) FROM items GROUP BY region")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Region: {row[0] if row[0] else 'None'}, Count: {row[1]}")
        
        # 샘플 데이터 확인
        print("\n--- Sample Data (Region, Title, Deposit, MonthlyRent) ---")
        cursor.execute("SELECT region, title, deposit, monthlyRent FROM items LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(f"[{row[0]}] {row[1]} | Deposit: {row[2]}, Rent: {row[3]}")
            
    except Exception as e:
        print(f"Error verifying data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_data("data/nemostore.db")
