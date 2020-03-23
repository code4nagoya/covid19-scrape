# pdfからcsvに変換するのに使う。１ページごとにテーブル形式の箇所をdfとして出力する
# 参考：https://github.com/chezou/tabula-py
import tabula
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request

base_url = "https://www.pref.aichi.jp"

def pdf_to_table(FILE_PATH):
    #任意のファイルパスをここに記載(ウェブ上のPDFについてもここで指定できる)
    page_url = base_url + FILE_PATH
    # ページ数を調べる
    pages = len(tabula.read_pdf(page_url, pages="all"))
    print("pages:", pages)

    # 1ページ目を読み込む
    df1 = tabula.read_pdf(page_url, stream=True, pages="1")[0]
    data1 = df1['発表日 年代・性別'].str.split(" ", expand=True)
    del df1['発表日 年代・性別'], df1['Unnamed: 0']
    df1["発表日"] = data1[0]
    df1["年代・性別"] = data1[1]

    # 2ページ以降はデータにカラムがないので全部結合している
    dfs = tabula.read_pdf(page_url, stream=True, pages="2-{}".format(pages), pandas_options={'header': None})
    df2 = pd.concat(dfs, ignore_index=True)
    data2 = df2[1].str.split(' ', expand=True)
    del df2[1]
    df2[7] = data2[0]
    df2[8] = data2[1]
    df2.columns = df1.columns

    # 1ページ目と2ページ目以降を結合
    df = pd.concat([df1, df2], ignore_index=True)
    df.index = df["No"]
    del df["No"]

    # CSVに書き込み(ファイル名はdata1.py)
    df.to_csv("data/data1.csv")
    print(df)

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

if __name__ == "__main__":
    FILE_PATH = findpath("/site/covid19-aichi/kansensya-kensa.html")
    pdf_to_table(FILE_PATH)