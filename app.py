import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# API түлхүүрийг орчны хувьсагчаас (Environment Variable) уншина
GEMINI_API_KEY = os.getenv("")
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_ai_response(prompt):
    # Одоогоор идэвхтэй байгаа стандарт загварууд
    models_to_try = [
        'gemini-2.5-flash',
        'gemini-2.5-pro'
    ]

    for model_name in models_to_try:
        print(f"[{model_name}] Хүсэлт илгээж байна...")
        for attempt in range(1, 3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    print(f"Амжилттай хариу авлаа! ({model_name})")
                    return response.text
            except Exception as e:
                err_str = str(e)
                print(f"[{model_name}] Алдаа: {err_str}")

                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    return "API key-ийн хязгаар дууссан байна. Түр хүлээнэ үү."

                if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < 2:
                    time.sleep(2.0)
                    continue
                else:
                    break

    return "Google AI сервер дээр одоогоор түр ачаалал хэт өндөр байна. Хэдэн минутын дараа дахин туршина уу."


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Prompt талбар олдсонгүй'}), 400

    prompt = data['prompt']
    ai_text = generate_ai_response(prompt)
    return jsonify({'response': ai_text})


if __name__ == '__main__':
    # Хэсэгчилсэн тест хийхэд
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)