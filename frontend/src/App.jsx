import React, { useState, useEffect } from 'react'
import { Bot, DollarSign, TrendingUp, Calendar, BarChart3, Users, Clock } from 'lucide-react'
import './App.css'

const API_BASE = 'https://razorflow-ai-production.up.railway.app'

function App() {
  const [activeBot, setActiveBot] = useState('finance')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchBotData(activeBot)
  }, [activeBot])

  const fetchBotData = async (botType) => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/api/${botType}`)
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error('Error fetching data:', error)
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  const bots = [
    { id: 'finance', name: 'Finance Bot', icon: DollarSign, color: 'green' },
    { id: 'sales', name: 'Sales Bot', icon: TrendingUp, color: 'blue' },
    { id: 'scheduler', name: 'Smart Scheduler', icon: Calendar, color: 'purple' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Bot className="h-8 w-8 text-blue-400" />
              <h1 className="text-2xl font-bold">RazorFlow AI</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-slate-400">v2.0.0</span>
              <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                Live
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Bot Selection */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {bots.map((bot) => {
            const Icon = bot.icon
            return (
              <button
                key={bot.id}
                onClick={() => setActiveBot(bot.id)}
                className={`p-6 rounded-xl border transition-all ${
                  activeBot === bot.id
                    ? 'bg-blue-500/20 border-blue-400 shadow-lg shadow-blue-500/25'
                    : 'bg-slate-800/50 border-slate-600 hover:border-slate-500'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`h-8 w-8 text-${bot.color}-400`} />
                  <div className="text-left">
                    <h3 className="font-semibold">{bot.name}</h3>
                    <p className="text-sm text-slate-400">AI Assistant</p>
                  </div>
                </div>
              </button>
            )
          })}
        </div>

        {/* Dashboard */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
          </div>
        ) : data ? (
          <div className="space-y-8">
            {/* Bot Header */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-600">
              <h2 className="text-2xl font-bold mb-2">{data.bot}</h2>
              <p className="text-slate-400">Real-time business insights and automation</p>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {Object.entries(data.data).map(([key, value]) => (
                <div key={key} className="bg-slate-800/50 rounded-xl p-6 border border-slate-600">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-slate-400 text-sm capitalize">{key.replace('_', ' ')}</p>
                      <p className="text-2xl font-bold">{typeof value === 'number' ? value.toLocaleString() : value}</p>
                    </div>
                    <BarChart3 className="h-8 w-8 text-blue-400" />
                  </div>
                </div>
              ))}
            </div>

            {/* Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-600">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2 text-green-400" />
                  Insights
                </h3>
                <ul className="space-y-3">
                  {data.insights.map((insight, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-slate-300">{insight}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-600">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <Users className="h-5 w-5 mr-2 text-blue-400" />
                  Recommendations
                </h3>
                <ul className="space-y-3">
                  {data.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-slate-300">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Call to Action */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 text-center">
              <h3 className="text-2xl font-bold mb-4">Ready to Automate Your Business?</h3>
              <p className="text-blue-100 mb-6">
                Get started with our AI assistants and transform your operations
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button className="px-6 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-blue-50 transition-colors">
                  Start Free Trial
                </button>
                <button className="px-6 py-3 border border-blue-300 text-white font-semibold rounded-lg hover:bg-blue-500/20 transition-colors">
                  Schedule Demo
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-20">
            <p className="text-slate-400">Failed to load data. Please try again.</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-800/50 border-t border-slate-700 mt-20">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center text-slate-400">
            <p>&copy; 2025 RazorFlow AI. Powered by AI for Business Automation.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
