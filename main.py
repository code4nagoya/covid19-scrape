# pdfからcsvに変換するのに使う。１ページごとにテーブル形式の箇所をdfとして出力する
# 参考：https://github.com/chezou/tabula-py
import tabula
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
from datetime import datetime
import os, json, pprint
import codecs

base_url = "https://www.pref.aichi.jp"

outdir = './data'
if not os.path.exists(outdir):
    os.mkdir(outdir)

def convert_table(FILE_PATH):
    #任意のファイルパスをここに記載(ウェブ上のPDFについてもここで指定できる)
    page_url = base_url + FILE_PATH
    # ページ数を調べる
    pages = len(tabula.read_pdf(page_url, pages="all"))
    print("pages:", pages)

    # 1ページ目を読み込む
    rows = tabula.read_pdf(page_url, stream=True, pages="all")
    df = pd.concat(rows, ignore_index=True)
    # 発表日と年代・性別が一緒のcolumnになっているので、分離する
    data = df['発表日 年代・性別'].str.split(" ", expand=True)
    df["発表日"] = data[0]
    df["年代・性別"] = data[1]
    df = df.set_index("No")
    # いらないデータを消す
    del df['発表日 年代・性別'], df['Unnamed: 0']

    # 日付のデータを更新する
    df = add_date(df)
    df.to_csv("./data/patients.csv")
    return df

def findpath(url):
    page_url = base_url + url
    raw_html = urllib.request.urlopen(page_url)
    soup = BeautifulSoup(raw_html, "html.parser")
    for aa in soup.find_all("a"):
        link = aa.get("href")
        name = aa.get_text()
        if "県内発生事例一覧" in name:
            table_link = link
            break
    return table_link  


def add_date(df):
    df["発表日"] = ["2020年" + date for date in df["発表日"]]
    basedate = pd.to_datetime(df["発表日"], format="%Y年%m月%d日")
    df["date"] = basedate.dt.strftime("%Y-%m-%d")
    df["short_date"] = basedate.dt.strftime("%m/%d")
    df["w"] = [int(w)+1 if int(w)+1 !=7 else 0 for w in basedate.dt.dayofweek]
    return df

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

def convert_json(df):
    # 取得時の時間を記録
    nowtime = datetime.now().strftime("%Y/%m/%d %H:%M")
    # 取得したデータをjson形式に変換
    converted = json.loads(df.to_json(orient="table", force_ascii=False))
    val_count = df["date"].value_counts(sort=False)
    patients_sumlist = [{"日付":date, "小計":int(val_count[date]) } for date in val_count.index]
    # スプレッドシートのデータを取得する
    sum_df = load_subject()
    # jsonを作成
    data = {
        "patients":{
            "date":nowtime,
            "data":converted["data"]
        },
        "patients_summary" : {
            "date": nowtime,
            "data":patients_sumlist
        },
        "lastUpdate": nowtime,
        "main_summary" : {
                "attr": "検査実施人数",
                "value": sum_df['検査実施人数'],
                "children": [
                    {
                        "attr": "陽性患者数",
                        "value": sum_df['陽性患者数'],
                        "children": [
                            {
                                "attr": "入院中",
                                "value": sum_df['入院中'],
                                "children": [
                                    {
                                        "attr": "軽症・中等症",
                                        "value": sum_df['軽症・中等症']
                                    },
                                    {
                                        "attr": "重症",
                                        "value": sum_df['重症']
                                    }
                                ]
                            },
                            {
                                "attr": "退院",
                                "value": sum_df['退院']
                            },
                            {
                                "attr": "転院",
                                "value": sum_df['転院']
                            },
                            {
                                "attr": "死亡",
                                "value": sum_df['死亡']
                            }
                        ]
                    }
                ]
        }
    }
    pprint.pprint(data)
    with codecs.open("./data/data.json", mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    FILE_PATH = findpath("/site/covid19-aichi/kansensya-kensa.html")
    df = convert_table(FILE_PATH)
    print(df)
    convert_json(df)