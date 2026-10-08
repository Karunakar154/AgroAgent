import os
import re

from sentence_transformers import SentenceTransformer


# ==================================================
# FILE LOCATION
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

KNOWLEDGE_FILE = os.path.join(
    BASE_DIR,
    "agriculture_knowledge.txt"
)


# ==================================================
# LOAD KNOWLEDGE
# ==================================================

with open(
    KNOWLEDGE_FILE,
    "r",
    encoding="utf-8"
) as file:

    knowledge = file.read().strip()


# ==================================================
# SPLIT KNOWLEDGE INTO MEANINGFUL SECTIONS
# ==================================================

lines = knowledge.splitlines()

documents = []

current_title = None
current_content = []


for line in lines:

    line = line.strip()

    # Ignore empty lines
    if not line:
        continue


    # Ignore separator lines
    if line.startswith("==="):
        continue


    # Detect numbered section headings
    #
    # Example:
    # 1. GENERAL CROP CULTIVATION
    # 26. TOMATO
    # 27. MUSKMELON
    #
    if re.match(
        r"^\d+\.\s+.+",
        line
    ):

        # Save previous section
        if current_title is not None:

            content = " ".join(
                current_content
            ).strip()

            if content:

                documents.append(
                    current_title
                    + "\n"
                    + content
                )


        # Start new section
        current_title = line

        current_content = []


    else:

        current_content.append(line)


# ==================================================
# SAVE LAST SECTION
# ==================================================

if current_title is not None:

    content = " ".join(
        current_content
    ).strip()

    if content:

        documents.append(
            current_title
            + "\n"
            + content
        )


# ==================================================
# EMBEDDING MODEL
# ==================================================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ==================================================
# CREATE EMBEDDINGS
# ==================================================

embeddings = embedding_model.encode(
    documents,
    convert_to_numpy=True,
    normalize_embeddings=True
)


# ==================================================
# FUNCTIONS
# ==================================================

def get_documents():

    return documents


def get_embeddings():

    return embeddings


def get_embedding_model():

    return embedding_model