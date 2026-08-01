import React, { useState } from 'react';
import ChatPage from './pages/ChatPage';
import FilesPage from './pages/FilesPage';
import { MessageSquare, Database } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 font-sans">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <Database className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600">
              Lightweight RAG
            </span>
          </div>
          <nav className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-2 rounded-md flex items-center text-sm font-medium transition-all ${
                activeTab === 'chat'
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-900 hover:bg-gray-200'
              }`}
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              Chat
            </button>
            <button
              onClick={() => setActiveTab('files')}
              className={`px-4 py-2 rounded-md flex items-center text-sm font-medium transition-all ${
                activeTab === 'files'
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-900 hover:bg-gray-200'
              }`}
            >
              <Database className="w-4 h-4 mr-2" />
              Files
            </button>
          </nav>
        </div>
      </header>

      <main className="flex-1 overflow-hidden">
        {activeTab === 'chat' ? <ChatPage /> : <FilesPage />}
      </main>
    </div>
  );
}

export default App;
