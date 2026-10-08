import json
import os
import time
import urllib.request
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

# ===== 1. TRAVELMAP.MN-ИЙН ДАТА САГ УНШИХ =====
try:
    nature_df = pd.read_csv("Nature_His_multi_translated.csv", encoding="utf-8")
    camp_df = pd.read_csv("Tourist_camps_multi.csv", encoding="utf-8")
    print(f"Дата амжилттай уншигдлаа: Байгаль={len(nature_df)}, Бааз={len(camp_df)}")
except Exception as e:
    print(f"Дата файл уншихад алдаа гарлаа: {e}")
    nature_df = pd.DataFrame()
    camp_df = pd.DataFrame()


def get_travelmap_context(aimag_name):
    """Шууд Travelmap.mn-ийн CSV дата сангаас тухайн аймгийн газруудыг шүүж текстийн контекст болгоно"""
    context_parts = []

    # 1. Байгалийн болон түүхэн газрууд шүүх
    if not nature_df.empty and "Aimag_name_mon" in nature_df.columns:
        nature_match = nature_df[
            nature_df["Aimag_name_mon"]
            .astype(str)
            .str.contains(aimag_name, na=False)
        ]
        if not nature_match.empty:
            cat_col = (
                "Category" if "Category" in nature_match.columns else "Category_mon"
            )
            context_parts.append(f"=== {aimag_name} аймгийн байгаль, түүхийн дурсгалт газрууд (Travelmap.mn) ===")
            for _, row in nature_match.head(15).iterrows():
                name = row.get("Name_mon", "Нэргүй")
                cat = row.get(cat_col, "Дурсгалт газар")
                context_parts.append(f"• {name} ({cat})")

    # 2. Жуулчны бааз, амралтын газрууд шүүх
    if not camp_df.empty and "Aimag_name_mon" in camp_df.columns:
        camp_match = camp_df[
            camp_df["Aimag_name_mon"]
            .astype(str)
            .str.contains(aimag_name, na=False)
        ]
        if not camp_match.empty:
            context_parts.append(f"\n=== {aimag_name} аймгийн жуулчны бааз, амралтын газрууд (Travelmap.mn) ===")
            for _, row in camp_match.head(10).iterrows():
                name = row.get("Name_mon", "Нэргүй")
                cat = row.get("Category", "Амралтын газар")
                context_parts.append(f"• {name} ({cat})")

    return "\n".join(context_parts)


# ===== 2. FLASK СЕРВЕР =====
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def generate_ai_response(user_query, travelmap_data=""):
    """Wikipedia ашиглахгүй, зөвхөн Travelmap.mn-ийн өгөгдөл дээр үндэслэн хариулах систем заавар"""
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY тохируулаагүй байна."

    system_prompt = (
        "Та бол зөвхөн Travelmap.mn платформын өгөгдөлд үндэслэн хариулдаг AI Аяллын Гид юм.\n"
        "Цэвэр гадны эх сурвалж эсвэл Wikipedia-ийн хамааралгүй мэдээллээр биш, "
        "доор өгөгдсөн Travelmap.mn-ийн дата сангийн мэдээлэлд тугуурлан аялагчид эелдэг, цэгцтэй зөвлөгөө өгнө үү.\n\n"
    )

    if travelmap_data:
        full_prompt = f"{system_prompt}TRAVELMAP.MN ДАТА САНГИЙН ЭХ СУРВАЛЖ:\n{travelmap_data}\n\nХЭРЭГЛЭГЧИЙН АСУУЛТ: {user_query}"
    else:
        full_prompt = f"{system_prompt}ХЭРЭГЛЭГЧИЙН АСУУЛТ: {user_query}"

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json",
    }

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
        err_str = str(e)
        print(f"AI хүсэлтэд алдаа гарлаа: {err_str}")
        if "429" in err_str:
            return "API key-ийн хязгаар дууссан байна. Түр хүлээнэ үү."

    return "Google AI сервер дээр одоогоор түр ачаалал хэт өндөр байна."


# ===== 3. ROUTE ТОХИРУУЛГА =====
@app.route("/generate", methods=["POST", "OPTIONS"])
@app.route("/chat", methods=["POST", "OPTIONS"])
def generate():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json() or {}
    user_message = data.get("prompt") or data.get("message")

    if not user_message:
        return jsonify({"error": "Prompt эсвэл message талбар олдсонгүй"}), 400

    # Монгол орны 21 аймаг + Улаанбаатар
    aimags = [
        "Архангай", "Баян-Өлгий", "Баянхонгор", "Булган", "Говь-Алтай",
        "Говьсүмбэр", "Дархан-Уул", "Дорноговь", "Дорнод", "Дундговь",
        "Завхан", "Орхон", "Сэлэнгэ", "Сүхбаатар", "Төв", "Увс",
        "Улаанбаатар", "Ховд", "Хэнтий", "Хөвсгөл", "Өвөрхангай", "Өмнөговь"
    ]

    matched_aimag = None
    for aimag in aimags:
        if aimag in user_message:
            matched_aimag = aimag
            break

    # Хэрэв аль нэг аймаг асуусан байвал CSV сангаас датагаа шүүж AI-д өгнө
    if matched_aimag:
        travelmap_context = get_travelmap_context(matched_aimag)
        ai_text = generate_ai_response(user_message, travelmap_context)
    else:
        ai_text = generate_ai_response(user_message)

    return jsonify({"response": ai_text, "reply": ai_text})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)