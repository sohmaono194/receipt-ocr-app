import pandas as pd
import calendar
from datetime import datetime

# データ読み込み
df = pd.read_csv("data/parsed_receipt.csv")

# 日付の変換と無効な日付の削除
df["日付"] = pd.to_datetime(df["日付"], errors='coerce')
df = df.dropna(subset=["日付"])

# ユーザー入力による年と月の指定
year = int(input("表示したい年を入力してください（例：2025）: "))
month = int(input("表示したい月を入力してください（1-12）: "))

# 指定された年と月のデータを抽出
target_month = f"{year}-{month:02}"
month_df = df[df["日付"].dt.to_period("M") == target_month]

# 日ごとの支出を集計
summary = month_df.groupby(df["日付"].dt.day)["金額"].sum()

# カレンダーの表示
cal = calendar.Calendar(firstweekday=6)  # 日曜日始まり

print(f"\n📅 {year}年{month}月の支出カレンダー\n")
print("日  月  火  水  木  金  土")

week = []
for day in cal.itermonthdays(year, month):
    if day == 0:
        week.append("    ")  # 空白の日
    else:
        amount = summary.get(day, 0)
        week.append(f"{day:2}¥{amount:>3}")
    if len(week) == 7:
        print("  ".join(week))
        week = []

# 残りの週を表示
if week:
    while len(week) < 7:
        week.append("    ")
    print("  ".join(week))

