# Flask REST API for the IR system - handles search requests and serves the web interface

import json
import sys
from pathlib import Path
import numpy as np
from flask import Flask, request, jsonify, render_template
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.query_processor import QueryProcessor
from src.indexer import DocumentIndexer
app = Flask(__name__)
query_processor = None  # Global variables to store loaded index


def initialize_index(index_path: str = "data/output/index.json"): # Load the TF-IDF index from JSON file into memory
  
    global query_processor 
    try:  
        doc_ids, vocab, tfidf_matrix, params = DocumentIndexer.load_index(index_path) # Load index components
        query_processor = QueryProcessor(doc_ids, vocab, tfidf_matrix, params)   # Initialize query processor   
        print(f"\nAPI initialized with index from {index_path}")       
    except Exception as e:
        print(f"\nFailed to load index: {e}")
        raise


@app.route("/")
def home():  # Serve the main web interface page
    return render_template("index.html")


@app.route("/search", methods=["POST"])  # Search endpoint - accepts query and top_k, returns ranked documents with scores
def search():
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json"
            }), 400
        
        body = request.get_json(silent=True)
        
        if not body:
            return jsonify({
                "error": "Missing JSON payload"
            }), 400
        
        # Extract query
        query_text = body.get("query")
        
        if not query_text:
            return jsonify({
                "error": "Field 'query' is required"
            }), 400
        
        if not isinstance(query_text, str) or not query_text.strip():
            return jsonify({
                "error": "Field 'query' must be a non-empty string"
            }), 400
        
        # Extract top_k parameter
        top_k = body.get("top_k", 3)
        
        try:
            top_k = int(top_k)
            if top_k < 1:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                "error": "Field 'top_k' must be a positive integer"
            }), 400
        
        # Check if index is loaded
        if query_processor is None:
            return jsonify({
                "error": "Search index not initialized"
            }), 503
        
        # Process query
        ranked_results = query_processor.process_query(query_text)
        
        # Format results
        output = [
            {
                "rank": rank,
                "document_id": doc_id,
                "score": round(float(score), 6)
            }
            for rank, doc_id, score in ranked_results[:top_k]
        ]
        
        return jsonify({
            "query": query_text,
            "count": len(output),
            "results": output
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route("/health", methods=["GET"]) # Health check - returns API status and number of indexed documents
def health_check():
   
    if query_processor is None:
        return jsonify({
            "status": "unhealthy",
            "message": "Index not loaded",
            "documents_loaded": 0
        }), 503
    
    return jsonify({
        "status": "healthy",
        "message": "API is running",
        "documents_loaded": len(query_processor.document_ids)
    }), 200

@app.route("/api/info", methods=["GET"])
def api_info():
    # Return API documentation
    return jsonify({
        "name": "IR Search API",
        "version": "1.0",
        "endpoints": {
            "/": "Web interface",
            "/health": "Health check",
            "/search": "Search documents (POST)",
            "/api/info": "API info"
        }
    }), 200


def run_api(host="0.0.0.0", port=5000, debug=False, index_path="data/output/index.json"):
   # Start the Flask server with the web interface and load the index   
    print("Information retrieval Search Engine")
    initialize_index(index_path)  # Load index 
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    # Run API server with web interface
    run_api(
        host="0.0.0.0",
        port=5000,
        debug=True,
        index_path="data/output/index.json"
    )