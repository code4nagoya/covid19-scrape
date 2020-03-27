# pdfからcsvに変換するのに使う。１ページごとにテーブル形式の箇所をdfとして出力する
# 参考：https://github.com/chezou/tabula-py
import tabula
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
from datetime import datetime
from datetime import timedelta
import os, json, pprint
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
    #任意のファイルパスをここに記載(ウェブ上のPDFについてもここで指定できる)
    page_url = base_url + FILE_PATH
    # ページ数を調べる
    pages = len(tabula.read_pdf(page_url, pages="all"))
    print("pages:", pages)

    # 全ページを読み込む
    rows = tabula.read_pdf(page_url, stream=True, pages="all")
    df = pd.concat(rows, ignore_index=True)
    # 発表日と年代・性別が一緒のcolumnになっているので、分離する
    data = df['発表日 年代・性別'].str.split(" ", expand=True)
    df["発表日"] = data[0]
    df["年代・性別"] = data[1]
    df = df.set_index("No")
    # 必要なデータだけを残す
    df = df[["No", "発表日", "年代・性別", "国籍", "住居地", "接触状況", "備考"]]

    # 日付のデータを更新する
    df = add_date(df)
    df.to_csv("./data/patients.csv")
    print(df.dtypes)
    return df

def build_table(FILE_PATH):
     #任意のファイルパスをここに記載(ウェブ上のPDFについてもここで指定できる)
    page_url = base_url + FILE_PATH
    # ページ数を調べる
    pages = len(tabula.read_pdf(page_url, pages="all"))
    print("pages:", pages)

    # 1ページ目を読み込む
    df1 = tabula.read_pdf(page_url, stream=True, pages="1")[0]
    # 発表日と年代・性別が一緒のcolumnになっているので、分離する
    data = df1['発表日 年代・性別'].str.split(" ", expand=True)
    df1["発表日"] = data[0]
    df1["年代・性別"] = data[1]
    # 必要なデータだけを残す
    df1 = df1[["No", "国籍", "住居地", "接触状況", "備考" , "発表日", "年代・性別"]]

    # 2ページ以降はデータにカラムがないので全部結合している
    rows = tabula.read_pdf(page_url, stream=True, pages="2-{}".format(pages), pandas_options={"header":None})
    df2 = pd.concat(rows, ignore_index=True)
    data2 = df2[1].str.split(' ', expand=True)
    del df2[1]
    df2[7] = data2[0]
    df2[8] = data2[1]
    df2.columns = df1.columns

    # １ページ目と２ページ目以降を結合
    df = pd.concat([df1, df2], ignore_index=True)
    df = df.astype(str).replace("nan", "")
    df = df.set_index("No")

    # 日付のデータを更新する
    df = add_date(df)
    df.to_csv("./data/patients.csv")
    print(df)
    return df

def add_date(df):
    print(df["発表日"])
    df["発表日"] = ["2020年" + str(date) for date in df["発表日"]] 
    basedate = pd.to_datetime(df["発表日"], format="%Y年%m月%d日")
    df["発表日"] = basedate.dt.strftime("%Y/%m/%d %H:%M")
    df["date"] = basedate.dt.strftime("%Y-%m-%d")
    df["short_date"] = basedate.dt.strftime("%m\\/%d")
    df["w"] = [str(int(w)+1) if int(w)+1 !=7 else "0" for w in basedate.dt.dayofweek]
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
    converted = json.loads(df.to_json(orient="table", force_ascii=False))
    # 日ごとの感染者数をカウントする
    val_count = df["date"].value_counts(sort=False)
    val_count = val_count.sort_index()

    # 開始日から最新の日付までのリストを作成
    strdt = datetime.strptime(val_count.index[0], '%Y-%m-%d')  # 開始日
    enddt = datetime.strptime(val_count.index[-1], '%Y-%m-%d')  # 終了日
    days_num = (enddt - strdt).days + 1
    dates_list = [(strdt + timedelta(i)).strftime('%Y-%m-%d') for i in range(days_num)]

    # 各日の感染者数をリスト化（誰もいないときは0として出力）
    patients_sumlist = [{"日付":date, "小計":int(val_count[date])} if date in val_count.index else {"日付":date, "小計":0} for date in dates_list]
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
    # pprint.pprint(data)
    with codecs.open("./data/data.json", mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    FILE_PATH = findpath("/site/covid19-aichi/kansensya-kensa.html")
    try:
        df = build_table(FILE_PATH)
    except:
        print("===============================================")
        traceback.print_exc()
        print("===============================================")
        df= convert_table(FILE_PATH)
    else:
        convert_json(df)