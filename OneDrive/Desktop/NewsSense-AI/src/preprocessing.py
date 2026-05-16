import re

def clean_text(text):
    text = str(text)
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s.,!?]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def word_count(text):
    return len(str(text).split())

def reading_time_minutes(text):
    words = word_count(text)
    return max(1, round(words / 200))