#Quick test script to verify the IR system works.
import sys
from pathlib import Path

def check_files():  # Check if required files exist
    print("\n[Checking Files]")
    
    # Check HTML files
    html_dir = Path("data/html_corpus")
    html_files = list(html_dir.glob("*.html"))
    print(f"  HTML files: {len(html_files)}/3")
    
    # Check queries
    if Path("queries.csv").exists():
        print("queries.csv found")
    else:
        print("queries.csv missing")
        return False
    
    return len(html_files) == 3


def test_indexer():  
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        
        from src.indexer import DocumentIndexer
        
        indexer = DocumentIndexer()
        stats = indexer.build_index("data/html_corpus")
        indexer.save_index("data/output/index.json")
        
        print(f"Indexed {stats['num_documents']} documents")
        print(f"Vocabulary: {stats['num_terms']} terms")
        return True
        
    except Exception as e:
        print(f"Failed: {e}")
        return False


def test_queries(): # Process queries and generate results
    print("\n Testing Query Processor")
    
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        
        from src.query_processor import run_queries
        
        run_queries(
            index_path="data/output/index.json",
            queries_csv="queries.csv",
            output_csv="data/output/results.csv"
        )
        
        print("Results saved to results.csv")
        return True
        
    except Exception as e:
        print(f"Failed: {e}")
        return False
    
def main():
   
    print("IR System Test")   
    if not check_files():
        print("\nMissing required files")
        return
    
    if test_indexer() and test_queries():
      
        print("All tests passed!")
        print("\nGenerated files:")
        print("data/output/index.json")
        print("data/output/results.csv")
    else:
        print("\nSome tests failed")

if __name__ == "__main__":
    main()