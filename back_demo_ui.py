from flask import Flask, render_template, request, jsonify
import networkx as nx
from Intelligence_AI_V2 import CognitiveAgent
from openai import OpenAI

OPENAI_API_KEY = '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'  # Replace with your actual API key


client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
app.static_folder = 'static'

# Placeholder function for simulating a ChatGPT response

def get_chatgpt_response(user_message):

    try:
        chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": "je veux que tu répondes à ce thème en citant un maximum tes sources via des liens" + user_message,
                    }
                ],
                model="gpt-3.5-turbo",
            )
        print(chat_completion.choices[0].message.content)
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"
# Initialize your chatbot and graph
PATH = "Parle moi du regain de tensions entre la Corée du Nord et du Sud".replace(' ', '_')
G = nx.read_gml(f"{PATH}/{PATH}.gml")

agent = CognitiveAgent(data_path="Parle moi du regain de tensions entre la Corée du Nord et du Sud", api_key='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')

# Define your options here

@app.route("/", methods=['GET'])
def home():
    return render_template("interface_user.html")

@app.route("/chat", methods=['POST'])
def chat():
    data = request.json
    user_message = data["message"]

    # Get the response from your chatbot
    chatbot_response = agent.search(user_message)
    # Simulate a ChatGPT response
    chatgpt_response_2 = get_chatgpt_response(user_message)

    return jsonify({
        "chatbot_response": chatbot_response,
        "chatgpt_response": "Chatgpt\n" + chatgpt_response_2
    })


if __name__ == "__main__":
    app.run(debug=True)