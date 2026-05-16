# NewsSense AI
## A News Noise Reduction and Personalized Knowledge Digest Engine

AI-powered system for cleaner, smarter, and personalized news consumption.

---

# Problem Statement

## PS 10 — News Without the Noise

Today’s users face:
- Information overload
- Duplicate news across platforms
- Clickbait headlines
- Sensational content
- Irrelevant recommendations
- Long unreadable articles
- One-size-fits-all summaries

NewsSense AI solves this by transforming noisy news into a clean, personalized, trustworthy, and actionable daily digest.

---

# Project Overview

NewsSense AI is an AI-powered personalized news intelligence system that:

- Filters irrelevant news
- Removes duplicate articles
- Detects clickbait headlines
- Calculates a News Noise Score
- Generates personalized summaries
- Explains why news matters to the user
- Tracks reading time saved
- Learns from user feedback

The platform focuses on helping users consume **better news, not more news**.

---

# Key Features

## Core Features
- User profile creation
- Interest-based personalization
- Knowledge-level summaries
- Duplicate news filtering
- Clickbait detection
- Noise score calculation
- Trust score calculation
- Personalized daily digest
- Reading time saved calculator
- Feedback learning system
- News Diet Dashboard

---

# Creative Features

## News Noise Score
Measures how noisy an article is using:
- Clickbait intensity
- Duplicate similarity
- Sensational words
- Low relevance

---

## Trust Score
Calculates article trustworthiness using:
- Source quality
- Low clickbait probability
- Cross-source similarity
- Content quality

---

## Why This Matters to You
Explains why the article is personally relevant based on:
- User interests
- Knowledge level
- Reading preferences

---

## Knowledge-Level Summary
Different summaries for:
- Beginner
- Intermediate
- Expert
- Student
- Professional
- Researcher

---

## Time Saved Calculator
Shows:
- Original reading time
- Digest reading time
- Total time saved

---

## News Diet Dashboard
Visual analytics for:
- Topic distribution
- Clickbait avoided
- Duplicate articles removed
- Reading time saved

---

# System Architecture

```text
User Profile
      ↓
News Collection
      ↓
Text Preprocessing
      ↓
Topic Matching
      ↓
Duplicate Detection
      ↓
Clickbait Detection
      ↓
Noise Score Calculation
      ↓
Trust Score Calculation
      ↓
Personalized Summarization
      ↓
Why This Matters Explanation
      ↓
Daily Digest Generation
      ↓
Feedback Learning
````

---

# Tech Stack

| Layer             | Technology                 |
| ----------------- | -------------------------- |
| Frontend          | Streamlit                  |
| Backend           | Python                     |
| ML/NLP            | scikit-learn, transformers |
| Similarity Engine | TF-IDF + Cosine Similarity |
| Database          | SQLite                     |
| Data Handling     | pandas                     |
| Visualization     | Streamlit Charts           |
| Deployment        | Streamlit Cloud            |
| Version Control   | GitHub                     |
