import { Link, useLocation } from 'react-router-dom';
import { Heart } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Navbar() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  return (
    <motion.nav 
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="fixed top-0 left-0 w-full z-50 px-5 sm:px-8 py-4 flex justify-between items-center bg-white/40 backdrop-blur-xl border-b border-white/50 shadow-[0_4px_30px_rgb(0,0,0,0.03)]"
    >
      {/* LOGO */}
      <Link to="/" className="flex items-center gap-2.5 group">
        <motion.div 
          whileHover={{ scale: 1.1, rotate: 12 }}
          className="bg-slate-900 p-1.5 rounded-full shadow-sm"
        >
          <Heart className="text-[#ff7eb3] fill-[#ff7eb3]" size={18} strokeWidth={1.5} />
        </motion.div>
        <span className="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-900">
          Mumz<span className="text-gradient">frd</span>
        </span>
      </Link>
      
      {/* LINKS */}
      <div className="flex gap-4 sm:gap-8 text-[15px] sm:text-base font-bold text-slate-500">
        <Link 
          to="/planner" 
          className={`transition-all duration-300 hover:text-slate-900 ${
            isActive('/planner') ? 'text-slate-900 drop-shadow-sm' : ''
          }`}
        >
          Planner
        </Link>
        <Link 
          to="/shopping" 
          className={`transition-all duration-300 hover:text-slate-900 ${
            isActive('/shopping') ? 'text-slate-900 drop-shadow-sm' : ''
          }`}
        >
          Shopping
        </Link>
      </div>
    </motion.nav>
  );
}