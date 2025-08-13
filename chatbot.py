import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ChatbotError(Exception):
    """Custom exception for chatbot-related errors."""
    pass

class Chatbot:
    def __init__(self, filepath):
        try:
            self.data = pd.read_csv(filepath)
        except FileNotFoundError:
            raise ChatbotError(f"The data file was not found at {filepath}")

        if 'question' not in self.data.columns or 'answer' not in self.data.columns:
            raise ChatbotError("The data file must contain 'question' and 'answer' columns.")

        self.vectorizer = TfidfVectorizer()
        self.question_vectors = self.vectorizer.fit_transform(self.data['question'])

    def get_response(self, query):
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.question_vectors)
        most_similar_index = np.argmax(similarities)
        return self.data['answer'].iloc[most_similar_index]

# Example usage (optional, for testing)
if __name__ == '__main__':
    try:
        bot = Chatbot('resources.csv')
        print("Chatbot is ready. Ask a question.")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            response = bot.get_response(user_input)
            print(f"Bot: {response}")
    except ChatbotError as e:
        print(f"Error: {e}")
