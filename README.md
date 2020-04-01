# convid-19-scrape
愛知県版convid-19サイトのスクレイピングコード

[愛知県の感染状況](https://www.pref.aichi.jp/site/covid19-aichi/kansensya-kensa.html)のPDFデータをCSVに変換している

## 初回の設定
- git clone -b up-loadcsv https://github.com/code4nagoya/convid19-scrape
- git clone https://github.com/code4nagoya/covid19

## データの更新方法
- cd convid-19-scrape
- git pull 
- cp convid19-scrape/`更新するデータ` covid19/data/

## githubのアクション

- レポジトリのページの`Actions`タブに実行結果のログが出力する。

- `up-loadcsv`ブランチにツールを実行した際に生成したjsonを保存する。

## 動作確認(Linuxで動作確認)

- ghostscriptのインストール

```apt install python3-tk ghostscript```

- Pythonライブラリのインストール

```pip3 install -r requirements.txt```

- 実行方法

```python3 main.py```

