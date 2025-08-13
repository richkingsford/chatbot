import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Chatbot:
    def __init__(self, filepath):
        self.data = pd.read_csv(filepath)
        self.vectorizer = TfidfVectorizer()
        self.question_vectors = self.vectorizer.fit_transform(self.data['question'])

    def get_response(self, query):
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.question_vectors)
        most_similar_index = np.argmax(similarities)
        return self.data['answer'].iloc[most_similar_index]

# Example usage (optional, for testing)
if __name__ == '__main__':
    bot = Chatbot('resources.csv')
    print("Chatbot is ready. Ask a question.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        response = bot.get_response(user_input)
        print(f"Bot: {response}")
