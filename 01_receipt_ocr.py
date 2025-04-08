import cv2
import pytesseract
from PIL import Image
import os

# Windowsの人だけ（Tesseractインストールパスに合わせて変更）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# レシート画像のファイルパス（画像名は自分のファイルに合わせて！）
image_path = 'receipts/20120820221619_original.jpg'

if not os.path.exists(image_path):
    raise FileNotFoundError(f"画像が見つかりません: {image_path}")

# ① 画像読み込み＆拡大
image = cv2.imread(image_path)
image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

# ② グレースケール化＆バイナリ化
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# ③ OCR実行
text = pytesseract.image_to_string(thresh, lang='jpn')

# ④ 結果出力
print("===== OCR結果 =====")
print(text)

# ⑤ 保存
os.makedirs('data', exist_ok=True)
with open('data/ocr_output.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print("\nOCR結果を data/ocr_output.txt に保存しました。")
