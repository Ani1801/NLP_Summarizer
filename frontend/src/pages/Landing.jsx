import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { FileSearch, ShieldCheck, Zap, ArrowRight, CheckCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import InteractiveDemoMockup from '../components/InteractiveDemoMockup';

const Landing = () => {
  const { user } = useAuth();

  // If user is already logged in, seamlessly push them to their dashboard
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 50, damping: 15 } }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-50 font-sans transition-colors duration-200 overflow-hidden relative">
      
      {/* Dynamic Background Elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-500/10 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[50%] rounded-full bg-purple-500/10 blur-[100px] pointer-events-none"></div>
      
      {/* Header / Navbar */}
      <header className="absolute top-0 w-full px-8 py-6 flex items-center justify-between z-10 glassmorphism bg-white/50 dark:bg-slate-900/50 backdrop-blur-md border-b border-white/20 dark:border-slate-800/50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-blue rounded flex items-center justify-center">
            <ShieldCheck size={20} className="text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">DocSummarizer</span>
        </div>
        <nav className="hidden md:flex items-center gap-8 font-medium text-sm text-slate-600 dark:text-slate-300">
          <a href="#features" className="hover:text-primary-blue transition-colors">Features</a>
          <a href="#demo" className="hover:text-primary-blue transition-colors">Interactive Demo</a>
          <a href="#pricing" className="hover:text-primary-blue transition-colors">Pricing</a>
        </nav>
        <div className="flex items-center gap-4">
          <Link to="/auth?mode=login" className="text-sm font-semibold text-slate-700 dark:text-slate-200 hover:text-primary-blue transition-colors">
            Log In
          </Link>
          <Link to="/auth?mode=signup" className="text-sm font-semibold bg-primary-blue hover:bg-blue-700 text-white px-5 py-2.5 rounded-full transition-all shadow-md shadow-blue-500/20 hover:shadow-lg hover:shadow-blue-500/30 active:scale-95">
            Get Started Free
          </Link>
        </div>
      </header>

      <main className="pt-32 pb-20 px-6 sm:px-8 max-w-7xl mx-auto flex flex-col items-center justify-center min-h-screen">
        
        {/* Main Hero Section */}
        <motion.div 
          className="text-center max-w-4xl mx-auto relative z-10"
          initial="hidden"
          animate="show"
          variants={containerVariants}
        >
          <motion.div variants={itemVariants} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50 dark:bg-blue-900/30 border border-blue-100 dark:border-blue-800/50 text-primary-blue dark:text-blue-400 text-xs font-semibold uppercase tracking-widest mb-8">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-blue opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-blue"></span>
            </span>
            DocSummarizer version 1.0 is live
          </motion.div>
          
          <motion.h1 variants={itemVariants} className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 leading-[1.1]">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-slate-900 to-slate-600 dark:from-white dark:to-slate-400">Revolutionize</span> <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Legal Document Analysis</span> with AI.
          </motion.h1>
          
          <motion.p variants={itemVariants} className="text-lg md:text-xl text-slate-600 dark:text-slate-400 mb-10 max-w-2xl mx-auto font-medium leading-relaxed">
            Instantly summarize legal contracts, detect risks & clauses, extract entities, compare versions side-by-side, and chat with zero-hallucination source tracking citations.
          </motion.p>
          
          <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/auth?mode=signup" className="w-full sm:w-auto text-base font-semibold bg-primary-blue hover:bg-blue-700 text-white px-8 py-3.5 rounded-full transition-all shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/40 hover:-translate-y-1 flex items-center justify-center gap-2 group">
              Start Summarizing Now
              <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <a href="#demo" className="w-full sm:w-auto text-base font-semibold bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-700 dark:text-slate-200 px-8 py-3.5 rounded-full transition-all flex items-center justify-center hover:bg-slate-50 dark:hover:bg-slate-800/80">
              View Interactive Flow Demo
            </a>
          </motion.div>
          
          <motion.div variants={itemVariants} className="mt-8 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm text-slate-500 dark:text-slate-400 font-medium">
            <div className="flex items-center gap-1.5"><CheckCircle size={16} className="text-emerald-500" /> No credit card required</div>
            <div className="flex items-center gap-1.5"><CheckCircle size={16} className="text-emerald-500" /> Free 14-day premium trial</div>
            <div className="flex items-center gap-1.5"><CheckCircle size={16} className="text-emerald-500" /> Cancel anytime</div>
          </motion.div>
        </motion.div>

        {/* Feature Cards Grid */}
        <motion.div 
          id="features"
          className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl mx-auto mt-28 relative z-10"
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-100px" }}
          variants={containerVariants}
        >
          <motion.div variants={itemVariants} className="bg-white dark:bg-slate-800/80 backdrop-blur-sm border border-slate-200 dark:border-slate-700 p-8 rounded-2xl shadow-sm hover:shadow-md transition-all group">
            <div className="w-12 h-12 bg-blue-50 dark:bg-blue-900/30 text-primary-blue rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Zap size={24} />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Multi-Level Summaries</h3>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
              Generates high-level executive summaries, key takeaways, and section-by-section breakdowns grounded in contract source text.
            </p>
          </motion.div>

          <motion.div variants={itemVariants} className="bg-white dark:bg-slate-800/80 backdrop-blur-sm border border-slate-200 dark:border-slate-700 p-8 rounded-2xl shadow-sm hover:shadow-md transition-all group">
            <div className="w-12 h-12 bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <FileSearch size={24} />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Clause & Entity Extraction</h3>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
              Automatically detects termination, payment, and liability clauses while parsing parties, key dates, monetary values, and jurisdiction.
            </p>
          </motion.div>

          <motion.div variants={itemVariants} className="bg-white dark:bg-slate-800/80 backdrop-blur-sm border border-slate-200 dark:border-slate-700 p-8 rounded-2xl shadow-sm hover:shadow-md transition-all group">
            <div className="w-12 h-12 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <ShieldCheck size={24} />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Side-by-Side Comparison</h3>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
              Compare contract versions to immediately highlight added, deleted, or reworded clauses with calculated risk shift scores.
            </p>
          </motion.div>
        </motion.div>

        {/* Interactive Action Walkthrough Section (Replacing Empty Placeholder Wireframe) */}
        <motion.div 
          id="demo"
          initial={{ opacity: 0, y: 60 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="mt-24 w-full relative z-10"
        >
          <div className="text-center mb-8">
            <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              See DocSummarizer in Action
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 font-medium">
              Watch how our AI scans, classifies clauses, extracts entities, and answers questions with verbatim citations.
            </p>
          </div>

          <InteractiveDemoMockup />
        </motion.div>

      </main>
    </div>
  );
};

export default Landing;
