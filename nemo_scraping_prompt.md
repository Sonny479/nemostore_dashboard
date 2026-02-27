## 1) HTTP 요청정보와 헤더
Request URL
https://www.nemoapp.kr/api/store/search-list?CompletedOnly=false&NELat=37.52748221586911&NELng=127.03858901633667&SWLat=37.51838723436393&SWLng=127.01654907038149&Zoom=16&SortBy=29&PageIndex=0
Request Method
GET
Status Code
200 OK
Remote Address
3.168.178.48:443
Referrer Policy
strict-origin-when-cross-origin

referer
https://www.nemoapp.kr/store
sec-ch-ua
"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"
sec-ch-ua-mobile
?0
sec-ch-ua-platform
"Windows"
sec-fetch-dest
empty
sec-fetch-mode
cors
sec-fetch-site
same-origin
user-agent
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36

## 2) Payload 정보
CompletedOnly=false&NELat=37.52748221586911&NELng=127.03858901633667&SWLat=37.51838723436393&SWLng=127.01654907038149&Zoom=16&SortBy=29&PageIndex=0

## 3) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)
items 하위 모든 정보 수집
```json
{
    "items": [
        {
```
## 4) 한페이지가 성공적으로 수집되는지 확인하기

## 5) 해당 수집 내용을 바탕으로 sqlitedb 스키마를 구성하고 해당 nemostore.db에 데이터를 1~5페이지까지 저장할 것, 이태원동과 신사동을 구분지을 수 있게 컬럼 구성할 것