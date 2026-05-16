def generate_summary(text, existing_summary="", knowledge_level="Beginner", digest_length="Short"):
    text = str(text)
    existing_summary = str(existing_summary)

    if existing_summary and existing_summary.lower() != "nan":
        base_summary = existing_summary
    else:
        sentences = text.split(".")
        base_summary = ". ".join(sentences[:2]).strip()

    if digest_length == "Short":
        words = base_summary.split()[:40]
    elif digest_length == "Medium":
        words = base_summary.split()[:80]
    else:
        words = base_summary.split()[:130]

    summary = " ".join(words)

    if knowledge_level == "Beginner":
        return "Simple explanation: " + summary

    elif knowledge_level == "Intermediate":
        return "Balanced explanation: " + summary

    else:
        return "Expert insight: " + summary + " This news may have broader social, economic, or policy-level impact."