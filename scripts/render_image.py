#!/usr/bin/env python3
"""
smp.json / rec.json 을 읽어서 네이버 블로그 위젯에 쓸 수 있는 카드 이미지(widget.png)를 만든다.

왜 이미지로 만드나요?
네이버 블로그의 "위젯 직접등록"은 <a href='...'><img src='...'></a> 형태만 지원하고
iframe이나 script는 "등록이 지원되지 않는 위젯코드입니다" 라며 막습니다. 그래서 살아있는
페이지 대신, 매시간 새로 그려진 "그림"을 올려두고 그 그림 주소를 위젯에 넣는 방식으로
우회합니다. 블로그 방문자가 그림을 볼 때마다 최신 그림을 받아오므로, 결과적으로 값이
새로고침되는 것처럼 보입니다.
"""
import json
import os
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMP_PATH = os.path.join(BASE_DIR, "smp.json")
REC_PATH = os.path.join(BASE_DIR, "rec.json")
OUT_PATH = os.path.join(BASE_DIR, "widget.png")

W, H = 170, 220

# GitHub Actions ubuntu-latest에서는 "sudo apt-get install -y fonts-noto-cjk" 로 아래 경로에 설치됩니다.
FONT_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

_font_cache = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        path = FONT_BOLD if bold else FONT_REGULAR
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def fmt_num(n):
    if n is None:
        return "-"
    try:
        n = float(n)
        if n == int(n):
            return f"{int(n):,}"
        return f"{n:,.2f}"
    except Exception:
        return str(n)


def fmt_date(yyyymmdd):
    if not yyyymmdd or len(str(yyyymmdd)) != 8:
        return ""
    s = str(yyyymmdd)
    return f"{s[0:4]}.{s[4:6]}.{s[6:8]}"


def fmt_time_kst(iso):
    if not iso:
        return "-"
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        kst = dt.astimezone(timezone(timedelta(hours=9)))
        return kst.strftime("%H:%M")
    except Exception:
        return "-"


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_gradient_bg(draw, w, h, top, bottom):
    for y in range(h):
        t = y / max(h - 1, 1)
        draw.line([(0, y), (w, y)], fill=lerp_color(top, bottom, t))


def render(smp, rec, out_path):
    img = Image.new("RGB", (W, H), (20, 33, 61))
    draw = ImageDraw.Draw(img)
    draw_gradient_bg(draw, W, H, (20, 33, 61), (27, 42, 74))

    pad = 9
    y = 10

    draw.text((pad, y), "전력시장 가격", font=font(12, bold=True), fill=(159, 208, 255))
    mode = smp.get("mode") or rec.get("mode") or "manual"
    dot_color = (74, 222, 128) if mode == "auto" else (250, 204, 21)
    draw.ellipse((W - pad - 8, y + 3, W - pad, y + 11), fill=dot_color)
    y += 22

    def draw_row(y, label, badge_text, price_text, unit, meta_text):
        row_h = 62
        draw.rounded_rectangle((pad - 2, y, W - pad + 2, y + row_h), radius=6, fill=(44, 58, 92))

        ty = y + 6
        draw.text((pad + 3, ty), label, font=font(10), fill=(184, 196, 221))
        f8 = font(8)
        bw = draw.textlength(badge_text, font=f8)
        badge_x = W - pad - 6 - bw - 6
        draw.rounded_rectangle((badge_x, ty - 1, badge_x + bw + 6, ty + 11), radius=3, fill=(66, 82, 120))
        badge_color = (159, 208, 255) if badge_text == "자동" else (250, 204, 21)
        draw.text((badge_x + 3, ty), badge_text, font=f8, fill=badge_color)

        ty += 16
        f17 = font(17, bold=True)
        draw.text((pad + 3, ty), price_text, font=f17, fill=(255, 255, 255))
        pw = draw.textlength(price_text, font=f17)
        draw.text((pad + 3 + pw + 3, ty + 5), unit, font=font(9), fill=(184, 196, 221))

        ty += 24
        draw.text((pad + 3, ty), meta_text, font=font(8), fill=(136, 148, 172))

        return y + row_h + 8

    smp_price = fmt_num(smp.get("price"))
    smp_unit = smp.get("unit") or "원/kWh"
    smp_badge = "자동" if smp.get("mode") == "auto" else "수동"
    if smp.get("price") is not None:
        smp_meta = (
            f"{fmt_date(smp.get('tradeDay'))} {smp.get('tradHour')}시 기준"
            if smp.get("tradHour") is not None
            else fmt_date(smp.get("tradeDay"))
        )
    else:
        smp_meta = "아직 값이 없어요"
    y = draw_row(y, "SMP (육지)", smp_badge, smp_price, smp_unit, smp_meta)

    rec_price = fmt_num(rec.get("landAvgPrc"))
    rec_unit = rec.get("unit") or "원"
    rec_badge = "자동" if rec.get("mode") == "auto" else "수동"
    rec_meta = f"{fmt_date(rec.get('bzDd'))} 거래일 기준" if rec.get("landAvgPrc") is not None else "아직 값이 없어요"
    y = draw_row(y, "REC 현물 평균가", rec_badge, rec_price, rec_unit, rec_meta)

    footer_smp = f"SMP {fmt_time_kst(smp.get('updatedAt'))}" if smp.get("updatedAt") else "SMP -"
    footer_rec = f"REC {fmt_time_kst(rec.get('updatedAt'))}" if rec.get("updatedAt") else "REC -"
    draw.text((pad, H - 16), f"갱신 · {footer_smp} / {footer_rec}", font=font(7), fill=(107, 120, 150))

    img.save(out_path)


def main():
    smp = load_json(SMP_PATH, {})
    rec = load_json(REC_PATH, {})
    render(smp, rec, OUT_PATH)
    print(f"widget.png 생성 완료 -> {OUT_PATH}")


if __name__ == "__main__":
    main()
