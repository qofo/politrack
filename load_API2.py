import requests
import psycopg2
import pandas as pd
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "1234",
    "database": "postgres"
}
API_KEY = "6c2af7fa59ef4e2fae3c3d7c8ab1b8c2"

def load_and_save_members():
    url = "https://open.assembly.go.kr/portal/openapi/nwvrqwxyaytdsfvhu"
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "pIndex": 1,
        "pSize": 1000,
        "AGE": "22"  # 22대 국회 예시
    }
    resp = requests.get(url, params=params)
    data = resp.json()["nwvrqwxyaytdsfvhu"][1:]  # 첫번째는 meta
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    for row in data:
        # 날짜 파싱 예외처리
        try:
            bth_date = datetime.strptime(row.get("BTH_DATE"), "%Y-%m-%d") if row.get("BTH_DATE") else None
        except Exception:
            bth_date = None

        cur.execute("""
            INSERT INTO member (
                hg_nm, hj_nm, eng_nm, bth_gbn_nm, bth_date, job_res_nm, poly_nm, orig_nm, elect_gbn_nm,
                cmit_nm, cmits, reele_gbn_nm, units, sex_gbn_nm, tel_no, e_mail, homepage, staff,
                secretary, secretary2, mona_cd, mem_title, assem_addr
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (mona_cd) DO NOTHING
        """, (
            row.get("HG_NM"), row.get("HJ_NM"), row.get("ENG_NM"), row.get("BTH_GBN_NM"), bth_date,
            row.get("JOB_RES_NM"), row.get("POLY_NM"), row.get("ORIG_NM"), row.get("ELECT_GBN_NM"),
            row.get("CMIT_NM"), row.get("CMITS"), row.get("REELE_GBN_NM"), row.get("UNITS"),
            row.get("SEX_GBN_NM"), row.get("TEL_NO"), row.get("E_MAIL"), row.get("HOMEPAGE"),
            row.get("STAFF"), row.get("SECRETARY"), row.get("SECRETARY2"), row.get("MONA_CD"),
            row.get("MEM_TITLE"), row.get("ASSEM_ADDR")
        ))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ member 테이블 적재 완료")


def load_and_save_sns():
    url = "https://open.assembly.go.kr/portal/openapi/negnlnyvatsjwocar"
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "pIndex": 1,
        "pSize": 1000
    }
    resp = requests.get(url, params=params)
    data = resp.json()["negnlnyvatsjwocar"][1:]
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for row in data:
        cur.execute("""
            INSERT INTO member_sns (mona_cd, t_url, f_url, y_url, b_url)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (mona_cd) DO NOTHING
        """, (
            row.get("MONA_CD"), row.get("T_URL"), row.get("F_URL"),
            row.get("Y_URL"), row.get("B_URL")
        ))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ member_sns 테이블 적재 완료")


def load_and_save_bills():
    url = "https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn"
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "pIndex": 1,
        "pSize": 1000,
        "AGE": "22"
    }
    resp = requests.get(url, params=params)
    print(resp.status_code)
    print(resp.text)
    data = resp.json()["nzmimeepazxkubdpn"][1:]
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for row in data:
        # 날짜 파싱 예외처리
        def parse_date(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d") if s else None
            except Exception:
                return None

        cur.execute("""
            INSERT INTO bill (
                bill_id, bill_no, bill_name, committee, propose_dt, proc_result, age, detail_link,
                proposer, member_list, law_proc_dt, law_present_dt, law_submit_dt, cmt_proc_result_cd,
                cmt_proc_dt, cmt_present_dt, committee_dt, proc_dt, committee_id, publ_proposer,
                law_proc_result_cd, rst_proposer
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (bill_id) DO NOTHING
        """, (
            row.get("BILL_ID"), row.get("BILL_NO"), row.get("BILL_NAME"), row.get("COMMITTEE"),
            parse_date(row.get("PROPOSE_DT")), row.get("PROC_RESULT"), row.get("AGE"),
            row.get("DETAIL_LINK"), row.get("PROPOSER"), row.get("MEMBER_LIST"),
            parse_date(row.get("LAW_PROC_DT")), parse_date(row.get("LAW_PRESENT_DT")),
            parse_date(row.get("LAW_SUBMIT_DT")), row.get("CMT_PROC_RESULT_CD"),
            parse_date(row.get("CMT_PROC_DT")), parse_date(row.get("CMT_PRESENT_DT")),
            parse_date(row.get("COMMITTEE_DT")), parse_date(row.get("PROC_DT")),
            row.get("COMMITTEE_ID"), row.get("PUBL_PROPOSER"), row.get("LAW_PROC_RESULT_CD"),
            row.get("RST_PROPOSER")
        ))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ bill 테이블 적재 완료")


if __name__ == "__main__":
    #load_and_save_members()
    #load_and_save_sns()
    load_and_save_bills()


