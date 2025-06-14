from flask import Flask, render_template, request
import psycopg2
import pandas as pd

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="1234",
        database="postgres"
    )

# 홈: 통합 검색/프로필 카드
@app.route("/", methods=["GET", "POST"])
def index():
    members = []
    if request.method == "POST":
        keyword = request.form.get("keyword", "")
        conn = get_connection()
        df = pd.read_sql(f"""
            SELECT * FROM member
            WHERE hg_nm ILIKE %s OR poly_nm ILIKE %s OR orig_nm ILIKE %s
        """, conn, params=(f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        members = df.to_dict("records")
        conn.close()
    return render_template("index.html", members=members)

# 프로필 상세 + 시각화
@app.route("/profile/<mona_cd>")
def profile(mona_cd):
    conn = get_connection()
    member = pd.read_sql("SELECT * FROM member WHERE mona_cd=%s", conn, params=(mona_cd,)).iloc[0].to_dict()
    # 정치자금 대분류별 비율
    funding = pd.read_sql("""
    SELECT f.category_major, SUM(f.amount) AS total
    FROM funding f
    JOIN politician p ON f.politician_id = p.politician_id
    WHERE p.name = %s
    GROUP BY f.category_major
    ORDER BY total DESC
    """, conn, params=(member["hg_nm"],))

    funding_data = funding.values.tolist()
    conn.close()
    return render_template("profile.html", member=member, funding_data=funding_data)

@app.route("/compare", methods=["GET", "POST"])
def compare():
    conn = get_connection()
    df_members = pd.read_sql("SELECT hg_nm, orig_nm, poly_nm, mona_cd FROM member", conn)
    search_results = []
    selected_mona_cds = []
    selected_members = []
    chart_data = {}

    # 1. 검색 및 선택 상태 유지
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        # 이전에 선택한 mona_cd 리스트를 hidden input으로 유지
        selected_mona_cds = request.form.getlist("selected_mona_cd")
        # 검색 시
        if "search" in request.form:
            if keyword:
                search_results = df_members[
                    df_members["hg_nm"].str.contains(keyword, case=False, na=False) |
                    df_members["orig_nm"].str.contains(keyword, case=False, na=False)
                ].to_dict("records")
        # 비교 시
        elif "compare" in request.form:
            # 체크박스에서 새로 선택한 것도 반영
            new_selected = request.form.getlist("search_result_mona_cd")
            for mc in new_selected:
                if mc not in selected_mona_cds and len(selected_mona_cds) < 4:
                    selected_mona_cds.append(mc)
            # 의원 정보 불러오기
            for mona_cd in selected_mona_cds:
                member = pd.read_sql("SELECT * FROM member WHERE mona_cd=%s", conn, params=(mona_cd,))
                if member.empty:
                    continue
                m = member.iloc[0].to_dict()
                m["attendance"] = 0.93  # 예시
                m["bills"] = 27  # 예시
                fund = pd.read_sql("""
                    SELECT category_major, SUM(amount) AS total
                    FROM funding f
                    JOIN politician p ON f.politician_id = p.politician_id
                    WHERE p.name = %s
                    GROUP BY category_major
                    ORDER BY total DESC
                """, conn, params=(m["hg_nm"],))
                fund_total = fund["total"].sum()
                funding_ratio = {}
                for _, row in fund.iterrows():
                    cat = row["category_major"]
                    ratio = round((row["total"] / fund_total) * 100, 1) if fund_total else 0
                    funding_ratio[cat] = ratio
                m["funding"] = funding_ratio
                selected_members.append(m)
            # 그래프 데이터
            chart_data = {
                "names": [m["hg_nm"] for m in selected_members],
                "attendance": [m["attendance"] for m in selected_members],
                "bills": [m["bills"] for m in selected_members],
                "funding_labels": list(set(cat for m in selected_members for cat in m["funding"].keys())),
                "funding": [
                    [m["funding"].get(cat, 0) for cat in list(set(cat for m2 in selected_members for cat in m2["funding"].keys()))]
                    for m in selected_members
                ]
            }
    else:
        search_results = []
        selected_mona_cds = []
        selected_members = []
        chart_data = {}
    conn.close()
    return render_template(
        "compare.html",
        members=df_members.to_dict("records"),
        search_results=search_results,
        selected_mona_cds=selected_mona_cds,
        selected_members=selected_members,
        chart_data=chart_data
    )


# 추천: 키워드 기반
@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    members = []
    if request.method == "POST":
        keyword = request.form.get("keyword", "")
        conn = get_connection()
        df = pd.read_sql("""
            SELECT * FROM member
            WHERE mem_title ILIKE %s OR cmit_nm ILIKE %s
        """, conn, params=(f"%{keyword}%", f"%{keyword}%"))
        members = df.to_dict("records")
        conn.close()
    return render_template("recommend.html", members=members)

if __name__ == "__main__":
    app.run(debug=True)
