import csv
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup

def parse_table(table):
    """table要素のデータを読み込んで二次元配列を返す"""

    ##### thead 要素をパースする #####

    # thead 要素を取得 (存在する場合)
    thead = table.find("thead")

    # thead が存在する場合
    if thead:
        tr = thead.find("tr")
        ths = tr.find_all("th")
        columns = [th.text for th in ths]    # pandas.DataFrame を意識
    
    # thead が存在しない場合
    else:
        columns = []

    ##### tbody 要素をパースする #####

    # tbody 要素を取得
    tbody = table.find("tbody")

    # tr 要素を取得
    trs = tbody.find_all("tr")

    # 出力したい行データ
    rows = [columns]

    # td (th) 要素の値を読み込む
    # tbody -- tr 直下に th が存在するパターンがあるので
    # find_all(["td", "th"]) とするのがコツ
    for tr in trs:
        row = [td.text for td in tr.find_all(["td", "th"])]
        rows.append(row)

    return rows

def make_df(rows):
    df = pd.DataFrame(rows[1:])
    df = df.set_index(0)
    df.columns = ["人数", "うち入院"]
    df = df.loc[:"○クルーズ船感染者の受け入れ"]
    return df

def make_csv(df,subjects):
    people = [subjects, df.loc["計", "人数"], df.loc["計", "うち入院"], df.loc["死亡", "人数"]]
    build_df = pd.DataFrame(people, columns=["人数"], index=["検査実施人数","陽性患者数", "入院中", "死亡"])
    build_df.to_csv("data.csv")
    return build_df

if __name__ == "__main__":    
    # URLの指定
    html = urlopen("https://www.pref.aichi.jp/site/covid19-aichi/kansensya-kensa.html")
    bsObj = BeautifulSoup(html, "html.parser")

    tables = bsObj.find_all("table")
    rows = parse_table(tables[0])
    # 全体の検査件数を調査
    subjects = parse_table(tables[1])[-1][1].replace(",", "")
    df = make_df(rows)
    print(make_csv(df, subjects))

