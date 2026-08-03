#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMP_PATH = os.path.join(BASE_DIR, "smp.json")
REC_PATH = os.path.join(BASE_DIR, "rec.json")

SERVICE_KEY = os.environ.get("DATA_GO_KR_KEY")


def http_get(url, retries=3, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as res:
                return res.read().decode("utf-8", errors="replace")
        except Exception as e:
            last_err = e
            print(f"  (http_get 시도 {attempt}/{retries} 실패: {e})")
            if attempt < retries:
                time.sleep(3)
    raise last_err


def fetch_smp():
    params = urllib.parse.urlencode({"ServiceKey": SERVICE_KEY, "areaCd": "1"})
    url = f"https://openapi.kpx.or.kr/openapi/smp1hToday/getSmp1hToday?{params}"
    text = http_get(url)

    m = re.search(r"<resultCode>(.*?)</resultCode>", text)
    if not m or m.group(1).strip() != "00":
        msg = re.search(r"<resultMsg>(.*?)</resultMsg>", text)
        raise RuntimeError(f"SMP API 오류: {msg.group(1) if msg else text[:200]}")

    items = re.findall(r"<item>([\s\S]*?)</item>", text)
    if not items:
        raise RuntimeError("SMP API: item 데이터 없음")

    latest = None
    for item in items:
        hour_m = re.search(r"<tradHour>(.*?)</tradHour>", item)
        smp_m = re.search(r"<smp>(.*?)</smp>", item)
        day_m = re.search(r"<tradeDay>(.*?)</tradeDay>", item)
        if not smp_m:
            continue
        try:
            hour = int(hour_m.group(1))
            smp = float(smp_m.group(1))
        except (ValueError, AttributeError):
            continue
        if latest is None or hour > latest["tradHour"]:
            latest = {"tradHour": hour, "smp": smp, "tradeDay": day_m.group(1) if day_m else None}

    if latest is None:
        raise RuntimeError("SMP API: 유효한 시간대 데이터 없음")

    return {
        "mode": "auto",
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "areaLabel": "육지",
        "price": latest["smp"],
        "unit": "원/kWh",
        "tradeDay": latest["tradeDay"],
        "tradHour": latest["tradHour"],
    }


def fetch_rec():
    params = urllib.parse.urlencode({
        "serviceKey": SERVICE_KEY,
        "pageNo": "1",
        "numOfRows": "1",
        "dataType": "json",
    })
    url = f"https://apis.data.go.kr/B552115/RecMarketInfo2/getRecMarketInfo2?{params}"
    text = http_get(url)
    data = json.loads(text)

    header = data.get("header") or (data.get("response") or {}).get("header")
    if not header or header.get("resultCode") != "00":
        raise RuntimeError(f"REC API 오류: {header.get('resultMsg') if header else text[:200]}")

    body = data.get("body") or (data.get("response") or {}).get("body") or {}
    items = ((body.get("items") or {}).get("item"))
    item = items[0] if isinstance(items, list) else items
    if not item:
        raise RuntimeError("REC API: item 데이터 없음")

    def to_num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    return {
        "mode": "auto",
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "bzDd": item.get("bzDd"),
        "landAvgPrc": to_num(item.get("landAvgPrc")),
        "clsPrc": to_num(item.get("clsPrc")),
        "landHgPrc": to_num(item.get("landHgPrc")),
        "landLwPrc": to_num(item.get("landLwPrc")),
        "unit": "원",
    }


def update_file(path, fetcher, label):
    try:
        data = fetcher()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"{label} 갱신 완료: {json.dumps(data, ensure_ascii=False)}")
    except Exception as e:
        print(f"{label} 갱신 실패: {e}", file=sys.stderr)


def main():
    if not SERVICE_KEY:
        print("DATA_GO_KR_KEY가 아직 설정되지 않았습니다. 자동 갱신을 건너뜁니다 (수동 모드 유지).")
        return
    update_file(SMP_PATH, fetch_smp, "SMP")
    update_file(REC_PATH, fetch_rec, "REC")


if __name__ == "__main__":
    main()
