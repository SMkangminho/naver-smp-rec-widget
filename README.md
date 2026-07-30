# 네이버 블로그 SMP·REC 가격 위젯

네이버 블로그 사이드바에 SMP(계통한계가격)와 REC(신재생에너지 공급인증서 현물시장) 가격을
보여주는 위젯입니다.

## 왜 "그림(이미지)" 방식인가요?

원래는 살아있는 웹페이지를 iframe으로 넣으려고 했는데, 네이버 블로그의 "위젯 직접등록"이
`<iframe>`이나 `<script>`가 들어간 코드는 **"등록이 지원되지 않는 위젯코드입니다"** 라며
막는다는 걸 실제로 확인했습니다. 네이버 위젯 직접등록이 지원하는 형태는 딱 이것뿐입니다.

```html
<a href='링크경로' target='_blank'><img src='이미지경로'></a>
```

그래서 이 프로젝트는 **매시간(또는 값을 바꿀 때마다) "숫자가 적힌 그림"을 새로 그려서
GitHub에 저장**해두고, 그 그림 주소를 위젯에 넣는 방식으로 만들었습니다. 블로그 방문자가
페이지를 열 때마다 최신 그림을 받아오므로, 결과적으로 값이 계속 갱신되는 것처럼 보입니다.

## 꼭 알아두어야 할 점

- SMP는 1시간 단위, REC는 거래일(하루) 단위로 갱신되는 값이라, 초 단위로 바뀌는
  "진짜 실시간"은 아닙니다.
- 지금(2026-07-30 기준) 공공데이터포털이 2026-07-29 19:00 ~ 2026-08-02 18:00 사이
  시스템 개편 작업 중이라 로그인/신규 열쇠 발급이 막혀 있습니다. 그래서 처음엔 손으로
  숫자를 넣는 "수동 모드"로 시작하고, 8월 2일 이후 열쇠를 받으면 "자동 모드"로 전환합니다.

## 두 가지 모드

### 모드 A — 수동 (지금 바로 가능)
GitHub 저장소 안의 `smp.json`, `rec.json` 파일을 하루 한두 번 직접 열어서 숫자만 바꿔주면,
GitHub Actions가 그 값으로 자동으로 `widget.png` 그림을 새로 그려줍니다. 코딩 지식이 필요 없습니다.

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
4. 저장하면 GitHub Actions가 자동으로 실행되어 `widget.png`를 새로 그려줍니다 (1분 내외).
   저장소 **Actions** 탭에서 초록색 체크가 뜨면 완료된 거예요. 블로그를 새로고침하면
   바뀐 그림이 보입니다.

### 모드 B — 자동 (열쇠를 받은 뒤)
1. 공공데이터포털(data.go.kr)에서 아래 두 API를 신청하고 **일반 인증키(Decoding)** 값을 받습니다.
   - 계통한계가격조회: https://www.data.go.kr/data/15076302/openapi.do
   - REC 현물시장 정보: https://www.data.go.kr/data/15099762/openapi.do
2. 저장소 **Settings > Secrets and variables > Actions > New repository secret**
   - Name: `DATA_GO_KR_KEY`
   - Value: 받은 인증키
3. 그게 끝입니다. 저장소 **Actions** 탭의 "Update SMP/REC widget image" 워크플로가
   매시간 자동으로 `smp.json`, `rec.json`, `widget.png`를 갱신하기 시작합니다. 그림 속
   배지도 "수동"에서 "자동"으로 바뀝니다.

> 열쇠를 등록하기 전까지는 `scripts/fetch_data.py`가 스스로 "아직 키 없음"을 감지하고
> 아무 것도 건드리지 않으므로, 수동으로 고쳐둔 값이 자동 실행 때문에 지워지는 일은 없습니다.

## 설정 순서 (처음 한 번만)

### 1) GitHub 저장소 만들기
1. GitHub에서 새 저장소 생성 (예: `naver-smp-rec-widget`), **Public**으로 설정
   (Private이면 이미지 주소가 외부에서 안 보입니다)
2. 이 폴더(zip 압축 해제한 것) 안의 파일을 그대로 업로드
   - 저장소를 막 만들면 파일이 없어서 "Add file" 버튼 대신 **"uploading an existing file"**
     같은 링크가 보일 수 있습니다. 그걸 눌러 파일을 끌어다 놓으면 됩니다.
   - `index.html`, `data.json` 파일은 이제 쓰지 않으니 업로드하지 않아도 됩니다.

### 2) 위젯 그림이 잘 만들어지는지 확인
1. 저장소 **Actions** 탭 클릭
2. "Update SMP/REC widget image" 워크플로 선택 → **Run workflow** 버튼으로 한 번 실행
3. 완료되면(초록 체크) 저장소 파일 목록에서 `widget.png`를 클릭해 그림이 잘 나오는지 확인

### 3) 네이버 블로그에 위젯 등록
1. 블로그 관리 > 꾸미기 설정 > **레이아웃·위젯 설정**
2. 오른쪽 위젯 목록에서 **위젯 직접등록** 클릭
3. 아래 코드에서 `계정명` 두 군데를 내 GitHub 계정 이름으로 바꿔서 붙여넣기
   ```html
   <a href='https://github.com/계정명/naver-smp-rec-widget' target='_blank'>
   <img src='https://raw.githubusercontent.com/계정명/naver-smp-rec-widget/main/widget.png'></a>
   ```
   (raw.githubusercontent.com 주소는 저장소가 **Public**일 때만 외부에서 보입니다)
4. 등록 후 레이아웃에서 위젯을 원하는 위치로 옮기고 저장

## 파일 구성
```
naver-smp-rec-widget/
├─ widget.png                    # 실제로 네이버 위젯에 뜨는 그림 (자동으로 계속 새로 그려짐)
├─ smp.json                      # SMP 값 (수동으로 고치거나, 자동으로 갱신됨)
├─ rec.json                      # REC 값 (수동으로 고치거나, 자동으로 갱신됨)
├─ scripts/fetch_data.py         # (모드 B) API 호출 후 두 json 파일을 갱신
├─ scripts/render_image.py       # json 값을 읽어서 widget.png 그림을 그림
└─ .github/workflows/update-data.yml   # 매시간 + json 수정 시 자동 실행
```

## 참고 / 한계
- 공공데이터포털 개발계정은 API별 일일 트래픽이 보통 100건으로 제한되어 있습니다.
  매시 1회(1일 24회) 호출이므로 여유는 충분합니다.
- SMP API는 제공기관에서 "추후 삭제 예정"이라고 안내하고 있어, 향후 후속 API로 교체가
  필요할 수 있습니다.
- REC 값은 육지·제주 통합이 아닌 **육지 평균가(landAvgPrc)** 를 기본으로 표시합니다.
- raw.githubusercontent.com은 짧은 캐시(수 분)를 적용하므로, 그림이 바뀐 직후 블로그에
  바로 반영 안 되면 몇 분 뒤 새로고침해보세요.
