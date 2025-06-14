import pandas as pd
import psycopg2
import ast
from datetime import datetime

def main():
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="1234",
        database="postgres"
    )
    cur = conn.cursor()

    # Read and parse the CSV exported from the Open Assembly API. The file
    # contains a single row where the "row" column is a string representation
    # of a list of dictionaries (not valid JSON). We therefore use
    # ``ast.literal_eval`` instead of ``json.loads``.
    df = pd.read_csv("member_info.csv")
    raw = str(df.loc[0, "row"]).strip()
    if raw.startswith("\"") and raw.endswith("\""):
        raw = raw[1:-1]
    records = ast.literal_eval(raw)
    
    # Create a table to store detailed member information.  It is separate from
    # the simple ``politician`` table used for funding data.
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
            mona_cd TEXT,
            mem_title TEXT,
            assem_addr TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Insert data into the member table
    for data in records:
        
        # Prepare the values for insertion
        values = (
            data['HG_NM'],
            data['HJ_NM'],
            data['ENG_NM'],
            data['BTH_GBN_NM'],
            datetime.strptime(data['BTH_DATE'], '%Y-%m-%d'),
            data['JOB_RES_NM'],
            data['POLY_NM'],
            data['ORIG_NM'],
            data['ELECT_GBN_NM'],
            data['CMIT_NM'],
            data['CMITS'],
            data['REELE_GBN_NM'],
            data['UNITS'],
            data['SEX_GBN_NM'],
            data['TEL_NO'],
            data['E_MAIL'],
            data['HOMEPAGE'],
            data['STAFF'],
            data['SECRETARY'],
            data['SECRETARY2'],
            data['MONA_CD'],
            data['MEM_TITLE'],
            data['ASSEM_ADDR']
        )

        # Insert into member table
        cur.execute("""
            INSERT INTO member (
                hg_nm, hj_nm, eng_nm, bth_gbn_nm, bth_date,
                job_res_nm, poly_nm, orig_nm, elect_gbn_nm,
                cmit_nm, cmits, reele_gbn_nm, units,
                sex_gbn_nm, tel_no, e_mail, homepage,
                staff, secretary, secretary2, mona_cd, mem_title,
                assem_addr
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, values)

    # Commit the changes and close the connection
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
