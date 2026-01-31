#!/usr/bin/env python3
"""
Interactive Document Search Demo

This script demonstrates how to use the DocumentSearchEngine
with an interactive command-line interface.
"""

from document_search import DocumentSearchEngine
import os


def create_sample_knowledge_base():
    """Create a sample knowledge base with various topics."""
    
    documents = {
        'ai_intro': {
            'content': '''
            Artificial Intelligence (AI) is the simulation of human intelligence by machines.
            AI systems can perform tasks that typically require human intelligence such as
            visual perception, speech recognition, decision-making, and language translation.
            Machine learning and deep learning are subsets of AI that enable systems to learn
            from data without explicit programming.
            ''',
            'metadata': {
                'title': 'Introduction to Artificial Intelligence',
                'category': 'Technology',
                'author': 'Dr. Sarah Chen',
                'date': '2024-01-15'
            }
        },
        'python_basics': {
            'content': '''
            Python is a versatile, high-level programming language known for its simplicity
            and readability. It supports multiple programming paradigms including procedural,
            object-oriented, and functional programming. Python is widely used in web development,
            data analysis, scientific computing, automation, and artificial intelligence.
            Popular frameworks include Django for web development and TensorFlow for machine learning.
            ''',
            'metadata': {
                'title': 'Python Programming Fundamentals',
                'category': 'Programming',
                'author': 'Mike Johnson',
                'date': '2024-02-20'
            }
        },
        'data_science': {
            'content': '''
            Data science is an interdisciplinary field that uses scientific methods, processes,
            algorithms, and systems to extract knowledge and insights from structured and
            unstructured data. It combines statistics, mathematics, programming, and domain
            expertise. Common tools include Python, R, SQL, and various visualization libraries
            like Matplotlib and Seaborn. Data scientists work with big data to solve complex problems.
            ''',
            'metadata': {
                'title': 'Data Science Overview',
                'category': 'Data',
                'author': 'Emily Rodriguez',
                'date': '2024-03-10'
            }
        },
        'ml_algorithms': {
            'content': '''
            Machine learning algorithms enable computers to learn from data and improve their
            performance over time. Supervised learning algorithms like linear regression, decision
            trees, and neural networks learn from labeled data. Unsupervised learning methods
            such as clustering and dimensionality reduction find patterns in unlabeled data.
            Reinforcement learning teaches agents to make decisions through trial and error.
            ''',
            'metadata': {
                'title': 'Machine Learning Algorithms',
                'category': 'AI/ML',
                'author': 'Dr. James Liu',
                'date': '2024-04-05'
            }
        },
        'web_dev': {
            'content': '''
            Web development encompasses the creation of websites and web applications for the internet.
            Front-end development focuses on user interface using HTML, CSS, and JavaScript.
            Back-end development handles server-side logic, databases, and APIs using languages
            like Python, Java, or Node.js. Full-stack developers work on both front-end and back-end.
            Modern frameworks like React, Vue, Django, and Flask simplify the development process.
            ''',
            'metadata': {
                'title': 'Modern Web Development',
                'category': 'Web',
                'author': 'Alex Thompson',
                'date': '2024-05-12'
            }
        },
        'databases': {
            'content': '''
            Databases are organized collections of structured information or data stored electronically.
            Relational databases like MySQL and PostgreSQL use tables and SQL for data management.
            NoSQL databases such as MongoDB and Redis offer flexible schema designs for unstructured data.
            Database design involves normalization, indexing, and query optimization for efficient
            data retrieval and storage. Cloud databases provide scalability and managed services.
            ''',
            'metadata': {
                'title': 'Database Systems',
                'category': 'Data',
                'author': 'Rachel Kim',
                'date': '2024-06-08'
            }
        },
        'cloud_computing': {
            'content': '''
            Cloud computing delivers computing services over the internet, including servers, storage,
            databases, networking, and software. Major cloud providers include AWS, Microsoft Azure,
            and Google Cloud Platform. Cloud services offer scalability, flexibility, and cost-efficiency.
            Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service
            (SaaS) are the main service models. Cloud computing enables businesses to scale rapidly.
            ''',
            'metadata': {
                'title': 'Cloud Computing Essentials',
                'category': 'Infrastructure',
                'author': 'David Brown',
                'date': '2024-07-15'
            }
        }
    }
    
    return documents


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def display_results(engine, results, query):
    """Display search results in a formatted way."""
    if not results:
        print("\n❌ No results found.")
        return
    
    print(f"\n✓ Found {len(results)} result(s):\n")
    
    for i, (doc_id, score, metadata) in enumerate(results, 1):
        print(f"\n{'─' * 80}")
        print(f"Result #{i} - Score: {score:.4f}")
        print(f"{'─' * 80}")
        print(f"Title:    {metadata.get('title', 'Untitled')}")
        print(f"Category: {metadata.get('category', 'N/A')}")
        print(f"Author:   {metadata.get('author', 'N/A')}")
        print(f"Date:     {metadata.get('date', 'N/A')}")
        print(f"\nSnippet:")
        snippet = engine.get_document_snippet(doc_id, query, 250)
        print(f"  {snippet}")


def interactive_search(engine):
    """Run interactive search interface."""
    
    print_header("INTERACTIVE DOCUMENT SEARCH")
    
    print("\nCommands:")
    print("  - Type your search query to search")
    print("  - 'stats' - Show search engine statistics")
    print("  - 'help' - Show this help message")
    print("  - 'quit' or 'exit' - Exit the program")
    
    while True:
        print("\n" + "-" * 80)
        query = input("\n🔍 Enter search query: ").strip()
        
        if not query:
            continue
        
        # Handle commands
        if query.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if query.lower() == 'stats':
            stats = engine.get_statistics()
            print("\n📊 Search Engine Statistics:")
            print(f"  Total documents: {stats['total_documents']}")
            print(f"  Unique terms: {stats['total_terms']}")
            print(f"  Average doc length: {stats['average_doc_length']:.2f} tokens")
            continue
        
        if query.lower() == 'help':
            print("\n📖 Help:")
            print("  Search modes:")
            print("    - OR  : Find documents with ANY of the keywords (default)")
            print("    - AND : Find documents with ALL of the keywords")
            print("    - PHRASE : Find exact phrase matches")
            print("\n  Tips:")
            print("    - Use specific keywords for better results")
            print("    - Try different search modes for different needs")
            print("    - Combine related terms for comprehensive results")
            continue
        
        # Get search mode
        print("\nSearch mode: [O]R / [A]ND / [P]HRASE (default: OR)")
        mode_input = input("Select mode: ").strip().upper()
        
        if mode_input == 'A':
            mode = 'AND'
        elif mode_input == 'P':
            mode = 'PHRASE'
        else:
            mode = 'OR'
        
        # Get number of results
        try:
            top_k_input = input("Number of results (default: 5): ").strip()
            top_k = int(top_k_input) if top_k_input else 5
        except ValueError:
            top_k = 5
        
        # Perform search
        print(f"\n⏳ Searching for '{query}' (mode: {mode})...")
        results = engine.search(query, mode=mode, top_k=top_k)
        
        # Display results
        display_results(engine, results, query)


def main():
    """Main function."""
    
    print_header("SMART DOCUMENT SEARCH ENGINE - DEMO")
    
    # Create search engine
    print("\n⚙️  Initializing search engine...")
    engine = DocumentSearchEngine()
    
    # Load sample documents
    print("📚 Loading sample knowledge base...")
    documents = create_sample_knowledge_base()
    
    for doc_id, doc_data in documents.items():
        engine.add_document(doc_id, doc_data['content'], doc_data['metadata'])
    
    print(f"✓ Loaded {len(documents)} documents")
    
    # Show statistics
    stats = engine.get_statistics()
    print(f"✓ Indexed {stats['total_terms']} unique terms")
    
    # Run interactive search
    interactive_search(engine)


if __name__ == '__main__':
    main()