import pandas as pd
import psycopg2
from datetime import datetime

def initSQL(cur):
    file_path = "2023_KAPF.xlsx"
    df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl")

    # 컬럼명 정리
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        "의원번호": "politician_id",
        "의원명": "name",
        "당": "party",
        "당ID": "party_id",
        "지역명": "district",
        "계정명": "category",
        "과목명": "subcategory",
        "연월일": "date",
        "내역": "description",
        "지출금회": "amount",
        "분류": "type"
    })

    # 1. 테이블 생성
    cur.execute("""
        CREATE TABLE party (
            party_id INT PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE district (
            district_id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE politician (
            politician_id INT PRIMARY KEY,
            name TEXT NOT NULL,
            party_id INT REFERENCES party(party_id),
            district_id INT REFERENCES district(district_id)
        );

        CREATE TABLE funding (
            funding_id SERIAL PRIMARY KEY,
            politician_id INT REFERENCES politician(politician_id),
            date DATE,
            category TEXT,
            subcategory TEXT,
            amount NUMERIC,
            description TEXT,
            type TEXT
        );
    """)
    conn.commit()

    # 2. 정당 삽입
    party_seen = set()
    for _, row in df.iterrows():
        if row["party_id"] not in party_seen:
            cur.execute("INSERT INTO party (party_id, name) VALUES (%s, %s)", (int(row["party_id"]), row["party"]))
            party_seen.add(row["party_id"])

    # 3. 지역구 삽입 및 매핑
    district_map = {}
    for district in df["district"].unique():
        cur.execute("INSERT INTO district (name) VALUES (%s) RETURNING district_id", (district,))
        did = cur.fetchone()[0]
        district_map[district] = did

    # 4. 정치인 삽입
    politician_seen = set()
    for _, row in df.iterrows():
        pid = int(row["politician_id"])
        if pid in politician_seen:
            continue
        did = district_map[row["district"]]
        cur.execute(
            "INSERT INTO politician (politician_id, name, party_id, district_id) VALUES (%s, %s, %s, %s)",
            (pid, row["name"], int(row["party_id"]), did)
        )
        politician_seen.add(pid)

    # 5. 정치자금 삽입
    for _, row in df.iterrows():
        date = pd.to_datetime(row["date"], errors='coerce')
        if pd.isna(row["amount"]):  # 수입/지출이 없는 경우 skip
            continue
        amount = float(row["amount"])
        cur.execute("""
            INSERT INTO funding (politician_id, date, category, subcategory, amount, description, type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            int(row["politician_id"]),
            date.date() if not pd.isnull(date) else None,
            row["category"],
            row["subcategory"],
            amount,
            row["description"],
            row["type"]
        ))

    conn.commit()
    print("✅ 데이터 적재 완료")

def main():
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="1234",
        database="postgres"
    )
    cur = conn.cursor()

    #initSQL(cur)

    query = """
    -- 1. 컬럼 추가
ALTER TABLE funding ADD COLUMN category_major TEXT;
ALTER TABLE funding ADD COLUMN category_minor TEXT;

-- 2. 분리하여 업데이트
UPDATE funding
SET category_major = SPLIT_PART(type, '_', 1),
    category_minor = SPLIT_PART(type, '_', 2);

-- 3. 결과 확인
SELECT type, category_major, category_minor FROM funding LIMIT 5;
    """
    
    cur.execute(query)
    conn.commit()
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
