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
    df.to_csv("./data/sample.csv")
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

def convert_json(df):
    # 取得時の時間を記録
    nowtime = datetime.now().strftime("%Y/%m/%d %H:%M")
    # 取得したデータをjson形式に変換
    converted = json.loads(df.to_json(orient="table", force_ascii=False))
    pprint.pprint(converted["data"])

    # jsonを作成
    data = {
        "patients":{
            "date":nowtime,
            "data":converted["data"]
        }
    }
    with codecs.open("./data/data.json", mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_date(df):
    df["発表日"] = ["2020年" + date for date in df["発表日"]]
    basedate = pd.to_datetime(df["発表日"], format="%Y年%m月%d日")
    df["data"] = basedate.dt.strftime("%Y-%m-%d")
    df["short_date"] = basedate.dt.strftime("%m/%d")
    df["w"] = [int(w)+1 if int(w)+1 !=7 else 0 for w in basedate.dt.dayofweek]
    return df
    
if __name__ == "__main__":
    FILE_PATH = findpath("/site/covid19-aichi/kansensya-kensa.html")
    # df = pdf_to_table(FILE_PATH)
    df = convert_table(FILE_PATH)
    print(df)
    convert_json(df)