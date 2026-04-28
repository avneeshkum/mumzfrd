import { motion } from 'framer-motion';
import { Heart } from 'lucide-react';

export default function Loader() {
  return (
    <motion.div 
      initial={{ opacity: 0, x: -10 }} 
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="flex justify-start w-full my-6 pl-1" 
    >
      <div className="flex items-center gap-5">
        
        {/* --- ICON ASSEMBLY WITH PROMINENT CIRCULAR RING --- */}
        <div className="relative w-12 h-12 flex items-center justify-center shrink-0">
          
          {/* THE FULL CIRCULAR TRACK (Faint) */}
          <div className="absolute inset-0 rounded-full border-[2.5px] border-slate-200/30" />

          {/* THE ROTATING GRADIENT RING */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 rounded-full border-[2.5px] border-transparent"
            style={{
              borderTopColor: '#ff7eb3',   // Pink
              borderRightColor: '#b891ff', // Purple
              filter: "drop-shadow(0 0 8px rgba(255, 126, 179, 0.5))",
            }}
          />

          {/* Central Frosted Icon Box (Same as Chat) */}
          <div className="w-9 h-9 bg-white/60 backdrop-blur-md rounded-[0.8rem] border border-white/80 shadow-sm flex items-center justify-center relative z-10">
            <Heart size={16} className="text-[#ff7eb3] fill-[#ff7eb3]" />
          </div>
        </div>

        {/* --- BRAND THINKING TEXT --- */}
        <div className="flex flex-col justify-center">
          <div className="flex items-baseline gap-1.5">
            <span className="font-extrabold text-slate-900 text-lg tracking-tight">
              Mumz<span className="text-gradient">frd</span>
            </span>
            <span className="font-semibold text-slate-400 text-sm animate-pulse tracking-wide">
              processing...
            </span>
          </div>
        </div>

      </div>
    </motion.div>
  );
}