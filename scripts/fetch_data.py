#!/usr/bin/env python3
import json
import os
import re
import sys
import time
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
    # 기존 "계통한계가격조회"(openapi.kpx.or.kr) API는 GitHub Actions에서 접속이
    # 안 돼서(타임아웃), data.go.kr 게이트웨이(apis.data.go.kr)를 쓰는 신규 API
    # "계통한계가격 및 수요예측(하루전 발전계획용)"으로 전환.
    #
