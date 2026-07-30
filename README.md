# 네이버 블로그 SMP·REC 가격 위젯

네이버 블로그 사이드바에 SMP(계통한계가격)와 REC(신재생에너지 공급인증서 현물시장) 가격을
보여주는 위젯입니다. **처음엔 손으로 숫자를 입력하는 "수동 모드"로 시작하고, 나중에
공공데이터포털 열쇠(인증키)를 등록하면 저절로 "자동 모드"로 바뀌는 구조**입니다. 코드를
다시 만들 필요 없이, 같은 저장소를 계속 쓰면 됩니다.

## 꼭 알아두어야 할 점

- 네이버 블로그는 **포스트 본문 안에서는 script/iframe을 걸러냅니다.** 이 위젯은 본문이 아니라
  블로그 관리 화면의 **"위젯 만들기"(사이드바)** 기능으로만 넣을 수 있습니다.
- SMP는 1시간 단위, REC는 거래일(하루) 단위로 갱신되는 값이라, 초 단위로 바뀌는
  "진짜 실시간"은 아닙니다.
- 지금(2026-07-30 기준) 공공데이터포털이 2026-07-29 19:00 ~ 2026-08-02 18:00 사이
  시스템 개편 작업 중이라 로그인/신규 열쇠 발급이 막혀 있습니다. 그래서 처음엔 수동 모드로
  시작하고, 8월 2일 이후 열쇠를 받으면 자동 모드로 전환합니다.

## 두 가지 모드

### 모드 A — 수동 (지금 바로 가능)
GitHub 저장소 안의 `smp.json`, `rec.json` 파일을 하루 한두 번 직접 열어서 숫자만 바꿔주는
방식입니다. 코딩 지식이 필요 없습니다.

1. 아래 사이트에서 오늘의 숫자를 확인합니다.
   - SMP(육지, 시간별): https://epsis.kpx.or.kr/epsisnew/selectEkmaSmpShdChart.do?menuId=040202
   - REC(현물시장): https://recloud.energy.or.kr 또는 전력거래소 공지자료
2. GitHub 저장소에서 `smp.json` 파일을 열고 오른쪽 위 연필(✏️) 아이콘 클릭 → 아래처럼
   숫자만 바꿔서 저장(Commit changes)
   ```json
   {
     "mode": "manual",
     "updatedAt": "2026-07-30T10:00:00+09:00",
     "areaLabel": "육지",
     "price": 118.9,
     "unit": "원/kWh",
     "tradeDay": "20260730",
     "tradHour": 10
   }
   ```
3. `rec.json`도 같은 방식으로 바꿉니다.
   ```json
   {
     "mode": "manual",
     "updatedAt": "2026-07-30T10:00:00+09:00",
     "bzDd": "20260729",
     "landAvgPrc": 68500,
     "clsPrc": 68000,
     "landHgPrc": 69000,
     "landLwPrc": 68000,
     "unit": "원"
   }
   ```
4. 저장하면 몇 초~몇 분 안에 블로그 위젯에도 바뀐 숫자가 보입니다. 위젯에는 "수동" 배지가 표시됩니다.

### 모드 B — 자동 (열쇠를 받은 뒤)
1. 공공데이터포털(data.go.kr)에서 아래 두 API를 신청하고 **일반 인증키(Decoding)** 값을 받습니다.
   - 계통한계가격조회: https://www.data.go.kr/data/15076302/openapi.do
   - REC 현물시장 정보: https://www.data.go.kr/data/15099762/openapi.do
2. 저장소 **Settings > Secrets and variables > Actions > New repository secret**
   - Name: `DATA_GO_KR_KEY`
   - Value: 받은 인증키
3. 그게 끝입니다. 저장소 **Actions** 탭의 "Update SMP/REC data" 워크플로가 매시간 자동으로
   `smp.json`, `rec.json`을 덮어쓰기 시작합니다. 위젯의 배지도 "수동"에서 "자동"으로 바뀝니다.
   (한 번 수동으로 Run workflow를 눌러서 바로 확인해볼 수도 있습니다.)

> 열쇠를 등록하기 전까지는 `scripts/fetch-data.js`가 스스로 "아직 키 없음"을 감지하고
> 아무 것도 건드리지 않으므로, 수동으로 고쳐둔 값이 자동 실행 때문에 지워지는 일은 없습니다.

## 설정 순서 (처음 한 번만)

### 1) GitHub 저장소 만들기
1. GitHub에서 새 저장소 생성 (예: `naver-smp-rec-widget`), Public으로 설정
2. 이 폴더(zip 압축 해제한 것) 안의 파일을 그대로 업로드
   - 저장소를 막 만들면 파일이 없어서 "Add file" 버튼 대신 **"uploading an existing file"**
     같은 링크가 보일 수 있습니다. 그걸 눌러 파일을 끌어다 놓으면 됩니다.
   - `data.json` 파일은 이제 쓰지 않으니 업로드하지 않아도 됩니다.

### 2) GitHub Pages 켜기
1. 저장소 **Settings > Pages**
2. Source를 `main` 브랜치 / `/ (root)`로 설정 후 저장
3. 잠시 후 `https://<계정명>.github.io/naver-smp-rec-widget/` 주소가 생깁니다. 이 주소를
   복사해두세요.

### 3) 네이버 블로그에 위젯 등록
1. 블로그 관리 > 꾸미기 설정 > **레이아웃·위젯 설정**
2. 오른쪽 위젯 목록에서 **위젯 직접등록** 클릭
3. 아래 코드에서 `src` 주소를 2)에서 만든 내 주소로 바꿔서 붙여넣기
   ```html
   <iframe src="https://<계정명>.github.io/naver-smp-rec-widget/"
           width="170" height="200" frameborder="0" scrolling="no"
           style="border:none;"></iframe>
   ```
   (네이버 블로그 위젯 최대 크기는 가로 170 x 세로 600px입니다.)
4. 등록 후 레이아웃에서 위젯을 원하는 위치로 옮기고 저장

## 파일 구성
```
naver-smp-rec-widget/
├─ index.html                    # 실제 iframe에 들어갈 위젯 화면
├─ smp.json                      # SMP 값 (수동으로 고치거나, 자동으로 갱신됨)
├─ rec.json                      # REC 값 (수동으로 고치거나, 자동으로 갱신됨)
├─ scripts/fetch-data.js         # (모드 B) API 호출 후 두 파일 갱신하는 Node 스크립트
└─ .github/workflows/update-data.yml   # 매시 5분 자동 실행 설정 (키 없으면 그냥 넘어감)
```

## 참고 / 한계
- 공공데이터포털 개발계정은 API별 일일 트래픽이 보통 100건으로 제한되어 있습니다.
  매시 1회(1일 24회) 호출이므로 여유는 충분합니다.
- SMP API는 제공기관에서 "추후 삭제 예정"이라고 안내하고 있어, 향후 후속 API로 교체가
  필요할 수 있습니다.
- REC 값은 육지·제주 통합이 아닌 **육지 평균가(landAvgPrc)** 를 기본으로 표시합니다.
