import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ModeCard({ title, subtitle, icon: Icon, path }) {
  const navigate = useNavigate();
  
  return (
    <motion.div 
      whileHover={{ y: -8, scale: 1.01 }}
      whileTap={{ scale: 0.97 }}
      onClick={() => navigate(path)}
      /* Reduced p-8 sm:p-10 to p-6 sm:p-8, and min-h-[340px] to min-h-[260px] sm:min-h-[280px] */
      className="glass-panel group cursor-pointer p-6 sm:p-8 rounded-[2rem] sm:rounded-[2.5rem] flex flex-col justify-between min-h-[260px] sm:min-h-[280px] lg:min-h-[300px] h-full transition-all duration-500 ease-out relative overflow-hidden"
    >
      {/* Shine effect on hover */}
      <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/40 to-transparent group-hover:animate-[shimmer_1.5s_ease-in-out_forwards] pointer-events-none" />

      <div className="relative z-10">
        {/* Adjusted Icon container margin and size slightly */}
        <div className="bg-white/60 backdrop-blur-md w-14 h-14 sm:w-16 sm:h-16 rounded-xl sm:rounded-[1.25rem] shadow-[0_4px_20px_rgb(0,0,0,0.05)] flex items-center justify-center mb-5 sm:mb-6 transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 ease-out">
          <Icon size={28} className="text-slate-800" strokeWidth={1.5} />
        </div>
        
        {/* Adjusted text sizing */}
        <h3 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold mb-2 sm:mb-3 tracking-tight text-slate-900 drop-shadow-sm">
          {title}
        </h3>
        
        <p className="text-slate-600 text-base sm:text-lg font-medium leading-relaxed max-w-[95%] line-clamp-2">
          {subtitle}
        </p>
      </div>

      {/* Adjusted top margin on the action button area */}
      <div className="relative z-10 flex justify-end mt-4 sm:mt-6">
        <div className="bg-slate-900 text-white p-3 sm:p-4 rounded-full shadow-lg group-hover:bg-gradient-to-r group-hover:from-[#ff7eb3] group-hover:to-[#ff758c] transition-all duration-500">
          <ArrowRight 
            size={20} 
            strokeWidth={2}
            className="transform group-hover:translate-x-1 transition-transform duration-300 ease-out sm:w-6 sm:h-6" 
          />
        </div>
      </div>
    </motion.div>
  );
}