#pdfからcsvに変換するのに使う。ページ指定で1枚ずつしか一気に使えないです。
import tabula
import pandas as pd

#任意のファイルパスをここに記載(ウェブ上のPDFについてもここで指定できる)
FILE_PATH = "https://www.pref.aichi.jp/uploaded/attachment/327109.pdf"

# ページ数を調べる
pages = len(tabula.read_pdf(FILE_PATH, pages="all"))
print("pages:", pages)

# 1ページ目を読み込む
df1 = tabula.read_pdf(FILE_PATH, stream=True, pages="1")[0]
data1 = df1['発表日 年代・性別'].str.split(" ", expand=True)
del df1['発表日 年代・性別'], df1['Unnamed: 0']
df1["発表日"] = data1[0]
df1["年代・性別"] = data1[1]

# 2ページ以降はデータがカラムがないので全部結合している
dfs = tabula.read_pdf(FILE_PATH, stream=True, pages="2-{}".format(pages), pandas_options={'header': None})
df2 = pd.concat(dfs, ignore_index=True)
data2 = df2[1].str.split(' ', expand=True)
del df2[1]
df2[7] = data2[0]
df2[8] = data2[1]
df2.columns = df1.columns

# 1ページ目と２ページ目以降を結合
df = pd.concat([df1, df2], ignore_index=True)
df.index = df["No"]
del df["No"]

# CSVに書き込み
df.to_csv("data1.csv")
print(df)