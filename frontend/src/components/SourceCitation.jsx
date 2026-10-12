import React, { useState } from 'react';
import { FileText, ExternalLink, Copy, Check, Quote } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * SourceCitation — Reusable component for displaying clickable document citations.
 * 
 * Props:
 *  - citation: { page_number: number, section: string, text: string }
 *  - inline: boolean (if true, renders as inline pill, else as standalone card tag)
 */
const SourceCitation = ({ citation, inline = true }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!citation) return null;

  const { page_number, section, text } = citation;

  const handleCopy = (e) => {
    e.stopPropagation();
    if (text) {
      navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const displayText = section 
    ? `Page ${page_number || 1} • ${section}`
    : `Page ${page_number || 1}`;

  return (
    <div className="relative inline-block text-left">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold transition-all duration-150 cursor-pointer ${
          inline
            ? 'bg-blue-50 hover:bg-blue-100 text-blue-700 dark:bg-blue-500/10 dark:hover:bg-blue-500/20 dark:text-blue-300 border border-blue-200/80 dark:border-blue-500/20'
            : 'bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
        }`}
      >
        <FileText size={11} className="text-blue-600 dark:text-blue-400 shrink-0" />
        <span>{displayText}</span>
      </button>

      {/* Popover showing verbatim source quote */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 6, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.96 }}
            transition={{ duration: 0.15 }}
            onMouseEnter={() => setIsOpen(true)}
            onMouseLeave={() => setIsOpen(false)}
            className="absolute bottom-full left-0 mb-2 w-72 sm:w-80 p-3.5 bg-white dark:bg-slate-900 rounded-xl shadow-xl border border-slate-200 dark:border-slate-800 z-50 text-xs text-slate-800 dark:text-slate-200"
          >
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2 mb-2">
              <div className="flex items-center gap-1.5 font-bold text-blue-600 dark:text-blue-400">
                <FileText size={13} />
                <span>Source Citation</span>
                <span className="text-[10px] bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300 px-1.5 py-0.5 rounded font-medium">
                  Page {page_number || 1}
                </span>
              </div>
              <button
                onClick={handleCopy}
                title="Copy source text"
                className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
              >
                {copied ? <Check size={13} className="text-emerald-500" /> : <Copy size={13} />}
              </button>
            </div>

            {section && (
              <p className="font-semibold text-[11px] text-slate-600 dark:text-slate-400 mb-1.5">
                Section: <span className="text-slate-900 dark:text-slate-100">{section}</span>
              </p>
            )}

            <div className="bg-slate-50 dark:bg-slate-800/60 rounded-lg p-2.5 border border-slate-100 dark:border-slate-800 italic text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed relative pl-6">
              <Quote size={12} className="absolute left-2 top-3 text-slate-400 dark:text-slate-500 rotate-180" />
              {text || 'No explicit text snippet available for this citation.'}
            </div>

            {/* Small arrow indicator */}
            <div className="absolute top-full left-4 -mt-1 w-2.5 h-2.5 bg-white dark:bg-slate-900 border-r border-b border-slate-200 dark:border-slate-800 transform rotate-45"></div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SourceCitation;
