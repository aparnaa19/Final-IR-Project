# Document indexer - builds TF-IDF vector space model from HTML files
import json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
try:
    from src.utils import read_clean_html, ensure_directories
except ModuleNotFoundError:
    from utils import read_clean_html, ensure_directories

class DocumentIndexer:
    # TF-IDF indexer - converts HTML documents into searchable vector space model
    
    def __init__(self, lowercase=True, stop_words="english", norm="l2"):  # Initialize TF-IDF vectorizer with preprocessing parameters
        self.vectorizer = TfidfVectorizer(
            lowercase=lowercase,
            stop_words=stop_words,
            norm=norm
        )
        self.document_ids = []
        self.tfidf_matrix = None
        self.vocabulary = []
        self.vectorizer_params = {
            "lowercase": lowercase,
            "stop_words": stop_words,
            "norm": norm
        }
    
    def build_index(self, corpus_dir: str, file_pattern="*.html") -> Dict:  # Build TF-IDF index from HTML files and return statistics
        corpus_path = Path(corpus_dir)
        html_files = sorted(corpus_path.glob(file_pattern))
        
        if not html_files:
            raise ValueError(f"No HTML files found in {corpus_dir}")
        
        print(f"\nBuilding index from {len(html_files)} documents")
        docs = {}    # Load and clean documents
        for html_file in html_files:
            doc_id = html_file.stem
            text = read_clean_html(html_file)
            if text:  # Only add non-empty documents
                docs[doc_id] = text
        if not docs:
            raise ValueError("No valid documents found after text extraction")
          
        self.document_ids = list(docs.keys())  # Prepare data for vectorization
        doc_texts = [docs[doc_id] for doc_id in self.document_ids]
        
        self.tfidf_matrix = self.vectorizer.fit_transform(doc_texts)  # Build TF-IDF matrix
        self.vocabulary = self.vectorizer.get_feature_names_out().tolist()
        stats = self._compute_statistics()  # Calculate statistics
        
        print(f"Index built successfully")
        print(f"Documents: {stats['num_documents']}")
        print(f"Vocabulary: {stats['num_terms']} unique terms")
        print(f"Matrix shape: {stats['matrix_shape']}")
        print(f"Sparsity: {stats['sparsity']:.2f}%")
        
        return stats
    
    def save_index(self, output_path: str) -> None:  # Save the TF-IDF index to a JSON file
        if self.tfidf_matrix is None:
            raise RuntimeError("Index not built yet. Call build_index() first.")
        output_file = Path(output_path)
        ensure_directories(output_file.parent) 
        index_data = {
            "document_ids": self.document_ids,
            "vocabulary": self.vocabulary,
            "tfidf_matrix": self.tfidf_matrix.toarray().tolist(),
            "vectorizer_params": self.vectorizer_params
        }
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)
        
        file_size_kb = output_file.stat().st_size / 1024
        print(f"\n Index saved: {output_file}")
        print(f"  Size: {file_size_kb:.2f} KB")
    
    def _compute_statistics(self) -> Dict:  # Calculate and return index statistics (documents, terms, sparsity)
        sparsity = 1 - (
            self.tfidf_matrix.nnz / 
            (self.tfidf_matrix.shape[0] * self.tfidf_matrix.shape[1])
        )
        
        return {
            "num_documents": self.tfidf_matrix.shape[0],
            "num_terms": self.tfidf_matrix.shape[1],
            "matrix_shape": f"{self.tfidf_matrix.shape[0]} x {self.tfidf_matrix.shape[1]}",
            "sparsity": sparsity * 100
        }
    
    @staticmethod
    def load_index(index_path: str) -> Tuple[List[str], List[str], np.ndarray, Dict]:  # Load index from JSON and return document IDs, vocabulary, matrix, and parameters
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        document_ids = data["document_ids"]
        vocabulary = data["vocabulary"]
        tfidf_matrix = np.array(data["tfidf_matrix"])
        params = data["vectorizer_params"]
        
        print(f"Index loaded from {index_path}")
        print(f"Documents: {len(document_ids)}")
        print(f"Vocabulary: {len(vocabulary)} terms")
        
        return document_ids, vocabulary, tfidf_matrix, params


def build_and_save_index(corpus_dir: str, output_path: str) -> None:  # Build and save index in one step - convenience wrapper function
    indexer = DocumentIndexer()
    indexer.build_index(corpus_dir)
    indexer.save_index(output_path)


if __name__ == "__main__":
    print("Building index for official HTML corpus")
    build_and_save_index(
        corpus_dir="data/html_corpus",
        output_path="data/output/index.json"
    )