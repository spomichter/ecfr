import React from 'react';
import Navbar from '../components/Navbar';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar activePage="home" />
      
      <main className="flex-grow">
        {/* Hero Section */}
        <section className="bg-gradient-to-r from-primary to-secondary text-white py-16">
          <div className="container-custom">
            <div className="max-w-3xl">
              <h1 className="text-4xl md:text-5xl font-bold mb-4">
                eCFR Analyzer
              </h1>
              <p className="text-xl mb-8">
                Explore, analyze, and visualize the Electronic Code of Federal Regulations with powerful tools and beautiful visualizations.
              </p>
              <div className="flex flex-wrap gap-4">
                <Link href="/visualizations" className="bg-white text-primary px-6 py-3 rounded-md font-medium hover:bg-gray-100 transition-colors">
                  Explore Visualizations
                </Link>
                <Link href="/search" className="bg-accent text-white px-6 py-3 rounded-md font-medium hover:bg-blue-500 transition-colors">
                  Search Regulations
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 bg-background">
          <div className="container-custom">
            <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {/* Feature 1 */}
              <div className="card">
                <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold mb-2">Data Analysis</h3>
                <p className="text-gray-600">
                  Comprehensive analysis of federal regulations including word count per agency, historical changes, and custom metrics.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="card">
                <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold mb-2">Semantic Search</h3>
                <p className="text-gray-600">
                  Find relevant regulations using natural language queries with advanced semantic search capabilities.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="card">
                <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold mb-2">LLM Chat</h3>
                <p className="text-gray-600">
                  Chat with your data using advanced language models to get insights and answers about federal regulations.
                </p>
              </div>

              {/* Feature 4 */}
              <div className="card">
                <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold mb-2">Visualizations</h3>
                <p className="text-gray-600">
                  Interactive visualizations including agency distribution, regulation clustering, and latent space exploration.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* About Section */}
        <section className="py-16 bg-white">
          <div className="container-custom">
            <div className="max-w-3xl mx-auto">
              <h2 className="text-3xl font-bold mb-6 text-center">About eCFR Analyzer</h2>
              <p className="text-lg mb-6">
                The Electronic Code of Federal Regulations (eCFR) is a continuously updated online version of the Code of Federal Regulations (CFR), which represents the official legal print publication.
              </p>
              <p className="text-lg mb-6">
                Our eCFR Analyzer provides tools to explore, analyze, and visualize this vast repository of federal regulations data, making it more accessible and understandable.
              </p>
              <p className="text-lg">
                Built with modern web technologies, the analyzer offers powerful search capabilities, interactive visualizations, and AI-powered chat to help users navigate and understand federal regulations.
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="container-custom">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <p className="text-lg font-bold">eCFR Analyzer</p>
              <p className="text-sm text-gray-400">© 2025 All rights reserved</p>
            </div>
            <div className="flex space-x-4">
              <Link href="/" className="hover:text-accent">Home</Link>
              <Link href="/visualizations" className="hover:text-accent">Visualizations</Link>
              <Link href="/search" className="hover:text-accent">Search</Link>
              <Link href="/chat" className="hover:text-accent">Chat</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
