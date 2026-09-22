import pandas as pd
import numpy as np
from deep_translator import GoogleTranslator

# 1. Файлын зам
FILES = {
    "tourist": {
        "main": "Tourist_camps_multi.csv",
        "draft": "Tourist_draft.csv"
    },
    "nature": {
        "main": "Nature_His_multi_translated.csv",
        "draft": "Nature_draft.csv"
    }
}

# Орчуулгын зураглал (Монгол -> Бусад 5 хэл)
TRANSLATION_MAP = {
    'Name_eng': ('Name_mon', 'en'),
    'Name_kr': ('Name_mon', 'ko'),
    'Name_jp': ('Name_mon', 'ja'),
    'Name_cn': ('Name_mon', 'zh-CN'),
    'Name_ru': ('Name_mon', 'ru'),

    'Description_eng': ('Description_mon', 'en'),
    'Description_kor': ('Description_mon', 'ko'),
    'Description_jpn': ('Description_mon', 'ja'),
    'Description_zho': ('Description_mon', 'zh-CN'),
    'Description_rus': ('Description_mon', 'ru'),
}


def is_valid_coord(lat, lon):
    """Lat, Long шалгагч"""
    try:
        if pd.isna(lat) or pd.isna(lon):
            return False
        lat_val = float(str(lat).strip())
        lon_val = float(str(lon).strip())
        return (40.0 <= lat_val <= 53.0) and (85.0 <= lon_val <= 122.0)
    except (ValueError, TypeError):
        return False


def auto_translate_row(row):
    """Хоосон орчуулгуудыг нөхөх"""
    for target_col, (src_col, target_lang) in TRANSLATION_MAP.items():
        if target_col in row.index and src_col in row.index:
            src_text = str(row.get(src_col, '')).strip()
            target_val = str(row.get(target_col, '')).strip()

            if src_text and src_text.lower() != 'nan' and (not target_val or target_val.lower() == 'nan'):
                try:
                    translated = GoogleTranslator(source='mn', target=target_lang).translate(src_text)
                    row[target_col] = translated
                except Exception as e:
                    print(f"⚠️ Орчуулгын алдаа ({src_col} -> {target_col}): {e}")
    return row


def process_and_sort(category_name):
    main_file = FILES[category_name]["main"]
    draft_file = FILES[category_name]["draft"]

    try:
        main_df = pd.read_csv(main_file, encoding='utf-8-sig')
        draft_df = pd.read_csv(draft_file, encoding='utf-8-sig')
    except FileNotFoundError as e:
        print(f"❌ Файл олдсонгүй: {e}")
        return

    if draft_df.empty:
        print(f"ℹ️ [{category_name}] Драфт файл хоосон байна.")
        return

    # Координаттай хэсгийг шүүх
    coord_mask = draft_df.apply(lambda r: is_valid_coord(r.get('Lat'), r.get('Long')), axis=1)
    ready_to_move = draft_df[coord_mask].copy()
    still_draft = draft_df[~coord_mask].copy()

    if ready_to_move.empty:
        print(f"ℹ️ [{category_name}] Координат нь бөглөгдсөн шинэ цэг байхгүй байна.")
        return

    print(f"\n🚀 [{category_name}] {len(ready_to_move)} шинэ цэгийг боловсруулж байна...")

    # Автомат орчуулга хийх
    ready_to_move = ready_to_move.apply(auto_translate_row, axis=1)

    # Нэгтгэх
    updated_main = pd.concat([main_df, ready_to_move], ignore_index=True)

    # Аймаг, Сумаар нь ЭРЭМБЭЛЭХ (Сорт хийх)
    sort_cols = []
    if 'Aimag_name_mon' in updated_main.columns:
        sort_cols.append('Aimag_name_mon')
    if 'Sum_name_mon' in updated_main.columns:
        sort_cols.append('Sum_name_mon')
    if 'Name_mon' in updated_main.columns:
        sort_cols.append('Name_mon')

    if sort_cols:
        updated_main = updated_main.sort_values(by=sort_cols, ascending=True).reset_index(drop=True)

    # '№' дугаарлалтыг дахин шинэчлэх (1, 2, 3...)
    if '№' in updated_main.columns:
        updated_main['№'] = range(1, len(updated_main) + 1)

    # Хадгалах
    updated_main.to_csv(main_file, index=False, encoding='utf-8-sig')
    still_draft.to_csv(draft_file, index=False, encoding='utf-8-sig')

    print(f"✅ Амжилттай: {len(ready_to_move)} цэг {main_file} руу Аймаг, Сумын дагуу зөв байрлалд эрэмбэлэгдэн орлоо.")
    print(f"   - {draft_file} файлд {len(still_draft)} цэг үлдлээ.")


if __name__ == "__main__":
    process_and_sort("tourist")
    process_and_sort("nature")