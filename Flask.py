from flask import Flask, request, jsonify
import pandas as pd
import google.generativeai as genai

app = Flask(__name__)

# Gemini API тохируулга
genai.configure(api_key="")
model = genai.GenerativeModel('gemini-1.5-flash')

# CSV Датаг санах ойд унших
tourist_df = pd.read_csv("Tourist_camps_multi.csv")
nature_df = pd.read_csv("Nature_His_multi_translated.csv")


@app.route('/api/chat', methods=['POST'])
def chat():
    user_query = request.json.get("message", "")

    # Хэрэглэгчийн асуултад тохирох датаг CSV-ээс шүүх контекст бэлтгэх
    prompt = f"""
    Чи бол TravelMap.mn-ийн аяллын ухаалаг гид AI байна.
    Хэрэглэгчийн асуулт: "{user_query}"

    Манай дата санд байгаа зарим цэгүүд:
    {tourist_df[['Name_mon', 'Aimag_name_mon', 'Sum_name_mon', 'Lat', 'Long']].head(30).to_json(orient='records')}

    Хариултаа дараах хэлбэрээр бэлдэнэ үү:
    1. Товч зөвлөгөө, аяллын маршрутыг текстээр тайлбарла.
    2. Санал болгож буй цэгүүдийн нэр болон Lat, Long солбицлыг JSON бүтцээр хариултандаа багтаа.
    """

    response = model.generate_content(prompt)
    return jsonify({"reply": response.text})


if __name__ == '__main__':
    app.run(port=5000)
