import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster, Search, LocateControl


# 1. МАРКЕР НЭМЭХ ФУНКЦ

def add_markers_by_type(df, nature_grp, hist_grp, relig_grp, camp_grp, resort_grp, sanatorium_grp, child_grp,
                        service_grp, transport_grp, search_grp):
    df.columns = df.columns.str.strip()
    df = df.fillna("")
    default_logo = "https://github.com/MongoliaMapGuide/map/blob/main/logo512.png?raw=true"

    for index, row in df.iterrows():
        # 🟢 1. Координат шалгах
        try:
            lat = float(row.get('Lat', 0))
            long = float(row.get('Long', 0))  # Таны CSV дээр 'Long' гэж байгаа тул
            if lat == 0 or long == 0: continue
        except:
            continue

        # 🟢 2. Мэдээллүүдийг авах (Олон хэлний орчуулга багтсан)
        name_en = str(row.get('Name_eng', '')).strip().upper()
        name_mn = str(row.get('Name_mon', '')).strip()
        aimag_mn = str(row.get('Aimag_name_mon', '')).strip()
        sum_mn = str(row.get('Sum_name_mon', '')).strip()
        phone = str(row.get('Phone', '')).strip()
        photo = str(row.get('Photo_URL', '')).strip()

        # Point_type-ийг бүхэл тоо болгох (1-12)
        try:
            p_val = int(float(row.get('Point_type', 0)))
        except:
            p_val = 0

        # 🎨 3. ШИНЭЧЛЭГДСЭН ТОН ЛОГИК (1-12)
        # Default утгууд
        target_grp, icon_name, icon_color = nature_grp, 'leaf', 'gray'

        if p_val == 1:  # Байгаль
            target_grp, icon_name, icon_color = nature_grp, 'mountain-sun', '#4CAF50'
        elif p_val == 2:  # Түүх
            target_grp, icon_name, icon_color = hist_grp, 'monument', '#2E7D32'
        elif p_val == 3:  # Шашин
            target_grp, icon_name, icon_color = relig_grp, 'om', '#FF9800'
        elif p_val == 4:  # Жуулчны бааз
            target_grp, icon_name, icon_color = camp_grp, 'tents', '#673AB7'
        elif p_val == 5:  # Амралтын газар
            target_grp, icon_name, icon_color = resort_grp, 'hotel', '#009688'
        elif p_val == 6:  # Сувилал
            target_grp, icon_name, icon_color = sanatorium_grp, 'kit-medical', '#E91E63'
        elif p_val == 7:  # Хүүхдийн зуслан
            target_grp, icon_name, icon_color = child_grp, 'child-reaching', '#FF4081'
        elif p_val == 8:  # Нисэх буудал
            target_grp, icon_name, icon_color = transport_grp, 'plane', '#00838F'
        elif p_val == 9:  # Төмөр замын өртөө
            target_grp, icon_name, icon_color = transport_grp, 'train', '#0097A7'
        elif p_val == 10:  # Хилийн боомт
            target_grp, icon_name, icon_color = transport_grp, 'archway', '#00ACC1'
        elif p_val == 11:  # Замын гуанз
            target_grp, icon_name, icon_color = service_grp, 'utensils', 'orange'
        elif p_val == 12:  # ШТС (Колонко)
            target_grp, icon_name, icon_color = service_grp, 'gas-pump', 'red'

        # 🖼️ 4. ЗУРАГ БОЛОВСРУУЛАХ
        if photo and "http" in photo.lower():
            img_src = photo.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0", "raw=1")
            img_tag = f'<img src="{img_src}" onerror="this.src=\'{default_logo}\';" style="width:100%; height:160px; object-fit:cover; border-radius:12px 12px 0 0;">'
        else:
            # Зураггүй бол default логог "гоёор" харуулна
            img_tag = f'<div style="width:100%; height:160px; background:#f5f5f5; display:flex; align-items:center; justify-content:center; border-radius:12px 12px 0 0;"><img src="{default_logo}" style="width:100px;"></div>'

        # 📝 5. POPUP HTML (Таны илгээсэн загвараар шинэчилсэн)
        import React,
        {useState}
        from
        'react';
        import
        './PopupCard.css'; // CSS
        загваруудыг
        тусад
        нь
        оруулна

        function
        PopupCard({title, location, phone, coordinates, descriptionMon, descriptionEng})
        {
            const[open, setOpen] = useState(false);

        return (
            < div className="popup-card" >
            < h3 > {title} < / h3 >
            < p > {location} < / p >
            {phone & & < p > 📞 < a href={`tel:${phone}`} > {phone} < / a > < / p >}
            < p > 🌐 GPS: {coordinates} < / p >

            < div className="popup-buttons" >
            < button className="primary" > View on Google Maps < / button >
            < button className="secondary" onClick={() = > setOpen(!open)} >
        {open ? 'Hide info': 'More info'}
        < / button >
            < / div >

                < div
        className = {`more - info ${open ? 'open': ''}`} >
        < h4 >🇲🇳 Description(Монгол) < / h4 >
                                         < p > {descriptionMon} < / p >
                                                                    < h4 >🇬🇧 Description(English) < / h4 >
                                                                                                      < p > {
                                                                                                          descriptionEng} < / p >
                                                                                                                              < / div >
                                                                                                                                  < / div >
        );
        }

        export
        default
        PopupCard;

        # 📍 6. МАРКЕР ЗУРАХ (FontAwesome багтсан)
        folium.Marker(
            location=[lat, long],
            popup=folium.Popup(popup_html, max_width=260),
            icon=folium.Icon(color='white', icon_color=icon_color, icon=icon_name, prefix='fa')
        ).add_to(target_grp)

        # 🔍 7. ХАЙЛТЫН ДАВХАРГА (Давхарласан шүүлтүүр)
        folium.GeoJson(
            data={"type": "Feature", "geometry": {"type": "Point", "coordinates": [long, lat]},
                  "properties": {"name": f"{name_en} {name_mn}"}},
            marker=folium.CircleMarker(radius=0, fill_color='#ffffff00', color='#ffffff00'),
            popup=folium.Popup(popup_html, max_width=260)
        ).add_to(search_grp)

# 2. ҮНДСЭН ХЭСЭГ (Main хэсэг хэвээрээ)
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    m = folium.Map(location=[47.0, 103.0], zoom_start=6, tiles=None)

    folium.TileLayer('OpenStreetMap', name='🌐 Street Map').add_to(m)
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google',
                     name='🛰️ Satellite').add_to(m)
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', attr='Google',
                     name='⛰️ Terrain Map').add_to(m)

    # Группүүд
    nature_grp = MarkerCluster(name="🏞️ Natural Wonders").add_to(m)
    hist_grp = MarkerCluster(name="🏛️ Historical Sites").add_to(m)
    relig_grp = MarkerCluster(name="🕉️ Religious Sites").add_to(m)
    camp_grp = MarkerCluster(name="⛺ Tourist Camps").add_to(m)
    resort_grp = MarkerCluster(name="🏢 Resorts").add_to(m)
    sanatorium_grp = MarkerCluster(name="🏥 Sanatoriums").add_to(m)
    child_grp = MarkerCluster(name="🧒 Children's Camps").add_to(m)
    service_grp = MarkerCluster(name="🍽️ Roadside Service").add_to(m)
    transport_grp = MarkerCluster(name="✈️ Transport").add_to(m)
    search_grp = folium.FeatureGroup(name="Search Layer", control=False).add_to(m)

    try:
        df = pd.read_csv(os.path.join(current_dir, "Tourist_camps_multi.csv"))
        nature_path = os.path.join(current_dir, "Nature_His_multi.csv")
        if os.path.exists(nature_path):
            df_nature = pd.read_csv(nature_path)
            if 'Category_eng' not in df_nature.columns:
                df_nature['Category_eng'] = 'Nature & History'
            df = pd.concat([df, df_nature], ignore_index=True)

        add_markers_by_type(df, nature_grp, hist_grp, relig_grp, camp_grp, resort_grp, sanatorium_grp, child_grp,
                            service_grp, transport_grp, search_grp)
    except Exception as e:
        print(f"Error: {e}")
        from folium.plugins import FloatImage

        # Логоны URL (GitHub дээрх шууд линк байвал сайн)
        logo_url = "https://github.com/MongoliaMapGuide/map/blob/main/logo512.png?raw=true"

        # Байршил: bottom=5 (доороос 5%), left=1 (зүүнээс 1%)
        FloatImage(logo_url, bottom=5, left=1).add_to(m)

    Search(layer=search_grp, geom_type='Point', placeholder='Хайх...', collapsed=False, search_label='name').add_to(m)
    LocateControl().add_to(m)
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    < div


    class ="popup-card" >

    < img
    src = "images/khubsugul.jpg"
    alt = "Khubsugul Dalai Tourist Camp" >
    < h3 > KHUBSUGUL
    DALAI
    TOURIST
    CAMP < / h3 >
    < p > Хөвсгөл
    далай
    жуулчны
    бааз < / p >
    < button


    class ="more-info-btn" > More info < / button >

    < div


    class ="more-info" >

    < h4 >🇲🇳 Description(Монгол) < / h4 >
    < p > Хөвсгөл
    далай
    жуулчны
    бааз
    нь
    Хөвсгөл
    нуурын
    эрэг
    дээр
    байрлах... < / p >
    < h4 >🇬🇧 Description(English) < / h4 >
    < p > Khubsugul
    Dalai
    Tourist
    Camp is located
    on
    the
    shore
    of
    Lake
    Khubsugul... < / p >
< / div >
< / div >

# Баруун доод буланд харагдах Share товчлууруудын код (Хамгийн шахсан хувилбар)
    share_buttons_html = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">

    <div style="position: fixed; 
                bottom: 20px; /* <--- Хуучин байранд нь буцаав */
                right: 15px; 
                z-index: 10000; 
                background: rgba(255, 255, 255, 0.95); 
                padding: 6px 5px; /* <--- Доторх зайг маш бага болгов */
                border-radius: 25px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                display: flex;
                flex-direction: column;
                gap: 4px; /* <--- Айкон хоорондын зайг 4px болгож шахлаа */
                align-items: center;
                width: 36px; 
                border: 1px solid #fff;">

        <a href="https://t.me/share/url?url={url}" target="_blank" style="color: #0088cc; font-size: 20px; line-height: 1.1;" title="Telegram">
            <i class="fa-brands fa-telegram"></i>
        </a>
        <a href="https://api.whatsapp.com/send?text={url}" target="_blank" style="color: #25D366; font-size: 20px; line-height: 1.1;" title="WhatsApp">
            <i class="fa-brands fa-whatsapp"></i>
        </a>
        <a href="https://twitter.com/intent/tweet?url={url}" target="_blank" style="color: #000; font-size: 18px; line-height: 1.1;" title="X (Twitter)">
            <i class="fa-brands fa-x-twitter"></i>
        </a>
        <a href="https://www.linkedin.com/sharing/share-offsite/?url={url}" target="_blank" style="color: #0077b5; font-size: 20px; line-height: 1.1;" title="LinkedIn">
            <i class="fa-brands fa-linkedin"></i>
        </a>
        <div style="width: 20px; border-top: 1px solid #eee; margin: 2px 0;"></div>
        <a href="https://github.com/bayarchoijil" target="_blank" style="color: #333; font-size: 20px; line-height: 1.1;" title="GitHub">
            <i class="fa-brands fa-github"></i>
        </a>
    </div>
    """.format(url="https://mongoliamapguide.github.io/map/")
    # --- VISITORS: ӨНӨӨДӨР / НИЙТ (Visitorbadge API) ---
    # Энэ хэсгийг бүхлээр нь хуулж өмнөх counter_html-ээ сольно
    counter_html = """
    <div style="position: fixed; 
                bottom: 20px; left: 20px; 
                z-index:9999; 
                display: flex;
                flex-direction: column;
                gap: 8px;">

       <div style="display: flex; gap: 6px;">
            <a href="https://www.facebook.com/sharer/sharer.php?u=https://mongoliamapguide.github.io/map/" 
               target="_blank" 
               style="background-color: #1877F2; color: white; padding: 6px 12px; border-radius: 50px; 
                      text-decoration: none; font-family: Arial, sans-serif; font-size: 11px; font-weight: bold;
                      display: flex; align-items: center; box-shadow: 0px 4px 10px rgba(0,0,0,0.2);">
               <i class="fa-brands fa-facebook" style="margin-right: 5px;"></i> Share
            </a>

           <a href="#" 
               onclick="shareOnMessenger(); return false;"
               style="background-color: #0084FF; color: white; padding: 6px 12px; border-radius: 50px; 
                      text-decoration: none; font-family: Arial, sans-serif; font-size: 11px; font-weight: bold;
                      display: flex; align-items: center; box-shadow: 0px 4px 10px rgba(0,0,0,0.2);">
               <i class="fa-brands fa-facebook-messenger" style="margin-right: 5px;"></i> Send
            </a>

            <script>
            function shareOnMessenger() {
                var url = "https://mongoliamapguide.github.io/map/";
                var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
                if (isMobile) {
                    window.location.href = "fb-messenger://share/?link=" + encodeURIComponent(url);
                } else {
                    window.open("https://www.facebook.com/dialog/send?app_id=1210892749527211&link=" + encodeURIComponent(url) + "&redirect_uri=" + encodeURIComponent(url), "_blank");
                }
            }
            </script>
        </div>

        <div style="display: flex; align-items: center; width: fit-content; border-radius: 6px; overflow: hidden; box-shadow: 0px 2px 8px rgba(0,0,0,0.15);">
            <img src="https://api.visitorbadge.io/api/combined?path=https%3A%2F%2Fbayarchoijil.github.io%2Fmap%2F&labelColor=%2327ae60&countColor=%23555555&style=flat" 
                 alt="visitor badge" style="height: 22px; vertical-align: middle;">
        </div>
    </div>

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    # Баруун доод буланд байрлах сошиал товчлуурууд (HTML/CSS)
bottom_right_buttons = """
<div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 8px; align-items: flex-end;">
    <a href="https://t.me/share/url?url=https://bayarchoijil.github.io/Travel_Map_MN/" target="_blank"
       style="background: #0088cc; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-telegram"></i>
    </a>
    <a href="https://twitter.com/intent/tweet?url=https://bayarchoijil.github.io/Travel_Map_MN/" target="_blank"
       style="background: #000000; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-x-twitter"></i>
    </a>
    <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://bayarchoijil.github.io/Travel_Map_MN/" target="_blank"
       style="background: #0077b5; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-linkedin-in"></i>
    </a>
    <a href="https://github.com/Bayarchoijil/Travel_Map_MN" target="_blank"
       style="background: #333; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-github"></i>
    </a>
</div>

<style>
    /* Folium-ийн Layer Control-ийг товчлууруудын дээр гаргахын тулд бага зэрэг дээшлүүлнэ */
    .leaflet-bottom.leaflet-right {
        bottom: 200px !important;
    }
</style>
    """
    # Таны 191-р мөрөнд байгаа код одоо алдаагүй ажиллана
    m.get_root().html.add_child(folium.Element(counter_html))

    m.save(os.path.join(current_dir, "index.html"))
    print("✨ Газрын зураг амжилттай үүслээ!")
