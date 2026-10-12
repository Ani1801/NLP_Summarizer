import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Loader2, AlertTriangle, FileText, CheckCircle, ShieldAlert, ChevronRight, Zap } from 'lucide-react';
import api from '../services/api';

const Compliance = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [regulations, setRegulations] = useState(['GDPR', 'CCPA', 'AI_ACT']);
  const [loading, setLoading] = useState(false);
  const [docsLoading, setDocsLoading] = useState(true);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const docs = await api.get('/api/library');
        setDocuments(docs);
      } catch (err) { console.error(err); }
      finally { setDocsLoading(false); }
    };
    fetchDocs();
  }, []);

  const toggleRegulation = (reg) => {
    setRegulations(prev =>
      prev.includes(reg) ? prev.filter(r => r !== reg) : [...prev, reg]
    );
  };

  const handleCheck = async () => {
    if (!selectedDoc || regulations.length === 0) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await api.post('/api/compliance/check', { audit_id: selectedDoc, regulations });
      setResult(data);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  const getSeverityStyle = (severity) => {
    const s = severity?.toLowerCase() || '';
    if (s === 'critical') return 'bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 border-red-200 dark:border-red-500/20';
    if (s === 'high') return 'bg-orange-50 dark:bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-200 dark:border-orange-500/20';
    if (s === 'medium') return 'bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-500/20';
    return 'bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-500/20';
  };

  const getRegulationBadge = (reg) => {
    const map = {
      'GDPR': { color: 'bg-blue-500', label: 'GDPR' },
      'CCPA': { color: 'bg-purple-500', label: 'CCPA' },
      'AI_ACT': { color: 'bg-emerald-500', label: 'AI Act' },
    };
    const r = map[reg] || { color: 'bg-slate-500', label: reg };
    return <span className={`${r.color} text-white text-[10px] font-bold px-2 py-0.5 rounded`}>{r.label}</span>;
  };

  const scoreColor = !result ? 'text-slate-400' :
    result.compliance_score > 80 ? 'text-emerald-500' :
    result.compliance_score >= 50 ? 'text-amber-500' : 'text-red-500';

  return (
    <div className="p-8 max-w-[1400px] mx-auto w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">Compliance Checker</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2 font-medium">Run proactive compliance audits against GDPR, CCPA, and the 2026 AI Act.</p>
      </div>

      {/* Config Panel */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Select Document</label>
            <select
              value={selectedDoc}
              onChange={(e) => setSelectedDoc(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-blue/20"
              disabled={docsLoading}
            >
              <option value="">Choose a document to audit...</option>
              {documents.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Regulations</label>
            <div className="flex gap-3">
              {[
                { id: 'GDPR', label: 'GDPR', desc: 'EU Data Protection' },
                { id: 'CCPA', label: 'CCPA', desc: 'California Privacy' },
                { id: 'AI_ACT', label: 'AI Act', desc: '2026 EU AI Regulation' },
              ].map(reg => (
                <button
                  key={reg.id}
                  onClick={() => toggleRegulation(reg.id)}
                  className={`flex-1 px-3 py-2.5 rounded-lg border-2 text-center transition-all ${
                    regulations.includes(reg.id)
                      ? 'border-primary-blue bg-blue-50 dark:bg-blue-500/10 text-primary-blue dark:text-blue-400'
                      : 'border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:border-slate-300'
                  }`}
                >
                  <p className="text-xs font-bold">{reg.label}</p>
                  <p className="text-[10px] opacity-70">{reg.desc}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm font-medium flex items-center gap-2">
            <AlertTriangle size={16} /> {error}
          </div>
        )}

        <div className="mt-4 flex justify-center">
          <button
            onClick={handleCheck}
            disabled={!selectedDoc || regulations.length === 0 || loading}
            className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-emerald-600 hover:to-teal-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-emerald-500/20"
          >
            {loading ? <><Loader2 size={18} className="animate-spin" /> Analyzing Compliance...</> : <><Shield size={18} /> Run Compliance Check</>}
          </button>
        </div>
      </div>

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            {/* Score + Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm flex flex-col items-center justify-center">
                <h3 className="text-sm font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3">Compliance Score</h3>
                <div className={`text-6xl font-extrabold ${scoreColor}`}>{result.compliance_score}</div>
                <p className="text-xs text-slate-500 mt-2">out of 100</p>
              </div>

              <div className="md:col-span-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
                <h3 className="text-sm font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3">Compliance Summary</h3>
                <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed mb-3">{result.summary}</p>
                <div className="flex gap-3 text-xs">
                  <span className="flex items-center gap-1 text-slate-500"><FileText size={12} /> {result.file_name}</span>
                  <span className="flex items-center gap-1 text-red-500"><AlertTriangle size={12} /> {result.total_violations} violation(s)</span>
                </div>
              </div>
            </div>

            {/* Violations */}
            {result.violations?.length > 0 && (
              <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800">
                  <h3 className="text-sm font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
                    Violations ({result.violations.length})
                  </h3>
                </div>
                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  {result.violations.map((v, idx) => (
                    <div key={idx} className="p-5">
                      <div className="flex items-center gap-3 mb-2 flex-wrap">
                        {getRegulationBadge(v.regulation)}
                        <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${getSeverityStyle(v.severity)}`}>
                          {v.severity}
                        </span>
                        {v.article_reference && (
                          <span className="text-[10px] text-slate-400 font-medium">{v.article_reference}</span>
                        )}
                      </div>
                      {v.clause && <p className="text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium">Section: {v.clause}</p>}
                      <p className="text-sm text-slate-700 dark:text-slate-300 mb-3">{v.description}</p>
                      {v.suggestion && (
                        <div className="bg-emerald-50 dark:bg-emerald-500/5 rounded-lg p-3 border border-emerald-100 dark:border-emerald-500/20">
                          <p className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase mb-1 flex items-center gap-1">
                            <Zap size={10} /> Suggested Fix
                          </p>
                          <p className="text-xs text-emerald-700 dark:text-emerald-300">{v.suggestion}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Items */}
            {result.action_items?.length > 0 && (
              <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
                <h3 className="text-sm font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                  <CheckCircle size={14} className="text-emerald-500" /> Prioritized Action Items
                </h3>
                <ol className="space-y-2">
                  {result.action_items.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-3 text-sm text-slate-700 dark:text-slate-300">
                      <span className="w-6 h-6 rounded-full bg-primary-blue/10 text-primary-blue dark:text-blue-400 flex items-center justify-center text-xs font-bold shrink-0">{idx + 1}</span>
                      {item}
                    </li>
                  ))}
                </ol>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Compliance;
