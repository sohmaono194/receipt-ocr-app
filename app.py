import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import calendar
import matplotlib
import requests
from PIL import Image
import re

# 日本語フォント設定
matplotlib.rcParams['font.family'] = 'Meiryo'

# OCR.space API を使ったOCR関数
def ocr_space_image(image_bytes, api_key, language='jpn'):
    url = 'https://api.ocr.space/parse/image'
    response = requests.post(
        url,
        files={'filename': ('image.jpg', image_bytes)},
        data={
            'apikey': api_key,
            'language': language,
            'isOverlayRequired': False
        }
    )
    result = response.json()
    if result.get('IsErroredOnProcessing'):
        raise Exception(result.get('ErrorMessage', ['Unknown error'])[0])
    return result['ParsedResults'][0]['ParsedText']

st.title("📷 レシートOCR支出管理アプリ")

uploaded_file = st.file_uploader("📤 レシート画像をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロード画像", use_column_width=True)

    image_bytes = uploaded_file.getvalue()

    # 🔑 APIキーの取得（Streamlit CloudやRenderなら secrets から取得）
    api_key = st.secrets["ocr_space_api_key"]

    try:
        # OCR.space でテキスト取得
        text = ocr_space_image(image_bytes, api_key, language="jpn")

        st.subheader("🧾 読み取ったテキスト")
        st.text(text)

        # テキストから「品目＋金額」を抽出
        lines = text.splitlines()
        items = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

            # 正規表現：金額が \または¥付き、または数字だけのパターン
            price_match = re.search(r'[¥\\]?\s?([0-9]{2,5})', next_line)

            if price_match:
                price = int(price_match.group(1))
                item = line.strip()
                # フィルタリング（不要ワードを除外）
                if not any(x in item for x in ['合計', '計', 'お預り', 'お釣り', 'ISPポイント', '支払方法', 'クレジット']):
                    items.append({
                        "日付": datetime.today().strftime("%Y-%m-%d"),
                        "品目": item,
                        "金額": price
                    })
                i += 2  # 2行進める
            else:
                i += 1  # 次の行へ

        if items:
            df = pd.DataFrame(items)

            st.subheader("📊 抽出結果")
            st.dataframe(df)

            # 円グラフ表示
            fig1, ax1 = plt.subplots()
            ax1.pie(df["金額"], labels=df["品目"], autopct="%1.1f%%", startangle=140)
            ax1.set_title("支出の内訳")
            st.pyplot(fig1)

            # 📅 カレンダー表示
            st.subheader("📅 カレンダー形式（合計支出）")

            df["日付"] = pd.to_datetime(df["日付"])
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

        else:
            st.warning("📄 レシートの内容が読み取れませんでした。")
    except Exception as e:
        st.error(f"OCRエラー：{e}")
else:
    st.info("画像をアップロードするとOCR処理が始まります。")