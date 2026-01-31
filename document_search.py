#!/usr/bin/env python3
"""
Smart Document Search and Retrieval System

Features:
- Keyword-based search with TF-IDF ranking
- Text preprocessing (stemming, stopword removal)
- Multiple search modes (AND, OR, phrase search)
- Document indexing and caching
- Relevance scoring
"""

import os
import re
import json
import pickle
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple
import math


class DocumentSearchEngine:
    """
    A smart document search engine with keyword-based retrieval.
    """
    
    def __init__(self, stopwords_file: str = None):
        """
        Initialize the search engine.
        
        Args:
            stopwords_file: Path to custom stopwords file (optional)
        """
        self.documents: Dict[str, str] = {}
        self.doc_metadata: Dict[str, Dict] = {}
        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)
        self.term_frequencies: Dict[str, Dict[str, int]] = {}
        self.doc_frequencies: Dict[str, int] = defaultdict(int)
        self.doc_lengths: Dict[str, int] = {}
        
        # Default common English stopwords
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
        }
        
        if stopwords_file and os.path.exists(stopwords_file):
            self.load_stopwords(stopwords_file)
    
    def load_stopwords(self, filepath: str):
        """Load custom stopwords from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.stopwords = set(line.strip().lower() for line in f if line.strip())
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text: lowercase, remove punctuation, tokenize, remove stopwords.
        
        Args:
            text: Raw text string
            
        Returns:
            List of preprocessed tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and special characters, keep alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Tokenize
        tokens = text.split()
        
        # Remove stopwords and short tokens
        tokens = [token for token in tokens if token not in self.stopwords and len(token) > 2]
        
        return tokens
    
    def add_document(self, doc_id: str, content: str, metadata: Dict = None):
        """
        Add a document to the search engine.
        
        Args:
            doc_id: Unique document identifier
            content: Document text content
            metadata: Optional metadata (title, author, date, etc.)
        """
        self.documents[doc_id] = content
        self.doc_metadata[doc_id] = metadata or {}
        
        # Preprocess and index
        tokens = self.preprocess_text(content)
        
        # Calculate term frequencies for this document
        term_freq = Counter(tokens)
        self.term_frequencies[doc_id] = dict(term_freq)
        self.doc_lengths[doc_id] = len(tokens)
        
        # Update inverted index and document frequencies
        unique_terms = set(tokens)
        for term in unique_terms:
            self.inverted_index[term].add(doc_id)
            self.doc_frequencies[term] += 1
    
    def load_documents_from_directory(self, directory: str, extensions: List[str] = None):
        """
        Load all documents from a directory.
        
        Args:
            directory: Path to directory containing documents
            extensions: List of file extensions to include (e.g., ['.txt', '.md'])
        """
        extensions = extensions or ['.txt', '.md', '.text']
        directory_path = Path(directory)
        
        for filepath in directory_path.rglob('*'):
            if filepath.is_file() and filepath.suffix.lower() in extensions:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    doc_id = str(filepath.relative_to(directory_path))
                    metadata = {
                        'filename': filepath.name,
                        'path': str(filepath),
                        'size': filepath.stat().st_size
                    }
                    
                    self.add_document(doc_id, content, metadata)
                    print(f"Indexed: {doc_id}")
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
    
    def calculate_tf_idf(self, term: str, doc_id: str) -> float:
        """
        Calculate TF-IDF score for a term in a document.
        
        Args:
            term: Search term
            doc_id: Document identifier
            
        Returns:
            TF-IDF score
        """
        if doc_id not in self.term_frequencies or term not in self.term_frequencies[doc_id]:
            return 0.0
        
        # Term Frequency (TF)
        tf = self.term_frequencies[doc_id][term] / self.doc_lengths[doc_id]
        
        # Inverse Document Frequency (IDF)
        num_docs = len(self.documents)
        doc_freq = self.doc_frequencies.get(term, 0)
        
        if doc_freq == 0:
            return 0.0
        
        idf = math.log(num_docs / doc_freq)
        
        return tf * idf
    
    def search(self, query: str, mode: str = 'OR', top_k: int = 10) -> List[Tuple[str, float, Dict]]:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query string
            mode: Search mode - 'OR' (any term), 'AND' (all terms), or 'PHRASE' (exact phrase)
            top_k: Number of top results to return
            
        Returns:
            List of tuples (doc_id, score, metadata) sorted by relevance
        """
        # Preprocess query
        query_terms = self.preprocess_text(query)
        
        if not query_terms:
            return []
        
        # Find candidate documents
        if mode == 'AND':
            # Documents must contain all terms
            candidate_docs = set(self.documents.keys())
            for term in query_terms:
                candidate_docs &= self.inverted_index.get(term, set())
        elif mode == 'PHRASE':
            # Exact phrase match
            return self._phrase_search(query, top_k)
        else:  # OR mode
            # Documents contain any term
            candidate_docs = set()
            for term in query_terms:
                candidate_docs |= self.inverted_index.get(term, set())
        
        # Calculate relevance scores
        scores = []
        for doc_id in candidate_docs:
            score = 0.0
            for term in query_terms:
                score += self.calculate_tf_idf(term, doc_id)
            
            if score > 0:
                scores.append((doc_id, score, self.doc_metadata.get(doc_id, {})))
        
        # Sort by score (descending) and return top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def _phrase_search(self, phrase: str, top_k: int) -> List[Tuple[str, float, Dict]]:
        """
        Search for exact phrase matches.
        
        Args:
            phrase: Exact phrase to search for
            top_k: Number of top results to return
            
        Returns:
            List of tuples (doc_id, score, metadata)
        """
        phrase_lower = phrase.lower()
        results = []
        
        for doc_id, content in self.documents.items():
            content_lower = content.lower()
            count = content_lower.count(phrase_lower)
            
            if count > 0:
                # Score based on frequency and document length
                score = count / len(content.split())
                results.append((doc_id, score, self.doc_metadata.get(doc_id, {})))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def get_document_snippet(self, doc_id: str, query: str, snippet_length: int = 200) -> str:
        """
        Get a relevant snippet from the document containing query terms.
        
        Args:
            doc_id: Document identifier
            query: Search query
            snippet_length: Length of snippet in characters
            
        Returns:
            Document snippet
        """
        if doc_id not in self.documents:
            return ""
        
        content = self.documents[doc_id]
        query_terms = self.preprocess_text(query)
        
        # Find first occurrence of any query term
        best_pos = len(content)
        for term in query_terms:
            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
            match = pattern.search(content)
            if match:
                best_pos = min(best_pos, match.start())
        
        if best_pos == len(content):
            # No match found, return beginning
            return content[:snippet_length] + "..."
        
        # Extract snippet around the match
        start = max(0, best_pos - snippet_length // 2)
        end = min(len(content), start + snippet_length)
        
        snippet = content[start:end]
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    def save_index(self, filepath: str):
        """Save the search index to disk."""
        index_data = {
            'documents': self.documents,
            'doc_metadata': self.doc_metadata,
            'inverted_index': {k: list(v) for k, v in self.inverted_index.items()},
            'term_frequencies': self.term_frequencies,
            'doc_frequencies': dict(self.doc_frequencies),
            'doc_lengths': self.doc_lengths
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(index_data, f)
        
        print(f"Index saved to {filepath}")
    
    def load_index(self, filepath: str):
        """Load the search index from disk."""
        with open(filepath, 'rb') as f:
            index_data = pickle.load(f)
        
        self.documents = index_data['documents']
        self.doc_metadata = index_data['doc_metadata']
        self.inverted_index = {k: set(v) for k, v in index_data['inverted_index'].items()}
        self.term_frequencies = index_data['term_frequencies']
        self.doc_frequencies = defaultdict(int, index_data['doc_frequencies'])
        self.doc_lengths = index_data['doc_lengths']
        
        print(f"Index loaded from {filepath}")
    
    def get_statistics(self) -> Dict:
        """Get search engine statistics."""
        return {
            'total_documents': len(self.documents),
            'total_terms': len(self.inverted_index),
            'average_doc_length': sum(self.doc_lengths.values()) / len(self.doc_lengths) if self.doc_lengths else 0
        }


def main():
    """Example usage of the document search engine."""
    
    # Create search engine
    engine = DocumentSearchEngine()
    
    # Add sample documents
    sample_docs = {
        'doc1': {
            'content': 'Python is a high-level programming language. It is widely used for web development, data science, and automation.',
            'metadata': {'title': 'Introduction to Python', 'author': 'John Doe'}
        },
        'doc2': {
            'content': 'Machine learning is a subset of artificial intelligence. Python is the most popular language for machine learning.',
            'metadata': {'title': 'Machine Learning Basics', 'author': 'Jane Smith'}
        },
        'doc3': {
            'content': 'Web development involves creating websites and web applications. Popular frameworks include Django and Flask.',
            'metadata': {'title': 'Web Development Guide', 'author': 'Bob Johnson'}
        },
        'doc4': {
            'content': 'Data science combines statistics, programming, and domain knowledge to extract insights from data.',
            'metadata': {'title': 'Data Science Overview', 'author': 'Alice Williams'}
        }
    }
    
    print("=" * 70)
    print("SMART DOCUMENT SEARCH ENGINE")
    print("=" * 70)
    
    # Index documents
    print("\nIndexing documents...")
    for doc_id, doc_data in sample_docs.items():
        engine.add_document(doc_id, doc_data['content'], doc_data['metadata'])
    
    # Display statistics
    stats = engine.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total documents: {stats['total_documents']}")
    print(f"  Total unique terms: {stats['total_terms']}")
    print(f"  Average document length: {stats['average_doc_length']:.2f} tokens")
    
    # Perform searches
    queries = [
        ('python programming', 'OR'),
        ('machine learning python', 'AND'),
        ('web development', 'OR')
    ]
    
    for query, mode in queries:
        print(f"\n{'=' * 70}")
        print(f"Search Query: '{query}' (Mode: {mode})")
        print(f"{'=' * 70}")
        
        results = engine.search(query, mode=mode, top_k=3)
        
        if not results:
            print("No results found.")
        else:
            for i, (doc_id, score, metadata) in enumerate(results, 1):
                print(f"\n{i}. Document: {doc_id}")
                print(f"   Title: {metadata.get('title', 'N/A')}")
                print(f"   Author: {metadata.get('author', 'N/A')}")
                print(f"   Relevance Score: {score:.4f}")
                print(f"   Snippet: {engine.get_document_snippet(doc_id, query, 150)}")
    
    # Save index
    print(f"\n{'=' * 70}")
    index_file = '/home/claude/search_index.pkl'
    engine.save_index(index_file)
    
    print("\nDemo completed successfully!")


if __name__ == '__main__':
    main()