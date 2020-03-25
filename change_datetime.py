import pandas as pd

def convert_datetime(df):
    df["発表日"] = ["2020年" + date for date in df["発表日"]]
    df["data"] = pd.to_datetime(df["発表日"], format="%Y年%m月%d日")
    df["short_date"] = df["data"].dt.strftime("%m/%d")
    df["w"] = [int(w)+1 if int(w)+1 !=7 else 0 for w in df["data"].dt.dayofweek]
    return df

if __name__ == "__main__":
    df = pd.read_csv("./data/patients.csv")
    print(convert_datetime(df))
