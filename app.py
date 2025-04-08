# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import calendar
import matplotlib
matplotlib.rcParams['font.family'] = 'Meiryo'
import re

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
import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import io
import os
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['font.family'] = 'Meiryo'

st.title("📷 レシートOCRアップロードアプリ")

uploaded_file = st.file_uploader("📤 レシート画像をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロード画像", use_column_width=True)

    # OCR処理
    text = pytesseract.image_to_string(image, lang="jpn")

    st.subheader("🧾 読み取ったテキスト")
    st.text(text)

    # テキストから抽出（簡易版：あとで詳細版に切り替え可）
    lines = text.splitlines()
    items = []
    for line in lines:
        match = re.search(r'(?P<item>.+?)\s+(?P<price>\d{2,6})$', line)
        if match:
            item = match.group("item").strip()
            price = int(match.group("price"))
            if not any(x in item for x in ['合計', 'お釣り', '本込', '税込']):
                items.append({"品目": item, "金額": price})

    if items:
        df = pd.DataFrame(items)
        st.subheader("📊 抽出結果")
        st.dataframe(df)

        # 円グラフ
        fig, ax = plt.subplots()
        ax.pie(df["金額"], labels=df["品目"], autopct="%1.1f%%", startangle=140)
        ax.set_title("支出内訳")
        st.pyplot(fig)
    else:
        st.warning("📄 レシートの内容が正しく読み取れませんでした。")
