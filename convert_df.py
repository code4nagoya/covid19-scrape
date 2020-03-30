import re
import pandas as pd
import camelot
from bs4 import BeautifulSoup
import urllib.request
from datetime import datetime

base_url = "https://www.pref.aichi.jp"


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
    csv_path = "./data/patients.csv"
    df_csv = pd.concat([table.df for table in tables])
    df_csv.to_csv(csv_path, index=None, header=None)
    df = pd.read_csv(csv_path, index_col=0,
                     parse_dates=["発表日"], date_parser=my_parser)
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


def my_parser(s):

    y = datetime.now().year
    m, d = map(int, re.findall("[0-9]{1,2}", s))

    return pd.Timestamp(year=y, month=m, day=d)


if __name__ == "__main__":
    FILE_PATH = findpath("/site/covid19-aichi/kansensya-kensa.html")
    df = convert_table(FILE_PATH)
    print(df)
