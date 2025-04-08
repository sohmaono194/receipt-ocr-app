# 05_calendar_summary.py

import pandas as pd
import calendar
from datetime import datetime

# データ読み込み
df = pd.read_csv("data/parsed_receipt.csv")

# 日付が複数ある場合にも対応
df["日付"] = pd.to_datetime(df["日付"], errors='coerce')

# 集計（月単位の支出）
target_month = df["日付"].dt.to_period("M").iloc[0]  # 最初の日付の月を対象にする
month_df = df[df["日付"].dt.to_period("M") == target_month]
summary = month_df.groupby(df["日付"].dt.day)["金額"].sum()

# カレンダー作成
year = target_month.year
month = target_month.month
cal = calendar.Calendar(firstweekday=6)  # 日曜日始まり

print(f"\n📅 {year}年{month}月の支出カレンダー\n")
print("日  月  火  水  木  金  土")

week_strs = []
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

# 残りの週
if week:
    while len(week) < 7:
        week.append("    ")
    print("  ".join(week))
