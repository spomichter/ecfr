# eCFR Analyzer

A comprehensive web application for analyzing the Electronic Code of Federal Regulations (eCFR).

## Project Overview

The eCFR Analyzer provides tools to explore, analyze, and visualize federal regulations data from the [Electronic Code of Federal Regulations](https://www.ecfr.gov/). This project leverages the public eCFR API to download and process regulation data, offering insights through interactive visualizations and advanced search capabilities.

## Features

- **Data Analysis**: Word count per agency, historical changes tracking, and custom metrics
- **Interactive Visualizations**: Beautiful, responsive visualizations of regulation data
- **LLM Chat**: Chat with your data using advanced language models
- **Semantic Search**: Find relevant regulations using natural language queries
- **Agency Filtering**: Search and chat on an agency-by-agency basis
- **Latent Space Visualization**: Explore the semantic clustering of regulations with interactive visualizations

## Technology Stack

- **Frontend**: Next.js with Tailwind CSS
- **Data Processing**: Python for data extraction, cleaning, and analysis
- **Vector Database**: For semantic search and RAG capabilities
- **Visualization**: Interactive charts and graphs using modern visualization libraries
- **API Integration**: Direct integration with the eCFR public API

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python 3.8+
- Git

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ecfr-analyzer.git
   cd ecfr-analyzer
   ```

2. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

3. Install Python dependencies:
   ```
   cd ../backend
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   ```

5. Run the development server:
   ```
   # Start backend
   cd backend
   python app.py
   
   # In another terminal, start frontend
   cd frontend
   npm run dev
   ```

## Project Structure

- `/backend`: Python scripts for data processing and analysis
- `/frontend`: Next.js application for the web interface
- `/data`: Storage for processed data and analysis results
- `/docs`: Project documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [eCFR](https://www.ecfr.gov/) for providing the public API
- All contributors to this project
