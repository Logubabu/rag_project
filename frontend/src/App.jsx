import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import UploadManager from './components/UploadManager';
import { Moon, Sun } from 'lucide-react';

function App() {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkMode(true);
    }
  }, []);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 text-slate-800 dark:text-slate-200 font-sans transition-colors duration-200">
      {/* Navbar */}
      <nav className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-xl">
                  R
                </div>
                <span className="font-semibold text-lg tracking-tight text-slate-900 dark:text-white">
                  RAG System
                </span>
              </div>
            </div>
            <div className="flex items-center">
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                title="Toggle Dark Mode"
              >
                {darkMode ? <Sun size={20} /> : <Moon size={20} />}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 h-[calc(100vh-4rem)]">
        <div className="flex flex-col lg:flex-row gap-6 h-full">
          {/* Sidebar / Upload Manager */}
          <div className="w-full lg:w-1/3 flex flex-col min-h-0 lg:h-full">
            <UploadManager />
          </div>

          {/* Main Chat Area */}
          <div className="w-full lg:w-2/3 flex flex-col min-h-0 lg:h-full">
            <ChatInterface />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
