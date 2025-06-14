import requests
import pandas as pd

API_KEY = "6c2af7fa59ef4e2fae3c3d7c8ab1b8c2"  # 반드시 본인 API KEY로 대체
url = "https://open.assembly.go.kr/portal/openapi/nwvrqwxyaytdsfvhu"
params = {
    "KEY": API_KEY,
    "Type": "json",
    "pIndex": 1,
    "pSize": 1000,
    "AGE": "21"
}

resp = requests.get(url, params=params)
data = resp.json()["nwvrqwxyaytdsfvhu"][1:]  # 첫 번째 요소는 meta

df = pd.DataFrame(data)
df.to_csv("member_info.csv", index=False)
