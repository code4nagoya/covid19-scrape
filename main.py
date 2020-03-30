import camelot
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
from datetime import datetime
from datetime import timedelta
import json
import codecs
import traceback

base_url = "https://www.pref.aichi.jp"

outdir = './data'
if not os.path.exists(outdir):
    os.mkdir(outdir)


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


def convert_table(FILE_PATH):
    # 最新版のPDFをダウンロード
    page_url = base_url + FILE_PATH
    pdf_path = "./data/source.pdf"
    with urllib.request.urlopen(page_url) as b:
        with open(pdf_path, "bw") as f:
            f.write(b.read())

    tables = camelot.read_pdf(
        pdf_path, pages="1-end", split_text=True,
        strip_text="\n", line_scale=40)

    # csvに保存
    csv_path = "./data/source.csv"
    df_csv = pd.concat([table.df for table in tables])
    df_csv.to_csv(csv_path, index=None, header=None)
    df = pd.read_csv(csv_path, index_col=0,
                     parse_dates=["発表日"], date_parser=my_parser)
    df = add_date(df).fillna("")
    str_index = pd.Index([str(num) for num in list(df.index)])
    df = df.set_index(str_index)
    print(df)
    return df


def add_date(df):
    basedate = df["発表日"]
    df["発表日"] = basedate.dt.strftime("%Y/%m/%d %H:%M")
    df["date"] = basedate.dt.strftime("%Y-%m-%d")
    df["short_date"] = basedate.dt.strftime("%m\\/%d")
    df["w"] = [str(int(w)+1) if int(w)+1 != 7 else "0"
               for w in basedate.dt.dayofweek]
    return df


def load_subject():
    FILE_PATH = "./data/main_summary.csv"
    # 愛知県の陽性検査者の数をまとめたスプレッドシートを読み込む
    url = ("https://docs.google.com/spreadsheets/d/"
           "1DdluQBSQSiACG1CaIg4K3K-HVeGGThyecRHSA84lL6I/"
           "export?format=csv&gid=0")
    with urllib.request.urlopen(url) as b:
        with open(FILE_PATH, "bw") as f:
            f.write(b.read())
    df = pd.read_csv(FILE_PATH, index_col=0, header=None)
    json_data = json.loads(df.to_json())
    return json_data["1"]


def convert_json(df):
    # 取得時の時間を記録
    nowtime = datetime.now().strftime("%Y/%m/%d %H:%M")
    converted = json.loads(df.to_json(orient="table", force_ascii=False))
    # 日ごとの感染者数をカウントする
    val_count = df["date"].value_counts(sort=False)
    val_count = val_count.sort_index()
    print(val_count)
    # 開始日から最新の日付までのリストを作成
    strdt = datetime.strptime(val_count.index[0], '%Y-%m-%d')  # 開始日
    enddt = datetime.strptime(val_count.index[-1], '%Y-%m-%d')  # 終了日
    days_num = (enddt - strdt).days + 1
    dates_list = [(strdt + timedelta(i)).strftime('%Y-%m-%d')
                  for i in range(days_num)]

    # 各日の感染者数をリスト化（誰もいないときは0として出力）
    patients_sumlist = [{"日付": date, "小計": int(val_count[date])}
                        if date in val_count.index else {"日付": date, "小計": 0}
                        for date in dates_list]

    # スプレッドシートのデータを取得する
    sum_df = load_subject()
    # jsonを作成
    data = {
        "patients": {
            "date": nowtime,
            "data": converted["data"]
        },
        "patients_summary": {
            "date": nowtime,
            "data": patients_sumlist
        },
        "lastUpdate": nowtime,
        "main_summary": {
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
    # pprint.pprint(data)
    with codecs.open("./data/data.json", mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def my_parser(s):
    y = datetime.now().year
    m, d = map(int, re.findall("[0-9]{1,2}", s))
    return pd.Timestamp(year=y, month=m, day=d)


if __name__ == "__main__":
    FILE_PATH = findpath("/site/covid19-aichi/kansensya-kensa.html")
    try:
        df = convert_table(FILE_PATH)
        convert_json(df)
    except Exception:
        print("===================")
        traceback.print_exc()
        print("===================")
