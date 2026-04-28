import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, CalendarCheck, Loader2, ChevronRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { sendMessage } from '../services/api';
import ProductCard from '../components/ProductCard';

export default function Planner() {
  const [date, setDate] = useState('');
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // States for bilingual text and streaming
  const [activeTab, setActiveTab] = useState('en'); 
  const [displayEn, setDisplayEn] = useState('');
  const [displayAr, setDisplayAr] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  const generate = async () => {
    if (!date) return;
    setLoading(true);
    setPlan(null);
    setDisplayEn('');
    setDisplayAr('');
    setActiveTab('en');
    
    try {
      const data = await sendMessage(`My due date is ${date}. Generate a pregnancy plan.`);
      setPlan(data);
      setLoading(false); // Stop button spinner
      setIsStreaming(true);

      // --- Streaming Logic ---
      const stream = (text, setFn, callback) => {
        let i = 0;
        const interval = setInterval(() => {
          setFn(text.slice(0, i + 1));
          i++;
          if (i >= text.length) {
            clearInterval(interval);
            if (callback) callback();
          }
        }, 15);
      };

      // Sequential streaming: English first, then Arabic
      stream(data.response_en, setDisplayEn, () => {
        if (data.response_ar) {
          stream(data.response_ar, setDisplayAr, () => setIsStreaming(false));
        } else {
          setIsStreaming(false);
        }
      });

    } catch (err) {
      console.error("Planner generation failed:", err);
      setLoading(false);
    }
  };

  return (
    <>
      {/* Premium Background Effects */}
      <div className="noise-overlay pointer-events-none"></div>
      <div className="mesh-bg fixed inset-0 z-0">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>

      <div className="relative min-h-screen pt-24 md:pt-32 px-4 sm:px-6 pb-20 w-full overflow-x-hidden z-10">
        <div className="max-w-4xl mx-auto w-full">
          
          {/* INPUT PANEL */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-panel w-full p-8 sm:p-12 rounded-[2.5rem] mb-12 text-center relative overflow-hidden"
          >
            <h2 className="text-4xl sm:text-5xl font-extrabold mb-4 tracking-tight text-slate-900 leading-tight">
              Your <span className="text-gradient">Journey</span> Starts Here
            </h2>
            <p className="text-slate-600 font-medium mb-10 text-base sm:text-lg max-w-lg mx-auto leading-relaxed">
              Enter your due date to generate your personalized, week-by-week pregnancy guide.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-xl mx-auto bg-white/30 p-2 rounded-[2.5rem] border border-white/50 backdrop-blur-md">
              <input 
                type="date" 
                value={date} 
                onChange={e => setDate(e.target.value)}
                className="w-full bg-transparent border-none text-slate-900 rounded-2xl px-6 py-4 outline-none font-bold text-lg cursor-pointer"
              />
              <motion.button 
                whileHover={{ scale: 1.02 }} 
                whileTap={{ scale: 0.98 }}
                onClick={generate} 
                disabled={loading || !date}
                className="bg-slate-900 text-white px-8 py-4 rounded-[2rem] font-bold flex items-center justify-center gap-2 w-full sm:w-auto shadow-xl hover:bg-gradient-to-r hover:from-[#ff7eb3] hover:to-[#ff758c] transition-all duration-500 disabled:opacity-50"
              >
                {/* Button spinner handles the loading state perfectly */}
                {loading ? <Loader2 size={24} className="animate-spin" /> : <Sparkles size={24} />}
                <span className="whitespace-nowrap">Generate Plan</span>
              </motion.button>
            </div>
          </motion.div>

          <AnimatePresence>
            {/* Extra Loader removed from here to keep the UI clean */}
            {plan && (
              <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="space-y-12">
                
                {/* LANGUAGE SWITCHER */}
                {plan.response_ar && (
                  <div className="flex justify-center -mb-6 relative z-20">
                    <div className="bg-white/60 backdrop-blur-2xl p-1.5 rounded-full border border-white/80 shadow-lg flex gap-1">
                      <button 
                        onClick={() => setActiveTab('en')}
                        className={`px-8 py-2.5 rounded-full font-bold text-sm transition-all duration-300 ${activeTab === 'en' ? 'bg-slate-900 text-white shadow-md' : 'text-slate-500 hover:text-slate-900'}`}
                      >
                        English
                      </button>
                      <button 
                        onClick={() => setActiveTab('ar')}
                        className={`px-8 py-2.5 rounded-full font-bold text-sm transition-all duration-300 ${activeTab === 'ar' ? 'bg-slate-900 text-white shadow-md' : 'text-slate-500 hover:text-slate-900'}`}
                      >
                        العربية
                      </button>
                    </div>
                  </div>
                )}

                {/* CONTENT CARD */}
                <div 
                  className={`glass-panel p-8 sm:p-14 rounded-[3rem] shadow-2xl relative overflow-hidden ${activeTab === 'ar' ? 'text-right' : 'text-left'}`}
                  dir={activeTab === 'ar' ? 'rtl' : 'ltr'}
                >
                  <div className={`flex items-center gap-4 mb-10 ${activeTab === 'ar' ? 'flex-row-reverse' : 'flex-row'}`}>
                    <div className="bg-slate-900 w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg shrink-0">
                      <CalendarCheck size={28} className="text-[#ff7eb3]" strokeWidth={2.5} />
                    </div>
                    <h3 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                      {activeTab === 'ar' ? 'دليلك الأسبوعي' : 'Weekly Guide'}
                    </h3>
                  </div>

                  <div className={`prose prose-slate prose-lg max-w-none 
                    ${activeTab === 'ar' ? 'font-serif text-2xl leading-relaxed' : 'font-sans'}
                    prose-headings:text-slate-900 prose-headings:font-black prose-headings:tracking-tighter
                    prose-p:text-slate-700 prose-p:font-medium prose-p:leading-relaxed
                    prose-strong:text-slate-900 prose-strong:font-black
                    prose-ul:list-none prose-ul:p-0`}>
                    
                    <ReactMarkdown 
                      components={{
                        h3: ({node, ...props}) => <h3 className="text-2xl sm:text-3xl mt-12 mb-6 text-slate-900 flex items-center gap-3" {...props} />,
                        li: ({node, ...props}) => (
                          <li className="flex items-start gap-3 mb-4 bg-white/40 p-4 rounded-2xl border border-white/50">
                            <ChevronRight size={20} className={`mt-1 shrink-0 text-[#ff758c] ${activeTab === 'ar' ? 'rotate-180' : ''}`} />
                            <span {...props} />
                          </li>
                        ),
                      }}
                    >
                      {activeTab === 'en' ? displayEn : displayAr}
                    </ReactMarkdown>

                    {/* Blinking Streaming Cursor */}
                    {isStreaming && (
                      <motion.span 
                        animate={{ opacity: [0, 1, 0] }} 
                        transition={{ repeat: Infinity, duration: 0.8 }} 
                        className="inline-block w-2.5 h-6 bg-[#ff758c] ml-1 align-middle" 
                      />
                    )}
                  </div>
                </div>
                
                {/* PRODUCTS SECTION */}
                {plan.products?.length > 0 && !isStreaming && (
                  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="pt-6">
                    <h3 className={`text-3xl font-extrabold mb-10 tracking-tight text-slate-900 ${activeTab === 'ar' ? 'text-right' : 'text-left'}`}>
                      {activeTab === 'ar' ? 'منتجات مقترحة لكِ' : <>Essentials for <span className="text-gradient">This Week</span></>}
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                      {plan.products.map((p, i) => (
                        <ProductCard key={i} product={p} />
                      ))}
                    </div>
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </>
  );
}