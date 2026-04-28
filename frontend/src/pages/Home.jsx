import { motion } from 'framer-motion';
import { Calendar, ShoppingBag } from 'lucide-react';
import ModeCard from '../components/ModeCard';

export default function Home() {
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.15, delayChildren: 0.4 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 50, scale: 0.9 },
    show: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: { type: "spring", stiffness: 60, damping: 14 } 
    }
  };

  return (
    <>
      {/* Background & Texture Overlay */}
      <div className="noise-overlay"></div>
      <div className="mesh-bg">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>

      {/* Changed pt-24 md:pt-32 to pt-16 md:pt-20 to save vertical space */}
      <div className="relative min-h-screen pt-16 md:pt-20 lg:pt-24 px-5 sm:px-8 max-w-6xl mx-auto flex flex-col justify-center pb-10">
        
        {/* HERO */}
        {/* Reduced mb-16 md:mb-24 to mb-10 md:mb-14 */}
        <motion.div 
          initial={{ opacity: 0, y: 30, filter: "blur(12px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="text-center mb-10 md:mb-14"
        >
          {/* Adjusted text sizes slightly to prevent wrapping on smaller laptops */}
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-extrabold tracking-tighter text-slate-900 mb-4 sm:mb-6">
            Mumz<span className="text-gradient">frd</span>
          </h1>

          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 1 }}
            className="mt-2 sm:mt-4 text-base sm:text-lg md:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed tracking-wide font-medium"
          >
            Helping moms make better decisions with AI-powered guidance.
          </motion.p>
        </motion.div>

        {/* CARDS */}
        {/* Reduced gap-8 md:gap-10 to gap-6 md:gap-8 */}
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 max-w-5xl mx-auto w-full"
        >
          <motion.div variants={itemVariants} className="h-full">
            <ModeCard 
              title="Pregnancy Planner"
              subtitle="Personalized week-by-week journey and essential checklists."
              icon={Calendar}
              path="/planner"
            />
          </motion.div>

          <motion.div variants={itemVariants} className="h-full">
            <ModeCard 
              title="Smart Shopping"
              subtitle="Find the best products for you and your baby with AI analysis."
              icon={ShoppingBag}
              path="/shopping"
            />
          </motion.div>
        </motion.div>

      </div>
    </>
  );
}