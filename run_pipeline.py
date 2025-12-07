# Main pipeline - runs crawler, indexer, and query processor in sequence
import argparse
from pathlib import Path

from src.crawler import run_crawler
from src.indexer import build_and_save_index
from src.query_processor import run_queries
from src.utils import ensure_directories


def run_full_pipeline(skip_crawler=False):  # Execute the complete IR pipeline.

    print("Information Retrieval Pipeline") 
    # Ensure all directories exist
    print("\n[STEP 0] Setting up directories...")
    ensure_directories(
        "data/wiki_corpus",
        "data/html_corpus",
        "data/output"
    )
    
    # Step 1: Crawl Wikipedia 
    if not skip_crawler:
        print("[STEP 1] Running Wikipedia Crawler (Demo Corpus)")
        try:
            run_crawler(output_dir="data/wiki_corpus")
            print("\nCrawling completed successfully")
        except Exception as e:
            print(f"\nCrawling failed: {e}")
            print("Continuing with existing corpus")
    else:
        print("\n[STEP 1] Skipping crawler (using existing Wikipedia corpus)")
    # Step 2: Build index for Wikipedia corpus (demo)
    print("[STEP 2] Building Index for Wikipedia Corpus (Demo)")
    try:
        build_and_save_index(
            corpus_dir="data/wiki_corpus",
            output_path="data/output/wikipedia_index.json"
        )
        print("\nWikipedia index built successfully")
    except Exception as e:
        print(f"\nWikipedia indexing failed: {e}")
    # Step 3: Build index for official corpus (graded)
    print("[STEP 3] Building Index for Official Corpus ")
   
    try:
        build_and_save_index(
            corpus_dir="data/html_corpus",
            output_path="data/output/index.json"
        )
        print("\nOfficial index built successfully")
    except Exception as e:
        print(f"\nOfficial indexing failed: {e}")
        raise
    
    # Step 4: Process queries
    
    print("[STEP 4] Processing Queries")
    
    queries_file = Path("queries.csv")
    if not queries_file.exists():
        print(f"\n queries.csv not found at {queries_file.absolute()}")
    else:
        try:
            run_queries(
                index_path="data/output/index.json",
                queries_csv="queries.csv",
                output_csv="data/output/results.csv"
            )
            print("\nQuery processing completed successfully")
        except Exception as e:
            print(f"\nQuery processing failed: {e}")
            raise
    
    # Final summary
  
    print("Pipeline execution complete")
    print("\nGenerated artifacts:")
    print("data/wiki_corpus/              - Crawled Wikipedia pages")
    print("data/output/wikipedia_index.json - Wikipedia TF-IDF index")
    print("data/output/index.json          - Official TF-IDF index")
    print("data/output/results.csv         - Query results")
    print("\nNext steps:")

def run_crawler_only():
    """Run only the crawler component."""
    print("\n[Running Crawler Only]")
    ensure_directories("data/wiki_corpus")
    run_crawler(output_dir="data/wiki_corpus")
    print("\n Crawler completed")


def run_indexer_only(corpus_type="official"):  # Run only the indexer for specified corpus (official or wikipedia)
    print(f"\n[Running Indexer Only - {corpus_type.upper()}]")
    
    if corpus_type == "official":
        build_and_save_index(
            corpus_dir="data/html_corpus",
            output_path="data/output/index.json"
        )
    elif corpus_type == "wikipedia":
        build_and_save_index(
            corpus_dir="data/wiki_corpus",
            output_path="data/output/wikipedia_index.json"
        )
    else:
        raise ValueError("corpus_type must be 'official' or 'wikipedia'")
    
    print("\nIndexer completed")


def run_query_processor_only():  # Run only the query processor component.
    print("\n[Running Query Processor Only]")
    
    run_queries(
        index_path="data/output/index.json",
        queries_csv="queries.csv",
        output_csv="data/output/results.csv"
    )
    print("\nQuery processor completed")


def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="IR System Pipeline Runner")
    
    # Pipeline options
    parser.add_argument("--skip-crawler", action="store_true", 
                       help="Skip crawling (use existing corpus)")
    parser.add_argument("--crawler-only", action="store_true", 
                       help="Only run the crawler")
    parser.add_argument("--indexer-only", action="store_true", 
                       help="Only run the indexer")
    parser.add_argument("--query-only", action="store_true", 
                       help="Only run query processing")
    parser.add_argument("--corpus", choices=["official", "wikipedia"], 
                       default="official",
                       help="Which corpus to index (default: official)")
    
    args = parser.parse_args()
    
    # Run the requested component(s)
    if args.crawler_only:
        run_crawler_only()
    elif args.indexer_only:
        run_indexer_only(args.corpus)
    elif args.query_only:
        run_query_processor_only()
    else:
        run_full_pipeline(skip_crawler=args.skip_crawler)


if __name__ == "__main__":
    main()