import psycopg2

def create_tables():
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="1234",
        database="postgres"
    )
    cur = conn.cursor()

    # 1. 의원 상세정보 테이블 (member)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS member (
        member_id SERIAL PRIMARY KEY,
        hg_nm TEXT NOT NULL,
        hj_nm TEXT,
        eng_nm TEXT,
        bth_gbn_nm TEXT,
        bth_date DATE,
        job_res_nm TEXT,
        poly_nm TEXT,
        orig_nm TEXT,
        elect_gbn_nm TEXT,
        cmit_nm TEXT,
        cmits TEXT,
        reele_gbn_nm TEXT,
        units TEXT,
        sex_gbn_nm TEXT,
        tel_no TEXT,
        e_mail TEXT,
        homepage TEXT,
        staff TEXT,
        secretary TEXT,
        secretary2 TEXT,
        mona_cd TEXT PRIMARY KEY,
        mem_title TEXT,
        assem_addr TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("ALTER TABLE member ADD CONSTRAINT unique_mona_cd UNIQUE (mona_cd);")

    # 2. SNS 정보 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS member_sns (
        sns_id SERIAL PRIMARY KEY,
        mona_cd TEXT REFERENCES member(mona_cd),
        t_url TEXT,
        f_url TEXT,
        y_url TEXT,
        b_url TEXT
    );
    """)

    # 3. 법률안(의안) 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bill (
        bill_id TEXT PRIMARY KEY,
        bill_no TEXT,
        bill_name TEXT,
        committee TEXT,
        propose_dt DATE,
        proc_result TEXT,
        age TEXT,
        detail_link TEXT,
        proposer TEXT,
        member_list TEXT,
        law_proc_dt DATE,
        law_present_dt DATE,
        law_submit_dt DATE,
        cmt_proc_result_cd TEXT,
        cmt_proc_dt DATE,
        cmt_present_dt DATE,
        committee_dt DATE,
        proc_dt DATE,
        committee_id TEXT,
        publ_proposer TEXT,
        law_proc_result_cd TEXT,
        rst_proposer TEXT
    );
    """)

    # 4. 의원-법률안 관계 테이블 (공동/대표발의)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS member_bill (
        member_bill_id SERIAL PRIMARY KEY,
        mona_cd TEXT REFERENCES member(mona_cd),
        bill_id TEXT REFERENCES bill(bill_id),
        role TEXT -- 대표/공동발의자 등
    );
    """)

    # 5. 본회의 표결 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vote (
        vote_id SERIAL PRIMARY KEY,
        mona_cd TEXT REFERENCES member(mona_cd),
        bill_id TEXT REFERENCES bill(bill_id),
        vote_date DATE,
        result_vote_mod TEXT -- 찬성/반대/기권 등
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ 모든 테이블 생성 완료")

if __name__ == "__main__":
    create_tables()
