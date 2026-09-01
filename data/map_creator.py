import os
import pandas as pd
import folium
from folium.plugins import LocateControl, Search, MarkerCluster, MeasureControl
# 1. Үндсэн зам болон тохиргоо
current_dir = os.path.dirname(os.path.abspath(__file__))

# Унших CSV файлуудын жагсаалт (Translate хийсэн файл руугаа заана)
DATA_FILES = ["Tourist_camps_multi.csv", "Nature_His_multi_translated.csv"]

# Файлуудыг нэгтгэж унших
dfs = []
for file in DATA_FILES:
    file_path = os.path.join(current_dir, file)
    dfs.append(pd.read_csv(file_path))

df = pd.concat(dfs, ignore_index=True)
df.columns = df.columns.str.strip()
df = df.fillna("")

# 2. ГАЗРЫН ЗУРАГ ҮҮСГЭХ
m = folium.Map(
    location=[47.0, 103.0],
    zoom_start=6,
    tiles=None,
    max_zoom=17,
    control_scale=True
)
# Суурь давхаргууд нэмэх
folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr='&copy; OpenTopoMap contributors',
    name="OpenTopoMap",
    overlay=False,
    control=True
).add_to(m)

folium.TileLayer('OpenStreetMap', name='🌐 Street Map').add_to(m)
folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google', name='🛰️ Satellite').add_to(
    m)
folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', attr='Google',
                 name='⛰️ Terrain Map').add_to(m)

# 3. КЛАСТЕР ГРУППҮҮД БОЛОН ИКОН ТОХИРУУЛГА
nature_grp = MarkerCluster(name='🏞️ Natural Wonders').add_to(m)
hist_grp = MarkerCluster(name='🏛️ Historical Sites').add_to(m)
relig_grp = MarkerCluster(name='🕉️ Religious Sites').add_to(m)
camp_grp = MarkerCluster(name='⛺ Tourist Camps').add_to(m)
resort_grp = MarkerCluster(name='🏢 Resorts').add_to(m)
sanatorium_grp = MarkerCluster(name='🏥 Sanatoriums').add_to(m)
child_grp = MarkerCluster(name='🧒 Children\'s Camps').add_to(m)
service_grp = MarkerCluster(name='🍽️ Roadside Service').add_to(m)
transport_grp = MarkerCluster(name='✈️ Transport').add_to(m)

groups_dict = {
    1: (nature_grp, 'mountain', '#4CAF50'),
    2: (hist_grp, 'landmark', '#2E7D32'),
    3: (relig_grp, 'om', '#FF9800'),
    4: (camp_grp, 'campground', '#673AB7'),
    5: (resort_grp, 'hotel', '#009688'),
    6: (sanatorium_grp, 'briefcase-medical', '#E91E63'),
    7: (child_grp, 'child', '#FF4081'),
    8: (transport_grp, 'plane', '#00838F'),
    9: (transport_grp, 'train', '#0097A7'),
    10: (transport_grp, 'archway', '#00ACC1'),
    11: (service_grp, 'utensils', 'orange'),
    12: (service_grp, 'gas-pump', 'red')
}

search_grp = folium.FeatureGroup(name="Search Layer", control=False).add_to(m)


# 4. МАРКЕР НЭМЭХ ФУНКЦ (Дутуу байсан үндсэн логик)
import pandas as pd
import folium

def add_markers_by_type(df, groups, search_layer, default_logo="https://via.placeholder.com/280x150?text=No+Image"):
    df.columns = df.columns.str.strip()
    df = df.fillna("")
    def build_popup_html(row):
        default_logo = "https://github.com/BayarCh/MongoliaGuideMap/blob/main/logo512.png?raw=true"

    # --- ДАВТАЛТ ФУНКЦИЙН ДОТОР ОРНО ---
    for index, row in df.iterrows():
        try:
            lat = float(row.get('Lat', 0))
            long = float(row.get('Long', 0))
            if lat == 0 or long == 0:
                continue

            p_val = int(float(row.get('Point_type', 1)))

            # 1. ТАЙЛБАРУУДЫГ АЮУЛГҮЙ УНШИЖ ЦЭВЭРЛЭХ
            def clean_desc(val):
                d = str(val).strip()
                return "" if d.lower() in ['nan', 'none', 'null', ''] else d

            desc_mon = clean_desc(row.get('Description_mon', ''))
            desc_eng = clean_desc(row.get('Description_eng', ''))
            desc_kor = clean_desc(row.get('Description_kor', row.get('Description_kr', '')))
            desc_jpn = clean_desc(row.get('Description_jpn', row.get('Description_jp', '')))
            desc_zho = clean_desc(row.get('Description_zho', row.get('Description_cn', '')))
            desc_rus = clean_desc(row.get('Description_rus', row.get('Description_ru', '')))

            # 2. НЭРҮҮДИЙГ ЦЭВЭРЛЭХ
            name_mn = str(row.get('Name_mon', '-')).replace("'", "\\'").strip()
            name_en = str(row.get('Name_eng', '-')).replace("'", "\\'").strip().upper()
            name_kr = str(row.get('Name_kr', '-')).replace("'", "\\'").strip()
            name_jp = str(row.get('Name_jp', '-')).replace("'", "\\'").strip()
            name_cn = str(row.get('Name_cn', '-')).replace("'", "\\'").strip()
            name_ru = str(row.get('Name_ru', '-')).replace("'", "\\'").strip()

            aimag_en = str(row.get('Aimag_name_eng', '-')).strip()
            sum_en = str(row.get('Sum_name_eng', '-')).strip()
            photo = str(row.get('Photo_URL', '')).strip()
            phone_val = str(row.get('Phone', '')).strip()
            phone_display = phone_val if phone_val.lower() not in ['nan', 'none', '', '0'] else None

            final_img = photo.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0", "raw=1") if "http" in photo.lower() else default_logo

            target_grp, icon_name, icon_color = groups.get(p_val, (None, 'leaf', 'gray'))
            if target_grp is None:
                continue

            kr_title = name_kr if name_kr and name_kr != '-' else name_en
            jp_title = name_jp if name_jp and name_jp != '-' else name_en
            cn_title = name_cn if name_cn and name_cn != '-' else name_en
            ru_title = name_ru if name_ru and name_ru != '-' else name_en

            lang_section_html = f"""
            <div class="pop-lang-fixed" style="display: block;">
                <div style="color: #555; font-size: 12px; font-weight: 500; margin-bottom: 8px; line-height: 1.3;">🇬🇧 {name_en}</div>
            </div>
            """

            # Сошиал / Холбоос холбох
            # Сошиал / Холбоос холбох (Олон линкийг салгаж цувруулах)
            import re

            fb_raw = str(
                row.get('Facebook', '')).strip()  # Хэрэв багачны нэр өөр бол энд солино (жишээ нь 'Social_Links')
            link_html = ""

            if fb_raw and fb_raw.lower() != 'nan':
                # Таслал, цэгтэй таслал эсвэл зайгаар тусгаарлагдсан олон линк байвал салгаж авна
                raw_links = re.split(r'[,;\s]+', fb_raw)

                for link in raw_links:
                    link = link.strip()
                    if not link:
                        continue

                    full_url = f"https://{link}" if not link.startswith(('http://', 'https://')) else link

                    # Линкийн төрлийг шалгаж зохих загварыг үүсгэх
                    if "facebook.com" in full_url.lower() or "fb.com" in full_url.lower():
                        link_html += f'<div style="margin-bottom: 5px;">🔵 <b>Facebook:</b> <a href="{full_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:#1877F2; font-weight: 600;">Visit Facebook Page</a></div>'
                    elif "instagram.com" in full_url.lower():
                        link_html += f'<div style="margin-bottom: 5px;">📸 <b>Instagram:</b> <a href="{full_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:#E4405F; font-weight: 600;">Visit Instagram Page</a></div>'
                    elif "youtube.com" in full_url.lower() or "youtu.be" in full_url.lower():
                        link_html += f'<div style="margin-bottom: 5px;">▶️ <b>YouTube:</b> <a href="{full_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:#FF0000; font-weight: 600;">Visit YouTube Channel</a></div>'
                    elif "t.me" in full_url.lower() or "telegram" in full_url.lower():
                        link_html += f'<div style="margin-bottom: 5px;">✈️ <b>Telegram:</b> <a href="{full_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:#0088cc; font-weight: 600;">Visit Telegram</a></div>'
                    else:
                        link_html += f'<div style="margin-bottom: 5px;">🌐 <b>Website:</b> <a href="{full_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:#008080; font-weight: 600;">Visit Official Website</a></div>'

            # Тайлбар харуулах загвар стилийг бэлдэх туслах функц
            def render_desc_box(desc_text):
                if not desc_text:
                    return ""
                return f'<div style="font-size: 11px; color: #555; line-height: 1.4; max-height: 90px; overflow-y: auto; background: #f8f9fa; padding: 6px 8px; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid #1a73e8;">{desc_text}</div>'

            # 3. ПОПАП HTML
            popup_html = f"""
            <div style="width: 280px; min-width: 280px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.15); display: flex; flex-direction: column;">
                <a href="{final_img}" target="_blank" title="Зургийг томсгож үзэх" style="text-decoration: none; display: block; position: relative; cursor: pointer !important;">
                    <div style="width: 100%; max-height: 225px; overflow: hidden; margin: 0; padding: 0; line-height: 0; background: white; display: flex; align-items: center; justify-content: center;">
                        <img src="{final_img}" style="width: 100%; height: auto; min-height: 225px; object-fit: cover; object-position: center; display: block; margin: 0; border: none; cursor: pointer !important;" onerror="this.src='https://via.placeholder.com/280x150?text=No+Image'">
                    </div>
                    <div style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.6); color: white; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-family: sans-serif; pointer-events: none;">🔍 Zoom in</div>
                </a>
                <div style="padding: 10px 15px 15px 15px; margin-top: -1px; background: white; position: relative; z-index: 2;">
                    <!-- 🇲🇳 MONGOLIAN -->
                    <div class="pop-lang lang-mn" style="display: block;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 6px 0; line-height: 1.2;">{name_mn}</div>
                        {render_desc_box(desc_mon)}
                    </div>

                    <!-- 🇬🇧 ENGLISH -->
                    <div class="pop-lang lang-en" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 6px 0; line-height: 1.2;">{name_en}</div>
                        {render_desc_box(desc_eng)}
                    </div>

                    <!-- 🇰🇷 KOREAN -->
                    <div class="pop-lang lang-kr" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 6px 0; line-height: 1.2;">{kr_title}</div>
                        {render_desc_box(desc_kor)}
                    </div>

                    <!-- 🇯🇵 JAPANESE -->
                    <div class="pop-lang lang-jp" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 6px 0; line-height: 1.2;">{jp_title}</div>
                        {render_desc_box(desc_jpn)}
                    </div>

                    <!-- 🇨🇳 CHINESE -->
                    <div class="pop-lang lang-cn" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 6px 0; line-height: 1.2;">{cn_title}</div>
                        {render_desc_box(desc_zho)}
                    </div>

                    <!-- 🇷🇺 RUSSIAN -->
                    <div class="pop-lang lang-ru" style="display: none;">
                        <div style="color: #1a73e8; font-size: 15px; font-weight: 800; text-transform: uppercase; margin: 0 0 6px 0; line-height: 1.2;">{ru_title}</div>
                        {render_desc_box(desc_rus)}
                    </div>

                    {lang_section_html}

                    <div style="font-size: 11px; color: #444; margin-bottom: 10px; line-height: 1.4; border-top: 1px solid #f5f5f5; padding-top: 10px;">
                        <div style="margin-bottom: 5px;">Location: {sum_en} <b>{aimag_en}</b></div>
                        {f'<div style="margin-bottom: 5px;">Phone: <a href="tel:{phone_display}" style="text-decoration:none; color:#1a73e8; font-weight: 600;">{phone_display}</a></div>' if phone_display else ''}
                        {link_html}
                        <div style="margin-top: 8px; color: #555; background: #f8f9fa; padding: 8px; border-radius: 6px; border-left: 3px solid #1a73e8;">
                            <b>GPS:</b> <span style="user-select: all; cursor: pointer; font-family: monospace;">{lat}, {long}</span>
                        </div>
                    </div>
                    <a href="https://www.google.com/maps/search/?api=1&query={lat},{long}" target="_blank" style="display: block; background: #1a73e8; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px; box-shadow: 0 2px 5px rgba(26,115,232,0.3);">
                        🚀 View on Google Maps
                    </a>
                </div>
            </div>
            """

            # 4. МАРКЕРУУДЫГ НЭМЭХ
            icon_html = f'<div style="background-color: {icon_color}; border: 2px solid white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.4);"><i class="fa-solid fa-{icon_name}" style="font-size: 14px;"></i></div>'

            folium.Marker(
                location=[lat, long],
                popup=folium.Popup(popup_html, max_width=280, min_width=280, max_height=425),
                icon=folium.DivIcon(icon_size=(32, 32), icon_anchor=(16, 16), html=icon_html)
            ).add_to(target_grp)

            s_marker = folium.CircleMarker(
                location=[lat, long], radius=5, weight=0, fill_color="rgba(0,0,0,0)", color="rgba(0,0,0,0)",
                popup=folium.Popup(popup_html, max_width=280, min_width=280, max_height=425)
            )
            s_marker.options['search_label'] = f"{name_mn} {name_en}".strip()
            s_marker.add_to(search_layer)

        except Exception as e:
            print(f"Мөр {index} дээр алдаа гарлаа: {e}")
            continue


# Өгөгдлийн файлуудыг унших
df_all = pd.DataFrame()
for f in DATA_FILES:
    if os.path.exists(f):
        df_temp = pd.read_csv(f)
        df_all = pd.concat([df_all, df_temp], ignore_index=True)

if not df_all.empty:
    add_markers_by_type(df_all, groups_dict, search_grp)

# 5. ХЭРЭГСЛҮҮД БОЛОН ХАЙЛТ НЭМЭХ
MeasureControl(position='topleft', primary_length_unit='kilometers', secondary_length_unit='miles',
               primary_area_unit='sqmeters').add_to(m)
LocateControl().add_to(m)
folium.LayerControl(position='topright', collapsed=False).add_to(m)

Search(
    layer=search_grp,
    geom_type='Point',
    placeholder='Хайх...',
    collapsed=True,
    search_label='search_label'
).add_to(m)

# 6. HEADERS & META TAGS
header_html = """
<title>TravelMap.mn - Mongolia Travel Guide</title>
<meta name="description" content="Interactive travel guide map of Mongolia.">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="shortcut icon" href="/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="/logo180.png">
<link rel="manifest" href="/manifest.json">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#1a73e8">

<meta property="og:title" content="TravelMap.mn - Mongolia Travel Guide">
<meta property="og:description" content="Interactive travel guide map of Mongolia.">
<meta property="og:image" content="https://travelmap.mn/logo1200x630.png">
<meta property="og:url" content="https://travelmap.mn">
<meta property="og:type" content="website">

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
"""
m.get_root().header.add_child(folium.Element(header_html))

# 7. GOOGLE ANALYTICS
analytics_code = """
<script async src="https://www.googletagmanager.com/gtag/js?id=G-345SKF986B"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-345SKF986B');
</script>
"""
m.get_root().header.add_child(folium.Element(analytics_code))

# 8. MAP CLICK JS (Google Form Point Picker)
click_js = """
<script>
function onMapClick(e) {
     var lat = e.latlng.lat.toFixed(6);
     var lng = e.latlng.lng.toFixed(6);
     var baseUrl = "https://docs.google.com/forms/d/e/1FAIpQLScNMWMTA4oZpFV2vMeYu8uUJx22Xo8-j_TrjrJY9wppwmn4DQ/viewform?usp=pp_url&entry.711679500=";
     var formUrl = baseUrl + lat + "," + lng;

     var content = '<div style="text-align: left; font-family: sans-serif; min-width: 220px; padding: 15px 25px 10px 18px; box-sizing: border-box;">' +
                   '<b style="font-size:14px; color:#2c3e50; display:block; margin-bottom:6px; white-space: nowrap;">📍 Add a new point?</b>' +
                   '<code style="color:#e74c3c; font-size:12px; background:#f8f9fa; padding:2px 6px; border-radius:3px; display:inline-block; margin-bottom:12px; margin-left: 20px;">' + lat + ', ' + lng + '</code><br>' +
                   '<div style="text-align: center; width: 100%;">' +
                   '<a href="' + formUrl + '" target="_blank" ' +
                   'style="background:#27ae60; color:white; padding:10px 20px; border-radius:25px; text-decoration:none; font-weight:bold; font-size:13px; display:inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">' +
                   'Send information</a>' +
                   '</div>' +
                   '</div>';

     L.popup()
         .setLatLng(e.latlng)
         .setContent(content)
         .openOn(this);
}

function initPointPicker() {
    for (var key in window) {
        if (key.startsWith('map_') && window[key] instanceof L.Map) {
            window[key].on('click', onMapClick);
            return;
        }
    }
    setTimeout(initPointPicker, 500);
}
initPointPicker();
</script>
"""
m.get_root().html.add_child(folium.Element(click_js))

# 9. СОШИАЛ TOBЧНУУД, QR БОЛОН ЭЦСИЙН CSS ЗАГВАРУУД
final_combined_controls = """
<div id="right-panel-controls" style="position: fixed; bottom: 20px; right: 20px; z-index: 999999 !important; display: flex; flex-direction: column; gap: 8px; align-items: flex-end;">

    <a href="https://www.facebook.com/sharer/sharer.php?u=https://travelmap.mn" target="_blank" 
       style="background: #1877F2; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-facebook-f"></i>
    </a>

    <a href="#" onclick="shareOnMessenger(); return false;"
       style="background: #0084FF; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-facebook-messenger"></i>
    </a>

    <a href="https://t.me/share/url?url=https://travelmap.mn" target="_blank" 
       style="background: #0088cc; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-telegram"></i>
    </a>

    <a href="https://twitter.com/intent/tweet?url=https://travelmap.mn" target="_blank" 
       style="background: #000000; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-x-twitter"></i>
    </a>

    <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://travelmap.mn" target="_blank" 
       style="background: #0077b5; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-linkedin-in"></i>
    </a>

    <a href="https://github.com/BayarCh/MongoliaGuideMap" target="_blank" 
       style="background: #333; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       <i class="fa-brands fa-github"></i>
    </a>

    <div class="visitor-stats" style="margin-top: 5px; background: white; padding: 2px; border-radius: 4px; box-shadow: 0px 2px 8px rgba(0,0,0,0.2);">
        <img src="https://api.visitorbadge.io/api/combined?path=https%3A%2F%2Fbayarchoijil.github.io%2Fmap%2F&labelColor=%2327ae60&countColor=%23555555&style=flat" 
             alt="visitor badge" style="height: 22px; display: block; vertical-align: middle;">
    </div>
</div>

<script>
function shareOnMessenger() {
    var url = "https://travelmap.mn"; // Энд мөн travelmap.mn болгож өөрчлөв
    var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    if (isMobile) {
        window.location.href = "fb-messenger://share/?link=" + encodeURIComponent(url);
    } else {
        window.open("https://www.facebook.com/dialog/send?app_id=1210892749527211&link=" + encodeURIComponent(url) + "&redirect_uri=" + encodeURIComponent(url), "_blank");
    }
}
</script>

<div id="qr-code-container" class="desktop-only" style="
    position: fixed; 
    bottom: 80px; 
    left: 15px; 
    z-index: 999999 !important; 
    background: rgba(255, 255, 255, 0.9); 
    padding: 8px; 
    border-radius: 10px; 
    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    text-align: center;
    border: 1px solid #ddd;
">
    <p style="margin: 0 0 5px 0; font-size: 9px; font-weight: bold; color: #1a73e8; font-family: sans-serif;">SCAN TO MOBILE</p>
    <img src="https://api.qrserver.com/v1/create-qr-code/?size=70x70&data=https://travelmap.mn/?v=77" 
         alt="QR Code" style="width: 70px; height: 70px; display: block;">
</div>

<style>
    @media (max-width: 768px) {
        .desktop-only { display: none !important; }
        .visitor-stats { display: none !important; }
        .leaflet-popup-content img { max-height: 120px !important; object-fit: cover !important; }
    }

    .leaflet-control-layers,
    .leaflet-control-layers-expanded,
    .leaflet-touch .leaflet-control-layers,
    .leaflet-touch .leaflet-control-layers-expanded {
        background: none !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-top: 15px !important;
        margin-right: 5px !important;
        display: flex !important;
        justify-content: flex-end !important;
    }

    .leaflet-control-layers-list {
        display: flex !important;
        flex-direction: row !important;
        align-items: flex-start !important;
        background: none !important;
        gap: 8px !important;
    }

    .leaflet-control-layers-base {
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 3px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        margin-right: 5px !important;
        flex-shrink: 0 !important;
    }

    .leaflet-control-layers-overlays {
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 3px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        flex-shrink: 0 !important;
    }

    .leaflet-control-layers label {
        font-size: 12px !important;
        margin-bottom: 5px !important;
        white-space: nowrap !important;
        display: flex !important;
        align-items: center !important;
    }

    .leaflet-control-layers input {
        margin-right: 8px !important;
    }

    .leaflet-control-scale {
        position: fixed !important;
        bottom: 43px !important; 
        left: 20px !important;   
        margin: 0 !important;
        z-index: 1000 !important;
    }

    .leaflet-bottom.leaflet-left {
        position: fixed !important;
        bottom: 10px !important;
        left: 10px !important;
        z-index: 999 !important;
        display: block !important; 
    }

    .leaflet-popup-content-wrapper { 
        padding: 0 !important; 
        border-radius: 12px !important; 
        overflow: hidden !important; 
        width: auto !important; 
        max-width: 300px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }

    .leaflet-popup-content { 
        margin: 0 !important; 
        width: auto !important; 
        display: flex !important;
        flex-direction: column !important;
        gap: 0 !important; 
    }

    .leaflet-popup-content img {
        width: 100% !important;
        height: auto !important;
        display: block !important; 
        margin: 0 !important;
        padding: 0 !important;
        border-radius: 12px 12px 0 0 !important;
        object-fit: cover !important;
    }

    .leaflet-popup-close-button { 
        top: 10px !important; 
        right: 10px !important; 
        color: white !important; 
        background: rgba(0,0,0,0.3) !important; 
        border-radius: 50% !important; 
        z-index: 1000 !important; 
    }
</style>

<div class="leaflet-bottom leaflet-left" style="pointer-events: auto; margin-bottom: 0px; margin-left: 1px;">
    <div class="leaflet-control-attribution leaflet-control" style="font-size: 11px; padding: 3px 5px; background: rgba(255, 255, 255, 0.8); border-radius: 4px; box-shadow: 0 1px 5px rgba(0,0,0,0.2);">
        &copy; <a href="https://travelmap.mn" target="_blank" style="color: #333; text-decoration: none;">2026 TravelMap.mn | BayarChoijil</a>
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(final_combined_controls))

# 10. ОЛОН ХЭЛНИЙ МОДАЛ БОЛОН JS ХӨДӨЛГҮҮР
js_styles = """
<style>
    .lang-switcher-panel {
        position: absolute;
        top: 300px;
        right: 10px;
        z-index: 1000;
        background: rgba(255, 255, 255, 0.95);
        padding: 4px;
        border-radius: 6px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.35);
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 4px;
        max-width: 130px;
    }
    .lang-btn {
        border: 1px solid #ccc;
        background: #f8f9fa;
        padding: 3px 2px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
        font-size: 10px;
        text-align: center;
        transition: all 0.2s;
    }
    .lang-btn.active {
        background: #1a73e8;
        color: white;
        border-color: #1a73e8;
    }
    @media (max-width: 600px) {
        .lang-switcher-panel { top: auto; bottom: 300px; right: 8px; gap: 3px; max-width: 105px; }
        .lang-btn { font-size: 9px; padding: 2px 1px; }
    }
    .leaflet-control-search { margin-top: 10px !important; margin-left: 12px !important; }
</style>
"""

js_html = """
<div class="lang-switcher-panel" id="langPanel">
    <button class="lang-btn active" data-lang="mn" onclick="switchLanguage('mn')">MN</button>
    <button class="lang-btn" data-lang="en" onclick="switchLanguage('en')">EN</button>
    <button class="lang-btn" data-lang="kr" onclick="switchLanguage('kr')">KR</button>
    <button class="lang-btn" data-lang="jp" onclick="switchLanguage('jp')">JP</button>
    <button class="lang-btn" data-lang="cn" onclick="switchLanguage('cn')">CN</button>
    <button class="lang-btn" data-lang="ru" onclick="switchLanguage('ru')">RU</button>
</div>
"""

js_script = """
<script>
var currentLang = 'mn';
var searchControl = null;
var mapObject = null;
var globalClusterGroups = [];

var dictControlLayers = {
    "Street Map": { "mn": "🌐 Гудамжны зураг", "en": "🌐 Street Map", "kr": "🌐 거리 지도", "jp": "🌐 街路地図", "cn": "🌐 街道地图", "ru": "🌐 Карта улиц" },
    "Satellite": { "mn": "🛰️ Хиймэл дагуул", "en": "🛰️ Satellite", "kr": "🛰️ 위성 지도", "jp": "🛰️ 卫星地图", "cn": "🛰️ 卫星地图", "ru": "🛰️ Спутник" },
    "Terrain Map": { "mn": "⛰️ Гадаргуун зураг", "en": "⛰️ Terrain Map", "kr": "⛰️ 지형 지도", "jp": "⛰️ 地形図", "cn": "⛰️ 地形图", "ru": "⛰️ Карта рельефа" },
    "OpenTopoMap": { "mn": "⛰️ OpenTopoMap", "en": "⛰️ Topo Map", "kr": "⛰️ 등고선 지도", "jp": "⛰️ 地形図", "cn": "⛰️ 地形图", "ru": "⛰️ Топокарта" },

    "Natural Wonders": { "mn": "🏞️ Байгалийн үзэсгэлэн", "en": "Natural Wonders", "kr": "🏞️ 자연 경관", "jp": "🏞️ 自然の景观", "cn": "🏞️ 自然奇观", "ru": "🏞️ Чудеса природы" },
    "Historical Sites": { "mn": "🏛️ Түүхэн дурсгал", "en": "Historical Sites", "kr": "🏛️ 역사 유적지", "jp": "🏛️ 歴史遺跡", "cn": "🏛️ 历史古迹", "ru": "🏛️ Исторические места" },
    "Religious Sites": { "mn": "🕉️ Сүм хийд, шашин", "en": "Religious Sites", "kr": "🕉️ 종교 사원", "jp": "🕉️ 宗教寺院", "cn": "🕉️ 宗教圣地", "ru": "🕉️ Религиозные места" },
    "Tourist Camps": { "mn": "⛺ Жуулчны бааз", "en": "Tourist Camps", "kr": "⛺ 여행자 캠프", "jp": "⛺ ツーリストキャンプ", "cn": "⛺ 旅游营地", "ru": "⛺ Турбазы" },
    "Resorts": { "mn": "🏢 Амралтын газар", "en": "Resorts", "kr": "🏢 리조트", "jp": "🏢 リゾート", "cn": "🏢 度假村", "ru": "🏢 Курорты" },
    "Sanatoriums": { "mn": "🏥 Сувилал", "en": "Sanatoriums", "kr": "🏥 요양원", "jp": "🏥 疗养所", "cn": "🏥 疗养院", "ru": "🏥 Санатории" },
    "Children's Camps": { "mn": "🧒 Хүүхдийн зуслан", "en": "Children's Camps", "kr": "🧒 어린이 캠프", "jp": "🧒 児童キャンプ", "cn": "🧒 儿童营地", "ru": "🧒 Детские лагеря" },
    "Roadside Service": { "mn": "🍽️ Зам дагуух үйлчилгээ", "en": "Roadside Service", "kr": "🍽️ 길거리 서비스", "jp": "🍽️ ロードサイド", "cn": "🍽️ 路边服务", "ru": "🍽️ Придорожный сервис" },
    "Transport": { "mn": "✈️ Тээвэр, ложистик", "en": "Transport", "kr": "✈️ 교통 / 物流", "jp": "✈️ 交通 / 物流", "cn": "✈️ 交通 / 物流", "ru": "✈️ Транспорт" }
};

document.addEventListener("DOMContentLoaded", function() {
    function initMultilangEngine() {
        for (var key in window) {
            if (key.startsWith('map_') && window[key] instanceof L.Map) { mapObject = window[key]; }
            if (window[key] instanceof L.MarkerClusterGroup) { globalClusterGroups.push(window[key]); }
        }

        if (mapObject) {
            mapObject.eachLayer(function(layer) {
                if (layer instanceof L.Control.Search && layer !== searchControl) {
                    mapObject.removeControl(layer);
                }
            });

            var badControls = document.querySelectorAll('.leaflet-control-search');
            if (badControls.length > 1) {
                for (var i = 1; i < badControls.length; i++) { badControls[i].remove(); }
            }

            mapObject.on('popupopen', function(e) { updatePopupLanguage(); });
            saveOriginalLabels();
        } else {
            setTimeout(initMultilangEngine, 300);
        }
    }
    initMultilangEngine();
});

function saveOriginalLabels() {
    var labels = document.querySelectorAll('.leaflet-control-layers label');
    if (labels.length > 0) {
        labels.forEach(function(label) {
            if (!label.getAttribute('data-raw-text')) {
                var txt = "";
                label.childNodes.forEach(function(node) {
                    if (node.nodeType === 3) txt += node.textContent;
                    else if (node.tagName === 'SPAN' && !node.querySelector('input')) txt += node.textContent;
                });
                if (!txt.trim() || !txt.includes('|')) { txt = label.innerText || ""; }
                txt = txt.trim();
                if (txt) { label.setAttribute('data-raw-text', txt); }
            }
        });
        refreshSearchAndLabels();
    } else {
        setTimeout(saveOriginalLabels, 150);
    }
}

function switchLanguage(lang) {
    currentLang = lang;
    document.querySelectorAll('.lang-btn').forEach(btn => {
        if(btn.getAttribute('data-lang') === lang) { btn.classList.add('active'); } 
        else { btn.classList.remove('active'); }
    });

    var placeholders = { 'mn':'Газрын нэрээ бичнэ үү...', 'en':'Search location...', 'kr':'위치 검색...', 'jp':'場所を検索...', 'cn':'搜索地點...', 'ru':'Поиск места...' };
    var inputField = document.querySelector('.search-input');
    if (inputField) { inputField.placeholder = placeholders[lang]; }

    refreshSearchAndLabels();
    updatePopupLanguage();
}

function refreshSearchAndLabels() {
    document.querySelectorAll('.leaflet-control-layers label').forEach(function(label) {
        var rawText = label.getAttribute('data-raw-text');
        if (rawText) {
            var targetText = rawText;
            if (rawText.includes('|')) {
                var parts = rawText.split('|');
                var mnPart = parts[0].trim();
                var enPart = parts[1].trim();
                var cleanEnKey = enPart.replace(/[^a-zA-Z ]/g, "").trim(); 

                if (currentLang === 'mn') {
                    targetText = mnPart;
                } else {
                    var matchedKey = Object.keys(dictControlLayers).find(function(k) {
                        return k.replace(/[^a-zA-Z ]/g, "").toLowerCase() === cleanEnKey.toLowerCase();
                    });
                    targetText = (matchedKey && dictControlLayers[matchedKey][currentLang]) ? dictControlLayers[matchedKey][currentLang] : enPart;
                }
            } else {
                var cleanKey = rawText.replace(/[^a-zA-Z ]/g, "").trim();
                var matchedKey = Object.keys(dictControlLayers).find(function(k) {
                    return k.replace(/[^a-zA-Z ]/g, "").toLowerCase() === cleanKey.toLowerCase();
                });
                if (matchedKey && dictControlLayers[matchedKey][currentLang]) { targetText = dictControlLayers[matchedKey][currentLang]; }
            }

            var textReplaced = false;
            for (var i = 0; i < label.childNodes.length; i++) {
                var node = label.childNodes[i];
                if (node.nodeType === 3 && node.textContent.trim().length > 0) {
                    node.textContent = " " + targetText.trim();
                    textReplaced = true;
                }
            }
            if (!textReplaced) {
                label.querySelectorAll('span').forEach(function(span) {
                    if (!span.querySelector('input')) { span.textContent = targetText.trim(); textReplaced = true; }
                });
            }
        }
    });
}

function updatePopupLanguage() {
    document.querySelectorAll('.pop-lang').forEach(function(div) {
        if (div.classList.contains('lang-' + currentLang)) {
            div.style.display = 'block';
        } else {
            div.style.display = 'none';
        }
    });
}
</script>
"""

ultimate_multilang_engine = js_styles + js_html + js_script
m.get_root().html.add_child(folium.Element(ultimate_multilang_engine))

# 11. ФАЙЛАА ХАДГАЛАХ
output_path = os.path.join(current_dir, "index.html")
m.save(output_path)
print(f"✨ Бүрэн нэгтгэсэн төгс хувилбар амжилттай үүслээ! Файлын байршил: {output_path}")


