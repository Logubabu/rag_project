import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, User, Bot, Copy, Trash2, CheckCircle2 } from 'lucide-react';
import { chat } from '../services/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chat(userMessage.content);
      
      const botMessage = {
        role: 'bot',
        content: response.answer,
        citations: response.citations,
      };
      
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'bot',
        content: 'Sorry, I encountered an error while processing your request.',
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-900 rounded-xl shadow-lg overflow-hidden border border-slate-200 dark:border-slate-800">
      {/* Header */}
      <div className="bg-white dark:bg-slate-800 p-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center z-10">
        <div>
          <h2 className="text-lg font-semibold text-slate-800 dark:text-white">RAG Assistant</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">Ask questions about your uploaded documents</p>
        </div>
        <button
          onClick={clearChat}
          className="p-2 text-slate-500 hover:text-red-500 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors"
          title="Clear chat"
        >
          <Trash2 size={18} />
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 space-y-4">
            <Bot size={48} className="opacity-50" />
            <p>Upload some documents and ask a question to get started.</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <Message key={index} message={msg} onCopy={() => copyToClipboard(msg.content)} />
          ))
        )}
        
        {isLoading && (
          <div className="flex items-start max-w-3xl space-x-4 animate-pulse">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center">
              <Bot size={18} className="text-indigo-600 dark:text-indigo-400" />
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-2xl rounded-tl-none p-4 shadow-sm border border-slate-100 dark:border-slate-700">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white dark:bg-slate-800 p-4 border-t border-slate-200 dark:border-slate-700">
        <form onSubmit={handleSubmit} className="flex relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={isLoading}
            className="flex-1 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-white rounded-full py-3 px-5 pr-12 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 dark:disabled:bg-slate-700 text-white rounded-full transition-colors flex items-center justify-center"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};

const Message = ({ message, onCopy }) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    onCopy();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex items-start max-w-4xl ${isUser ? 'ml-auto flex-row-reverse space-x-reverse space-x-4' : 'space-x-4'}`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser 
          ? 'bg-indigo-600 text-white' 
          : 'bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400'
      }`}>
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>
      
      <div className={`relative group flex flex-col max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`p-4 shadow-sm ${
          isUser 
            ? 'bg-indigo-600 text-white rounded-2xl rounded-tr-none' 
            : `bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl rounded-tl-none text-slate-800 dark:text-slate-200 ${message.isError ? 'border-red-300 dark:border-red-800' : ''}`
        }`}>
          {isUser ? (
            <div className="whitespace-pre-wrap">{message.content}</div>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>
        
        {/* Citations */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-2 w-full flex flex-wrap gap-2">
            {message.citations.map((cite, idx) => (
              <div 
                key={idx} 
                className="inline-flex flex-col text-[10px] sm:text-xs bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md p-1.5 cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                title={cite.text}
              >
                <span className="font-semibold text-slate-700 dark:text-slate-300 flex items-center">
                  <span className="w-2 h-2 rounded-full bg-green-500 mr-1"></span>
                  {cite.filename}
                </span>
                <span className="text-slate-500 dark:text-slate-400">
                  Chunk: {cite.chunk_index} | Sim: {cite.similarity_score.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Actions */}
        {!isUser && (
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleCopy}
              className="p-1.5 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-md border border-slate-200 dark:border-slate-600 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
            >
              {copied ? <CheckCircle2 size={14} className="text-green-500" /> : <Copy size={14} />}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
