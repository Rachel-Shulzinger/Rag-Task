import { motion } from 'framer-motion'
import { Database, Loader2 } from 'lucide-react'

export default function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 via-purple-500 to-pink-500">
      <motion.div
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center text-white"
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          className="w-24 h-24 mx-auto mb-6 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center"
        >
          <Database size={48} />
        </motion.div>
        
        <h2 className="text-3xl font-bold mb-2">טוען מערכת RAG</h2>
        <p className="text-white/80 mb-4">בונה אינדקס וקטורי...</p>
        
        <div className="flex items-center justify-center gap-2">
          <Loader2 className="animate-spin" size={20} />
          <span>זה יקח כ-30 שניות</span>
        </div>

        <div className="mt-8 space-y-2 text-sm text-white/60">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            ✓ טוען 24 מסמכים
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
          >
            ✓ יוצר embeddings
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5 }}
          >
            ✓ בונה vector store
          </motion.div>
        </div>
      </motion.div>
    </div>
  )
}
