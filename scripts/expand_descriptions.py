"""
markets.json의 description_text를 300자 이상으로 확장한다.
region, city, days, specialties를 활용해 풍부한 소개문을 생성.
"""
import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "_data" / "markets.json"

REGION_CONTEXT = {
    "경기도": "경기도는 수도권에 위치해 교통이 편리하며, 농업·임업·어업이 고루 발달한 지역입니다.",
    "강원도": "강원도는 태백산맥과 동해를 품은 청정 자연으로 유명하며, 신선한 산나물과 해산물이 풍부합니다.",
    "충청북도": "충청북도는 내륙 산지와 넓은 평야가 공존하는 지역으로, 다양한 농산물과 특산물이 생산됩니다.",
    "충청남도": "충청남도는 서해안을 끼고 있어 해산물이 풍부하고, 내포 평야의 쌀과 채소가 유명합니다.",
    "전라북도": "전라북도는 비옥한 호남 평야를 기반으로 쌀, 채소, 한우 등 다양한 농산물이 생산되는 풍요로운 곳입니다.",
    "전라남도": "전라남도는 남해안 다도해와 넓은 농경지를 가진 곳으로, 신선한 해산물과 풍성한 농산물로 유명합니다.",
    "경상북도": "경상북도는 내륙의 산악지대와 동해안이 어우러진 지역으로, 사과, 한우, 해산물 등이 특산물로 꼽힙니다.",
    "경상남도": "경상남도는 남해안을 따라 신선한 해산물이 풍부하며, 내륙의 비옥한 토지에서 다양한 농산물이 재배됩니다.",
    "제주도": "제주도는 화산 지형과 해양 기후 속에서 자란 독특한 농수산물로 유명하며, 관광과 농업이 조화를 이루는 섬입니다.",
    "전북특별자치도": "전북은 비옥한 호남 평야를 기반으로 쌀, 채소, 한우 등 다양한 농산물이 생산되는 풍요로운 곳입니다.",
    "세종특별자치시": "세종시는 행정 중심 복합도시로 성장하며, 인근 농촌 지역에서 신선한 로컬 농산물이 활발하게 거래됩니다.",
    "인천광역시": "인천은 서해안과 접한 항구 도시로, 신선한 해산물과 주변 농촌에서 생산된 채소·곡물이 풍부합니다.",
    "대전광역시": "대전은 충청도 교통의 요충지로, 주변 농촌에서 재배된 신선한 채소와 전통 먹거리가 장터에서 거래됩니다.",
    "광주광역시": "광주는 호남 문화의 중심지로, 전통 음식 문화가 깊이 뿌리내린 곳입니다. 지역 농산물과 전통 먹거리가 풍부합니다.",
    "울산광역시": "울산은 공업 도시이면서도 주변 농산어촌에서 생산된 신선한 식재료가 재래시장에서 활발히 거래됩니다.",
    "부산광역시": "부산은 항구 도시답게 신선한 해산물이 넘치고, 주변 경남 농촌에서 올라오는 싱싱한 채소와 과일도 풍부합니다.",
    "대구광역시": "대구는 경상도의 중심 도시로, 사과, 복숭아 등 과일과 지역 농산물이 재래시장에서 활발히 거래됩니다.",
}

SPECIALTIES_DESC = {
    "잣": "잣은 소나무 열매로, 고소한 맛과 영양이 뛰어나 건강 식재료로 인기가 높습니다.",
    "산나물": "청정 자연에서 자란 산나물은 봄철 대표 식재료로, 두릅·고사리·참나물 등 다양한 종류를 만나볼 수 있습니다.",
    "버섯": "표고버섯, 송이버섯, 능이버섯 등 향기롭고 신선한 버섯류는 이 지역 5일장의 대표 품목입니다.",
    "한우": "정성껏 키운 한우는 육질이 뛰어나고 맛이 깊어, 시장에서 인기 있는 고급 식재료입니다.",
    "쌀": "이 지역에서 재배된 품질 좋은 쌀은 밥맛이 뛰어나 인근 도시 소비자들에게도 인기를 끌고 있습니다.",
    "채소": "농민들이 직접 재배한 신선한 채소는 마트보다 저렴하고 품질이 좋아 장날마다 먼저 팔립니다.",
    "과일": "지역 특산 과일은 신선도와 당도가 높아 선물용으로도 인기가 많습니다.",
    "해산물": "인근 해역에서 갓 잡아온 신선한 해산물은 이 장터의 자랑거리입니다.",
    "도자기": "전통 도예 기법으로 만든 도자기와 생활 자기는 이 지역 문화유산의 일부입니다.",
    "약초": "청정 산지에서 채취한 약초와 한방 재료는 건강을 생각하는 방문객들에게 큰 인기를 끕니다.",
    "옹기": "전통 방식으로 구운 옹기는 발효 식품 보관에 탁월하며, 장인 정신이 담긴 공예품입니다.",
    "닭": "농가에서 직접 키운 토종닭과 오리는 씹는 맛이 좋고 육질이 탄탄해 장날 인기 품목입니다.",
    "오리": "농가에서 직접 키운 오리는 육질이 부드럽고 영양이 풍부한 인기 식재료입니다.",
    "인삼": "이 지역의 인삼은 뿌리가 굵고 유효 성분이 풍부해 전국적으로 품질을 인정받고 있습니다.",
    "고추": "햇볕이 잘 드는 밭에서 자란 빨간 고추는 매운 맛과 향이 뛰어나 김장철 필수 재료입니다.",
    "마늘": "이 지역에서 재배된 마늘은 알이 굵고 향이 진해 전국 각지에서 찾는 특산물입니다.",
    "사과": "일교차가 큰 기후에서 자란 사과는 당도와 색깔이 뛰어나 선물용으로 많이 찾습니다.",
    "배": "넓은 배 과수원에서 재배한 배는 과즙이 풍부하고 달콤해 장날 인기 품목입니다.",
    "복숭아": "빛깔이 곱고 향긋한 복숭아는 여름 제철 과일로 이 지역 농가의 주요 소득원입니다.",
    "포도": "당도 높고 싱싱한 포도는 여름~가을 장날에 빠지지 않는 인기 품목입니다.",
    "감": "가을에 수확한 홍시와 곶감은 달콤한 맛으로 장날 먼저 팔리는 인기 제철 과일입니다.",
}

DAYS_DESC = {
    (1, 6): "매월 1일과 6일, 11일, 16일, 21일, 26일",
    (2, 7): "매월 2일과 7일, 12일, 17일, 22일, 27일",
    (3, 8): "매월 3일과 8일, 13일, 18일, 23일, 28일",
    (4, 9): "매월 4일과 9일, 14일, 19일, 24일, 29일",
    (5, 0): "매월 5일과 10일, 15일, 20일, 25일, 30일",
}

def days_to_key(days: list) -> tuple:
    ds = sorted(days)
    if len(ds) == 2:
        return tuple(ds)
    return tuple(ds)

def make_days_str(days: list) -> str:
    ds = sorted(days)
    key = tuple(ds[:2]) if len(ds) >= 2 else tuple(ds)
    return DAYS_DESC.get(key, "·".join(str(d) for d in ds) + "일")

def expand_description(m: dict) -> str:
    name = m.get("name", "")
    region = m.get("region", "")
    city = m.get("city", "")
    days = m.get("days", [])
    specialties = m.get("specialties", [])
    existing = m.get("description_text", "")

    days_str = make_days_str(days)
    region_ctx = REGION_CONTEXT.get(region, f"{region}은 다양한 농산물과 특산물이 풍부한 지역입니다.")

    # 특산물 설명 최대 2개
    spec_descs = []
    for s in specialties[:3]:
        if s in SPECIALTIES_DESC:
            spec_descs.append(SPECIALTIES_DESC[s])
    spec_text = " ".join(spec_descs[:2]) if spec_descs else ""

    specialties_str = "·".join(specialties) if specialties else "각종 신선한 농산물"

    # 새 설명 조합
    if len(existing) >= 250:
        # 이미 충분히 길면 부가 정보만 추가
        extra = f"\n\n{region_ctx} {name}은 {days_str}에 열려, 주변 지역 주민들이 {specialties_str} 등 다양한 물건을 거래하는 소중한 생활 문화 공간입니다."
        if spec_text:
            extra += f" {spec_text}"
        return existing + extra
    else:
        # 기존 내용을 기반으로 새 설명 작성
        new_desc = (
            f"{name}은 {region} {city}에 위치한 전통 5일장으로, {days_str}에 장이 열립니다. "
            f"{region_ctx} "
            f"이 시장에서는 {specialties_str} 등 지역 특산물을 합리적인 가격에 만나볼 수 있습니다. "
        )
        if spec_text:
            new_desc += spec_text + " "
        new_desc += (
            f"지역 농민들이 직접 재배하고 수확한 신선한 먹거리를 저렴하게 구입할 수 있어, "
            f"장날이면 인근 주민들뿐 아니라 멀리서 찾아오는 방문객들로 활기가 넘칩니다. "
            f"전통 장터 특유의 인정 넘치는 분위기와 함께 지역 문화를 체험할 수 있는 공간입니다."
        )
        return new_desc


def main():
    markets = json.loads(DATA_FILE.read_text(encoding='utf-8'))
    updated = 0
    for m in markets:
        new_desc = expand_description(m)
        if len(new_desc) > len(m.get('description_text', '')):
            m['description_text'] = new_desc
            updated += 1
    DATA_FILE.write_text(json.dumps(markets, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"완료: {updated}개 시장 설명 확장")
    # 결과 통계
    lengths = [len(m.get('description_text','')) for m in markets]
    print(f"평균 길이: {sum(lengths)//len(lengths)}자, 최소: {min(lengths)}자, 최대: {max(lengths)}자")
    short = sum(1 for l in lengths if l < 200)
    print(f"200자 미만: {short}개")


if __name__ == "__main__":
    main()
