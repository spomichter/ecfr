import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Sample data based on our analysis
const allAgencyData = [
  { name: 'Department of Defense', count: 42, category: 'Defense' },
  { name: 'Department of Health', count: 38, category: 'Health' },
  { name: 'Department of Transportation', count: 35, category: 'Transportation' },
  { name: 'Environmental Protection Agency', count: 30, category: 'Environment' },
  { name: 'Department of Agriculture', count: 28, category: 'Agriculture' },
  { name: 'Department of Energy', count: 25, category: 'Energy' },
  { name: 'Department of Labor', count: 22, category: 'Labor' },
  { name: 'Department of Commerce', count: 20, category: 'Commerce' },
  { name: 'Department of Education', count: 18, category: 'Education' },
  { name: 'Department of Justice', count: 17, category: 'Justice' },
  { name: 'Department of Housing', count: 15, category: 'Housing' },
  { name: 'Department of Treasury', count: 14, category: 'Treasury' },
];

const titleData = [
  { name: 'Title 1', parts: 10, sections: 45, agency: 'General Services Administration' },
  { name: 'Title 2', parts: 15, sections: 78, agency: 'Office of Management and Budget' },
  { name: 'Title 3', parts: 8, sections: 32, agency: 'Executive Office of the President' },
  { name: 'Title 4', parts: 12, sections: 56, agency: 'General Services Administration' },
  { name: 'Title 5', parts: 20, sections: 95, agency: 'Office of Personnel Management' },
  { name: 'Title 6', parts: 14, sections: 67, agency: 'Department of Homeland Security' },
  { name: 'Title 7', parts: 25, sections: 120, agency: 'Department of Agriculture' },
  { name: 'Title 8', parts: 18, sections: 85, agency: 'Department of Justice' },
];

const wordCountData = [
  { name: 'Title 1', count: 25000, agency: 'General Services Administration' },
  { name: 'Title 2', count: 45000, agency: 'Office of Management and Budget' },
  { name: 'Title 3', count: 18000, agency: 'Executive Office of the President' },
  { name: 'Title 4', count: 32000, agency: 'General Services Administration' },
  { name: 'Title 5', count: 55000, agency: 'Office of Personnel Management' },
  { name: 'Title 6', count: 38000, agency: 'Department of Homeland Security' },
  { name: 'Title 7', count: 62000, agency: 'Department of Agriculture' },
  { name: 'Title 8', count: 41000, agency: 'Department of Justice' },
];

const complexityData = [
  { name: 'Title 1', avgSentenceLength: 18.5, avgWordLength: 5.2, agency: 'General Services Administration' },
  { name: 'Title 2', avgSentenceLength: 22.3, avgWordLength: 5.8, agency: 'Office of Management and Budget' },
  { name: 'Title 3', avgSentenceLength: 16.7, avgWordLength: 4.9, agency: 'Executive Office of the President' },
  { name: 'Title 4', avgSentenceLength: 19.2, avgWordLength: 5.3, agency: 'General Services Administration' },
  { name: 'Title 5', avgSentenceLength: 24.1, avgWordLength: 6.1, agency: 'Office of Personnel Management' },
  { name: 'Title 6', avgSentenceLength: 20.5, avgWordLength: 5.5, agency: 'Department of Homeland Security' },
  { name: 'Title 7', avgSentenceLength: 23.8, avgWordLength: 5.9, agency: 'Department of Agriculture' },
  { name: 'Title 8', avgSentenceLength: 21.2, avgWordLength: 5.6, agency: 'Department of Justice' },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#8dd1e1'];

// Get unique agencies for filter
const allAgencies = [...new Set([
  ...titleData.map(item => item.agency),
  ...wordCountData.map(item => item.agency),
  ...complexityData.map(item => item.agency),
])];

// Get unique categories for filter
const allCategories = [...new Set(allAgencyData.map(item => item.category))];

export default function Visualizations() {
  const [selectedAgency, setSelectedAgency] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');
  
  // Filter data based on selected agency
  const filteredTitleData = selectedAgency === 'All' 
    ? titleData 
    : titleData.filter(item => item.agency === selectedAgency);
    
  const filteredWordCountData = selectedAgency === 'All' 
    ? wordCountData 
    : wordCountData.filter(item => item.agency === selectedAgency);
    
  const filteredComplexityData = selectedAgency === 'All' 
    ? complexityData 
    : complexityData.filter(item => item.agency === selectedAgency);
    
  // Filter agency data based on selected category
  const filteredAgencyData = selectedCategory === 'All' 
    ? allAgencyData 
    : allAgencyData.filter(item => item.category === selectedCategory);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar activePage="visualizations" />
      
      <main className="flex-grow py-8 bg-background">
        <div className="container-custom">
          <h1 className="text-3xl font-bold mb-8">eCFR Data Visualizations</h1>
          
          {/* Filters */}
          <div className="bg-white p-4 rounded-lg shadow-md mb-8">
            <h2 className="text-xl font-bold mb-4">Filter Visualizations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filter by Agency:
                </label>
                <select 
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
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filter Agency Chart by Category:
                </label>
                <select 
                  className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  <option value="All">All Categories</option>
                  {allCategories.map((category) => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            {/* Agency Distribution Chart */}
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Agency Distribution</h2>
              <p className="text-gray-600 mb-4">
                Number of CFR references by agency
                {selectedCategory !== 'All' && ` (Category: ${selectedCategory})`}
              </p>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={filteredAgencyData}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={100} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#2b6cb0" name="Number of References" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            {/* Title Structure Chart */}
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Title Structure</h2>
              <p className="text-gray-600 mb-4">
                Number of parts and sections by title
                {selectedAgency !== 'All' && ` (Agency: ${selectedAgency})`}
              </p>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={filteredTitleData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="parts" fill="#4299e1" name="Parts" />
                    <Bar dataKey="sections" fill="#1a365d" name="Sections" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            {/* Word Count Chart */}
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Word Count by Title</h2>
              <p className="text-gray-600 mb-4">
                Total word count in each title
                {selectedAgency !== 'All' && ` (Agency: ${selectedAgency})`}
              </p>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={filteredWordCountData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#2b6cb0" name="Word Count" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            {/* Text Complexity Chart */}
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Text Complexity</h2>
              <p className="text-gray-600 mb-4">
                Average sentence and word length by title
                {selectedAgency !== 'All' && ` (Agency: ${selectedAgency})`}
              </p>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={filteredComplexityData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="avgSentenceLength" fill="#4299e1" name="Avg. Sentence Length" />
                    <Bar dataKey="avgWordLength" fill="#1a365d" name="Avg. Word Length" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
          
          {/* Distribution Pie Chart */}
          <div className="card mb-12">
            <h2 className="text-xl font-bold mb-4">Regulation Distribution</h2>
            <p className="text-gray-600 mb-4">
              Distribution of regulations across top titles
              {selectedAgency !== 'All' && ` (Agency: ${selectedAgency})`}
            </p>
            <div className="h-96 flex justify-center">
              <ResponsiveContainer width="100%" height="100%" maxWidth={600}>
                <PieChart>
                  <Pie
                    data={filteredWordCountData}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    outerRadius={150}
                    fill="#8884d8"
                    dataKey="count"
                    nameKey="name"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {filteredWordCountData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value.toLocaleString()} words`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
            <h2 className="text-xl font-bold mb-2 text-primary">Note on Visualizations</h2>
            <p>
              These visualizations are based on sample data to demonstrate the capabilities of the eCFR Analyzer. 
              As we continue to improve our data collection process, these charts will be updated with actual 
              regulation data from the Electronic Code of Federal Regulations.
            </p>
          </div>
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
