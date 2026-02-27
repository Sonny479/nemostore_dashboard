import requests
import json
import os

def probe_api():
    url = "https://www.nemoapp.kr/api/store/search-list"
    params = {
        "CompletedOnly": "false",
        "NELat": "37.54730730353837",
        "NELng": "127.02759998013038",
        "SWLat": "37.529109173089566",
        "SWLng": "126.9835164412612",
        "Zoom": "15",
        "SortBy": "29",
        "PageIndex": "0"
    }
    
    headers = {
        "referer": "https://www.nemoapp.kr/store",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }
    
    print(f"Requesting: {url} with params {params}")
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # 데이터 폴더 생성
        os.makedirs("data", exist_ok=True)
        # 샘플 응답 저장
        with open("data/sample_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        if "items" in data and len(data["items"]) > 0:
            first_item = data["items"][0]
            print("\n--- First Item Fields ---")
            for key, value in first_item.items():
                print(f"{key}: {type(value).__name__}")
            print(f"\nTotal items on page 0: {len(data['items'])}")
        else:
            print("No items found in response.")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    probe_api()
