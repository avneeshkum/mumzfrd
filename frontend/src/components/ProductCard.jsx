import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, Star } from 'lucide-react';

export default function ProductCard({ product }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 60, damping: 14 }}
      whileHover={{ y: -6, scale: 1.01 }}
      className="glass-panel group relative p-6 sm:p-7 rounded-[2rem] flex flex-col h-full overflow-hidden border border-white/60"
    >
      {/* Decorative Shine Effect */}
      <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/40 to-transparent group-hover:animate-[shimmer_1.5s_ease-in-out_forwards] pointer-events-none" />

      {/* BEST CHOICE BADGE */}
      {product.isBest && (
        <div className="absolute top-0 right-0 bg-gradient-to-r from-[#ff7eb3] to-[#ff758c] text-white text-[10px] sm:text-xs font-bold px-4 py-1.5 rounded-bl-[1.5rem] uppercase tracking-widest shadow-md flex items-center gap-1.5 z-10">
          <Star size={12} className="fill-white" />
          <span>Best Choice</span>
        </div>
      )}

      {/* HEADER SECTION */}
      <div className="mb-6 mt-2 relative z-10">
        <h4 className="text-xl sm:text-2xl font-extrabold text-slate-900 leading-tight mb-3 pr-4 group-hover:text-[#ff7eb3] transition-colors duration-300">
          {product.name}
        </h4>
        
        {/* Floating Price Tag */}
        <div className="inline-block bg-white/70 backdrop-blur-md rounded-xl px-3 sm:px-4 py-1.5 border border-white/80 shadow-[0_4px_15px_rgb(0,0,0,0.05)]">
          <p className="text-transparent bg-clip-text bg-gradient-to-r from-[#ff7eb3] to-[#b891ff] font-extrabold text-lg sm:text-xl">
            {product.price}
          </p>
        </div>
      </div>
      
      {/* PROS & CONS (Frosted Bubbles) */}
      <div className="space-y-3 mt-auto flex-1 flex flex-col justify-end relative z-10">
        
        {/* Pros Bubble */}
        <div className="flex gap-3 items-start bg-white/50 backdrop-blur-sm p-3.5 sm:p-4 rounded-2xl border border-white/50 shadow-[0_2px_10px_rgb(0,0,0,0.02)] transition-all duration-300 group-hover:bg-white/60">
          <div className="bg-emerald-100 p-1 rounded-full shrink-0 shadow-sm border border-emerald-50">
            <CheckCircle2 size={16} className="text-emerald-500" strokeWidth={2.5} />
          </div>
          <span className="text-slate-700 text-[14px] sm:text-[15px] font-medium leading-snug">
            {product.pros}
          </span>
        </div>

        {/* Cons Bubble */}
        <div className="flex gap-3 items-start bg-white/50 backdrop-blur-sm p-3.5 sm:p-4 rounded-2xl border border-white/50 shadow-[0_2px_10px_rgb(0,0,0,0.02)] transition-all duration-300 group-hover:bg-white/60">
          <div className="bg-rose-100 p-1 rounded-full shrink-0 shadow-sm border border-rose-50">
            <XCircle size={16} className="text-rose-400" strokeWidth={2.5} />
          </div>
          <span className="text-slate-700 text-[14px] sm:text-[15px] font-medium leading-snug">
            {product.cons}
          </span>
        </div>

      </div>
    </motion.div>
  );
}