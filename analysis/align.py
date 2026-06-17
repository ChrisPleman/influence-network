"""Semantic similarity between lobbying issue text and bill text.

This is the capstone's headline NLP step: given a lobbying-activity description
and a bill's text/summary, how aligned are they? Two backends:

* TF-IDF + cosine  (default; light, no downloads, a solid baseline)
* sentence-transformers embeddings + cosine  (better; needs the model)

Usage:
    from analysis.align import similarity, similarity_matrix
    similarity("telehealth expansion for workers",
               "A bill to expand telehealth benefits...")   # -> 0.0..1.0
"""
from __future__ import annotations

from typing import Sequence

# --- TF-IDF backend (always available) ---------------------------------------

def _tfidf_similarity_matrix(a_texts: Sequence[str], b_texts: Sequence[str]):
    """Cosine similarity of every a vs every b using TF-IDF. Returns a matrix."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    matrix = vec.fit_transform(list(a_texts) + list(b_texts))
    a_mat = matrix[: len(a_texts)]
    b_mat = matrix[len(a_texts):]
    return cosine_similarity(a_mat, b_mat)


# --- sentence-transformers backend (optional, better) ------------------------

_MODEL = None


def _get_model(model_name: str = "all-MiniLM-L6-v2"):
    """Lazily load and cache the embedding model."""
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer(model_name)
    return _MODEL


def _embed_similarity_matrix(a_texts: Sequence[str], b_texts: Sequence[str]):
    from sentence_transformers import util
    model = _get_model()
    a_emb = model.encode(list(a_texts), convert_to_tensor=True, normalize_embeddings=True)
    b_emb = model.encode(list(b_texts), convert_to_tensor=True, normalize_embeddings=True)
    return util.cos_sim(a_emb, b_emb).cpu().numpy()


# --- public API --------------------------------------------------------------

def similarity_matrix(a_texts: Sequence[str], b_texts: Sequence[str],
                      method: str = "tfidf"):
    """Return an (len(a) x len(b)) cosine-similarity matrix.

    method: "tfidf" (default, no downloads) or "embeddings" (sentence-transformers).
    """
    if method == "embeddings":
        return _embed_similarity_matrix(a_texts, b_texts)
    return _tfidf_similarity_matrix(a_texts, b_texts)


def similarity(text_a: str, text_b: str, method: str = "tfidf") -> float:
    """Cosine similarity between two single texts, in [0, 1]."""
    return float(similarity_matrix([text_a], [text_b], method=method)[0][0])
