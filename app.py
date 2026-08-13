from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini model
GEMINI_MODEL = "gemini-2.5-flash"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()

        prompt = data.get("prompt", "").strip()

        if not prompt:
            return jsonify({
                "success": False,
                "error": "Please enter a prompt."
            }), 400

        if not GEMINI_API_KEY:
            return jsonify({
                "success": False,
                "error": "GEMINI_API_KEY is not configured."
            }), 500

        system_prompt = """
You are an expert web developer.

The user will describe a webpage they want.

Generate ONE complete standalone HTML document.

Requirements:
1. Return ONLY HTML code.
2. Do not use Markdown code fences.
3. Include HTML, CSS and JavaScript in the same file.
4. Use modern responsive design.
5. Make the webpage visually attractive.
6. Use Google Fonts only if useful.
7. Do not use external JavaScript libraries unless absolutely necessary.
8. Make buttons and interactions functional using JavaScript.
9. The generated page must work when placed directly inside an iframe.
10. Do not explain the code.
"""

        full_prompt = system_prompt + "\n\nUSER REQUEST:\n" + prompt

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{GEMINI_MODEL}:generateContent"
        )

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 12000
            }
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            try:
                error_data = response.json()
            except Exception:
                error_data = response.text

            return jsonify({
                "success": False,
                "error": str(error_data)
            }), response.status_code

        result = response.json()

        candidates = result.get("candidates", [])

        if not candidates:
            return jsonify({
                "success": False,
                "error": "Gemini did not return any generated content."
            }), 500

        parts = candidates[0].get("content", {}).get("parts", [])

        generated_code = ""

        for part in parts:
            if "text" in part:
                generated_code += part["text"]

        generated_code = generated_code.strip()

        # Remove Markdown fences if Gemini accidentally adds them
        if generated_code.startswith("```html"):
            generated_code = generated_code[7:]

        elif generated_code.startswith("```"):
            generated_code = generated_code[3:]

        if generated_code.endswith("```"):
            generated_code = generated_code[:-3]

        generated_code = generated_code.strip()

        return jsonify({
            "success": True,
            "html": generated_code
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "AI request timed out. Please try again."
        }), 504

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
