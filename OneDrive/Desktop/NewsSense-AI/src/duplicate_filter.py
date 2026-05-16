from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def detect_duplicates(df, text_column="clean_content", threshold=0.75):
    """
    Detect duplicate/similar news articles using TF-IDF + Cosine Similarity.

    Returns:
    - df with duplicate_score and is_duplicate columns
    - number of duplicates found
    """

    if df.empty or text_column not in df.columns:
        df["duplicate_score"] = 0
        df["is_duplicate"] = False
        return df, 0

    texts = df[text_column].fillna("").astype(str).tolist()

    if len(texts) <= 1:
        df["duplicate_score"] = 0
        df["is_duplicate"] = False
        return df, 0

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(texts)

    similarity_matrix = cosine_similarity(tfidf_matrix)

    duplicate_scores = []
    duplicate_flags = []

    for i in range(len(similarity_matrix)):
        max_similarity = 0

        for j in range(len(similarity_matrix)):
            if i != j:
                max_similarity = max(max_similarity, similarity_matrix[i][j])

        duplicate_score = round(max_similarity * 100, 2)
        duplicate_scores.append(duplicate_score)

        duplicate_flags.append(duplicate_score >= threshold * 100)

    df["duplicate_score"] = duplicate_scores
    df["is_duplicate"] = duplicate_flags

    duplicate_count = int(df["is_duplicate"].sum())

    return df, duplicate_count


def remove_duplicate_articles(df):
    """
    Keeps the first article and removes later duplicate articles.
    """
    if "is_duplicate" not in df.columns:
        return df

    clean_df = df[df["is_duplicate"] == False].copy()
    clean_df = clean_df.reset_index(drop=True)

    return clean_df