# convid-19-scrape
愛知県版convid-19サイトのスクレイピングコード

[愛知県の感染状況](https://www.pref.aichi.jp/site/covid19-aichi/kansensya-kensa.html)のPDFデータをCSVに変換している

# 初回の設定
- git clone -b up-loadcsv https://github.com/Miura55/convid-19-scrape
- git clone https://github.com/code4nagoya/covid19

# データの更新方法
- cd convid-19-scrape
- git pull 
- cp convid-19-scrape/```更新するデータ``` covid19/data/