from transformers import pipeline
import re

# ---------------------------------------
# LOAD MODEL (STABLE & ACCURATE)
# ---------------------------------------
summarizer = pipeline(
    "summarization",
    model="google/pegasus-cnn_dailymail",
    device=-1
)

# ---------------------------------------
# CLEAN TEXT
# ---------------------------------------
def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()

# ---------------------------------------
# REMOVE NOISE
# ---------------------------------------
def remove_noise(text):
    sentences = text.split(".")
    filtered = []

    for s in sentences:
        s = s.strip()

        if len(s.split()) < 6:
            continue

        if any(k in s.lower() for k in [
            "copyright", "all rights reserved",
            "isbn", "publisher", "printed in"
        ]):
            continue

        filtered.append(s)

    return ". ".join(filtered)

# ---------------------------------------
# SPLIT INTO CHUNKS
# ---------------------------------------
def split_into_chunks(text, max_words=150):
    words = text.split()
    return [
        " ".join(words[i:i + max_words])
        for i in range(0, len(words), max_words)
    ]

# ---------------------------------------
# SUMMARIZE SINGLE CHUNK (FIXED)
# ---------------------------------------
def summarize_chunk(chunk):

    chunk = "Summarize the following text:\n" + chunk

    # 🔥 Dynamic length control
    input_len = len(chunk.split())

    max_len = min(60, int(input_len * 0.6))
    min_len = min(25, int(input_len * 0.3))

    # Safety fallback
    if max_len < 15:
        max_len = 15
    if min_len < 5:
        min_len = 5

    try:
        result = summarizer(
            chunk,
            max_length=max_len,
            min_length=min_len,
            do_sample=False   # stable, no hallucination
        )

        return result[0]["summary_text"]

    except Exception as e:
        print("Chunk summarization error:", e)
        return ""

# ---------------------------------------
# MAIN FUNCTION
# ---------------------------------------
def generate_summary(text):

    if not text:
        return ""

    try:
        # Step 1: Clean
        text = clean_text(text)

        # Step 2: Remove noise
        text = remove_noise(text)

        # Step 3: Handle short text
        if len(text.split()) < 80:
            return summarize_chunk(text)

        # Step 4: Chunking
        chunks = split_into_chunks(text)

        summaries = []

        # Step 5: Process chunks
        for chunk in chunks:
            summary = summarize_chunk(chunk)
            if summary:
                summaries.append(summary)

        if not summaries:
            return "No meaningful content found."

        # Step 6: Final summarization
        final_input = " ".join(summaries[:5])
        final_summary = summarize_chunk(final_input)

        return final_summary if final_summary else " ".join(summaries)

    except Exception as e:
        print("Summarization failed:", e)
        return ""