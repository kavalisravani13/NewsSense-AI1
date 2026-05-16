import mysql.connector


# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root123",
            database="newsense_ai"
        )

        if connection.is_connected():
            print("MySQL connected successfully")

        return connection

    except Exception as e:
        print("Database connection error:", e)
        return None


# -------------------------------------------------
# SAVE USER PROFILE
# -------------------------------------------------

def save_user_profile(name, knowledge_level, digest_length, interests):

    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        user_query = """
        INSERT INTO users (name, knowledge_level, digest_length)
        VALUES (%s, %s, %s)
        """

        cursor.execute(user_query, (
            name,
            knowledge_level,
            digest_length
        ))

        user_id = cursor.lastrowid

        interest_query = """
        INSERT INTO user_interests (user_id, interest)
        VALUES (%s, %s)
        """

        for interest in interests:
            cursor.execute(interest_query, (user_id, interest))

        connection.commit()

        print("User profile saved successfully")

    except Exception as e:
        print("Error saving user profile:", e)

    finally:
        cursor.close()
        connection.close()


# -------------------------------------------------
# SAVE FEEDBACK
# -------------------------------------------------

def save_feedback_to_mysql(
    user_name,
    knowledge_level,
    digest_length,
    selected_interests,
    title,
    topic,
    feedback,
    relevance_score,
    clickbait_label,
    duplicate_score,
    noise_score,
    trust_score
):

    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:

        query = """
        INSERT INTO feedback (
            user_name,
            knowledge_level,
            digest_length,
            selected_interests,
            title,
            topic,
            feedback,
            relevance_score,
            clickbait_label,
            duplicate_score,
            noise_score,
            trust_score
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            user_name,
            knowledge_level,
            digest_length,
            selected_interests,
            title,
            topic,
            feedback,
            relevance_score,
            clickbait_label,
            duplicate_score,
            noise_score,
            trust_score
        )

        cursor.execute(query, values)

        connection.commit()

        print("Feedback saved successfully")

    except Exception as e:
        print("Error saving feedback:", e)

    finally:
        cursor.close()
        connection.close()


# -------------------------------------------------
# GET FEEDBACK
# -------------------------------------------------

def get_feedback_from_mysql():

    connection = get_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:

        query = """
        SELECT * FROM feedback
        ORDER BY created_at DESC
        """

        cursor.execute(query)

        results = cursor.fetchall()

        return results

    except Exception as e:
        print("Error fetching feedback:", e)
        return []

    finally:
        cursor.close()
        connection.close()