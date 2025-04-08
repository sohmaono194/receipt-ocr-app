# 03_visualize_expenses.py

import pandas as pd
import matplotlib.pyplot as plt
import os

csv_path = 'data/parsed_receipt.csv'

if not os.path.exists(csv_path):
    raise FileNotFoundError("parsed_receipt.csv が見つかりません。Step 2 を実行してください。")

df = pd.read_csv(csv_path)

print("===== 読み込んだデータ =====")
print(df)

total = df["金額"].sum()
print(f"\n💰 合計支出：{total} 円")

# 円グラフ（品目別）
plt.figure(figsize=(6, 6))
plt.pie(df["金額"], labels=df["品目"], autopct="%1.1f%%", startangle=140)
plt.title("📦 支出の内訳（品目別）")
plt.tight_layout()
plt.show()

# 棒グラフ（日付ごとの合計）
plt.figure(figsize=(8, 4))
grouped = df.groupby("日付")["金額"].sum().reset_index()
plt.bar(grouped["日付"], grouped["金額"])
plt.xlabel("日付")
plt.ylabel("金額（円）")
plt.title("📅 日別支出")
plt.tight_layout()
plt.show()
