"""Build TF-IDF index for Wikipedia corpus"""
from pathlib import Path
from src.indexer import DocumentIndexer

def build_wikipedia_index():
    """Build TF-IDF index for all Wikipedia pages"""
    
    wiki_corpus = Path('data/wiki_corpus')
    output_file = Path('data/output/wiki_index.json')
    print("Building Wikipedia TF-IDF Index")    
    html_files = list(wiki_corpus.glob('*.html'))   # Count pages
    print(f"\nFound {len(html_files)} Wikipedia pages")
    
    if len(html_files) == 0:
        print("Error: No Wikipedia pages found!")
        print("Run the crawler first to collect pages.")
        return
    
    if len(html_files) < 100:
        print(f"Warning: Only {len(html_files)} pages (expected 100)")
        response = input("Continue anyway? (y/n): ")
        if response.lower() not in ['yes', 'y']:
            return  
    print("\nBuilding TF-IDF index")  # Build index using your DocumentIndexer class
    indexer = DocumentIndexer(
        lowercase=True,
        stop_words='english',
        norm='l2'
    )
    indexer.build_index(corpus_dir='data/wiki_corpus')   # Build index from wiki_corpus directory 
    indexer.save_index(output_path=str(output_file))  # Save to wiki_index.json 
    print(" Wikipedia index complete!")
    print(f"Indexed: {len(indexer.document_ids)} documents")
    print(f"Vocabulary: {len(indexer.vocabulary)} terms")
    print(f"Output: {output_file}")

if __name__ == '__main__':
    build_wikipedia_index()