import argparse
import os

import pandas as pd
from elasticsearch import Elasticsearch, helpers

ES_INDEX = os.getenv("ES_INDEX", "kbo_pitcher_stats")
ES_HOSTS = os.getenv("ES_HOSTS", "http://localhost:9200").split(",")

# 엑셀 헤더 -> ES 필드명 매핑
# 왼쪽은 엑셀에 있는 열 이름, 오른쪽은 ES 필드(소문자)
# 네 엑셀 헤더에 맞게만 수정하면 됨.
COLUMN_MAP = {
    "선수명": "player_name",

    "팀명": "team",

    "ERA": "era",
    "G": "g",
    "W": "w",
    "L": "l",
    "SV": "sv",
    "HLD": "hld",
    "WPCT": "wpct",
    "IP": "ip",
    "H": "h",
    "HR": "hr",
    "BB": "bb",
    "HBP": "hbp",
    "SO": "so",
    "R": "r",
    "ER": "er",
    "WHIP": "whip",
    "CG": "cg",
    "SHO": "sho",
    "QS": "qs",
    "BSV": "bsv",
    "TBF": "tbf",
    "NP": "np",
    "AVG": "avg",
    "2B": "2b",
    "3B": "3b",
    "SAC": "sac",
    "SF": "sf",
    "IBB": "ibb",
    "WP": "wp",
    "BK": "bk",
}


def parse_ip(value):
    """엑셀 IP 컬럼 파싱: 180 2/3, 123 1/3, 100.2 등."""
    if pd.isna(value):
        return None

    # 이미 숫자면 그대로 float
    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).strip()
    if not s:
        return None

    # "180 2/3" 형태
    if " " in s:
        base_str, frac_str = s.split()
    else:
        base_str, frac_str = s, None

    try:
        base = float(base_str)
    except ValueError:
        return None

    if frac_str in ("1/3", "⅓"):
        frac = 1.0 / 3.0
    elif frac_str in ("2/3", "⅔"):
        frac = 2.0 / 3.0
    else:
        frac = 0.0

    return round(base + frac, 2)


def normalize_row(row, season_from_sheet: int):
    """엑셀 한 줄(row)을 ES 문서 구조로 변환."""
    doc = {
        "season": season_from_sheet
    }

    for col_excel, es_field in COLUMN_MAP.items():
        if col_excel in row and pd.notna(row[col_excel]):
            value = row[col_excel]
            if es_field == "ip":
                value = parse_ip(value)
            doc[es_field] = value

    return doc


def load_excel_to_es(excel_path: str):
    es = Elasticsearch(ES_HOSTS)

    if not es.indices.exists(index=ES_INDEX):
        print(f"Index '{ES_INDEX}' 가 없어서 생성하지 않고 진행합니다. (미리 매핑 만들어둬야 함)")

    # sheet_name=None 이면 모든 시트를 dict로 읽어옴
    xls = pd.read_excel(excel_path, sheet_name=None)

    actions = []

    for sheet_name, df in xls.items():
        try:
            season = int(sheet_name)
        except ValueError:
            print(f"시트 이름 '{sheet_name}' 는 시즌 숫자가 아니라서 스킵합니다.")
            continue

        print(f"시트 '{sheet_name}' (season={season}) 로딩 중, 행 개수: {len(df)}")

        # 컬럼 이름 정리 (앞뒤 공백 제거)
        df = df.rename(columns=lambda c: str(c).strip())

        for _, row in df.iterrows():
            doc = normalize_row(row, season_from_sheet=season)
            # 최소한 player_name, team 정도는 있어야 인덱싱
            if "player_name" not in doc or "team" not in doc:
                continue

            action = {
                "_index": ES_INDEX,
                "_source": doc
            }
            actions.append(action)

    if not actions:
        print("적재할 데이터가 없습니다.")
        return

    print(f"총 {len(actions)} 건 bulk 인덱싱 시작...")
    helpers.bulk(es, actions)
    print("완료!")


def main():
    parser = argparse.ArgumentParser(description="KBO 투수 엑셀 데이터를 Elasticsearch에 적재")
    parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="엑셀 파일 경로 (예: data/kbo_pitcher_stats.xlsx)"
    )
    args = parser.parse_args()

    load_excel_to_es(args.file)


if __name__ == "__main__":
    main()
