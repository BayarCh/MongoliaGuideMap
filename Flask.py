import json
import os
import time
import urllib.request
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Render болон орчны хувьсагчаас API түлхүүрийг аюулгүй авна
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def generate_ai_response(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/interactions"

    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json",
    }

    # Серверээс дэмжих загваруудыг дарааллуулан туршина
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-1.5-flash",
    ]

    for model_name in models_to_try:
        payload = {"model": model_name, "input": prompt}

        for attempt in range(1, 3):
            try:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data, headers=headers, method="POST"
                )

                with urllib.request.urlopen(req) as response:
                    res = json.loads(response.read().decode("utf-8"))

                    steps = res.get("steps", [])
                    for step in steps:
                        if step.get("type") == "model_output":
                            for content in step.get("content", []):
                                if content.get("type") == "text":
                                    answer = content.get("text", "").strip()
                                    if answer:
                                        return answer

            except Exception as e:
                err_str = str(e)
                print(f"[{model_name}] Алдаа: {err_str}")

                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    return (
                        "API key-ийн хязгаар дууссан байна. Түр хүлээнэ үү."
                    )

                if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < 2:
                    time.sleep(2.0)
                    continue
                else:
                    break

    return "Одоогоор ачаалал өндөр байна. Хэдэн минутын дараа дахин туршина уу."


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Мессеж хоосон байна"}), 400

        ai_reply = generate_ai_response(user_message)

        return jsonify({"response": ai_reply})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)