import os
import pandas as pd

# Хоёр файлын нэрс
files = ["Nature_His_multi_translated.csv", "Tourist_camps_multi.csv"]

total_combined_count = 0
all_dfs = []

for file_path in files:
    print(f"\n========================================")
    print(f"Файл: {file_path}")
    print(f"========================================")

    if not os.path.exists(file_path):
        print(f"Алдаа: {file_path} файл олдсонгүй!")
        continue

    df = pd.read_csv(file_path)
    all_dfs.append(df)

    # 'Category' багана байгаа эсэхийг шалгах
    if "Category" not in df.columns:
        print(f"Алдаа: '{file_path}' дотор 'Category' багана олдсонгүй!")
        print("Баганууд:", df.columns.tolist())
    else:
        counts = df["Category"].value_counts()
        print(counts)
        print("-" * 40)
        print(f"Энэ файлын нийт цэг: {len(df)}")
        total_combined_count += len(df)

# Хэрэв хоёулаа амжилттай олдсон бол нийт дүнг гаргах
if all_dfs:
    combined_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\n========================================")
    print(f" БҮХ ФАЙЛЫН НИЙТ ДҮН")
    print(f"========================================")
    print(f"Нэгтгэсэн нийт цэгийн тоо: {len(combined_df)}")

    # Хэрэв бүх файлын категоруудыг нийлүүлж нэгдсэн байдлаар тоолмоор байвал:
    if "Category" in combined_df.columns:
        print("\n--- Бүх категоруудын нийт нэгдсэн тоо ---")
        print(combined_df["Category"].value_counts())