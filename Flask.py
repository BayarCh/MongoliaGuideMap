import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

# Хязгаарлалтыг нь салгаж хадгалсан API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

client = genai.Client(api_key=GEMINI_API_KEY)


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Мессеж хоосон байна"}), 400

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite", contents=user_message
        )
        print("RESPONSE:")
        print(response.text)
        return jsonify({"response": response.text})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)