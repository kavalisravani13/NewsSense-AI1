from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_relevance(article_text, article_topic, user_interests):
    article_text = str(article_text)
    article_topic = str(article_topic)

    user_interest_text = " ".join(user_interests)

    combined_article_text = article_topic + " " + article_text

    documents = [combined_article_text, user_interest_text]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    tfidf_score = similarity * 100

    # Topic match bonus
    topic_bonus = 0

    for interest in user_interests:
        if article_topic.lower() == interest.lower():
            topic_bonus = 60
            break
        elif interest.lower() in article_topic.lower() or article_topic.lower() in interest.lower():
            topic_bonus = 40
            break

    final_score = tfidf_score + topic_bonus

    return round(min(final_score, 100), 2)