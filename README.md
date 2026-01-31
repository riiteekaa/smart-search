# Smart Document Search & Retrieval System

A powerful keyword-based document search engine with TF-IDF ranking, text preprocessing, and multiple search modes.

## Features

- **TF-IDF Ranking**: Uses Term Frequency-Inverse Document Frequency for relevance scoring
- **Text Preprocessing**: Automatic tokenization, lowercasing, stopword removal
- **Multiple Search Modes**:
  - `OR`: Match any keyword (default)
  - `AND`: Match all keywords
  - `PHRASE`: Exact phrase matching
- **Document Indexing**: Fast inverted index for efficient searching
- **Snippet Extraction**: Context-aware snippet generation
- **Index Persistence**: Save and load search indexes
- **Metadata Support**: Store and retrieve document metadata
- **Batch Loading**: Load multiple documents from directories

## Installation

No external dependencies required! Uses only Python standard library.

```bash
python document_search.py
```

## Quick Start

```python
from document_search import DocumentSearchEngine

# Create search engine
engine = DocumentSearchEngine()

# Add documents
engine.add_document(
    doc_id='doc1',
    content='Python is great for data science and machine learning.',
    metadata={'title': 'Python Guide', 'author': 'John Doe'}
)

# Search
results = engine.search('python data science', mode='AND', top_k=5)

# Display results
for doc_id, score, metadata in results:
    print(f"Document: {doc_id}, Score: {score:.4f}")
    print(f"Snippet: {engine.get_document_snippet(doc_id, 'python data science')}")
```

## Usage Examples

### 1. Adding Individual Documents

```python
engine = DocumentSearchEngine()

engine.add_document(
    doc_id='report_2024',
    content='Annual financial report for 2024...',
    metadata={
        'title': '2024 Annual Report',
        'author': 'Finance Team',
        'date': '2024-12-31'
    }
)
```

### 2. Loading Documents from Directory

```python
# Load all .txt and .md files from a directory
engine.load_documents_from_directory(
    directory='/path/to/documents',
    extensions=['.txt', '.md', '.doc']
)
```

### 3. Different Search Modes

```python
# OR search - match any keyword
results = engine.search('python machine learning', mode='OR')

# AND search - match all keywords
results = engine.search('python machine learning', mode='AND')

# PHRASE search - exact phrase
results = engine.search('machine learning algorithms', mode='PHRASE')
```

### 4. Working with Results

```python
results = engine.search('artificial intelligence', top_k=10)

for doc_id, score, metadata in results:
    print(f"\nDocument ID: {doc_id}")
    print(f"Title: {metadata.get('title', 'Untitled')}")
    print(f"Relevance Score: {score:.4f}")
    
    # Get contextual snippet
    snippet = engine.get_document_snippet(doc_id, 'artificial intelligence', 200)
    print(f"Snippet: {snippet}")
    
    # Access full document
    full_text = engine.documents[doc_id]
```

### 5. Saving and Loading Index

```python
# Save index to disk
engine.save_index('my_search_index.pkl')

# Load index from disk
new_engine = DocumentSearchEngine()
new_engine.load_index('my_search_index.pkl')
```

### 6. Custom Stopwords

```python
# Create stopwords file (one word per line)
with open('custom_stopwords.txt', 'w') as f:
    f.write('the\nand\nor\nbut\n')

# Use custom stopwords
engine = DocumentSearchEngine(stopwords_file='custom_stopwords.txt')
```

### 7. Get Statistics

```python
stats = engine.get_statistics()
print(f"Total documents: {stats['total_documents']}")
print(f"Unique terms: {stats['total_terms']}")
print(f"Avg doc length: {stats['average_doc_length']:.2f}")
```

## How It Works

### 1. **Text Preprocessing**
- Converts text to lowercase
- Removes punctuation and special characters
- Tokenizes into words
- Removes stopwords (common words like "the", "and", etc.)
- Filters short tokens (< 3 characters)

### 2. **Inverted Index**
- Maps each unique term to documents containing it
- Enables fast lookup of candidate documents

### 3. **TF-IDF Scoring**
- **Term Frequency (TF)**: How often a term appears in a document
- **Inverse Document Frequency (IDF)**: How rare the term is across all documents
- **TF-IDF Score**: TF × IDF (higher = more relevant)

### 4. **Ranking**
- Calculates TF-IDF score for each query term in each document
- Sums scores across all query terms
- Ranks results by total score

## API Reference

### DocumentSearchEngine

#### Methods

**`__init__(stopwords_file=None)`**
- Initialize search engine with optional custom stopwords

**`add_document(doc_id, content, metadata=None)`**
- Add single document to index
- `doc_id`: Unique identifier
- `content`: Document text
- `metadata`: Optional dict with title, author, etc.

**`load_documents_from_directory(directory, extensions=None)`**
- Load all documents from directory
- `directory`: Path to directory
- `extensions`: List of file extensions (default: ['.txt', '.md', '.text'])

**`search(query, mode='OR', top_k=10)`**
- Search for documents
- `query`: Search query string
- `mode`: 'OR', 'AND', or 'PHRASE'
- `top_k`: Maximum number of results
- Returns: List of (doc_id, score, metadata) tuples

**`get_document_snippet(doc_id, query, snippet_length=200)`**
- Extract relevant snippet from document
- `doc_id`: Document identifier
- `query`: Search query for context
- `snippet_length`: Length in characters
- Returns: Context snippet string

**`save_index(filepath)`**
- Save index to disk (pickle format)

**`load_index(filepath)`**
- Load index from disk

**`get_statistics()`**
- Get search engine statistics
- Returns: Dict with total_documents, total_terms, average_doc_length

## Advanced Example

```python
# Build a documentation search system
engine = DocumentSearchEngine()

# Load documents
engine.load_documents_from_directory('./docs', extensions=['.md', '.txt'])

# Interactive search
while True:
    query = input("\nEnter search query (or 'quit'): ")
    if query.lower() == 'quit':
        break
    
    mode = input("Search mode (OR/AND/PHRASE): ").upper()
    
    results = engine.search(query, mode=mode, top_k=5)
    
    if not results:
        print("No results found.")
        continue
    
    print(f"\nFound {len(results)} results:\n")
    
    for i, (doc_id, score, metadata) in enumerate(results, 1):
        print(f"{i}. {metadata.get('title', doc_id)}")
        print(f"   Score: {score:.4f}")
        print(f"   {engine.get_document_snippet(doc_id, query, 150)}\n")
```

## Performance Tips

1. **Index Persistence**: Save index to avoid re-indexing on each run
2. **Batch Loading**: Use `load_documents_from_directory()` for multiple files
3. **Appropriate top_k**: Limit results to what you need
4. **Choose Right Mode**: Use AND for precise results, OR for broader search
5. **Custom Stopwords**: Tailor stopwords to your domain

## Limitations

- No stemming/lemmatization (can be added)
- Simple tokenization (word-based)
- In-memory storage (not suitable for very large corpora)
- No fuzzy matching or spell correction

## Future Enhancements

- Add stemming (Porter/Lancaster stemmer)
- Support for synonyms and word embeddings
- Boolean operators in queries
- Fuzzy matching for typos
- Pagination for large result sets
- Multi-language support
- Phrase proximity search

## License

MIT License - Free to use and modify