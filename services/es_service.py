from elasticsearch import Elasticsearch
from config import ES_HOSTS, ES_INDEX

es = Elasticsearch(ES_HOSTS)

GOOD_ASC_METRICS = {"era", "whip", "avg"}


def get_top_pitchers(
    season: int,
    metric: str,
    team: str,
    min_ip: float | None = None,
    sort_dir: str | None = None,
):
    if sort_dir in ("asc", "desc"):
        order = sort_dir
    else:
        order = "asc" if metric in GOOD_ASC_METRICS else "desc"

    filters: list[dict] = [{"term": {"season": season}}]

    if team and team.lower() != "all":
        filters.append({"term": {"team": team}})

    if min_ip is not None:
        filters.append({"range": {"ip": {"gte": min_ip}}})

    body = {
        "size": 20,
        "query": {
            "bool": {
                "filter": filters
            }
        },
        "sort": [
            {metric: {"order": order}}
        ]
    }

    try:
        res = es.search(index=ES_INDEX, body=body)
    except Exception as e:
        print(f"[ES ERROR] {e}")
        return [], order

    pitchers = []
    hits = res.get("hits", {}).get("hits", [])

    # ---------- 여기부터 순위 계산: RANK() 스타일 ----------
    current_rank = 0          # 실제 표시할 순위 (1,2,2,4,...)
    last_value = None         # 직전 metric 값
    # position: 정렬된 순서(1,2,3,4,...)
    for position, hit in enumerate(hits, start=1):
        source = hit.get("_source", {})
        value = source.get(metric)

        # float은 반올림해서 비교 (ERA, WHIP 같은 지표)
        if isinstance(value, float):
            compare_val = round(value, 3)
        else:
            compare_val = value

        if last_value is None or compare_val != last_value:
            # 값이 바뀌면, 순위 = 현재 위치
            current_rank = position
            last_value = compare_val

        # 값이 같으면 current_rank 그대로 사용 (순위 건너뛰는 효과)
        source["rank"] = current_rank
        pitchers.append(source)
    # ---------------------------------------------------

    return pitchers, order
