from src.mysql_database import (
    save_user_profile,
    save_feedback_to_mysql,
    get_feedback_from_mysql
)

print("\n========================================")
print("NEWSSENSE AI MYSQL TEST")
print("========================================\n")


# =========================================
# SAVE USER PROFILE
# =========================================

print("Saving user profile...\n")

user_id = save_user_profile(
    name="Sravani",
    knowledge_level="Beginner",
    digest_length="Short",
    interests=["AI", "Technology"]
)

print("User saved successfully")
print("Generated User ID:", user_id)

print("\n========================================\n")


# =========================================
# SAVE FEEDBACK
# =========================================

print("Saving feedback...\n")

feedback_saved = save_feedback_to_mysql(
    user_name="Sravani",
    knowledge_level="Beginner",
    digest_length="Short",
    selected_interests="AI, Technology",
    title="AI Revolution",
    topic="AI",
    feedback="Relevant",
    relevance_score=0.95,
    clickbait_label="No",
    duplicate_score=0.10,
    noise_score=0.15,
    trust_score=0.90
)

print("Feedback Saved Status:", feedback_saved)

print("\n========================================\n")


# =========================================
# FETCH FEEDBACK DATA
# =========================================

print("Fetching dashboard data...\n")

data = get_feedback_from_mysql()

print("Dashboard Data:\n")

if len(data) == 0:

    print("No feedback records found.")

else:

    for row in data:

        print("========================================")
        print("Feedback ID:", row["feedback_id"])
        print("User Name:", row["user_name"])
        print("Knowledge Level:", row["knowledge_level"])
        print("Digest Length:", row["digest_length"])
        print("Selected Interests:", row["selected_interests"])
        print("Article Title:", row["title"])
        print("Topic:", row["topic"])
        print("Feedback:", row["feedback"])
        print("Relevance Score:", row["relevance_score"])
        print("Clickbait Label:", row["clickbait_label"])
        print("Duplicate Score:", row["duplicate_score"])
        print("Noise Score:", row["noise_score"])
        print("Trust Score:", row["trust_score"])
        print("Created At:", row["created_at"])
        print("========================================\n")


print("\n========================================")
print("MYSQL TEST COMPLETED")
print("========================================")