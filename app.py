import logging
import sys
from flask import Flask, request, jsonify, render_template_string
from chatbot import Chatbot, ChatbotError

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chatbot_app.log"),
        logging.StreamHandler(sys.stdout)  # Also log to console
    ]
)

app = Flask(__name__)

# --- Initialize Chatbot ---
try:
    bot = Chatbot('resources.csv')
    logging.info("Chatbot initialized successfully.")
except ChatbotError as e:
    logging.error(f"Failed to initialize chatbot: {e}")
    # If the bot fails to load, we can't run the app.
    # In a real-world scenario, you might have a fallback or a status page.
    # For this MVP, we will exit.
    print(f"FATAL: {e}. Application cannot start.", file=sys.stderr)
    sys.exit(1)


# --- HTML Template ---
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Intelligent Chatbot</title>
    <style>
        :root {
            --body-bg: #f5f8ff;
            --chat-bg: #ffffff;
            --user-msg-bg: #007bff;
            --bot-msg-bg: #e9e9eb;
            --text-color: #333;
            --user-text-color: #fff;
            --bot-text-color: #000;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--body-bg);
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .chat-container {
            width: 90%;
            max-width: 600px;
            height: 90vh;
            max-height: 800px;
            display: flex;
            flex-direction: column;
            background: var(--chat-bg);
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .chat-header {
            padding: 20px;
            background: var(--user-msg-bg);
            color: var(--user-text-color);
            text-align: center;
            font-size: 1.2rem;
            font-weight: bold;
        }
        .message-list {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .message {
            display: flex;
            align-items: flex-end;
            max-width: 80%;
        }
        .message .bubble {
            padding: 10px 15px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .message.user {
            align-self: flex-end;
        }
        .message.user .bubble {
            background: var(--user-msg-bg);
            color: var(--user-text-color);
            border-bottom-right-radius: 4px;
        }
        .message.bot {
            align-self: flex-start;
        }
        .message.bot .bubble {
            background: var(--bot-msg-bg);
            color: var(--bot-text-color);
            border-bottom-left-radius: 4px;
        }
        .message.bot.thinking .bubble {
            display: flex;
            gap: 5px;
            align-items: center;
        }
        .dot {
            width: 8px;
            height: 8px;
            background-color: #aaa;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1.0); }
        }
        .input-area {
            display: flex;
            padding: 20px;
            border-top: 1px solid #eee;
        }
        #question {
            flex: 1;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 20px;
            margin-right: 10px;
            font-size: 1rem;
        }
        #question:focus {
            outline: none;
            border-color: var(--user-msg-bg);
        }
        #submit-btn {
            padding: 10px 20px;
            border: none;
            background-color: var(--user-msg-bg);
            color: white;
            cursor: pointer;
            border-radius: 20px;
            font-size: 1rem;
            transition: background-color 0.2s;
        }
        #submit-btn:hover {
            background-color: #0056b3;
        }
        #submit-btn:disabled {
            background-color: #aaa;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">Intelligent Chatbot</div>
        <div class="message-list" id="message-list">
            <div class="message bot">
                <div class="bubble">Hello! Ask me something about my data.</div>
            </div>
        </div>
        <div class="input-area">
            <form id="question-form" style="display: contents;">
                <input type="text" id="question" placeholder="Type your question..." required autocomplete="off">
                <button type="submit" id="submit-btn">Send</button>
            </form>
        </div>
    </div>
    <script>
        const form = document.getElementById('question-form');
        const input = document.getElementById('question');
        const submitBtn = document.getElementById('submit-btn');
        const messageList = document.getElementById('message-list');

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const question = input.value.trim();
            if (!question) return;

            addMessage(question, 'user');
            input.value = '';
            input.disabled = true;
            submitBtn.disabled = true;

            const thinkingMessage = addMessage('...', 'bot', true);

            try {
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: question })
                });
                const data = await res.json();

                thinkingMessage.remove();

                if (res.ok) {
                    addMessage(data.answer, 'bot');
                } else {
                    addMessage(data.error || 'An unknown error occurred.', 'bot');
                }
            } catch (error) {
                thinkingMessage.remove();
                addMessage('Could not connect to the server. Please try again.', 'bot');
            } finally {
                input.disabled = false;
                submitBtn.disabled = false;
                input.focus();
            }
        });

        function addMessage(text, sender, isThinking = false) {
            const messageEl = document.createElement('div');
            messageEl.classList.add('message', sender);

            const bubble = document.createElement('div');
            bubble.classList.add('bubble');

            if (isThinking) {
                messageEl.classList.add('thinking');
                bubble.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
            } else {
                bubble.innerText = text;
            }

            messageEl.appendChild(bubble);
            messageList.appendChild(messageEl);
            messageList.scrollTop = messageList.scrollHeight;
            return messageEl;
        }
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
    if not data or 'question' not in data:
        logging.warning("Received invalid request to /ask: 'question' field missing.")
        return jsonify({'error': 'Invalid request. The "question" field is required.'}), 400

    question = data['question']
    logging.info(f"Received question: {question}")

    try:
        answer = bot.get_response(question)
        logging.info(f"Found answer: {answer}")
        return jsonify({'answer': answer})
    except Exception as e:
        # This will catch any unexpected error from the chatbot logic.
        logging.error(f"An unexpected error occurred while processing question '{question}': {e}", exc_info=True)
        return jsonify({'error': 'Sorry, an internal error occurred.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
