import React, { useState, useEffect } from 'react';
import DataVisualizer from './DataVisualizer';
import MediaAnalyzer from './MediaAnalyzer';
import { MessageCircle, BarChart } from 'lucide-react';

const BeekeepingAnalyzer = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');

  // Socket event listeners
  useEffect(() => {
    window.socket.on('response', (response) => {
      const botMessage = {
        type: 'bot',
        content: response.data,
        timestamp: new Date().toIsoString()
      };
      setMessages(prev => [...prev, botMessage]);
    });

    return () => {
      window.socket.off('response');
    };
  }, []);

  const handleMessageSubmit = (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    // Add user message
    const newMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toIsoString()
    };
    setMessages(prev => [...prev, newMessage]);

    // Send to server
    window.socket.emit('message', {
      user_id: window.userId,
      message: inputMessage
    });

    setInputMessage('');
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-4">
      <div className="flex space-x-2 mb-4">
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex items-center px-4 py-2 rounded ${
            activeTab === 'chat' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          <MessageCircle className="mr-2 h-5 w-5" />
          Chat
        </button>
        <button
          onClick={() => setActiveTab('analyze')}
          className={`flex items-center px-4 py-2 rounded ${
            activeTab === 'analyze' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          <BarChart className="mr-2 h-5 w-5" />
          Analyze
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        {activeTab === 'chat' && (
          <div>
            <div className="h-96 overflow-y-auto mb-4 space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-100 ml-auto max-w-[80%]'
                      : 'bg-gray-100 mr-auto max-w-[80%]'
                  }`}
                >
                  {message.content}
                </div>
              ))}
            </div>
            <form onSubmit={handleMessageSubmit} className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                className="flex-1 p-2 border rounded"
                placeholder="Ask about bee productivity..."
              />
              <button
                type="submit"
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Send
              </button>
            </form>
          </div>
        )}

        {activeTab === 'analyze' && (
          <div>
            <MediaAnalyzer />
            <DataVisualizer />
          </div>
        )}
      </div>
    </div>
  );
};

export default BeekeepingAnalyzer;