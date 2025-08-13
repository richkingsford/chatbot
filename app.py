from flask import Flask, request, jsonify, render_template_string
from chatbot import Chatbot

app = Flask(__name__)
bot = Chatbot('resources.csv')

# HTML template for the user interface
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Chatbot MVP</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; }
        #chatbox { margin-top: 20px; }
        #response { margin-top: 20px; padding: 15px; background: #e9e9eb; border-radius: 4px; }
        form { display: flex; }
        input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px 0 0 4px; }
        button { padding: 10px 15px; border: none; background-color: #007bff; color: white; cursor: pointer; border-radius: 0 4px 4px 0; }
        button:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Chatbot MVP</h1>
        <p>Ask a question based on the provided data. Try things like "What is the capital of France?" or "Who painted the Mona Lisa?".</p>
        <div id="chatbox">
            <form id="question-form">
                <input type="text" id="question" name="question" placeholder="Ask your question..." required>
                <button type="submit">Ask</button>
            </form>
        </div>
        <div id="response-container" style="display:none;">
            <h2>Answer:</h2>
            <div id="response"></div>
        </div>
    </div>
    <script>
        document.getElementById('question-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const question = document.getElementById('question').value;
            const responseContainer = document.getElementById('response-container');
            const responseDiv = document.getElementById('response');

            const res = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question })
            });
            const data = await res.json();

            responseDiv.innerText = data.answer;
            responseContainer.style.display = 'block';
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'error': 'Question is required.'}), 400

    answer = bot.get_response(question)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
