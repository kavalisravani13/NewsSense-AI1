import streamlit as st
import pandas as pd

from src.preprocessing import clean_text, word_count, reading_time_minutes
from src.topic_matcher import calculate_relevance
from src.clickbait_detector import detect_clickbait
from src.score_calculator import calculate_noise_score, calculate_trust_score, why_this_matters
from src.summarizer import generate_summary
from src.duplicate_filter import detect_duplicates, remove_duplicate_articles

from src.mysql_database import (
    save_user_profile,
    save_feedback_to_mysql,
    get_feedback_from_mysql
)

st.set_page_config(
    page_title="NewsSense AI",
    page_icon="📰",
    layout="wide"
)

st.title("📰 NewsSense AI")
st.subheader("News Noise Reduction and Personalized Knowledge Digest Engine")

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

if "feedback_records" not in st.session_state:
    st.session_state["feedback_records"] = []


def load_and_process_news():
    df = pd.read_csv("data/sample_news.csv")

    # Safety check for missing columns
    if "existing_summary" not in df.columns:
        df["existing_summary"] = ""

    df["content"] = df["content"].fillna("")
    df["title"] = df["title"].fillna("")
    df["topic"] = df["topic"].fillna("General")
    df["source"] = df["source"].fillna("Unknown")
    df["existing_summary"] = df["existing_summary"].fillna("")

    # Text preprocessing
    df["clean_content"] = df["content"].apply(clean_text)
    df["word_count"] = df["clean_content"].apply(word_count)
    df["reading_time"] = df["clean_content"].apply(reading_time_minutes)

    # Relevance score
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

    # Clickbait detection using title + content + existing summary
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

    # Initial noise and trust scores
    df["noise_score"] = df.apply(
        lambda row: calculate_noise_score(
            row["clickbait_score"],
            row["relevance_score"]
        ),
        axis=1
    )

    df["trust_score"] = df["noise_score"].apply(calculate_trust_score)

    # Duplicate detection
    df, duplicate_count = detect_duplicates(
        df,
        text_column="clean_content",
        threshold=0.75
    )

    st.session_state["duplicate_count"] = duplicate_count

    # Final noise score including duplicate penalty
    df["noise_score"] = df.apply(
        lambda row: calculate_noise_score(
            row["clickbait_score"],
            row["relevance_score"]
        ) + (row["duplicate_score"] * 0.2),
        axis=1
    )

    df["noise_score"] = df["noise_score"].apply(lambda x: round(min(x, 100), 2))
    df["trust_score"] = df["noise_score"].apply(calculate_trust_score)

    return df


if menu == "Home":
    st.header("Welcome to NewsSense AI")

    st.write("""
    NewsSense AI uses a NewsSumm++ inspired dataset to reduce noisy,
    duplicate, and clickbait-driven news into a personalized knowledge digest.
    """)

    st.success("Create your profile first, then explore the news digest and dashboard.")


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
        default=["Science and Technology", "Business and Finance"]
    )

    knowledge_level = st.selectbox(
        "Select your knowledge level",
        ["Beginner", "Intermediate", "Expert"]
    )

    digest_length = st.selectbox(
        "Preferred digest length",
        ["Short", "Medium", "Detailed"]
    )

    if st.button("Save Profile"):

        st.session_state["name"] = name
        st.session_state["interests"] = interests
        st.session_state["knowledge_level"] = knowledge_level
        st.session_state["digest_length"] = digest_length

        # SAVE TO MYSQL
        save_user_profile(
            name,
            knowledge_level,
            digest_length,
            interests
        )

        st.success("Profile saved successfully and stored in MySQL!")

    

elif menu == "News Dataset":
    st.header("📂 NewsSumm++ Sample Dataset")

    df = load_and_process_news()

    duplicate_count = st.session_state.get("duplicate_count", 0)
    clean_articles = len(df) - duplicate_count

    st.success(f"Dataset loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Articles", len(df))
    col2.metric("Duplicates Detected", duplicate_count)
    col3.metric("Clean Articles", clean_articles)

    st.subheader("Dataset Preview")
    st.dataframe(df.head(20))

    st.subheader("Processed Dataset Preview")
    st.dataframe(
        df[[
            "title",
            "topic",
            "source",
            "word_count",
            "reading_time",
            "relevance_score",
            "clickbait_score",
            "clickbait_label",
            "duplicate_score",
            "is_duplicate",
            "noise_score",
            "trust_score"
        ]].head(20)
    )

    st.subheader("Topic Distribution")
    st.bar_chart(df["topic"].value_counts())

    st.subheader("Clickbait Level Distribution")
    st.bar_chart(df["clickbait_label"].value_counts())

    st.subheader("Duplicate Detection Summary")
    st.bar_chart(df["is_duplicate"].value_counts())

    st.subheader("Dataset Columns")
    st.write(df.columns.tolist())

elif menu == "News Digest":

    st.header("🧠 Your Personalized News Digest")

    if "interests" not in st.session_state:
        st.warning("Please create your profile first from the User Profile page.")

    else:

        df = load_and_process_news()

        # Remove duplicate articles
        df = remove_duplicate_articles(df)

        df["personalized_summary"] = df.apply(
            lambda row: generate_summary(
                row["clean_content"],
                row["existing_summary"],
                st.session_state["knowledge_level"],
                st.session_state["digest_length"]
            ),
            axis=1
        )

        df["why_matters"] = df["topic"].apply(
            lambda topic: why_this_matters(
                topic,
                st.session_state["interests"]
            )
        )

        df["summary_reading_time"] = df["personalized_summary"].apply(
            reading_time_minutes
        )

        df["time_saved"] = (
            df["reading_time"] - df["summary_reading_time"]
        )

        df["time_saved"] = df["time_saved"].apply(
            lambda x: max(0, x)
        )

        df = df.sort_values(
            by=["relevance_score", "trust_score"],
            ascending=False
        )

        digest_df = df.head(10)

        st.success(
            f"Showing top {len(digest_df)} personalized non-duplicate articles for you."
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Articles Selected", len(digest_df))
        col2.metric(
            "Duplicates Removed",
            st.session_state.get("duplicate_count", 0)
        )

        col3.metric(
            "Avg Relevance",
            f"{round(digest_df['relevance_score'].mean(), 2)}%"
        )

        col4.metric(
            "Avg Trust",
            f"{round(digest_df['trust_score'].mean(), 2)}%"
        )

        col5.metric(
            "Time Saved",
            f"{int(digest_df['time_saved'].sum())} min"
        )

        # =========================
        # LOOP THROUGH ARTICLES
        # =========================

        for index, row in digest_df.iterrows():

            st.markdown("---")

            st.subheader(row["title"])

            c1, c2, c3, c4, c5 = st.columns(5)

            c1.metric("Relevance", f"{row['relevance_score']}%")
            c2.metric("Clickbait", row["clickbait_label"])
            c3.metric("Duplicate", f"{row['duplicate_score']}%")
            c4.metric("Noise", f"{row['noise_score']}%")
            c5.metric("Trust", f"{row['trust_score']}%")

            st.write("**Topic:**", row["topic"])
            st.write("**Source:**", row["source"])

            st.info(row["personalized_summary"])

            st.success(row["why_matters"])

            st.write(
                f"⏱️ Original reading time: {row['reading_time']} min"
            )

            st.write(
                f"⚡ Time saved through digest: {row['time_saved']} min"
            )

            # =========================
            # FEEDBACK SECTION
            # =========================

            feedback = st.selectbox(
                f"Feedback for {row['title']}",
                [
                    "Relevant",
                    "Not Relevant",
                    "Too Simple",
                    "Too Complex",
                    "Save Article"
                ],
                key=f"feedback_{index}"
            )

            feedback_key = f"submitted_{index}"

            # Initialize session state
            if feedback_key not in st.session_state:
                st.session_state[feedback_key] = False

            # Submit button
            if st.button(
                f"Submit Feedback - {row['title']}",
                key=f"btn_{index}"
            ):

                # Prevent duplicate submission
                if st.session_state[feedback_key]:

                    st.warning(
                        "Feedback already submitted for this article."
                    )

                else:

                    feedback_record = {
                        "user_name": st.session_state.get(
                            "name",
                            "Unknown User"
                        ),
                        "knowledge_level": st.session_state.get(
                            "knowledge_level",
                            "Unknown"
                        ),
                        "digest_length": st.session_state.get(
                            "digest_length",
                            "Unknown"
                        ),
                        "selected_interests": ", ".join(
                            st.session_state.get("interests", [])
                        ),
                        "title": row["title"],
                        "topic": row["topic"],
                        "feedback": feedback,
                        "relevance_score": row["relevance_score"],
                        "clickbait_label": row["clickbait_label"],
                        "duplicate_score": row["duplicate_score"],
                        "noise_score": row["noise_score"],
                        "trust_score": row["trust_score"]
                    }

                    # Save in session state
                    st.session_state["feedback_records"].append(
                        feedback_record
                    )

                    # Save in MySQL
                    save_feedback_to_mysql(
                        feedback_record["user_name"],
                        feedback_record["knowledge_level"],
                        feedback_record["digest_length"],
                        feedback_record["selected_interests"],
                        feedback_record["title"],
                        feedback_record["topic"],
                        feedback_record["feedback"],
                        feedback_record["relevance_score"],
                        feedback_record["clickbait_label"],
                        feedback_record["duplicate_score"],
                        feedback_record["noise_score"],
                        feedback_record["trust_score"]
                    )

                    # Mark as submitted
                    st.session_state[feedback_key] = True

                    st.success(
                        f"Feedback saved to MySQL: {feedback}"
                    )

        # =========================
        # DOWNLOAD SECTION
        # =========================

        st.subheader("Download Personalized Digest")

        st.download_button(
            "Download Digest CSV",
            data=digest_df.to_csv(index=False),
            file_name="personalized_news_digest.csv",
            mime="text/csv"
        )

elif menu == "News Diet Dashboard":
    st.header("📊 News Diet Dashboard")

    if "interests" not in st.session_state:
        st.warning("Please create your profile first from the User Profile page.")
    else:
        df = load_and_process_news()

        total_articles_before = len(df)
        duplicate_count = st.session_state.get("duplicate_count", 0)

        # Keep only clean articles for digest dashboard
        df = remove_duplicate_articles(df)

        df["personalized_summary"] = df.apply(
            lambda row: generate_summary(
                row["clean_content"],
                row["existing_summary"],
                st.session_state["knowledge_level"],
                st.session_state["digest_length"]
            ),
            axis=1
        )

        df["summary_reading_time"] = df["personalized_summary"].apply(reading_time_minutes)
        df["time_saved"] = df["reading_time"] - df["summary_reading_time"]
        df["time_saved"] = df["time_saved"].apply(lambda x: max(0, x))

        digest_df = df.sort_values(
            by=["relevance_score", "trust_score"],
            ascending=False
        ).head(10)

        st.success("Your personalized news diet analysis is ready.")

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Articles Analyzed", total_articles_before)
        col2.metric("Duplicates Removed", duplicate_count)
        col3.metric("Digest Articles", len(digest_df))
        col4.metric("Time Saved", f"{int(digest_df['time_saved'].sum())} min")
        col5.metric("Avg Trust", f"{round(digest_df['trust_score'].mean(), 2)}%")

        st.markdown("---")

        st.subheader("📌 Topic Distribution in Your Digest")
        st.bar_chart(digest_df["topic"].value_counts())

        st.subheader("🧠 Average Relevance by Topic")
        relevance_by_topic = digest_df.groupby("topic")["relevance_score"].mean().sort_values(ascending=False)
        st.bar_chart(relevance_by_topic)

        st.subheader("🛡️ Average Trust Score by Topic")
        trust_by_topic = digest_df.groupby("topic")["trust_score"].mean().sort_values(ascending=False)
        st.bar_chart(trust_by_topic)

        st.subheader("🔊 Average Noise Score by Topic")
        noise_by_topic = digest_df.groupby("topic")["noise_score"].mean().sort_values(ascending=False)
        st.bar_chart(noise_by_topic)

        st.subheader("🎯 Clickbait Level Distribution")
        st.bar_chart(digest_df["clickbait_label"].value_counts())

        st.subheader("♻️ Duplicate Detection Summary")
        duplicate_summary = pd.Series({
            "Clean Articles": len(df),
            "Duplicates Removed": duplicate_count
        })
        st.bar_chart(duplicate_summary)

        st.subheader("📋 News Diet Summary")

        top_topic = digest_df["topic"].value_counts().idxmax()
        avg_noise = round(digest_df["noise_score"].mean(), 2)
        avg_trust = round(digest_df["trust_score"].mean(), 2)
        total_time_saved = int(digest_df["time_saved"].sum())

        st.info(
            f"""
            Your current news digest is mainly focused on **{top_topic}**.

            Duplicates Removed: **{duplicate_count}**

            Average Noise Score: **{avg_noise}%**

            Average Trust Score: **{avg_trust}%**

            Estimated Reading Time Saved: **{total_time_saved} minutes**
            """
        )

        st.subheader("✅ Impact Generated")

        st.write("""
        NewsSense AI helps the user by:
        - Reducing repeated and noisy news
        - Removing duplicate stories
        - Avoiding clickbait-heavy articles
        - Prioritizing relevant topics
        - Saving reading time
        - Creating a healthier news consumption pattern
        """)


elif menu == "Feedback Dashboard":
    st.header("💬 Feedback Dashboard")

    feedback_records = get_feedback_from_mysql()

    if len(feedback_records) == 0:
        st.info("No feedback submitted yet. Go to News Digest and submit feedback for articles.")
    else:
        feedback_df = pd.DataFrame(feedback_records)

        st.success(f"Total feedback records collected: {len(feedback_df)}")

        st.subheader("Feedback Records")

        ordered_columns = [
            "user_name",
            "knowledge_level",
            "digest_length",
            "selected_interests",
            "title",
            "topic",
            "feedback",
            "relevance_score",
            "clickbait_label",
            "duplicate_score",
            "noise_score",
            "trust_score"
        ]

        st.dataframe(feedback_df[ordered_columns])

        st.subheader("📌 Feedback Distribution")
        st.bar_chart(feedback_df["feedback"].value_counts())

        st.subheader("📰 Feedback by Topic")
        st.bar_chart(feedback_df["topic"].value_counts())

        st.subheader("🎓 Feedback by Knowledge Level")
        st.bar_chart(feedback_df["knowledge_level"].value_counts())

        st.subheader("📊 Average Scores by Feedback Type")

        score_summary = feedback_df.groupby("feedback")[
            ["relevance_score", "duplicate_score", "noise_score", "trust_score"]
        ].mean()

        st.dataframe(score_summary)

        st.subheader("🧠 Learning Insight")

        most_common_feedback = feedback_df["feedback"].value_counts().idxmax()
        most_common_level = feedback_df["knowledge_level"].value_counts().idxmax()

        if most_common_feedback == "Relevant":
            st.success(
                f"Most feedback is marked as Relevant. The recommendation system is working well for {most_common_level} users."
            )

        elif most_common_feedback == "Not Relevant":
            st.warning(
                f"Many articles are marked as Not Relevant by {most_common_level} users. The system should adjust topic matching and recommendation ranking."
            )

        elif most_common_feedback == "Too Simple":
            st.info(
                f"Some {most_common_level} users feel the summaries are too simple. The system should generate more detailed summaries for this level."
            )

        elif most_common_feedback == "Too Complex":
            st.info(
                f"Some {most_common_level} users feel the summaries are too complex. The system should simplify future summaries for this level."
            )

        elif most_common_feedback == "Save Article":
            st.success(
                f"{most_common_level} users saved articles. Similar topics can be prioritized in future digests."
            )

        st.subheader("⬇️ Download Feedback Data")

        st.download_button(
            "Download Feedback CSV",
            data=feedback_df.to_csv(index=False),
            file_name="feedback_records.csv",
            mime="text/csv"
        )


elif menu == "About Project":
    st.header("About NewsSense AI")

    st.write("""
    NewsSense AI is a News Noise Reduction Engine.
    It uses news text, topic labels, and summaries to generate clean,
    personalized, and meaningful news digests.
    """)

    st.subheader("Core Features")

    st.write("""
    - NewsSumm++ inspired news dataset
    - User interest-based personalization
    - Relevance score
    - Duplicate detection
    - Clickbait detection
    - Noise score
    - Trust score
    - Personalized summaries
    - Why this matters explanation
    - News diet dashboard
    - Feedback collection
    - Feedback dashboard
    - Feedback-based learning insight
    - User-level feedback analysis
    """)