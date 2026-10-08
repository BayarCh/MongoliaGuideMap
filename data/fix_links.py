import pandas as pd
import os

# 1. Тохиргоо
dropbox_path = r'C:\Users\DELL\Dropbox'
csv_files = {
    'Nature_His_multi.csv': 'Nature',
    'Tourist_camps_multi.csv': 'Tourism'
}


def fix_all_issues(file_name, subfolder):
    if not os.path.exists(file_name):
        print(f"❌ {file_name} олдсонгүй!")
        return

    # CSV-г бүх баганатай нь (орчуулгатай нь) унших
    df = pd.read_csv(file_name)

    # Зургуудыг авах
    img_folder = os.path.join(dropbox_path, subfolder)
    if os.path.exists(img_folder):
        photos = sorted([f for f in os.listdir(img_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

        # Photo_URL баганыг шинэчлэх (бусад багана хөндөгдөхгүй)
        new_links = []
        for i in range(len(df)):
            if i < len(photos):
                new_links.append(f"{subfolder}/{photos[i]}")
            else:
                new_links.append("")

        df['Photo_URL'] = new_links

        # UTF-8-SIG-ээр хадгалах (Монгол, Хятад, Орос үсгийг алдагдуулахгүй)
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        print(f"✅ {file_name} амжилттай засагдлаа. Баганууд: {list(df.columns)}")
    else:
        print(f"❌ Хавтас олдсонгүй: {img_folder}")


# 2. Гүйцэтгэх
for csv, folder in csv_files.items():
    fix_all_issues(csv, folder)