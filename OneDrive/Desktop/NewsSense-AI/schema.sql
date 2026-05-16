CREATE DATABASE IF NOT EXISTS newsense_ai;

USE newsense_ai;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    knowledge_level VARCHAR(50),
    digest_length VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_interests (
    interest_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    interest VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100),
    knowledge_level VARCHAR(50),
    digest_length VARCHAR(50),
    selected_interests TEXT,
    title VARCHAR(255),
    topic VARCHAR(100),
    feedback VARCHAR(100),
    relevance_score FLOAT,
    clickbait_label VARCHAR(50),
    duplicate_score FLOAT,
    noise_score FLOAT,
    trust_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SHOW TABLES;
