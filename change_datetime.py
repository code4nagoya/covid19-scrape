import pandas as pd

def convert_datetime(df):
    df["発表日"] = ["2020年" + date for date in df["発表日"]]
    basedate = pd.to_datetime(df["発表日"], format="%Y年%m月%d日")
    df["date"] = basedate.dt.strftime("%Y-%m-%d")
    df["short_date"] = basedate.dt.strftime("%m/%d")
    df["w"] = [int(w)+1 if int(w)+1 !=7 else 0 for w in basedate.dt.dayofweek]
    return df

if __name__ == "__main__":
    df = pd.read_csv("./data/patients.csv")
    # new_df = convert_datetime(df)
    val_count = df["date"].value_counts(sort=False)
    # patients_sumlist = [{"日付":date, "小計":val_count[date] } for date in val_count.index]
    # print(patients_sumlist)

    print(type(int(val_count["2020-02-22"])))