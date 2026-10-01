import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import generativeai as genai

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

GEMINI_API_KEY = ""
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_ai_response(prompt):
    # Одоогоор Google дээр идэвхтэй байгаа үндсэн ба Pro хувилбарууд
    models_to_try = [
        'gemini-3.8-flash',
        'gemini-3.8-pro',
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
                    return "API key-ийн өдрийн хязгаар (20 хүсэлт) дууссан байна."

                if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < 2:
                    time.sleep(2.0)
                    continue
                else:
                    break

    return "Google AI сервер дээр одоогоор түр ачаалал хэт өндөр байна. Хэдэн минутын дараа дахин нэг асууна уу."


@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'text': 'Асуулт хоосон байна.'}), 400

        user_message = data['message']
        system_prompt = f"Та бол TravelMap.mn вэб сайтын туслах AI гид юм. Асуулт: {user_message}"

        ai_text = generate_ai_response(system_prompt)
        return jsonify({'text': ai_text})

    except Exception as e:
        print("Server Error:", e)
        return jsonify({'text': f"Серверийн алдаа: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
