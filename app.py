from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5-coder"   # Change to "llama3.2" if you prefer

# Store conversation history (resets when server restarts)
conversation = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    prompt = data.get("message", "").strip()

    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    # Add user's message
    conversation.append({
        "role": "user",
        "content": prompt
    })

    payload = {
        "model": MODEL_NAME,
        "messages": conversation,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=300
        )

        response.raise_for_status()

        result = response.json()

        ai_message = result["message"]["content"]

        conversation.append({
            "role": "assistant",
            "content": ai_message
        })

        return jsonify({
            "reply": ai_message
        })

    except requests.exceptions.ConnectionError:
        return jsonify({
            "reply": "❌ Ollama is not running.\n\nStart it using:\n\nollama serve"
        })

    except Exception as e:
        return jsonify({
            "reply": str(e)
        })


@app.route("/clear", methods=["POST"])
def clear_chat():
    conversation.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True)
