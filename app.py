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
except Exception as e:
    print(f"Файл уншихад алдаа гарлаа: {e}")
    nature_df = pd.DataFrame()
    camp_df = pd.DataFrame()


def get_places_by_aimag(aimag):
    if nature_df.empty:
        return "Байгалийн дурсгалт газрын дата хоосон байна."

    nature = nature_df[
        nature_df["Aimag_name_mon"].astype(str).str.contains(aimag, na=False)
    ]

    places = []
    category_col = (
        "Category" if "Category" in nature.columns else "Category_mon"
    )

    for _, row in nature.head(10).iterrows():
        cat = row[category_col] if category_col in row else "Байгалийн газар"
        places.append(f"• {row['Name_mon']} ({cat})")

    return "\n".join(places)


# ===== FLASK СЕРВЕР =====
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def generate_ai_response(prompt):
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY тохируулаагүй байна."

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

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


@app.route("/generate", methods=["POST", "OPTIONS"])
@app.route("/chat", methods=["POST", "OPTIONS"])
def generate():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json() or {}
    user_message = data.get("prompt") or data.get("message")

    if not user_message:
        return jsonify({"error": "Prompt эсвэл message талбар олдсонгүй"}), 400

    if "Увс" in user_message:
        places_list = get_places_by_aimag("Увс")
        return jsonify({"response": places_list, "reply": places_list})

    ai_text = generate_ai_response(user_message)
    return jsonify({"response": ai_text, "reply": ai_text})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)