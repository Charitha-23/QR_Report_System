from transformers import pipeline
import re

# ---------------------------------------
# LOAD MODEL
# ---------------------------------------
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
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

        if len(s) < 30:
            continue

        if any(k in s.lower() for k in [
            "copyright",
            "all rights reserved",
            "no part of this",
            "any similarity",
            "fictional",
            "isbn",
            "printed in",
            "publisher"
        ]):
            continue

        filtered.append(s)

    return ". ".join(filtered)


# ---------------------------------------
# CHECK IF CHUNK IS MEANINGFUL
# ---------------------------------------
def is_meaningful(chunk):

    words = chunk.split()

    if len(words) < 50:
        return False

    avg_len = sum(len(w) for w in words) / len(words)

    if avg_len < 3:
        return False

    return True


# ---------------------------------------
# SPLIT INTO CHUNKS
# ---------------------------------------
def split_into_chunks(text, max_words=300):

    words = text.split()
    chunks = []

    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)

    return chunks


# ---------------------------------------
# SUMMARIZE SINGLE CHUNK
# ---------------------------------------
def summarize_chunk(chunk):

    try:
        result = summarizer(
            chunk,
            max_length=120,
            min_length=40,
            do_sample=False
        )

        return result[0]["summary_text"]

    except Exception as e:
        print("Chunk summarization error:", e)
        return ""


# ---------------------------------------
# FORMAT SHORT TEXT
# ---------------------------------------
def format_short_text(text):

    sentences = text.split(".")
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    return "\n".join([f"• {s}" for s in sentences[:5]])


# ---------------------------------------
# MAIN FUNCTION
# ---------------------------------------
def generate_summary(text):

    if not text:
        return ""

    try:
        # Step 1: Clean text
        text = clean_text(text)

        # Step 2: Remove noise
        text = remove_noise(text)

        print("\n--- CLEANED TEXT SAMPLE ---\n", text[:500])

        # Step 3: Handle short text
        if len(text) < 150:
            print("Text too short → skipping AI")
            return format_short_text(text)

        # Step 4: Split into chunks
        chunks = split_into_chunks(text, max_words=300)

        print(f"Total chunks before filtering: {len(chunks)}")

        # Step 5: Limit chunks (important)
        chunks = chunks[:20]

        chunk_summaries = []

        # Step 6: Process chunks
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}")

            if not is_meaningful(chunk):
                print("Skipping noisy chunk")
                continue

            summary = summarize_chunk(chunk)

            if summary:
                chunk_summaries.append(summary)

        if not chunk_summaries:
            return "No meaningful content found for summarization."

        # Step 7: Combine summaries
        combined_summary = "\n".join(chunk_summaries)

        # Step 8: Final summarization
        if len(chunk_summaries) > 3:
            print("Generating final summary...")

            final_input = " ".join(chunk_summaries[:10])

            final = summarize_chunk(final_input)

            return final if final else combined_summary

        return combined_summary

    except Exception as e:
        print("Summarization failed:", e)
        return ""
    
import re

STOP_WORDS = ["show", "me", "on", "in", "the", "about", "for", "all"]

SYNONYMS = {
    "failure": ["failure", "fault", "breakdown", "error"],
    "machine": ["machine", "equipment", "device"],
    "report": ["report", "document", "file"]
}

def extract_keywords(query):
    words = re.findall(r'\w+', query.lower())
    return [w for w in words if w not in STOP_WORDS]


def expand_keywords(keywords):
    expanded = set()

    for word in keywords:
        expanded.add(word)
        if word in SYNONYMS:
            expanded.update(SYNONYMS[word])

    return list(expanded)


def process_query(query):
    keywords = extract_keywords(query)
    keywords = expand_keywords(keywords)
    return keywords