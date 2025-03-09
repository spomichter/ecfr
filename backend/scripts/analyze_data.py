#!/usr/bin/env python3
"""
Script to process and analyze the collected eCFR data.
This script performs various analyses on the data collected by the hybrid_collector.py script.
"""

import os
import json
import logging
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter, defaultdict
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
INPUT_DIR = "../data/hybrid"
OUTPUT_DIR = "../data/analysis"
FIGURES_DIR = "../data/analysis/figures"

def ensure_directory_exists(directory):
    """Ensure the output directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def download_nltk_resources():
    """Download required NLTK resources."""
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
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

def analyze_agencies(agencies_data):
    """Analyze agencies data."""
    if not agencies_data:
        logger.warning("No agencies data to analyze")
        return None
    
    agencies = agencies_data.get("agencies", [])
    
    # Create a DataFrame for agencies
    agencies_df = pd.DataFrame(agencies)
    
    # Add column for number of CFR references
    agencies_df["num_cfr_references"] = agencies_df["cfr_references"].apply(lambda x: len(x) if isinstance(x, list) else 0)
    
    # Count agencies by title
    title_counts = defaultdict(int)
    for agency in agencies:
        for ref in agency.get("cfr_references", []):
            title = ref.get("title")
            if title:
                title_counts[title] += 1
    
    title_counts_df = pd.DataFrame({
        "title": list(title_counts.keys()),
        "agency_count": list(title_counts.values())
    }).sort_values("title")
    
    # Save the analysis results
    results = {
        "total_agencies": len(agencies),
        "agencies_by_title": dict(title_counts),
        "agencies_with_most_references": agencies_df.sort_values("num_cfr_references", ascending=False)[["name", "num_cfr_references"]].head(10).to_dict("records")
    }
    
    # Create visualizations
    ensure_directory_exists(FIGURES_DIR)
    
    # Plot agencies by title
    plt.figure(figsize=(12, 8))
    sns.barplot(data=title_counts_df, x="title", y="agency_count")
    plt.title("Number of Agencies by CFR Title")
    plt.xlabel("CFR Title")
    plt.ylabel("Number of Agencies")
    plt.xticks(rotation=90)
    plt.tight_layout()
    agencies_by_title_plot = os.path.join(FIGURES_DIR, "agencies_by_title.png")
    plt.savefig(agencies_by_title_plot)
    plt.close()
    
    # Plot agencies with most references
    top_agencies = agencies_df.sort_values("num_cfr_references", ascending=False).head(15)
    plt.figure(figsize=(12, 8))
    sns.barplot(data=top_agencies, x="num_cfr_references", y="name")
    plt.title("Agencies with Most CFR References")
    plt.xlabel("Number of CFR References")
    plt.ylabel("Agency Name")
    plt.tight_layout()
    top_agencies_plot = os.path.join(FIGURES_DIR, "top_agencies_by_references.png")
    plt.savefig(top_agencies_plot)
    plt.close()
    
    return {
        "results": results,
        "figures": {
            "agencies_by_title": agencies_by_title_plot,
            "top_agencies_by_references": top_agencies_plot
        }
    }

def analyze_titles(titles_data, content_data=None):
    """Analyze titles data."""
    if not titles_data:
        logger.warning("No titles data to analyze")
        return None
    
    titles = titles_data.get("titles", [])
    
    # Create a DataFrame for titles
    titles_df = pd.DataFrame(titles)
    
    # The titles data doesn't have a 'parts' field, so we'll use the content data to get part counts
    # Initialize with 0 parts for all titles
    titles_df["num_parts"] = 0
    
    # If we have content data, update the part counts
    if content_data and content_data.get("results", {}):
        results = content_data.get("results", {})
        for title_num, title_data in results.items():
            structure = title_data.get("structure", {})
            chapters = structure.get("chapters", [])
            # Count parts in each chapter
            part_count = sum(len(chapter.get("parts", [])) for chapter in chapters)
            # Update the DataFrame if this title exists
            title_idx = titles_df.index[titles_df["number"] == title_num].tolist()
            if title_idx:
                titles_df.at[title_idx[0], "num_parts"] = part_count
    
    # Save the analysis results
    results = {
        "total_titles": len(titles),
        "titles_with_most_parts": titles_df.sort_values("num_parts", ascending=False)[["number", "name", "num_parts"]].head(10).to_dict("records")
    }
    
    # Create visualizations
    ensure_directory_exists(FIGURES_DIR)
    
    # Plot titles by number of parts
    plt.figure(figsize=(12, 8))
    sns.barplot(data=titles_df.sort_values("num_parts", ascending=False).head(15), x="number", y="num_parts")
    plt.title("Number of Parts by CFR Title")
    plt.xlabel("CFR Title")
    plt.ylabel("Number of Parts")
    plt.xticks(rotation=90)
    plt.tight_layout()
    titles_by_parts_plot = os.path.join(FIGURES_DIR, "titles_by_parts.png")
    plt.savefig(titles_by_parts_plot)
    plt.close()
    
    return {
        "results": results,
        "figures": {
            "titles_by_parts": titles_by_parts_plot
        }
    }

def analyze_content(content_data):
    """Analyze content data."""
    if not content_data:
        logger.warning("No content data to analyze")
        return None
    
    results = content_data.get("results", {})
    
    # Collect statistics on titles and parts
    title_stats = []
    for title_num, title_data in results.items():
        structure = title_data.get("structure", {})
        chapters = structure.get("chapters", [])
        parts_data = title_data.get("parts", {})
        
        # Count parts and sections
        total_parts = sum(len(chapter.get("parts", [])) for chapter in chapters)
        total_sections = sum(len(part_data.get("sections", [])) for part_data in parts_data.values())
        
        title_stats.append({
            "title": title_num,
            "name": title_data.get("name", ""),
            "chapters": len(chapters),
            "parts": total_parts,
            "sections": total_sections
        })
    
    # Create a DataFrame for title statistics
    title_stats_df = pd.DataFrame(title_stats)
    
    # Save the analysis results
    analysis_results = {
        "total_titles_analyzed": len(title_stats),
        "title_statistics": title_stats
    }
    
    # Create visualizations if we have enough data
    if len(title_stats) > 0:
        ensure_directory_exists(FIGURES_DIR)
        
        # Plot chapters, parts, and sections by title
        title_stats_df_melted = pd.melt(
            title_stats_df, 
            id_vars=["title", "name"], 
            value_vars=["chapters", "parts", "sections"],
            var_name="category",
            value_name="count"
        )
        
        plt.figure(figsize=(12, 8))
        sns.barplot(data=title_stats_df_melted, x="title", y="count", hue="category")
        plt.title("Chapters, Parts, and Sections by CFR Title")
        plt.xlabel("CFR Title")
        plt.ylabel("Count")
        plt.xticks(rotation=90)
        plt.legend(title="Category")
        plt.tight_layout()
        content_stats_plot = os.path.join(FIGURES_DIR, "content_stats_by_title.png")
        plt.savefig(content_stats_plot)
        plt.close()
        
        return {
            "results": analysis_results,
            "figures": {
                "content_stats_by_title": content_stats_plot
            }
        }
    
    return {
        "results": analysis_results,
        "figures": {}
    }

def calculate_word_counts(content_data):
    """Calculate word counts for titles and parts."""
    if not content_data:
        logger.warning("No content data to analyze for word counts")
        return None
    
    results = content_data.get("results", {})
    
    # Initialize word count data
    word_counts = {
        "by_title": {},
        "by_part": {}
    }
    
    # Process each title
    for title_num, title_data in results.items():
        title_name = title_data.get("name", "")
        parts_data = title_data.get("parts", {})
        
        title_word_count = 0
        part_word_counts = {}
        
        # Process each part
        for part_num, part_data in parts_data.items():
            # Check if we have sections data
            sections_file = part_data.get("sections_file")
            if sections_file and os.path.exists(sections_file):
                with open(sections_file, 'r') as f:
                    sections = json.load(f)
                
                # Count words in each section
                part_word_count = 0
                for section in sections:
                    content = section.get("content", "")
                    words = word_tokenize(content)
                    part_word_count += len(words)
                
                part_word_counts[part_num] = part_word_count
                title_word_count += part_word_count
        
        word_counts["by_title"][title_num] = {
            "name": title_name,
            "word_count": title_word_count
        }
        
        word_counts["by_part"][title_num] = part_word_counts
    
    # Create visualizations if we have enough data
    if word_counts["by_title"]:
        ensure_directory_exists(FIGURES_DIR)
        
        # Create DataFrame for title word counts
        title_word_counts_df = pd.DataFrame([
            {
                "title": title_num,
                "name": data["name"],
                "word_count": data["word_count"]
            }
            for title_num, data in word_counts["by_title"].items()
        ])
        
        if not title_word_counts_df.empty:
            # Plot word counts by title
            plt.figure(figsize=(12, 8))
            sns.barplot(data=title_word_counts_df, x="title", y="word_count")
            plt.title("Word Count by CFR Title")
            plt.xlabel("CFR Title")
            plt.ylabel("Word Count")
            plt.xticks(rotation=90)
            plt.tight_layout()
            word_counts_plot = os.path.join(FIGURES_DIR, "word_counts_by_title.png")
            plt.savefig(word_counts_plot)
            plt.close()
            
            return {
                "results": word_counts,
                "figures": {
                    "word_counts_by_title": word_counts_plot
                }
            }
    
    return {
        "results": word_counts,
        "figures": {}
    }

def analyze_text_complexity(content_data):
    """Analyze text complexity of regulations."""
    if not content_data:
        logger.warning("No content data to analyze for text complexity")
        return None
    
    results = content_data.get("results", {})
    
    # Initialize complexity data
    complexity_data = {
        "by_title": {},
        "by_part": {}
    }
    
    # Process each title
    for title_num, title_data in results.items():
        title_name = title_data.get("name", "")
        parts_data = title_data.get("parts", {})
        
        title_metrics = {
            "avg_sentence_length": 0,
            "avg_word_length": 0,
            "total_sentences": 0,
            "total_words": 0
        }
        
        part_metrics = {}
        
        # Process each part
        for part_num, part_data in parts_data.items():
            # Check if we have sections data
            sections_file = part_data.get("sections_file")
            if sections_file and os.path.exists(sections_file):
                with open(sections_file, 'r') as f:
                    sections = json.load(f)
                
                # Analyze text complexity for each section
                part_sentences = []
                part_words = []
                
                for section in sections:
                    content = section.get("content", "")
                    
                    # Tokenize sentences and words
                    sentences = nltk.sent_tokenize(content)
                    words = [word for sentence in sentences for word in word_tokenize(sentence)]
                    
                    part_sentences.extend(sentences)
                    part_words.extend(words)
                
                # Calculate metrics
                total_sentences = len(part_sentences)
                total_words = len(part_words)
                
                if total_sentences > 0:
                    avg_sentence_length = total_words / total_sentences
                else:
                    avg_sentence_length = 0
                
                if total_words > 0:
                    avg_word_length = sum(len(word) for word in part_words) / total_words
                else:
                    avg_word_length = 0
                
                part_metrics[part_num] = {
                    "avg_sentence_length": avg_sentence_length,
                    "avg_word_length": avg_word_length,
                    "total_sentences": total_sentences,
                    "total_words": total_words
                }
                
                # Update title metrics
                title_metrics["total_sentences"] += total_sentences
                title_metrics["total_words"] += total_words
        
        # Calculate title averages
        if title_metrics["total_sentences"] > 0:
            title_metrics["avg_sentence_length"] = title_metrics["total_words"] / title_metrics["total_sentences"]
        
        if title_metrics["total_words"] > 0:
            # We don't have the individual words at this level, so we calculate a weighted average
            title_metrics["avg_word_length"] = sum(
                metrics["avg_word_length"] * metrics["total_words"] 
                for metrics in part_metrics.values() if metrics["total_words"] > 0
            ) / title_metrics["total_words"]
        
        complexity_data["by_title"][title_num] = {
            "name": title_name,
            **title_metrics
        }
        
        complexity_data["by_part"][title_num] = part_metrics
    
    # Create visualizations if we have enough data
    if complexity_data["by_title"]:
        ensure_directory_exists(FIGURES_DIR)
        
        # Create DataFrame for title complexity
        title_complexity_df = pd.DataFrame([
            {
                "title": title_num,
                "name": data["name"],
                "avg_sentence_length": data["avg_sentence_length"],
                "avg_word_length": data["avg_word_length"],
                "total_sentences": data["total_sentences"],
                "total_words": data["total_words"]
            }
            for title_num, data in complexity_data["by_title"].items()
        ])
        
        if not title_complexity_df.empty:
            # Plot average sentence length by title
            plt.figure(figsize=(12, 8))
            sns.barplot(data=title_complexity_df, x="title", y="avg_sentence_length")
            plt.title("Average Sentence Length by CFR Title")
            plt.xlabel("CFR Title")
            plt.ylabel("Average Sentence Length (words)")
            plt.xticks(rotation=90)
            plt.tight_layout()
            sentence_length_plot = os.path.join(FIGURES_DIR, "avg_sentence_length_by_title.png")
            plt.savefig(sentence_length_plot)
            plt.close()
            
            # Plot average word length by title
            plt.figure(figsize=(12, 8))
            sns.barplot(data=title_complexity_df, x="title", y="avg_word_length")
            plt.title("Average Word Length by CFR Title")
            plt.xlabel("CFR Title")
            plt.ylabel("Average Word Length (characters)")
            plt.xticks(rotation=90)
            plt.tight_layout()
            word_length_plot = os.path.join(FIGURES_DIR, "avg_word_length_by_title.png")
            plt.savefig(word_length_plot)
            plt.close()
            
            return {
                "results": complexity_data,
                "figures": {
                    "avg_sentence_length_by_title": sentence_length_plot,
                    "avg_word_length_by_title": word_length_plot
                }
            }
    
    return {
        "results": complexity_data,
        "figures": {}
    }

def extract_common_terms(content_data):
    """Extract common terms from regulations."""
    if not content_data:
        logger.warning("No content data to analyze for common terms")
        return None
    
    results = content_data.get("results", {})
    
    # Download NLTK resources
    download_nltk_resources()
    
    # Initialize stop words and lemmatizer
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    
    # Initialize terms data
    terms_data = {
        "by_title": {},
        "overall": Counter()
    }
    
    # Process each title
    for title_num, title_data in results.items():
        title_name = title_data.get("name", "")
        parts_data = title_data.get("parts", {})
        
        title_terms = Counter()
        
        # Process each part
        for part_num, part_data in parts_data.items():
            # Check if we have sections data
            sections_file = part_data.get("sections_file")
            if sections_file and os.path.exists(sections_file):
                with open(sections_file, 'r') as f:
                    sections = json.load(f)
                
                # Extract terms from each section
                for section in sections:
                    content = section.get("content", "")
                    
                    # Tokenize words
                    words = word_tokenize(content.lower())
                    
                    # Remove stop words and lemmatize
                    filtered_words = [
                        lemmatizer.lemmatize(word) 
                        for word in words 
                        if word.isalpha() and word not in stop_words and len(word) > 2
                    ]
                    
                    # Update counters
                    title_terms.update(filtered_words)
                    terms_data["overall"].update(filtered_words)
        
        terms_data["by_title"][title_num] = {
            "name": title_name,
            "common_terms": title_terms.most_common(50)
        }
    
    # Create visualizations if we have enough data
    if terms_data["overall"]:
        ensure_directory_exists(FIGURES_DIR)
        
        # Plot overall most common terms
        plt.figure(figsize=(12, 8))
        common_terms = pd.DataFrame(terms_data["overall"].most_common(30), columns=["term", "count"])
        sns.barplot(data=common_terms, x="count", y="term")
        plt.title("Most Common Terms in CFR")
        plt.xlabel("Count")
        plt.ylabel("Term")
        plt.tight_layout()
        common_terms_plot = os.path.join(FIGURES_DIR, "common_terms_overall.png")
        plt.savefig(common_terms_plot)
        plt.close()
        
        # Create visualizations for each title if we have enough titles
        title_term_plots = {}
        for title_num, title_data in terms_data["by_title"].items():
            if title_data["common_terms"]:
                plt.figure(figsize=(12, 8))
                title_common_terms = pd.DataFrame(title_data["common_terms"][:20], columns=["term", "count"])
                sns.barplot(data=title_common_terms, x="count", y="term")
                plt.title(f"Most Common Terms in Title {title_num}: {title_data['name']}")
                plt.xlabel("Count")
                plt.ylabel("Term")
                plt.tight_layout()
                title_terms_plot = os.path.join(FIGURES_DIR, f"common_terms_title_{title_num}.png")
                plt.savefig(title_terms_plot)
                plt.close()
                
                title_term_plots[title_num] = title_terms_plot
        
        return {
            "results": {
                "overall_common_terms": terms_data["overall"].most_common(100),
                "title_common_terms": {title_num: data["common_terms"] for title_num, data in terms_data["by_title"].items()}
            },
            "figures": {
                "common_terms_overall": common_terms_plot,
                **{f"common_terms_title_{title_num}": plot for title_num, plot in title_term_plots.items()}
            }
        }
    
    return {
        "results": {
            "overall_common_terms": terms_data["overall"].most_common(100),
            "title_common_terms": {title_num: data["common_terms"] for title_num, data in terms_data["by_title"].items()}
        },
        "figures": {}
    }

def run_analysis():
    """Run all analysis functions and save the results."""
    # Ensure output directories exist
    ensure_directory_exists(OUTPUT_DIR)
    ensure_directory_exists(FIGURES_DIR)
    
    # Load data
    data = load_data()
    
    # Run analyses
    analyses = {
        "agencies": analyze_agencies(data["agencies"]),
        "titles": analyze_titles(data["titles"], data["content"]),
        "content": analyze_content(data["content"]),
        "word_counts": calculate_word_counts(data["content"]),
        "text_complexity": analyze_text_complexity(data["content"]),
        "common_terms": extract_common_terms(data["content"])
    }
    
    # Save analysis results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(OUTPUT_DIR, f"analysis_results_{timestamp}.json")
    
    # Extract results and figures
    results = {key: analysis["results"] if analysis else None for key, analysis in analyses.items()}
    figures = {}
    for key, analysis in analyses.items():
        if analysis and "figures" in analysis:
            figures[key] = analysis["figures"]
    
    # Save results
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "results": results,
            "figures": figures
        }, f, indent=2)
    
    logger.info(f"Analysis results saved to: {results_file}")
    
    return {
        "results": results,
        "figures": figures,
        "results_file": results_file
    }

if __name__ == "__main__":
    run_analysis()
