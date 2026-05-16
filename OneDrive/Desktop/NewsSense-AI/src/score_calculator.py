def calculate_noise_score(clickbait_score, relevance_score):
    low_relevance_penalty = max(0, 100 - relevance_score)

    noise_score = (clickbait_score * 0.6) + (low_relevance_penalty * 0.4)

    return round(min(noise_score, 100), 2)


def calculate_trust_score(noise_score):
    trust_score = 100 - noise_score

    return round(max(0, trust_score), 2)

def why_this_matters(topic, user_interests):
    interests = ", ".join(user_interests)

    return (
        f"This story matters to you because it is related to '{topic}', "
        f"which connects with your selected interests: {interests}."
    )