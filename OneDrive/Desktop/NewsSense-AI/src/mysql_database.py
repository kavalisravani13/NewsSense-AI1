import mysql.connector
from mysql.connector import Error


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():

    try:

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root123",
            database="newsense_ai",
            port=3306
        )

        if connection.is_connected():
            print("MySQL connected successfully")

        return connection

    except Error as e:

        print("DATABASE CONNECTION ERROR:", e)

        return None


# =====================================================
# SAVE USER PROFILE
# =====================================================

def save_user_profile(
    name,
    knowledge_level,
    digest_length,
    interests
):

    print("save_user_profile called")

    connection = get_connection()

    if connection is None:
        return None

    try:

        cursor = connection.cursor()

        query = """
        INSERT INTO users (
            name,
            knowledge_level,
            digest_length
        )
        VALUES (%s, %s, %s)
        """

        values = (
            name,
            knowledge_level,
            digest_length
        )

        cursor.execute(query, values)

        user_id = cursor.lastrowid

        interest_query = """
        INSERT INTO user_interests (
            user_id,
            interest
        )
        VALUES (%s, %s)
        """

        for interest in interests:

            cursor.execute(
                interest_query,
                (
                    user_id,
                    interest
                )
            )

        connection.commit()

        print("User profile saved successfully")

        return user_id

    except Error as e:

        print("ERROR SAVING USER PROFILE:", e)

        return None

    finally:

        cursor.close()
        connection.close()


# =====================================================
# SAVE FEEDBACK TO MYSQL
# =====================================================

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

    print("save_feedback_to_mysql called")

    connection = get_connection()

    if connection is None:
        return False

    try:

        cursor = connection.cursor()

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
            float(relevance_score),
            clickbait_label,
            float(duplicate_score),
            float(noise_score),
            float(trust_score)
        )

        cursor.execute(query, values)

        connection.commit()

        print("Feedback saved successfully")

        return True

    except Error as e:

        print("ERROR SAVING FEEDBACK:", e)

        return False

    finally:

        cursor.close()
        connection.close()


# =====================================================
# GET FEEDBACK FROM MYSQL
# =====================================================

def get_feedback_from_mysql():

    print("get_feedback_from_mysql called")

    connection = get_connection()

    if connection is None:
        return []

    try:

        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT
            feedback_id,
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
            trust_score,
            created_at
        FROM feedback
        ORDER BY created_at DESC
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        print("Feedback fetched successfully")

        return rows

    except Error as e:

        print("ERROR FETCHING FEEDBACK:", e)

        return []

    finally:

        cursor.close()
        connection.close()