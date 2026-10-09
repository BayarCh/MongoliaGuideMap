import json
import os
import time
import urllib.request
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

# ===== CSV ДАТА УНШИХ =====
try:
    nature_df = pd.read_csv("Nature_His_multi_translated.csv", encoding="utf-8")
    camp_df = pd.read_csv("Tourist_camps_multi.csv", encoding="utf-8")
    print(
        f"Дата ачааллаа: Байгаль={len(nature_df)} бичлэг, Бааз={len(camp_df)} бичлэг"
    )
except Exception as e:
    print(f"Дата файл уншихад алдаа гарлаа: {e}")
    nature_df = pd.DataFrame()
    camp_df = pd.DataFrame()


def get_places_by_aimag(aimag):
    """Тухайн аймгийн CSV дээрх мэдээллийг ангилал бүрээр нь шүүж буцаана"""
    output = []

    # 1. БАЙГАЛИЙН БОЛОН ТҮҮХЭН ДУРСГАЛТ ГАЗРУУД
    if not nature_df.empty and "Aimag_name_mon" in nature_df.columns:
        nature = nature_df[
            nature_df["Aimag_name_mon"]
            .astype(str)
            .str.strip()
            .str.contains(aimag, na=False)
        ]
        if not nature.empty:
            output.append(
                f"=== 🏔️ {aimag} аймгийн Байгаль, түүхийн дурсгалт газрууд (Нийт {len(nature)}) ==="
            )
            cat_col = (
                "Category_mon"
                if "Category_mon" in nature.columns
                else "Category"
            )
            sum_col = "Sum_mon" if "Sum_mon" in nature.columns else "Sum"

            grouped = nature.groupby(cat_col)
            for category, group in grouped:
                output.append(f"\n📍 **{category} ({len(group)}):**")
                for _, row in group.iterrows():
                    name = row.get("Name_mon", "Нэргүй")
                    sum_name = (
                        f" - {row.get(sum_col)} сум"
                        if sum_col in row and pd.notna(row.get(sum_col))
                        else ""
                    )
                    output.append(f"  • {name}{sum_name}")

    # 2. ЖУУЛЧНЫ БААЗ, ҮЙЛЧИЛГЭЭНИЙ ГАЗРУУД
    if not camp_df.empty and "Aimag_name_mon" in camp_df.columns:
        camps = camp_df[
            camp_df["Aimag_name_mon"]
            .astype(str)
            .str.strip()
            .str.contains(aimag, na=False)
        ]
        if not camps.empty:
            output.append(
                f"\n=== 🏕️ {aimag} аймгийн Жуулчны бааз, үйлчилгээний газрууд (Нийт {len(camps)}) ==="
            )
            camp_cat = (
                "Category_mon" if "Category_mon" in camps.columns else "Category"
            )
            sum_col = "Sum_mon" if "Sum_mon" in camps.columns else "Sum"

            grouped_camps = camps.groupby(camp_cat)
            for category, group in grouped_camps:
                output.append(f"\n🏢 **{category} ({len(group)}):**")
                for _, row in group.iterrows():
                    name = row.get("Name_mon", "Нэргүй")
                    sum_name = (
                        f" - {row.get(sum_col)} сум"
                        if sum_col in row and pd.notna(row.get(sum_col))
                        else ""
                    )
                    output.append(f"  • {name}{sum_name}")

    if not output:
        return f"{aimag} аймаг дээр одоогоор мэдээлэл олдсонгүй."

    return "\n".join(output)


# ===== ТӨВ АЙМГИЙН ТУРШИЛТ (Терминал дээр асахдаа шууд хэвлэнэ) =====
print("\n===== ТӨВ АЙМГИЙН ДАТА ТУРШИЛТ =====")
print(get_places_by_aimag("Төв"))
print("====================================\n")

# ===== FLASK СЕРВЕР =====
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def generate_ai_response(user_query, travelmap_data=""):
    if not GEMINI_API_KEY:
        return "API Key тохируулаагүй байна."

    system_prompt = (
        "Та бол зөвхөн Travelmap.mn платформын өгөгдөлд үндэслэн хариулдаг AI Аяллын Гид юм.\n"
        "Доор өгөгдсөн Travelmap.mn-ийн дата сангийн мэдээлэлд тугуурлан аялагчид эелдэг, цэгцтэй зөвлөгөө өгнө үү.\n\n"
    )

    if travelmap_data:
        full_prompt = f"{system_prompt}TRAVELMAP.MN ДАТА САНГИЙН ЭХ СУРВАЛЖ:\n{travelmap_data}\n\nХЭРЭГЛЭГЧИЙН АСУУЛТ: {user_query}"
    else:
        full_prompt = f"{system_prompt}ХЭРЭГЛЭГЧИЙН АСУУЛТ: {user_query}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers=headers, method="POST"
        )
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            candidates = res.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
    except Exception as e:
        return f"AI Холболтын алдаа: {e}"

    return "Хариу ирсэнгүй."


@app.route("/generate", methods=["POST", "OPTIONS"])
@app.route("/chat", methods=["POST", "OPTIONS"])
def generate():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json() or {}
    user_message = data.get("prompt") or data.get("message", "")

    print(f"\n[ИРСЭН АСУУЛТ]: {user_message}")

    if not user_message:
        return jsonify({"error": "Асуулт хоосон байна"}), 400

    aimags = [
        "Архангай",
        "Баян-Өлгий",
        "Баянхонгор",
        "Булган",
        "Говь-Алтай",
        "Говьсүмбэр",
        "Дархан-Уул",
        "Дорноговь",
        "Дорнод",
        "Дундговь",
        "Завхан",
        "Орхон",
        "Сэлэнгэ",
        "Сүхбаатар",
        "Төв",
        "Увс",
        "Улаанбаатар",
        "Ховд",
        "Хэнтий",
        "Хөвсгөл",
        "Өвөрхангай",
        "Өмнөговь",
    ]

    matched_aimag = None
    for aimag in aimags:
        if aimag in user_message:
            matched_aimag = aimag
            break

    if matched_aimag:
        print(f"[ШҮҮСЭН АЙМАГ]: {matched_aimag}")
        db_places = get_places_by_aimag(matched_aimag)
        print(
            f"[ТЕРМИНАЛД ХЭВЛЭСЭН ДАТА]:\n{db_places[:300]}...\n"
        )  # Эхний 300 тэмдэгтийг терминалд харуулна
        return jsonify({"response": db_places, "reply": db_places})

    ai_text = generate_ai_response(user_message)
    return jsonify({"response": ai_text, "reply": ai_text})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)