import pandas as pd
import time
import os
from duckduckgo_search import DDGS


def search_facebook_link(camp_name):
    """DuckDuckGo ашиглан фэйсбүүк линкийг хурдан хайх функц"""
    search_query = f"{camp_name} facebook"
    try:
        # Блок хийгдэхгүйгээр шууд хайлтын илэрцийг авна
        with DDGS() as ddgs:
            results = ddgs.text(search_query, max_results=3)
            if results:
                for r in results:
                    url = r.get('href', '')
                    # Хэрэв Facebook-ийн бодит хуудас мөн байвал авна
                    if "facebook.com/" in url and not any(x in url for x in ["sharer", "pages/create", "groups"]):
                        # Линкийг цэвэрлэх
                        return url.split('?')[0]  # Хэрэггүй нууцлалын кодуудыг хасах
    except Exception as e:
        print(f" ⚠️ Хайлтад алдаа гарлаа ({camp_name}): {e}")
    return ""


# --- ҮНДСЭН ФАЙЛ ДЭЭР АЖИЛЛАХ ---
file_name = "Tourist_camps_multi.csv"

if os.path.exists(file_name):
    print(f"📖 {file_name} файлыг уншиж байна...")
    df = pd.read_csv(file_name)

    # Хэрэв Facebook багана байхгүй бол шинээр үүсгэх
    if 'Facebook' not in df.columns:
        df['Facebook'] = ""

    df['Facebook'] = df['Facebook'].fillna("")

    success_count = 0
    limit = 30  # Эхний ээлжинд аюулгүй байдлаар 30-ийг бөглөж туршина.

    print("\n⚡ DuckDuckGo ашиглан хурдан хайлтыг эхлүүлж байна...")
    print("-" * 55)

    for idx, row in df.iterrows():
        if success_count >= limit:
            print(f"\n🛑 Туршилтын хязгаар болох {limit} цэгт хүрлээ.")
            break

        name = row['Name_mon']
        current_fb = str(row['Facebook']).strip()

        # Хэрэв фэйсбүүк нь байхгүй бол хайна
        if not current_fb or current_fb == "" or current_fb == "nan":
            print(f"🔍 Хайж байна: {name} ...", end=" ", flush=True)
            found_url = search_facebook_link(name)

            if found_url:
                df.at[idx, 'Facebook'] = found_url
                print(f"✅ Олдлоо: {found_url}")
                success_count += 1
            else:
                print("❌ Олдсонгүй")

            # DuckDuckGo маш хурдан учраас ердөө 1-хэн секунд амрахад хангалттай
            time.sleep(1)

    # Хадгалах
    df.to_csv(file_name, index=False, encoding="utf-8")
    print("-" * 55)
    print(f"🎉 Дууслаа! {success_count} шинэ фэйсбүүк линкийг {file_name} файлд амжилттай нэмж хадгаллаа.")

else:
    print(f"❌ Алдаа: '{file_name}' файл олдсонгүй.")