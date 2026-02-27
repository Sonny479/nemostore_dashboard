import requests
import json
import sqlite3
import os
import time

def setup_db(db_path):
    """SQLite 데이터베이스 및 테이블 초기화 및 컬럼 추가"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블 생성 (region 컬럼 포함)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY,
        region TEXT,
        articleType INTEGER,
        buildingManagementSerialNumber TEXT,
        number INTEGER,
        previewPhotoUrl TEXT,
        smallPhotoUrls TEXT,
        originPhotoUrls TEXT,
        businessLargeCode INTEGER,
        businessLargeCodeName TEXT,
        businessMiddleCode INTEGER,
        businessMiddleCodeName TEXT,
        priceType INTEGER,
        priceTypeName TEXT,
        deposit INTEGER,
        monthlyRent INTEGER,
        premium INTEGER,
        sale INTEGER,
        maintenanceFee INTEGER,
        floor INTEGER,
        groundFloor INTEGER,
        size REAL,
        title TEXT,
        firstDeposit INTEGER,
        firstMonthlyRent INTEGER,
        firstPremium INTEGER,
        nearSubwayStation TEXT,
        viewCount INTEGER,
        favoriteCount INTEGER,
        isMoveInDate BOOLEAN,
        createdDateUtc TEXT,
        editedDateUtc TEXT,
        state INTEGER,
        areaPrice INTEGER
    )
    """)
    
    # 기존 테이블에 region 컬럼이 없는 경우 추가 (마이그레이션)
    cursor.execute("PRAGMA table_info(items)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'region' not in columns:
        print("Adding 'region' column and migrating existing data...")
        cursor.execute("ALTER TABLE items ADD COLUMN region TEXT")
        # 기존 데이터는 이태원으로 설정
        cursor.execute("UPDATE items SET region = 'itaewon' WHERE region IS NULL")
        
    conn.commit()
    return conn

def fetch_and_save(conn, region_name, coords, max_pages=10):
    """지정된 지역과 좌표로 데이터를 수집하여 DB에 저장"""
    url = "https://www.nemoapp.kr/api/store/search-list"
    headers = {
        "referer": "https://www.nemoapp.kr/store",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "\"Windows\"",
    }
    
    base_params = {
        "CompletedOnly": "false",
        "NELat": coords["NELat"],
        "NELng": coords["NELng"],
        "SWLat": coords["SWLat"],
        "SWLng": coords["SWLng"],
        "Zoom": coords["Zoom"],
        "SortBy": "29"
    }
    
    cursor = conn.cursor()
    total_inserted = 0
    
    print(f"\n--- Starting collection for region: {region_name} ---")
    
    for page in range(max_pages):
        print(f"[{region_name}] Fetching page {page}...")
        params = base_params.copy()
        params["PageIndex"] = str(page)
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            items = data.get("items", [])
            if not items:
                print(f"No more items found at page {page}. Stopping.")
                break
                
            for item in items:
                small_photos = json.dumps(item.get("smallPhotoUrls", []))
                origin_photos = json.dumps(item.get("originPhotoUrls", []))
                
                cursor.execute("""
                INSERT OR REPLACE INTO items (
                    id, region, articleType, buildingManagementSerialNumber, number, previewPhotoUrl,
                    smallPhotoUrls, originPhotoUrls, businessLargeCode, businessLargeCodeName,
                    businessMiddleCode, businessMiddleCodeName, priceType, priceTypeName,
                    deposit, monthlyRent, premium, sale, maintenanceFee, floor, groundFloor,
                    size, title, firstDeposit, firstMonthlyRent, firstPremium,
                    nearSubwayStation, viewCount, favoriteCount, isMoveInDate,
                    createdDateUtc, editedDateUtc, state, areaPrice
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get("id"), region_name, item.get("articleType"), item.get("buildingManagementSerialNumber"),
                    item.get("number"), item.get("previewPhotoUrl"), small_photos, origin_photos,
                    item.get("businessLargeCode"), item.get("businessLargeCodeName"),
                    item.get("businessMiddleCode"), item.get("businessMiddleCodeName"),
                    item.get("priceType"), item.get("priceTypeName"),
                    item.get("deposit"), item.get("monthlyRent"), item.get("premium"),
                    item.get("sale"), item.get("maintenanceFee"), item.get("floor"),
                    item.get("groundFloor"), item.get("size"), item.get("title"),
                    item.get("firstDeposit"), item.get("firstMonthlyRent"), item.get("firstPremium"),
                    item.get("nearSubwayStation"), item.get("viewCount"), item.get("favoriteCount"),
                    item.get("isMoveInDate"), item.get("createdDateUtc"), item.get("editedDateUtc"),
                    item.get("state"), item.get("areaPrice")
                ))
                total_inserted += 1
            
            conn.commit()
            print(f"[{region_name}] Page {page} saved. Total items: {total_inserted}")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
            
    print(f"--- Finished region: {region_name}. Total unique items stored/updated: {total_inserted} ---")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    db_file = "data/nemostore.db"
    
    regions = [
        # 신사/압구정/역삼 인근 지역 (요청하신 좌표)
        {
            "name": "shinsa",
            "coords": {
                "NELat": "37.52748221586911",
                "NELng": "127.03858901633667",
                "SWLat": "37.51838723436393",
                "SWLng": "127.01654907038149",
                "Zoom": "16"
            },
            "max_pages": 5
        }
    ]
    
    connection = setup_db(db_file)
    try:
        for reg in regions:
            fetch_and_save(connection, reg["name"], reg["coords"], reg["max_pages"])
    finally:
        connection.close()
