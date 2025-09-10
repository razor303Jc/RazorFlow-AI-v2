import React, { useState, useEffect } from 'react'
import { Activity, Zap, Clock, Server, Wifi } from 'lucide-react'

const PerformanceMonitor = ({ apiBase }) => {
  const [metrics, setMetrics] = useState({
    responseTime: 0,
    apiStatus: 'unknown',
    requestCount: 0,
    errorCount: 0,
    lastUpdate: null
  })
  const [isMonitoring, setIsMonitoring] = useState(false)

  useEffect(() => {
    let interval
    if (isMonitoring) {
      interval = setInterval(checkPerformance, 5000) // Check every 5 seconds
    }
    return () => clearInterval(interval)
  }, [isMonitoring, apiBase])

  const checkPerformance = async () => {
    const startTime = performance.now()
    
    try {
      const response = await fetch(`${apiBase}/health`)
      const endTime = performance.now()
      const responseTime = endTime - startTime

      if (response.ok) {
        setMetrics(prev => ({
          ...prev,
          responseTime: Math.round(responseTime),
          apiStatus: 'healthy',
          requestCount: prev.requestCount + 1,
          lastUpdate: new Date().toLocaleTimeString()
        }))
      } else {
        throw new Error('API response not ok')
      }
    } catch (error) {
      const endTime = performance.now()
      const responseTime = endTime - startTime

      setMetrics(prev => ({
        ...prev,
        responseTime: Math.round(responseTime),
        apiStatus: 'error',
        requestCount: prev.requestCount + 1,
        errorCount: prev.errorCount + 1,
        lastUpdate: new Date().toLocaleTimeString()
      }))
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-400'
      case 'error': return 'text-red-400'
      case 'warning': return 'text-yellow-400'
      default: return 'text-gray-400'
    }
  }

  const getResponseTimeColor = (time) => {
    if (time < 100) return 'text-green-400'
    if (time < 500) return 'text-yellow-400'
    return 'text-red-400'
  }

  const performLoadTest = async () => {
    setIsMonitoring(true)
    const requests = []
    const startTime = performance.now()

    // Perform 10 concurrent requests
    for (let i = 0; i < 10; i++) {
      requests.push(
        fetch(`${apiBase}/api/finance`).then(response => ({
          success: response.ok,
          time: performance.now() - startTime
        })).catch(() => ({
          success: false,
          time: performance.now() - startTime
        }))
      )
    }

    try {
      const results = await Promise.all(requests)
      const successCount = results.filter(r => r.success).length
      const avgTime = results.reduce((sum, r) => sum + r.time, 0) / results.length

      setMetrics(prev => ({
        ...prev,
        responseTime: Math.round(avgTime),
        apiStatus: successCount === 10 ? 'healthy' : successCount > 5 ? 'warning' : 'error',
        requestCount: prev.requestCount + 10,
        errorCount: prev.errorCount + (10 - successCount),
        lastUpdate: new Date().toLocaleTimeString()
      }))
    } catch (error) {
      console.error('Load test failed:', error)
    }

    setTimeout(() => setIsMonitoring(false), 2000)
  }

  return (
    <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold flex items-center">
          <Activity className="h-5 w-5 mr-2 text-blue-400" />
          Performance Monitor
        </h3>
        <div className="flex space-x-2">
          <button
            onClick={() => setIsMonitoring(!isMonitoring)}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              isMonitoring 
                ? 'bg-red-600 hover:bg-red-700 text-white' 
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {isMonitoring ? 'Stop' : 'Start'} Monitor
          </button>
          <button
            onClick={performLoadTest}
            disabled={isMonitoring}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded text-sm transition-colors"
          >
            Load Test
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* API Status */}
        <div className="bg-slate-700/50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">API Status</p>
              <p className={`text-lg font-bold ${getStatusColor(metrics.apiStatus)}`}>
                {metrics.apiStatus.charAt(0).toUpperCase() + metrics.apiStatus.slice(1)}
              </p>
            </div>
            <Server className={`h-6 w-6 ${getStatusColor(metrics.apiStatus)}`} />
          </div>
        </div>

        {/* Response Time */}
        <div className="bg-slate-700/50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Response Time</p>
              <p className={`text-lg font-bold ${getResponseTimeColor(metrics.responseTime)}`}>
                {metrics.responseTime}ms
              </p>
            </div>
            <Clock className={`h-6 w-6 ${getResponseTimeColor(metrics.responseTime)}`} />
          </div>
        </div>

        {/* Request Count */}
        <div className="bg-slate-700/50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Requests</p>
              <p className="text-lg font-bold text-blue-400">
                {metrics.requestCount}
              </p>
            </div>
            <Wifi className="h-6 w-6 text-blue-400" />
          </div>
        </div>

        {/* Error Count */}
        <div className="bg-slate-700/50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Errors</p>
              <p className="text-lg font-bold text-red-400">
                {metrics.errorCount}
              </p>
            </div>
            <Zap className="h-6 w-6 text-red-400" />
          </div>
        </div>

        {/* Success Rate */}
        <div className="bg-slate-700/50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Success Rate</p>
              <p className="text-lg font-bold text-green-400">
                {metrics.requestCount > 0 
                  ? Math.round(((metrics.requestCount - metrics.errorCount) / metrics.requestCount) * 100)
                  : 0
                }%
              </p>
            </div>
            <Activity className="h-6 w-6 text-green-400" />
          </div>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="mt-6 flex items-center justify-between text-sm">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              isMonitoring ? 'bg-green-400 animate-pulse' : 'bg-gray-400'
            }`}></div>
            <span className="text-slate-400">
              {isMonitoring ? 'Monitoring Active' : 'Monitoring Stopped'}
            </span>
          </div>
          {metrics.lastUpdate && (
            <span className="text-slate-500">
              Last Update: {metrics.lastUpdate}
            </span>
          )}
        </div>
        
        <div className="text-slate-400">
          Endpoint: <span className="text-blue-400">{apiBase}</span>
        </div>
      </div>
    </div>
  )
}

export default PerformanceMonitor
