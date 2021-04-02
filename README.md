# SSF
---
## 지원금 추천 프로그램  
다양한 지원금, 장학금 정보를 사용자에게 제공하는 프로그램  
사용자가 원하는 지원 자격을 설정하여 그에 해당하는 지원금 리스트를 출력  

---
## 지원금 목록 Crawling  
사용한 라이브러리 : selenium, pandas, re, sqlite3  
url : 온라인 청년센터 (https://www.youthcenter.go.kr/main.do)  
  
---
## Chromedriver 다운 받기  
url : https://chromedriver.chromium.org/downloads
  
---
## SQLite 저장  
### columns
    - index : 인덱스  
    - title : 지원금 이름  
    - agemin, agemax : 지원 가능 나이 범위 (만)
    - areacode : 시도 code (area-code-df.csv 기준)
    - arealist : 지원 가능 시군구 list ( 공백 : 제한 없음 ) 
    - work : 학력 기준 (고교 졸업, 대학 재학, 대학 졸업 등)
    - type : 생활 복지, 취업 지원, 주거 금융 등
    - area : 지역 및 소득분위
    - host : 주최
    - href : 관련 사이트 url

