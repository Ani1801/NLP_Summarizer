import React, { useState, useEffect } from 'react';
import { FileText, AlertTriangle, Scale, Target } from 'lucide-react';
import api from '../services/api';

const StatCards = () => {
  const [data, setData] = useState({
    "Total Audits": 0,
    "Critical Risks": 0,
    "Average Compliance": 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const result = await api.get('/api/dashboard/stats');
        setData(result);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };
    fetchStats();
  }, []);

  const getSeverityColor = (score) => {
    if (score > 80) return 'emerald';
    if (score >= 50) return 'amber';
    return 'red';
  };

  const getCriticalRiskColor = (count) => {
    if (count === 0) return 'emerald';
    if (count <= 2) return 'amber';
    return 'red';
  };

  const complianceScore = data['Average Compliance'] || 0;
  const criticalCount = data['Critical Risks'] || 0;

  const stats = [
    {
      title: 'Total Audits',
      value: data['Total Audits']?.toString() || '0',
      change: 'Lifetime totals',
      icon: FileText,
      color: 'blue'
    },
    {
      title: 'Critical Risks',
      value: criticalCount.toString(),
      change: criticalCount > 0 ? 'Requires Attention' : 'All clear',
      icon: AlertTriangle,
      color: getCriticalRiskColor(criticalCount),
      indicator: criticalCount > 0
    },
    {
      title: 'Clauses Analyzed',
      value: (data['Total Audits'] * 12).toString(), // Mocked estimate based on audits
      change: 'Estimated totals',
      icon: Scale,
      color: 'indigo'
    },
    {
      title: 'Avg. Compliance Score',
      value: `${complianceScore}%`,
      change: 'Lifetime average',
      icon: Target,
      color: getSeverityColor(complianceScore)
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <div key={idx} className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200/60 dark:border-slate-800 flex flex-col relative overflow-hidden group transition-colors duration-200">
            <div className="flex justify-between items-start mb-4">
              <div>
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">{stat.title}</p>
                <h3 className="text-3xl font-bold text-slate-800 dark:text-white tracking-tight">{stat.value}</h3>
              </div>
              {/* Using CSS variables explicitly for dynamic bg colors or explicit mapping */}
              <div className={`p-2.5 rounded-lg bg-${stat.color}-50 dark:bg-${stat.color}-500/10 text-${stat.color}-600 dark:text-${stat.color}-400`}>
                <Icon size={22} className={stat.color === 'blue' ? 'text-primary-blue dark:text-blue-400' : ''} />
              </div>
            </div>
            
            <div className="mt-auto flex items-center gap-2">
              {stat.indicator && (
                <span className="w-2 h-2 rounded-full bg-red-500 dark:bg-red-400 animate-pulse"></span>
              )}
              <p className={`text-xs font-medium ${stat.indicator ? 'text-red-500 dark:text-red-400 font-semibold' : 'text-slate-500 dark:text-slate-400'}`}>
                {stat.change}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StatCards;
