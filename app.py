from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get Gemini API key from environment
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
                "error": "Gemini API key is not configured."
            }), 500


        system_prompt = """
You are an expert web developer and UI designer.

The user will describe a website they want.

Generate ONE complete standalone HTML document.

IMPORTANT RULES:

1. Return ONLY the HTML code.
2. Do NOT use Markdown code fences.
3. Include HTML, CSS and JavaScript in the same file.
4. Create a beautiful modern responsive UI.
5. Make the design professional.
6. Make buttons functional.
7. Add animations where appropriate.
8. Use CSS instead of external libraries whenever possible.
9. The generated page must work inside an iframe.
10. Do not explain the code.
11. Do not include <html> code fences.
12. Start directly with <!DOCTYPE html>.
"""


        full_prompt = (
            system_prompt
            + "\n\nUSER REQUEST:\n"
            + prompt
        )


        # Gemini API URL

        url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/"
            + GEMINI_MODEL
            + ":generateContent"
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


        # API error

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


        candidates = result.get(
            "candidates",
            []
        )


        if not candidates:

            return jsonify({

                "success": False,

                "error":
                "Gemini did not return generated content."

            }), 500


        parts = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )


        generated_code = ""


        for part in parts:

            if "text" in part:

                generated_code += part["text"]


        generated_code = generated_code.strip()


        # Remove Markdown fences if Gemini adds them

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

            "error":
            "Gemini request timed out. Please try again."

        }), 504


    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# Render configuration

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(

        host="0.0.0.0",

        port=port,

        debug=False

    )
