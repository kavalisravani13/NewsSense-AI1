CLICKBAIT_WORDS = [
    "shocking",
    "you won't believe",
    "unbelievable",
    "secret",
    "truth",
    "viral",
    "exposed",
    "must see",
    "breaking",
    "danger",
    "warning",
    "everyone is angry",
    "this will change everything",
    "hidden",
    "revealed",
    "controversy",
    "panic",
    "fear",
    "outrage",
    "alarming",
    "massive",
    "dramatic",
    "huge",
    "crisis",
    "scandal"
]

def detect_clickbait(title, content="", summary=""):
    title = str(title)
    content = str(content)
    summary = str(summary)

    combined_text = f"{title} {content} {summary}".lower()

    score = 0

    for word in CLICKBAIT_WORDS:
        if word in combined_text:
            score += 12

    if "!" in title:
        score += 10

    if title.isupper() and len(title) > 5:
        score += 15

    if len(title.split()) <= 4:
        score += 5

    score = min(score, 100)

    if score >= 60:
        label = "High"
    elif score >= 30:
        label = "Medium"
    else:
        label = "Low"

    return score, label