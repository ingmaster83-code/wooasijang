#!/usr/bin/env python3
"""
generate_content.py - DeepSeek API로 시장별 소개문·팁·SEO 설명 생성

사용법:
  python scripts/generate_content.py           # description 없는 것만
  python scripts/generate_content.py --limit 10  # 10개만 테스트
  python scripts/generate_content.py --force    # 전체 재생성
"""
import json
import sys
import time
import re
import argparse
from pathlib import Path
import requests

sys.stdout.reconfigure(encoding='utf-8')

API_KEY_PATH = Path(r"C:\개인\개인 프로젝트\blogwriter_new\blogger_seo_bot\config\deepseek_api_key.txt")
DATA_FILE    = Path(__file__).parent.parent / "_data" / "markets.json"
DELAY        = 0.1

PROMPT_TMPL = """다음 전통시장 정보를 바탕으로 JSON 형식으로만 응답하세요. 다른 텍스트 없이 JSON만 출력하세요.
{{
  "description": "시장 소개문 200자 내외. 장날, 위치, 특산물을 자연스럽게 포함",
  "tip": "방문객을 위한 실용적인 팁 100자 내외",
  "seo_description": "네이버/구글 검색 최적화용 120자 이내 소개문"
}}
시장정보: {name} {region} {city} {days}일장 특산물: {specialties}"""


def get_api_key() -> str:
    return API_KEY_PATH.read_text(encoding="utf-8").strip()


def parse_json_response(text: str) -> dict:
    # 마크다운 코드블록 제거
    text = re.sub(r'```(?:json)?\s*', '', text).strip()
    text = text.rstrip('`').strip()
    return json.loads(text)


def generate_content(market: dict, api_key: str) -> dict:
    days_str = "·".join(str(d) for d in sorted(market.get("days", [])))
    specialties = "·".join(market.get("specialties", []))
    prompt = PROMPT_TMPL.format(
        name=market.get("name", ""),
        region=market.get("region", ""),
        city=market.get("city", ""),
        days=days_str,
        specialties=specialties,
    )
    resp = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.6,
        },
        timeout=30,
    )
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"].strip()
    return parse_json_response(raw)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    markets = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    api_key = get_api_key()

    targets = [m for m in markets if args.force or not m.get("description_text")]
    if args.limit:
        targets = targets[:args.limit]

    total = len(targets)
    print(f"생성 대상: {total}건\n")

    id_map = {m["id"]: i for i, m in enumerate(markets)}
    done = 0
    fail = 0

    for market in targets:
        try:
            content = generate_content(market, api_key)
            idx = id_map.get(market["id"])
            if idx is not None:
                markets[idx]["description_text"] = content.get("description", "")[:250]
                markets[idx]["tip"]              = content.get("tip", "")[:130]
                markets[idx]["seo_description"]  = content.get("seo_description", "")[:155]
            done += 1
            try:
                print(f"  [{done}/{total}] {market['name']}: {content.get('seo_description','')[:40]}...")
            except Exception:
                print(f"  [{done}/{total}] (출력 생략)")
        except Exception as e:
            fail += 1
            try:
                print(f"  [실패] {market.get('name','')}: {e}")
            except Exception:
                print(f"  [실패] (출력 불가)")

        if done % 20 == 0 and done > 0:
            DATA_FILE.write_text(
                json.dumps(markets, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            print(f"  [저장] {done}건 완료")

        time.sleep(DELAY)

    DATA_FILE.write_text(
        json.dumps(markets, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n완료: {done}건 성공, {fail}건 실패")


if __name__ == "__main__":
    main()
