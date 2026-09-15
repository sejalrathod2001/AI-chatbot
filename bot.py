from flask import Flask, request, jsonify, Response,render_template
from google import genai

app = Flask(__name__)

client = genai.Client(api_key="AQ.Ab8RN6I0b5WUL_LH8iPqLKXnoLwzJiBsrNYlanPbcZ5s99zSgA")

# (user_input + model_output turns) added  
histories = {}
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
   
    try:
        data = request.get_json()
        user_message = data.get("message")
        user_id = data.get("user_id", "default")

        if not user_message:
            return jsonify({"error": "message is required"}), 400

        if user_id not in histories:
          histories[user_id] = []

        history = histories[user_id]

 # user msg added here
        history.append({
          "type": "user_input",
          "content": [{"type": "text", "text": user_message}]
 })

        def generate():
            full_reply = ""
            try:
                stream = client.interactions.create(
                    model="gemini-3.1-flash-lite",
                    system_instruction="You are chat assistant you need to give accurate or concise answers.",
                    store=False,
                    input=history,
                    stream=True
                )

                for event in stream:
                    if event.event_type == "step.delta" and event.delta:
                       if event.delta.type == "text" and event.delta.text:
                          full_reply += event.delta.text
                          yield event.delta.text

            except Exception as e:
                 yield f"[error: {str(e)}]"

            finally:
 # histroy added 
                if full_reply:
                    history.append({
                        "type": "model_output",
                        "content": [{"type": "text", "text": full_reply}]
                })

        return Response(generate(), mimetype="text/plain")

    except Exception as e:
         return jsonify({"error": str(e)}), 500

@app.route("/history/<user_id>", methods=["GET"])
def get_history(user_id):
 
    try:
        if user_id not in histories:
           return jsonify({"error": "user not found"}), 404

        return jsonify({"history": histories[user_id]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
 app.run(debug=True)
