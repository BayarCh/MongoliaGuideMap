import pandas as pd

# 1. Хоёр файлаа унших
tourist_df = pd.read_csv("Tourist_camps_multi.csv")
nature_df = pd.read_csv("Nature_His_multi.csv")

# 2. Зөвхөн хэрэгцээт багануудыг авч нэгтгэх
combined_df = pd.concat([
    tourist_df[['Point_type', 'Category']],
    nature_df[['Point_type', 'Category']]
], ignore_index=True)

# 3. Ангиллын нэрсийн зураглал (Mapping)
point_type_mapping = {
    1: "Natural Wonders (Байгалийн үзэсгэлэнт газар)",
    2: "Historical Sites (Түүхийн дурсгалт газар)",
    3: "Religious Sites (Шашны дурсгалт газар)",
    4: "Tourist_Camp (Жуулчны бааз)",
    5: "Resort (Амралтын газар)",
    6: "Spa_Resort (Рашаан/Саам сувилал)",
    7: "Children_Summer_Camp (Хүүхдийн зуслан)",
    8: "Airport (Нисэх буудал)",
    9: "Railway_Station (Төмөр замын өртөө)",
    10: "Border Crossing (Хилийн боомт)",
    11: "Roadside_Diner (Замын гуанз)",
    12: "Gas_Station (Шатахуун түгээх станц)"
}

# 4. Тоолох ба хэвлэх
combined_df['Point_type_Name'] = combined_df['Point_type'].map(point_type_mapping)
counts = combined_df['Point_type_Name'].value_counts().reindex(point_type_mapping.values(), fill_value=0)

print("--- ЦЭГИЙН ТӨРӨЛ БҮРИЙН ТОО ---")
for idx, (name, count) in enumerate(counts.items(), 1):
    print(f"{idx}. {name}: {count}")

print(f"\nНийт цэгийн тоо: {counts.sum()}")