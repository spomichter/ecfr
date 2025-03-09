#!/usr/bin/env python3
"""
Script to create a vector database for RAG capabilities.
This script processes the collected eCFR data and creates embeddings for semantic search.
"""

import os
import json
import logging
import re
import pandas as pd
import numpy as np
from datetime import datetime
import nltk
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
import pickle
from sentence_transformers import SentenceTransformer
import faiss
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
INPUT_DIR = "../data/hybrid"
OUTPUT_DIR = "../data/vector_db"
CHUNK_SIZE = 512  # Maximum number of characters per chunk
CHUNK_OVERLAP = 128  # Overlap between chunks
MODEL_NAME = "all-MiniLM-L6-v2"  # Sentence transformer model for embeddings

def ensure_directory_exists(directory):
    """Ensure the output directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def download_nltk_resources():
    """Download required NLTK resources."""
    try:
        nltk.download('punkt')
        logger.info("Successfully downloaded NLTK resources")
    except Exception as e:
        logger.error(f"Error downloading NLTK resources: {e}")

def load_data():
    """Load the collected data."""
    data = {
        "agencies": None,
        "titles": None,
        "content": None
    }
    
    # Load agencies data
    agencies_file = os.path.join(INPUT_DIR, "agencies", "latest.json")
    if os.path.exists(agencies_file):
        with open(agencies_file, 'r') as f:
            data["agencies"] = json.load(f)
        logger.info(f"Loaded agencies data from {agencies_file}")
    else:
        logger.warning(f"Agencies data file not found: {agencies_file}")
    
    # Load titles data
    titles_file = os.path.join(INPUT_DIR, "titles", "latest.json")
    if os.path.exists(titles_file):
        with open(titles_file, 'r') as f:
            data["titles"] = json.load(f)
        logger.info(f"Loaded titles data from {titles_file}")
    else:
        logger.warning(f"Titles data file not found: {titles_file}")
    
    # Load content data
    collection_files = [f for f in os.listdir(INPUT_DIR) if f.startswith("collection_summary_")]
    if collection_files:
        # Get the most recent collection summary
        latest_collection = sorted(collection_files)[-1]
        collection_file = os.path.join(INPUT_DIR, latest_collection)
        with open(collection_file, 'r') as f:
            data["content"] = json.load(f)
        logger.info(f"Loaded content data from {collection_file}")
    else:
        logger.warning("No collection summary files found")
    
    return data

def extract_text_from_content(content_data):
    """Extract text from content data for embedding."""
    if not content_data:
        logger.warning("No content data to extract text from")
        return []
    
    results = content_data.get("results", {})
    
    # Initialize list to store text chunks with metadata
    text_chunks = []
    
    # Process each title
    for title_num, title_data in results.items():
        title_name = title_data.get("name", "")
        parts_data = title_data.get("parts", {})
        
        # Process each part
        for part_num, part_data in parts_data.items():
            # Check if we have sections data
            sections_file = part_data.get("sections_file")
            if sections_file and os.path.exists(sections_file):
                with open(sections_file, 'r') as f:
                    sections = json.load(f)
                
                # Process each section
                for section in sections:
                    section_num = section.get("section", "")
                    section_title = section.get("title", "")
                    content = section.get("content", "")
                    
                    if content:
                        # Split content into sentences
                        sentences = sent_tokenize(content)
                        
                        # Create chunks of sentences
                        current_chunk = ""
                        for sentence in sentences:
                            # If adding this sentence would exceed chunk size, save current chunk and start a new one
                            if len(current_chunk) + len(sentence) > CHUNK_SIZE:
                                if current_chunk:
                                    text_chunks.append({
                                        "title_num": title_num,
                                        "title_name": title_name,
                                        "part_num": part_num,
                                        "section_num": section_num,
                                        "section_title": section_title,
                                        "text": current_chunk.strip(),
                                        "source": f"Title {title_num}, Part {part_num}, Section {section_num}"
                                    })
                                
                                # Start a new chunk with overlap
                                words = current_chunk.split()
                                overlap_words = words[-min(len(words), CHUNK_OVERLAP // 10):]  # Approximate overlap by words
                                current_chunk = " ".join(overlap_words) + " " + sentence
                            else:
                                current_chunk += " " + sentence
                        
                        # Add the last chunk if it's not empty
                        if current_chunk.strip():
                            text_chunks.append({
                                "title_num": title_num,
                                "title_name": title_name,
                                "part_num": part_num,
                                "section_num": section_num,
                                "section_title": section_title,
                                "text": current_chunk.strip(),
                                "source": f"Title {title_num}, Part {part_num}, Section {section_num}"
                            })
    
    logger.info(f"Extracted {len(text_chunks)} text chunks from content data")
    return text_chunks

def create_embeddings(text_chunks):
    """Create embeddings for text chunks using sentence transformers."""
    if not text_chunks:
        logger.warning("No text chunks to create embeddings for")
        return None
    
    # Load the model
    logger.info(f"Loading sentence transformer model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    
    # Extract texts for embedding
    texts = [chunk["text"] for chunk in text_chunks]
    
    # Create embeddings
    logger.info(f"Creating embeddings for {len(texts)} text chunks")
    embeddings = model.encode(texts, show_progress_bar=True)
    
    logger.info(f"Created embeddings with shape: {embeddings.shape}")
    return embeddings

def create_faiss_index(embeddings):
    """Create a FAISS index for fast similarity search."""
    if embeddings is None:
        logger.warning("No embeddings to create FAISS index for")
        return None
    
    # Get the dimensionality of the embeddings
    d = embeddings.shape[1]
    
    # Create the index
    logger.info(f"Creating FAISS index with dimension {d}")
    index = faiss.IndexFlatL2(d)  # L2 distance (Euclidean)
    
    # Add the embeddings to the index
    index.add(embeddings)
    
    logger.info(f"Added {index.ntotal} vectors to FAISS index")
    return index

def create_vector_database():
    """Create a vector database for RAG capabilities."""
    # Ensure output directory exists
    ensure_directory_exists(OUTPUT_DIR)
    
    # Download NLTK resources
    download_nltk_resources()
    
    # Load data
    data = load_data()
    
    # Extract text chunks from content
    text_chunks = extract_text_from_content(data["content"])
    
    if not text_chunks:
        logger.error("No text chunks extracted. Cannot create vector database.")
        return
    
    # Create embeddings
    embeddings = create_embeddings(text_chunks)
    
    if embeddings is None:
        logger.error("Failed to create embeddings. Cannot create vector database.")
        return
    
    # Create FAISS index
    index = create_faiss_index(embeddings)
    
    if index is None:
        logger.error("Failed to create FAISS index. Cannot create vector database.")
        return
    
    # Save the vector database components
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save text chunks
    chunks_file = os.path.join(OUTPUT_DIR, f"text_chunks_{timestamp}.pkl")
    with open(chunks_file, 'wb') as f:
        pickle.dump(text_chunks, f)
    logger.info(f"Saved text chunks to: {chunks_file}")
    
    # Save embeddings
    embeddings_file = os.path.join(OUTPUT_DIR, f"embeddings_{timestamp}.npy")
    np.save(embeddings_file, embeddings)
    logger.info(f"Saved embeddings to: {embeddings_file}")
    
    # Save FAISS index
    index_file = os.path.join(OUTPUT_DIR, f"faiss_index_{timestamp}.bin")
    faiss.write_index(index, index_file)
    logger.info(f"Saved FAISS index to: {index_file}")
    
    # Save latest files for easy access
    latest_chunks_file = os.path.join(OUTPUT_DIR, "latest_text_chunks.pkl")
    with open(latest_chunks_file, 'wb') as f:
        pickle.dump(text_chunks, f)
    
    latest_embeddings_file = os.path.join(OUTPUT_DIR, "latest_embeddings.npy")
    np.save(latest_embeddings_file, embeddings)
    
    latest_index_file = os.path.join(OUTPUT_DIR, "latest_faiss_index.bin")
    faiss.write_index(index, latest_index_file)
    
    # Create a metadata file
    metadata = {
        "timestamp": timestamp,
        "model_name": MODEL_NAME,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "num_chunks": len(text_chunks),
        "embedding_dim": embeddings.shape[1],
        "files": {
            "text_chunks": chunks_file,
            "embeddings": embeddings_file,
            "faiss_index": index_file,
            "latest_text_chunks": latest_chunks_file,
            "latest_embeddings": latest_embeddings_file,
            "latest_faiss_index": latest_index_file
        }
    }
    
    metadata_file = os.path.join(OUTPUT_DIR, f"vector_db_metadata_{timestamp}.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved vector database metadata to: {metadata_file}")
    
    latest_metadata_file = os.path.join(OUTPUT_DIR, "latest_metadata.json")
    with open(latest_metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Successfully created vector database with {len(text_chunks)} chunks")
    
    return metadata

def test_vector_search(query, top_k=5):
    """Test the vector database with a sample query."""
    # Load the metadata
    metadata_file = os.path.join(OUTPUT_DIR, "latest_metadata.json")
    if not os.path.exists(metadata_file):
        logger.error(f"Metadata file not found: {metadata_file}")
        return
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    # Load the model
    model_name = metadata.get("model_name", MODEL_NAME)
    logger.info(f"Loading sentence transformer model: {model_name}")
    model = SentenceTransformer(model_name)
    
    # Load the text chunks
    chunks_file = metadata["files"]["latest_text_chunks"]
    with open(chunks_file, 'rb') as f:
        text_chunks = pickle.load(f)
    
    # Load the FAISS index
    index_file = metadata["files"]["latest_faiss_index"]
    index = faiss.read_index(index_file)
    
    # Encode the query
    query_embedding = model.encode([query])[0].reshape(1, -1)
    
    # Search the index
    distances, indices = index.search(query_embedding, top_k)
    
    # Get the results
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(text_chunks):
            chunk = text_chunks[idx]
            results.append({
                "score": float(1.0 / (1.0 + distances[0][i])),  # Convert distance to similarity score
                "source": chunk["source"],
                "title_num": chunk["title_num"],
                "title_name": chunk["title_name"],
                "part_num": chunk["part_num"],
                "section_num": chunk["section_num"],
                "section_title": chunk["section_title"],
                "text": chunk["text"]
            })
    
    return results

if __name__ == "__main__":
    # Create the vector database
    metadata = create_vector_database()
    
    # Test the vector database with a sample query
    if metadata:
        logger.info("Testing vector database with a sample query...")
        query = "What are the requirements for incorporation by reference?"
        results = test_vector_search(query)
        
        if results:
            logger.info(f"Top {len(results)} results for query: '{query}'")
            for i, result in enumerate(results):
                logger.info(f"Result {i+1} (Score: {result['score']:.4f}):")
                logger.info(f"Source: {result['source']}")
                logger.info(f"Title: {result['title_name']}")
                logger.info(f"Text snippet: {result['text'][:200]}...")
                logger.info("-" * 80)
