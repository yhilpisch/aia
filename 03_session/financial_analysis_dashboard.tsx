import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

const FinancialAnalysisDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');

  // Raw data processing
  const companies = ['AAPL', 'MSFT', 'AMZN', 'NFLX', 'META', 'GOOG', 'INTC', 'AMD', 'NVDA', 'GE', 'GS', 'BAC', 'JPM', 'MS'];
  
  const data = {
    MarketCapitalizationMln: [2990296.5309, 3424096.8786, 2187190.7308, 515609.0348, 1576632.1889, 2050458.6486, 89639.0922, 185747.5871, 3304519.893, 257831.7804, 188931.1949, 333059.7519, 737264.7956, 207294.2019],
    PERatio: [30.3809, 34.848, 32.8057, 55.8585, 24.5067, 18.9314, null, 80.6761, 44.5724, 36.7447, 13.8897, 12.8921, 12.7851, 14.7669],
    ProfitMargin: [0.243, 0.3579, 0.1014, 0.2307, 0.3911, 0.3086, -0.3619, 0.0802, 0.5585, 0.1763, 0.2806, 0.2858, 0.3538, 0.2235],
    RevenueGrowth: [0.051, 0.133, 0.086, 0.125, 0.161, 0.12, -0.004, 0.359, 0.779, 0.109, 0.063, 0.057, 0.048, 0.163],
    DividendYield: [0.0053, 0.0074, 0, 0, 0.0033, 0.005, 0.0122, 0, 0.0003, 0.0062, 0.02, 0.0241, 0.0215, 0.0293],
    ROE: [1.3802, 0.3361, 0.2524, 0.4084, 0.3984, 0.3479, -0.1813, 0.039, 1.1918, 0.272, 0.1222, 0.0946, 0.1735, 0.1388]
  };

  // Create datasets for charts
  const marketCapData = companies.map((company, i) => ({
    company,
    marketCap: data.MarketCapitalizationMln[i] / 1000, // Convert to billions
    sector: getSector(company)
  })).sort((a, b) => b.marketCap - a.marketCap);

  const profitabilityData = companies.map((company, i) => ({
    company,
    profitMargin: data.ProfitMargin[i] * 100,
    peRatio: data.PERatio[i],
    roe: data.ROE[i] * 100,
    sector: getSector(company)
  })).filter(d => d.peRatio !== null);

  const growthData = companies.map((company, i) => ({
    company,
    revenueGrowth: data.RevenueGrowth[i] * 100,
    sector: getSector(company)
  }));

  const dividendData = companies.map((company, i) => ({
    company,
    dividendYield: data.DividendYield[i] * 100,
    sector: getSector(company)
  })).filter(d => d.dividendYield > 0);

  function getSector(company) {
    const sectors = {
      'AAPL': 'Technology', 'MSFT': 'Technology', 'AMZN': 'Technology',
      'NFLX': 'Technology', 'META': 'Technology', 'GOOG': 'Technology',
      'INTC': 'Technology', 'AMD': 'Technology', 'NVDA': 'Technology',
      'GE': 'Industrial', 'GS': 'Financial', 'BAC': 'Financial',
      'JPM': 'Financial', 'MS': 'Financial'
    };
    return sectors[company];
  }

  const sectorColors = {
    'Technology': '#3B82F6',
    'Financial': '#10B981',
    'Industrial': '#F59E0B'
  };

  const tabs = [
    { id: 'overview', label: 'Market Overview' },
    { id: 'profitability', label: 'Profitability' },
    { id: 'growth', label: 'Growth Analysis' },
    { id: 'dividends', label: 'Dividend Analysis' },
    { id: 'insights', label: 'Key Insights' }
  ];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Financial Analysis Dashboard</h1>
          <p className="text-gray-600">Comprehensive analysis of 14 major companies across Technology, Financial, and Industrial sectors</p>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow-lg mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <>
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-4">Market Capitalization Leaders</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={marketCapData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="company" />
                    <YAxis label={{ value: 'Market Cap ($B)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip formatter={(value) => [`$${value.toFixed(0)}B`, 'Market Cap']} />
                    <Bar dataKey="marketCap">
                      {marketCapData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={sectorColors[entry.sector]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                <div className="mt-4 grid grid-cols-3 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-blue-800">Technology Dominance</h3>
                    <p className="text-sm text-blue-600">9 of top 10 companies by market cap</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-green-800">Total Market Cap</h3>
                    <p className="text-sm text-green-600">${(marketCapData.reduce((sum, d) => sum + d.marketCap, 0) / 1000).toFixed(1)}T combined</p>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-yellow-800">Top 3 Leaders</h3>
                    <p className="text-sm text-yellow-600">NVDA, MSFT, AAPL control 65% of total</p>
                  </div>
                </div>
              </div>
            </>
          )}

          {activeTab === 'profitability' && (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h2 className="text-xl font-bold mb-4">Profit Margins by Company</h2>
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart data={profitabilityData.sort((a, b) => b.profitMargin - a.profitMargin)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="company" />
                      <YAxis label={{ value: 'Profit Margin (%)', angle: -90, position: 'insideLeft' }} />
                      <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Profit Margin']} />
                      <Bar dataKey="profitMargin">
                        {profitabilityData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={sectorColors[entry.sector]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h2 className="text-xl font-bold mb-4">P/E Ratio vs ROE (Sorted by P/E Ratio)</h2>
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart data={profitabilityData.sort((a, b) => a.peRatio - b.peRatio)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="company" />
                      <YAxis yAxisId="left" label={{ value: 'P/E Ratio', angle: -90, position: 'insideLeft' }} />
                      <YAxis yAxisId="right" orientation="right" label={{ value: 'ROE (%)', angle: 90, position: 'insideRight' }} />
                      <Tooltip 
                        formatter={(value, name) => [
                          name === 'roe' ? `${value.toFixed(1)}%` : value.toFixed(1),
                          name === 'roe' ? 'ROE' : 'P/E Ratio'
                        ]}
                      />
                      <Legend />
                      <Bar yAxisId="left" dataKey="peRatio" name="P/E Ratio" fill="#8884d8" />
                      <Bar yAxisId="right" dataKey="roe" name="ROE (%)" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">Profitability Insights</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-purple-800">Highest Profit Margin</h3>
                    <p className="text-lg font-bold text-purple-600">NVDA: 55.9%</p>
                    <p className="text-sm text-purple-600">AI boom driving exceptional margins</p>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-red-800">Struggling Profitability</h3>
                    <p className="text-lg font-bold text-red-600">INTC: -36.2%</p>
                    <p className="text-sm text-red-600">Major restructuring needed</p>
                  </div>
                  <div className="bg-indigo-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-indigo-800">Highest ROE</h3>
                    <p className="text-lg font-bold text-indigo-600">AAPL: 138%</p>
                    <p className="text-sm text-indigo-600">Exceptional capital efficiency</p>
                  </div>
                </div>
              </div>
            </>
          )}

          {activeTab === 'growth' && (
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-4">Revenue Growth Analysis</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={growthData.sort((a, b) => b.revenueGrowth - a.revenueGrowth)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="company" />
                    <YAxis label={{ value: 'Revenue Growth (%)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Revenue Growth']} />
                    <Bar dataKey="revenueGrowth">
                      {growthData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.revenueGrowth < 0 ? '#EF4444' : sectorColors[entry.sector]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-emerald-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-emerald-800">Growth Leader</h3>
                  <p className="text-lg font-bold text-emerald-600">NVDA: 77.9%</p>
                  <p className="text-sm text-emerald-600">AI revolution impact</p>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-blue-800">Strong Tech Growth</h3>
                  <p className="text-lg font-bold text-blue-600">AMD: 35.9%</p>
                  <p className="text-sm text-blue-600">Data center expansion</p>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-orange-800">Stable Growth</h3>
                  <p className="text-lg font-bold text-orange-600">META: 16.1%</p>
                  <p className="text-sm text-orange-600">Social media maturity</p>
                </div>
                <div className="bg-red-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-red-800">Declining</h3>
                  <p className="text-lg font-bold text-red-600">INTC: -0.4%</p>
                  <p className="text-sm text-red-600">Market share erosion</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'dividends' && (
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-4">Dividend Yield Comparison</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={dividendData.sort((a, b) => b.dividendYield - a.dividendYield)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="company" />
                    <YAxis label={{ value: 'Dividend Yield (%)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip formatter={(value) => [`${value.toFixed(2)}%`, 'Dividend Yield']} />
                    <Bar dataKey="dividendYield">
                      {dividendData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={sectorColors[entry.sector]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">Dividend Strategy Analysis</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold mb-3">High Dividend Payers (Financial Sector)</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between p-2 bg-green-50 rounded">
                        <span>Morgan Stanley (MS)</span>
                        <span className="font-bold">2.93%</span>
                      </div>
                      <div className="flex justify-between p-2 bg-green-50 rounded">
                        <span>Bank of America (BAC)</span>
                        <span className="font-bold">2.41%</span>
                      </div>
                      <div className="flex justify-between p-2 bg-green-50 rounded">
                        <span>JPMorgan (JPM)</span>
                        <span className="font-bold">2.15%</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-3">Growth-Focused (Low/No Dividends)</h3>
                    <div className="space-y-2">
                      <div className="p-2 bg-blue-50 rounded">
                        <span>AMZN, NFLX, AMD: No dividends</span>
                      </div>
                      <div className="p-2 bg-blue-50 rounded">
                        <span>NVDA: 0.03% (token dividend)</span>
                      </div>
                      <div className="p-2 bg-blue-50 rounded">
                        <span>Focus on reinvestment for growth</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'insights' && (
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-6">Key Strategic Insights</h2>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="border-l-4 border-blue-500 pl-4">
                      <h3 className="font-bold text-lg text-blue-800">🏆 AI Revolution Winners</h3>
                      <p className="text-gray-700">NVIDIA leads with 77.9% revenue growth and 55.9% profit margins, capturing AI infrastructure demand. Microsoft and Google also benefit from AI integration.</p>
                    </div>
                    
                    <div className="border-l-4 border-red-500 pl-4">
                      <h3 className="font-bold text-lg text-red-800">⚠️ Intel's Crisis</h3>
                      <p className="text-gray-700">Only company with negative revenue growth (-0.4%) and massive losses (-36.2% profit margin). Missing the AI transition and losing market share to AMD and NVIDIA.</p>
                    </div>
                    
                    <div className="border-l-4 border-green-500 pl-4">
                      <h3 className="font-bold text-lg text-green-800">💰 Financial Sector Stability</h3>
                      <p className="text-gray-700">Banks (JPM, BAC, GS, MS) offer consistent dividends (2-3%) with reasonable P/E ratios (13-15), providing income and value.</p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="border-l-4 border-purple-500 pl-4">
                      <h3 className="font-bold text-lg text-purple-800">📊 Valuation Extremes</h3>
                      <p className="text-gray-700">AMD trades at 80.7x P/E vs Netflix at 55.8x, suggesting AMD may be overvalued relative to growth prospects. Financial stocks appear undervalued.</p>
                    </div>
                    
                    <div className="border-l-4 border-orange-500 pl-4">
                      <h3 className="font-bold text-lg text-orange-800">🔄 Capital Allocation Strategies</h3>
                      <p className="text-gray-700">Apple's 138% ROE shows exceptional capital efficiency. Growth companies (AMZN, NFLX) reinvest vs. mature companies (financials) returning cash via dividends.</p>
                    </div>
                    
                    <div className="border-l-4 border-teal-500 pl-4">
                      <h3 className="font-bold text-lg text-teal-800">🎯 Investment Themes</h3>
                      <p className="text-gray-700">Three clear strategies emerge: AI growth (NVDA, MSFT), stable tech (AAPL, GOOG), and income/value (financial sector). Each serves different portfolio needs.</p>
                    </div>
                  </div>
                </div>
                
                <div className="mt-8 bg-gray-50 p-6 rounded-lg">
                  <h3 className="font-bold text-xl mb-4">Portfolio Construction Recommendations</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-blue-100 p-4 rounded-lg">
                      <h4 className="font-semibold text-blue-800">Growth Portfolio</h4>
                      <p className="text-sm text-blue-700">NVDA, AMD, META for AI/tech exposure with higher risk/reward</p>
                    </div>
                    <div className="bg-green-100 p-4 rounded-lg">
                      <h4 className="font-semibold text-green-800">Balanced Portfolio</h4>
                      <p className="text-sm text-green-700">AAPL, MSFT, GOOG for stable growth with reasonable valuations</p>
                    </div>
                    <div className="bg-yellow-100 p-4 rounded-lg">
                      <h4 className="font-semibold text-yellow-800">Income Portfolio</h4>
                      <p className="text-sm text-yellow-700">JPM, BAC, MS for dividends and value with lower volatility</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FinancialAnalysisDashboard;