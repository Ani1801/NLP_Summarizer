import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, UploadCloud, ShieldAlert, Sparkles, MessageSquare, 
  CheckCircle2, Building2, Layers, Send, ArrowRight, Loader2 
} from 'lucide-react';

const steps = [
  { id: 1, label: '1. Document Upload', title: 'Upload & Instant Text Parsing' },
  { id: 2, label: '2. Clause Detection', title: 'AI Clause Classification & Highlighting' },
  { id: 3, label: '3. Entity Extraction', title: 'Parties, Dates & Dollar Amounts' },
  { id: 4, label: '4. Grounded RAG Chat', title: 'Zero-Hallucination Q&A with Citations' },
];

const InteractiveDemoMockup = () => {
  const [activeStep, setActiveStep] = useState(1);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  // Auto-cycle through steps every 2.5 seconds
  useEffect(() => {
    if (!isAutoPlaying) return;
    const interval = setInterval(() => {
      setActiveStep(prev => (prev % steps.length) + 1);
    }, 2800);
    return () => clearInterval(interval);
  }, [isAutoPlaying]);

  return (
    <div 
      className="w-full max-w-5xl mx-auto rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden bg-slate-900 text-white relative"
      onMouseEnter={() => setIsAutoPlaying(false)}
      onMouseLeave={() => setIsAutoPlaying(true)}
    >
      {/* Window Titlebar */}
      <div className="h-12 bg-slate-800/90 px-4 flex items-center justify-between border-b border-slate-700/80">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
          <div className="w-3 h-3 rounded-full bg-amber-500/80"></div>
          <div className="w-3 h-3 rounded-full bg-emerald-500/80"></div>
          <span className="ml-2 text-xs font-mono text-slate-400">Master_Services_Agreement_v2.pdf — Interactive Preview</span>
        </div>

        {/* Step Flow Indicators */}
        <div className="flex gap-1 bg-slate-900/60 p-1 rounded-lg border border-slate-700/50">
          {steps.map(step => (
            <button
              key={step.id}
              onClick={() => {
                setActiveStep(step.id);
                setIsAutoPlaying(false);
              }}
              className={`px-3 py-1 rounded-md text-[11px] font-bold transition-all ${
                activeStep === step.id
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {step.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Mock Content Screen */}
      <div className="p-6 md:p-8 min-h-[420px] flex flex-col justify-between relative bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950">
        <AnimatePresence mode="wait">
          
          {/* STEP 1: UPLOAD & PARSE */}
          {activeStep === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.35 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center"
            >
              <div className="space-y-4">
                <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-blue-500/20 text-blue-400 text-xs font-bold border border-blue-500/30">
                  <UploadCloud size={13} /> Step 1: Uploading & Scanning
                </div>
                <h3 className="text-2xl font-bold tracking-tight text-white">Instant Legal Document OCR & Parsing</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Upload contracts up to 500 pages. Our parser indexes text layout, section headings, and page boundaries for citation tracking.
                </p>

                {/* Animated Progress Bar */}
                <div className="space-y-2 bg-slate-800/80 p-4 rounded-xl border border-slate-700">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-300 flex items-center gap-1.5">
                      <FileText size={14} className="text-blue-400" /> Master_Services_Agreement_v2.pdf
                    </span>
                    <span className="text-blue-400 font-mono">100% Parsed</span>
                  </div>
                  <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                    <motion.div 
                      className="h-full bg-gradient-to-r from-blue-500 to-indigo-500" 
                      initial={{ width: '0%' }}
                      animate={{ width: '100%' }}
                      transition={{ duration: 1.8, ease: "easeInOut" }}
                    />
                  </div>
                  <p className="text-[11px] text-slate-400 flex items-center gap-1">
                    <CheckCircle2 size={12} className="text-emerald-400" /> 18 pages indexed • 42 sections mapped
                  </p>
                </div>
              </div>

              {/* PDF Preview Graphic */}
              <div className="bg-slate-800/60 p-5 rounded-2xl border border-slate-700/80 flex flex-col gap-3 relative overflow-hidden">
                <div className="flex items-center justify-between border-b border-slate-700/60 pb-2 text-xs text-slate-400">
                  <span>PDF Document Viewer</span>
                  <span className="text-emerald-400 font-semibold text-[10px] bg-emerald-500/10 px-2 py-0.5 rounded">Active Audit</span>
                </div>
                <div className="space-y-2 font-mono text-[11px] text-slate-300">
                  <div className="p-2 bg-slate-900/80 rounded border border-blue-500/30 text-blue-300">
                    <span className="font-bold">SECTION 1.1:</span> SCOPE OF SERVICES & DELIVERABLES...
                  </div>
                  <div className="p-2 bg-slate-900/40 rounded border border-slate-800">
                    <span className="font-bold">SECTION 3.2:</span> PAYMENT TERMS & INTEREST...
                  </div>
                  <div className="p-2 bg-slate-900/40 rounded border border-slate-800 opacity-60">
                    <span className="font-bold">SECTION 5.4:</span> TERMINATION FOR CONVENIENCE...
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* STEP 2: CLAUSE DETECTION */}
          {activeStep === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.35 }}
              className="space-y-4"
            >
              <div className="flex justify-between items-center">
                <div>
                  <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-bold border border-purple-500/30">
                    <Layers size={13} /> Step 2: Clause Classification
                  </div>
                  <h3 className="text-xl font-bold tracking-tight text-white mt-1">Automatic Clause Detection & Risk Scoring</h3>
                </div>
                <span className="text-xs bg-amber-500/20 text-amber-300 border border-amber-500/30 px-3 py-1 rounded-full font-bold">
                  Risk Score: 78 / 100 (Safe)
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <motion.div 
                  initial={{ scale: 0.9, opacity: 0 }} 
                  animate={{ scale: 1, opacity: 1 }} 
                  transition={{ delay: 0.1 }}
                  className="bg-slate-800/80 p-4 rounded-xl border border-red-500/40 space-y-2"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-extrabold bg-red-500/20 text-red-400 px-2 py-0.5 rounded border border-red-500/30 uppercase">Termination</span>
                    <span className="text-[10px] text-slate-400">Page 3 • Sec 5.4</span>
                  </div>
                  <h4 className="font-bold text-xs text-white">30-Day Notice for Convenience</h4>
                  <p className="text-[11px] text-slate-400 leading-relaxed italic">"Either party may terminate upon 30 days written notice."</p>
                </motion.div>

                <motion.div 
                  initial={{ scale: 0.9, opacity: 0 }} 
                  animate={{ scale: 1, opacity: 1 }} 
                  transition={{ delay: 0.25 }}
                  className="bg-slate-800/80 p-4 rounded-xl border border-emerald-500/40 space-y-2"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-extrabold bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/30 uppercase">Payment</span>
                    <span className="text-[10px] text-slate-400">Page 2 • Sec 3.1</span>
                  </div>
                  <h4 className="font-bold text-xs text-white">Net-30 & 1.5% Late Penalty</h4>
                  <p className="text-[11px] text-slate-400 leading-relaxed italic">"Invoices payable in 30 days. Overdue balances incur 1.5%."</p>
                </motion.div>

                <motion.div 
                  initial={{ scale: 0.9, opacity: 0 }} 
                  animate={{ scale: 1, opacity: 1 }} 
                  transition={{ delay: 0.4 }}
                  className="bg-slate-800/80 p-4 rounded-xl border border-amber-500/40 space-y-2"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-extrabold bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded border border-amber-500/30 uppercase">Liability Cap</span>
                    <span className="text-[10px] text-slate-400">Page 4 • Sec 8.2</span>
                  </div>
                  <h4 className="font-bold text-xs text-white">12 Months Fees Capped</h4>
                  <p className="text-[11px] text-slate-400 leading-relaxed italic">"Aggregate liability capped at total fees paid in 12 months."</p>
                </motion.div>
              </div>
            </motion.div>
          )}

          {/* STEP 3: ENTITY EXTRACTION */}
          {activeStep === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.35 }}
              className="space-y-4"
            >
              <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold border border-emerald-500/30">
                <Building2 size={13} /> Step 3: Key Entity Metadata Grid
              </div>
              <h3 className="text-xl font-bold tracking-tight text-white">Extracted Parties, Timeline & Financial Terms</h3>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700">
                  <span className="text-[10px] text-slate-400 font-bold uppercase block">Provider</span>
                  <span className="text-xs font-bold text-white">Acme Solutions Inc.</span>
                </div>
                <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700">
                  <span className="text-[10px] text-slate-400 font-bold uppercase block">Client</span>
                  <span className="text-xs font-bold text-white">Global Logistics Corp</span>
                </div>
                <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700">
                  <span className="text-[10px] text-slate-400 font-bold uppercase block">Effective Date</span>
                  <span className="text-xs font-bold text-emerald-400">Oct 1, 2026</span>
                </div>
                <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700">
                  <span className="text-[10px] text-slate-400 font-bold uppercase block">Total Value</span>
                  <span className="text-xs font-bold text-amber-400">$240,000 USD</span>
                </div>
              </div>
            </motion.div>
          )}

          {/* STEP 4: RAG CHAT */}
          {activeStep === 4 && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.35 }}
              className="space-y-4"
            >
              <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-bold border border-indigo-500/30">
                <Sparkles size={13} /> Step 4: Grounded RAG Chatbot Q&A
              </div>
              <h3 className="text-xl font-bold tracking-tight text-white">Ask Questions with Verbatim Page Citations</h3>

              <div className="bg-slate-800/90 p-4 rounded-xl border border-slate-700 space-y-3">
                <div className="flex justify-end">
                  <div className="bg-blue-600 text-white px-3.5 py-2 rounded-xl text-xs max-w-sm">
                    What is the notice period for terminating this contract?
                  </div>
                </div>

                <div className="flex justify-start">
                  <div className="bg-slate-900 text-slate-200 p-3.5 rounded-xl text-xs border border-slate-700 space-y-2 max-w-md">
                    <p>According to Section 5.4 (Page 3), either party may terminate for convenience upon 30 days prior written notice.</p>
                    <div className="inline-flex items-center gap-1.5 bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded text-[10px] font-bold border border-blue-500/30">
                      📄 Page 3 • Sec 5.4
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>

      {/* Animated Action Bar Footer */}
      <div className="px-6 py-3 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span>Live Interactive Action Demo</span>
        </div>
        <div className="flex items-center gap-1 text-slate-300 font-semibold">
          <span>Click tabs to explore flow</span>
          <ArrowRight size={14} className="text-blue-400" />
        </div>
      </div>
    </div>
  );
};

export default InteractiveDemoMockup;
