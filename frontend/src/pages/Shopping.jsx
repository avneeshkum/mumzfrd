import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, ShoppingBag, Heart } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { sendMessage } from '../services/api';
import ProductCard from '../components/ProductCard';
import Loader from '../components/Loader';

export default function Shopping() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  // High-Precision Auto Scroll Logic
  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'end' 
      });
    }
  };

  // Trigger scroll on every message update or streaming tick
  useEffect(() => {
    scrollToBottom();
    const timeout = setTimeout(scrollToBottom, 100);
    return () => clearTimeout(timeout);
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = { role: 'user', text: input, id: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const data = await sendMessage(input);
      const aiMsgId = Date.now() + 1;
      
      const responseText = data.response_en || "";
      const arabicText = data.response_ar || "";

      // Initialize AI message state
      setMessages(prev => [...prev, { 
        id: aiMsgId,
        role: 'ai', 
        textEn: '', 
        textAr: '', 
        fullEn: responseText,
        fullAr: arabicText,
        activeLang: 'en',
        products: data.products,
        isStreaming: true 
      }]);
      
      setLoading(false);

      // --- Bilingual Typewriter Streaming ---
      let i = 0;
      let j = 0;
      
      const enInterval = setInterval(() => {
        if (i < responseText.length) {
          const currentEn = responseText.slice(0, i + 1);
          setMessages(prev => prev.map(m => 
            m.id === aiMsgId ? { ...m, textEn: currentEn } : m
          ));
          i++;
        } else {
          clearInterval(enInterval);
          const arInterval = setInterval(() => {
            if (j < arabicText.length) {
              const currentAr = arabicText.slice(0, j + 1);
              setMessages(prev => prev.map(m => 
                m.id === aiMsgId ? { ...m, textAr: currentAr } : m
              ));
              j++;
            } else {
              setMessages(prev => prev.map(m => 
                m.id === aiMsgId ? { ...m, isStreaming: false } : m
              ));
              clearInterval(arInterval);
            }
          }, 10);
        }
      }, 15);

    } catch (err) {
      setMessages(prev => [...prev, { 
        id: Date.now(),
        role: 'ai', 
        textEn: "Sorry, I'm having trouble connecting right now. Please try again.",
        textAr: "عذراً، أواجه مشكلة في الاتصال حالياً. يرجى المحاولة مرة أخرى.",
        activeLang: 'en'
      }]);
      setLoading(false);
    }
  };

  const toggleLanguage = (id, lang) => {
    setMessages(prev => prev.map(m => 
      m.id === id ? { ...m, activeLang: lang } : m
    ));
  };

  return (
    <>
      <div className="noise-overlay pointer-events-none"></div>
      <div className="mesh-bg fixed inset-0 z-0">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>

      <div className="relative min-h-screen flex flex-col w-full overflow-x-hidden z-10 font-sans">
        
        <div className="flex-1 w-full max-w-4xl mx-auto px-4 sm:px-6 pt-24 pb-48 flex flex-col">
          
          <AnimatePresence>
            {messages.length === 0 && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="flex-1 flex flex-col items-center justify-center text-center mt-10 mb-20"
              >
                <div className="glass-panel w-20 h-20 rounded-[1.5rem] flex items-center justify-center mb-8 border border-white shadow-xl">
                  <ShoppingBag size={40} className="text-slate-800" strokeWidth={1.2} />
                </div>
                <h1 className="text-5xl sm:text-6xl font-extrabold mb-4 tracking-tighter text-slate-900">
                  Smart <span className="text-gradient">Shopping</span>
                </h1>
                <p className="text-slate-600 font-medium text-lg max-w-md mx-auto leading-relaxed px-4">
                  Ask me about the safest car seats, organic diapers, or the best strollers for your lifestyle.
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="space-y-12 sm:space-y-20 w-full flex flex-col">
            {messages.map((m) => (
              <motion.div 
                key={m.id} 
                initial={{ opacity: 0, y: 20 }} 
                animate={{ opacity: 1, y: 0 }}
                className={`w-full flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}
              >
                {/* USER BUBBLE */}
                {m.role === 'user' && (
                  <div className="bg-slate-900 text-white rounded-[2rem] rounded-tr-md px-6 py-4 sm:px-8 sm:py-5 max-w-[85%] sm:max-w-[70%] shadow-2xl border border-slate-800">
                    <p className="text-[15px] sm:text-base font-medium leading-relaxed">
                      {m.text}
                    </p>
                  </div>
                )}

                {/* AI RESPONSE */}
                {m.role === 'ai' && (
                  <div className="flex gap-4 sm:gap-6 w-full max-w-[98%] items-start">
                    <div className="hidden sm:flex glass-panel p-2.5 rounded-[1rem] border border-white/60 shadow-sm shrink-0 mt-1">
                      <Heart size={20} className="text-[#ff7eb3] fill-[#ff7eb3]" />
                    </div>

                    <div className="flex-1 w-full flex flex-col min-w-0">
                      {/* Language Switcher */}
                      {!m.isStreaming && m.fullAr && (
                        <div className="flex gap-1 mb-4 bg-white/40 w-fit p-1 rounded-full border border-white/60 backdrop-blur-xl shadow-sm">
                          <button 
                            onClick={() => toggleLanguage(m.id, 'en')}
                            className={`px-4 py-1.5 rounded-full text-[10px] font-black tracking-widest transition-all ${m.activeLang === 'en' ? 'bg-slate-900 text-white shadow-md' : 'text-slate-500'}`}
                          >
                            EN
                          </button>
                          <button 
                            onClick={() => toggleLanguage(m.id, 'ar')}
                            className={`px-4 py-1.5 rounded-full text-[10px] font-black tracking-widest transition-all ${m.activeLang === 'ar' ? 'bg-slate-900 text-white shadow-md' : 'text-slate-500'}`}
                          >
                            AR
                          </button>
                        </div>
                      )}

                      {/* FIXED RENDERER: Removed className from ReactMarkdown */}
                      <div 
                        className={`prose prose-slate prose-lg max-w-none transition-all duration-500 ${m.activeLang === 'ar' ? 'text-right font-serif' : 'text-left font-sans'}`}
                        dir={m.activeLang === 'ar' ? 'rtl' : 'ltr'}
                      >
                        <div className="text-lg sm:text-xl text-slate-800 font-medium leading-relaxed tracking-wide">
                          <ReactMarkdown>
                            {m.activeLang === 'en' ? m.textEn : m.textAr}
                          </ReactMarkdown>
                        </div>
                        
                        {m.isStreaming && (
                          <motion.span 
                            animate={{ opacity: [0, 1, 0] }}
                            transition={{ repeat: Infinity, duration: 0.8 }}
                            className="inline-block w-1.5 h-6 bg-[#ff7eb3] ml-1 align-middle"
                          />
                        )}
                      </div>
                      
                      {m.products && m.products.length > 0 && !m.isStreaming && (
                        <motion.div 
                          initial={{ opacity: 0, y: 15 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8 w-full mt-10"
                        >
                          {m.products.map((p, idx) => (
                            <div key={idx} className="h-full">
                              <ProductCard product={p} />
                            </div>
                          ))}
                        </motion.div>
                      )}
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
            
            <AnimatePresence>
              {loading && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }} 
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="w-full flex justify-start"
                >
                  <div className="hidden sm:flex w-[68px] shrink-0" />
                  <Loader />
                </motion.div>
              )}
            </AnimatePresence>
            
            <div ref={scrollRef} className="h-10 w-full shrink-0" />
          </div>
        </div>

        {/* Input Dock */}
        <div className="fixed bottom-0 left-0 w-full px-4 sm:px-6 pb-6 sm:pb-10 pt-6 bg-gradient-to-t from-[#fcfbfb] via-[#fcfbfb]/90 to-transparent z-50">
          <div className="max-w-3xl mx-auto relative group">
            <div className="absolute inset-0 bg-[#ff7eb3]/10 blur-3xl rounded-full transition-opacity duration-700 opacity-0 group-hover:opacity-100 pointer-events-none" />
            <div className="relative flex items-center glass-panel rounded-full border border-white/80 bg-white/70 backdrop-blur-2xl shadow-[0_20px_60px_rgba(0,0,0,0.1)] p-2 transition-all duration-500 focus-within:shadow-[0_20px_60px_rgba(255,117,140,0.2)] focus-within:bg-white/90">
              <div className="pl-5 sm:pl-7 pr-2 text-slate-400">
                <Sparkles size={24} className="text-[#ff7eb3]" />
              </div>
              <input 
                value={input} 
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder="Ask Mumzfrd anything..."
                className="w-full bg-transparent border-none text-slate-900 placeholder-slate-400 py-3 sm:py-5 px-2 outline-none font-bold text-[15px] sm:text-xl"
                disabled={loading}
              />
              <motion.button 
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSend} 
                disabled={!input.trim() || loading}
                className="bg-slate-900 text-white p-4 sm:p-5 rounded-full shadow-2xl flex-shrink-0 disabled:opacity-30 hover:bg-gradient-to-br hover:from-[#ff7eb3] hover:to-[#ff758c] transition-all duration-300 ml-2"
              >
                <Send size={22} className="ml-[2px]" />
              </motion.button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}