# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import calendar
import matplotlib
matplotlib.rcParams['font.family'] = 'Meiryo'

# CSV読み込み
csv_path = 'data/parsed_receipt.csv'

st.title("📷 レシート支出管理アプリ")

# CSVファイルがあるかチェック
try:
    df = pd.read_csv(csv_path)
    df["日付"] = pd.to_datetime(df["日付"])

    st.subheader("📋 支出一覧")
    st.dataframe(df)

    st.subheader("📊 支出の内訳（円グラフ）")
    fig1, ax1 = plt.subplots()
    ax1.pie(df["金額"],labels=df["品目"], autopct="%1.1f%%")
    st.pyplot(fig1)

    st.subheader("📅 カレンダー形式（合計支出）")

    # 月と年を取得
    month = df["日付"].dt.month[0]
    year = df["日付"].dt.year[0]

    grouped = df.groupby(df["日付"].dt.day)["金額"].sum()
    cal = calendar.Calendar(firstweekday=6)

    week_lines = []
    week = []
    for day in cal.itermonthdays(year, month):
        if day == 0:
            week.append(" ")
        else:
            yen = grouped.get(day, 0)
            week.append(f"{day}日\n¥{yen}")
        if len(week) == 7:
            week_lines.append(week)
            week = []
    if week:
        while len(week) < 7:
            week.append(" ")
        week_lines.append(week)

    st.write(f"🗓 {year}年 {month}月")
    st.table(pd.DataFrame(week_lines, columns=["日", "月", "火", "水", "木", "金", "土"]))

except FileNotFoundError:
    st.warning("⚠️ 支出データがありません。先に OCR 処理と解析をしてください。")
