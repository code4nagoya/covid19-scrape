import pandas as pd
import urllib.request
import json, pprint

def load_subject():
    FILE_PATH = "./data/main_summary.csv"
    # 愛知県の陽性検査者の数をまとめたスプレッドシートを読み込む
    url = "https://docs.google.com/spreadsheets/d/1DdluQBSQSiACG1CaIg4K3K-HVeGGThyecRHSA84lL6I/export?format=csv&gid=0"
    with urllib.request.urlopen(url) as b:
        with open(FILE_PATH, "bw") as f:
            f.write(b.read())
    df = pd.read_csv(FILE_PATH, index_col=0, header=None)
    json_data = json.loads(df.to_json())
    return json_data["1"]

if __name__ == "__main__":
    df = load_subject()
    print(df)