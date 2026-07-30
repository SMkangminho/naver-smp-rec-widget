// SMP(계통한계가격) / REC(현물시장) 최신값을 공공데이터포털 API에서 가져와
// smp.json, rec.json 으로 각각 저장한다.
//
// 동작 방식:
//  - DATA_GO_KR_KEY 라는 비밀 열쇠(GitHub Secret)가 아직 없으면, 아무것도 하지 않고 조용히 끝난다.
//    (그동안은 사용자가 smp.json / rec.json을 직접 GitHub 화면에서 수정해서 씁니다 = "수동 모드")
//  - 나중에 DATA_GO_KR_KEY를 등록하면, 이 스크립트가 매시간 자동으로 두 파일을 덮어써서
//    "자동 모드"로 저절로 바뀐다. 코드를 따로 고칠 필요가 없다.

const fs = require("fs");
const path = require("path");

const SERVICE_KEY = process.env.DATA_GO_KR_KEY;
const SMP_PATH = path.join(__dirname, "..", "smp.json");
const REC_PATH = path.join(__dirname, "..", "rec.json");

if (!SERVICE_KEY) {
  console.log(
    "DATA_GO_KR_KEY가 아직 설정되지 않았습니다. 자동 갱신을 건너뜁니다 (수동 모드 유지)."
  );
  process.exit(0);
}

// --- SMP (계통한계가격, XML 응답) ---
async function fetchSmp() {
  const url = new URL("https://openapi.kpx.or.kr/openapi/smp1hToday/getSmp1hToday");
  url.searchParams.set("ServiceKey", SERVICE_KEY);
  url.searchParams.set("areaCd", "1"); // 육지

  const res = await fetch(url.toString());
  const text = await res.text();

  const resultCodeMatch = text.match(/<resultCode>(.*?)<\/resultCode>/);
  if (!resultCodeMatch || resultCodeMatch[1].trim() !== "00") {
    const msg = text.match(/<resultMsg>(.*?)<\/resultMsg>/);
    throw new Error(`SMP API 오류: ${msg ? msg[1] : text.slice(0, 200)}`);
  }

  const items = [...text.matchAll(/<item>([\s\S]*?)<\/item>/g)].map((m) => m[1]);
  if (items.length === 0) throw new Error("SMP API: item 데이터 없음");

  let latest = null;
  for (const item of items) {
    const tradHour = Number((item.match(/<tradHour>(.*?)<\/tradHour>/) || [])[1]);
    const smp = Number((item.match(/<smp>(.*?)<\/smp>/) || [])[1]);
    const tradeDay = (item.match(/<tradeDay>(.*?)<\/tradeDay>/) || [])[1];
    if (!Number.isFinite(smp)) continue;
    if (!latest || tradHour > latest.tradHour) latest = { tradHour, smp, tradeDay };
  }
  if (!latest) throw new Error("SMP API: 유효한 시간대 데이터 없음");

  return {
    mode: "auto",
    updatedAt: new Date().toISOString(),
    areaLabel: "육지",
    price: latest.smp,
    unit: "원/kWh",
    tradeDay: latest.tradeDay,
    tradHour: latest.tradHour,
  };
}

// --- REC 현물시장 정보 (JSON 응답) ---
async function fetchRec() {
  const url = new URL("https://apis.data.go.kr/B552115/RecMarketInfo2/getRecMarketInfo2");
  url.searchParams.set("serviceKey", SERVICE_KEY);
  url.searchParams.set("pageNo", "1");
  url.searchParams.set("numOfRows", "1");
  url.searchParams.set("dataType", "json");

  const res = await fetch(url.toString());
  const json = await res.json();

  const header = json?.header || json?.response?.header;
  if (!header || header.resultCode !== "00") {
    throw new Error(`REC API 오류: ${header ? header.resultMsg : JSON.stringify(json).slice(0, 200)}`);
  }

  const items = json?.body?.items?.item ?? json?.response?.body?.items?.item;
  const item = Array.isArray(items) ? items[0] : items;
  if (!item) throw new Error("REC API: item 데이터 없음");

  return {
    mode: "auto",
    updatedAt: new Date().toISOString(),
    bzDd: item.bzDd ?? null,
    landAvgPrc: item.landAvgPrc != null ? Number(item.landAvgPrc) : null,
    clsPrc: item.clsPrc != null ? Number(item.clsPrc) : null,
    landHgPrc: item.landHgPrc != null ? Number(item.landHgPrc) : null,
    landLwPrc: item.landLwPrc != null ? Number(item.landLwPrc) : null,
    unit: "원",
  };
}

async function updateFile(filePath, fetcher, label) {
  try {
    const data = await fetcher();
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + "\n");
    console.log(`${label} 갱신 완료:`, JSON.stringify(data));
  } catch (e) {
    console.error(`${label} 갱신 실패:`, e.message || e);
    // 실패하면 기존 파일은 그대로 둔다 (덮어쓰지 않음)
  }
}

(async () => {
  await updateFile(SMP_PATH, fetchSmp, "SMP");
  await updateFile(REC_PATH, fetchRec, "REC");
})();
