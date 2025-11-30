"""In-memory vector database for content search."""

from __future__ import annotations

import math
import string
from typing import Any, Dict, Iterable, List, Tuple

from .models import LearningContent


class VectorDBManager:
    """In-memory index that supports BM25, dense and hybrid search."""

    def __init__(self) -> None:
        self._contents: Dict[str, LearningContent] = {}
        self._tokenized_docs: Dict[str, List[str]] = {}
        self._tfidf_vectors: Dict[str, Dict[str, float]] = {}
        self._vector_norms: Dict[str, float] = {}
        self._doc_freq: Dict[str, int] = {}
        self._doc_lengths: Dict[str, int] = {}
        self._avg_doc_len: float = 0.0

    def add_contents(self, contents: Iterable[LearningContent]) -> None:
        """Add or replace a batch of contents and rebuild indices."""
        updated = False
        for content in contents:
            updated = True
            self._contents[content.id] = content
        if updated:
            self._rebuild_indices()

    @property
    def contents(self) -> Dict[str, LearningContent]:
        return self._contents

    def search(
        self,
        query: str,
        top_k: int = 10,
        strategy: str = "hybrid",
        *,
        dense_weight: float = 0.65,
    ) -> List[Tuple[LearningContent, float]]:
        """Return ranked results for query using the desired strategy.

        Args:
            query: The free form search string.
            top_k: Maximum number of results to return.
            strategy: One of "dense", "bm25" or "hybrid".
            dense_weight: Combination weight used for the hybrid mode.
        """
        if not query.strip():
            return []

        if strategy not in {"dense", "bm25", "hybrid"}:
            raise ValueError(f"Unsupported strategy '{strategy}'.")

        bm25_scores = self._bm25_scores(query)
        dense_scores = self._dense_scores(query)

        if strategy == "bm25":
            combined = bm25_scores
        elif strategy == "dense":
            combined = dense_scores
        else:
            combined = self._combine_scores(bm25_scores, dense_scores, dense_weight)

        ordered_ids = sorted(combined, key=combined.get, reverse=True)
        results: List[Tuple[LearningContent, float]] = []
        for content_id in ordered_ids[:top_k]:
            results.append((self._contents[content_id], combined[content_id]))
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        translator = str.maketrans({c: " " for c in string.punctuation})
        clean = text.translate(translator).lower()
        return [token for token in clean.split() if token]

    def _rebuild_indices(self) -> None:
        self._tokenized_docs.clear()
        self._tfidf_vectors.clear()
        self._vector_norms.clear()
        self._doc_freq.clear()
        self._doc_lengths.clear()

        for content_id, content in self._contents.items():
            tokens = self._tokenize(content.document_text())
            self._tokenized_docs[content_id] = tokens
            token_counts: Dict[str, int] = {}
            for token in tokens:
                token_counts[token] = token_counts.get(token, 0) + 1
            
            # Update document frequency (once per document, not per occurrence)
            for token in token_counts:
                self._doc_freq[token] = self._doc_freq.get(token, 0) + 1
            
            self._doc_lengths[content_id] = len(tokens)
            self._tfidf_vectors[content_id] = token_counts

        total_docs = len(self._contents)
        if total_docs == 0:
            self._avg_doc_len = 0.0
            return

        self._avg_doc_len = sum(self._doc_lengths.values()) / total_docs

        for content_id, token_counts in self._tfidf_vectors.items():
            tfidf_vector: Dict[str, float] = {}
            norm = 0.0
            for token, count in token_counts.items():
                tf = 1 + math.log(count)
                df = self._doc_freq[token]
                idf = math.log((total_docs + 1) / (df + 1)) + 1
                value = tf * idf
                tfidf_vector[token] = value
                norm += value * value
            self._tfidf_vectors[content_id] = tfidf_vector
            self._vector_norms[content_id] = math.sqrt(norm) if norm else 0.0

    def _dense_scores(self, query: str) -> Dict[str, float]:
        tokens = self._tokenize(query)
        if not tokens:
            return {}
        query_counts: Dict[str, int] = {}
        for token in tokens:
            query_counts[token] = query_counts.get(token, 0) + 1

        total_docs = len(self._contents)
        query_vector: Dict[str, float] = {}
        norm = 0.0
        for token, count in query_counts.items():
            tf = 1 + math.log(count)
            df = self._doc_freq.get(token)
            if not df:
                continue
            idf = math.log((total_docs + 1) / (df + 1)) + 1
            value = tf * idf
            query_vector[token] = value
            norm += value * value
        query_norm = math.sqrt(norm) if norm else 0.0

        scores: Dict[str, float] = {}
        if not query_vector:
            return scores
        for content_id, doc_vector in self._tfidf_vectors.items():
            numerator = 0.0
            for token, weight in query_vector.items():
                numerator += weight * doc_vector.get(token, 0.0)
            doc_norm = self._vector_norms.get(content_id, 0.0)
            if numerator and doc_norm and query_norm:
                scores[content_id] = numerator / (doc_norm * query_norm)
        return scores

    def _bm25_scores(
        self,
        query: str,
        *,
        k1: float = 1.6,
        b: float = 0.75,
    ) -> Dict[str, float]:
        tokens = self._tokenize(query)
        scores: Dict[str, float] = {}
        if not tokens:
            return scores
        total_docs = len(self._contents)
        for token in tokens:
            df = self._doc_freq.get(token)
            if not df:
                continue
            idf = math.log(1 + (total_docs - df + 0.5) / (df + 0.5))
            for content_id, doc_tokens in self._tokenized_docs.items():
                freq = doc_tokens.count(token)
                if not freq:
                    continue
                numerator = freq * (k1 + 1)
                denominator = freq + k1 * (1 - b + b * self._doc_lengths[content_id] / (self._avg_doc_len or 1))
                scores[content_id] = scores.get(content_id, 0.0) + idf * (numerator / denominator)
        return scores

    @staticmethod
    def _combine_scores(
        bm25_scores: Dict[str, float],
        dense_scores: Dict[str, float],
        dense_weight: float,
    ) -> Dict[str, float]:
        combined: Dict[str, float] = {}
        for content_id, score in bm25_scores.items():
            combined[content_id] = combined.get(content_id, 0.0) + (1 - dense_weight) * score
        for content_id, score in dense_scores.items():
            combined[content_id] = combined.get(content_id, 0.0) + dense_weight * score
        return combined

    def _bm25_search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        scores = self._bm25_scores(query)
        ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return ordered[:top_k]
