import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User } from 'lucide-react'

const Chat = ({ botType, apiBase }) => {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      content: `Hello! I'm the ${botType.charAt(0).toUpperCase() + botType.slice(1)} AI assistant. How can I help you today?`,
      timestamp: new Date().toLocaleTimeString()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Reset chat when bot changes
    setMessages([
      {
        type: 'bot',
        content: `Hello! I'm the ${botType.charAt(0).toUpperCase() + botType.slice(1)} AI assistant. How can I help you today?`,
        timestamp: new Date().toLocaleTimeString()
      }
    ])
  }, [botType])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch(`${apiBase}/api/chat/${botType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage })
      })

      if (response.ok) {
        const data = await response.json()
        const botMessage = {
          type: 'bot',
          content: data.response,
          timestamp: new Date().toLocaleTimeString(),
          confidence: data.confidence
        }
        setMessages(prev => [...prev, botMessage])
      } else {
        throw new Error('Failed to send message')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        type: 'bot',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toLocaleTimeString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getBotColor = (botType) => {
    switch (botType) {
      case 'finance': return 'text-green-400'
      case 'sales': return 'text-blue-400'
      case 'scheduler': return 'text-purple-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <div data-testid="chat" className="bg-slate-800/50 rounded-lg border border-slate-700 h-96 flex flex-col">
      {/* Chat Header */}
      <div className="p-4 border-b border-slate-700">
        <div className="flex items-center space-x-2">
          <Bot className={`h-5 w-5 ${getBotColor(botType)}`} />
          <h3 className="font-semibold">
            {botType.charAt(0).toUpperCase() + botType.slice(1)} AI Chat
          </h3>
          <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">
            Online
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start space-x-2 max-w-[80%] ${
              message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                message.type === 'user' 
                  ? 'bg-blue-500' 
                  : message.isError 
                    ? 'bg-red-500' 
                    : 'bg-slate-600'
              }`}>
                {message.type === 'user' ? (
                  <User className="h-4 w-4 text-white" />
                ) : (
                  <Bot className="h-4 w-4 text-white" />
                )}
              </div>
              <div className={`rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.isError
                    ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                    : 'bg-slate-700 text-slate-200'
              }`}>
                <p className="text-sm">{message.content}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs opacity-60">{message.timestamp}</span>
                  {message.confidence && (
                    <span className="text-xs opacity-60">
                      {Math.round(message.confidence * 100)}% confident
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2 max-w-[80%]">
              <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div className="bg-slate-700 rounded-lg p-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-slate-700">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Ask the ${botType} AI anything...`}
            className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed px-4 py-2 rounded-lg transition-colors"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default Chat
