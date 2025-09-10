import React from 'react'
import { BarChart3, TrendingUp, Users, Clock, DollarSign, Calendar } from 'lucide-react'

const Dashboard = ({ data, botType }) => {
  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-400">Failed to load data. Please try again.</p>
      </div>
    )
  }

  const renderFinanceDashboard = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Revenue</p>
            <p className="text-2xl font-bold text-green-400">
              ${(data?.data?.revenue || 0).toLocaleString()}
            </p>
          </div>
          <DollarSign className="h-8 w-8 text-green-400" />
        </div>
      </div>
      
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Expenses</p>
            <p className="text-2xl font-bold text-red-400">
              ${(data?.data?.expenses || 0).toLocaleString()}
            </p>
          </div>
          <BarChart3 className="h-8 w-8 text-red-400" />
        </div>
      </div>
      
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Profit</p>
            <p className="text-2xl font-bold text-blue-400">
              ${(data?.data?.profit || 0).toLocaleString()}
            </p>
          </div>
          <TrendingUp className="h-8 w-8 text-blue-400" />
        </div>
      </div>
      
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Growth</p>
            <p className="text-2xl font-bold text-purple-400">
              {data.data.growth}%
            </p>
          </div>
          <TrendingUp className="h-8 w-8 text-purple-400" />
        </div>
      </div>
    </div>
  )

  const renderSalesDashboard = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Leads</p>
            <p className="text-2xl font-bold text-blue-400">
              {data?.data?.leads || 0}
            </p>
          </div>
          <Users className="h-8 w-8 text-blue-400" />
        </div>
      </div>
      
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Conversions</p>
            <p className="text-2xl font-bold text-green-400">
              {data?.data?.conversions || 0}
            </p>
          </div>
          <TrendingUp className="h-8 w-8 text-green-400" />
        </div>
      </div>
      
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Pipeline Value</p>
            <p className="text-2xl font-bold text-purple-400">
              ${(data?.data?.pipeline_value || 0).toLocaleString()}
            </p>
          </div>
          <DollarSign className="h-8 w-8 text-purple-400" />
        </div>
      </div>
      
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Close Rate</p>
            <p className="text-2xl font-bold text-yellow-400">
              {data?.data?.close_rate || 0}%
            </p>
          </div>
          <BarChart3 className="h-8 w-8 text-yellow-400" />
        </div>
      </div>
    </div>
  )

  const renderSchedulerDashboard = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Meetings Today</p>
            <p className="text-2xl font-bold text-blue-400">
              {data.data.meetings_today}
            </p>
          </div>
          <Calendar className="h-8 w-8 text-blue-400" />
        </div>
      </div>
      
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Availability</p>
            <p className="text-2xl font-bold text-green-400">
              {data.data.availability}
            </p>
          </div>
          <Clock className="h-8 w-8 text-green-400" />
        </div>
      </div>
      
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700 md:col-span-2">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Next Meeting</p>
            <p className="text-lg font-bold text-purple-400">
              {data.data.next_meeting}
            </p>
          </div>
          <Calendar className="h-8 w-8 text-purple-400" />
        </div>
      </div>
    </div>
  )

  const renderInsightsAndRecommendations = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Insights */}
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <BarChart3 className="h-5 w-5 mr-2 text-blue-400" />
          AI Insights
        </h3>
        <div className="space-y-3">
          {data.insights.map((insight, index) => (
            <div key={index} className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
              <p className="text-slate-300">{insight}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <TrendingUp className="h-5 w-5 mr-2 text-green-400" />
          Recommendations
        </h3>
        <div className="space-y-3">
          {data.recommendations.map((recommendation, index) => (
            <div key={index} className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
              <p className="text-slate-300">{recommendation}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  return (
    <div data-testid="dashboard" className="space-y-8">
      {/* Dashboard Cards */}
      {botType === 'finance' && renderFinanceDashboard()}
      {botType === 'sales' && renderSalesDashboard()}
      {botType === 'scheduler' && renderSchedulerDashboard()}

      {/* Insights and Recommendations */}
      {renderInsightsAndRecommendations()}
    </div>
  )
}

export default Dashboard
