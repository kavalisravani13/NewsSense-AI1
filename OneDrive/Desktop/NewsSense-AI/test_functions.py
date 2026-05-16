from src.mysql_database import (
    save_user_profile,
    save_article,
    save_feedback,
    get_feedback_data
)

# Save user
user_id = save_user_profile(
    "Sravani",
    ["AI", "Technology"],
    "Beginner",
    "Short"
)

print("User saved:", user_id)

# Save article
article_id = save_article(
    "AI Revolution",
    "Artificial Intelligence is changing industries.",
    "AI",
    "OpenAI News",
    0.95,
    0.10,
    0.15,
    0.90,
    "AI is transforming jobs and industries.",
    "This matters because you are interested in AI."
)

print("Article saved:", article_id)

# Save feedback
feedback_saved = save_feedback(
    user_id,
    article_id,
    "Relevant"
)

print("Feedback saved:", feedback_saved)

# Fetch dashboard data
data = get_feedback_data()

print("\nDashboard Data:")

for row in data:
    print(row)