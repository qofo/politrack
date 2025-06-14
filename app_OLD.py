from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="1234",
        database="postgres"
    )

@app.route("/")
def home():
    return "<h2>POLITRACK에 오신 것을 환영합니다</h2><a href='/politicians'>의원 목록 보기</a>"


@app.route("/politicians")
def list_politicians():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.politician_id, p.name, pa.name, d.name
        FROM politician p
        JOIN party pa ON p.party_id = pa.party_id
        JOIN district d ON p.district_id = d.district_id
        ORDER BY p.name
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("politicians.html", politicians=data)

@app.route("/politician/<int:pid>")
def politician_detail(pid):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM politician WHERE politician_id = %s", (pid,))
    name = cur.fetchone()[0]

    cur.execute("""
        SELECT date, category, subcategory, amount, description, type
        FROM funding
        WHERE politician_id = %s
        ORDER BY date DESC
    """, (pid,))
    records = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("politician_detail.html", name=name, records=records)

if __name__ == "__main__":
    app.run(debug=True)
