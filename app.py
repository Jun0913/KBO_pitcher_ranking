from flask import Flask, render_template, request
from services.es_service import get_top_pitchers, GOOD_ASC_METRICS

# ERA / WPCT / WHIP / AVG 는 기본적으로 규정이닝(100이닝) 필터
IP_FILTER_METRICS = {"era", "wpct", "whip", "avg"}


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        # 기본값: 2025 / ALL / ERA / 규정이닝 IP>=100
        season = 2025
        metric = "era"
        team = "all"
        default_dir = "asc"  # ERA는 값이 낮을수록 좋음

        pitchers, sort_dir = get_top_pitchers(
            season=season,
            metric=metric,
            team=team,
            min_ip=100.0,          # 기본 첫 화면은 항상 전체 + 규정이닝
            sort_dir=default_dir,
        )

        return render_template(
            "rankings.html",
            season=season,
            metric=metric,
            team=team,
            sort_dir=sort_dir,
            pitchers=pitchers,
            metrics_list=get_metrics_list(),
            teams_list=get_teams_list()
        )

    @app.route("/rankings")
    def rankings():
        season = int(request.args.get("season", 2025))
        metric = request.args.get("metric", "era")
        team = request.args.get("team", "all")
        sort_dir = request.args.get("sort_dir")

        if sort_dir not in ("asc", "desc"):
            sort_dir = "asc" if metric in GOOD_ASC_METRICS else "desc"

        # 🔥 규정이닝 필터 로직
        # - 팀이 "전체"일 때만 ERA/WPCT/WHIP/AVG 에 대해 100이닝 이상 필터 적용
        # - 특정 팀이 선택되면 어떤 지표든 이닝 제한 없이 보여줌
        if team.lower() == "all" and metric in IP_FILTER_METRICS:
            min_ip = 100.0
        else:
            min_ip = None

        pitchers, sort_dir = get_top_pitchers(
            season=season,
            metric=metric,
            team=team,
            min_ip=min_ip,
            sort_dir=sort_dir,
        )

        return render_template(
            "rankings.html",
            season=season,
            metric=metric,
            team=team,
            sort_dir=sort_dir,
            pitchers=pitchers,
            metrics_list=get_metrics_list(),
            teams_list=get_teams_list()
        )

    return app


def get_metrics_list():
    return [
        ("era", "ERA"),
        ("g", "G"),
        ("w", "W"),
        ("l", "L"),
        ("sv", "SV"),
        ("hld", "HLD"),
        ("wpct", "WPCT"),
        ("ip", "IP"),
        ("h", "H"),
        ("hr", "HR"),
        ("bb", "BB"),
        ("hbp", "HBP"),
        ("so", "SO"),
        ("r", "R"),
        ("er", "ER"),
        ("whip", "WHIP"),
        ("cg", "CG"),
        ("sho", "SHO"),
        ("qs", "QS"),
        ("bsv", "BSV"),
        ("tbf", "TBF"),
        ("np", "NP"),
        ("avg", "AVG"),
        ("2b", "2B"),
        ("3b", "3B"),
        ("sac", "SAC"),
        ("sf", "SF"),
        ("ibb", "IBB"),
        ("wp", "WP"),
        ("bk", "BK"),
    ]


def get_teams_list():
    return [
        ("all", "전체"),
        ("KIA", "KIA"),
        ("롯데", "롯데"),
        ("삼성", "삼성"),
        ("SSG", "SSG"),
        ("두산", "두산"),
        ("LG", "LG"),
        ("NC", "NC"),
        ("KT", "KT"),
        ("한화", "한화"),
        ("키움", "키움"),
    ]


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=9941, debug=True)
