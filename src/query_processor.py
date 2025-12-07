# Query processor - vectorizes queries and ranks documents using cosine similarity

import csv
from pathlib import Path
from typing import List, Tuple, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class QueryProcessor:
   # Query processor - ranks documents by cosine similarity to query vector 
    def __init__(self, document_ids: List[str], vocabulary: List[str], 
                 tfidf_matrix: np.ndarray, vectorizer_params: Dict):
        # Initialize query processor with index data (doc IDs, vocab, TF-IDF matrix)
        self.document_ids = document_ids
        self.vocabulary = vocabulary
        self.tfidf_matrix = tfidf_matrix
        self.vectorizer_params = vectorizer_params
        
        print(f"Query processor initialized")
        print(f"  Ready to search {len(self.document_ids)} documents")
    
    def process_query(self, query_text: str) -> List[Tuple[int, str, float]]:  # Initialize query processor with index data (doc IDs, vocab, TF-IDF matrix)
        # Vectorize query using same vocabulary as index
        query_vectorizer = TfidfVectorizer(
            lowercase=self.vectorizer_params.get("lowercase", True),
            stop_words=self.vectorizer_params.get("stop_words", "english"),
            vocabulary=self.vocabulary,
            norm=self.vectorizer_params.get("norm", "l2")
        )
        
        query_vector = query_vectorizer.fit_transform([query_text]).toarray()
        
        # Compute cosine similarity with all documents
        similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        # Pair documents with their scores
        doc_score_pairs = list(zip(self.document_ids, similarity_scores))
        
        # Sort by score (descending)
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Add rank (1-based indexing)
        ranked_results = [
            (rank + 1, doc_id, score)
            for rank, (doc_id, score) in enumerate(doc_score_pairs)
        ]
        
        return ranked_results
    
    def process_queries_from_csv(self, queries_csv: str, 
                                  output_csv: str = "data/output/results.csv") -> None:  # Process all queries from CSV file and save ranked results to output CSV
        queries = self._load_queries(queries_csv)
        
        print(f"\nProcessing {len(queries)} queries...")
        
        all_results = []
        
        for query in queries:
            query_id = query["query_id"]
            query_text = query["query_text"]
            
            print(f"\n  Query: {query_id}")
            print(f"  Text: \"{query_text}\"")
            
            # Get ranked documents
            ranked_docs = self.process_query(query_text)
            
            # Display top 3 results
            for rank, doc_id, score in ranked_docs[:3]:
                print(f"    {rank}. {doc_id} (score: {score:.4f})")
            
            # Collect all results for this query
            for rank, doc_id, score in ranked_docs:
                all_results.append({
                    "query_id": query_id,
                    "rank": rank,
                    "document_id": doc_id
                })
        
        # Save results to CSV
        self._save_results(all_results, output_csv)
    
    def _load_queries(self, queries_csv: str) -> List[Dict[str, str]]: # Process all queries from CSV file and save ranked results to output CSV
        queries = []
        
        with open(queries_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                queries.append({
                    "query_id": row["query_id"],
                    "query_text": row["query_text"]
                })
        
        return queries
    
    def _save_results(self, results: List[Dict], output_csv: str) -> None:
        # Save query results to CSV with query_id, rank, and document_id columns
        output_path = Path(output_csv)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, 
                fieldnames=["query_id", "rank", "document_id"]
            )
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\nResults saved: {output_path}")
        print(f"Total rows: {len(results)}")


def run_queries(index_path: str, queries_csv: str, 
                output_csv: str = "data/output/results.csv") -> None:
    # Load index and process queries - convenience wrapper function
    from src.indexer import DocumentIndexer    
    doc_ids, vocab, tfidf_matrix, params = DocumentIndexer.load_index(index_path) # Load index
    
    # Initialize processor and run queries
    processor = QueryProcessor(doc_ids, vocab, tfidf_matrix, params)
    processor.process_queries_from_csv(queries_csv, output_csv)


if __name__ == "__main__":
    print("Processing queries...")
    run_queries(
        index_path="data/output/index.json",
        queries_csv="queries.csv",
        output_csv="data/output/results.csv"
    )