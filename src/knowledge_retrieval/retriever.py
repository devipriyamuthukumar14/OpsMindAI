
import pandas as pd

from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Locate project files
PROJECT_PATH = Path(__file__).resolve().parents[2]

KB_PATH = (
    PROJECT_PATH / "knowledge_base" / "it_troubleshooting.csv"
)


# Load knowledge base
kb_df = pd.read_csv(KB_PATH)

# Prepare searchable text
kb_df["search_text"] = (
    kb_df["title"].fillna("") + " " +
    kb_df["problem"].fillna("")
)


# Create TF-IDF vectorizer
kb_vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2)
)

kb_matrix = kb_vectorizer.fit_transform(
    kb_df["search_text"]
)


# Search function
def search_knowledge_base(query, top_k=3):

    query_vector = kb_vectorizer.transform([query])

    similarity_scores = cosine_similarity(
        query_vector,
        kb_matrix
    ).flatten()

    top_indices = similarity_scores.argsort()[::-1][:top_k]

    results = kb_df.iloc[top_indices][
        ["title", "problem", "solution", "category"]
    ].copy()

    results["similarity_score"] = similarity_scores[top_indices]

    return results
