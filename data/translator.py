import pandas as pd
from deep_translator import GoogleTranslator
import time
import os

# 1. Тохиргоо (Файлын замаа та өөрийнхөөрөө тааруулаарай)
INPUT_FILE = r"Nature_His_multi.csv"
OUTPUT_FILE = r"Nature_His_multi_translated.csv"

# Хэрэв өмнө нь хэсэгчлэн хийсэн файл байвал түүнийг үргэлжлүүлж уншина
if os.path.exists(OUTPUT_FILE):
    df = pd.read_csv(OUTPUT_FILE, encoding='utf-8-sig')
else:
    df = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')

# Орчуулах хэлнүүд
languages = {
    'kor': 'ko',    # Солонгос
    'jpn': 'ja',    # Япон
    'zho': 'zh-CN', # Хятад
    'rus': 'ru'     # Орос
}

# 2. Эх үүсвэр багана (Description_eng байхгүй бол Description_mon-оос уншина)
source_col = 'Description_eng' if 'Description_eng' in df.columns else 'Description_mon'
print(f"Эх үүсвэр тайлбар багана: {source_col}")

# 3. Орчуулах функц
for lang_suffix, lang_code in languages.items():
    col_name = f'Description_{lang_suffix}'

    # Хэрэв багана байхгүй бол хоосон утгаар үүсгэх
    if col_name not in df.columns:
        df[col_name] = ""

    print(f"\n--- {lang_code} хэл рүү тайлбарыг орчуулж байна... ---")
    translator = GoogleTranslator(source='auto', target=lang_code)

    for index, text in enumerate(df[source_col]):
        # Хэрэв аль хэдийн орчуулагдсан бол алгасах
        if pd.notnull(df.loc[index, col_name]) and str(df.loc[index, col_name]).strip() != "" and df.loc[index, col_name] != "Translation Error":
            continue

        try:
            if pd.notnull(text) and str(text).strip() != "" and str(text).strip().lower() != 'nan':
                result = translator.translate(str(text))
                df.at[index, col_name] = result  # Шууд тухайн нүдэнд нь хадгалах
                time.sleep(0.5)  # 0.5 секунд хүлээх (арай хурдан)

                if index % 20 == 0:
                    print(f"{index}-р мөр амжилттай...")
            else:
                df.at[index, col_name] = ""
        except Exception as e:
            print(f"⚠️ {index}-р мөр саатал: {e}. Эх бичвэрийг хэвээр үлдээлээ.")
            df.at[index, col_name] = str(text)
            time.sleep(2)

    # Хэл бүрийн дараа шууд хадгалах
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"✅ Description_{lang_suffix} багана амжилттай хадгалагдлаа.")

print("\n🎉 БҮХ ТАЙЛБАР АМЖИЛТТАЙ ОРЧУУЛАГДАЖ ДУУСЛАА!")