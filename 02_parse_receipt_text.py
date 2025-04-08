# 02_parse_receipt_text.py

import re
import pandas as pd
import os

# OCR結果ファイルを読み込み
ocr_path = 'data/ocr_output.txt'
if not os.path.exists(ocr_path):
    raise FileNotFoundError("OCR結果ファイルがありません。まず 01_receipt_ocr.py を実行してください。")

with open(ocr_path, 'r', encoding='utf-8') as f:
    text = f.read()

print("===== OCR読み取り結果（確認） =====")
print(text)
print("===================================")

# ① 日付抽出（例：2012年8月18日）
date_match = re.search(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日', text)
date = f"{date_match.group(1)}-{int(date_match.group(2)):02}-{int(date_match.group(3)):02}" if date_match else "不明"

# ② 品目＋金額の抽出
items = []
previous_line = ""

for line in text.splitlines():
    line = line.strip()
    if not line or len(line) < 2:
        continue

    # 金額だけの行（→前の行と結びつける）
    if re.fullmatch(r'[0-9０-９,，]{2,7}', line):
        price_str = line.replace(',', '').replace('，', '')
        price_str = price_str.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        try:
            price = int(price_str)
            if price < 50 or price > 2000:
                continue

            item = previous_line.strip()

            # 除外キーワード
            exclusion_keywords = ['合計', 'お買上高', 'お釣り', 'お預', '領収', '本込', '税込', '店', '電話', '現金', '消費']
            if any(x in item for x in exclusion_keywords):
                continue

            # 型番除去（「123-456 商品名」→「商品名」）
            item = re.sub(r'^[\d\-]+[\s　]*', '', item)
            item = re.sub(r'\s+[0-9]$', '', item)  # 数量削除

            items.append({"日付": date, "品目": item, "金額": price})
        except:
            continue
        continue

    # 1行に品目＋金額があるパターン
    match = re.search(r'(?P<item>.+?)\s+(?P<price>\d{2,6})$', line)
    if match:
        item = match.group("item").strip()
        price_str = match.group("price")

        try:
            price = int(price_str)
            if price < 50 or price > 2000:
                continue

            # 除外キーワード
            exclusion_keywords = ['合計', 'お買上高', 'お釣り', 'お預', '領収', '本込', '税込', '店', '電話', '現金', '消費']
            if any(x in item for x in exclusion_keywords):
                continue

            item = re.sub(r'^[\d\-]+[\s　]*', '', item)
            item = re.sub(r'\s+[0-9]$', '', item)

            items.append({"日付": date, "品目": item, "金額": price})
        except:
            continue

    # 次の金額行と結びつけるために保存
    previous_line = line

# ③ 表として表示（DataFrame）
df = pd.DataFrame(items)
print("\n===== 抽出された内容（表） =====")
print(df)

# ④ CSVとして保存
os.makedirs('data', exist_ok=True)
df.to_csv('data/parsed_receipt.csv', index=False, encoding='utf-8-sig')
print("\n✅ CSVとして保存しました：data/parsed_receipt.csv")
