import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import { ChatBubbleLeftRightIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline';

// Sample data for chat
const sampleAgencies = [
  "All Agencies",
  "Department of Agriculture",
  "Department of Commerce",
  "Department of Defense",
  "Department of Education",
  "Department of Energy",
  "Department of Health",
  "Department of Homeland Security",
  "Department of Housing",
  "Department of Justice",
  "Department of Labor",
  "Department of Transportation",
  "Department of Treasury",
  "Environmental Protection Agency",
  "General Services Administration",
  "Office of Management and Budget",
  "Office of Personnel Management"
];

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'system',
      content: 'Welcome to the eCFR Chat Assistant. I can help you understand federal regulations. Ask me anything about the Code of Federal Regulations!'
    }
  ]);
  const [input, setInput] = useState('');
  const [selectedAgency, setSelectedAgency] = useState('All Agencies');
  const [isLoading, setIsLoading] = useState(false);

  // Handle sending a message
  const handleSendMessage = (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message
    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: input,
      agency: selectedAgency !== 'All Agencies' ? selectedAgency : null
    };
    
    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);
    
    // Simulate AI response
    setTimeout(() => {
      let responseContent = '';
      
      if (input.toLowerCase().includes('safety') || input.toLowerCase().includes('requirements')) {
        responseContent = selectedAgency !== 'All Agencies' 
          ? `${selectedAgency} has several safety requirements in their regulations. For example, they require regular inspections, safety training programs, and compliance with industry standards. Would you like me to provide specific sections from their regulations?`
          : 'Safety requirements vary across different agencies. Some common themes include regular inspections, training programs, and compliance with industry standards. Would you like me to focus on a specific agency?';
      } else if (input.toLowerCase().includes('deadline') || input.toLowerCase().includes('filing')) {
        responseContent = selectedAgency !== 'All Agencies'
          ? `${selectedAgency} typically requires filings on a quarterly basis, with annual comprehensive reports due within 90 days of the fiscal year end. There are also special filing requirements for certain events that must be reported within 30 days.`
          : 'Filing deadlines vary by agency. Most require quarterly and annual filings, with special event reporting as needed. Would you like information about a specific agency?';
      } else if (input.toLowerCase().includes('exempt') || input.toLowerCase().includes('exception')) {
        responseContent = selectedAgency !== 'All Agencies'
          ? `${selectedAgency} provides exemptions for small businesses with fewer than 50 employees and for certain non-profit organizations. There are also exemptions for research activities and educational institutions in some cases.`
          : 'Exemptions vary across agencies, but common exemptions include those for small businesses, non-profits, research activities, and educational institutions. Would you like details for a specific agency?';
      } else {
        responseContent = selectedAgency !== 'All Agencies'
          ? `I found several regulations from ${selectedAgency} that might be relevant to your query. They cover areas such as compliance requirements, reporting standards, and operational guidelines. Would you like me to provide specific sections?`
          : 'I can help you find information across all federal regulations. To provide more specific information, could you either specify an agency or provide more details about what you\'re looking for?';
      }
      
      const aiMessage = {
        id: messages.length + 2,
        role: 'assistant',
        content: responseContent
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar activePage="chat" />
      
      <main className="flex-grow py-8 bg-background">
        <div className="container-custom">
          <h1 className="text-3xl font-bold mb-8">Chat with eCFR</h1>
          
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-md p-4">
                <h2 className="text-lg font-bold mb-4">Filter by Agency</h2>
                <select
                  className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary"
                  value={selectedAgency}
                  onChange={(e) => setSelectedAgency(e.target.value)}
                >
                  {sampleAgencies.map((agency) => (
                    <option key={agency} value={agency}>{agency}</option>
                  ))}
                </select>
                
                <div className="mt-6">
                  <h3 className="font-semibold mb-2">Suggested Questions:</h3>
                  <ul className="space-y-2">
                    <li>
                      <button 
                        className="text-left text-primary hover:text-secondary w-full"
                        onClick={() => {
                          setInput("What are the safety requirements?");
                          document.getElementById("chat-input").focus();
                        }}
                      >
                        What are the safety requirements?
                      </button>
                    </li>
                    <li>
                      <button 
                        className="text-left text-primary hover:text-secondary w-full"
                        onClick={() => {
                          setInput("When are filing deadlines?");
                          document.getElementById("chat-input").focus();
                        }}
                      >
                        When are filing deadlines?
                      </button>
                    </li>
                    <li>
                      <button 
                        className="text-left text-primary hover:text-secondary w-full"
                        onClick={() => {
                          setInput("Are there any exemptions for small businesses?");
                          document.getElementById("chat-input").focus();
                        }}
                      >
                        Are there any exemptions for small businesses?
                      </button>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            
            {/* Chat Area */}
            <div className="lg:col-span-3">
              <div className="bg-white rounded-lg shadow-md flex flex-col h-[600px]">
                {/* Chat Messages */}
                <div className="flex-grow overflow-y-auto p-4">
                  {messages.map((message) => (
                    <div 
                      key={message.id} 
                      className={`mb-4 ${
                        message.role === 'user' ? 'flex justify-end' : 'flex justify-start'
                      }`}
                    >
                      <div 
                        className={`max-w-[80%] rounded-lg p-3 ${
                          message.role === 'user' 
                            ? 'bg-primary text-white' 
                            : message.role === 'system'
                              ? 'bg-gray-100 text-gray-800 border border-gray-200'
                              : 'bg-accent text-white'
                        }`}
                      >
                        {message.content}
                        {message.agency && (
                          <div className="text-xs mt-1 opacity-80">
                            Filtered by: {message.agency}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {isLoading && (
                    <div className="flex justify-start mb-4">
                      <div className="bg-accent text-white rounded-lg p-3 max-w-[80%]">
                        <div className="flex space-x-2">
                          <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Input Area */}
                <div className="border-t border-gray-200 p-4">
                  <form onSubmit={handleSendMessage} className="flex space-x-2">
                    <input
                      id="chat-input"
                      type="text"
                      className="flex-grow border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="Type your message..."
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      disabled={isLoading}
                    />
                    <button
                      type="submit"
                      className="bg-primary text-white p-2 rounded-md hover:bg-secondary transition-colors disabled:bg-gray-400"
                      disabled={isLoading || !input.trim()}
                    >
                      <PaperAirplaneIcon className="h-5 w-5" />
                    </button>
                  </form>
                  
                  {selectedAgency !== 'All Agencies' && (
                    <div className="mt-2 text-sm text-gray-500">
                      Chatting about regulations from: {selectedAgency}
                    </div>
                  )}
                </div>
              </div>
              
              <div className="mt-6 bg-blue-50 rounded-lg p-4 border border-blue-200">
                <h2 className="text-lg font-bold mb-2 text-primary flex items-center">
                  <ChatBubbleLeftRightIcon className="h-5 w-5 mr-2" />
                  About eCFR Chat
                </h2>
                <p className="text-gray-700">
                  This chat interface demonstrates how users can interact with federal regulations using natural language. 
                  The current implementation uses simulated responses, but the final version will connect to a 
                  language model with access to the complete eCFR database, allowing for accurate and detailed responses 
                  about specific regulations.
                </p>
              </div>
            </div>
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
