import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

// Sample data for search results
const sampleRegulations = [
  {
    id: 1,
    title: "Title 1",
    part: "Part 51",
    section: "51.1",
    agency: "General Services Administration",
    content: "Incorporation by reference provisions provide a means for agencies to include technical standards developed by private sector organizations in their regulations.",
    relevance: 0.95
  },
  {
    id: 2,
    title: "Title 2",
    part: "Part 200",
    section: "200.216",
    agency: "Office of Management and Budget",
    content: "Federal award may not be used for certain telecommunications and video surveillance services or equipment.",
    relevance: 0.89
  },
  {
    id: 3,
    title: "Title 5",
    part: "Part 1320",
    section: "1320.5",
    agency: "Office of Personnel Management",
    content: "General requirements for information collection include minimizing burden, ensuring practical utility, and evaluating the need for information.",
    relevance: 0.82
  },
  {
    id: 4,
    title: "Title 7",
    part: "Part 205",
    section: "205.105",
    agency: "Department of Agriculture",
    content: "Except for operations exempt or excluded in §205.101, each production or handling operation or specified portion of a production or handling operation that produces or handles crops, livestock, livestock products, or other agricultural products that are intended to be sold, labeled, or represented as '100 percent organic,' 'organic,' or 'made with organic (specified ingredients or food group(s))' must be certified according to the provisions of subpart E of this part and must meet all other applicable requirements of this part.",
    relevance: 0.78
  },
  {
    id: 5,
    title: "Title 10",
    part: "Part 50",
    section: "50.46",
    agency: "Department of Energy",
    content: "Each boiling or pressurized light-water nuclear power reactor fueled with uranium oxide pellets within cylindrical zircaloy or ZIRLO cladding must be provided with an emergency core cooling system (ECCS) that must be designed so that its calculated cooling performance following postulated loss-of-coolant accidents conforms to the criteria set forth in paragraph (b) of this section.",
    relevance: 0.75
  },
  {
    id: 6,
    title: "Title 14",
    part: "Part 25",
    section: "25.853",
    agency: "Department of Transportation",
    content: "Compartment interiors in transport category airplanes must meet the test requirements of part I of appendix F of this part, or other approved equivalent methods, regardless of the passenger capacity of the airplane.",
    relevance: 0.72
  },
  {
    id: 7,
    title: "Title 21",
    part: "Part 101",
    section: "101.9",
    agency: "Department of Health",
    content: "Nutrition information relating to food shall be provided for all products intended for human consumption and offered for sale unless an exemption is provided for the product.",
    relevance: 0.68
  },
  {
    id: 8,
    title: "Title 40",
    part: "Part 60",
    section: "60.4",
    agency: "Environmental Protection Agency",
    content: "All requests, reports, applications, submittals, and other communications to the Administrator pursuant to this part shall be submitted in duplicate to the appropriate Regional Office of the U.S. Environmental Protection Agency.",
    relevance: 0.65
  }
];

// Get unique agencies for filter
const allAgencies = [...new Set(sampleRegulations.map(item => item.agency))];

export default function Search() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgency, setSelectedAgency] = useState('All');
  const [searchResults, setSearchResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);

  // Handle search submission
  const handleSearch = (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) return;
    
    // Filter regulations based on search query and selected agency
    let results = sampleRegulations.filter(reg => 
      reg.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      reg.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      reg.part.toLowerCase().includes(searchQuery.toLowerCase()) ||
      reg.section.toLowerCase().includes(searchQuery.toLowerCase())
    );
    
    // Apply agency filter if not "All"
    if (selectedAgency !== 'All') {
      results = results.filter(reg => reg.agency === selectedAgency);
    }
    
    // Sort by relevance
    results.sort((a, b) => b.relevance - a.relevance);
    
    setSearchResults(results);
    setHasSearched(true);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar activePage="search" />
      
      <main className="flex-grow py-8 bg-background">
        <div className="container-custom">
          <h1 className="text-3xl font-bold mb-8">Semantic Search</h1>
          
          {/* Search Form */}
          <div className="bg-white p-6 rounded-lg shadow-md mb-8">
            <form onSubmit={handleSearch} className="space-y-4">
              <div>
                <label htmlFor="search-query" className="block text-sm font-medium text-gray-700 mb-1">
                  Search Federal Regulations:
                </label>
                <div className="flex">
                  <input
                    type="text"
                    id="search-query"
                    className="flex-grow border border-gray-300 rounded-l-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Enter keywords or natural language query..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <button
                    type="submit"
                    className="bg-primary text-white px-4 py-2 rounded-r-md hover:bg-secondary transition-colors"
                  >
                    <MagnifyingGlassIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
              
              <div>
                <label htmlFor="agency-filter" className="block text-sm font-medium text-gray-700 mb-1">
                  Filter by Agency:
                </label>
                <select
                  id="agency-filter"
                  className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary"
                  value={selectedAgency}
                  onChange={(e) => setSelectedAgency(e.target.value)}
                >
                  <option value="All">All Agencies</option>
                  {allAgencies.map((agency) => (
                    <option key={agency} value={agency}>{agency}</option>
                  ))}
                </select>
              </div>
              
              <button
                type="submit"
                className="w-full bg-primary text-white py-2 rounded-md hover:bg-secondary transition-colors"
              >
                Search Regulations
              </button>
            </form>
          </div>
          
          {/* Search Results */}
          {hasSearched && (
            <div className="bg-white rounded-lg shadow-md">
              <div className="border-b border-gray-200 px-6 py-4">
                <h2 className="text-xl font-bold">
                  Search Results {selectedAgency !== 'All' && `(Agency: ${selectedAgency})`}
                </h2>
                <p className="text-gray-600">
                  Found {searchResults.length} results for "{searchQuery}"
                </p>
              </div>
              
              {searchResults.length > 0 ? (
                <ul className="divide-y divide-gray-200">
                  {searchResults.map((result) => (
                    <li key={result.id} className="px-6 py-4 hover:bg-gray-50">
                      <div className="flex justify-between">
                        <h3 className="text-lg font-semibold text-primary">
                          {result.title}, {result.part}, {result.section}
                        </h3>
                        <span className="text-sm text-gray-500">
                          Relevance: {(result.relevance * 100).toFixed(0)}%
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{result.agency}</p>
                      <p className="text-gray-800">{result.content}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="px-6 py-8 text-center">
                  <p className="text-gray-500 mb-4">No results found for your search criteria.</p>
                  <p className="text-gray-600">Try using different keywords or removing filters.</p>
                </div>
              )}
            </div>
          )}
          
          {!hasSearched && (
            <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
              <h2 className="text-xl font-bold mb-2 text-primary">Semantic Search Capabilities</h2>
              <p className="mb-4">
                Our semantic search goes beyond simple keyword matching to understand the meaning and context of your query.
                This allows you to find relevant regulations even when they don't contain the exact words you searched for.
              </p>
              <p>
                Try searching for concepts like "safety requirements", "reporting obligations", or "environmental standards"
                to see how our system can find semantically related content.
              </p>
            </div>
          )}
        </div>
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
              <a href="/" className="hover:text-accent">Home</a>
              <a href="/visualizations" className="hover:text-accent">Visualizations</a>
              <a href="/search" className="hover:text-accent">Search</a>
              <a href="/chat" className="hover:text-accent">Chat</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
