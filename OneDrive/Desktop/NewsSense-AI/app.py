# =========================================================
# NEWSSENSE AI - STREAMLIT CLOUD VERSION (WITHOUT MYSQL)
# =========================================================

import streamlit as st
import pandas as pd

from src.preprocessing import clean_text, word_count, reading_time_minutes
from src.topic_matcher import calculate_relevance
from src.clickbait_detector import detect_clickbait
from src.score_calculator import (
    calculate_noise_score,
    calculate_trust_score,
    why_this_matters
)
from src.summarizer import generate_summary
from src.duplicate_filter import (
    detect_duplicates,
    remove_duplicate_articles
)

# =========================================================
# STREAMLIT PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NewsSense AI",
    page_icon="📰",
    layout="wide"
)

st.title("📰 NewsSense AI")
st.subheader("News Noise Reduction and Personalized Knowledge Digest Engine")

# =========================================================
# SESSION STATE
# =========================================================

if "feedback_records" not in st.session_state:
    st.session_state["feedback_records"] = []

# =========================================================
# SIDEBAR MENU
# =========================================================

menu = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "User Profile",
        "News Dataset",
        "News Digest",
        "News Diet Dashboard",
        "Feedback Dashboard",
        "About Project"
    ]
)

# =========================================================
# LOAD AND PROCESS NEWS
# =========================================================

def load_and_process_news():

    df = pd.read_csv("data/sample_news.csv")

    if "existing_summary" not in df.columns:
        df["existing_summary"] = ""

    df["content"] = df["content"].fillna("")
    df["title"] = df["title"].fillna("")
    df["topic"] = df["topic"].fillna("General")
    df["source"] = df["source"].fillna("Unknown")
    df["existing_summary"] = df["existing_summary"].fillna("")

    # TEXT CLEANING
    df["clean_content"] = df["content"].apply(clean_text)

    # WORD COUNT
    df["word_count"] = df["clean_content"].apply(word_count)

    # READING TIME
    df["reading_time"] = df["clean_content"].apply(
        reading_time_minutes
    )

    # RELEVANCE SCORE
    if "interests" in st.session_state:

        df["relevance_score"] = df.apply(
            lambda row: calculate_relevance(
                row["clean_content"],
                row["topic"],
                st.session_state["interests"]
            ),
            axis=1
        )

    else:

        df["relevance_score"] = 0

    # CLICKBAIT DETECTION
    df["clickbait_score"] = df.apply(
        lambda row: detect_clickbait(
            row["title"],
            row["content"],
            row["existing_summary"]
        )[0],
        axis=1
    )

    df["clickbait_label"] = df.apply(
        lambda row: detect_clickbait(
            row["title"],
            row["content"],
            row["existing_summary"]
        )[1],
        axis=1
    )

    # INITIAL NOISE SCORE
    df["noise_score"] = df.apply(
        lambda row: calculate_noise_score(
            row["clickbait_score"],
            row["relevance_score"]
        ),
        axis=1
    )

    # TRUST SCORE
    df["trust_score"] = df["noise_score"].apply(
        calculate_trust_score
    )

    # DUPLICATE DETECTION
    df, duplicate_count = detect_duplicates(
        df,
        text_column="clean_content",
        threshold=0.75
    )

    st.session_state["duplicate_count"] = duplicate_count

    # FINAL NOISE SCORE
    df["noise_score"] = df.apply(
        lambda row: calculate_noise_score(
            row["clickbait_score"],
            row["relevance_score"]
        ) + (row["duplicate_score"] * 0.2),
        axis=1
    )

    df["noise_score"] = df["noise_score"].apply(
        lambda x: round(min(x, 100), 2)
    )

    df["trust_score"] = df["noise_score"].apply(
        calculate_trust_score
    )

    return df


# =========================================================
# HOME PAGE
# =========================================================

if menu == "Home":

    st.header("Welcome to NewsSense AI")

    st.write("""
    NewsSense AI reduces noisy, duplicate,
    and clickbait-heavy news into a
    personalized knowledge digest.
    """)

    st.success(
        "Create your profile first, then explore the digest."
    )


# =========================================================
# USER PROFILE
# =========================================================

elif menu == "User Profile":

    st.header("👤 Create Your News Profile")

    name = st.text_input("Enter your name")

    interests = st.multiselect(
        "Select your interests",
        [
            "National News",
            "Politics",
            "Business and Finance",
            "Local News",
            "Crime and Justice",
            "International News",
            "Entertainment",
            "Sports",
            "Education",
            "Health and Wellness",
            "Science and Technology",
            "Environment",
            "Opinion and Editorial",
            "Lifestyle and Features",
            "Technology and Gadgets"
        ],
        default=[
            "Science and Technology",
            "Business and Finance"
        ]
    )

    knowledge_level = st.selectbox(
        "Select your knowledge level",
        [
            "Beginner",
            "Intermediate",
            "Expert"
        ]
    )

    digest_length = st.selectbox(
        "Preferred digest length",
        [
            "Short",
            "Medium",
            "Detailed"
        ]
    )

    if st.button("Save Profile"):

        st.session_state["name"] = name
        st.session_state["interests"] = interests
        st.session_state["knowledge_level"] = knowledge_level
        st.session_state["digest_length"] = digest_length

        st.success(
            "Profile saved successfully for this session!"
        )


# =========================================================
# NEWS DATASET
# =========================================================

elif menu == "News Dataset":

    st.header("📂 News Dataset")

    df = load_and_process_news()

    duplicate_count = st.session_state.get(
        "duplicate_count",
        0
    )

    clean_articles = len(df) - duplicate_count

    st.success(
        f"Dataset loaded with {df.shape[0]} rows."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Articles", len(df))
    col2.metric("Duplicates", duplicate_count)
    col3.metric("Clean Articles", clean_articles)

    st.subheader("Dataset Preview")

    st.dataframe(df.head(20))


# =========================================================
# NEWS DIGEST
# =========================================================

elif menu == "News Digest":

    st.header("📰 Personalized News Digest")

    if "interests" not in st.session_state:

        st.warning(
            "Please create your profile first."
        )

    else:

        df = load_and_process_news()

        df = remove_duplicate_articles(df)

        digest_df = df.sort_values(
            by=["relevance_score", "trust_score"],
            ascending=False
        ).head(10)

        for index, row in digest_df.iterrows():

            st.markdown("---")

            st.subheader(row["title"])

            st.write(f"Topic: {row['topic']}")
            st.write(f"Source: {row['source']}")

            st.write(
                f"Relevance Score: {row['relevance_score']}"
            )

            st.write(
                f"Clickbait Level: {row['clickbait_label']}"
            )

            st.write(
                f"Duplicate Score: {row['duplicate_score']}"
            )

            st.write(
                f"Noise Score: {row['noise_score']}"
            )

            st.write(
                f"Trust Score: {row['trust_score']}"
            )

            summary = generate_summary(
                row["clean_content"],
                row["existing_summary"],
                st.session_state["knowledge_level"],
                st.session_state["digest_length"]
            )

            st.subheader("Summary")

            st.write(summary)

            st.info(
                why_this_matters(
                    row["topic"],
                    st.session_state["interests"]
                )
            )

            feedback = st.selectbox(
                "Give Feedback",
                [
                    "Relevant",
                    "Not Relevant",
                    "Too Simple",
                    "Too Complex",
                    "Save Article"
                ],
                key=f"feedback_{index}"
            )

            if st.button(
                f"Submit Feedback {index}"
            ):

                feedback_record = {

                    "user_name":
                        st.session_state.get("name", ""),

                    "knowledge_level":
                        st.session_state.get(
                            "knowledge_level",
                            ""
                        ),

                    "digest_length":
                        st.session_state.get(
                            "digest_length",
                            ""
                        ),

                    "selected_interests":
                        ", ".join(
                            st.session_state.get(
                                "interests",
                                []
                            )
                        ),

                    "title":
                        row["title"],

                    "topic":
                        row["topic"],

                    "feedback":
                        feedback,

                    "relevance_score":
                        row["relevance_score"],

                    "clickbait_label":
                        row["clickbait_label"],

                    "duplicate_score":
                        row["duplicate_score"],

                    "noise_score":
                        row["noise_score"],

                    "trust_score":
                        row["trust_score"]
                }

                st.session_state[
                    "feedback_records"
                ].append(feedback_record)

                st.success(
                    f"Feedback saved: {feedback}"
                )


# =========================================================
# NEWS DIET DASHBOARD
# =========================================================

elif menu == "News Diet Dashboard":

    st.header("📊 News Diet Dashboard")

    if "interests" not in st.session_state:

        st.warning(
            "Please create your profile first."
        )

    else:

        df = load_and_process_news()

        duplicate_count = st.session_state.get(
            "duplicate_count",
            0
        )

        df = remove_duplicate_articles(df)

        digest_df = df.sort_values(
            by=["relevance_score", "trust_score"],
            ascending=False
        ).head(10)

        st.success(
            "Your personalized news dashboard is ready."
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Digest Articles",
            len(digest_df)
        )

        col2.metric(
            "Duplicates Removed",
            duplicate_count
        )

        col3.metric(
            "Average Trust",
            f"{round(digest_df['trust_score'].mean(), 2)}%"
        )

        st.subheader("Topic Distribution")

        st.bar_chart(
            digest_df["topic"].value_counts()
        )

        st.subheader("Clickbait Distribution")

        st.bar_chart(
            digest_df["clickbait_label"].value_counts()
        )


# =========================================================
# FEEDBACK DASHBOARD
# =========================================================

elif menu == "Feedback Dashboard":

    st.header("💬 Feedback Dashboard")

    feedback_records = st.session_state.get(
        "feedback_records",
        []
    )

    if len(feedback_records) == 0:

        st.info(
            "No feedback submitted yet."
        )

    else:

        feedback_df = pd.DataFrame(
            feedback_records
        )

        st.success(
            f"Total feedback records: {len(feedback_df)}"
        )

        st.dataframe(feedback_df)

        st.subheader("Feedback Distribution")

        st.bar_chart(
            feedback_df["feedback"].value_counts()
        )

        st.subheader("Topic Distribution")

        st.bar_chart(
            feedback_df["topic"].value_counts()
        )

        st.download_button(
            "Download Feedback CSV",
            data=feedback_df.to_csv(index=False),
            file_name="feedback_records.csv",
            mime="text/csv"
        )


# =========================================================
# ABOUT PROJECT
# =========================================================

elif menu == "About Project":

    st.header("About NewsSense AI")

    st.write("""
    NewsSense AI is a personalized
    news noise reduction engine.

    It helps users:
    - Avoid clickbait
    - Remove duplicate news
    - Save reading time
    - Consume relevant news
    - Improve information quality
    """)

    st.subheader("Core Features")

    st.write("""
    - Personalized news digest
    - Relevance scoring
    - Duplicate detection
    - Clickbait detection
    - Noise score
    - Trust score
    - AI summaries
    - Feedback dashboard
    - News diet analytics
    """)